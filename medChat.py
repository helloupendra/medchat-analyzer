from dotenv import load_dotenv
import os
import streamlit as st
from openai import OpenAI

load_dotenv()  # Loads variables from .env into environment

api_key=os.getenv("OPENAI_API_KEY")
# Set your OpenAI API key here or use environment variable
#openai.api_key = os.getenv(api_key) or api_key
client = OpenAI( api_key = api_key)

@st.cache_data(show_spinner=False)
def generate_report(conversation, report_type):
    if report_type == "patient":
        prompt = f"""
        You are a medical assistant. Given the Hindi conversation between a doctor and a patient:
        {conversation}

        Generate a report for the patient in Hindi including:
        - Doctor’s name
        - List of prescribed medicines with dosages and usage instructions
        - Any additional advice or instructions given by the doctor
        """
    elif report_type == "doctor":
        prompt = f"""
        You are a medical record assistant. Given the Hindi conversation between a doctor and a patient:
        {conversation}

        Generate a report for the doctor including:
        - Patient's symptoms and complaints
        - List of prescribed medicines with rationale
        - Duration of treatment
        - Next check-up or follow-up schedule
        """
    elif report_type == "firm":
        prompt = f"""
        You are a medical quality control agent. Analyze the Hindi conversation between a doctor and a patient:
        {conversation}

        Generate a firm-level report including:
        - Behavior of doctor and patient
        - Whether diagnosis and prescription align with symptoms
        - Was empathy and clarity maintained?
        - Mention if a next check-up or reminder is needed
        """
    elif report_type == "sentiment":
        prompt = f"""
        You are a language and sentiment expert. Analyze the emotional tone and sentiment of the following Hindi medical conversation:
        {conversation}

        Generate a sentiment report in English including:
        - Overall sentiment (Positive, Neutral, Negative)
        - Emotional tone (e.g., calm, anxious, empathetic, rude)
        - Any signs of distress or urgency
        - Politeness and clarity in communication
        """
    elif report_type == "intent":
        prompt = f"""
        You are a medical conversation analyst. Analyze the following Hindi conversation between a doctor and a patient:
        {conversation}

        Extract and provide:
        1. Important keywords (e.g., symptoms, conditions, medicines, actions)
        2. Patient's intent (e.g., consultation, prescription request, symptom explanation, follow-up)
        3. Doctor’s intent (e.g., diagnosis, reassurance, test recommendation)
        4. Brief summary of the core topic or goal of the interaction
        """
    else:
        return "Invalid report type"

    try:
        #client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or api_key)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# Streamlit UI
st.set_page_config(page_title="Hindi Medical Report Generator", layout="wide")
st.title("🩺 Hindi Medical Talk Analyzer")

conversation = st.text_area("Paste the Hindi conversation between doctor and patient:", height=300)
if st.button("Clear Cache"):
    st.cache_data.clear()
    st.success("Cache cleared. You can regenerate fresh reports now.")

if st.button("Generate Reports"):
    if conversation.strip():
        with st.spinner("Generating Patient Report..."):
            patient_report = generate_report(conversation, "patient")
        with st.spinner("Generating Doctor Report..."):
            doctor_report = generate_report(conversation, "doctor")
        with st.spinner("Generating Firm Report..."):
            firm_report = generate_report(conversation, "firm")
        with st.spinner("Generating Sentiment & Tone Report..."):
            sentiment_report = generate_report(conversation, "sentiment")
        with st.spinner("Generating Keyword & Intent Report..."):
            intent_report = generate_report(conversation, "intent")

        st.success("Reports Generated!")

        st.subheader(" Patient Report")
        st.text_area("Patient Report", patient_report, height=100)

        st.subheader(" Doctor Report")
        st.text_area("Doctor Report", doctor_report, height=100)

        st.subheader(" Firm Report")
        st.text_area("Firm Report", firm_report, height=100)

        st.subheader(" Sentiment & Tone Analysis")
        st.text_area("Sentiment Analysis", sentiment_report, height=100)
        
        st.subheader(" Keyword & Intent Detection")
        st.text_area("Intent & Keywords", intent_report, height=100)

        st.download_button("Download Patient Report", patient_report)



    else:
        st.warning("Please paste a conversation before generating reports.")

st.markdown("---")
st.caption("Built using OpenAI API and Streamlit | ©2025")