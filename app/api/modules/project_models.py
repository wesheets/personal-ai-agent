"""
Project management models for the Promethios system.

This module defines the Pydantic models used for request and response
validation in the Project Management API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ProjectInitiateRequest(BaseModel):
    """
    Request model for initiating a new project.
    
    Attributes:
        user_id: ID of the user initiating the project
        project_name: Name of the project
        goal: Main goal or objective of the project
        agent_id: ID of the agent assigned to the project
    """
    user_id: str = Field(..., description="ID of the user initiating the project")
    project_name: str = Field(..., description="Name of the project")
    goal: str = Field(..., description="Main goal or objective of the project")
    agent_id: str = Field(..., description="ID of the agent assigned to the project")

class ProjectInitiateResponse(BaseModel):
    """
    Response model for a newly initiated project.
    
    Attributes:
        status: Status of the project initiation (ok, error)
        project_id: Unique identifier for the project
        goal_id: Unique identifier for the project goal
        agent_id: ID of the agent assigned to the project
    """
    status: str = Field(..., description="Status of the project initiation (ok, error)")
    project_id: str = Field(..., description="Unique identifier for the project")
    goal_id: str = Field(..., description="Unique identifier for the project goal")
    agent_id: str = Field(..., description="ID of the agent assigned to the project")
