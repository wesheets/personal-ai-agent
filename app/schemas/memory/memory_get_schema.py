"""
Memory Get Schema Module

This module defines the schema for memory retrieval operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class MemoryItem(BaseModel):
    """
    Schema for a single memory item.
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

# memory_tag: stubbed_phase2.5
class MemoryGetResponse(BaseModel):
    """
    Schema for memory get response.
    """
    memories: List[MemoryItem] = Field(..., description="List of memory items")
    total_count: int = Field(..., description="Total number of memories")
    status: str = Field(..., description="Status of the operation")

# memory_tag: stubbed_phase2.5
class MemoryGetByIdResponse(BaseModel):
    """
    Schema for memory get by ID response.
    """
    memory: MemoryItem = Field(..., description="The requested memory item")
    status: str = Field(..., description="Status of the operation")
