# import all the event sources & event sink
# collect all the events from the event sources
# call event sink with our collected events
# print to console / output to file formatted markdown

from test_events import get_test_events
from generate_events_calendar import get_events

# print(get_test_events())
# Test get_events()
events = get_events()
count = 1
for event in events:
    print(count)
    print(event.date,  " | ", event.name, " | ", event.location, " \n ", event.organizerName,  " | ", event.url)
    print(f"Virtual: {event.virtual}", " | ", event.maybeSpam)
    print("_________________________________________________________________________")
    count+=1