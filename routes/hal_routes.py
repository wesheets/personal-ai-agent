"""
HAL constraint simulation routes for testing ethics system.
feature/phase-3.5-hardening
SHA256: 7e9d4f5d7c6b8a9e2c1d4f5d7c6b8a9e2c1d4f5d7c6b8a9e2c1d4f5d7c6b8a9e
INTEGRITY: v3.5.0-hal-routes
LAST_MODIFIED: 2025-04-17

main
"""
from fastapi import APIRouter, Request
import logging
import json
import datetime
from typing import Dict, Any, List
from app.agents.memory_agent import handle_memory_task
from app.agents.hal_agent import SAFETY_CONSTRAINTS, log_constraint

# Configure logging
logger = logging.getLogger("api")

# Create router
router = APIRouter(tags=["HAL"])

@router.get("/simulate-block")
async def simulate_hal_constraint(
    constraint: str = "ethical_concern",
    agent: str = "ash-agent",
    task: str = "Perform unauthorized data access"
):
    """
    Simulates a HAL constraint block for testing the ethics system.
    
    This endpoint returns a mock blocked task and logs it to the MemoryAgent.
    It's intended for testing HAL's constraint behavior without triggering actual blocks.
    
    Parameters:
    - constraint: The constraint type to simulate (default: ethical_concern)
    - agent: The agent to simulate being blocked (default: ash-agent)
    - task: The task description to simulate being blocked (default: "Perform unauthorized data access")
    
    Returns:
    - A simulation result with the constraint details and memory log status
    """
    try:
        # Validate constraint type
        if constraint not in SAFETY_CONSTRAINTS:
            valid_constraints = ", ".join(SAFETY_CONSTRAINTS)
            return {
                "status": "error",
                "message": f"Invalid constraint type. Valid types are: {valid_constraints}",
                "simulation_status": "failed"
            }
        
        # Create a simulated constraint entry
        constraint_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "source": "HAL",
            "target": agent,
            "type": "constraint",
            "reason": constraint,
            "task": task,
            "simulation": True  # Mark this as a simulation
        }
        
        # Log to memory agent with structured format
        structured_log = f"STRUCTURED_LOG:{json.dumps(constraint_entry)}"
        memory_result = handle_memory_task(structured_log)
        
        # Also log in human-readable format
        readable_log = f"LOG: [SIMULATION] HAL blocked task to {agent} due to {constraint} protocol breach"
        handle_memory_task(readable_log)
        
        # Return the simulation result
        return {
            "status": "success",
            "simulation_status": "completed",
            "constraint": constraint,
            "agent": agent,
            "task": task,
            "block_message": f"I'm sorry, but I cannot complete this task due to {constraint}. This incident has been logged.",
            "memory_log": {
                "status": "logged",
                "result": memory_result
            },
            "timestamp": constraint_entry["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Error in HAL constraint simulation: {str(e)}")
        return {
            "status": "error",
            "message": f"Simulation failed: {str(e)}",
            "simulation_status": "failed"
        }

@router.get("/constraints")
async def list_constraints():
    """
    Returns the list of available safety constraints for the HAL system.
    
    This endpoint is useful for UI components that need to display available
    constraint types for simulation or monitoring.
    """
    return {
        "constraints": SAFETY_CONSTRAINTS,
        "count": len(SAFETY_CONSTRAINTS),
        "status": "success"
    }

from fastapi import APIRouter
router = APIRouter()
