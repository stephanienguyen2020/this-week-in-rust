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

# Usage
drafts_folder = 'draft/'
draft_reader = DraftReader(drafts_folder)
newest_draft = draft_reader.find_newest_draft()

# Print Newest Draft
if newest_draft:
    draft_reader.read_and_print_file(os.path.join(drafts_folder, newest_draft))
else:
    print("No draft files found.")