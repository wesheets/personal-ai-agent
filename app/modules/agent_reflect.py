"""
Agent Reflection Module

This module provides functionality for agents to reflect on the outcome of completed tasks
and store reflection memory entries. It allows agents to record their thoughts on task
execution, whether successful or failed, to improve future performance.

Endpoint: /api/modules/agent/reflect
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import memory-related functions
from app.modules.memory_writer import write_memory, generate_reflection

# Configure logging
logger = logging.getLogger("api.modules.agent_reflect")

# Define the router
router = APIRouter()

# Define the models
class ReflectRequest(BaseModel):
    """Request model for the reflect endpoint"""
    agent_id: str
    task_id: str
    task_summary: str
    outcome: str  # "success" or "failure"
    notes: str
    project_id: Optional[str] = None

class ReflectResponse(BaseModel):
    """Response model for the reflect endpoint"""
    status: str = "reflected"
    memory_id: str
    reflection: str

def generate_task_reflection(agent_id: str, task_summary: str, outcome: str, notes: str) -> str:
    """
    Generate a reflection for a completed task.
    
    Args:
        agent_id (str): The ID of the agent
        task_summary (str): Summary of the completed task
        outcome (str): Outcome of the task (success or failure)
        notes (str): Additional notes about the task execution
        
    Returns:
        str: Generated reflection text
    """
    # Extract agent name without "-agent" suffix if present
    agent_name = agent_id.replace("-agent", "").upper()
    
    # Generate reflection based on outcome
    if outcome.lower() == "success":
        reflection = f"{agent_name} successfully completed the task: {task_summary}. "
        
        # Add insights based on notes
        if "memory" in notes.lower():
            reflection += "The agent effectively utilized memory capabilities. "
        
        if "search" in notes.lower():
            reflection += "Search functionality was properly leveraged. "
            
        if "summarization" in notes.lower() or "summarize" in notes.lower():
            reflection += "Summarization skills were applied effectively. "
            
        # Add forward-looking statement
        reflection += "This suggests stronger confidence in similar tasks moving forward."
    else:
        reflection = f"{agent_name} encountered challenges with the task: {task_summary}. "
        
        # Add insights based on notes
        if "memory" in notes.lower():
            reflection += "Memory retrieval or storage may need improvement. "
            
        if "search" in notes.lower():
            reflection += "Search functionality could be enhanced. "
            
        if "summarization" in notes.lower() or "summarize" in notes.lower():
            reflection += "Summarization approach might need refinement. "
            
        # Add forward-looking statement
        reflection += "This suggests areas for improvement in future similar tasks."
    
    return reflection

def get_project_id_from_task(task_id: str) -> Optional[str]:
    """
    Attempt to fetch project_id from task context if not provided.
    This is a placeholder implementation that would be replaced with actual task lookup.
    
    Args:
        task_id (str): The task ID to look up
        
    Returns:
        Optional[str]: The project ID if found, None otherwise
    """
    # In a real implementation, this would query a task database or API
    # For now, we'll return None and let the caller handle it
    return None

@router.post("/reflect", response_model=ReflectResponse)
async def reflect(request: ReflectRequest):
    """
    Record a reflection on a completed task and store it as a memory entry.
    
    Args:
        request (ReflectRequest): The reflection request
        
    Returns:
        ReflectResponse: The reflection response with memory ID and generated reflection
        
    Raises:
        HTTPException: If required fields are missing or other errors occur
    """
    # Validate the request
    if not request.agent_id:
        raise HTTPException(status_code=422, detail="agent_id is required")
    
    if not request.task_id:
        raise HTTPException(status_code=422, detail="task_id is required")
    
    if not request.task_summary:
        raise HTTPException(status_code=422, detail="task_summary is required")
    
    if not request.outcome:
        raise HTTPException(status_code=422, detail="outcome is required")
    
    if request.outcome.lower() not in ["success", "failure"]:
        raise HTTPException(status_code=422, detail="outcome must be 'success' or 'failure'")
    
    # Get project_id if not provided
    project_id = request.project_id
    if not project_id:
        project_id = get_project_id_from_task(request.task_id)
    
    # Generate reflection text
    reflection = generate_task_reflection(
        agent_id=request.agent_id,
        task_summary=request.task_summary,
        outcome=request.outcome,
        notes=request.notes
    )
    
    # Generate tags
    tags = ["reflection", "task_outcome", "learning"]
    if request.outcome.lower() == "success":
        tags.append("success")
    else:
        tags.append("failure")
    
    # Write reflection to memory
    memory = write_memory(
        agent_id=request.agent_id,
        type="reflection",
        content=reflection,
        tags=tags,
        project_id=project_id,
        status=request.outcome,
        task_id=request.task_id
    )
    
    # Log successful reflection
    logger.info(f"✅ Reflection recorded for agent {request.agent_id} on task {request.task_id}")
    
    # Return the response
    return ReflectResponse(
        status="reflected",
        memory_id=memory["memory_id"],
        reflection=reflection
    )

# Add a print statement to confirm the route is defined
print("🧠 Route defined: /reflect -> reflect")
