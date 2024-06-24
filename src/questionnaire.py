import json
from pathlib import Path

QUESTIONNAIRES = ["PHQ9"]


class Questionnaire:
    """A class to represent a questionnaire and store its chat history."""
    def __init__(self, name, questions, allowed_answers):
        self.name = name
        self.questions = questions
        self.current_question_idx = 0
        self.allowed_answers = allowed_answers
        self.chat_histories = {idx: [] for idx in range(len(questions))}

    def get_question(self, idx):
        return self.questions[idx]

    def increment_question_idx(self):
        self.current_question_idx += 1

    def get_current_question(self):
        return self.get_question(self.current_question_idx)

    def get_allowed_answers(self):
        return self.allowed_answers

    def get_allowed_answers_str(self):
        return f" Erlaube Antworten: {' '.join(self.allowed_answers)}"

    def get_system_prompt(self, idx):
        return self.questions[idx] + self.get_allowed_answers_str()

    def get_num_questions(self):
        return len(self.questions)

    def add_chat_message(self, idx, message):
        if idx in self.chat_histories:
            self.chat_histories[idx].append(message)
        else:
            raise IndexError("Question index out of range.")

    def get_chat_history(self, idx):
        if idx in self.chat_histories:
            return self.chat_histories[idx]
        else:
            raise IndexError("Question index out of range.")

    def clear_chat_history(self, idx=None):
        if idx is None:
            for key in self.chat_histories:
                self.chat_histories[key] = []
        elif idx in self.chat_histories:
            self.chat_histories[idx] = []
        else:
            raise IndexError("Question index out of range.")


def load_questionnaire(name):
    dir_path = Path(__file__).parent.parent
    data_path = dir_path / "data/questionnaires.json"
    if name not in QUESTIONNAIRES:
        raise ValueError(
            f"Questionnaire '{name}' not found. Allowed questionnaires: {QUESTIONNAIRES}"
        )
    with open(data_path, "r") as file:
        data = json.load(file)
    return Questionnaire(name, data[name]["questions"], data[name]["allowed_answers"])

