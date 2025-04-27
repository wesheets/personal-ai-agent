"""
CEO Agent Schema Definitions

This module defines the schemas for CEO agent requests and responses.
The CEO agent is responsible for strategic coordination, plan review,
and agent resource allocation.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CEOReviewRequest(BaseModel):
    """
    Schema for CEO agent review request.
    """
    project_id: str = Field(..., description="Unique identifier for the project")
    plan_id: Optional[str] = Field(None, description="Identifier for the plan to review")
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Context information for the review"
    )
    tools: Optional[List[str]] = Field(
        default=["review_plans", "reallocate_agents", "trigger_reorg"],
        description="List of tools to use for the review"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_123",
                "plan_id": "plan_456",
                "context": {
                    "priority": "high",
                    "deadline": "2025-05-01",
                    "resources_available": ["NOVA", "CRITIC", "OBSERVER"]
                },
                "tools": ["review_plans", "reallocate_agents"]
            }
        }


class AgentAllocation(BaseModel):
    """
    Schema for agent allocation details.
    """
    agent_id: str = Field(..., description="Identifier for the agent")
    role: str = Field(..., description="Role assigned to the agent")
    priority: int = Field(
        ..., 
        description="Priority level (1-10, with 10 being highest)",
        ge=1,
        le=10
    )
    estimated_duration: Optional[int] = Field(
        None, 
        description="Estimated duration in minutes"
    )
    dependencies: Optional[List[str]] = Field(
        default=[],
        description="List of agent IDs this agent depends on"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "NOVA",
                "role": "UI_DESIGNER",
                "priority": 8,
                "estimated_duration": 120,
                "dependencies": ["CRITIC"]
            }
        }


class CEOPlanResult(BaseModel):
    """
    Schema for CEO agent plan result.
    """
    status: str = Field(..., description="Status of the review (success, error)")
    project_id: str = Field(..., description="Project identifier")
    plan_id: Optional[str] = Field(None, description="Plan identifier")
    strategic_assessment: Optional[str] = Field(
        None, 
        description="Strategic assessment of the plan"
    )
    agent_allocations: Optional[List[AgentAllocation]] = Field(
        default=[],
        description="List of agent allocations"
    )
    recommendations: Optional[List[str]] = Field(
        default=[],
        description="List of recommendations"
    )
    reorganization_needed: Optional[bool] = Field(
        False,
        description="Whether reorganization is needed"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the review"
    )
    message: Optional[str] = Field(None, description="Error message if status is error")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "project_id": "proj_123",
                "plan_id": "plan_456",
                "strategic_assessment": "Plan is viable but requires additional resources for timely completion.",
                "agent_allocations": [
                    {
                        "agent_id": "NOVA",
                        "role": "UI_DESIGNER",
                        "priority": 8,
                        "estimated_duration": 120,
                        "dependencies": ["CRITIC"]
                    },
                    {
                        "agent_id": "CRITIC",
                        "role": "QUALITY_ASSURANCE",
                        "priority": 7,
                        "estimated_duration": 60,
                        "dependencies": []
                    }
                ],
                "recommendations": [
                    "Allocate additional resources to UI development",
                    "Consider parallel processing for backend tasks",
                    "Implement early feedback loops with CRITIC agent"
                ],
                "reorganization_needed": False,
                "timestamp": "2025-04-24T19:10:05Z"
            }
        }


# Fallback schema for handling errors
class CEOErrorResult(BaseModel):
    """
    Schema for CEO agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    project_id: Optional[str] = Field(None, description="Project identifier if applicable")
    plan_id: Optional[str] = Field(None, description="Plan identifier if applicable")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "Failed to review plan: insufficient data",
                "project_id": "proj_123",
                "plan_id": "plan_456",
                "timestamp": "2025-04-24T19:10:05Z"
            }
        }
