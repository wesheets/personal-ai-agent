"""
Delegate Schema Module

This module defines the schema for delegate operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class TaskData(BaseModel):
    """
    Schema for task data in delegation request.
    """
    goal_id: str = Field(..., description="The goal identifier")
    description: str = Field(..., description="The task description")
    task_category: str = Field(..., description="The task category")

# memory_tag: stubbed_phase2.5
class DelegateRequest(BaseModel):
    """
    Schema for delegate request.
    """
    agent_name: str = Field(..., description="The agent to delegate the task to")
    task: TaskData = Field(..., description="The task data")

# memory_tag: stubbed_phase2.5
class DelegateResponse(BaseModel):
    """
    Schema for delegate response.
    """
    status: str = Field(..., description="Status of the delegation operation")
    message: str = Field(..., description="Message describing the result of the operation")
    task_id: str = Field(..., description="The task identifier")
