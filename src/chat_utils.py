from typing import List
from datetime import datetime


class ChatMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content

class ChatBox:
    def __init__(self, messages: List[ChatMessage]):
        self.messages = messages

    def add_messages(self, *messages):
        self.messages += list(messages)

    def remove_last_message(self, role: str):
        """Remove the last message of the given role."""
        for i in range(len(self.messages) - 1, -1, -1):
            if self.messages[i].role == role:
                self.messages.pop(i)
                break

    def replace_last_bot_message(self, new_content):
        """Replace the last bot message with the user's input."""
        for i in range(len(self.messages) - 1, -1, -1):
            if self.messages[i].role == "assistant":
                self.messages[i].content = new_content
                break
        if self.messages[-1].role == "info":
            self.messages.pop()

    def get_display_messages(self):
        """Return messages that are supposed to be displayed in chat window."""
        return [message for message in self.messages if message.role != "system"]

    def to_google_sheet_format(self):
        """Return the chat history in a format suitable for Google Sheets upload.
        Only upload one sample at a time, i.e. from the last system message to the end."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        messages = [message for message in self.messages if message.role != "info"]

        # Find the index of the last system message
        last_system_msg_index = None
        for i, message in enumerate(messages):
            if message.role == "system":
                last_system_msg_index = i

        # If a system message was found, slice the messages list from its index
        if last_system_msg_index is not None:
            messages = messages[last_system_msg_index:]

        data = [[timestamp, message.role, message.content] for message in messages]
        return data