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

@router.post("/result")
async def log_task_result(request: Request):
    try:
        data = await request.json()
        agent_id = data["agent_id"]
        task_id = data["task_id"]
        outcome = data["outcome"]
        confidence_score = data["confidence_score"]
        output = data["output"]
        notes = data["notes"]

        memory = write_memory(
            agent_id=agent_id,
            type="task_result",
            content=output,
            project_id="agent-feedback",
            tags=["task_result", outcome, f"confidence_{confidence_score}"],
            status="success",
            task_id=task_id,
            extra_fields={
                "confidence_score": confidence_score,
                "notes": notes
            }
        )

        print(f"✅ [TASK RESULT] Logged memory: {memory['memory_id']}")
        return {"status": "logged", "memory_id": memory["memory_id"]}

    except Exception as e:
        print(f"❌ [TASK RESULT] Logging failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
