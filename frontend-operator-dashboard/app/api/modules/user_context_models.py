"""
Pydantic models for the user context module.

This module defines the request and response schemas for the user_context endpoints
which provide user registration and context retrieval functionality.
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

class UserContextRegisterRequest(BaseModel):
    """
    Request model for registering a new user
    
    This model defines the input schema for registering a new user with their
    preferences and agent association.
    """
    user_id: str
    name: str
    agent_id: str
    preferences: Dict[str, Any] = Field(default_factory=dict)

class UserContextRegisterResponse(BaseModel):
    """
    Response model for the user registration endpoint
    
    This model defines the output schema for user registration, including
    the generated user_context_id and memory_scope.
    """
    status: str
    user_context_id: str
    memory_scope: str

class UserContextGetRequest(BaseModel):
    """
    Request model for retrieving user context
    
    This model defines the input schema for retrieving a user's context
    """
    user_id: str

class UserContextGetResponse(BaseModel):
    """
    Response model for the user context retrieval endpoint
    
    This model defines the output schema for a user's context, including
    their preferences and associated agent.
    """
    user_id: str
    agent_id: str
    memory_scope: str
    preferences: Dict[str, Any]
    created_at: Optional[str] = None  # ISO8601 timestamp
