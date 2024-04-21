from typing import Dict, List

import requests

from azure.identity import InteractiveBrowserCredential

# Define the scopes for Microsoft Graph API
SCOPES = ['https://graph.microsoft.com/.default']


def get_meetings(config_credentials: Dict) -> List[Dict]:
    """
        Connects to the Azure Teams App, authenticates via web browser,
        and returns all calendar events for the user

        Parameters:
        config_credentials: Dict - The credentials required for authentication

        Returns:
        A list of event dictionaries from the Microsoft Azure API
    """

    # Create the InteractiveBrowserCredential
    interactive_cred = InteractiveBrowserCredential(
        client_id=config_credentials['client_id'],
        tenant_id=config_credentials['tenant_id']
    )

    # Get access token
    access_token = interactive_cred.get_token('https://graph.microsoft.com/.default').token

    # Define endpoint to get calendar events
    graph_api_endpoint = 'https://graph.microsoft.com/v1.0/users/' + \
        f'{config_credentials["user_id"]}/calendar/events'

    # Prepare request headers
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    # Make a GET request to retrieve calendar events
    response = requests.get(graph_api_endpoint, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()['value']
    else:
        print(f"Failed to retrieve calendar events: {response.text}")
        return []
