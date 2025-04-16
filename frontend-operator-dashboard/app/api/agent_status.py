from fastapi import APIRouter
from app.core.run import AGENT_HANDLERS, run_agent
import logging
from typing import Dict, Any

logger = logging.getLogger("api")

router = APIRouter()

@router.get("/agent/status")
async def check_agent_status():
    """
    Check the operational status of all registered agents.
    
    Returns:
        dict: A dictionary with agent IDs as keys and status information as values.
              Status can be "alive", "error", or "not implemented".
    """
    results = {}
    
    for agent_id, handler in AGENT_HANDLERS.items():
        try:
            logger.info(f"Checking status of agent: {agent_id}")
            
            # Send a simple ping message to test the agent
            response = run_agent(agent_id, "ping")
            
            # Check if the response is valid
            if response and isinstance(response, str):
                results[agent_id] = {
                    "status": "alive",
                    "response": response[:100] + "..." if len(response) > 100 else response
                }
            else:
                results[agent_id] = {
                    "status": "error",
                    "message": "Agent returned invalid response"
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to ping agent {agent_id}: {str(e)}")
            results[agent_id] = {
                "status": "error",
                "message": str(e)
            }
    
    return {
        "agents": results,
        "total": len(results),
        "alive": sum(1 for agent in results.values() if agent["status"] == "alive"),
        "error": sum(1 for agent in results.values() if agent["status"] == "error")
    }
