import streamlit as st


def message_to_markdown(message_type, message_text):
    # Add custom CSS for the message bubbles
    st.markdown(
        """
    <style>
        .message-bubble {
            padding: 10px 40px;
            border-radius: 10px;
            display: inline-block;
            max-width: 70%;
        }
        .user-message {
            background-color: #4CAF50;
            color: white;
            clear: both;
            float: left;
        }
        .bot-message {
            background-color: #E0E0E0;
            color: #333;
            float: right;
            margin-left: 20px;
            clear: both;
        }
        .info-message {
            background-color: #ADD8E6;  /* Light blue */
            color: #333;
            margin-right: auto;
            margin-left: auto;
            margin-bottom: 20px;
            display: block; /* Changed from float to block for centering */
            clear: both;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    if message_type == "user":
        st.markdown(
            f'<div class="message-bubble user-message">{message_text}</div>',
            unsafe_allow_html=True,
        )
    elif message_type == "assistant":
        st.markdown(
            f'<div class="message-bubble bot-message">{message_text}</div>',
            unsafe_allow_html=True,
        )
    elif message_type == "info":
        st.markdown(
            f'<div class="message-bubble info-message">{message_text}</div>',
            unsafe_allow_html=True,
        )
