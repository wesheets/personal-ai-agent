"""
Loop Sanity Validator Schema Definitions

This module defines the schemas for Loop Sanity Validator requests and responses.
The Loop Sanity Validator is responsible for validating loop configurations before execution,
ensuring structural integrity and preventing invalid loop plans.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class LoopValidationRequest(BaseModel):
    """
    Schema for Loop Sanity Validator request.
    """
    project_id: str = Field(
        ..., 
        description="Unique identifier for the project"
    )
    loop_id: str = Field(
        ..., 
        description="Unique identifier for the loop to validate"
    )
    planned_agents: List[str] = Field(
        ..., 
        description="List of agent identifiers planned for the loop execution"
    )
    expected_schema: Dict[str, Any] = Field(
        ..., 
        description="Expected schema structure for loop inputs and outputs"
    )
    max_loops: int = Field(
        ..., 
        description="Maximum number of loop iterations allowed",
        ge=1
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional context information for validation"
    )
    
    @validator('planned_agents')
    def validate_planned_agents(cls, v):
        if not v:
            raise ValueError("At least one agent must be planned for the loop")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_123",
                "loop_id": "loop_456",
                "planned_agents": ["ORCHESTRATOR", "CRITIC", "SAGE", "NOVA"],
                "expected_schema": {
                    "input": {
                        "query": "string",
                        "parameters": "object"
                    },
                    "output": {
                        "result": "string",
                        "status": "string",
                        "metadata": "object"
                    }
                },
                "max_loops": 5,
                "context": {
                    "priority": "high",
                    "timeout_seconds": 300
                }
            }
        }


class ValidationIssue(BaseModel):
    """
    Schema for validation issue details.
    """
    issue_type: str = Field(
        ..., 
        description="Type of validation issue (agent, schema, loops, structural)"
    )
    severity: str = Field(
        ..., 
        description="Severity of the issue (warning, error, critical)"
    )
    description: str = Field(
        ..., 
        description="Detailed description of the issue"
    )
    affected_component: str = Field(
        ..., 
        description="Component affected by the issue"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "issue_type": "agent",
                "severity": "error",
                "description": "Agent 'UNKNOWN_AGENT' is not registered in the system",
                "affected_component": "planned_agents"
            }
        }


class ValidationRecommendation(BaseModel):
    """
    Schema for validation recommendation details.
    """
    recommendation_type: str = Field(
        ..., 
        description="Type of recommendation (agent, schema, loops, structural)"
    )
    description: str = Field(
        ..., 
        description="Detailed description of the recommendation"
    )
    priority: int = Field(
        ..., 
        description="Priority of the recommendation (1-5, with 5 being highest)",
        ge=1,
        le=5
    )
    
    class Config:
        schema_extra = {
            "example": {
                "recommendation_type": "agent",
                "description": "Replace 'UNKNOWN_AGENT' with 'CRITIC' for proper validation",
                "priority": 4
            }
        }


class LoopValidationResult(BaseModel):
    """
    Schema for Loop Sanity Validator result.
    """
    valid: bool = Field(
        ..., 
        description="Whether the loop configuration is valid"
    )
    project_id: str = Field(
        ..., 
        description="Project identifier"
    )
    loop_id: str = Field(
        ..., 
        description="Loop identifier"
    )
    issues: List[ValidationIssue] = Field(
        default=[],
        description="List of validation issues found"
    )
    recommendations: List[ValidationRecommendation] = Field(
        default=[],
        description="List of recommendations to fix issues"
    )
    validation_score: float = Field(
        ..., 
        description="Overall validation score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the validation"
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the validation engine"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "valid": True,
                "project_id": "proj_123",
                "loop_id": "loop_456",
                "issues": [],
                "recommendations": [
                    {
                        "recommendation_type": "loops",
                        "description": "Consider reducing max_loops from 5 to 3 for better performance",
                        "priority": 2
                    }
                ],
                "validation_score": 0.95,
                "timestamp": "2025-04-24T19:44:16Z",
                "version": "1.0.0"
            }
        }


# Fallback schema for handling errors
class LoopValidationError(BaseModel):
    """
    Schema for Loop Sanity Validator error result.
    """
    status: str = Field(
        "error", 
        description="Status of the operation"
    )
    message: str = Field(
        ..., 
        description="Error message"
    )
    project_id: Optional[str] = Field(
        None, 
        description="Project identifier if applicable"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Loop identifier if applicable"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the validation engine"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "Failed to validate loop: invalid schema format",
                "project_id": "proj_123",
                "loop_id": "loop_456",
                "timestamp": "2025-04-24T19:44:16Z",
                "version": "1.0.0"
            }
        }
