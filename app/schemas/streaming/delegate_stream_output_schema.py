"""
Delegate Stream Schema Module

This module defines the schema for delegate stream operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class DelegateStreamRequest(BaseModel):
    """
    Schema for delegate stream request.
    """
    agent_id: str = Field(..., description="The agent identifier")
    task: Dict[str, Any] = Field(..., description="The task data")

# memory_tag: stubbed_phase2.5
class DelegateStreamResponse(BaseModel):
    """
    Schema for delegate stream response.
    """
    status: str = Field(..., description="Status of the operation")
    agent: str = Field(..., description="The agent name")
    message: str = Field(..., description="The response message")
    tone: str = Field(..., description="The tone of the response")
    received: Optional[Dict[str, Any]] = Field(None, description="The received request data")
    processing: Dict[str, Any] = Field(..., description="Processing metadata")
