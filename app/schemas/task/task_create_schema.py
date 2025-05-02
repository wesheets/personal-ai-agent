"""
Task Create Schema Module

This module defines the schema for task creation operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class TaskCreateRequest(BaseModel):
    """
    Schema for task creation request.
    """
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(None, description="Description of the task")
    priority: Optional[str] = Field("medium", description="Priority level of the task")
    assigned_to: Optional[str] = Field(None, description="Agent or user assigned to the task")
    tags: List[str] = Field(default=[], description="Tags associated with the task")
    due_date: Optional[str] = Field(None, description="Due date for the task")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# memory_tag: stubbed_phase2.5
class TaskCreateResponse(BaseModel):
    """
    Schema for task creation response.
    """
    task_id: str = Field(..., description="Unique identifier for the created task")
    project_id: str = Field(..., description="ID of the project containing this task")
    title: str = Field(..., description="Title of the task")
    status: str = Field(..., description="Status of the operation")
    created_at: str = Field(..., description="Timestamp when the task was created")
    assigned_to: Optional[str] = Field(None, description="Agent or user assigned to the task")
