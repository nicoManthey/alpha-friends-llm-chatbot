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


role = Role("user")

if not isinstance(role, Role):
    raise ValueError(f"Role '{role}' not allowed. Choose from: {Role.allowed_roles()}")

print("finished")
