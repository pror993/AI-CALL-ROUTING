import sqlite3
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
        ("John Doe", "johndoe@example.com", True),   # First-time caller
        ("Jane Smith", "janesmith@example.com", False),  # Returning caller
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO Clients (Name, ContactInfo, FirstTimeCaller)
        VALUES (?, ?, ?)
    ''', clients)

    conn.commit()
    conn.close()

# Add a new client to the Clients table
def add_client(name: str, contact_info: str, first_time_caller: bool) -> int:
    """
    Adds a new client to the Clients table if they do not already exist.
    If the client exists, their ClientID is returned.

    Args:
        name (str): Name of the client.
        contact_info (str): Contact information of the client (e.g., email, phone).
        first_time_caller (bool): Whether this is the client's first call.

    Returns:
        int: The ClientID of the client (newly added or existing).
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if the client already exists in the Clients table
    cursor.execute('''
        SELECT ClientID FROM Clients WHERE Name = ? AND ContactInfo = ?
    ''', (name, contact_info))
    result = cursor.fetchone()

    # If the client exists, return their ClientID
    if result:
        client_id = result[0]
    else:
        # Insert the client into the Clients table
        cursor.execute('''
            INSERT INTO Clients (Name, ContactInfo, FirstTimeCaller)
            VALUES (?, ?, ?)
        ''', (name, contact_info, first_time_caller))

        # Get the ID of the newly inserted client
        client_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return client_id

# Fetch a client by their ID
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
            "FirstTimeCaller": bool(client[3]),
        }
    return None

# Retrieve all calls for a specific client
def get_calls_by_client(client_id: int) -> List[Dict]:
    """
    Fetch all calls for a specific client.

    Args:
        client_id (int): Unique identifier for the client.

    Returns:
        List[Dict]: A list of dictionaries representing calls made by the client.
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

# Record a new call in the Calls table
def record_call(
    client_id: int,
    metadata: Dict,
    transcription: str,
    sentiment: str,
    urgency: str,
    intent: str,
    agent_id: int
):
    """
    Records a new call in the Calls table for a specific client.

    Args:
        client_id (int): The ID of the client making the call.
        metadata (Dict): Metadata about the call (e.g., extracted key phrases).
        transcription (str): Text transcription of the call.
        sentiment (str): Sentiment analysis result (Positive, Negative, Neutral).
        urgency (str): The urgency level of the call (High, Medium, Low).
        intent (str): The detected intent of the call (e.g., Support, General Inquiry).
        agent_id (int): The ID of the agent assigned to the call.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Serialize metadata as a string for storage
    metadata_str = str(metadata)

    # Insert the call into the Calls table
    cursor.execute('''
        INSERT INTO Calls (ClientID, Metadata, Transcription, Sentiment, Urgency, Intent, AssignedAgentID)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (client_id, metadata_str, transcription, sentiment, urgency, intent, agent_id))

    conn.commit()
    conn.close()
