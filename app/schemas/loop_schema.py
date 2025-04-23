"""
Loop Schema Module
This module defines the schemas for loop-related operations.
"""
from typing import Dict, Any, Optional, List, Literal
from pydantic import BaseModel, Field

class LoopResponseRequest(BaseModel):
    """
    Request model for loop-respond endpoint.
    Used to generate agent responses to memory within a loop.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    project_id: str = Field(..., description="Project identifier")
    agent: str = Field(..., description="Agent identifier (e.g., hal, ash, critic)")
    input_key: str = Field(..., description="Memory key to read input from")
    response_type: Literal["code", "comment", "judgment"] = Field(..., description="Type of response to generate")
    target_file: Optional[str] = Field(None, description="Target file for code responses, required if response_type is 'code'")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_123456",
                "project_id": "project_789012",
                "agent": "hal",
                "input_key": "task_description",
                "response_type": "code",
                "target_file": "api/user_service.py"
            }
        }
