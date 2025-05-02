"""
Memory Read Request Schema Module

This module defines the schema for memory read request operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# memory_tag: stubbed_phase2.5
class MemoryReadRequest(BaseModel):
    """
    Schema for memory read request.
    """
    key: str = Field(..., description="Key of the memory to read")
