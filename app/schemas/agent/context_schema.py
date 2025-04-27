"""
Agent Context Schema Module

This module defines the schema for agent context operations.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# memory_tag: stubbed_phase2.5
class AgentContextGetRequest(BaseModel):
    """
    Schema for agent context GET request.
    """
    agent_id: str = Field(..., description="The agent identifier")
    loop_id: Optional[str] = Field(None, description="The loop identifier")
    include_memory_stats: bool = Field(True, description="Whether to include memory usage statistics")

# memory_tag: stubbed_phase2.5
class AgentContextPostRequest(BaseModel):
    """
    Schema for agent context POST request.
    """
    agent_id: str = Field(..., description="The agent identifier")
    loop_id: Optional[str] = Field(None, description="The loop identifier")
    include_memory_stats: bool = Field(True, description="Whether to include memory usage statistics")

# memory_tag: stubbed_phase2.5
class AgentContextGetResponse(BaseModel):
    """
    Schema for agent context GET response.
    """
    agent_id: str = Field(..., description="The agent identifier")
    loop_id: Optional[str] = Field(None, description="The loop identifier")
    loop_state: Optional[Dict[str, Any]] = Field(None, description="The loop state")
    last_agent: Optional[str] = Field(None, description="The last agent used in the loop")
    memory_stats: Optional[Dict[str, Any]] = Field(None, description="Memory usage statistics")
    status: str = Field(..., description="Status of the operation")
