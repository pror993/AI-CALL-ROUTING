from database.agent_database import initialize_agent_database
from database.client_database import initialize_client_database

if __name__ == "__main__":
    # Initialize the databases
    initialize_agent_database()
    initialize_client_database()
    print("Databases have been created and initialized.")
