"""
Init Schema Module

This module defines the schema for system initialization operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class InitRequest(BaseModel):
    """
    Schema for initialization request.
    """
    agent_id: Optional[str] = Field(None, description="ID of the agent to initialize")
    config: Optional[Dict[str, Any]] = Field(default={}, description="Configuration parameters")
    mode: Optional[str] = Field("standard", description="Initialization mode")
    reset: Optional[bool] = Field(False, description="Whether to reset existing state")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# memory_tag: stubbed_phase2.5
class InitResponse(BaseModel):
    """
    Schema for initialization response.
    """
    status: str = Field(..., description="Status of the initialization")
    agent_id: Optional[str] = Field(None, description="ID of the initialized agent")
    session_id: str = Field(..., description="ID of the initialized session")
    timestamp: str = Field(..., description="Timestamp of initialization")
    message: Optional[str] = Field(None, description="Additional status message")
