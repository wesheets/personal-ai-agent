"""
PESSIMIST Pre-Run Evaluation Schema Definitions

This module defines the schemas for PESSIMIST Pre-Run Evaluation requests and responses.
The PESSIMIST Pre-Run Evaluation is responsible for evaluating loop plans before execution,
identifying potential risks, and providing confidence scores.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class AgentMapping(BaseModel):
    """
    Schema for agent mapping details.
    """
    agent_id: str = Field(
        ..., 
        description="Identifier for the agent"
    )
    role: str = Field(
        ..., 
        description="Role assigned to the agent in the loop"
    )
    priority: Optional[int] = Field(
        None, 
        description="Priority level (1-10, with 10 being highest)",
        ge=1,
        le=10
    )
    dependencies: Optional[List[str]] = Field(
        default=[],
        description="List of agent IDs this agent depends on"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "CRITIC",
                "role": "QUALITY_ASSURANCE",
                "priority": 8,
                "dependencies": ["SAGE"]
            }
        }


class LoopComponent(BaseModel):
    """
    Schema for loop component details.
    """
    component_id: str = Field(
        ..., 
        description="Unique identifier for the component"
    )
    component_type: str = Field(
        ..., 
        description="Type of component (agent, module, service)"
    )
    description: str = Field(
        ..., 
        description="Description of the component"
    )
    risk_level: Optional[str] = Field(
        default="medium",
        description="Risk level associated with the component (low, medium, high)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "component_id": "memory_service",
                "component_type": "service",
                "description": "Long-term memory storage service",
                "risk_level": "medium"
            }
        }


class PessimistCheckRequest(BaseModel):
    """
    Schema for PESSIMIST Pre-Run Evaluation request.
    """
    project_id: str = Field(
        ..., 
        description="Unique identifier for the project"
    )
    loop_id: str = Field(
        ..., 
        description="Unique identifier for the loop to evaluate"
    )
    loop_plan: Dict[str, Any] = Field(
        ..., 
        description="Detailed plan for the loop execution"
    )
    component_list: List[LoopComponent] = Field(
        ..., 
        description="List of components involved in the loop"
    )
    agent_map: List[AgentMapping] = Field(
        ..., 
        description="Mapping of agents to roles in the loop"
    )
    context: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional context information for evaluation"
    )
    
    @validator('component_list')
    def validate_component_list(cls, v):
        if not v:
            raise ValueError("At least one component must be specified")
        return v
    
    @validator('agent_map')
    def validate_agent_map(cls, v):
        if not v:
            raise ValueError("At least one agent mapping must be specified")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_123",
                "loop_id": "loop_456",
                "loop_plan": {
                    "steps": [
                        {"step_id": 1, "agent": "ORCHESTRATOR", "action": "plan"},
                        {"step_id": 2, "agent": "SAGE", "action": "analyze"},
                        {"step_id": 3, "agent": "CRITIC", "action": "review"}
                    ],
                    "max_iterations": 3,
                    "timeout_seconds": 300
                },
                "component_list": [
                    {
                        "component_id": "memory_service",
                        "component_type": "service",
                        "description": "Long-term memory storage service",
                        "risk_level": "medium"
                    },
                    {
                        "component_id": "schema_validator",
                        "component_type": "module",
                        "description": "Schema validation module",
                        "risk_level": "low"
                    }
                ],
                "agent_map": [
                    {
                        "agent_id": "ORCHESTRATOR",
                        "role": "COORDINATOR",
                        "priority": 10,
                        "dependencies": []
                    },
                    {
                        "agent_id": "SAGE",
                        "role": "ANALYZER",
                        "priority": 7,
                        "dependencies": ["ORCHESTRATOR"]
                    },
                    {
                        "agent_id": "CRITIC",
                        "role": "QUALITY_ASSURANCE",
                        "priority": 8,
                        "dependencies": ["SAGE"]
                    }
                ],
                "context": {
                    "priority": "high",
                    "user_id": "user_789",
                    "previous_loop_success": True
                }
            }
        }


class Risk(BaseModel):
    """
    Schema for risk details.
    """
    risk_id: str = Field(
        ..., 
        description="Unique identifier for the risk"
    )
    risk_type: str = Field(
        ..., 
        description="Type of risk (agent, component, plan, structural)"
    )
    severity: str = Field(
        ..., 
        description="Severity of the risk (low, medium, high, critical)"
    )
    description: str = Field(
        ..., 
        description="Detailed description of the risk"
    )
    affected_elements: List[str] = Field(
        ..., 
        description="List of elements affected by the risk"
    )
    mitigation_suggestions: Optional[List[str]] = Field(
        default=[],
        description="List of suggested mitigations for the risk"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "risk_id": "risk_001",
                "risk_type": "agent",
                "severity": "high",
                "description": "CRITIC agent has no fallback mechanism if review fails",
                "affected_elements": ["CRITIC", "step_3"],
                "mitigation_suggestions": [
                    "Add error handling to CRITIC agent",
                    "Implement retry mechanism",
                    "Add GUARDIAN agent as fallback"
                ]
            }
        }


class RecommendedChange(BaseModel):
    """
    Schema for recommended change details.
    """
    change_id: str = Field(
        ..., 
        description="Unique identifier for the recommended change"
    )
    change_type: str = Field(
        ..., 
        description="Type of change (agent, component, plan, structural)"
    )
    priority: int = Field(
        ..., 
        description="Priority of the change (1-10, with 10 being highest)",
        ge=1,
        le=10
    )
    description: str = Field(
        ..., 
        description="Detailed description of the recommended change"
    )
    affected_elements: List[str] = Field(
        ..., 
        description="List of elements affected by the change"
    )
    expected_impact: Optional[str] = Field(
        None,
        description="Expected impact of implementing the change"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "change_id": "change_001",
                "change_type": "agent",
                "priority": 8,
                "description": "Add GUARDIAN agent as fallback for CRITIC",
                "affected_elements": ["agent_map", "loop_plan"],
                "expected_impact": "Improved resilience against review failures"
            }
        }


class PessimistCheckResult(BaseModel):
    """
    Schema for PESSIMIST Pre-Run Evaluation result.
    """
    project_id: str = Field(
        ..., 
        description="Project identifier"
    )
    loop_id: str = Field(
        ..., 
        description="Loop identifier"
    )
    confidence_score: float = Field(
        ..., 
        description="Confidence score for the loop plan (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    approved: bool = Field(
        ..., 
        description="Whether the loop plan is approved (confidence >= 0.6)"
    )
    risks: List[Risk] = Field(
        default=[],
        description="List of identified risks"
    )
    recommended_changes: List[RecommendedChange] = Field(
        default=[],
        description="List of recommended changes"
    )
    evaluation_summary: str = Field(
        ..., 
        description="Summary of the evaluation results"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the evaluation"
    )
    version: str = Field(
        default="1.0.0",
        description="Version of the evaluation engine"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "proj_123",
                "loop_id": "loop_456",
                "confidence_score": 0.75,
                "approved": True,
                "risks": [
                    {
                        "risk_id": "risk_001",
                        "risk_type": "agent",
                        "severity": "medium",
                        "description": "CRITIC agent has no fallback mechanism if review fails",
                        "affected_elements": ["CRITIC", "step_3"],
                        "mitigation_suggestions": [
                            "Add error handling to CRITIC agent",
                            "Implement retry mechanism",
                            "Add GUARDIAN agent as fallback"
                        ]
                    }
                ],
                "recommended_changes": [
                    {
                        "change_id": "change_001",
                        "change_type": "agent",
                        "priority": 6,
                        "description": "Add error handling to CRITIC agent",
                        "affected_elements": ["CRITIC"],
                        "expected_impact": "Improved resilience against review failures"
                    }
                ],
                "evaluation_summary": "Loop plan is generally sound with medium confidence. Some minor risks identified with the CRITIC agent that should be addressed.",
                "timestamp": "2025-04-24T19:46:43Z",
                "version": "1.0.0"
            }
        }


# Fallback schema for handling errors
class PessimistCheckError(BaseModel):
    """
    Schema for PESSIMIST Pre-Run Evaluation error result.
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
        description="Version of the evaluation engine"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "Failed to evaluate loop plan: invalid agent mapping",
                "project_id": "proj_123",
                "loop_id": "loop_456",
                "timestamp": "2025-04-24T19:46:43Z",
                "version": "1.0.0"
            }
        }
