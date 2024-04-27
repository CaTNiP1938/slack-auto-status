"""
    Contains the main runnable file that sets the slack status.
"""

from datetime import datetime, timedelta
from typing import List, Tuple

from integrations import azure_teams, google_calendar, slack

import file
import utils


# Global variables
config = None
silent_output = None
status_expiry_date = None
status_emoji = None
meeting_status_emoji = None


def set_configuration() -> None:
    """
    Initialize config and status related variables

    Returns:
    None
    """
    global silent_output
    global status_expiry_date
    global status_emoji
    global meeting_status_emoji

    silent_output = config.get('silentOutput', True)
    status_expiry_date = int(
        datetime.now().replace(hour=23, minute=59, second=59).timestamp())  # Until tonight
    status_emoji = config.get('statusEmoji', ':speech_balloon:')
    meeting_status_emoji = config.get('meetingStatusEmoji', ':calendar:')


def create_status_message(time_windows: List[Tuple[datetime, datetime]],
        meetings: List[Tuple[datetime, datetime]]) -> str:
    """
    Creates the slack status message from the inputs gathered

    Parameters:
    time_windows: List[Tuple[datetime, datetime]] - The available time windows
        with breaks creating gaps
    meetings: List[Tuple[datetime, datetime]] - Additional time windows
        representing meetings

    Returns:
    A string containing the final status message
    """

    status_message = ""

    # Add comma separated time windows' hours
    index = 0
    for time_window in time_windows:
        status_message += \
            f"{time_window[0].strftime('%H:%M')} - {time_window[1].strftime('%H:%M')}"

        if index < len(time_windows) - 1:
            status_message += ', '

        index += 1

    # Add meetings if they are apparent
    if meetings:
        status_message += f' ({meeting_status_emoji} '

        index = 0
        for meeting in meetings:
            status_message += f"{meeting[0].strftime('%H:%M')} - {meeting[1].strftime('%H:%M')}"
            if index < len(meetings) - 1:
                status_message += ', '

            index += 1

        status_message += ')'

    return status_message


def get_half_manual_input() -> str:
    """
    From fix time formatted user inputs, creates a slack status.
    Asks for boundaries, breaks and meetings.

    Returns:
    The formatted status (f.e. 08:00 - 09:00, 10:00 -16:00)
    """

    # We need to keep track of available time windows we can insert breaks or meetings into
    available_windows = []

    # We also keep track of the windows outside of meetings
    # this will be present in the slack status before the meetings' listing
    time_windows = []

    # Get start and end time - ask if we want to get it automatically
    if utils.get_boolean_input("Would you like to add start and end time automatically? " +
            "(starts from next 15 minutes, ends in + 8:30 hours)"):

        # Round to next 15 minutes
        now = datetime.now()
        if now.minute > 0 and now.minute <= 15:
            start_time = now.replace(minute=15)
        elif now.minute > 15 and now.minute <= 30:
            start_time = now.replace(minute=30)
        elif now.minute > 30 and now.minute <= 45:
            start_time = now.replace(minute=45)
        elif now.minute > 45 or now.minute == 0:
            start_time = now.replace(minute=0) + timedelta(hours=1)
        else:
            raise Exception(f"Unknown case for minute: {now.minute}")

        # End time: start + 8 and a half hours
        end_time = start_time + timedelta(hours=8, minutes=30)

    else:
        # Get start time as python datetime
        start_time = utils.get_hour_input(
            'Set the starting time of the status',
            available_windows
        )

        # Get end time as python datetime
        end_time = utils.get_hour_input(
            'Set the ending time of the status',
            available_windows,
            after_than=start_time
        )

    # Add the set limits as tuple of the only available and time window
    available_windows.append((start_time, end_time))
    time_windows.append((start_time, end_time))

    # Print current status
    meetings = []
    status_message = create_status_message(time_windows, meetings)

    # Get meetings - ask if we want to load it from integration first
    prompt = "Would you like to add meetings from integrations first? "
    prompt += f"Current status is: {status_message}."
    if utils.get_boolean_input(prompt):
        integration_meetings = get_meetings_from_integrations()
        for int_meeting in integration_meetings:

            # Add the new meeting to the list and the re-sort
            meetings.append(int_meeting)
            meetings.sort(key=lambda x: x[0])

            # Alter available windows (but not time windows) based on the new meeting
            available_windows = utils.add_new_window(int_meeting, available_windows)

            # Calculate status message with each iteration
            # so we can prompt to the user how it's changing
            status_message = create_status_message(time_windows, meetings)

    # Get meetings - we ask for each if the user wants to add yet another
    status_message = create_status_message(time_windows, meetings)
    while True:
        prompt_part = "a" if len(meetings) == 0 else "another"
        prompt = f"Would you like to add {prompt_part} meeting? "
        prompt += f"Current status is: {status_message}."

        if not utils.get_boolean_input(prompt):
            break

        meeting_start = utils.get_hour_input(
            'Set the starting time of the meeting',
            available_windows
        )

        meeting_end = utils.get_hour_input(
            'Set the ending time of the meeting',
            available_windows,
            after_than=meeting_start
        )

        # Add the new meeting to the list and the re-sort
        new_meeting = (meeting_start, meeting_end)
        meetings.append(new_meeting)
        meetings.sort(key=lambda x: x[0])

        # Alter available windows (but not time windows) based on the new meeting
        available_windows = utils.add_new_window(new_meeting, available_windows)

        # Calculate status message with each iteration
        # so we can prompt to the user how it's changing
        status_message = create_status_message(time_windows, meetings)

    # Get breaks - we ask for each if the user wants to add yet another
    first_break = True
    while True:
        prompt_part = "a" if first_break else "another"
        prompt = f"Would you like to add {prompt_part} break? "
        prompt += f"Current status is: {status_message}."

        if not utils.get_boolean_input(prompt):
            break

        break_start = utils.get_hour_input(
            'Set the starting time of the break',
            available_windows
        )

        break_end = utils.get_hour_input(
            'Set the ending time of the break',
            available_windows,
            after_than=break_start
        )

        # Add the new meeting to the list
        new_break = (break_start, break_end)

        # Alter available windows and time windows too, based on the new break
        available_windows = utils.add_new_window(new_break, available_windows)
        time_windows = utils.add_new_window(new_break, time_windows)
        if first_break:
            first_break = False

        # Calculate status message with each iteration
        # so we can prompt to the user how it's changing
        status_message = create_status_message(time_windows, meetings)

    return status_message


