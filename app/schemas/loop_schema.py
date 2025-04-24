from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LoopResponseRequest(BaseModel):
    """
    Schema for the loop/respond endpoint request.
    
    This schema defines the structure of requests to the HAL agent's
    loop/respond endpoint for code generation tasks.
    """
    project_id: str = Field(..., description="Project identifier")
    loop_id: str = Field(..., description="Loop identifier, typically same as project_id")
    agent: str = Field(..., description="Agent identifier, e.g. 'hal'")
    response_type: str = Field(..., description="Type of response expected, e.g. 'code'")
    target_file: str = Field(..., description="Target file for the generated code")
    input_key: str = Field(..., description="Memory key to read the task from")
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "insight_loop_saas",
                "loop_id": "insight_loop_saas",
                "agent": "hal",
                "response_type": "code",
                "target_file": "OnboardingForm.jsx",
                "input_key": "build_task"
            }
        }

class LoopResponseResult(BaseModel):
    """
    Schema for the loop/respond endpoint response.
    
    This schema defines the structure of responses from the HAL agent's
    loop/respond endpoint after code generation.
    """
    status: str = Field(..., description="Status of the operation")
    output_tag: str = Field(..., description="Memory tag where the result was stored")
    timestamp: str = Field(..., description="Timestamp of the operation")
    code: Optional[str] = Field(None, description="Generated code (optional)")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "HAL build complete",
                "output_tag": "hal_build_task_response",
                "timestamp": "2025-04-24T00:50:48.123456",
                "code": "// Optional: The generated React component code"
            }
        }
