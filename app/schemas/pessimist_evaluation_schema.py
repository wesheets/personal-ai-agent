"""
PESSIMIST Evaluation Schema
This module defines the schema models for the PESSIMIST agent's evaluation functionality.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Risk(BaseModel):
    """
    Schema for a single risk identified by the PESSIMIST agent.
    """
    title: str = Field(..., description="Short title of the risk")
    description: str = Field(..., description="Detailed description of the risk")
    severity: int = Field(..., description="Risk severity score (1-10)", ge=1, le=10)
    likelihood: int = Field(..., description="Risk likelihood score (1-10)", ge=1, le=10)
    impact: int = Field(..., description="Risk impact score (1-10)", ge=1, le=10)
    category: str = Field(..., description="Risk category (e.g., 'security', 'performance', 'usability')")
    mitigation: Optional[str] = Field(None, description="Suggested mitigation strategy")

class PessimistEvaluationRequest(BaseModel):
    """
    Schema for PESSIMIST evaluation request.
    """
    project_id: str = Field(..., description="Unique identifier for the project")
    content: str = Field(..., description="Content to evaluate for risks")
    context: Optional[Dict[str, Any]] = Field({}, description="Additional context for evaluation")
    risk_threshold: Optional[int] = Field(5, description="Threshold for flagging high risks (1-10)", ge=1, le=10)
    tools: Optional[List[str]] = Field(
        default=["evaluate", "analyze", "recommend"],
        description="List of tools to use for the evaluation"
    )

class PessimistEvaluationResult(BaseModel):
    """
    Schema for PESSIMIST evaluation result.
    """
    status: str = Field(..., description="Status of the evaluation (success or error)")
    project_id: str = Field(..., description="Unique identifier for the project")
    risks: List[Risk] = Field(..., description="List of identified risks")
    overall_risk_score: int = Field(..., description="Overall risk score (1-10)", ge=1, le=10)
    recommendations: List[str] = Field(..., description="List of recommendations to mitigate risks")
    timestamp: float = Field(..., description="Timestamp of the evaluation")
