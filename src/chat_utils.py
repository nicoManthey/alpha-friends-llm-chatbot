from typing import List
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    INFO = "info"
    SYSTEM = "system"

    @classmethod
    def allowed_roles(cls):
        return [role.value for role in cls]


class ChatMessage:
    def __init__(self, role, content):
        if not isinstance(role, Role):
            raise ValueError(
                f"Role '{role}' not allowed. Choose from: {Role.allowed_roles()}"
            )
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
            if self.messages[i].role == Role.ASSISTANT:
                self.messages[i].content = new_content
                break
        if self.messages[-1].role == Role.INFO:
            self.messages.pop()

    def messages_without_roles(self, *excluded_roles):
        """Return messages excluding those with specified roles."""
        excluded_roles_set = set(excluded_roles)
        return [
            message
            for message in self.messages
            if message.role not in excluded_roles_set
        ]

    def to_google_sheet_format(self, questionnaire_name):
        """Return the chat history in a format suitable for Google Sheets upload.
        Only upload one sample at a time, i.e. from the last system message to the end."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        question_id = 0
        messages = self.messages_without_roles(Role.SYSTEM)
        for message in messages:
            if message.role == Role.INFO:
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
            for message in messages
        ]
        return data
