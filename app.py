import streamlit as st
from pydub import AudioSegment
import os
import speech_recognition as sr
from call_analyzer import CallAnalyzer  # Import the CallAnalyzer class
from database.agent_database import get_all_agents, get_agent_schedule  # For displaying agent data
from database.client_database import add_client, get_calls_by_client, get_all_clients  # For client data
from utils.agent_matching import assign_agent_and_schedule  # For agent matching
import pandas as pd  # For structured data display
from datetime import datetime, timedelta

# Custom CSS for professional styling
st.markdown(
    """
    <style>
        body {
            background-color: #FFF0DC;
            color: #131010;
        }
        .main {
            padding: 20px;
            border-radius: 10px;
            background-color: #FFFFFF;
            border-left: 5px solid #F0BB78;
            border-right: 5px solid #F0BB78;
        }
        .stButton>button {
            background-color: #F0BB78 !important;
            color: #131010 !important;
            font-size: 16px;
            border-radius: 5px;
            border: none;
            padding: 8px 16px;
        }
        .stNumberInput>div>div>input, .stTextInput>div>div>input {
            border-radius: 5px;
            padding: 8px;
            background-color: #FFF0DC;
            color: #543A14;
            border: 1px solid #543A14;
        }
        .stDataFrame {
            background-color: #FFFFFF;
            color: #131010;
            border-radius: 10px;
            padding: 10px;
        }
        .stMarkdown h2, .stMarkdown h3 {
            color: #543A14;
        }
        .stMarkdown p {
            color: #131010;
        }
        .stExpander {
            background-color: #F0BB78;
            border-radius: 10px;
            padding: 10px;
            color: #131010;
        }
        .card {
            background-color: #FFF0DC;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .card h4 {
            margin: 0;
            color: #543A14;
        }
        .card p {
            margin: 5px 0;
            color: #131010;
        }
        .info-box {
            background-color: #F0BB78;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            color: #131010;
        }
        .info-box h4 {
            margin: 0;
            color: #543A14;
        }
        .info-box p {
            margin: 5px 0;
            color: #131010;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title of the application
st.title("GenCallAI")

# Helper function: Save uploaded audio file
def save_audio_file(uploaded_file, output_path="temp_audio.mp3"):
    with open(output_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return output_path

# Helper function: Transcribe audio to text
def transcribe_audio(audio_path):
    try:
        # Convert MP3 to WAV for transcription
        audio = AudioSegment.from_file(audio_path)
        wav_path = "temp_audio.wav"
        audio.export(wav_path, format="wav")

        # Initialize recognizer
        recognizer = sr.Recognizer()

        # Load WAV file
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)  # Read the entire audio file
            transcription = recognizer.recognize_google(audio_data)  # Perform transcription

        return transcription
    except sr.UnknownValueError:
        st.error("Google Speech Recognition could not understand the audio.")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition: {e}")
        return None
    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")
        return None

# Streamlit UI: Title
st.title("AI-Powered Call Routing and Analysis")

# Step 1: File Upload
uploaded_file = st.file_uploader("Upload a conversation audio file (.mp3)", type=["mp3"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")  # Play the uploaded file
    st.success("File uploaded successfully!")

    # Save audio locally
    audio_file_path = save_audio_file(uploaded_file)
    st.info("Transcribing the audio file...")

    # Transcribe the audio file
    transcription = transcribe_audio(audio_file_path)

    if transcription:
        # Display transcription
        st.subheader("Transcription")
        st.write(transcription)

# Helper function: Perform analysis combining text and audio features
def combined_analysis(transcription, audio_path, call_analyzer):
    try:
        # Perform combined analysis (text + audio features)
        analysis_results = call_analyzer.analyze(transcription, audio_path)
        
        # Determine language proficiency
        language_proficiency = call_analyzer.analyze_language_proficiency(transcription)

        return analysis_results, language_proficiency
    except Exception as e:
        st.error(f"Error performing analysis: {e}")
        return None, None

# Initialize CallAnalyzer
call_analyzer = CallAnalyzer()

if uploaded_file and transcription:
    # Step 2: Perform Combined Analysis (Text + Audio Features)
    st.info("Analyzing transcription and audio features for sentiment, urgency, and metadata...")

    analysis_results, language_proficiency = combined_analysis(
        transcription, audio_file_path, call_analyzer
    )

    if analysis_results:
        # Display conversation analysis results
        st.subheader("Conversation Analysis")
        st.write(f"**Sentiment:** {analysis_results['sentiment']}")
        st.write(f"**Urgency:** {analysis_results['urgency']}")
        st.write(f"**Intent:** {analysis_results['intent']}")
        st.write(f"**Language Proficiency:** {language_proficiency}")
        st.write("**Extracted Metadata:**")
        st.json(analysis_results["metadata"])

        # Extracted name from metadata
        extracted_name = analysis_results["metadata"].get("name", [""])[0] if analysis_results["metadata"].get("name") else "Ravi Singh"

        # Extracted claim ID from metadata and ensure it's an integer
        extracted_claim_id = analysis_results["metadata"].get("claim_id", [None])[0] if analysis_results["metadata"].get("claim_id") else "11"
        if extracted_claim_id is not None:
            extracted_claim_id = int(extracted_claim_id)

# Agent Matching and Scheduling Workflow
if st.checkbox("Perform Agent Matching and Schedule"):
    st.info("Matching a suitable agent for the call...")

    # Input fields for client details
    client_name = st.text_input("Enter Client Name", extracted_name)
    contact_info = st.text_input("Enter Contact Info (e.g., email, phone)", "9987549758")
    first_time_caller = st.checkbox("Is this their first time calling?", value=True)
    claim_id = st.number_input("Enter Claim ID*", min_value=11, step=1, value=extracted_claim_id if extracted_claim_id else 11)

    # Button to start the assignment process
    if st.button("Assign Agent to Call"):
        # Add the client to the database if not already present
        client_id = add_client(client_name, contact_info, first_time_caller)

        # Perform agent matching and scheduling
        matched_agent = assign_agent_and_schedule(
            client_id=client_id,
            urgency=analysis_results["urgency"],
            intent=analysis_results["intent"],
            metadata=analysis_results["metadata"],
            transcription=transcription,
            sentiment=analysis_results["sentiment"],
            claim_id=claim_id
        )

        # Display the results of the agent assignment
        if matched_agent:
            st.subheader("Assigned Agent")
            st.write(f"**Name:** {matched_agent['Name']}")
            st.write(f"**Proficiency:** {matched_agent['Proficiency']}")
            st.write(f"**Specialization:** {matched_agent['Specialization']}")
            st.write(f"**Shift Time:** {matched_agent['ShiftStart']} - {matched_agent['ShiftEnd']}")
            st.write(f"**Tiredness Level:** {matched_agent['TirednessLevel']}")
            st.success("Agent successfully assigned to the call!")

            # Load the updated schedule for the agent
            agent_schedule = get_agent_schedule(matched_agent["AgentID"])

            # Checkbox to show the updated schedule
            if st.checkbox("Show Agent's Updated Schedule"):
                st.subheader("Agent's Updated Schedule")
                st.write(agent_schedule)
        else:
            st.warning("No suitable agent found. Please check agent availability or database entries.")

        # Step 5 (Optional): Show Client's Call History
        if st.checkbox("Show Client's Call History"):
            client_calls = get_calls_by_client(client_id)
            if client_calls:
                st.subheader(f"Call History for {client_name}")
                st.write(client_calls)
            else:
                st.warning("No call history available for this client.")
