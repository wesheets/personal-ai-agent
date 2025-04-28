"""
Root Schema Module

This module defines the schema for the root endpoint.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class RootResponse(BaseModel):
    """
    Schema for root endpoint response.
    """
    status: str = Field(..., description="Status of the API")
    version: str = Field(..., description="API version")
    endpoints: List[str] = Field(..., description="List of available endpoints")
    documentation: Optional[str] = Field(None, description="URL to API documentation")
    environment: Optional[str] = Field(None, description="Current environment (dev, staging, prod)")
    uptime: Optional[float] = Field(None, description="API uptime in seconds")
