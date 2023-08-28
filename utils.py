import streamlit as st
from datetime import datetime
import tiktoken
from firebase_admin import firestore
from firebase_admin import auth
import pandas as pd


def get_time():
    """return time"""
    now = datetime.now()
    return now.strftime("%H:%M:%S")


def get_open_ai_key():
    """get openai key
    :return:
    """
    return st.secrets["OPENAI_API_KEY"]


def get_tokens(text: str, model_name: str) -> int:
    """
    calculate the number of tokens corresponding to text and tokenizer for that model
    :param model_name:
    :param text:
    :return:
    """
    tokenizer = tiktoken.encoding_for_model(model_name)
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


def template_insurance():
    """
    :return: prompt template
    """
    # template = """let's play a game where you ask me a series of questions, the order of which is influenced by my responses. every time I say "new game" we restart the process.
    #
    #     the first question is "what is your name?"
    #
    #     After that, ask for my height and weight then calculate my BMI.
    #     If it is greater than 35, then ask for my average weight for the last 3 years.
    #     if it is less than 35, move forward to the next question.
    #
    #     The next question is "Are you currently taking any medications?"
    #
    #     If I say yes, ask for the medications and dosages.
    #     If I give you more than 2 medications, also ask me to list the reasons i'm taking those medicines.
    #     If I say I take no medicines, move on to the next question.
    #
    #     The next question is whether I currently have any diseases.
    #     If I say no, the game is over.
    #     Write a summary of my answers as a bullet point list.
    #
    #     if I say yes, ask me if I have any metabolic and/or cardiovascular diseases.
    #     if I say yes to metabolic, ask me if I have diabetes or obesity.
    #     if I say yes to cardiovascular diseases, ask me what my cholesterol and blood pressure are.
    #
    #     This ends the game. Write a summary of my answers as bullet point list.
    # """

    template = """let's play a game where you ask me a series of questions, the order of which is influenced by my answers.
            Every time I say "new game" we restart the process.
            Every time I say "end game" this ends the game and you go to the 'End of game' section.
            ###
            The first question is "what is your name?"
            ###
            After that, ask for my height and weight and calculate my Body Mass Index (BMI).
            Instructions:
                - always double check the units for weight and height before calculation
                - always double check for human possible weight and height values
                - do not provide the intermediate calculations
                - action: present the final result 
            Action:
                - If BMI is greater than 35, then ask for my average weight for the last 3 years. 
                - if BMI is less than 35, move forward to the next question.
            ###
            The next question is "Are you currently taking any medications?"
            ###
            If I say yes, ask for the medications and dosages. 
            If I give you more than 2 medications, also ask me to list the reasons i'm taking those medicines. 
            If I say no, move on to the next question.
            ###
            The next question is whether I currently have any diseases.
            ###
            If I say no, move on the next question.
            if I say yes, ask me if I have any metabolic or cardiovascular diseases. 
            if I say yes to metabolic, ask me if I have diabetes or obesity. 
            if I say yes to cardiovascular diseases, ask me what my cholesterol and blood pressure are.
            Then move on the next question.
            ###
            The next question is about my life style. Ask me if I have been out of country in last 3 years ?
            If I say yes, then ask about the locations and dates for each of them then move on the next question.
            If I say no, move on the next question.
            ###
            The next question is "Do you have any hobbies or sports or activities ?"
            If I say yes, ask for the frequency for each of them? This ends the game.
            If I say no, this ends the game, go to 'End of game' section
            ###
            End of game: summarize my answers using a bullet list format and ask to download the result.
        """
    return template


def count_user_collection(collection_name: str, user_uid: str) -> list:
    """
    :param collection_name:
    :param user_uid:
    :param db:
    :return: list of collection data
    """
    db = firestore.client()
    collection = db.collection(f"{collection_name}")
    docs = collection.stream()
    cnt = 0
    for doc in docs:
        col = doc.to_dict()
        # print(col)
        if col['username'] == user_uid:
            cnt += 1
    return cnt


def get_user_data(user_uid: str) -> pd.DataFrame:
    """
    return user's basic data
    :param user_uid:
    :param db:
    :return:
    """
    page = auth.list_users()
    res = []
    while page:
        for user in page.users:
            if user.email == user_uid:
                user_uid = user.uid
                user_name = user.display_name
                user_email = user.email
                user_email_verified = user.email_verified
                user_creation_timestamp = datetime.fromtimestamp(user.user_metadata.creation_timestamp / 1000)
                user_last_sign_in_timestamp = datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000)
                res.append({"user_uid": user_uid,
                            "user_name": user_name,
                            "user_email": user_email,
                            "user_email_verified": user_email_verified,
                            "user_creation_timestamp": user_creation_timestamp,
                            "user_last_sign_in_timestamp": user_last_sign_in_timestamp})
        page = page.get_next_page()
    print(res)
    num_interaction = count_user_collection("users_app", res[0]['user_email'])
    print(f"number of chats: {num_interaction}")
    col_values = list(res[0].values())
    index_names = list(res[0].keys())
    index_names = [index.replace("_", " ").replace("user", "") for index in index_names]
    col_values.append(num_interaction)
    index_names.append("number Of Use")
    user_df = pd.DataFrame(list(zip(index_names, col_values)))
    user_df.columns = ['Settings', 'Value']
    return user_df