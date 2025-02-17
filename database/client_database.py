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
            ClaimID INTEGER,
            AssignedAgentID INTEGER,
            FOREIGN KEY (ClientID) REFERENCES Clients (ClientID),
            FOREIGN KEY (AssignedAgentID) REFERENCES Agents (AgentID)
        )
    ''')

    # Insert mockup client data
    clients = [
        ("Harsh Kumar", "+919876543210", True),
        ("Anita Rao", "+919876543211", False),
        ("Rohit Sharma", "+919876543212", True),
        ("Sneha Kapoor", "+919876543213", False),
        ("Vikas Gupta", "+919876543214", True),
        ("Suresh Reddy", "+919876543215", False),
        ("Neha Gupta", "+919876543216", True),
        ("Rahul Verma", "+919876543217", False),
        ("Pooja Desai", "+919876543218", True),
        ("Karan Joshi", "+919876543219", False),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO Clients (Name, ContactInfo, FirstTimeCaller)
        VALUES (?, ?, ?)
    ''', clients)

    # Insert mockup call data
    calls = [
        (1, json.dumps({"name": ["Harsh Kumar"], "purpose": "Hospital Bill issue", "claim_id": "5"}), "I submitted a health insurance claim last week. Can you update me on its status and expected payout date?...", "Positive", "High", "Inquiry", 1, 1),
        (2, json.dumps({"name": ["Anita Rao"], "purpose": "Pre-authorization for Treatment", "claim_id": "12"}), "I need to undergo surgery next week. Can you confirm if my insurance policy covers it and what documents are required for approval?...", "Negative", "Medium", "Support", 2, 2),
        (3, json.dumps({"name": ["Rohit Sharma"], "purpose": "Credit Card Chargeback Requests", "claim_id": "8"}), "I noticed an unauthorized transaction on my credit card. How can I dispute this charge and request a refund?...", "Neutral", "High", "Complaint", 3, 3),
        (4, json.dumps({"name": ["Sneha Kapoor"], "purpose": "Flight Delay Compensation", "claim_id": "15"}), "My flight was delayed for over 6 hours. Am I eligible for compensation under my travel insurance policy?...", "Positive", "Low", "Inquiry", 4, 1),
        (5, json.dumps({"name": ["Vikas Gupta"], "purpose": "Product Damage Claim", "claim_id": "20"}), "I received a damaged phone from your online store. Can you process a replacement under the return policy?...", "Negative", "Medium", "Support", 5, 2),
        (6, "Metadata for call 6", "Transcription for call 6", "Neutral", "Medium", "Support", 6, 3),
        (7, "Metadata for call 7", "Transcription for call 7", "Positive", "High", "Inquiry", 7, 1),
        (8, "Metadata for call 8", "Transcription for call 8", "Negative", "Low", "Complaint", 8, 2),
        (9, "Metadata for call 9", "Transcription for call 9", "Neutral", "Medium", "Support", 9, 3),
        (10, "Metadata for call 10", "Transcription for call 10", "Positive", "High", "Inquiry", 10, 1),
    ]

    cursor.executemany('''
        INSERT INTO Calls (ClientID, Metadata, Transcription, Sentiment, Urgency, Intent, ClaimID, AssignedAgentID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
            "ClaimID": call[7],
            "AssignedAgentID": call[8],
        }
        for call in calls
    ]

# Add a new client to the database or return the existing client ID if the client already exists
def add_client(name: str, contact_info: str, first_time_caller: bool) -> int:
    """
    Add a new client to the database or return the existing client ID if the client already exists.

    Args:
        name (str): The name of the client.
        contact_info (str): The contact information of the client.
        first_time_caller (bool): Whether the client is a first-time caller.

    Returns:
        int: The ClientID of the client.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if the client already exists based on contact information
    cursor.execute("SELECT ClientID FROM Clients WHERE ContactInfo = ?", (contact_info,))
    client = cursor.fetchone()

    if client:
        client_id = client[0]
    else:
        # Insert new client if not already present
        cursor.execute('''
            INSERT INTO Clients (Name, ContactInfo, FirstTimeCaller)
            VALUES (?, ?, ?)
        ''', (name, contact_info, first_time_caller))
        conn.commit()
        client_id = cursor.lastrowid

    conn.close()
    return client_id

# Record a new call for a client
def record_call(client_id: int, metadata: Dict, transcription: str, sentiment: str, urgency: str, intent: str, claim_id: int, assigned_agent_id: int):
    """
    Record a new call for a client.

    Args:
        client_id (int): The unique ID of the client.
        metadata (Dict): Metadata about the call.
        transcription (str): Transcription of the call.
        sentiment (str): Sentiment of the call.
        urgency (str): Urgency of the call.
        intent (str): Intent of the call.
        claim_id (int): The ID of the claim.
        assigned_agent_id (int): The ID of the assigned agent.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Serialize metadata as a JSON string
    metadata_json = json.dumps(metadata)

    cursor.execute('''
        INSERT INTO Calls (ClientID, Metadata, Transcription, Sentiment, Urgency, Intent, ClaimID, AssignedAgentID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (client_id, metadata_json, transcription, sentiment, urgency, intent, claim_id, assigned_agent_id))

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