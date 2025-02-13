import sqlite3
from typing import Dict, List

DATABASE_PATH = "database/data/agents.db"  # SQLite database file for agents


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
