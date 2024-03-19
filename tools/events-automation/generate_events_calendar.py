import datetime
import os.path
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# TODO: not sure if we will need to modify the calendar events, set to read&modify for now
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Automate loading environment variables in Python script, make them accessible to the project
load_dotenv()

# TODO: this is personal credentials oath2 client ids, so this may need to change later on
OAUTH2_CLIENT_SECRET_CRED = json.loads(os.environ['CREDENTIALS_JSON'])
creds = None

def main():
    authenticate()
    try:
        service = build("calendar", "v3", credentials=creds)

        # TODO: Call the Calendar API, queries all events from closest Wednesday to the next 4 weeks
        # events_result = list()
        
    except HttpError as error:
        print(f"An error occurred: {error}")

def authenticate():
    # Credential authentication one time creates token.json automatically when the authorization flow completes, so we don't have to authenticate every time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # If has creds, but it's expired, refresh them
            creds.refresh(Request())
        else:
            # If creds not exist, let user login via the Oauth flow
            flow = InstalledAppFlow.flow = InstalledAppFlow.from_client_secrets_file(OAUTH2_CLIENT_SECRET_CRED, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials by open token.json, and write creds into file
        with open("token.json", "w") as token:
            token.write(creds.to_json())

# TODO: Implement the function to return list of google.events into list of generic type Event
# def get_events(events): -> List[Event]: