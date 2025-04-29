# app/schemas/core/agent_result.py
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum

class ResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"
    DELEGATED = "DELEGATED"
    HALT = "HALT" # Added for Critic/Sage intervention

class AgentResult(BaseModel):
    status: ResultStatus = Field(..., description="The final status of the agent execution.")
    output: Optional[Any] = Field(None, description="The primary output or result produced by the agent.")
    error_message: Optional[str] = Field(None, description="Details about any error that occurred during execution.")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata, e.g., execution time, tokens used, reflection_id.")
    delegation_target: Optional[str] = Field(None, description="The ID of the agent to delegate to if status is DELEGATED.")
    delegation_input: Optional[Dict[str, Any]] = Field(None, description="The input data for the delegated agent.")
    requires_intervention: Optional[bool] = Field(False, description="Flag set by Critic/Sage if loop requires operator intervention or pause.")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "output": {"summary": "Task completed successfully.", "details": "..."},
                "metadata": {"execution_time": 1.23, "reflection_id": "uuid-123"}
            }
        }
