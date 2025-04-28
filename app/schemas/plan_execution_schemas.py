# memory_tag: phase3.0_sprint4_batch3_stub_creation

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class PlanExecutionRequest(BaseModel):
    """Schema for requesting the execution of a plan."""
    plan_id: str = Field(..., description="The unique identifier of the plan to be executed.")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional parameters to pass to the plan execution context.")
    timeout: Optional[int] = Field(default=300, description="Maximum execution time in seconds before timeout.")

    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "d47ac10b-58cc-4372-a567-0e02b2c3d479",
                "parameters": {"target_surface": "pice"},
                "timeout": 600
            }
        }

class PlanExecutionResponse(BaseModel):
    """Schema for the response after initiating plan execution."""
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for this specific execution instance.")
    plan_id: str = Field(..., description="The unique identifier of the plan being executed.")
    status: str = Field(..., description="The initial status of the plan execution (e.g., \"started\", \"queued\").")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the execution was initiated.")

    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "plan_id": "d47ac10b-58cc-4372-a567-0e02b2c3d479",
                "status": "started",
                "started_at": "2025-04-28T12:30:00Z"
            }
        }
