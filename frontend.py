import streamlit as st
import requests
import pandas as pd
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.mention import mention

# Base API URL
BASE_URL = "http://localhost:8000"

# Set page config
st.set_page_config(page_title="Agent & Client Portal", layout="wide")

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
        }
        .stButton>button {
            background-color: #F0BB78 !important;
            color: #131010 !important;
            font-size: 16px;
            border-radius: 5px;
            border: none;
            padding: 8px 16px;
        }
        .stNumberInput>div>div>input {
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

# Helper functions
def fetch_agent_details(agent_id):
    response = requests.get(f"{BASE_URL}/agents/{agent_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch agent details.")
        return None

def fetch_agent_schedule(agent_id):
    response = requests.get(f"{BASE_URL}/agents/{agent_id}/schedule")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch agent schedule.")
        return None

def fetch_client_details(client_id):
    response = requests.get(f"{BASE_URL}/clients/{client_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch client details.")
        return None

def fetch_client_call_history(client_id):
    response = requests.get(f"{BASE_URL}/clients/{client_id}/calls")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch client call history.")
        return None

def fetch_all_agents():
    response = requests.get(f"{BASE_URL}/agents/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch all agents.")
        return None

def fetch_all_clients():
    response = requests.get(f"{BASE_URL}/clients/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch all clients.")
        return None

# Streamlit UI
st.title("Agent Schedule and Client Information")

# Layout using columns
col1, col2 = st.columns([1, 2])

# Sidebar - Agent Selection
with st.sidebar:
    st.header("Agent Selection")
    agent_id = st.number_input("Enter Agent ID", min_value=1, step=1, value=1)
    if st.button("Fetch Agent Schedule"):
        agent_details = fetch_agent_details(agent_id)
        if agent_details:
            st.subheader("Agent Details")
            st.markdown(f"**Name:** {agent_details['Name']}")
            st.markdown(f"**Proficiency:** {agent_details['Proficiency']}")
            st.markdown(f"**Specialization:** {agent_details['Specialization']}")
            st.markdown(f"**Status:** {agent_details['Status']}")
            st.markdown(f"**Current Calls:** {agent_details['CurrentCalls']}")
            st.markdown(f"**Shift Time:** {agent_details['ShiftStart']} - {agent_details['ShiftEnd']}")
            st.markdown(f"**Tiredness Level:** {agent_details['TirednessLevel']}")

            agent_schedule = fetch_agent_schedule(agent_id)
            if agent_schedule:
                st.subheader("Agent's Schedule")
                schedule_df = pd.DataFrame(agent_schedule)
                if not schedule_df.empty:
                    # Format date and time columns
                    schedule_df['Start Date'] = pd.to_datetime(schedule_df['StartTime']).dt.strftime('%Y-%m-%d')
                    schedule_df['Start Time'] = pd.to_datetime(schedule_df['StartTime']).dt.strftime('%H:%M:%S')
                    schedule_df['End Date'] = pd.to_datetime(schedule_df['EndTime']).dt.strftime('%Y-%m-%d')
                    schedule_df['End Time'] = pd.to_datetime(schedule_df['EndTime']).dt.strftime('%H:%M:%S')
                    schedule_df = schedule_df[['Start Date', 'Start Time', 'End Date', 'End Time', 'ClientID']]
                    st.dataframe(schedule_df, use_container_width=True)

# Client Information Section
with col2:
    st.subheader("Client Information")
    client_id = st.number_input("Enter Client ID", min_value=1, step=1, value=1)
    if st.button("Fetch Client Details"):
        client_details = fetch_client_details(client_id)
        client_call_history = fetch_client_call_history(client_id)
        
        if client_details:
            st.markdown(f"**Name:** {client_details['Name']}")
            st.markdown(f"**Contact Info:** {client_details['ContactInfo']}")
            st.markdown(f"**First Time Caller:** {'Yes' if client_details['FirstTimeCaller'] else 'No'}")
        
        if client_call_history:
            st.subheader("Client's Call History")
            with st.expander("View Call History"):
                for call in client_call_history:
                    urgency_icon = "🔺" if call['Urgency'] == "High" else "🟡" if call['Urgency'] == "Medium" else "🟢"
                    st.markdown(
                        f"""
                        <div class="card">
                            <h4>Call ID: {call['CallID']}</h4>
                            <p><strong>Metadata:</strong> {call['Metadata']}</p>
                            <p><strong>Transcription:</strong> {call['Transcription']}</p>
                            <p><strong>Sentiment:</strong> {call['Sentiment']}</p>
                            <p><strong>Urgency:</strong> {urgency_icon} {call['Urgency']}</p>
                            <p><strong>Intent:</strong> {call['Intent']}</p>
                            <p><strong>Claim ID:</strong> {call['ClaimID']}</p>
                            <p><strong>Assigned Agent ID:</strong> {call['AssignedAgentID']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# Manager View Section
st.subheader("Manager View")

# Fetch and display all agents
if st.button("Fetch All Agents"):
    all_agents = fetch_all_agents()
    if all_agents:
        st.subheader("All Agents")
        agents_df = pd.DataFrame(all_agents)
        st.dataframe(agents_df, use_container_width=True)

# Fetch and display all clients
if st.button("Fetch All Clients"):
    all_clients = fetch_all_clients()
    if all_clients:
        st.subheader("All Clients")
        clients_df = pd.DataFrame(all_clients)
        st.dataframe(clients_df, use_container_width=True)

# Additional Information Section
with st.expander("How It Works", expanded=False):
    st.markdown(
        """
        <div class="info-box">
            <h4>How It Works</h4>
            <p>This application uses AI-powered call routing and analysis to streamline the process of handling customer calls. Here's how it works:</p>
            <ul>
                <li><strong>Audio Transcription:</strong> Converts uploaded audio files into text using Google Speech Recognition.</li>
                <li><strong>Sentiment and Metadata Analysis:</strong> Analyzes the transcribed text for sentiment, urgency, intent, and extracts metadata such as client name and claim ID.</li>
                <li><strong>Agent Matching:</strong> Matches clients with suitable agents based on the analysis results, agent proficiency, and workload.</li>
                <li><strong>Database Management:</strong> Manages client and agent data using SQLite databases.</li>
                <li><strong>API Endpoints:</strong> Provides API endpoints for accessing agent and client data, and their schedules and call histories.</li>
                <li><strong>Frontend Dashboard:</strong> A React-based dashboard for viewing and managing agent schedules and client information.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
