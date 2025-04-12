"""
Task Result Module

This module provides functionality for agents to report the outcome, confidence, and reasoning
for completed tasks. This finishes the reflection loop and creates a structured result memory.

Endpoint: /api/modules/task/result
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field, validator

# Import memory-related functions from memory.py instead of memory_writer.py
# This ensures memories are stored in both SQLite database and in-memory store
from app.api.modules.memory import write_memory

# Configure logging
logger = logging.getLogger("api.modules.task_result")

# Create router
router = APIRouter()
print("🧠 Route defined: /api/modules/task/result -> task_result")

# Define the models
class TaskResultRequest(BaseModel):
    """Request model for the task result endpoint"""
    agent_id: str
    task_id: str
    outcome: str  # "success", "failure", or "partial"
    confidence_score: float
    output: str
    notes: Optional[str] = None
    project_id: Optional[str] = None
    memory_trace_id: Optional[str] = None
    
    @validator('outcome')
    def validate_outcome(cls, v):
        allowed_values = ["success", "failure", "partial"]
        if v.lower() not in allowed_values:
            raise ValueError(f"outcome must be one of: {', '.join(allowed_values)}")
        return v.lower()
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError("confidence_score must be between 0 and 1")
        return v

class TaskResultResponse(BaseModel):
    """Response model for the task result endpoint"""
    status: str = "logged"
    memory_id: str

@router.post("/result", response_model=TaskResultResponse)
async def task_result(request: Request):
    """
    Record the outcome, confidence, and reasoning for a completed task.
    
    Args:
        request (Request): The HTTP request containing task result data
        
    Returns:
        TaskResultResponse: The response with status and memory_id
        
    Raises:
        HTTPException: If required fields are missing or other errors occur
    """
    try:
        # Parse request body
        body = await request.json()
        task_result_request = TaskResultRequest(**body)
        
        # Generate tags based on outcome and confidence
        tags = ["task_result", f"outcome_{task_result_request.outcome}"]
        
        # Add confidence level tag
        if task_result_request.confidence_score >= 0.8:
            tags.append("high_confidence")
        elif task_result_request.confidence_score >= 0.5:
            tags.append("medium_confidence")
        else:
            tags.append("low_confidence")
            
        # Format content to include all relevant information
        content = f"Task Result: {task_result_request.output}\n\n"
        content += f"Confidence: {task_result_request.confidence_score:.2f}\n\n"
        
        if task_result_request.notes:
            content += f"Notes: {task_result_request.notes}"
        
        # Write result to memory
        memory = write_memory(
            agent_id=task_result_request.agent_id,
            type="task_result",
            content=content,
            tags=tags,
            project_id=task_result_request.project_id,
            status=task_result_request.outcome,
            task_id=task_result_request.task_id,
            memory_trace_id=task_result_request.memory_trace_id
        )
        
        # Log successful result recording
        logger.info(f"✅ Task result recorded for agent {task_result_request.agent_id} on task {task_result_request.task_id}")
        
        # Return the response
        return TaskResultResponse(
            status="logged",
            memory_id=memory["memory_id"]
        )
    except ValueError as e:
        # Handle validation errors
        logger.error(f"❌ Validation error in task result: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Handle other errors
        logger.error(f"❌ Error recording task result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error recording task result: {str(e)}")
