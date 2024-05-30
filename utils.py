"""
    Contains some utility functions used by the main 'script.py' file
"""

import re

from datetime import datetime
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo

import file


def is_input_an_hour(input: str) -> bool:
    """
    Check if input is in hh:mm format

    Parameters:
    input: str - The input to check

    Returns:
    True if the input matches the hh:mm, False otherwise
    """

    pattern = re.compile("^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")
    return pattern.match(input)


def get_boolean_input(prompt: str) -> bool:
    """
    Reads input from user until their anwser can
    be interpreted as a boolean value

    Parameters:
    prompt: str - The text that will appear in the terminal
        before the input is taken

    Returns:
    The boolean value set by the user
    """

    print(prompt + " (y/n)")
    user_input = input()
    while user_input != 'y' and user_input != 'n':
        print("Invalid input, please choose: y/n")
        user_input = input()

    return True if user_input == 'y' else False


def get_text_input(prompt: str) -> str:
    """
    Reads input from user until their anwser can
    be interpreted as a text value

    Parameters:
    prompt: str - The text that will appear in the terminal
        before the input is taken

    Returns:
    The text value set by the user
    """

    print(prompt)
    user_input = input()
    while not user_input:
        print("Invalid input, please add text")
        user_input = input()

    return user_input


def get_hour_input(
        prompt: str, available_windows: List[Tuple[datetime, datetime]] = None,
        after_than: datetime = None) -> datetime:
    """
    Reads input from user until their anwser can
    be interpreted as an hour that applies to the conditions

    Parameters:
    prompt: str - The text that will appear in the terminal
        before the input is taken
    available_windows: List[Tuple[datetime, datetime]] - List of windows that are still
        available to take. If set, input is checkd if it's inside these windows.
        f.e. [Tuple(08:00, 10:00), Tuple(11:00, 12:00)]
        (the hour is checkedwith the day set as today)
    after_than: datetime - If set, only an hour after the parameter (equal is fine)
        will count as a valid option (with the day set as today)

    Returns:
    A datetime object set for today as the day and the
    hours and minutes coming from the input
    """

    print(prompt + " (hh:mm)")

    # Set up a forever loop, exit if the input is valid
    while True:

        # Get user input
        user_input = input()

        # If input is not in the valid format: continue
        if not is_input_an_hour(user_input):
            print("Invalid input, please set: hh:mm")
            continue

        # Convert input into python datetime object
        datetime_input = __convert_hour_input(user_input)

        # Check if input is in windows, with or without after_than being set
        if not __check_input_in_windows(datetime_input, available_windows, after_than):
            print(__get_windows_error_message(available_windows, after_than))
            continue

        # If haven't continued so far: break
        break

    # Convert hour input into datetime object
    input_datetime_input = __convert_hour_input(user_input)
    return input_datetime_input


def __convert_hour_input(input: str) -> datetime:
    """
    Converts hour input text (hh:mm) as python datetime

    Parameters:
    input: str - The text input taken from the user (format is "hh:mm")

    Returns:
    A datetime object set for today as the day and the
    hours and minutes coming from the input
    """

    hour_only = int(input.split(':')[0])
    minute_only = int(input.split(':')[1])
    return datetime.now().replace(hour=hour_only, minute=minute_only, second=0, microsecond=0)


def __check_input_in_windows(input: datetime,
        windows: List[Tuple[datetime, datetime]], after_than: datetime = None) -> bool:
    """
    Checks if input is in one of the windows specified

    Parameters:
    input: datetime - The input time to be checked
    windows: List[Tuple[datetime, datetime]] - The time windows the input
        needs to be checked against
    after_than: datetime - If this parameter is set, it means we have a start time already,
        and need to check the input to be after this time as well

    Returns:
    A boolean value depicting if the time is in one of the windows or not
    Comparison is loose (lesser/greater or equal is used)
    """

    # If windows is empty, return true, unless after_than is set, then we need to check that
    if len(windows) == 0:
        return input >= after_than if after_than else True

    # Treat separately, if after_than parameter is set
    if after_than:

        # If there are windows, only the one where after_than is, matters
        for window in windows:
            if after_than >= window[0] and after_than <= window[1]:
                return input >= after_than and input <= window[1]

    else:
        for window in windows:
            if input >= window[0] and input <= window[1]:
                return True

        return False


