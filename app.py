from typing import Optional
import re

import streamlit as st
import streamlit.components.v1 as components
from huggingface_hub._inference_endpoints import InferenceEndpointStatus as IES

from src.functions import get_prompt_and_question_message, find_match_in_allowed_answers
from src.streamlit_utils import message_to_markdown
from src.chat_utils import ChatMessage, ChatBox
from src.questionnaire import load_questionnaire, QUESTIONNAIRES, Questionnaire
from src.endpoint_helper import EndpointHelper as EH
from src.google_sheet_helper import GSheetHelper as SH



instructions = f"""
## alpha friends questionnaire chatbot

### Instructions:

1. Choose the questionnaire you want to start by typing the name of the questionnaire.
   This step is optional. The default questionnaire is PHQ9.
   You can choose an other questionnaire at any time by typing the name of the questionnaire.
   Available questionnaires: {", ".join(QUESTIONNAIRES)}.
2. Answer the questions. The chatbot will guide you through the process.

The system prompt will reset once a question was ansered correctly, i.e. context about the last question will be lost.

Blue messages are info messages. They are scripted, i.e. no LLM output.

Grey messages are bot messages by the LLM.

Green messages are user messages.

### Limitations:

- Training data is very limited as of now.
- LLM will be bad for anything that's not represented in the training data yet.
- The LLM is not able to detect out-of-scope questions.
  (e.g. when asking "What is the capital of France?", it should do a fallback. To be implemented.).
- Training data only has a history of length 1 and 2. LLM output quality will deteriorate after that.

### TODO:
- app should have out-of-scope detection with sentence transformer.
- app should allow user to replace bad LLM responses.
- finalize Google Sheets upload function.
- add "Tell me the answer options again" to training dataset.
"""


def main():
    st.set_page_config(
        page_title="Chatbot Application",
        page_icon=":robot_face:",
        layout="wide"
    )
    if "endpoint_helper" not in st.session_state:
        st.session_state.endpoint_helper = EH()
    endpoint_helper = st.session_state.endpoint_helper
    # status = "ok"
    status = endpoint_helper.status()
    if status in [IES.PAUSED, IES.SCALED_TO_ZERO, IES.INITIALIZING]:
        st.write(("LLM endpoint is sleeping. Waking it up... This might take 1 - 2 minutes. "
                  "Please refresh the browser every now and then."))
        endpoint_helper.wakeup_endpoint()
    else:
        if "sheet_helper" not in st.session_state:
            st.session_state.sheet_helper = SH()
        sheet_helper = st.session_state.sheet_helper
        chat(endpoint_helper, sheet_helper)

def chat(endpoint_helper: EH, sheet_helper: SH):
    col1, col2 = st.columns(2)

    with col1:
        st.write(instructions)

    with col2:
        if "questionnaire" not in st.session_state:
            st.session_state.questionnaire = load_questionnaire("PHQ9")
        questionnaire = st.session_state.questionnaire

        if "chatbox" not in st.session_state:
            messages = get_prompt_and_question_message(questionnaire)
            st.session_state.chatbox = ChatBox(messages)
        chatbox = st.session_state.chatbox

        # Initialize counter for javascript injection
        if 'counter' not in st.session_state:
            st.session_state.counter = 0

        # Display the messages using the message_to_markdown function
        for message in chatbox.get_display_messages():
            message_to_markdown(message.role, message.content)

        # Create a form to handle input and button
        with st.form(key="chat_form"):
            chat_input = st.text_input("Enter your message:", key="chat_input")

            # Inject JavaScript to autofocus the chat input field
            components.html(
                f"""
                <div>some hidden container</div>
                <p>{st.session_state.counter}</p>
                <script>
                    var input = window.parent.document.querySelectorAll("input[type=text]");
                    for (var i = 0; i < input.length; ++i) {{
                        input[i].focus();
                    }}
                </script>
                """,
                height=0,
            )

            # Send the message when the "Enter" key is pressed
            if st.form_submit_button("Send"):
                if chat_input:
                    chatbox.add_messages([ChatMessage(role="user", content=chat_input)])

                    # Handle new questionnaire by user input
                    if chat_input in QUESTIONNAIRES:
                        questionnaire = load_questionnaire(chat_input)
                        bot_uttr = "Questionnaire was set to: " + questionnaire.name
                        info_message = ChatMessage(role="info", content=bot_uttr)
                        first_messages = [info_message] + get_prompt_and_question_message(
                            questionnaire
                        )
                        chatbox = ChatBox(first_messages)

                    # Handle LLM
                    else:
                        bot_uttr = endpoint_helper.get_llm_answer(chatbox.messages)
                        print(f"bot_uttr: {bot_uttr}")
                        # bot_uttr = "placeholder"
                        chatbox.add_messages([ChatMessage(role="assistant", content=bot_uttr)])

                        # Handle question was answered successfully
                        match = find_match_in_allowed_answers(bot_uttr, questionnaire.allowed_answers)
                        if match:
                            # Load a new question, load new system prompt, add to chatbox
                            questionnaire.increment_question_idx()
                            first_messages = get_prompt_and_question_message(questionnaire)
                            chatbox.add_messages(first_messages)

                    # Update the session state
                    st.session_state.questionnaire = questionnaire
                    st.session_state.chatbox = chatbox

                    # Empty the input field
                    st.session_state.enter_pressed = False
                    st.rerun()

        if False:
            # TODO: Upload sample until last question to Google Sheets
            # (or until 2nd last question if no new utterances were made after the last question)
            # Button to upload chatbox to Google Sheets
            if st.button("Upload Chatbox to Google Sheets"):
                data_to_upload = chatbox.to_google_sheet_format()
                sheet_helper.authorize()
                sheet_helper.select_worksheet('streamlit-app')
                sheet_helper.upload_data(data_to_upload)
                st.success("Chatbox uploaded to Google Sheets.")

if __name__ == "__main__":
    main()
