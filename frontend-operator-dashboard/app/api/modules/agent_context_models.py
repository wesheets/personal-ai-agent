"""
Pydantic models for the agent context endpoint.

This module defines the request and response schemas for the /agent/context endpoint
which provides a structured snapshot of an agent's activities.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TaskItem(BaseModel):
    """Task item within a project context"""
    task: str
    status: str

class ProjectContext(BaseModel):
    """Project context containing metadata and tasks"""
    project_id: str
    last_action: str
    loop_count: int
    last_active: str  # ISO8601 timestamp
    tasks: List[TaskItem]

class AgentContextRequest(BaseModel):
    """
    Request model for the agent context endpoint
    
    This model defines the input schema for retrieving an agent's context
    """
    agent_id: str

class AgentContextResponse(BaseModel):
    """
    Response model for the agent context endpoint
    
    This model defines the output schema for an agent's context, including
    active projects, tasks, and agent state information
    """
    status: str
    agent_id: str
    active_projects: List[ProjectContext]
    agent_state: str
    last_active: str  # ISO8601 timestamp
