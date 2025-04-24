"""
Agent Context Schema

This module defines the schemas for agent context endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class MemoryUsage(BaseModel):
    """Memory usage statistics."""
    total_entries: int = Field(..., description="Total number of memory entries")
    recent_entries: int = Field(..., description="Number of entries in the last 24 hours")
    tags_count: Dict[str, int] = Field(
        {}, 
        description="Count of entries by tag"
    )
    size_bytes: Optional[int] = Field(
        None, 
        description="Total size of memory entries in bytes (if available)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "total_entries": 1250,
                "recent_entries": 42,
                "tags_count": {
                    "conversation": 850,
                    "plan_generated": 125,
                    "agent_output": 275
                },
                "size_bytes": 2560000
            }
        }


class AgentState(str, Enum):
    """Possible states for an agent."""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"


class LoopState(BaseModel):
    """Current state of a loop."""
    loop_id: str = Field(..., description="Unique identifier for the loop")
    current_step: int = Field(..., description="Current step in the loop")
    total_steps: int = Field(..., description="Total number of steps in the loop")
    started_at: str = Field(..., description="ISO timestamp when the loop started")
    last_updated: str = Field(..., description="ISO timestamp when the loop was last updated")
    state: str = Field(..., description="Current state of the loop")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_12345",
                "current_step": 3,
                "total_steps": 5,
                "started_at": "2025-04-24T20:30:00Z",
                "last_updated": "2025-04-24T20:45:00Z",
                "state": "active"
            }
        }


class LastAgentAction(BaseModel):
    """Information about the last agent action."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    action_type: str = Field(..., description="Type of action performed")
    timestamp: str = Field(..., description="ISO timestamp when the action was performed")
    status: str = Field(..., description="Status of the action")
    details: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional details about the action"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "CRITIC",
                "action_type": "review",
                "timestamp": "2025-04-24T20:44:30Z",
                "status": "completed",
                "details": {
                    "review_id": "rev_789",
                    "issues_found": 2,
                    "confidence": 0.85
                }
            }
        }


class AgentContextRequest(BaseModel):
    """Request schema for getting agent context."""
    agent_id: Optional[str] = Field(
        None, 
        description="Unique identifier for the agent (if None, returns context for all agents)"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Unique identifier for the loop (if None, returns context for current loop)"
    )
    include_memory_stats: bool = Field(
        True, 
        description="Whether to include memory usage statistics"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "ORCHESTRATOR",
                "loop_id": "loop_12345",
                "include_memory_stats": True
            }
        }


class AgentContextResponse(BaseModel):
    """Response schema for agent context."""
    agent_id: str = Field(..., description="Unique identifier for the agent")
    state: AgentState = Field(..., description="Current state of the agent")
    loop_state: Optional[LoopState] = Field(
        None, 
        description="Current state of the loop (if available)"
    )
    last_action: Optional[LastAgentAction] = Field(
        None, 
        description="Information about the last agent action (if available)"
    )
    memory_usage: Optional[MemoryUsage] = Field(
        None, 
        description="Memory usage statistics (if requested)"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the response"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "agent_id": "ORCHESTRATOR",
                "state": "active",
                "loop_state": {
                    "loop_id": "loop_12345",
                    "current_step": 3,
                    "total_steps": 5,
                    "started_at": "2025-04-24T20:30:00Z",
                    "last_updated": "2025-04-24T20:45:00Z",
                    "state": "active"
                },
                "last_action": {
                    "agent_id": "ORCHESTRATOR",
                    "action_type": "plan",
                    "timestamp": "2025-04-24T20:40:00Z",
                    "status": "completed",
                    "details": {
                        "plan_id": "plan_456",
                        "steps_created": 5
                    }
                },
                "memory_usage": {
                    "total_entries": 1250,
                    "recent_entries": 42,
                    "tags_count": {
                        "conversation": 850,
                        "plan_generated": 125,
                        "agent_output": 275
                    },
                    "size_bytes": 2560000
                },
                "timestamp": "2025-04-24T20:46:30Z",
                "version": "1.0.0"
            }
        }


class AgentContextError(BaseModel):
    """Error response schema for agent context."""
    message: str = Field(..., description="Error message")
    agent_id: Optional[str] = Field(None, description="Agent ID if available")
    loop_id: Optional[str] = Field(None, description="Loop ID if available")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Failed to get agent context: Agent not found",
                "agent_id": "UNKNOWN_AGENT",
                "loop_id": "loop_12345",
                "timestamp": "2025-04-24T20:46:30Z",
                "version": "1.0.0"
            }
        }
