"""
Memory Write Schema Module

This module defines the schema for memory writing operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class MemoryWriteRequest(BaseModel):
    """
    Schema for memory write request.
    """
    content: str = Field(..., description="Content of the memory to write")
    agent_id: str = Field(..., description="ID of the agent associated with the memory")
    type: str = Field(..., description="Type of memory (e.g., observation, reflection, plan)")
    tags: List[str] = Field(default=[], description="Tags associated with the memory")
    project_id: Optional[str] = Field(None, description="ID of the associated project")
    task_id: Optional[str] = Field(None, description="ID of the associated task")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# memory_tag: stubbed_phase2.5
class MemoryWriteResponse(BaseModel):
    """
    Schema for memory write response.
    """
    memory_id: str = Field(..., description="Unique identifier for the written memory")
    status: str = Field(..., description="Status of the operation")
    timestamp: str = Field(..., description="Timestamp when the memory was written")
    agent_id: str = Field(..., description="ID of the agent associated with the memory")
    type: str = Field(..., description="Type of memory")
    tags: List[str] = Field(default=[], description="Tags associated with the memory")
