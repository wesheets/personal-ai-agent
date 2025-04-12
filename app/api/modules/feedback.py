"""
Feedback Module for Agent Self-Reflection

This module provides endpoints for agents to log audit-based reflections as new memory entries,
enabling self-improvement through reflection on past performance.

The module allows agents to:
- Write feedback based on audit results
- Generate reflection summaries
- Store reflections as persistent memories

This closes the cognition loop by letting agents self-reflect on audit results and
write feedback memories to improve their planning, confidence, and strategic choices.
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime
import re

# Import the memory writer function to store reflections
from app.api.modules.memory import write_memory

# Configure logging
logger = logging.getLogger("api.modules.feedback")

# Create router
router = APIRouter()

class FeedbackRequest(BaseModel):
    agent_id: str
    task_id: str
    status: str
    planned_content: str
    result_content: str
    confidence_delta: Optional[float] = None

@router.post("/write")
async def write_feedback(request: Request):
    """
    Write feedback based on audit results.
    
    This endpoint receives audit result payloads and generates a memory summary
    that is stored as a persistent memory entry. This enables agents to self-reflect
    on their performance and improve future planning and execution.
    
    Request body:
    - agent_id: ID of the agent
    - task_id: ID of the task
    - status: Status of the task (success, failure, unattempted)
    - planned_content: The original task plan
    - result_content: The actual task result
    - confidence_delta: (Optional) Change in confidence after task execution
    
    Returns:
    - status: "ok" if successful
    - memory_id: ID of the created memory
    """
    try:
        # Parse request body
        body = await request.json()
        feedback_request = FeedbackRequest(**body)
        
        # Log the request
        logger.info(f"📝 [FEEDBACK] Received feedback request for agent {feedback_request.agent_id}, task {feedback_request.task_id}")
        print(f"📝 [FEEDBACK] Received feedback request for agent {feedback_request.agent_id}, task {feedback_request.task_id}")
        
        # Generate reflection content based on audit data
        reflection_content = generate_reflection_summary(
            feedback_request.status,
            feedback_request.planned_content,
            feedback_request.result_content,
            feedback_request.task_id,
            feedback_request.confidence_delta
        )
        
        # Determine reflection topics based on status
        reflect_on = []
        if feedback_request.status == "success":
            reflect_on = ["strategy", "execution"]
        elif feedback_request.status == "failure":
            reflect_on = ["error_analysis", "improvement"]
        else:  # unattempted
            reflect_on = ["prioritization", "planning"]
        
        # Create metadata
        metadata = {
            "task_id": feedback_request.task_id,
            "audit_status": feedback_request.status,
            "reflect_on": reflect_on
        }
        
        # Add confidence_delta to metadata if provided
        if feedback_request.confidence_delta is not None:
            metadata["confidence_delta"] = feedback_request.confidence_delta
            
        # Add confidence_delta to tags if provided
        tags = ["feedback", feedback_request.status, "reflection"]
        if feedback_request.confidence_delta is not None:
            confidence_tag = "confidence_up" if feedback_request.confidence_delta > 0 else "confidence_down"
            tags.append(confidence_tag)
        
        # Write to memory system
        memory = write_memory(
            agent_id=feedback_request.agent_id,
            type="feedback_summary",
            content=reflection_content,
            tags=tags,
            project_id="agent-feedback",
            status="success",
            task_id=feedback_request.task_id,
            metadata=metadata
        )
        
        # Log success
        logger.info(f"✅ [FEEDBACK] Created feedback memory: {memory['memory_id']}")
        print(f"✅ [FEEDBACK] Created feedback memory: {memory['memory_id']}")
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "memory_id": memory["memory_id"]
            }
        )
    except Exception as e:
        # Log error
        logger.error(f"❌ [FEEDBACK] Error creating feedback: {str(e)}")
        print(f"❌ [FEEDBACK] Error creating feedback: {str(e)}")
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error creating feedback: {str(e)}"
            }
        )

@router.get("/write")
async def auto_write_feedback_from_audit(
    agent_id: str,
    task_id: str,
    auto_write: bool = Query(True, description="Whether to automatically write feedback based on audit results")
):
    """
    Auto-trigger feedback writing from audit results.
    
    This endpoint allows the /audit endpoint to automatically trigger feedback writing
    by redirecting to this endpoint with the appropriate parameters.
    
    Query parameters:
    - agent_id: ID of the agent
    - task_id: ID of the task
    - auto_write: Whether to automatically write feedback (defaults to True)
    
    Returns:
    - status: "ok" if successful
    - message: Description of the action taken
    """
    if not auto_write:
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "message": "Auto-write is disabled, no feedback created"
            }
        )
    
    try:
        # This would normally fetch audit results from the database
        # For now, we'll just return a placeholder response
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "message": f"Auto-write feedback triggered for agent {agent_id}, task {task_id}",
                "note": "This is a placeholder for the auto-write feature"
            }
        )
    except Exception as e:
        logger.error(f"❌ [FEEDBACK] Error in auto-write: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error in auto-write: {str(e)}"
            }
        )

def generate_reflection_summary(status: str, planned_content: str, result_content: str, task_id: str, confidence_delta: Optional[float] = None) -> str:
    """
    Generate a reflection summary based on the audit data.
    
    Args:
        status: Status of the task (success, failure, unattempted)
        planned_content: The original task plan
        result_content: The actual task result
        task_id: ID of the task
        confidence_delta: Optional change in confidence after task execution
        
    Returns:
        A reflection summary string
    """
    # Generate different summaries based on status
    if status == "success":
        summary = f"Task {task_id} was completed successfully. Plan matched result."
        
        # Add more detailed analysis if content is available
        if planned_content and result_content:
            # Compress long content using NLP-like summary
            if len(planned_content) > 500 or len(result_content) > 500:
                planned_summary = compress_content(planned_content)
                result_summary = compress_content(result_content)
                summary += f"\n\nPlanned approach: {planned_summary}"
                summary += f"\n\nExecution result: {result_summary}"
            else:
                summary += f"\n\nThe execution followed the planned approach, achieving the intended outcome."
            
            summary += f"\n\nKey success factors included proper task planning and effective execution strategy."
    
    elif status == "failure":
        summary = f"Task {task_id} encountered issues during execution. Plan and result did not align."
        
        # Add more detailed analysis if content is available
        if planned_content and result_content:
            # Compress long content using NLP-like summary
            if len(planned_content) > 500 or len(result_content) > 500:
                planned_summary = compress_content(planned_content)
                result_summary = compress_content(result_content)
                summary += f"\n\nPlanned approach: {planned_summary}"
                summary += f"\n\nActual outcome: {result_summary}"
            else:
                summary += f"\n\nThe execution deviated from the planned approach, resulting in suboptimal outcomes."
            
            summary += f"\n\nAreas for improvement include better error handling and more robust planning."
    
    else:  # unattempted
        summary = f"Task {task_id} was planned but not attempted. No execution result available."
        
        # Add more detailed analysis if content is available
        if planned_content:
            # Compress long content using NLP-like summary
            if len(planned_content) > 500:
                planned_summary = compress_content(planned_content)
                summary += f"\n\nPlanned approach: {planned_summary}"
            else:
                summary += f"\n\nThe task was properly planned but not prioritized for execution."
            
            summary += f"\n\nFuture improvements should focus on task prioritization and resource allocation."
    
    # Add confidence delta information if provided
    if confidence_delta is not None:
        if confidence_delta > 0:
            summary += f"\n\nAgent confidence increased by {confidence_delta:.2f} after this task."
        elif confidence_delta < 0:
            summary += f"\n\nAgent confidence decreased by {abs(confidence_delta):.2f} after this task."
        else:
            summary += f"\n\nAgent confidence remained unchanged after this task."
    
    # Add timestamp for reference
    timestamp = datetime.utcnow().isoformat()
    summary += f"\n\nReflection generated at: {timestamp}"
    
    return summary

def compress_content(content: str, max_length: int = 200) -> str:
    """
    Compress long content to a shorter summary.
    This is a simple implementation that could be replaced with a more sophisticated NLP approach.
    
    Args:
        content: The content to compress
        max_length: Maximum length of the compressed content
        
    Returns:
        A compressed summary of the content
    """
    # If content is already short enough, return it as is
    if len(content) <= max_length:
        return content
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    # If only one sentence, truncate it
    if len(sentences) <= 1:
        return content[:max_length-3] + "..."
    
    # Take the first sentence and the last sentence
    first_sentence = sentences[0]
    last_sentence = sentences[-1]
    
    # If first and last sentences are too long together, truncate them
    if len(first_sentence) + len(last_sentence) + 5 > max_length:
        available_length = max_length - 5  # Account for "..." and " ... "
        first_part = first_sentence[:available_length//2]
        last_part = last_sentence[-available_length//2:]
        return f"{first_part}... ... {last_part}"
    
    # Otherwise, return first and last sentences
    return f"{first_sentence} ... {last_sentence}"
