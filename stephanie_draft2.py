import os
import re
from datetime import datetime

class DraftReader:
    def __init__(self, drafts_folder):
        self.drafts_folder = drafts_folder

    def find_newest_draft(self):
        date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}-this-week-in-rust.md')
        valid_files = [file for file in os.listdir(self.drafts_folder) if date_pattern.match(file)]
        valid_files.sort(reverse=True)
        return valid_files[0] if valid_files else None

    def read_and_print_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(content)
        except FileNotFoundError:
            print("File not found. Please check the file path and try again.")

class Event:
    def __init__(self, name, location, date, url, virtual, organizerName, maybeSpam, popularity=None, recurring=None, inPast=None):
        self.name = name
        self.location = location
        self.date = date
        self.url = url
        self.virtual = virtual
        self.organizerName = organizerName
        self.popularity = popularity
        self.recurring = recurring
        self.inPast = inPast
        self.maybeSpam = maybeSpam

    def get_name(self):
        return f"Name: {self.name}"

    def get_location(self):
        return f"Location: {self.location}"

    def get_date(self):
        return f"Date: {self.date}"

    def get_url(self):
        return f"URL: {self.url}"

    def is_virtual(self):
        return f"Virtual: {self.virtual}"

    def get_organizer_name(self):
        return f"Organizer Name: {self.organizerName}"

    def get_popularity(self):
        return f"Popularity: {self.popularity}" if self.popularity else "Popularity: Unknown"

    def is_recurring(self):
        return f"Recurring: {self.recurring}"

    def is_in_past(self):
        return "In Past: Yes" if self.inPast else "In Past: No"

    def is_maybe_spam(self):
        return f"Maybe Spam: {self.maybeSpam}"

    def event_details(self):
        details = [
            self.get_name(), 
            self.get_location(), 
            self.get_date(),
            self.get_url(),
            self.is_virtual(),
            self.get_organizer_name(),
            self.get_popularity(),
            self.is_recurring(),
            self.is_in_past(),
            self.is_maybe_spam()
        ]
        return "\n".join(details)

    def __repr__(self):
        return self.event_details()

# Regex patterns for the event details
def parse_events(text):
    event_pattern = re.compile(r'^\*\s+(?P<date>\d{4}-\d{2}-\d{2})\s+\|\s+(?P<location>[^|]+?)\s+\|\s+\[(?P<name>[^\]]+)\]\((?P<url>http[^)]+)\)')
    
    events = []
    lines = text.split('\n')
    lines = iter(lines)
    for line in lines:
        if 'Upcoming Events' in line:
            break

    for line in lines:
        match = event_pattern.match(line.strip())
        if match:
            date = datetime.strptime(match.group('date'), '%Y-%m-%d').date()
            location = match.group('location').strip()
            name = match.group('name').strip()
            url = match.group('url').strip()
            virtual = "Virtual" in location

            # Placeholder values for additional attributes
            organizerName = "Placeholder Organizer"
            popularity = None
            recurring = False
            inPast = date < datetime.now().date()
            maybeSpam = False

            events.append(Event(name, location, date, url, virtual, organizerName, maybeSpam, popularity, recurring, inPast))

    return events

# Usage
drafts_folder = 'draft/'
draft_reader = DraftReader(drafts_folder)
newest_draft = draft_reader.find_newest_draft()

if newest_draft:
    draft_path = os.path.join(drafts_folder, newest_draft)
    with open(draft_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Pass the content to parse_events function
    parsed_events = parse_events(content)
    for event in parsed_events:
        print(event)  # Or do whatever you need with the event data
else:
    print("No draft files found.")