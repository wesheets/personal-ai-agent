"""
Projects Schema Module

This module defines the schema for projects operations.
"""
from pydantic import BaseModel, Field, RootModel
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class ProjectsListRequest(BaseModel):
    """
    Schema for projects list request.
    """
    project_id: Optional[str] = Field(None, description="Filter by project ID")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    tags: Optional[str] = Field(None, description="Filter by tags (comma-separated)")

# memory_tag: stubbed_phase2.5
class ProjectItem(BaseModel):
    """
    Schema for a single project item.
    """
    project_id: str = Field(..., description="The project identifier")
    goal: str = Field(..., description="Main objective of the project")
    user_id: str = Field(..., description="Identifier of the user who owns the project")
    tags: List[str] = Field(default=[], description="List of tags for categorizing the project")
    context: Optional[str] = Field(None, description="Summary or notes about the project")
    created_at: str = Field(..., description="Timestamp of project creation")
    log_id: Optional[str] = Field(None, description="Unique identifier for the log entry")

# memory_tag: stubbed_phase2.5
class ProjectsListResponse(RootModel):
    """
    Schema for projects list response.
    """
    root: List[ProjectItem] = Field(..., description="List of projects")
