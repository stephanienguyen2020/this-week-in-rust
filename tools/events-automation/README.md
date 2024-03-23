# Documentation

This is guidelines for developer

## How to use get_events() from Rust Community Calendar

We are using Google Calendar API to query all events within desired range from Rust Community Calendar

To use the function you need to follow Google Calendar quickstart document to meet the prerequisites: 
* [Google Cloud project](https://developers.google.com/workspace/guides/create-project)
* [Google authorize credentials key](https://developers.google.com/calendar/api/quickstart/python#set_up_your_environment)
(Make sure to add yourself as Test users when you doing the Configure the OAuth consent screen)
* [Google client library](https://developers.google.com/calendar/api/quickstart/python#install_the_google_client_library)

Navigate to the directory of the events-automation:

```
cd /usr/local/src/this-week-in-rust/tools/events-automation/
```

Create an environment:
```
touch .env
```

Create a CREDENTIALS_JSON variable and place the credentials key (from the downloaded credentials.json) as value:
```
CREDENTIALS_JSON=<everything-from-credentials.json>
```

Now you could call get_events() from generate_events_calendar