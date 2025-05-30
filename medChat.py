import streamlit as st  # ✅ MUST BE FIRST
from dotenv import load_dotenv
import os
from openai import OpenAI

# === Load Environment Variables ===
load_dotenv()

# === Load API Key from .env or Streamlit Secrets ===
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Set it in your .env or Streamlit Secrets.")
    st.stop()

# === Initialize OpenAI Client ===
client = OpenAI(api_key=api_key)

# === Report Generator Function ===
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

    # Try GPT-4o first, fallback to GPT-3.5 silently
    for model_name in ["gpt-4o", "gpt-3.5-turbo"]:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except:
            continue

    return "⚠️ Could not generate report at this time. Please try again later."

# === Streamlit UI ===
st.set_page_config(page_title="Hindi Medical Report Generator", layout="wide")
st.title("🩺 Hindi Medical Talk Analyzer")

# === Example Conversations ===
example_conversations = {
    "Example 1: Fever and Sore Throat": """
डॉक्टर: नमस्ते, बताइए आपको क्या परेशानी है?
मरीज: डॉक्टर साहब, पिछले तीन दिनों से बुखार है और गले में दर्द हो रहा है।
डॉक्टर: क्या खांसी या जुकाम भी है?
मरीज: हाँ, थोड़ी बहुत खांसी है और शरीर में भी दर्द है।
डॉक्टर: कोई एलर्जी या पुरानी बीमारी है?
मरीज: नहीं, ऐसा कुछ नहीं है।
डॉक्टर: ठीक है, मैं आपको पैरासिटामोल 500mg दिन में तीन बार खाने की सलाह देता हूँ।
""",
    "Example 2: Headache and Eye Strain": """
डॉक्टर: नमस्ते, आपको कब से सिरदर्द हो रहा है?
मरीज: दो दिन से लगातार सिरदर्द हो रहा है, खासकर स्क्रीन देखने पर।
डॉक्टर: क्या चश्मा पहनते हैं?
मरीज: हाँ, लेकिन नंबर कुछ समय से चेक नहीं करवाया।
डॉक्टर: ठीक है, सबसे पहले एक आंखों की जांच करवाएं और इस बीच दर्द के लिए सिट्रापार 500mg लें।
""",
    "Example 3: Diabetes Follow-Up": """
डॉक्टर: आपकी पिछली रिपोर्ट में शुगर का लेवल बढ़ा हुआ था। कैसा महसूस कर रहे हैं?
मरीज: थोड़ी थकान रहती है और कभी-कभी चक्कर भी आते हैं।
डॉक्टर: आपने दवाइयाँ नियमित ली हैं?
मरीज: हाँ, लेकिन डाइट में थोड़ी लापरवाही हो गई थी।
डॉक्टर: आपको ग्लूकोफेज 500mg सुबह-शाम फिर से शुरू करनी चाहिए और डाइट चार्ट फॉलो करें।
"""
}

# === Example selector and input area ===
example_choice = st.selectbox("📋 Choose a sample conversation or write your own:", ["-- Select an example --"] + list(example_conversations.keys()))
user_input = st.empty()

if example_choice != "-- Select an example --":
    selected_convo = example_conversations[example_choice].strip()
    conversation = user_input.text_area("Conversation", selected_convo, height=300)
else:
    conversation = user_input.text_area("Paste the Hindi conversation between doctor and patient:", height=300)

if st.button("Clear Cache"):
    st.cache_data.clear()
    st.success("✅ Cache cleared. You can regenerate fresh reports now.")

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

        st.success("✅ Reports Generated!")

        st.subheader("🧾 Patient Report")
        st.text_area("Patient Report", patient_report, height=100)

        st.subheader("🩺 Doctor Report")
        st.text_area("Doctor Report", doctor_report, height=100)

        st.subheader("🏢 Firm Report")
        st.text_area("Firm Report", firm_report, height=100)

        st.subheader("💬 Sentiment & Tone Analysis")
        st.text_area("Sentiment Analysis", sentiment_report, height=100)

        st.subheader("🔍 Keyword & Intent Detection")
        st.text_area("Intent & Keywords", intent_report, height=100)

        st.download_button("📥 Download Patient Report", patient_report)

    else:
        st.warning("⚠️ Please paste or select a conversation before generating reports.")

st.markdown("---")
st.caption("Built using OpenAI API and Streamlit | ©2025")