def __get_windows_error_message(windows: List[Tuple[datetime, datetime]],
        after_than: datetime = None) -> str:
    """
    Constructs the error message if the input has failed the conditions

    Parameters:
    windows: List[Tuple[datetime, datetime]] - The time windows the input was checked against
    after_than: datetime - If this parameter is set, it means we have a start time already,
        and have to construct this into the error message as well

    Returns:
    The error message to be thrown back to the user
    """

    # Treat separately, if after_than parameter is set
    if after_than:

        # If windows is empty, only the after_than confition could have been failed
        if len(windows) == 0:
            return f"Time must be after {after_than.strftime('%H:%M')}"

        # If there are windows, only the one where after_than is, matters
        for window in windows:
            if after_than >= window[0] and after_than <= window[1]:
                return f"Time must be after {after_than.strftime('%H:%M')} " + \
                    f"and before {window[1].strftime('%H:%M')}"

    else:
        error_message = "Time must be between one of these windows: "

        index = 0
        for window in windows:
            error_message += f"{window[0].strftime('%H:%M')} - {window[1].strftime('%H:%M')}"

            if index < len(windows) - 1:
                error_message += ", "

            index += 1

    return error_message


def add_new_window(new_window: Tuple[datetime, datetime],
        windows: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
    """
    Merges a new time window into the list of time windows

    Parameters:
    new_window: Tuple[datetime, datetime] - The new time window to be merged
    windows: List[Tuple[datetime, datetime]] - The list of time windows to be merged

    Returns:
    The list with the added time window. For example, from (08:00 - 16:00)
    with (10:00 - 11:00), becomes (08:00 - 10:00), (11:00 - 16:00)
    """

    if len(windows) == 0:
        windows.append(new_window)
        return windows

    index = 0
    for window in windows:
        if new_window[0] >= window[0] and new_window[0] <= window[1]:

            # Append new entry to the next position
            windows.insert(index+1, (new_window[1], window[1]))

            # Alter current windows' end
            windows[index] = (window[0], new_window[0])

            break
        index += 1

    # Delete windows where the starting and ending time is the same
    windows = [tup for tup in windows if tup[0] != tup[1]]

    return windows


def get_old_status() -> None | str:
    """
    Get old status if it exists in the status file

    Parameters:
    None

    Returns:
    None, if the status file does not exist or it's not for today.
    The status message otherwise.
    """

    old_status = file.read_status_file()
    current_month = datetime.now().month
    current_day = datetime.now().day
    if old_status is not False and old_status[0] == current_month and old_status[1] == current_day:
        return old_status[2]
    else:
        return None


def parse_google_meetings(google_meetings: List[Dict]) \
        -> List[Tuple[datetime, datetime]]:
    """
        Utility function to parse meetings coming from google calendar API

        Parameters:
        google_meetings: List[Dict] - The raw meetings input from google

        Returns:
        All meetings for the current day with their start and end time.
    """

    # Initialize return list
    return_list = []

    # Return on empty list or None object
    if not google_meetings:
        return return_list

    # Get start and end date for each meeting
    for meeting in google_meetings:

        # Get start end end dates
        start = meeting["start"].get("dateTime", meeting["start"].get("date"))
        end = meeting["end"].get("dateTime", meeting["end"].get("date"))

        # If the times are saved with timezone, we cut it
        start = start.split('+')[0]
        end = end.split('+')[0]

        # Convert to datetime
        try:
            start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            start = datetime.strptime(start, '%Y-%m-%d')

        try:
            end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            end = datetime.strptime(end, '%Y-%m-%d')

        # If meeting is not for today, skip it
        now = datetime.now()
        if now.month != start.month or now.day != start.day:
            continue

        return_list.append((start, end))

    return return_list


def parse_teams_meetings(teams_meetings: List[Dict], time_zone: str) -> \
        List[Tuple[datetime, datetime]]:
    """
        Utility function to parse meetings coming from azure teams API

        Parameters:
        teams_meetings: List[Dict] - The raw meetings input from teams
        time_zone: str - The timezone string (f.e. 'Europe/Amsterdam'). The dates are converted
            using the timezone since teams sends the dates in UTC.

        Returns:
        All meetings for the current day with their start and end time.
    """

    # Initialize return list
    return_list = []

    # Return on empty list or None object
    if not teams_meetings:
        return return_list

    # Get start and end date for each meeting
    for meeting in teams_meetings:

        # Get start end end dates
        start = meeting["start"].get("dateTime", meeting["start"].get("date"))
        end = meeting["end"].get("dateTime", meeting["end"].get("date"))

        # Cut the millisecond from the times
        start = start.split('.')[0]
        end = end.split('.')[0]

        # Convert to datetime
        utc = ZoneInfo('UTC')
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=utc)
        end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=utc)

        # Apply timezone from param
        param_tz = ZoneInfo(time_zone)
        start = start.astimezone(param_tz).replace(tzinfo=None)
        end = end.astimezone(param_tz).replace(tzinfo=None)

        # If meeting is not for today, skip it
        now = datetime.now()
        if now.year != start.year or now.month != start.month or now.day != start.day:
            continue

        return_list.append((start, end))

    return return_list
