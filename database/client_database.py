import sqlite3
import json
from typing import Dict, List

DATABASE_PATH = "database/data/clients.db"  # Path to the SQLite database file

# Initialize the Clients and Calls tables with mockup data
def initialize_client_database():
    """
    Initializes the client database, creating the Clients and Calls tables and populating
    them with mockup data.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create the Clients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Clients (
            ClientID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            ContactInfo TEXT,
            FirstTimeCaller BOOLEAN
        )
    ''')

    # Create the Calls table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Calls (
            CallID INTEGER PRIMARY KEY AUTOINCREMENT,
            ClientID INTEGER,
            Metadata TEXT,
            Transcription TEXT,
            Sentiment TEXT,
            Urgency TEXT,
            Intent TEXT,
            AssignedAgentID INTEGER,
            FOREIGN KEY (ClientID) REFERENCES Clients (ClientID),
            FOREIGN KEY (AssignedAgentID) REFERENCES Agents (AgentID)
        )
    ''')

    # Insert mockup client data
    clients = [
        ("Amit Sharma", "amit.sharma@example.com", True),
        ("Priya Singh", "priya.singh@example.com", False),
        ("Vikram Patel", "vikram.patel@example.com", True),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO Clients (Name, ContactInfo, FirstTimeCaller)
        VALUES (?, ?, ?)
    ''', clients)

    # Insert mockup call data
    calls = [
        (1, "Metadata for call 1", "Transcription for call 1", "Positive", "High", "Inquiry", 1),
        (2, "Metadata for call 2", "Transcription for call 2", "Negative", "Low", "Complaint", 2),
        (3, "Metadata for call 3", "Transcription for call 3", "Neutral", "Medium", "Support", 3),
    ]

    cursor.executemany('''
        INSERT INTO Calls (ClientID, Metadata, Transcription, Sentiment, Urgency, Intent, AssignedAgentID)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', calls)

    conn.commit()
    conn.close()

# Retrieve client details by their ID
def get_client_by_id(client_id: int) -> Dict:
    """
    Fetch a client by their ID.

    Args:
        client_id (int): Unique identifier for the client.

    Returns:
        Dict: A dictionary of the client's details or None if not found.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Clients WHERE ClientID = ?", (client_id,))
    client = cursor.fetchone()
    conn.close()

    if client:
        return {
            "ClientID": client[0],
            "Name": client[1],
            "ContactInfo": client[2],
            "FirstTimeCaller": client[3],
        }
    return None

# Retrieve all calls for a specific client
def get_calls_by_client(client_id: int) -> List[Dict]:
    """
    Fetch all calls for a specific client by their ID.

    Args:
        client_id (int): Unique identifier for the client.

    Returns:
        List[Dict]: A list of dictionaries representing the client's call history.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Calls WHERE ClientID = ?", (client_id,))
    calls = cursor.fetchall()
    conn.close()

    return [
        {
            "CallID": call[0],
            "ClientID": call[1],
            "Metadata": call[2],
            "Transcription": call[3],
            "Sentiment": call[4],
            "Urgency": call[5],
            "Intent": call[6],
            "AssignedAgentID": call[7],
        }
        for call in calls
    ]

# Add a new client to the database
def add_client(name: str, contact_info: str, first_time_caller: bool) -> int:
    """
    Add a new client to the database.

    Args:
        name (str): The name of the client.
        contact_info (str): The contact information of the client.
        first_time_caller (bool): Whether the client is a first-time caller.

    Returns:
        int: The ClientID of the newly added client.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Clients (Name, ContactInfo, FirstTimeCaller)
        VALUES (?, ?, ?)
    ''', (name, contact_info, first_time_caller))

    conn.commit()
    client_id = cursor.lastrowid
    conn.close()

    return client_id

# Record a new call for a client
def record_call(client_id: int, metadata: Dict, transcription: str, sentiment: str, urgency: str, intent: str, assigned_agent_id: int):
    """
    Record a new call for a client.

    Args:
        client_id (int): The unique ID of the client.
        metadata (Dict): Metadata about the call.
        transcription (str): Transcription of the call.
        sentiment (str): Sentiment of the call.
        urgency (str): Urgency of the call.
        intent (str): Intent of the call.
        assigned_agent_id (int): The ID of the assigned agent.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Serialize metadata as a JSON string
    metadata_json = json.dumps(metadata)

    cursor.execute('''
        INSERT INTO Calls (ClientID, Metadata, Transcription, Sentiment, Urgency, Intent, AssignedAgentID)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (client_id, metadata_json, transcription, sentiment, urgency, intent, assigned_agent_id))

    conn.commit()
    conn.close()

# Fetch all clients
def get_all_clients() -> List[Dict]:
    """
    Fetch all clients in the database.

    Returns:
        List[Dict]: A list of dictionaries representing clients.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Clients")
    clients = cursor.fetchall()
    conn.close()

    return [
        {
            "ClientID": client[0],
            "Name": client[1],
            "ContactInfo": client[2],
            "FirstTimeCaller": client[3],
        }
        for client in clients
    ]