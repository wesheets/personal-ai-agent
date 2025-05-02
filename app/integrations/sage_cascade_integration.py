"""
SAGE Cascade Integration Module

This module integrates SAGE into the orchestrator loop flow,
enabling it to operate in post-CRITIC cascade mode.
"""

import logging
import sys
import os
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("app.integrations.sage_cascade_integration")

# Import SAGE review function
try:
    from app.agents.sage import review_loop_summary
    sage_available = True
except ImportError:
    sage_available = False
    logger.warning("⚠️ SAGE agent not available, cascade mode will be disabled")

# Import memory functions if available
try:
    from app.modules.orchestrator_memory import read_memory
    memory_available = True
except ImportError:
    memory_available = False
    logger.warning("⚠️ Memory module not available, using mock implementation")
    
    # Mock implementation for testing
    async def read_memory(agent_id, memory_type, tag):
        logger.info(f"Mock memory read: {agent_id}, {memory_type}, {tag}")
        return {"status": "success", "value": "Mock memory value"}

async def process_critic_result(loop_id: str, critic_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process CRITIC result and trigger SAGE review if appropriate.
    
    This function is called after CRITIC completes its review.
    If CRITIC approves the loop, SAGE is invoked to analyze the summary.
    
    Args:
        loop_id: Unique identifier for the loop
        critic_result: Result from CRITIC review
        
    Returns:
        Dict containing the SAGE review result or status information
    """
    if not sage_available:
        logger.warning("SAGE agent not available, skipping cascade")
        return {
            "status": "skipped",
            "message": "SAGE agent not available",
            "loop_id": loop_id
        }
    
    try:
        logger.info(f"Processing CRITIC result for loop: {loop_id}")
        
        # Check if CRITIC approved the loop
        approved = critic_result.get("approved", False)
        
        if not approved:
            logger.info(f"CRITIC did not approve loop {loop_id}, skipping SAGE review")
            return {
                "status": "skipped",
                "message": "CRITIC did not approve loop",
                "loop_id": loop_id
            }
        
        # Get loop summary from memory
        summary_tag = f"loop_summary_{loop_id}"
        
        if memory_available:
            memory_result = await read_memory(
                agent_id="orchestrator",
                memory_type="loop",
                tag=summary_tag
            )
            
            if memory_result.get("status") != "success":
                logger.warning(f"Failed to read loop summary from memory: {memory_result}")
                summary_text = critic_result.get("summary_text", "No summary available")
            else:
                summary_text = memory_result.get("value", "No summary available")
        else:
            # Fallback to using summary from CRITIC result
            summary_text = critic_result.get("summary_text", "No summary available")
        
        logger.info(f"Invoking SAGE review for loop: {loop_id}")
        
        # Call SAGE review function
        sage_result = await review_loop_summary(loop_id, summary_text)
        
        logger.info(f"SAGE review completed for loop: {loop_id}")
        
        return {
            "status": "success",
            "sage_result": sage_result,
            "loop_id": loop_id
        }
    
    except Exception as e:
        logger.error(f"Error in SAGE cascade processing: {str(e)}")
        return {
            "status": "error",
            "message": f"Error in SAGE cascade processing: {str(e)}",
            "loop_id": loop_id
        }

async def should_invoke_sage(loop_id: str) -> bool:
    """
    Determine if SAGE should be invoked for a given loop.
    
    This function can be used to implement more complex logic
    for deciding when to invoke SAGE in the cascade.
    
    Args:
        loop_id: Unique identifier for the loop
        
    Returns:
        Boolean indicating whether SAGE should be invoked
    """
    # For now, always invoke SAGE in cascade mode
    # This could be extended with more complex logic in the future
    return True
