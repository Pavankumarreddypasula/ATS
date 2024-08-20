import os
import io
import base64
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
import requests
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Streamlit App Configuration (only called once)
st.set_page_config(page_title="ATS Resume Expert")

# Function to convert PDF to image using Cloudmersive API
def convert_pdf_to_image_online(uploaded_file):
    url = "https://api.cloudmersive.com/pdf/convert/to/png"
    headers = {"Apikey": os.getenv("CLOUDMERSIVE_API_KEY")}
    files = {"file": uploaded_file}

    response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        img_data = io.BytesIO(response.content)
        image = Image.open(img_data)
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # Encode to base64
            }
        ]
        return pdf_parts
    else:
        raise Exception("Failed to convert PDF to image using Cloudmersive API")

# Function to get the response from Gemini API
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Streamlit App Layout for ATS Tracking System
st.header("ATS Tracking System")
input_text = st.text_area("Job Description: ", key="job_description_input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Provide the percentage match if the resume matches
the job description. First, the output should come as a percentage, then list the missing keywords, and finally, provide final thoughts.
"""

# Buttons
submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

if submit1 and uploaded_file:
    pdf_content = convert_pdf_to_image_online(uploaded_file)
    response = get_gemini_response(input_text, pdf_content, input_prompt1)
    st.subheader("The Response is")
    st.write(response)
elif submit3 and uploaded_file:
    pdf_content = convert_pdf_to_image_online(uploaded_file)
    response = get_gemini_response(input_text, pdf_content, input_prompt3)
    st.subheader("The Response is")
    st.write(response)
elif (submit1 or submit3) and not uploaded_file:
    st.write("Please upload the resume")

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
