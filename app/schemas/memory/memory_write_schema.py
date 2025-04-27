"""
Memory Write Schema Module

This module defines the schema for memory write operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class MemoryWriteRequest(BaseModel):
    """
    Schema for memory write request.
    """
    project_id: str = Field(default="default", description="The project identifier")
    agent: str = Field(default="default", description="The agent identifier")
    type: str = Field(default="note", description="The memory entry type")
    content: str = Field(..., description="The memory entry content")
    tags: Optional[List[str]] = Field(default=[], description="Optional list of tags")
    chain_id: Optional[str] = Field(default="default", description="The chain identifier")

# memory_tag: stubbed_phase2.5
class MemoryWriteResponse(BaseModel):
    """
    Schema for memory write response.
    """
    status: str = Field(..., description="Status of the memory write operation")
    message: str = Field(..., description="Message describing the result of the operation")
    content: str = Field(..., description="The content that was written to memory")
    project_id: str = Field(..., description="The project identifier")
    chain_id: str = Field(..., description="The chain identifier")
    timestamp: str = Field(..., description="Timestamp of the memory write operation")
