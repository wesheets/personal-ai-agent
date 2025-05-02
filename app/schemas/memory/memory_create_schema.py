"""
Memory Create Schema Module

This module defines the schema for memory creation operations.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# memory_tag: stubbed_phase2.5
class MemoryCreateRequest(BaseModel):
    """
    Schema for memory creation request.
    """
    content: str = Field(..., description="Content of the memory")
    agent_id: str = Field(..., description="ID of the agent associated with the memory")
    type: str = Field(..., description="Type of memory (e.g., observation, reflection, plan)")
    tags: Optional[List[str]] = Field(default=[], description="Tags associated with the memory")
    project_id: Optional[str] = Field(None, description="ID of the associated project")
    task_id: Optional[str] = Field(None, description="ID of the associated task")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# memory_tag: stubbed_phase2.5
class MemoryCreateResponse(BaseModel):
    """
    Schema for memory creation response.
    """
    memory_id: str = Field(..., description="ID of the created memory")
    status: str = Field(..., description="Status of the operation")
    timestamp: str = Field(..., description="Timestamp of memory creation")
    agent_id: str = Field(..., description="ID of the agent associated with the memory")
    type: str = Field(..., description="Type of memory")
    tags: List[str] = Field(default=[], description="Tags associated with the memory")
