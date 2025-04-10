"""
Data models for the Plan Generator module.

This module defines the Pydantic models used for request and response
validation in the Plan Generator API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class TaskPlan(BaseModel):
    """
    A single task in a generated plan.
    
    Attributes:
        day: The day or sequence number for this task
        title: The title or description of the task
        type: The type or category of the task
    """
    day: int = Field(..., description="Day or sequence number for this task")
    title: str = Field(..., description="Title or description of the task")
    type: str = Field(..., description="Type or category of the task")

class PlanGenerateRequest(BaseModel):
    """
    Request model for generating a task plan.
    
    Attributes:
        agent_id: ID of the agent to generate the plan for
        project_id: ID of the project context
        memory_trace_id: ID for memory tracing
        persona: Persona or role to use for plan generation
        objective: Main objective or goal of the plan
        input_data: Additional parameters for customization
        task_id: Optional task ID for the generated plan
    """
    agent_id: str = Field(..., description="ID of the agent to generate the plan for")
    project_id: str = Field(..., description="ID of the project context")
    memory_trace_id: Optional[str] = Field(None, description="ID for memory tracing")
    persona: str = Field(..., description="Persona or role to use for plan generation")
    objective: str = Field(..., description="Main objective or goal of the plan")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for customization")
    task_id: Optional[str] = Field(None, description="Optional task ID for the generated plan")

class PlanGenerateResponse(BaseModel):
    """
    Response model for a generated task plan.
    
    Attributes:
        status: Status of the plan generation (success, error)
        log: Description of the plan generation process
        tasks: List of tasks with title, type, and day/sequence
        task_id: ID of the generated plan
        project_id: ID of the project context
        memory_trace_id: ID for memory tracing
    """
    status: str = Field(..., description="Status of the plan generation (success, error)")
    log: str = Field(..., description="Description of the plan generation process")
    tasks: List[TaskPlan] = Field(..., description="List of tasks with title, type, and day/sequence")
    task_id: str = Field(..., description="ID of the generated plan")
    project_id: str = Field(..., description="ID of the project context")
    memory_trace_id: str = Field(..., description="ID for memory tracing")
