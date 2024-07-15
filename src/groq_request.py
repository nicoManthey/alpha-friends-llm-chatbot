from typing import List
import dotenv
import os
import sys
import json

from groq import Groq

from src.load_env_vars import GROQ_API_KEY, GROQ_MODEL_NAME
from src.chat_utils import Role, ChatMessage


def get_groq_answer(messages: List[ChatMessage]):
    """Create the input string for the LLM API. Only include messages
    with roles 'user', 'system', 'assistant'. Only consider messages
    after the last 'system' message."""

    def preprocess_and_validate(messages):
        # Step 1: Find the index of the last 'system' message
        last_system_index = None
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].role == Role.SYSTEM:
                last_system_index = i
                break

        if last_system_index is not None:
            # Step 2: Slice the list from the last 'system' message onwards
            messages = messages[last_system_index:]

        # Step 3: Keep only messages with roles 'user', 'system', 'assistant'
        messages = [
            message
            for message in messages
            if message.role in [Role.USER, Role.SYSTEM, Role.ASSISTANT]
        ]
        if not messages:
            raise ValueError("The messages list is empty.")
        if not len(messages) >= 2:
            raise ValueError("The messages list must contain at least 2 messages.")
        if messages[0].role != Role.SYSTEM:
            raise ValueError("The first message must be of role 'system'.")
        if messages[1].role != Role.USER:
            raise ValueError("The second message must be of role 'user'.")
        return messages

    messages = preprocess_and_validate(messages)

    client = Groq(api_key=GROQ_API_KEY)
    print(f"--------- sending groq request with messages: -----------")
    for message in messages:
        print("#################")
        print(f"{message.role}: {message.content}")
    completion = client.chat.completions.create(
        model=GROQ_MODEL_NAME,
        messages=[
            {"role": message.role, "content": message.content} for message in messages
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    reply = ""
    for chunk in completion:
        reply += chunk.choices[0].delta.content or ""
    return reply
