from typing import Optional
import re

from src.chat_utils import ChatMessage
from src.questionnaire import Questionnaire


def get_prompt_and_question_message(questionnaire: Questionnaire) -> list[ChatMessage]:
    "Get the system prompt and info message when starting a new questionnaire."
    question = questionnaire.get_current_question()
    allowed_answers = questionnaire.get_allowed_answers_str()
    system_prompt = question + allowed_answers
    first_messages = [
        ChatMessage(role="system", content=system_prompt),
        ChatMessage(role="info", content=question)
    ]
    return first_messages


def find_match_in_allowed_answers(bot_uttr: str, allowed_answers: list[str]) -> Optional[str]:
    """
    Searches for any of the allowed answers in the bot's utterance, ignoring case.

    :param bot_uttr: The utterance from the bot.
    :param allowed_answers: A list of allowed answers.
    :return: The first matching allowed answer found in the user's utterance, or None if no match is found.
    """
    bot_uttr_lower = bot_uttr.lower()
    for allowed_answer in allowed_answers:
        if re.search(re.escape(allowed_answer.lower()), bot_uttr_lower, re.IGNORECASE):
            return allowed_answer
    return None
