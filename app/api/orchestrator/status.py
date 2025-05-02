"""
Orchestrator Status Module

This module provides functionality to check the status of orchestrator projects.
It returns project orchestration state, memory activity, and recent summary using memory thread data.
"""

import re
import logging
import traceback
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Query

# Import THREAD_DB from memory_thread module
from app.modules.memory_thread import THREAD_DB
from app.modules.memory_summarize import summarize_memory_thread
from app.schemas.memory import SummarizationRequest

# Configure logging
logger = logging.getLogger("api.orchestrator.status")

# Create router for orchestrator status endpoint
router = APIRouter()

def extract_score(text: str) -> Optional[int]:
    """
    Extract a score from text using regex patterns like 7/10 or Score: 8/10.
    
    Args:
        text: Text content to extract score from
        
    Returns:
        Optional[int]: Extracted score (1-10) or None if no score found
    """
    if not text:
        return None
        
    # Try to match patterns like "7/10" or "Score: 8/10"
    match = re.search(r"(\d{1,2})\/10", text)
    
    if match:
        score = int(match.group(1))
        # Validate score is in range 1-10
        if 1 <= score <= 10:
            return score
    
    return None

@router.get("/api/orchestrator/status")
async def get_orchestrator_status(
    project_id: str = Query(..., description="Project identifier"),
    chain_id: str = Query(..., description="Chain identifier")
) -> Dict[str, Any]:
    """
    Get the status of an orchestrator project.
    
    Args:
        project_id: Project identifier
        chain_id: Chain identifier
        
    Returns:
        Dict[str, Any]: Project orchestration state, memory activity, and recent summary
    """
    logger.info(f"GET /api/orchestrator/status called with project_id={project_id}, chain_id={chain_id}")
    
    try:
        # Get the memory thread
        thread_key = f"{project_id}::{chain_id}"
        thread_key_alt = f"{project_id}:{chain_id}"
        
        # Check if thread exists with either key format
        if thread_key in THREAD_DB:
            thread = THREAD_DB[thread_key]
        elif thread_key_alt in THREAD_DB:
            thread = THREAD_DB[thread_key_alt]
        else:
            # Return empty status if no thread found
            logger.warning(f"No memory thread found for project_id={project_id}, chain_id={chain_id}")
            return {
                "project_id": project_id,
                "chain_id": chain_id,
                "memory_count": 0,
                "agents_logged": [],
                "last_agent": None,
                "last_step_type": None,
                "last_summary": "No memory thread found for this project and chain.",
                "critic_score": None
            }
        
        # Extract fields from memory
        memory_count = len(thread)
        
        # Get ordered list of agents from each memory
        agents_logged = []
        for memory in thread:
            agent = memory.get("agent", "").lower()
            if agent and agent not in agents_logged:
                agents_logged.append(agent)
        
        # Get last memory
        last_memory = thread[-1] if thread else {}
        last_agent = last_memory.get("agent") if last_memory else None
        
        # Get last step type
        last_step_type = last_memory.get("step_type") if last_memory else None
        # Convert enum to string if needed
        if hasattr(last_step_type, "value"):
            last_step_type = last_step_type.value
        
        # Call summarizer module
        summary_request = SummarizationRequest(
            project_id=project_id,
            chain_id=chain_id,
            agent_id="orchestrator"
        )
        
        try:
            summary_result = await summarize_memory_thread(summary_request)
            last_summary = summary_result.get("summary", "Unable to generate summary.")
        except Exception as e:
            logger.error(f"Error calling summarize_memory_thread: {str(e)}")
            last_summary = "Unable to generate summary due to an error."
        
        # Extract CRITIC score
        critic_memories = [m for m in thread if m.get("agent", "").lower() == "critic"]
        critic_score = None
        
        if critic_memories:
            latest_critic_memory = critic_memories[-1]
            critic_content = latest_critic_memory.get("content", "")
            critic_score = extract_score(critic_content)
        
        # Return the status
        result = {
            "project_id": project_id,
            "chain_id": chain_id,
            "memory_count": memory_count,
            "agents_logged": agents_logged,
            "last_agent": last_agent,
            "last_step_type": last_step_type,
            "last_summary": last_summary,
            "critic_score": critic_score
        }
        
        logger.info(f"Orchestrator status generated for project_id={project_id}, chain_id={chain_id}")
        return result
    
    except Exception as e:
        # Log unexpected errors
        error_msg = f"Unexpected error in get_orchestrator_status: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)
