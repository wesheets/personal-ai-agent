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
    user_id: Optional[str] = None
    task_id: str
    result: str  # "success", "failure", or "partial"
    content: str
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    status: Optional[str] = None
    confidence_score: Optional[float] = None
    notes: Optional[str] = None
    memory_trace_id: Optional[str] = None
    
    @validator('result')
    def validate_result(cls, v):
        allowed_values = ["success", "failure", "partial"]
        if v.lower() not in allowed_values:
            raise ValueError(f"result must be one of: {', '.join(allowed_values)}")
        return v.lower()
    
    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError("confidence_score must be between 0 and 1")
        return v

class TaskResultResponse(BaseModel):
    """Response model for the task result endpoint"""
    status: str = "logged"
    memory_id: str

@router.post("/result")
async def log_task_result(request: Request):
    """
    Log the result of a previously planned task with success/failure status.
    
    This endpoint stores task results as memory entries with structured metadata,
    enabling future auditing against the original plan.
    
    The task result is stored with memory_type: task_result and includes metadata
    such as task_id, result, project_id, status, and goal_id if available.
    """
    try:
        data = await request.json()
        logger.info(f"🔄 Received task result for task_id: {data.get('task_id')}")
        
        # Create TaskResultRequest object for validation
        task_result = TaskResultRequest(**data)
        
        # Create tags list, including user_id as a scope if provided
        tags = ["task_result", task_result.result]
        
        # Add user scope tag if user_id is provided
        if task_result.user_id:
            user_scope = f"user:{task_result.user_id}"
            if user_scope not in tags:
                tags.append(user_scope)
        
        # Create metadata with structured information
        metadata = {
            "task_id": task_result.task_id,
            "result": task_result.result,
            "project_id": task_result.project_id
        }
        
        # Add optional fields to metadata if provided
        if task_result.goal_id:
            metadata["goal_id"] = task_result.goal_id
        
        if task_result.status:
            metadata["status"] = task_result.status
            
        if task_result.confidence_score is not None:
            metadata["confidence_score"] = task_result.confidence_score
            tags.append(f"confidence_{task_result.confidence_score}")
            
        if task_result.notes:
            metadata["notes"] = task_result.notes

        # Write memory with all provided parameters
        memory = write_memory(
            agent_id=task_result.agent_id,
            type="task_result",
            content=task_result.content,
            tags=tags,
            project_id=task_result.project_id,
            status=task_result.status,
            task_id=task_result.task_id,
            memory_trace_id=task_result.memory_trace_id,
            metadata=metadata
        )

        logger.info(f"✅ Task result logged: memory_id={memory['memory_id']}, task_id={task_result.task_id}")
        return {"status": "logged", "memory_id": memory["memory_id"]}

    except Exception as e:
        logger.error(f"❌ Task result logging failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
