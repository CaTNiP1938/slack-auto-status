import datetime
import os.path

from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file google_token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_meetings(config_credentials: Dict) -> List[Dict]:
    """
        Connects to the Google Calendar API, authenticates via web browser,
        and returns the next 10 events (meetings) for the user

        Parameters:
        config_credentials: Dict - The credentials required for authentication

        Returns:
        A list of event dictionaries from the Google Calendar API
    """

    creds = None

    # The file google_token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists("integrations/google_token.json"):
        creds = Credentials.from_authorized_user_file("integrations/google_token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                config_credentials, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("integrations/google_token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise
