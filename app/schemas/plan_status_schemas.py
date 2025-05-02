# memory_tag: phase3.0_sprint4_batch3_stub_creation

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PlanStatusRequest(BaseModel):
    """Schema for requesting the status of a plan execution."""
    execution_id: str = Field(..., description="The unique identifier of the plan execution instance.")

    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
            }
        }

class PlanStepStatus(BaseModel):
    """Schema for the status of a single step within a plan execution."""
    step_id: str
    step_number: int
    status: str # e.g., pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class PlanStatusResponse(BaseModel):
    """Schema for the response containing the status of a plan execution."""
    execution_id: str = Field(..., description="The unique identifier of the plan execution instance.")
    plan_id: str = Field(..., description="The unique identifier of the plan being executed.")
    overall_status: str = Field(..., description="The overall status of the plan execution (e.g., \"running\", \"completed\", \"failed\").")
    current_step: Optional[int] = Field(None, description="The step number currently being executed.")
    steps_status: List[PlanStepStatus] = Field(..., description="Status details for each step in the plan.")
    started_at: datetime = Field(..., description="Timestamp when the execution was initiated.")
    last_updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the status was last updated.")
    final_result: Optional[Dict[str, Any]] = Field(None, description="Final result or output upon completion.")

    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "plan_id": "d47ac10b-58cc-4372-a567-0e02b2c3d479",
                "overall_status": "running",
                "current_step": 2,
                "steps_status": [
                    {"step_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "step_number": 1, "status": "completed", "started_at": "2025-04-28T12:30:05Z", "completed_at": "2025-04-28T12:30:45Z"},
                    {"step_id": "g47ac10b-58cc-4372-a567-0e02b2c3d479", "step_number": 2, "status": "running", "started_at": "2025-04-28T12:30:46Z"}
                ],
                "started_at": "2025-04-28T12:30:00Z",
                "last_updated_at": "2025-04-28T12:32:00Z",
                "final_result": None
            }
        }
