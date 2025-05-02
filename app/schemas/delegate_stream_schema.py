"""
Delegate Stream Schema

This module defines the schemas for the delegate stream endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class StreamType(str, Enum):
    """Types of streams that can be delegated."""
    AGENT = "agent"
    LOOP = "loop"
    MEMORY = "memory"
    PLAN = "plan"
    CUSTOM = "custom"


class StreamPriority(str, Enum):
    """Priority levels for streams."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StreamRequest(BaseModel):
    """Request schema for creating a delegate stream."""
    stream_type: StreamType = Field(
        ..., 
        description="Type of stream to create"
    )
    target_id: str = Field(
        ..., 
        description="Identifier for the target to stream (e.g., loop_id, agent_id)"
    )
    description: str = Field(
        ..., 
        description="Description of the stream purpose"
    )
    priority: StreamPriority = Field(
        StreamPriority.MEDIUM, 
        description="Priority level for the stream"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Filters to apply to the stream"
    )
    max_events: Optional[int] = Field(
        None, 
        description="Maximum number of events to stream"
    )
    timeout_seconds: Optional[int] = Field(
        None, 
        description="Timeout in seconds for the stream"
    )
    agent_id: Optional[str] = Field(
        None, 
        description="Agent ID requesting the stream"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Loop ID associated with the stream"
    )
    
    @validator('target_id')
    def target_id_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('target_id must not be empty')
        return v
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('description must not be empty')
        return v
    
    @validator('max_events')
    def max_events_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('max_events must be positive')
        return v
    
    @validator('timeout_seconds')
    def timeout_seconds_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('timeout_seconds must be positive')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "stream_type": "loop",
                "target_id": "loop_12345",
                "description": "Stream loop events for monitoring",
                "priority": "medium",
                "filters": {
                    "event_types": ["agent_call", "memory_access", "error"],
                    "min_confidence": 0.7
                },
                "max_events": 1000,
                "timeout_seconds": 3600,
                "agent_id": "MONITOR",
                "loop_id": "loop_12345"
            }
        }


class StreamResponse(BaseModel):
    """Response schema for stream creation."""
    stream_id: str = Field(..., description="Unique identifier for the stream")
    stream_type: StreamType = Field(..., description="Type of stream created")
    target_id: str = Field(..., description="Identifier for the target being streamed")
    status: str = Field(..., description="Status of the stream (e.g., 'active', 'pending', 'closed')")
    connection_url: str = Field(..., description="URL for connecting to the stream")
    token: str = Field(..., description="Authentication token for the stream")
    expires_at: str = Field(..., description="ISO timestamp when the stream expires")
    agent_id: Optional[str] = Field(None, description="Agent ID that requested the stream")
    loop_id: Optional[str] = Field(None, description="Loop ID associated with the stream")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of stream creation"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "stream_id": "stream_12345",
                "stream_type": "loop",
                "target_id": "loop_12345",
                "status": "active",
                "connection_url": "wss://api.promethios.ai/streams/stream_12345",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_at": "2025-04-25T21:00:00Z",
                "agent_id": "MONITOR",
                "loop_id": "loop_12345",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class StreamError(BaseModel):
    """Error response schema for stream operations."""
    message: str = Field(..., description="Error message")
    stream_type: Optional[StreamType] = Field(None, description="Requested stream type if available")
    target_id: Optional[str] = Field(None, description="Requested target ID if available")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Failed to create stream: Target not found",
                "stream_type": "loop",
                "target_id": "loop_12345",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class StreamStatusRequest(BaseModel):
    """Request schema for checking stream status."""
    stream_id: str = Field(..., description="Unique identifier for the stream")
    
    class Config:
        schema_extra = {
            "example": {
                "stream_id": "stream_12345"
            }
        }


class StreamStatusResponse(BaseModel):
    """Response schema for stream status."""
    stream_id: str = Field(..., description="Unique identifier for the stream")
    stream_type: StreamType = Field(..., description="Type of stream")
    target_id: str = Field(..., description="Identifier for the target")
    status: str = Field(..., description="Status of the stream (e.g., 'active', 'pending', 'closed')")
    events_streamed: int = Field(..., description="Number of events streamed so far")
    connected_clients: int = Field(..., description="Number of clients connected to the stream")
    created_at: str = Field(..., description="ISO timestamp when the stream was created")
    expires_at: str = Field(..., description="ISO timestamp when the stream expires")
    agent_id: Optional[str] = Field(None, description="Agent ID that requested the stream")
    loop_id: Optional[str] = Field(None, description="Loop ID associated with the stream")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the status check"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "stream_id": "stream_12345",
                "stream_type": "loop",
                "target_id": "loop_12345",
                "status": "active",
                "events_streamed": 42,
                "connected_clients": 2,
                "created_at": "2025-04-24T20:00:00Z",
                "expires_at": "2025-04-25T20:00:00Z",
                "agent_id": "MONITOR",
                "loop_id": "loop_12345",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class StreamCloseRequest(BaseModel):
    """Request schema for closing a stream."""
    stream_id: str = Field(..., description="Unique identifier for the stream to close")
    reason: Optional[str] = Field(None, description="Reason for closing the stream")
    
    class Config:
        schema_extra = {
            "example": {
                "stream_id": "stream_12345",
                "reason": "Monitoring complete"
            }
        }


class StreamCloseResponse(BaseModel):
    """Response schema for stream closure."""
    stream_id: str = Field(..., description="Unique identifier for the stream that was closed")
    status: str = Field(..., description="Status of the closure (e.g., 'success', 'already_closed')")
    events_streamed: int = Field(..., description="Total number of events streamed")
    duration_seconds: int = Field(..., description="Duration of the stream in seconds")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the closure"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "stream_id": "stream_12345",
                "status": "success",
                "events_streamed": 128,
                "duration_seconds": 1800,
                "timestamp": "2025-04-24T21:30:00Z",
                "version": "1.0.0"
            }
        }


class StreamEvent(BaseModel):
    """Schema for a stream event."""
    event_id: str = Field(..., description="Unique identifier for the event")
    stream_id: str = Field(..., description="Identifier for the stream")
    event_type: str = Field(..., description="Type of event")
    source: str = Field(..., description="Source of the event")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the event"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "event_id": "event_12345",
                "stream_id": "stream_12345",
                "event_type": "agent_call",
                "source": "loop_processor",
                "data": {
                    "agent_id": "MEMORY",
                    "function": "recall",
                    "parameters": {"query": "project goals"},
                    "result": {"confidence": 0.92, "matches": 3}
                },
                "timestamp": "2025-04-24T21:15:30Z"
            }
        }
