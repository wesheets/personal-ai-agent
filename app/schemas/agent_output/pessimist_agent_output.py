from pydantic import BaseModel, Field
from typing import Optional
from app.utils.status import ResultStatus

class PessimistRiskAssessmentResult(BaseModel):
    loop_id: str = Field(..., description="The ID of the loop being assessed.")
    status: ResultStatus = Field(..., description="The overall status of the risk assessment process.")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="The calculated risk score for the plan (0.0 = low risk, 1.0 = high risk).")
    justification: str = Field(..., description="The Pessimist's reasoning for the assigned risk score.")
    error_message: Optional[str] = Field(default=None, description="Details if an error occurred during risk assessment.")

