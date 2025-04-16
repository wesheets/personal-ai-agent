"""
Response Module Models

This module provides Pydantic models for the respond endpoint, which enables
agent responses based on user context and memory scope.
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any

class RespondRequest(BaseModel):
    """
    Request model for the respond endpoint
    
    This model defines the schema for respond requests, including user identification
    and the message to respond to.
    """
    user_id: str = Field(..., description="ID of the user sending the message")
    message: str = Field(..., description="Message content to respond to")
    log_interaction: bool = Field(False, description="Whether to log the interaction to memory")
    session_id: Optional[str] = Field(None, description="Optional session ID for multi-thread continuity")

class RespondResponse(BaseModel):
    """
    Response model for the respond endpoint
    
    This model defines the schema for respond responses, including the agent's response
    and metadata about the agent and processing.
    """
    status: str = Field(..., description="Status of the response (ok, error)")
    agent_id: str = Field(..., description="ID of the agent that generated the response")
    response: str = Field(..., description="Agent's response to the user's message")
    memory_id: Optional[str] = Field(None, description="ID of the memory created for this response")
    session_id: Optional[str] = Field(None, description="Session ID for multi-thread continuity")
