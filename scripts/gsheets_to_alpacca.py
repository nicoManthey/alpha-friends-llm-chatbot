# Description: Convert the Google Sheets data to the Alpacca format.
# Store the data in a JSON file inside the data/phq9 directory.
# Currently the data support SFT format.
# ATTENTION: Currently this is hard-coded for PHQ-9 dialogue.


from pathlib import Path
import json

import pandas as pd

from src.google_sheet_helper import GSheetHelper as SH
from src.chat_utils import Role


def question_df_to_alpacca(question_df: pd.DataFrame) -> dict:
    """Convert a DataFrame with the same question ID to the Alpacca format."""
    num_user_messages = question_df["role"].eq(Role.USER).sum()
    num_assistant_messages = question_df["role"].eq(Role.ASSISTANT).sum()
    assert (
        num_user_messages == num_assistant_messages
    ), "Number of user and assistant messages must be equal."

    history = []
    if num_user_messages > 1 or num_assistant_messages > 1:
        user_messages = question_df.loc[
            question_df["role"] == Role.USER, "content"
        ].tolist()
        assistant_messages = question_df.loc[
            question_df["role"] == Role.ASSISTANT, "content"
        ].tolist()
        for user, assistant in zip(user_messages, assistant_messages):
            history.append([user, assistant])

    input_content = ""
    system_content = question_df.loc[
        question_df["role"] == Role.INFO, "content"
    ].values[0]
    instruction_content = question_df.loc[
        question_df["role"] == Role.USER, "content"
    ].values[-1]
    output_content = question_df.loc[
        question_df["role"] == Role.ASSISTANT, "content"
    ].values[-1]

    json_output = {
        "input": input_content,
        "system": system_content,
        "instruction": instruction_content,
        "output": output_content,
        "history": history,
    }

    return json_output


if __name__ == "__main__":
    output_dir = Path(__file__).parent.parent / "data/phq9"
    output_fname = output_dir / "data_gsheets.json"

    sheet_helper = SH()
    sheet_helper.authorize()
    sheet_helper.select_worksheet("streamlit-app")

    df = sheet_helper.get_data()

    # Split the DataFrame into a list of DataFrames where each contains only rows with the same questionnaire and question ID
    dfs_by_timestamp = [group for _, group in df.groupby("run ID (upload timestamp)")]

    # Split each DataFrame into a list of DataFrames where each contains only rows with the same question ID
    dfs_by_timestamp_and_question = []
    for df in dfs_by_timestamp:
        dfs_by_question = [group for _, group in df.groupby("question ID")]
        dfs_by_timestamp_and_question.append(dfs_by_question)

    alpacca_data = []
    for dfs_by_question in dfs_by_timestamp_and_question:
        for df in dfs_by_question:
            alpacca_data.append(question_df_to_alpacca(df))

    with open(output_fname, "w", encoding="utf-8") as f:
        json.dump(alpacca_data, f, indent=4)
