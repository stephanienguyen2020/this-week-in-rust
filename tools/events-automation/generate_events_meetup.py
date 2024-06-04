import requests
import datetime
import concurrent.futures
import pandas as pd

from jwt_auth import generate_signed_jwt
from urllib.parse import urlsplit
from event import Event

def authenticate():
    URL = "https://secure.meetup.com/oauth2/access"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": generate_signed_jwt()
    }
    response = requests.post(url=URL, headers=headers, data=body)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")
        return access_token, refresh_token
    else:
        print("Failed to obtain access token")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return None, None

def fetch_groups(endCursor=""):
    URL = "https://api.meetup.com/gql"
    access_token, refresh_token = authenticate()

    if not access_token:
        print("Authentication failed, cannot proceed to fetch events.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = {
        "query": """
        query (
            $searchGroupInput: ConnectionInput!, 
            $searchGroupFilter: SearchConnectionFilter!,
            $sortOrder: KeywordSort!
        ) {
            keywordSearch(
                input: $searchGroupInput, 
                filter: $searchGroupFilter,
                sort: $sortOrder
            ) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                edges {
                    node {
                        result {
                            ... on Group {
                                id
                                name
                                link
                                urlname
                                latitude
                                longitude
                            }
                        }
                    }
                }
            }
        }
        """,
        "variables": {
            "searchGroupFilter": {
                "query": "Rust",
                "lat": 0.0,
                "lon": 0.0,
                "radius": 20000,
                "source": "GROUPS"
            },
            "searchGroupInput": {
                "first": 200,
                "after": endCursor
            },
            "sortOrder":{
                "sortField": "RELEVANCE"
            }
        }
    }
    return requests.post(url=URL, headers=headers, json=data)

def get_rush_groups():
    """
    Return a dictionary of groups
    """
    endCursor = None
    groups = dict()
    while True:
        response = fetch_groups(endCursor).json()
        data = response['data']
        edges = data['keywordSearch']['edges']
        pageInfo = data['keywordSearch']['pageInfo']
        for node in edges:
            group = node["node"]["result"]
            if not (group["id"] in groups):
                groups[group["id"]] = group
        if pageInfo['hasNextPage']:
            endCursor = pageInfo['endCursor']
        else:
            break
    return groups

def get_known_rush_groups(fileName):
    """
    Read url and location of groups. Extract the urlname from the url
    Return a dictionary of groups
    """
    groups = dict()
    df = pd.read_csv(fileName, header=0, usecols=['url', 'location'])

    # Format: [source](https://stackoverflow.com/questions/35616434/how-can-i-get-the-base-of-a-url-in-python)
    # https://www.meetup.com/seattle-rust-user-group/
    # split_url.scheme   "http"
    # split_url.netloc   "www.meetup.com" 
    # split_url.path     "/seattle-rust-user-group/"
    for index, row in df.iterrows():
        group = {}
        group["link"] = row["url"]
        split_url = urlsplit(group["link"])
        group["urlname"] = (split_url.path).replace("/", "")
        group["location"] = row["location"]
        groups[index] = group
    return groups

def get_20_events(groups) -> list[Event]:
    # TODO: Make sure list of 20 events has all values for list of Event
    events = []
    URL = "https://api.meetup.com/gql"
    access_token, refresh_token = authenticate()

    if not access_token:
        print("Authentication failed, cannot proceed to fetch events.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {}
    count = 1
    for group in groups.values():
        urlName = group["urlname"]
        data = {
            "query": """
            query ($urlName: String!, $searchEventInput: ConnectionInput!) {
                groupByUrlname(urlname: $urlName) {
                    upcomingEvents(input: $searchEventInput, sortOrder: ASC) {
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                        edges {
                            node {
                                id
                                title
                                dateTime
                                eventUrl
                                venue {
                                    venueType
                                    lat
                                    lng
                                }
                            }
                        }
                    }
                }
            }
            """,
            "variables": {
                "urlName": urlName,
                "searchEventInput": {
                    "first": 20
                }
            }
        }
        response = requests.post(url=URL, headers=headers, json=data)
        data = response.json()["data"]

        if data:
            searchGroupByUrlname = data["groupByUrlname"]
            if searchGroupByUrlname:
                edges = searchGroupByUrlname["upcomingEvents"]["edges"]
                if edges:
                    for edge in edges:
                        node = edge["node"]
                        if node:
                            name = node["title"]
                            lat, lng = 0, 0
                            virtual = True
                            venue = node["venue"]
                            # TODO: What if venue is None? would it consider as spam event?
                            if venue:
                                lat, lng = venue["lat"], venue["lng"] # set to location?
                                if venue["venueType"] != "online":
                                    virtual = False
                            location = f"{lat}, {lng}"
                            date = node["dateTime"]
                            url = node["eventUrl"]
                            organizerName = group.get("name", urlName)
                            organizerUrl = group["link"]
                            # print(f"Event({name}, location={location}\ndate={date}, url={url}, virtual={virtual}\norganizerName={organizerName}, organizerUrl={organizerUrl}\n")
                            events.append(Event(name, location, date, url, virtual, organizerName, organizerUrl))
    return events

def get_events() -> list[Event]:
    # TODO: get list of events from Meetup and known Rush groups, and combine two list together
    # return the event source
    # groups = get_rush_groups()
    events_meetup_groups = get_20_events(get_rush_groups())
    # groups = get_known_rush_groups("rust_meetup_groups.csv")
    events_known_groups = get_20_events(get_known_rush_groups("rust_meetup_groups.csv"))
    return events_meetup_groups + events_known_groups

print(len(get_events()))