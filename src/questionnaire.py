from typing import Optional
from pathlib import Path
import re
import json

from src.chat_utils import Role, ChatMessage


def _load_questionnaires_json() -> dict:
    dir_path = Path(__file__).parent.parent
    data_path = dir_path / "data/questionnaires.json"
    with open(data_path, "r") as file:
        return json.load(file)


class Questionnaire:
    """A class to represent a questionnaire and store its chat history."""

    def __init__(self, name, json_data: dict):
        self.name = name
        self.questions = list(json_data["questions"])
        self.current_question_idx = 0
        self.questionnaire_short_description = str(
            json_data["questionnaire_short_description"]
        )
        self.allowed_answers = list(json_data["allowed_answers"])
        self.example_reply_accepted_answer = json_data["example_reply_accepted_answer"]
        self.prompt_template = str(json_data["prompt_template"])

    @staticmethod
    def get_implemented_questionnaires():
        questionnaire_json = _load_questionnaires_json()
        return list(questionnaire_json.keys())

    @staticmethod
    def load_questionnaire(name):
        questionnaire_json = _load_questionnaires_json()
        implemented_questionnaires = list(questionnaire_json.keys())
        if name not in implemented_questionnaires:
            raise ValueError(
                f"Questionnaire '{name}' not found. Allowed questionnaires: {implemented_questionnaires}"
            )
        return Questionnaire(name, questionnaire_json[name])

    def get_question(self, idx):
        return self.questions[idx]

    def increment_question_idx(self):
        self.current_question_idx += 1

    def is_finished(self):
        return self.current_question_idx >= len(self.questions) - 1

    def get_current_question(self):
        return self.get_question(self.current_question_idx)

    def get_current_question_id(self):
        return self.current_question_idx + 1

    def get_allowed_answers(self):
        return self.allowed_answers

    def _get_allowed_answers_str(self):
        return ", ".join(self.allowed_answers) + "."

    def get_num_questions(self):
        return len(self.questions)

    def _get_filled_prompt(self):
        replacements = {
            "questionnaire_name": self.name,
            "questionnaire_short_description": self.questionnaire_short_description.format(
                **{"questionnaire_name": self.name}
            ),
            "allowed_answers": self._get_allowed_answers_str(),
            "question_id_and_question": f"{self.get_current_question_id()}) {self.get_current_question()}",
            # "example_reply_accepted_answer": self.example_reply_accepted_answer,
        }
        formatted_prompt = self.prompt_template.format(**replacements)
        return formatted_prompt

    def get_prompt_and_question_message(self) -> list[ChatMessage]:
        "Get the system prompt and info message when starting a new questionnaire."
        first_messages = [
            ChatMessage(role=Role.SYSTEM, content=self._get_filled_prompt()),
            ChatMessage(role=Role.INFO, content=self.get_current_question()),
        ]
        return first_messages

    def extract_question_answer(self, bot_uttr: str) -> Optional[str]:
        """
        Searches for any of the allowed answers in the bot's utterance, but only if they are inside quotation marks.
        Goal of this method is to extract the LLM classification.

        :param bot_uttr: The utterance from the bot.
        :return: The first matching allowed answer found in the user's utterance, or None if no match is found.
        """
        if "?" in bot_uttr:
            return None

        bot_uttr_lower = bot_uttr.lower()
        for allowed_answer in self.allowed_answers:
            print(f"Trying to match: {allowed_answer} to bot_uttr: {bot_uttr_lower}")
            # Prepare patterns for both single and double-quoted allowed answers
            patterns = [
                f"'{re.escape(allowed_answer.lower())}'",  # Single quotes
                f'"{re.escape(allowed_answer.lower())}"',  # Double quotes
            ]
            # Check if any of the patterns match
            for pattern in patterns:
                if re.search(pattern, bot_uttr_lower):
                    return allowed_answer
        return None
