"""
Task List Schema Module

This module defines the schema for task listing operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class TaskItem(BaseModel):
    """
    Schema for a single task item.
    """
    task_id: str = Field(..., description="Unique identifier for the task")
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(None, description="Description of the task")
    status: str = Field(..., description="Current status of the task")
    priority: Optional[str] = Field(None, description="Priority level of the task")
    created_at: str = Field(..., description="Timestamp when the task was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when the task was last updated")
    assigned_to: Optional[str] = Field(None, description="Agent or user assigned to the task")
    tags: List[str] = Field(default=[], description="Tags associated with the task")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# memory_tag: stubbed_phase2.5
class TaskListResponse(BaseModel):
    """
    Schema for task list response.
    """
    tasks: List[TaskItem] = Field(..., description="List of tasks")
    project_id: str = Field(..., description="ID of the project containing these tasks")
    total_count: int = Field(..., description="Total number of tasks")
    status: str = Field(..., description="Status of the operation")
