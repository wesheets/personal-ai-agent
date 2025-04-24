"""
Plan Generate Schema

This module defines the schemas for plan generation endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class PlanType(str, Enum):
    """Types of plans that can be generated."""
    TASK = "task"
    PROJECT = "project"
    SPRINT = "sprint"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CUSTOM = "custom"


class PlanFormat(str, Enum):
    """Output formats for generated plans."""
    STEPS = "steps"
    MARKDOWN = "markdown"
    JSON = "json"
    TREE = "tree"
    GANTT = "gantt"


class PlanGenerateRequest(BaseModel):
    """Request schema for plan generation."""
    goal: str = Field(..., description="Goal or objective for the plan")
    plan_type: PlanType = Field(
        PlanType.TASK, 
        description="Type of plan to generate"
    )
    format: PlanFormat = Field(
        PlanFormat.STEPS, 
        description="Output format for the plan"
    )
    context: Optional[str] = Field(
        None, 
        description="Additional context for plan generation"
    )
    constraints: Optional[List[str]] = Field(
        None, 
        description="List of constraints to consider"
    )
    max_steps: Optional[int] = Field(
        None, 
        description="Maximum number of steps in the plan"
    )
    agent_id: Optional[str] = Field(
        None, 
        description="Agent ID requesting the plan"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Loop ID associated with the plan"
    )
    
    @validator('goal')
    def goal_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('goal must not be empty')
        return v
    
    @validator('max_steps')
    def max_steps_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('max_steps must be positive')
        if v is not None and v > 100:
            return 100  # Cap at 100 for performance
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "goal": "Implement a new feature for the user dashboard",
                "plan_type": "task",
                "format": "steps",
                "context": "The dashboard currently shows basic metrics but needs to display user activity over time.",
                "constraints": ["Must be completed in 2 weeks", "Must use existing API endpoints"],
                "max_steps": 10,
                "agent_id": "ORCHESTRATOR",
                "loop_id": "loop_12345"
            }
        }


class PlanStep(BaseModel):
    """Schema for a plan step."""
    step_number: int = Field(..., description="Step number")
    description: str = Field(..., description="Step description")
    estimated_time: Optional[str] = Field(None, description="Estimated time to complete the step")
    dependencies: Optional[List[int]] = Field(None, description="List of step numbers this step depends on")
    
    class Config:
        schema_extra = {
            "example": {
                "step_number": 1,
                "description": "Analyze requirements and create specifications",
                "estimated_time": "2 hours",
                "dependencies": []
            }
        }


class PlanGenerateResponse(BaseModel):
    """Response schema for plan generation."""
    plan_id: str = Field(..., description="Unique identifier for the plan")
    goal: str = Field(..., description="Original goal or objective")
    plan_type: PlanType = Field(..., description="Type of plan generated")
    format: PlanFormat = Field(..., description="Output format of the plan")
    steps: Optional[List[PlanStep]] = Field(None, description="List of plan steps")
    content: Optional[str] = Field(None, description="Plan content in the requested format")
    total_steps: int = Field(..., description="Total number of steps in the plan")
    estimated_completion_time: Optional[str] = Field(None, description="Estimated time to complete the entire plan")
    agent_id: Optional[str] = Field(None, description="Agent ID that requested the plan")
    loop_id: Optional[str] = Field(None, description="Loop ID associated with the plan")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the plan generation"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "plan_id": "plan_12345",
                "goal": "Implement a new feature for the user dashboard",
                "plan_type": "task",
                "format": "steps",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Analyze requirements and create specifications",
                        "estimated_time": "2 hours",
                        "dependencies": []
                    },
                    {
                        "step_number": 2,
                        "description": "Design UI mockups for the new feature",
                        "estimated_time": "3 hours",
                        "dependencies": [1]
                    }
                ],
                "content": None,
                "total_steps": 2,
                "estimated_completion_time": "5 hours",
                "agent_id": "ORCHESTRATOR",
                "loop_id": "loop_12345",
                "timestamp": "2025-04-24T20:55:00Z",
                "version": "1.0.0"
            }
        }


class PlanGenerateError(BaseModel):
    """Error response schema for plan generation."""
    message: str = Field(..., description="Error message")
    goal: Optional[str] = Field(None, description="Original goal if available")
    plan_type: Optional[PlanType] = Field(None, description="Requested plan type if available")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Failed to generate plan: Goal is too vague",
                "goal": "Improve the system",
                "plan_type": "task",
                "timestamp": "2025-04-24T20:55:00Z",
                "version": "1.0.0"
            }
        }
