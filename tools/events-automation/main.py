# import all the event sources & event sink
# collect all the events from the event sources
# call event sink with our collected events
# print to console / output to file formatted markdown

from test_events import get_test_events
from datetime import date, timedelta
from country_code_to_continent import country_code_to_continent

# TODO: Flagged events list handling.

def main():
    # Get Events list from Event Sources.
    event_list = get_test_events()

    # Format date and location data.
    format_data(event_list)

    # Remove events outside of date range.
    date_window_filter(event_list)

    # Sort remaining events by date, then location.
    event_list.sort(key=lambda event: (event.date, event.location))

    # Flag potential duplicate events.
    potential_duplicate(event_list)
    
    # Group by virtual or by continent.
    event_list = group_virtual_continent(event_list)

    # Output Sorted Event List.
    output_to_screen(event_list)


def output_to_screen(event_list):
    # Outputs sorted Event List to terminal screen.
    # Output Virtual Events:
    if "Virtual" in event_list:
        print("### Virtual:\n")
        output_event_details(event_list["Virtual"])
        del event_list["Virtual"]

    # Output Non-Virtual Events:
    for key, value in dict(sorted(event_list.items())).items():
        print(f'### {key}:\n')
        output_event_details(value)


def output_event_details(event_group):
    # Outputs event details
    for event in event_group:
        if event.duplicate:
            print("** NOTE POTENTIAL DUPLICATE: **")
        print(event.to_markdown_string())
    print()


def format_data(event_list):
    # Formats date and location data into specified format.
    for event in event_list:
        event.format_date()
        event.format_location()


def date_window_filter(event_list):
    # Removes Events that are outside current date window.
    # Date window = closest wednesday + 5 weeks.
    start_date = date.today()
    while start_date.weekday() != 2:
        start_date = start_date + timedelta(days=1)
        
    for event in event_list:
        if not (start_date <= event.date <= start_date + timedelta(weeks=5)):
            event_list.remove(event)


def group_virtual_continent(event_list):
    # Return dictionary of events separated in virtual and by continent.
    separated_event_list = {}

    for event in event_list:
        # Separates Events by Virtual or by Continent
        key = "Virtual" if event.virtual else country_code_to_continent(event.location[-2:])
        separated_event_list.setdefault(key, []).append(event)
    
    return separated_event_list


def potential_duplicate(event_list):
    # Identifies possible duplicate Events within Event List.
    for i in range(len(event_list)):
        for j in range(i+1, len(event_list)):
            if event_list[i].date == event_list[j].date and \
               event_list[i].url == event_list[j].url and \
               event_list[i].name == event_list[j].name and \
               event_list[i].organizerName == event_list[j].organizerName and \
               event_list[i].location == event_list[j].location:
                event_list[i].duplicate = True


if __name__ == "__main__":
    main()
