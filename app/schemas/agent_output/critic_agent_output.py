from pydantic import BaseModel, Field
from typing import List, Optional
from app.utils.status import ResultStatus

class CriticPlanEvaluationResult(BaseModel):
    loop_id: str = Field(..., description="The ID of the loop being evaluated.")
    status: ResultStatus = Field(..., description="The overall status of the evaluation process.")
    approved: bool = Field(..., description="Whether the proposed plan is approved by the Critic.")
    justification: str = Field(..., description="The Critic's reasoning for the approval or rejection decision.")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="The Critic's confidence in its evaluation.")
    error_message: Optional[str] = Field(default=None, description="Details if an error occurred during evaluation.")

