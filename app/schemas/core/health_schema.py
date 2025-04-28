"""
Core Health Schema Module

This module defines the schema for health check operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# memory_tag: stubbed_phase2.5
class HealthCheckResponse(BaseModel):
    """
    Schema for health check response.
    """
    status: str = Field(..., description="Status of the system")
