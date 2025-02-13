import streamlit as st
import requests
import pandas as pd

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Initialize session state for client selection
if "selected_client_id" not in st.session_state:
    st.session_state.selected_client_id = None

# Helper function to fetch agent details
def fetch_agent_details(agent_id):
    response = requests.get(f"{BASE_URL}/agents/{agent_id}")
    return response.json() if response.status_code == 200 else None

# Helper function to fetch agent schedule
def fetch_agent_schedule(agent_id):
    response = requests.get(f"{BASE_URL}/agents/{agent_id}/schedule")
    return response.json() if response.status_code == 200 else None

# Helper function to fetch client details
def fetch_client_details(client_id):
    response = requests.get(f"{BASE_URL}/clients/{client_id}")
    return response.json() if response.status_code == 200 else None

# Helper function to fetch client call history
def fetch_client_call_history(client_id):
    response = requests.get(f"{BASE_URL}/clients/{client_id}/calls")
    return response.json() if response.status_code == 200 else None

# Streamlit UI: Title
st.title("Agent Schedule and Client Information")

# Step 1: Select Agent
st.sidebar.header("Agent Selection")
agent_id = st.sidebar.number_input("Enter Agent ID", min_value=1, step=1)
if st.sidebar.button("Fetch Agent Schedule"):
    agent_details = fetch_agent_details(agent_id)
    if agent_details:
        st.sidebar.subheader("Agent Details")
        st.sidebar.write(f"**Name:** {agent_details['Name']}")
        st.sidebar.write(f"**Proficiency:** {agent_details['Proficiency']}")
        st.sidebar.write(f"**Specialization:** {agent_details['Specialization']}")
        st.sidebar.write(f"**Status:** {agent_details['Status']}")
        st.sidebar.write(f"**Current Calls:** {agent_details['CurrentCalls']}")
        st.sidebar.write(f"**Shift Time:** {agent_details['ShiftStart']} - {agent_details['ShiftEnd']}")
        st.sidebar.write(f"**Tiredness Level:** {agent_details['TirednessLevel']}")
        
        agent_schedule = fetch_agent_schedule(agent_id)
        if agent_schedule:
            st.subheader("Agent's Schedule")
            schedule_df = pd.DataFrame(agent_schedule)
            if not schedule_df.empty and {'StartTime', 'EndTime', 'ClientID'}.issubset(schedule_df.columns):
                st.table(schedule_df[['StartTime', 'EndTime', 'ClientID']])
                
                client_ids = [entry['ClientID'] for entry in agent_schedule]
                selected_client = st.radio("Select a Client ID", client_ids, index=0, key="client_selector")
                st.session_state.selected_client_id = selected_client

# Display client details and call history if a client is selected
if st.session_state.selected_client_id:
    client_id = st.session_state.selected_client_id
    client_details = fetch_client_details(client_id)
    if client_details:
        with st.expander("Client Details", expanded=True):
            st.write(f"**Name:** {client_details['Name']}")
            st.write(f"**Contact Info:** {client_details['ContactInfo']}")
            st.write(f"**First Time Caller:** {client_details['FirstTimeCaller']}")
        
        client_call_history = fetch_client_call_history(client_id)
        if client_call_history:
            with st.expander("Client's Call History", expanded=False):
                for call in client_call_history:
                    st.write(f"**Call ID:** {call['CallID']}")
                    st.write(f"**Metadata:** {call['Metadata']}")
                    st.write(f"**Transcription:** {call['Transcription']}")
                    st.write(f"**Sentiment:** {call['Sentiment']}")
                    st.write(f"**Urgency:** {call['Urgency']}")
                    st.write(f"**Intent:** {call['Intent']}")
                    st.write(f"**Claim ID:** {call['ClaimID']}")
                    st.write(f"**Assigned Agent ID:** {call['AssignedAgentID']}")
                    st.write("---")