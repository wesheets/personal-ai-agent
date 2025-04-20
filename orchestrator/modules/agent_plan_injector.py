"""
Agent Plan Injector Module

This module provides functionality to create and inject execution contracts to agents
before they build anything, ensuring no agent can execute without receiving, validating,
and logging its assignment.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.tool_predictor import predict_required_tools, check_tool_availability

def generate_agent_contract(agent: str, loop_plan: dict) -> dict:
    """
    Creates the execution task contract for a single agent.
    
    Args:
        agent (str): The agent identifier (e.g., "hal", "nova", "critic")
        loop_plan (dict): The loop plan containing goals and files
        
    Returns:
        dict: The agent execution contract
    """
    if not loop_plan or not isinstance(loop_plan, dict):
        raise ValueError("Invalid loop plan object")
    
    if not agent or not isinstance(agent, str):
        raise ValueError("Invalid agent identifier")
    
    loop_id = loop_plan.get("loop_id")
    if not loop_id:
        raise ValueError("Loop plan missing loop_id")
    
    # Find a goal for this agent
    # In a real implementation, this would use more sophisticated logic to match goals to agents
    goals = loop_plan.get("goals", [])
    if not goals:
        raise ValueError("Loop plan has no goals")
    
    # For simplicity, assign the first goal to this agent
    # In a real implementation, this would be more sophisticated
    goal = goals[0]
    
    # Find a file for this agent to work on
    # In a real implementation, this would use more sophisticated logic to match files to agents
    planned_files = loop_plan.get("planned_files", [])
    if not planned_files:
        raise ValueError("Loop plan has no planned files")
    
    # For simplicity, assign the first file to this agent
    # In a real implementation, this would be more sophisticated
    file = planned_files[0]
    
    # Determine tools required for this agent
    # In a real implementation, this would be more targeted to the specific agent and task
    all_tools = loop_plan.get("tool_requirements", [])
    if not all_tools and "tool_requirements" not in loop_plan:
        # If no tools specified in the plan, predict them
        all_tools = predict_required_tools(loop_plan)
    
    # For simplicity, assign all tools to this agent
    # In a real implementation, this would be more targeted
    tools = all_tools
    
    # Create the contract
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    contract = {
        "loop_id": loop_id,
        "agent": agent,
        "goal": goal,
        "file": file,
        "tools": tools,
        "confirmed": loop_plan.get("confirmed", False),
        "received_at": timestamp,
        "trace_id": f"loop_{loop_id}_{agent}_contract"
    }
    
    return contract

def inject_agent_contract(project_id: str, loop_plan: dict) -> Dict[str, dict]:
    """
    Injects execution contracts to all agents in a loop plan.
    
    Args:
        project_id (str): The project identifier
        loop_plan (dict): The loop plan containing agents, goals, and files
        
    Returns:
        dict: Dictionary mapping agent names to their contracts
    """
    if not loop_plan or not isinstance(loop_plan, dict):
        raise ValueError("Invalid loop plan object")
    
    loop_id = loop_plan.get("loop_id")
    if not loop_id:
        raise ValueError("Loop plan missing loop_id")
    
    # Check if the plan is confirmed
    if not loop_plan.get("confirmed", False):
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"⚠️ Cannot inject agent contracts: Loop plan {loop_id} is not confirmed",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        return {}
    
    # Get the agents from the loop plan
    agents = loop_plan.get("agents", [])
    if not agents:
        raise ValueError("Loop plan has no agents")
    
    # Generate contracts for each agent
    agent_contracts = {}
    for agent in agents:
        try:
            contract = generate_agent_contract(agent, loop_plan)
            agent_contracts[agent] = contract
            
            # Log the contract to memory
            log_to_memory(project_id, {
                "agent_contracts": {
                    agent: contract
                }
            })
            
            # Log to loop trace
            log_to_memory(project_id, {
                "loop_trace": [{
                    "trace_id": contract["trace_id"],
                    "type": "agent_contract_delivered",
                    "loop_id": loop_id,
                    "agent": agent,
                    "file": contract["file"],
                    "timestamp": contract["received_at"]
                }]
            })
            
            # Log to chat
            log_to_chat(project_id, {
                "role": "orchestrator",
                "message": f"📋 Orchestrator delivered task to {agent.upper()}.",
                "timestamp": contract["received_at"]
            })
            
        except ValueError as e:
            # Log error to memory
            log_to_memory(project_id, {
                "orchestrator_warnings": [{
                    "type": "agent_contract_failed",
                    "loop_id": loop_id,
                    "agent": agent,
                    "error": str(e),
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                }]
            })
            
            # Log to chat
            log_to_chat(project_id, {
                "role": "orchestrator",
                "message": f"⚠️ Failed to create contract for {agent.upper()}: {str(e)}",
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            })
    
    return agent_contracts

def check_agent_execution_readiness(project_id: str, loop_id: int, agent: str) -> tuple:
    """
    Checks if an agent is ready for execution by verifying:
    1. It has a confirmed contract
    2. All required tools are available
    3. The contract has a valid timestamp and trace_id
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        agent (str): The agent identifier
        
    Returns:
        tuple: (is_ready, reason)
    """
    # In a real implementation, this would retrieve the contract from memory
    # For now, we'll just print a message and return a mock result
    print(f"Checking execution readiness for agent {agent} in loop {loop_id}")
    
    # Mock implementation - in a real system, this would check actual contracts in memory
    contract_exists = True
    contract_confirmed = True
    tools_available = True
    valid_timestamp = True
    
    if not contract_exists:
        return False, "Agent contract not found"
    
    if not contract_confirmed:
        return False, "Agent contract not confirmed"
    
    if not tools_available:
        return False, "Required tools not available"
    
    if not valid_timestamp:
        return False, "Invalid contract timestamp"
    
    return True, "All conditions met"

def log_to_memory(project_id: str, data: dict):
    """
    Logs data to project memory.
    
    Args:
        project_id (str): The project ID
        data (dict): The data to log
    """
    # In a real implementation, this would store data in a database or file
    print(f"Logging to memory for project {project_id}:")
    print(json.dumps(data, indent=2))

def log_to_chat(project_id: str, message: dict):
    """
    Logs a message to the chat.
    
    Args:
        project_id (str): The project ID
        message (dict): The message to log
    """
    # In a real implementation, this would add the message to the chat
    print(f"Logging to chat for project {project_id}:")
    print(json.dumps(message, indent=2))

if __name__ == "__main__":
    # Example usage
    example_plan = {
        "loop_id": 31,
        "agents": ["hal", "nova", "critic"],
        "goals": ["Add form logic to ContactForm.jsx", "Implement validation"],
        "planned_files": ["ContactForm.jsx", "validation.js"],
        "tool_requirements": ["form_validator", "component_builder"],
        "confirmed": True,
        "confirmed_by": "operator",
        "confirmed_at": "2025-04-23T20:18:00Z"
    }
    
    project_id = "lifetree_001"
    
    # Generate a contract for a single agent
    nova_contract = generate_agent_contract("nova", example_plan)
    print("\nGenerated contract for NOVA:")
    print(json.dumps(nova_contract, indent=2))
    
    # Inject contracts to all agents
    print("\nInjecting contracts to all agents:")
    agent_contracts = inject_agent_contract(project_id, example_plan)
    
    # Check execution readiness
    print("\nChecking execution readiness:")
    is_ready, reason = check_agent_execution_readiness(project_id, example_plan["loop_id"], "nova")
    print(f"NOVA ready for execution: {is_ready} - {reason}")
