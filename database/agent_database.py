import sqlite3
from typing import Dict, List

DATABASE_PATH = "database/data/agents.db"  # SQLite database file for agents
CLIENTS_DATABASE_PATH = "database/data/clients.db"  # SQLite database file for clients

# Initialize the Agents database and populate with mockup data
def initialize_agent_database():
    """
    Initializes the agent database, creating the Agents table and populating it with mockup data.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create the Agents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Agents (
            AgentID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Proficiency TEXT,
            Specialization TEXT,
            Status TEXT,
            CurrentCalls INTEGER,
            ShiftStart TIME,
            ShiftEnd TIME,
            TirednessLevel INTEGER
        )
    ''')

    # Create the Schedule table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Schedule (
            ScheduleID INTEGER PRIMARY KEY AUTOINCREMENT,
            AgentID INTEGER,
            ClientID INTEGER,
            StartTime TEXT,
            EndTime TEXT,
            FOREIGN KEY (AgentID) REFERENCES Agents (AgentID),
            FOREIGN KEY (ClientID) REFERENCES Clients (ClientID)
        )
    ''')

    # Insert mockup agent data
    agents = [
        ("Rajesh", "High", "Death Claims", "Available", 0, "08:00", "16:00", 10),
        ("Mukesh", "Medium", "Motor Claims", "Available", 0, "09:00", "17:00", 20),
        ("Richa", "High", "Technical Support", "Available", 2, "10:00", "18:00", 30),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO Agents (Name, Proficiency, Specialization, Status, CurrentCalls, ShiftStart, ShiftEnd, TirednessLevel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', agents)

    # Insert mockup schedule data
    schedules = [
        (1, 1, "2025-02-13 10:00:00", "2025-02-13 10:30:00"),
        (2, 2, "2025-02-13 11:00:00", "2025-02-13 11:30:00"),
        (3, 3, "2025-02-13 12:00:00", "2025-02-13 12:30:00"),
        (1, 4, "2025-02-13 13:00:00", "2025-02-13 13:30:00"),
        (2, 5, "2025-02-13 14:00:00", "2025-02-13 14:30:00"),
        (3, 6, "2025-02-13 15:00:00", "2025-02-13 15:30:00"),
        (1, 7, "2025-02-13 16:00:00", "2025-02-13 16:30:00"),
        (2, 8, "2025-02-13 17:00:00", "2025-02-13 17:30:00"),
        (3, 9, "2025-02-13 18:00:00", "2025-02-13 18:30:00"),
        (1, 10, "2025-02-13 19:00:00", "2025-02-13 19:30:00"),
    ]

    cursor.executemany('''
        INSERT INTO Schedule (AgentID, ClientID, StartTime, EndTime)
        VALUES (?, ?, ?, ?)
    ''', schedules)

    conn.commit()
    conn.close()

# Retrieve all agents
def get_all_agents() -> List[Dict]:
    """
    Fetch all agents in the database.

    Returns:
        List[Dict]: A list of dictionaries representing agents.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Agents")
    agents = cursor.fetchall()
    conn.close()

    return [
        {
            "AgentID": agent[0],
            "Name": agent[1],
            "Proficiency": agent[2],
            "Specialization": agent[3],
            "Status": agent[4],
            "CurrentCalls": agent[5],
            "ShiftStart": agent[6],
            "ShiftEnd": agent[7],
            "TirednessLevel": agent[8],
        }
        for agent in agents
    ]

# Retrieve an agent by their ID
def get_agent_by_id(agent_id: int) -> Dict:
    """
    Fetch an agent by their ID.

    Args:
        agent_id (int): Unique identifier for the agent.

    Returns:
        Dict: A dictionary of the agent's details or None if not found.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Agents WHERE AgentID = ?", (agent_id,))
    agent = cursor.fetchone()
    conn.close()

    if agent:
        return {
            "AgentID": agent[0],
            "Name": agent[1],
            "Proficiency": agent[2],
            "Specialization": agent[3],
            "Status": agent[4],
            "CurrentCalls": agent[5],
            "ShiftStart": agent[6],
            "ShiftEnd": agent[7],
            "TirednessLevel": agent[8],
        }
    return None

# Update an agent's status and workload
def update_agent_status(agent_id: int, status: str, tiredness: int):
    """
    Update an agent's status and tiredness level.

    Args:
        agent_id (int): Unique identifier for the agent.
        status (str): New status for the agent (e.g., 'Available', 'Busy').
        tiredness (int): Updated tiredness level for the agent.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE Agents
        SET Status = ?, TirednessLevel = ?
        WHERE AgentID = ?
    ''', (status, tiredness, agent_id))

    conn.commit()
    conn.close()

# Add a new schedule entry
def add_schedule(agent_id: int, client_id: int, start_time: str, end_time: str):
    """
    Add a new schedule entry for an agent.

    Args:
        agent_id (int): Unique identifier for the agent.
        client_id (int): Unique identifier for the client.
        start_time (str): Start time of the scheduled call.
        end_time (str): End time of the scheduled call.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO Schedule (AgentID, ClientID, StartTime, EndTime)
        VALUES (?, ?, ?, ?)
    ''', (agent_id, client_id, start_time, end_time))

    conn.commit()
    conn.close()

# Retrieve the schedule for a specific agent
def get_agent_schedule(agent_id: int) -> List[Dict]:
    """
    Fetch the schedule for a specific agent.

    Args:
        agent_id (int): Unique identifier for the agent.

    Returns:
        List[Dict]: A list of dictionaries representing the agent's schedule.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Attach the clients database
    cursor.execute(f"ATTACH DATABASE '{CLIENTS_DATABASE_PATH}' AS clients_db")

    cursor.execute('''
        SELECT Schedule.ScheduleID, Schedule.AgentID, Schedule.ClientID, Schedule.StartTime, Schedule.EndTime,
               clients_db.Clients.Name AS ClientName, clients_db.Clients.ContactInfo AS ClientContactInfo, clients_db.Clients.FirstTimeCaller AS ClientFirstTimeCaller
        FROM Schedule
        JOIN clients_db.Clients ON Schedule.ClientID = clients_db.Clients.ClientID
        WHERE Schedule.AgentID = ?
    ''', (agent_id,))
    schedule = cursor.fetchall()
    conn.close()

    return [
        {
            "ScheduleID": entry[0],
            "AgentID": entry[1],
            "ClientID": entry[2],
            "StartTime": entry[3],
            "EndTime": entry[4],
            "ClientName": entry[5],
            "ClientContactInfo": entry[6],
            "ClientFirstTimeCaller": entry[7],
        }
        for entry in schedule
    ]