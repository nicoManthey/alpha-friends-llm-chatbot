from typing import List
from datetime import datetime
import dotenv
import os
import sys
import json


class ChatMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class ChatBox:
    def __init__(self, messages: List[ChatMessage]):
        self.messages = messages

    def add_messages(self, messages: List[ChatMessage]):
        self.messages += messages

    def get_display_messages(self):
        """Return messages that are supposed to be displayed in chat window."""
        return [message for message in self.messages if message.role != "system"]

    def to_google_sheet_format(self):
        """Return the chat history in a format suitable for Google Sheets upload."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        messages = [message for message in self.messages if message.role != "info"]
        data = [[timestamp, message.role, message.content] for message in messages]
        return data