import os
import io
import base64
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Streamlit App Configuration (only called once)
st.set_page_config(page_title="ATS Resume Expert")



# Streamlit App Layout for Q&A Demo
st.header("Gemini LLM Application")

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to load Gemini Pro model and get responses
def get_gemini_response(question):
    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = model.start_chat(history=[])
    response = chat.send_message(question, stream=True)
    return response

input_query = st.text_input("Input: ", key="question_input")
submit_query = st.button("Ask the question")

if submit_query and input_query:
    response = get_gemini_response(input_query)
    st.session_state['chat_history'].append(("You", input_query))
    
    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)
        st.session_state['chat_history'].append(("Bot", chunk.text))

st.subheader("The Chat History is")
for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")
