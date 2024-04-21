"""
    Contains all logic regarding to sending requests to the Slack API.
"""

import requests

from typing import Dict


def set_user_status(
        token: str, status_message: str, status_emoji: str,
        status_expiry_date: int, user_id: str) -> Dict[str, any]:
    """
    Send user status setting request to the Slack API

    Parameters:
    token: str - The authorization token (without the "Bearer" tag)
    status_message: str - The text to be set as the status
    status_emoji: str - The emoji appearing for the status next to the profile name.
        It is required to be valid and set in slack format (f.e. :computer:)
    status_expiry_date: int - The POSIX timestamp of the expiration date,
        when the status will be deleted
    user_id - The id of the slack user for the workspace

    Returns:
    The Slack API's response in JSON format
    """

    return requests.post(
        url='https://slack.com/api/users.profile.set',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json={
            'profile': {
                'status_text': status_message,
                'status_emoji': status_emoji,
                'status_expiration': status_expiry_date
            },
            'user': user_id
        }
    ).json()
