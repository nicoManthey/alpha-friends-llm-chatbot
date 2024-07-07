import streamlit as st
import streamlit.components.v1 as components

from src.streamlit_utils import message_to_markdown
from src.chat_utils import Role, ChatMessage, ChatBox
from src.questionnaire import QUESTIONNAIRES, Questionnaire
from src.google_sheet_helper import GSheetHelper as SH
from src.groq_request import get_groq_answer


instructions = f"""
## alpha friends questionnaire chatbot

### Anleitung:

1. Die Demo führt dich durch den PHQ-9 Fragebogen. Weitere Fragebögen kommen in der Zukunft.
2. Rechts sind zwei Textfelder. Im oberen kannst du mit dem Chatbot interagieren. Im unteren kannst du einen Kommentar
   zu der jeweils letzten Antwort des Chatbots hinterlassen.
3. Nachdem du einen Fragebogen abgeschlossen hast, erscheint rechts unten ein Button mit dem du den Chatverlauf
   auf Google Sheets hochladen kannst.
   Wenn du den klickst, können wir die Gesprächsdaten analysieren.
   Wir speichern dabei den Benutzer-Input, den Bot-Output und die Kommentare.
   [Hier kannst du dir bisher gespeicherte Daten ansehen](https://docs.google.com/spreadsheets/d/1mx071HioSsIRDVRqv8CWm3VNxQS_cVKqZXSIxprourA/edit?gid=907089658#gid=907089658).


Blaue Meldungen sind Info-Meldungen. Sie sind geskriptet, d.h. keine LLM-Ausgabe.

Grüne Meldungen sind Benutzernachrichten.

Graue Meldungen sind Bot-Meldungen des LLM.

Mögliche PHQ-9-Antworten: Überhaupt nicht, An einzelnen Tagen, An mehr als der Hälfte der Tage, Beinahe jeden Tag.

### Erläuterungen:

- Momentan benutzt der ChatBot das Language Model Llama 3 70b, bereitgestellt von der Firma Groq.
  Dabei wird Prompt Engineering eingesetzt, um die Qualität der Antworten zu verbessern.
  Auf lange Sicht wird das Modell durch ein speziell für diesen Zweck trainiertes Modell ersetzt.

## TODOs:

- GAD-7, Malmö-POTS Fragebögen hinzufügen
"""


def main():
    st.set_page_config(
        page_title="Chatbot Application", page_icon=":robot_face:", layout="wide"
    )
    # endpoint_helper and sheet_helper have some costly initialization
    # steps that don't need to be repeated
    if "sheet_helper" not in st.session_state:
        sheet_helper = SH()
        sheet_helper.authorize()
        sheet_helper.select_worksheet("streamlit-app")
        st.session_state.sheet_helper = sheet_helper
    sheet_helper = st.session_state.sheet_helper
    chat(sheet_helper)


def chat(sheet_helper: SH):
    col1, col2 = st.columns(2)

    with col1:
        st.write(instructions)

    with col2:
        if "questionnaire" not in st.session_state:
            # TODO: rm hard-coded questionnaire name
            st.session_state.questionnaire = Questionnaire.load_questionnaire("PHQ-9")
        questionnaire = st.session_state.questionnaire

        if "chatbox" not in st.session_state:
            messages = questionnaire.get_prompt_and_question_message()
            st.session_state.chatbox = ChatBox(messages)
        chatbox = st.session_state.chatbox

        # Initialize counter for javascript injection
        if "counter" not in st.session_state:
            st.session_state.counter = 0

        # Initialize the questionnaire finished flag if not already set
        if "questionnaire_finished" not in st.session_state:
            st.session_state.questionnaire_finished = False

        if "upload_button_clicked" not in st.session_state:
            st.session_state.upload_button_clicked = False

        # Display the messages using the message_to_markdown function
        for message in chatbox.messages_without_roles(Role.SYSTEM):
            message_to_markdown(message.role, message.content)

        if "user_gave_remark" not in st.session_state:
            st.session_state.user_gave_remark = False
        if st.session_state.user_gave_remark:
            st.toast("Dein Kommentar wurde aufgenommen. Danke!", icon="😍")
            st.session_state.user_gave_remark = False

        def set_session_state():
            st.session_state.questionnaire = questionnaire
            st.session_state.chatbox = chatbox

        # Create a form to handle input and button
        if not st.session_state.questionnaire_finished:
            with st.form(key="chat_form", clear_on_submit=True):
                chat_input = st.text_input("Gib deine Nachricht ein:", key="chat_input")

                # Send the message when the "Enter" key is pressed
                if st.form_submit_button("Abschicken"):
                    if chat_input:
                        # Handle user wants to switch the questionnaire
                        if chat_input in QUESTIONNAIRES:
                            questionnaire = Questionnaire.load_questionnaire(chat_input)
                            bot_uttr = (
                                "Fragebogen wurde umgestellt auf: " + questionnaire.name
                            )
                            info_message = ChatMessage(role=Role.INFO, content=bot_uttr)
                            messages = [
                                info_message
                            ] + questionnaire.get_prompt_and_question_message()
                            chatbox = ChatBox(messages)

                        # Handle LLM answer
                        else:
                            chatbox.add_messages(
                                ChatMessage(role=Role.USER, content=chat_input)
                            )
                            bot_uttr = get_groq_answer(chatbox.messages)
                            # bot_uttr = endpoint_helper.get_llm_answer(chatbox.messages)
                            chatbox.add_messages(
                                ChatMessage(role=Role.ASSISTANT, content=bot_uttr)
                            )

                            # Handle question was answered successfully
                            matched_answer = questionnaire.extract_question_answer(
                                bot_uttr
                            )
                            if matched_answer:
                                # Load next question and update chatbox
                                if questionnaire.is_finished():
                                    st.session_state.questionnaire_finished = True
                                else:
                                    questionnaire.increment_question_idx()
                                    messages = (
                                        questionnaire.get_prompt_and_question_message()
                                    )
                                    chatbox.add_messages(*messages)

                        # Update the session state
                        set_session_state()
                        st.rerun()

            # A form to handle user comments about the last bot message
            with st.form(key="comment_form", clear_on_submit=True):
                comment_input = st.text_input(
                    "Dein Kommentar über die lezte Bot-Ausgabe:", key="comment_input"
                )
                if st.form_submit_button("Abschicken"):
                    if comment_input:
                        chatbox.messages[-1].comment = comment_input
                        st.session_state.user_gave_remark = True
                        set_session_state()
                        st.rerun()

        else:
            st.write("Du hast den Fragebogen abgeschlossen. Danke fürs Mitmachen!")

            # Button to upload the chat history to Google Sheets
            if st.button(
                "Auf Google Sheets hochladen",
                disabled=st.session_state.upload_button_clicked,
            ):
                data_to_upload = chatbox.to_google_sheet_format(questionnaire.name)
                sheet_helper.upload_data(data_to_upload)
                st.session_state.upload_button_clicked = True
                st.success("Fragebogen erfolgreich hochgeladen!")
                st.rerun()

        # Inject JavaScript to autofocus the chat input field
        components.html(
            f"""
            <div>some hidden container</div>
            <p>{st.session_state.counter}</p>
            <script>
                var input = window.parent.document.querySelectorAll("input[type=text]");
                if (input.length >= 2) {{
                    input[input.length - 2].focus();
                }}
            </script>
            """,
            height=0,
        )


if __name__ == "__main__":
    main()
