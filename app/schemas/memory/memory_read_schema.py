"""
Memory Read Schema Module

This module defines the schema for memory reading operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class MemoryReadResponse(BaseModel):
    """
    Schema for memory read response.
    """
    memories: List[Dict[str, Any]] = Field(..., description="List of memory items")
    total_count: int = Field(..., description="Total number of memories")
    status: str = Field(..., description="Status of the operation")
    agent_id: Optional[str] = Field(None, description="ID of the agent associated with the memories")
    filters_applied: Optional[Dict[str, Any]] = Field(default={}, description="Filters applied to the query")

# memory_tag: stubbed_phase2.5
class MemoryReadByIdResponse(BaseModel):
    """
    Schema for memory read by ID response.
    """
    memory_id: str = Field(..., description="Unique identifier for the memory")
    content: str = Field(..., description="Content of the memory")
    agent_id: str = Field(..., description="ID of the agent associated with the memory")
    type: str = Field(..., description="Type of memory (e.g., observation, reflection, plan)")
    tags: List[str] = Field(default=[], description="Tags associated with the memory")
    created_at: str = Field(..., description="Timestamp when the memory was created")
    project_id: Optional[str] = Field(None, description="ID of the associated project")
    task_id: Optional[str] = Field(None, description="ID of the associated task")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    status: str = Field(..., description="Status of the operation")



# memory_tag: phase3.3b_critical_surface_patch
class MemoryReadRequest(BaseModel):
    """
    Schema for memory read request.
    """
    memory_id: str
    include_full_context: bool = False
