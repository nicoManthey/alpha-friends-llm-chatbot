from typing import List
import dotenv
import os
import sys
import json

import huggingface_hub as hfh
from huggingface_hub._inference_endpoints import InferenceEndpointStatus as IES
from huggingface_hub.utils._errors import BadRequestError

from src.chat_utils import ChatMessage


dotenv.load_dotenv(dotenv.find_dotenv())
env_vars = dotenv.dotenv_values()

HF_TOKEN_WRITE = env_vars["HF_TOKEN_WRITE"]
LLM_REPO_NAME = env_vars["LLM_REPO_NAME"]


# hfh.login(token=HF_TOKEN_WRITE, write_permission=True)


# CURRENTLY NOT USED (atm we use groq)
class EndpointHelper:
    """A class to represent a HuggingFace endpoint helper.
    Implements:
    - status
    - wakeup_endpoint
    - get_llm_answer
    - _make_llm_input

    possible statuses of endpoint.status:
    PENDING = "pending"
    INITIALIZING = "initializing"
    UPDATING = "updating"
    UPDATE_FAILED = "updateFailed"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    SCALED_TO_ZERO = "scaledToZero"
    """

    def __init__(self, token: str = HF_TOKEN_WRITE):
        self.token = token
        self.endpoint = hfh.get_inference_endpoint(LLM_REPO_NAME)
        print(f"endpoint: {self.endpoint}")

    def status(self):
        return self.endpoint.status

    def wakeup_endpoint(self):
        if self.endpoint.status in [IES.PAUSED, IES.SCALED_TO_ZERO]:
            try:
                self.endpoint.resume()
            except BadRequestError as e:
                print(
                    f"Current endpoint status: {self.endpoint.status}. Got error: {e}"
                )

    def get_llm_answer(self, messages: List[ChatMessage]) -> str:
        llm_input = self._make_llm_input(messages)
        output = self.endpoint.client.text_generation(llm_input)
        output = output.replace("<|end|>", "")
        print(f"LLM output: >>{output}<<")
        return output

    def _make_llm_input(self, messages: List[ChatMessage]) -> str:
        """Create the input string for the LLM API. Only include messages
        with roles 'user', 'system', 'assistant'. Only consider messages
        after the last 'system' message."""
        # Step 1: Find the index of the last 'system' message
        last_system_index = None
        for i in range(len(messages) - 1, -1, -1):
            if messages[i].role == "system":
                last_system_index = i
                break

        if last_system_index is not None:
            # Step 2: Slice the list from the last 'system' message onwards
            messages = messages[last_system_index:]

        # Step 3: Keep only messages with roles 'user', 'system', 'assistant'
        messages = [
            message
            for message in messages
            if message.role in ["user", "system", "assistant"]
        ]
        if not messages:
            raise ValueError("The messages list is empty.")
        # if not all(message in ["user", "system", "assistant"] for message in messages):
        #     input_roles = [message.role for message in messages]
        #     raise ValueError(f"Invalid role in messages list. Input roles: {input_roles}.")
        if not len(messages) >= 2:
            raise ValueError("The messages list must contain at least 2 messages.")
        if messages[0].role != "system":
            raise ValueError("The first message must be of role 'system'.")
        if messages[1].role != "user":
            raise ValueError("The second message must be of role 'user'.")

        llm_input = "<s>"
        last_role = None
        for message in messages:
            if last_role == "system" and message.role != "user":
                raise ValueError(
                    "A 'system' message must be followed by a 'user' message."
                )
            if last_role == "assistant" and message.role != "user":
                raise ValueError(
                    "An 'assistant' message must be followed by a 'user' message."
                )

            llm_input += f"<|{message.role}|>\n{message.content}<|end|>\n"
            last_role = message.role

        llm_input += "<|assistant|>"
        return llm_input
