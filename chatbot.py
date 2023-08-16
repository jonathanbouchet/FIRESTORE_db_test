import streamlit as st
import random
import time
import logging
from utils import *
from app_v3 import login_panel


# Create and configure logger
logging.basicConfig(
    filename="app.log",
    format='%(asctime)s %(message)s',
    filemode='w',)

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)


def new_chatbot() -> None:
    """

    :return:
    """
    # check a logout has not been issued already
    if not st.session_state["logout"] or st.session_state["authentication_status"] is True:

        # add the login panel manager
        if st.sidebar.button("Logout"):
            st.empty() # clear page
            print("will logout")
            st.session_state["logout"] = True
            st.session_state["name"] = None
            st.session_state["username"] = None
            st.session_state["authentication_status"] = None
            # st.session_state["authentication_status"] = False
            st.session_state['messages'] = []
            print(st.session_state)
            return st.session_state["logout"]

        st.title("Reflexive AI")
        st.header("Virtual Insurance Agent")

        # Set API key
        openai_api_key = st.sidebar.text_input(
            ":blue[API-KEY]",
            placeholder="Paste your OpenAI API key here",
            type="password")

        MODEL = st.sidebar.selectbox(
            label=":blue[MODEL]",
            options=["gpt-3.5-turbo-16k-0613",
                     "gpt-3.5-turbo",
                     "gpt-3.5-turbo-16k",
                     "gpt-3.5-turbo-0613",
                     "text-davinci-003",
                     "text-davinci-002"])

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("type your message here"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                assistant_response = random.choice(
                    [
                        "Hello there! How can I assist you today?",
                        "Hi, human! Is there anything I can help you with?",
                        "Do you need help?",
                        "this ends the chat"
                    ]
                )
                # Simulate stream of response with milliseconds delay
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + " ")
                message_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            # check for user response right at the beginning by looking at any message non-empty
            print(f"st.session_state:{st.session_state}")
            if st.session_state:
                print(f"st.session_state checked")
                print(f"current session:{st.session_state['messages']}")
                # temporary because added a white space for the random messages
                if st.session_state['messages'][-1]['role'] == "assistant" and st.session_state['messages'][-1]['content'].strip() == "this ends the chat":
                    now = datetime.now()
                    print(f"current time :{now}")
                    # Print the output
                    # with open('./app.log') as current_log:
                    #     data = current_log.read()

            print(f"end of session\t{st.session_state.messages}")
            st.write(st.session_state)
            print(st.session_state)
        return st.session_state["logout"]


# Run the main page
if __name__ == "__main__":
    print(f"in chatbot.py, starting to run main")
    new_chatbot()

