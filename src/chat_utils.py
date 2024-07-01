from typing import List
from datetime import datetime


ROLES = ["user", "assistant", "info", "system"]


class ChatMessage:
    def __init__(self, role, content):
        if role not in ROLES:
            raise ValueError(f"Role '{role}' not allowed. Choose from: {ROLES}")
        self.role = role
        self.content = content
        self.comment = None
        self.question_id = None


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

    def to_google_sheet_format(self, questionnaire_name):
        """Return the chat history in a format suitable for Google Sheets upload.
        Only upload one sample at a time, i.e. from the last system message to the end."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        question_id = 0
        for message in self.messages:
            if message.role == "system":
                question_id += 1
            message.question_id = question_id
        data = [
            [
                timestamp,
                questionnaire_name,
                message.question_id,
                message.comment,
                message.role,
                message.content,
            ]
            for message in self.messages
        ]
        return data
