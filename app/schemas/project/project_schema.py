"""
Project Schema Module

This module defines the schema for project operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class ProjectCreateRequest(BaseModel):
    """
    Schema for project creation request.
    """
    title: str = Field(..., description="Title of the project")
    description: Optional[str] = Field(None, description="Description of the project")
    owner_id: str = Field(..., description="ID of the project owner")
    tags: List[str] = Field(default=[], description="Tags associated with the project")
    due_date: Optional[str] = Field(None, description="Due date for the project")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# memory_tag: stubbed_phase2.5
class ProjectCreateResponse(BaseModel):
    """
    Schema for project creation response.
    """
    project_id: str = Field(..., description="Unique identifier for the created project")
    title: str = Field(..., description="Title of the project")
    status: str = Field(..., description="Status of the operation")
    created_at: str = Field(..., description="Timestamp when the project was created")
    owner_id: str = Field(..., description="ID of the project owner")

# memory_tag: stubbed_phase2.5
class ProjectGetResponse(BaseModel):
    """
    Schema for project get response.
    """
    project_id: str = Field(..., description="Unique identifier for the project")
    title: str = Field(..., description="Title of the project")
    description: Optional[str] = Field(None, description="Description of the project")
    owner_id: str = Field(..., description="ID of the project owner")
    status: str = Field(..., description="Current status of the project")
    created_at: str = Field(..., description="Timestamp when the project was created")
    updated_at: Optional[str] = Field(None, description="Timestamp when the project was last updated")
    tags: List[str] = Field(default=[], description="Tags associated with the project")
    due_date: Optional[str] = Field(None, description="Due date for the project")
    task_count: Optional[int] = Field(None, description="Number of tasks in the project")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
