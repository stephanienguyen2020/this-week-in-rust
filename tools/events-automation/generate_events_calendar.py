import datetime
import os.path
import json
import os
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from event import Event

# TODO: not sure if we will need to modify the calendar events, set to read&modify for now
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Automate loading environment variables in Python script, make them accessible to the project
load_dotenv()

# TODO: this is personal credentials oath2 client ids, so this may need to change later on
OAUTH2_CLIENT_SECRET_CRED = json.loads(os.getenv('CREDENTIALS_JSON', '{}'))

def authenticate() -> list[:]:
    creds = None
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
            flow = InstalledAppFlow.flow = InstalledAppFlow.from_client_config(OAUTH2_CLIENT_SECRET_CRED, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials by open token.json, and write creds into file
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    try:
        service = build("calendar", "v3", credentials=creds)

        # TODO: Call the Calendar API, queries all events from closest Wednesday to the next 4 weeks
        calendars_result = service.events().list(
            calendarId="apd9vmbc22egenmtu5l6c5jbfc@group.calendar.google.com",
            timeMin='2024-03-14T06:00:00-07:00', 
            timeMax='2024-03-23T06:00:00-07:00', 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return calendars_result.get("items", [])
    except HttpError as error:
        print(f"An error occurred: {error}")

# TODO: Implement the function to return list of google.events into list of generic type Event
def get_events() -> list[Event]:
    event_list = list()
    events = authenticate()
    for event in events:
        # name, location, date, url, virtual, organizerName, maybeSpam
        name = event.get("summary", "No title")
        location = event.get("location", event["start"].get("timeZone", "No location"))
        date = event["start"].get("dateTime", event["start"].get("date"))
        description = event.get("description", "No description")
        virtual = True
        organizerName = event["organizer"].get("displayName", "No organizer")
        maybeSpam = False

        url = get_URLs(description)
        if url == "No URL":
            url = get_URLs(location)
            if url == "No URL":
                virtual = False

        # Check what info missing should be consider the event is spam?
        
        print(date,  " | ", name, " | ", location, " \n ", organizerName,  " | ", url)
        print(f"Virtual: {virtual}", " | ", maybeSpam)
        print()
        event_list.append(Event(name, location, date, url, virtual, organizerName, maybeSpam))

    return event_list

def get_URLs(text) -> str:
    soup = BeautifulSoup(text, "html.parser")
    link = soup.find('a')
    if link:
        return link.get("href")

    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    href_vals = re.findall(url_pattern, text)
    for url in href_vals:
        parsed_url = urlparse(url)
        # if the url is valid
        if bool(parsed_url.scheme) and bool(parsed_url.netloc): 
            return url
    return "No URL"

print(get_events())