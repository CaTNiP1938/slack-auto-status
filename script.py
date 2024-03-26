"""
    Contains the main runnable file that sets the slack status.
"""

from datetime import datetime
from typing import List, Tuple

from integrations import slack

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
    global status_message
    global status_expiry_date
    global status_emoji
    global meeting_status_emoji

    silent_output = config.get('silentOutput', True)
    status_message = ""
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

    # Get meetings - we ask for each if the user wants to add yet another
    meetings = []
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

        # Add the new meeting to the list
        new_meeting = (meeting_start, meeting_end)
        meetings.append(new_meeting)

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

    # Set base value for decisions
    input_manually = False
    input_fully_manually = False

    # Only ask the base questions if the input is not already done by updating
    if not input_update:

        # Check if the user wants to set the status manually
        # (either fully or by asking for the boundaries, meetings)
        if utils.get_boolean_input("Do you want to set the status manually?"):

            # Check if the user wants to set the status fully manually (free text)
            # or half manually (setting boundaries, meetings with fix time formats)
            if utils.get_boolean_input(
                    "Do you want to set the status FULLY manually with a free text?"):
                status_message = utils.get_text_input("Add the fix status message you want to set:")
            else:
                status_message = get_half_manual_input()

        # Fully automated status: boundaries are set based on time,
        # meetings are based on config + integration
        else:
            raise NotImplementedError()

    # TODO: Remove these
    print('')
    print("The final status message will be:")
    print(status_message)
    print('')

    # Set the final status to all workspaces
    set_slack_status(status_message)