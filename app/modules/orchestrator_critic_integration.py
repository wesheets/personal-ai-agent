"""
Orchestrator Integration for CRITIC Rejection

This module extends the orchestrator with CRITIC rejection handling,
enabling the system to block auto-delegation when loop rejections exist.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import memory operations
try:
    from app.modules.memory_writer import read_memory
except ImportError:
    logging.warning("⚠️ Could not import memory operations, using mock implementations")
    # Mock implementation for testing
    async def read_memory(project_id, tag):
        return None

# Configure logging
logger = logging.getLogger("app.modules.orchestrator_critic_integration")

async def check_for_rejections(loop_id: str) -> Dict[str, Any]:
    """
    Check if there are any CRITIC rejections for a loop.
    
    Args:
        loop_id: Unique identifier for the loop
        
    Returns:
        Dictionary containing rejection information if found, None otherwise
    """
    try:
        # Read from memory
        memory_tag = f"loop_rejection_{loop_id}"
        rejection = await read_memory(loop_id, memory_tag)
        
        if not rejection:
            logger.info(f"✅ No rejections found for loop {loop_id}")
            return None
        
        logger.warning(f"⚠️ Rejection found for loop {loop_id}: {rejection.get('reason', 'Unknown reason')}")
        return rejection
    
    except Exception as e:
        logger.error(f"❌ Error checking for rejections: {str(e)}")
        return None

async def handle_rejection(loop_id: str, rejection: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a CRITIC rejection by generating an appropriate response.
    
    Args:
        loop_id: Unique identifier for the loop
        rejection: The rejection information
        
    Returns:
        Dictionary containing the response to the rejection
    """
    try:
        agent = rejection.get("agent", "unknown")
        reason = rejection.get("reason", "Unknown reason")
        recommendation = rejection.get("recommendation", "Retry the operation")
        
        response = {
            "status": "blocked",
            "message": f"Loop {loop_id} blocked due to CRITIC rejection",
            "details": {
                "agent": agent,
                "reason": reason,
                "recommendation": recommendation,
                "timestamp": rejection.get("timestamp", datetime.utcnow().isoformat())
            },
            "next_steps": [
                {
                    "action": "review_rejection",
                    "description": "Review the rejection details"
                },
                {
                    "action": "follow_recommendation",
                    "description": recommendation
                },
                {
                    "action": "clear_rejection",
                    "description": "Clear the rejection and retry"
                }
            ]
        }
        
        logger.info(f"✅ Generated rejection response for loop {loop_id}")
        return response
    
    except Exception as e:
        logger.error(f"❌ Error handling rejection: {str(e)}")
        return {
            "status": "error",
            "message": f"Error handling rejection: {str(e)}",
            "details": {
                "loop_id": loop_id
            }
        }

async def clear_rejection(loop_id: str) -> bool:
    """
    Clear a CRITIC rejection from memory.
    
    Args:
        loop_id: Unique identifier for the loop
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        # Import write_memory here to avoid circular imports
        from app.api.modules.memory import write_memory
        
        # Write empty value to effectively delete
        memory_tag = f"loop_rejection_{loop_id}"
        result = await write_memory(loop_id, memory_tag, None)
        
        # Log the operation
        if result and result.get("status") == "success":
            logger.info(f"✅ Rejection cleared for loop {loop_id}")
            return True
        else:
            logger.error(f"❌ Failed to clear rejection for loop {loop_id}: {result}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error clearing rejection: {str(e)}")
        return False
