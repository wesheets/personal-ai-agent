"""
Memory Delete Schema Module

This module defines the schema for memory deletion operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# memory_tag: stubbed_phase2.5
class MemoryDeleteRequest(BaseModel):
    """
    Schema for memory delete request.
    """
    key: str = Field(..., description="Key of the memory to delete")

# memory_tag: stubbed_phase2.5
class MemoryDeleteResponse(BaseModel):
    """
    Schema for memory delete response.
    """
    status: str = Field(..., description="Status of the operation")
    key: str = Field(..., description="Key of the deleted memory")
    message: str = Field(..., description="Status message about the deletion")
