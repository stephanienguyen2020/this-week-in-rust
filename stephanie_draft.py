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
    def __init__(self, name, location, date, url, virtual):
        self.name = name
        self.location = location
        self.date = date
        self.url = url
        self.virtual = "Virtual" in location

    def __repr__(self):
        return f"Event(name={self.name}, location={self.location}, date={self.date}, url={self.url}, virtual={self.virtual})"

# Regex patterns for the event details
event_pattern = re.compile(r'^\*\s+(?P<date>\d{4}-\d{2}-\d{2})\s+\|\s+(?P<location>[^|]+?)\s+\|\s+\[(?P<name>[^\]]+)\]\((?P<url>http[^)]+)\)')

def parse_events(text):
    events = []
    lines = text.split('\n')
    
    # Skip all lines until 'Upcoming Events'
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
            events.append(Event(name, location, date, url, virtual))
    
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