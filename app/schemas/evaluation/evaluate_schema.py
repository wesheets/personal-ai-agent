"""
Evaluation Schema Module

This module defines the schema for evaluation operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class EvaluateRequest(BaseModel):
    """
    Schema for evaluate request.
    """
    plan_content: str = Field(..., description="Plan or proposal content to evaluate")
    context: Optional[str] = Field(None, description="Additional context for the evaluation")
    risk_tolerance: str = Field(default="medium", description="Risk tolerance level (low, medium, high)")
    evaluation_depth: str = Field(default="standard", description="Depth of evaluation (quick, standard, comprehensive)")
    focus_areas: List[str] = Field(default=[], description="Specific areas to focus on during evaluation")

# memory_tag: stubbed_phase2.5
class RiskAssessment(BaseModel):
    """
    Schema for risk assessment.
    """
    risk_id: str = Field(..., description="Unique identifier for the risk")
    category: str = Field(..., description="Risk category")
    description: str = Field(..., description="Risk description")
    likelihood: float = Field(..., description="Likelihood of the risk occurring (0-1)")
    impact: float = Field(..., description="Impact of the risk if it occurs (0-1)")
    risk_score: float = Field(..., description="Overall risk score (likelihood * impact)")
    mitigation_suggestions: List[str] = Field(..., description="Suggestions for mitigating the risk")

# memory_tag: stubbed_phase2.5
class EvaluateResponse(BaseModel):
    """
    Schema for evaluate response.
    """
    status: str = Field(..., description="Status of the evaluation operation")
    message: str = Field(..., description="Message describing the result of the operation")
    evaluation_id: str = Field(..., description="Unique identifier for the evaluation")
    summary: str = Field(..., description="Summary of the evaluation")
    risks: List[RiskAssessment] = Field(..., description="List of identified risks")
    edge_cases: List[Dict[str, Any]] = Field(..., description="List of identified edge cases")
    assumptions: List[Dict[str, Any]] = Field(..., description="List of identified assumptions")
    overall_risk_score: float = Field(..., description="Overall risk score for the plan")
    timestamp: str = Field(..., description="Timestamp of the evaluation")