def get_meetings_from_integrations() -> List[Tuple[datetime, datetime]]:
    """
        Uses integrations to get the meetings in a list

        Returns:
        The list of the time windows as the meetings, f.e. [(08:00 - 09:00), (10:00, 10:30)]
        Overlapping is not checked or handled.
    """

    meeting_list = []

    # Google calendar meetings - if it is present among the integrations
    if 'google-calendar' in config['integrations']:

        # Go through each integration
        index = 0
        for google_calendar_integration in config['integrations']['google-calendar']:

            # Only load it if it is enabled
            if google_calendar_integration['enabled'] is True:

                print(f"Getting meetings from {index+1}. Google Calendar API...")

                # Get meetings
                google_meetings = google_calendar.get_meetings(
                    google_calendar_integration['credentials'],
                    index
                )

                # Parse meetings
                meeting_list.extend(utils.parse_google_meetings(google_meetings))

                index += 1
                print("Done!")

    # Azure teams meetings - if it is present among the integrations
    if 'azure-teams' in config['integrations']:

        # Go through each integration
        index = 0
        for azure_teams_integration in config['integrations']['azure-teams']:

            # Only load it if it is enabled
            if azure_teams_integration['enabled'] is True:

                print(f"Getting meetings from {index+1}. Azure Teams API...")

                # Get meetings
                teams_meetings = azure_teams.get_meetings(
                    azure_teams_integration['credentials']
                )

                # Parse meetings
                meeting_list.extend(utils.parse_teams_meetings(
                    teams_meetings,
                    config['localTimeZone']
                ))

                index += 1
                print("Done!")

    # Remove duplicates from list
    meeting_list = list(dict.fromkeys(meeting_list))

    return meeting_list


def get_vacation_status(until_date: datetime) -> str:
    """
    Produces a status message and sets certain configurations for the vacation status.

    Parameters:
    until_date: datetime - The date until the vacation lasts.

    Returns:
    The status message to be set
    """

    global status_expiry_date
    global status_emoji

    status_expiry_date = int(
        until_date.replace(hour=23, minute=59, second=59).timestamp())  # Until last day of vacation
    status_emoji = config['vacation'].get('statusEmoji', ':palm_tree:')

    # Get next day to be clear in the status when thevacation ends
    next_day = until_date + timedelta(days=1)

    return f"On vacation. Will be back on {next_day.month}/{next_day.day}"


def set_slack_status(slack_status: str) -> None:
    """
    Sets the given status text to all workspaces defined in config

    Parameters:
    slack_status: str - The status to be set.

    Returns:
    None
    """

    # Loop through the api tokens provided in the config
    token_number = 0
    for token_number in range(len(config['slackApiTokens'])):
        print(f"Configuring the {token_number + 1}. workspace...")

        # Send the request to slack
        slack_response = slack.set_user_status(
            token=config["slackApiTokens"][token_number],
            status_message=status_message,
            status_emoji=status_emoji,
            status_expiry_date=status_expiry_date,
            user_id=config['slackUserIds'][token_number]
        )

        # Log if it's not silenced
        if not silent_output:
            print('Slack response:')
            print(slack_response)

        # Handle response
        slack_response_status = slack_response.get('ok', False)
        if slack_response_status is False:
            slack_response_error = slack_response.get('error',
                'Error not present in slack response!')
            print(f'Error on setting slack status: {slack_response_error}')
        else:
            print('Done')

        token_number += 1


if __name__ == '__main__':

    # Read and set configuration into the global variables
    config = file.read_configuration()
    set_configuration()

    # Check if vacation is supposed to be set based on the configuration
    vacation_set = False
    if 'vacation' in config and 'untilDate' in config['vacation']:
        vacation_until = datetime.strptime(config['vacation']['untilDate'], '%Y-%m-%d')

        # Set vacation if it's set to the future in the config
        if vacation_until > datetime.now():
            print(f"Vacation set in config until {config['vacation']['untilDate']}")
            status_message = get_vacation_status(vacation_until)
            vacation_set = True

    if not vacation_set:

        # Set base value for decisions
        input_manually = False
        input_fully_manually = False

        # Check if the user wants to set the status fully manually (free text)
        # or half manually (setting boundaries, meetings with fix time formats)
        if utils.get_boolean_input("Do you want to set the status partially automatically?"):
            status_message = get_half_manual_input()
        else:
            status_message = utils.get_text_input("Add the fix status message you want to set:")

    print('')
    print("The final status message will be:")
    print(status_message)
    print('')

    # Set the final status to all workspaces
    set_slack_status(status_message)
