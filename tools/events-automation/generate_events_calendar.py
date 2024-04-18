import datetime
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
from urllib.parse import urlsplit
from event import Event

# TODO: not sure if we will need to modify the calendar events, set to read&modify for now
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Automate loading environment variables in Python script, make them accessible to the project
load_dotenv()

# TODO: this is personal credentials oath2 client ids, so this may need to change later on
OAUTH2_CLIENT_SECRET_CRED = json.loads(os.getenv('CREDENTIALS_JSON', '{}'))

WEDNESDAY_DATETIME_DAY = 2
END_DATE_WEEKS = 4 # Number of weeks to skip

def get_closest_wednesday():
    """
    Returns the closest Wednesday to the current day
    """
    day = datetime.datetime.today()

    while day.weekday() != WEDNESDAY_DATETIME_DAY:
        day += datetime.timedelta(days=1)
    
    return day

def get_desired_date_range():
    """
    Returns datetime.datetime for the next closest Wednesday, and the Wednesday that 
    is four weeks later.
    """
    closest_wednesday = get_closest_wednesday()

    # We add END_DATE_WEEKS, and 1 day because Meetup requires DAY+1 for proper querying
    end_date = closest_wednesday + datetime.timedelta(weeks=END_DATE_WEEKS, days=1) 

    return closest_wednesday, end_date

def authenticate() -> list[:]:
    """
    Authenticates with the Google API, queries the Google Calendar API, and returns a list of events
    :rtype: list[]
    """
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
        # Get the desired date range in RFC3339 format with time zone offset, which with UTC timezone information
        timeMin, timeMax = get_desired_date_range()
        timeMin = datetime.datetime(timeMin.year, timeMin.month, timeMin.day, tzinfo=datetime.timezone.utc)
        timeMax = datetime.datetime(timeMax.year, timeMax.month, timeMax.day, tzinfo=datetime.timezone.utc)
        calendars_result = service.events().list(
            calendarId="apd9vmbc22egenmtu5l6c5jbfc@group.calendar.google.com",
            timeMin=timeMin.isoformat(), 
            timeMax=timeMax.isoformat(), 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return calendars_result.get("items", [])
    except HttpError as error:
        print(f"An error occurred: {error}")

def get_events() -> list[Event]:
    """
    Returns a list of Event objects converted from Google Calendar events.
    :rtype: list[Event]
    """
    event_list = list()
    events = authenticate()
    for event in events:
        # Event(name, location, date, url, virtual, organizerName, organizerUrl, duplicate=False)
        name = event.get("summary", "No title")
        location = event.get("location", event["start"].get("timeZone", "No location"))
        date = datetime.datetime.fromisoformat(event["start"].get("dateTime", event["start"].get("date")))
        description = event.get("description", "No description")
        virtual = True # update the Event attribute virtual to True, False, None
        organizerUrl = "No URL"
        organizerName = "No organizer"
        url = get_URLs(description)
        if url == "No URL":
            url = get_URLs(location)
            if url == "No URL":
                virtual = False
        
        if url != "No URL":
            # TODO: Get the organizerURL, then extract the group name
            # Format: [source](https://stackoverflow.com/questions/35616434/how-can-i-get-the-base-of-a-url-in-python)
            # https://www.meetup.com/seattle-rust-user-group/...
            # split_url.scheme   "http"
            # split_url.netloc   "www.meetup.com" 
            # split_url.path     "/seattle-rust-user-group/..."
            split_url = urlsplit(url)
            clean_path = "/".join((split_url.path).split("/")[:2])
            organizerUrl = split_url.scheme + "://" + split_url.netloc + clean_path
            organizerName = (split_url.path).split("/")[1]
            # TODO: Checking if the organizerName is valid name
            if organizerName == "about" or organizerName == "event":
                organizerName = event["organizer"].get("displayName", "No organizer")

        event_list.append(Event(name, location, date, url, virtual, organizerName, organizerUrl))
    return event_list

def get_URLs(text) -> str:
    """
    Returns the first valid URL found in the text.
    :type text: str
    :rtype: str
    """
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