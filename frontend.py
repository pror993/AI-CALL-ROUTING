import streamlit as st
import requests
import pandas as pd

# Base API URL
BASE_URL = "http://localhost:8000"

# Set page config
st.set_page_config(page_title="Agent & Client Portal", layout="wide")

# Custom CSS for enhanced UI
st.markdown("""
    <style>
        body {
            background-color: #121212;
            color: white;
        }
        .main {
            padding: 20px;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #4CAF50 !important;
            color: white !important;
            font-size: 16px;
            border-radius: 5px;
        }
        .stNumberInput>div>div>input {
            border-radius: 5px;
            padding: 8px;
            background-color: #222;
            color: white;
        }
        .stTable, .stDataFrame {
            background-color: #ffffff;
            color: black;
            border-radius: 10px;
            padding: 10px;
        }
        .stMarkdown h2, .stMarkdown h3 {
            color: #4CAF50;
        }
        .stMarkdown p {
            color: #E0E0E0;
        }
        .stExpander {
            background-color: #1e1e1e;
            border-radius: 10px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

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

# Streamlit UI
st.title("📊 Agent Schedule and Client Information")

# Layout using columns
col1, col2 = st.columns([1, 2])

# Sidebar - Agent Selection
with col1:
    st.subheader("👨‍💼 Agent Selection")
    agent_id = st.number_input("Enter Agent ID", min_value=1, step=1, value=1)
    if st.button("🔍 Fetch Agent Schedule"):
        agent_details = fetch_agent_details(agent_id)
        if agent_details:
            st.markdown(f"**🆔 Name:** :blue[{agent_details['Name']}]")
            st.markdown(f"**🏆 Proficiency:** {agent_details['Proficiency']}")
            st.markdown(f"**🎯 Specialization:** {agent_details['Specialization']}")

            # Dynamic color for status
            status_color = "🟢" if agent_details["Status"] == "Available" else "🔴"
            st.markdown(f"**📌 Status:** {status_color} {agent_details['Status']}")

            st.markdown(f"**📞 Current Calls:** {agent_details['CurrentCalls']}")
            st.markdown(f"**⏳ Shift Time:** {agent_details['ShiftStart']} - {agent_details['ShiftEnd']}")
            st.markdown(f"**💤 Tiredness Level:** {agent_details['TirednessLevel']}")

            agent_schedule = fetch_agent_schedule(agent_id)
            if agent_schedule:
                st.subheader("📅 Agent's Schedule")

                # Convert schedule to DataFrame
                schedule_df = pd.DataFrame(agent_schedule)

                if not schedule_df.empty and {'StartTime', 'EndTime', 'ClientID'}.issubset(schedule_df.columns):
                    styled_df = schedule_df[['StartTime', 'EndTime', 'ClientID']].style.set_properties(
                        **{
                            "background-color": "#222222",  # Dark background
                            "color": "white",  # White text
                            "border-color": "#444444"  # Soft gray border
                        }
                    )
                    
                    # Display table with styling
                    st.dataframe(styled_df, use_container_width=True)

# Client Information Section
with col2:
    st.subheader("🧑‍💼 Client Information")
    client_id = st.number_input("Enter Client ID", min_value=1, step=1, value=1)
    
    if st.button("🔎 Fetch Client Details"):
        client_details = fetch_client_details(client_id)
        client_call_history = fetch_client_call_history(client_id)
        
        if client_details:
            st.markdown(f"**🆔 Name:** :orange[{client_details['Name']}]")
            st.markdown(f"**📞 Contact Info:** {client_details['ContactInfo']}")
            
            first_time_caller = "✅ Yes" if client_details['FirstTimeCaller'] else "❌ No"
            st.markdown(f"**📌 First Time Caller:** {first_time_caller}")

        if client_call_history:
            st.subheader("📞 Client's Call History")
            with st.expander("View Call History", expanded=False):
                for call in client_call_history:
                    sentiment_color = "🟢" if call['Sentiment'] == "Positive" else "🔴"
                    urgency_color = "🔺 High" if call['Urgency'] == "High" else "🟡 Medium" if call['Urgency'] == "Medium" else "🟢 Low"

                    st.markdown(f"**📞 Call ID:** {call['CallID']}")
                    st.markdown(f"**📋 Metadata:** {call['Metadata']}")
                    st.markdown(f"**📝 Transcription:** {call['Transcription']}")
                    st.markdown(f"**💬 Sentiment:** {sentiment_color} {call['Sentiment']}")
                    st.markdown(f"**⚠️ Urgency:** {urgency_color}")
                    st.markdown(f"**🎯 Intent:** {call['Intent']}")
                    st.markdown(f"**📂 Claim ID:** {call['ClaimID']}")
                    st.markdown(f"**👨‍💼 Assigned Agent ID:** {call['AssignedAgentID']}")
                    st.write("---")
