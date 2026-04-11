from database.agent_database import get_all_agents, update_agent_status, add_schedule
from database.client_database import record_call
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import heapq

# Priority queue for handling calls based on urgency
call_queue = []

def match_agent(urgency: str, intent: str) -> Optional[Dict]:
    """
    Match a suitable agent for a call based on urgency, intent, and agent attributes.

    Args:
        urgency (str): The urgency level of the call (High, Medium, Low).
        intent (str): The intent of the call (e.g., Support, Sales, Technical Inquiry).

    Returns:
        Dict: Details of the best-matched agent, or None if no agent is available.
    """
    # Step 1: Get all available agents
    agents = get_all_agents()
    available_agents = [agent for agent in agents if agent["Status"] == "Available"]

    if not available_agents:
        return None  # No agents are available

    # Step 2: Define a scoring function based on agent attributes and call metadata
    def calculate_agent_score(agent: Dict) -> float:
        score = 0

        # Match urgency level
        urgency_weights = {"High": 3, "Medium": 2, "Low": 1}
        if urgency in urgency_weights:
            if urgency == "High" and agent["Proficiency"] == "High":
                score += urgency_weights["High"]
            elif urgency == "Medium" and agent["Proficiency"] in ["Medium", "High"]:
                score += urgency_weights["Medium"]
            elif urgency == "Low":
                score += urgency_weights["Low"]

        # Match intent with specialization
        if intent.lower() == agent["Specialization"].lower():
            score += 3  # Higher weight for matching specialization

        # Reduce score based on tiredness level
        score -= agent["TirednessLevel"] * 0.1  # Higher tiredness reduces score slightly

        # Promote agents with fewer current calls
        score -= agent["CurrentCalls"] * 0.2  # Penalize agents with higher workloads

        return score

    # Step 3: Sort agents by their calculated scores
    available_agents.sort(key=calculate_agent_score, reverse=True)

    # Step 4: Return the best-matched agent
    return available_agents[0] if available_agents else None

def assign_agent_and_schedule(
    client_id: int,
    urgency: str,
    intent: str,
    metadata: Dict,
    transcription: str,
    sentiment: str,
    claim_id: int
) -> Optional[Dict]:
    """
    Assign a matched agent to a call, update their status, and record the call.

    Args:
        client_id (int): The client ID for this call.
        urgency (str): The urgency level of the call (High, Medium, Low).
        intent (str): The intent of the call (e.g., Support, Sales, Technical Inquiry).
        metadata (Dict): Additional metadata extracted from the conversation.
        transcription (str): The text transcription of the conversation.
        sentiment (str): The sentiment detected in the conversation (Positive, Neutral, Negative).
        claim_id (int): The ID of the claim.

    Returns:
        Dict: Details of the assigned agent, or None if no agent is available.
    """
    # Step 1: Match the best agent
    matched_agent = match_agent(urgency, intent)

    if matched_agent:
        # Step 2: Update the agent's status and workload in the database
        update_agent_status(
            agent_id=matched_agent["AgentID"],
            status="Busy",
            tiredness=matched_agent["TirednessLevel"] + 10,  # Increment tiredness level
        )

        # Step 3: Record the call in the database
        record_call(
            client_id=client_id,
            metadata=metadata,
            transcription=transcription,
            sentiment=sentiment,
            urgency=urgency,
            intent=intent,
            claim_id=claim_id,
            assigned_agent_id=matched_agent["AgentID"],
        )

        # Step 4: Add the call to the priority queue based on urgency
        urgency_priority = {"High": 1, "Medium": 2, "Low": 3}
        priority = urgency_priority.get(urgency, 3)
        heapq.heappush(call_queue, (priority, datetime.now(), matched_agent["AgentID"], client_id))

        # Step 5: Update the agent's schedule based on the priority queue
        while call_queue:
            _, start_time, agent_id, client_id = heapq.heappop(call_queue)
            end_time = start_time + timedelta(minutes=30)  # Assuming each call lasts 30 minutes
            add_schedule(
                agent_id=agent_id,
                client_id=client_id,
                start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            )

        # Step 6: Return the matched agent
        return matched_agent

    return None
