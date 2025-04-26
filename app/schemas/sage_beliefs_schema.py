"""
SAGE Beliefs Schema
This module defines the schema models for the SAGE agent's beliefs functionality.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BeliefUpdate(BaseModel):
    """
    Schema for a single belief update.
    """
    key: str = Field(..., description="Belief key to update")
    value: Any = Field(..., description="New value for the belief")
    reason: Optional[str] = Field(None, description="Reason for the update")

class SageBeliefRequest(BaseModel):
    """
    Schema for SAGE belief request.
    """
    operation: str = Field(..., description="Operation type ('get' or 'update')")
    domain: str = Field(..., description="Domain for the beliefs (e.g., 'technical', 'business', 'ethics')")
    category: Optional[str] = Field(None, description="Optional category filter for get operations")
    updates: Optional[List[BeliefUpdate]] = Field(None, description="List of belief updates for update operations")
    context: Optional[Dict[str, Any]] = Field({}, description="Additional context for the operation")

class SageBeliefResponse(BaseModel):
    """
    Schema for SAGE belief response.
    """
    status: str = Field(..., description="Status of the operation (success or error)")
    operation: str = Field(..., description="Operation type that was performed")
    domain: str = Field(..., description="Domain for the beliefs")
    beliefs: Optional[Dict[str, Any]] = Field(None, description="Current beliefs for get operations")
    updated: Optional[List[str]] = Field(None, description="List of updated belief keys for update operations")
    timestamp: float = Field(..., description="Timestamp of the operation")

class SageErrorResult(BaseModel):
    """
    Schema for SAGE error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    domain: Optional[str] = Field(None, description="Domain for the beliefs")
    operation: Optional[str] = Field(None, description="Operation type that was attempted")
