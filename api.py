from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database.agent_database import get_agent_by_id, get_all_agents, get_agent_schedule
from database.client_database import get_client_by_id, get_calls_by_client, get_all_clients

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

# Define your API endpoints here

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
                "ClientID": int,
                "Metadata": str,
                "Transcription": str,
                "Sentiment": str,
                "Urgency": str,
                "Intent": str,
                "ClaimID": int,
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
async def get_agent_schedule_api(agent_id: int):
    """
    Get the schedule of a specific agent by their unique AgentID.
    The schedule includes all calls assigned to the agent, sorted by time.

    Args:
        agent_id (int): The unique ID of the agent.

    Returns:
        JSON array, where each item represents a scheduled call:
        [
            {
                "ScheduleID": int,
                "AgentID": int,
                "ClientID": int,
                "StartTime": str,
                "EndTime": str,
                "ClientName": str,
                "ClientContactInfo": str,
                "ClientFirstTimeCaller": bool
            },
            ...
        ]

    HTTP 404 Error if the agent or their schedule cannot be found.
    """
    # Check if agent exists (to validate the agent_id)
    agent = get_agent_by_id(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found.")

    # Retrieve the agent's schedule from the database
    schedule = get_agent_schedule(agent_id)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"No schedule found for agent with ID {agent_id}.")
    return schedule  # JSON response with agent's schedule


# 6. Fetch all clients and their call histories
@app.get("/clients/")
async def get_all_clients_api():
    """
    Get details of all clients in the system along with their call histories.

    Returns:
        JSON array, where each item represents a client and their call history:
        [
            {
                "ClientID": int,
                "Name": str,
                "ContactInfo": str,
                "FirstTimeCaller": bool,
                "CallHistory": [
                    {
                        "ClientID": int,
                        "Metadata": str,
                        "Transcription": str,
                        "Sentiment": str,
                        "Urgency": str,
                        "Intent": str,
                        "ClaimID": int,
                        "AssignedAgentID": int
                    },
                    ...
                ]
            },
            ...
        ]
    """
    clients = get_all_clients()
    for client in clients:
        client["CallHistory"] = get_calls_by_client(client["ClientID"])
    return clients  # JSON response with all clients and their call histories


# 7. Fetch agent's schedule along with client's call history
@app.get("/agents/{agent_id}/schedule_with_client_history")
async def get_agent_schedule_with_client_history(agent_id: int):
    """
    Get the schedule of a specific agent by their unique AgentID along with the call history of each client in the schedule.

    Args:
        agent_id (int): The unique ID of the agent.

    Returns:
        JSON array, where each item represents a scheduled call along with the client's call history:
        [
            {
                "ScheduleID": int,
                "AgentID": int,
                "ClientID": int,
                "StartTime": str,
                "EndTime": str,
                "ClientName": str,
                "ClientContactInfo": str,
                "ClientFirstTimeCaller": bool,
                "ClientCallHistory": [
                    {
                        "ClientID": int,
                        "Metadata": str,
                        "Transcription": str,
                        "Sentiment": str,
                        "Urgency": str,
                        "Intent": str,
                        "ClaimID": int,
                        "AssignedAgentID": int
                    },
                    ...
                ]
            },
            ...
        ]

    HTTP 404 Error if the agent or their schedule cannot be found.
    """
    # Check if agent exists (to validate the agent_id)
    agent = get_agent_by_id(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent with ID {agent_id} not found.")

    # Retrieve the agent's schedule from the database
    schedule = get_agent_schedule(agent_id)
    if not schedule:
        raise HTTPException(status_code=404, detail=f"No schedule found for agent with ID {agent_id}.")

    # Add client's call history to each schedule entry
    for entry in schedule:
        client_id = entry["ClientID"]
        entry["ClientCallHistory"] = get_calls_by_client(client_id)

    return schedule  # JSON response with agent's schedule and client's call history