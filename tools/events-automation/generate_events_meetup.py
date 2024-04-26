import requests
import datetime
import concurrent.futures
import pandas as pd

from generate_token import generate_signed_jwt
from urllib.parse import urlsplit

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