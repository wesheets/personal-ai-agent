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
        task_id: Unique identifier for this task
        description: The description of the task
    """
    task_id: str = Field(..., description="Unique identifier for this task")
    description: str = Field(..., description="Description of the task")

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

# New models for user goal-based plan generation

class UserGoalPlanTask(BaseModel):
    """
    A single task in a user goal-based plan.
    
    Attributes:
        task_id: Unique identifier for this task
        description: The description of the task
    """
    task_id: str = Field(..., description="Unique identifier for this task")
    description: str = Field(..., description="Description of the task")

class UserGoalPlanRequest(BaseModel):
    """
    Request model for generating a plan from a user goal.
    
    Attributes:
        user_id: ID of the user requesting the plan
        goal: The user's goal or objective
        project_id: ID of the project context
        goal_id: Optional ID for the goal
    """
    user_id: str = Field(..., description="ID of the user requesting the plan")
    goal: str = Field(..., description="The user's goal or objective")
    project_id: str = Field(..., description="ID of the project context")
    goal_id: Optional[str] = Field(None, description="Optional ID for the goal")

class UserGoalPlanResponse(BaseModel):
    """
    Response model for a generated user goal-based plan.
    
    Attributes:
        status: Status of the plan generation (ok, error)
        plan: List of tasks in the plan
    """
    status: str = Field(..., description="Status of the plan generation (ok, error)")
    plan: List[UserGoalPlanTask] = Field(..., description="List of tasks in the plan")
