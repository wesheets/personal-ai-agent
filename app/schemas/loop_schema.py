"""
Schema definitions for loop-related API endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class LoopResponseRequest(BaseModel):
    """
    Schema for loop response request
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    project_id: str = Field(..., description="Project identifier")
    agent: str = Field(..., description="Agent to use for response (hal, ash, critic)")
    input_key: str = Field(..., description="Memory key to read for input")
    response_type: str = Field(..., description="Type of response to generate (text, code, etc.)")
    target_file: Optional[str] = Field(None, description="Target file for code generation")
