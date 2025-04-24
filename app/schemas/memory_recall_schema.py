"""
Memory Recall Schema

This module defines the schemas for memory recall endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class RecallMethod(str, Enum):
    """Methods for memory recall."""
    TAG = "tag"
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"
    AGENT = "agent"


class RecallSortOrder(str, Enum):
    """Sort order for memory recall results."""
    NEWEST_FIRST = "newest_first"
    OLDEST_FIRST = "oldest_first"
    RELEVANCE = "relevance"


class MemoryRecallRequest(BaseModel):
    """Request schema for memory recall."""
    method: RecallMethod = Field(
        RecallMethod.TAG, 
        description="Method to use for memory recall"
    )
    query: str = Field(..., description="Query string for memory recall")
    limit: int = Field(10, description="Maximum number of results to return")
    offset: int = Field(0, description="Offset for pagination")
    sort_order: RecallSortOrder = Field(
        RecallSortOrder.NEWEST_FIRST, 
        description="Sort order for results"
    )
    start_date: Optional[str] = Field(
        None, 
        description="ISO timestamp for start date filter (inclusive)"
    )
    end_date: Optional[str] = Field(
        None, 
        description="ISO timestamp for end date filter (inclusive)"
    )
    agent_filter: Optional[str] = Field(
        None, 
        description="Filter results by agent ID"
    )
    loop_filter: Optional[str] = Field(
        None, 
        description="Filter results by loop ID"
    )
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('query must not be empty')
        return v
    
    @validator('limit')
    def limit_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('limit must be positive')
        if v > 100:
            return 100  # Cap at 100 for performance
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "method": "tag",
                "query": "plan_generated",
                "limit": 10,
                "offset": 0,
                "sort_order": "newest_first",
                "start_date": "2025-04-20T00:00:00Z",
                "end_date": "2025-04-24T23:59:59Z",
                "agent_filter": "ORCHESTRATOR",
                "loop_filter": "loop_12345"
            }
        }


class MemoryEntry(BaseModel):
    """Schema for a memory entry."""
    memory_id: str = Field(..., description="Unique identifier for the memory entry")
    content: Dict[str, Any] = Field(..., description="Content of the memory entry")
    tags: List[str] = Field(..., description="Tags associated with the memory entry")
    agent_id: Optional[str] = Field(None, description="Agent ID associated with the memory entry")
    loop_id: Optional[str] = Field(None, description="Loop ID associated with the memory entry")
    timestamp: str = Field(..., description="ISO timestamp when the memory was created")
    
    class Config:
        schema_extra = {
            "example": {
                "memory_id": "mem_12345",
                "content": {
                    "plan_id": "plan_456",
                    "steps": [
                        "Analyze requirements",
                        "Design solution",
                        "Implement code",
                        "Test implementation",
                        "Deploy to production"
                    ],
                    "goal": "Implement new feature"
                },
                "tags": ["plan_generated", "orchestrator_output"],
                "agent_id": "ORCHESTRATOR",
                "loop_id": "loop_12345",
                "timestamp": "2025-04-24T20:40:00Z"
            }
        }


class MemoryRecallResponse(BaseModel):
    """Response schema for memory recall."""
    query: str = Field(..., description="Original query string")
    method: RecallMethod = Field(..., description="Method used for memory recall")
    total_results: int = Field(..., description="Total number of results found")
    returned_results: int = Field(..., description="Number of results returned in this response")
    results: List[MemoryEntry] = Field(..., description="Memory entries found")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the response"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "plan_generated",
                "method": "tag",
                "total_results": 125,
                "returned_results": 10,
                "results": [
                    {
                        "memory_id": "mem_12345",
                        "content": {
                            "plan_id": "plan_456",
                            "steps": [
                                "Analyze requirements",
                                "Design solution",
                                "Implement code",
                                "Test implementation",
                                "Deploy to production"
                            ],
                            "goal": "Implement new feature"
                        },
                        "tags": ["plan_generated", "orchestrator_output"],
                        "agent_id": "ORCHESTRATOR",
                        "loop_id": "loop_12345",
                        "timestamp": "2025-04-24T20:40:00Z"
                    }
                ],
                "timestamp": "2025-04-24T20:48:45Z",
                "version": "1.0.0"
            }
        }


class MemoryRecallError(BaseModel):
    """Error response schema for memory recall."""
    message: str = Field(..., description="Error message")
    query: Optional[str] = Field(None, description="Original query string if available")
    method: Optional[RecallMethod] = Field(None, description="Method used for memory recall if available")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Failed to recall memory: Invalid query format",
                "query": "plan_generated",
                "method": "tag",
                "timestamp": "2025-04-24T20:48:45Z",
                "version": "1.0.0"
            }
        }
