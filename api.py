from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database.agent_database import get_agent_by_id, get_all_agents
from database.client_database import get_client_by_id, get_calls_by_client

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for cross-origin access
# This allows access to the API from web apps, mobile apps, etc.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Change this in production to allow specific origins.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# --- API ROUTES ---

# 1. Fetch agent details by their AgentID
@app.get("/agents/{agent_id}")
async def get_agent_details(agent_id: int):
    """
    Get detailed information about a specific agent by their unique AgentID.

    Args:
        agent_id (int): The unique ID of the agent.

    Returns:
        JSON object with the agent's details:
        {
            "AgentID": int,
            "Name": str,
            "Proficiency": str,
            "Specialization": str,
            "Status": str,
            "CurrentCalls": int,
            "ShiftStart": str,
            "ShiftEnd": str,
            "TirednessLevel": int
        }

    HTTP 404 Error if the agent is not found.
    """
    agent = get_agent_by_id(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found.")
    return agent  # JSON response with agent details


# 2. Fetch details of all agents (useful for debugging or showing all agent data)
@app.get("/agents/")
async def get_all_agents_api():
    """
    Get details of all agents in the system.

    Returns:
        JSON array, where each item represents an agent:
        [
            {
                "AgentID": int,
                "Name": str,
                "Proficiency": str,
                "Specialization": str,
                "Status": str,
                "CurrentCalls": int,
                "ShiftStart": str,
                "ShiftEnd": str,
                "TirednessLevel": int
            },
            ...
        ]
    """
    agents = get_all_agents()
    return agents  # JSON response with all agents


# 3. Fetch client details by their ClientID
@app.get("/clients/{client_id}")
async def get_client_details(client_id: int):
    """
    Get detailed information about a specific client by their unique ClientID.

    Args:
        client_id (int): The unique ID of the client.

    Returns:
        JSON object with the client's details:
        {
            "ClientID": int,
            "Name": str,
            "ContactInfo": str,
            "FirstTimeCaller": bool
        }

    HTTP 404 Error if the client is not found.
    """
    client = get_client_by_id(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail=f"Client with ID {client_id} not found.")
    return client  # JSON response with client details


# 4. Fetch all call history for a specific client by their ClientID
@app.get("/clients/{client_id}/calls")
async def get_client_call_history(client_id: int):
    """
    Get the call history of a specific client by their unique ClientID.

    Args:
        client_id (int): The unique ID of the client.

    Returns:
        JSON array, where each item represents a call made by the client:
        [
            {
                "CallID": int,
                "ClientID": int,
                "Metadata": str,
                "Transcription": str,
                "Sentiment": str,
                "Urgency": str,
                "Intent": str,
                "AssignedAgentID": int
            },
            ...
        ]

    HTTP 404 Error if no calls are found for the client.
    """
    calls = get_calls_by_client(client_id)
    if not calls:
        raise HTTPException(status_code=404, detail=f"No calls found for client with ID {client_id}.")
    return calls  # JSON response with client's call history


# 5. Fetch all calls assigned to a specific agent, sorted by time (agent's schedule)
@app.get("/agents/{agent_id}/schedule")
async def get_agent_schedule(agent_id: int):
    """
    Get the schedule of a specific agent by their unique AgentID.
    The schedule includes all calls assigned to the agent, sorted by time.

    Args:
        agent_id (int): The unique ID of the agent.

    Returns:
        JSON array, where each item represents a scheduled call:
        [
            {
                "CallID": int,
                "ClientID": int,
                "ClientName": str,
                "StartTime": str,
                "EndTime": str,
                "Transcription": str,
                "Sentiment": str,
                "Urgency": str,
                "Intent": str
            },
            ...
        ]

    HTTP 404 Error if the agent or their schedule cannot be found.
    """
    # For simplicity, here's mockup scheduling data (replace with real query logic if DB supports schedules)
    schedule = [
        {
            "CallID": 1,
            "ClientID": 1,
            "ClientName": "John Doe",
            "StartTime": "10:00 AM",
            "EndTime": "10:30 AM",
            "Transcription": "I need help with my insurance claim.",
            "Sentiment": "Negative",
            "Urgency": "High",
            "Intent": "Claim Inquiry"
        },
        {
            "CallID": 2,
            "ClientID": 2,
            "ClientName": "Jane Smith",
            "StartTime": "11:00 AM",
            "EndTime": "11:30 AM",
            "Transcription": "Can you tell me more about your services?",
            "Sentiment": "Positive",
            "Urgency": "Low",
            "Intent": "General Inquiry"
        }
    ]

    # Check if agent exists (to validate the agent_id)
    agent = get_agent_by_id(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found.")

    # For now, return mockup data. You can replace this with DB query results.
    return schedule
