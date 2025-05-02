from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PessimistEvaluateRequest(BaseModel):
    """
    Schema for pessimist evaluate request.
    """
    plan_content: str = Field(..., description="Plan or proposal content to evaluate")
    context: Optional[str] = Field(None, description="Additional context for the evaluation")
    risk_tolerance: str = Field(default="medium", description="Risk tolerance level (low, medium, high)")
    evaluation_depth: str = Field(default="standard", description="Depth of evaluation (quick, standard, comprehensive)")
    focus_areas: List[str] = Field(default=[], description="Specific areas to focus on during evaluation")

class RiskAssessment(BaseModel):
    """
    Schema for risk assessment.
    """
    risk_id: str
    category: str
    description: str
    likelihood: float
    impact: float
    risk_score: float
    mitigation_suggestions: List[str]

class PessimistEvaluateResponse(BaseModel):
    """
    Schema for pessimist evaluate response.
    """
    status: str
    message: str
    evaluation_id: str
    summary: str
    risks: List[RiskAssessment]
    edge_cases: List[Dict[str, Any]]
    assumptions: List[Dict[str, Any]]
    overall_risk_score: float
    timestamp: str
