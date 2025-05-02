"""
Memory Schema Module

This module defines the schema models for memory API operations in the application.

Includes:
- MemoryAddRequest model for adding new memory entries
- MemoryAddResponse model for add operation responses
- MemorySearchRequest model for searching memory entries
- MemorySearchResponse model for search operation responses
- MemoryEntry model for individual memory entries
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class MemoryEntry(BaseModel):
    """Schema for a memory entry."""
    memory_id: str = Field(..., description="Unique identifier for the memory entry")
    content: str = Field(..., description="Content of the memory entry")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadata associated with the memory entry")
    tags: List[str] = Field(default=[], description="Tags associated with the memory entry")
    agent_id: Optional[str] = Field(None, description="Agent ID associated with the memory entry")
    project_id: str = Field(..., description="Project ID associated with the memory entry")
    timestamp: str = Field(..., description="ISO timestamp when the memory was created")
    
    class Config:
        schema_extra = {
            "example": {
                "memory_id": "mem_12345",
                "content": "This is a sample memory content for testing purposes.",
                "metadata": {
                    "source": "user_input",
                    "importance": "high"
                },
                "tags": ["test", "memory", "sample"],
                "agent_id": "test_agent",
                "project_id": "test_project",
                "timestamp": "2025-04-24T20:40:00Z"
            }
        }


class MemoryAddRequest(BaseModel):
    """Request schema for adding a memory entry."""
    project_id: str = Field(..., description="Project ID to associate with the memory")
    content: str = Field(..., description="Content of the memory entry")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadata to associate with the memory")
    tags: List[str] = Field(default=[], description="Tags to associate with the memory")
    agent_id: Optional[str] = Field(None, description="Agent ID to associate with the memory")
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('content must not be empty')
        return v
    
    @validator('project_id')
    def project_id_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('project_id must not be empty')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "test_project",
                "content": "This is a sample memory content for testing purposes.",
                "metadata": {
                    "source": "user_input",
                    "importance": "high"
                },
                "tags": ["test", "memory", "sample"],
                "agent_id": "test_agent"
            }
        }


class MemoryAddResponse(BaseModel):
    """Response schema for adding a memory entry."""
    status: str = Field(..., description="Status of the operation (success or error)")
    message: str = Field(..., description="Message describing the result of the operation")
    memory_id: Optional[str] = Field(None, description="Unique identifier for the added memory entry")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the response"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Memory added successfully",
                "memory_id": "mem_12345",
                "timestamp": "2025-04-24T20:40:00Z"
            }
        }


class MemorySearchRequest(BaseModel):
    """Request schema for searching memory entries."""
    project_id: str = Field(..., description="Project ID to search within")
    query: str = Field(..., description="Query string for semantic search")
    limit: int = Field(10, description="Maximum number of results to return")
    tags: Optional[List[str]] = Field(None, description="Filter results by tags")
    agent_id: Optional[str] = Field(None, description="Filter results by agent ID")
    threshold: float = Field(0.7, description="Similarity threshold for results (0.0 to 1.0)")
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('query must not be empty')
        return v
    
    @validator('project_id')
    def project_id_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('project_id must not be empty')
        return v
    
    @validator('limit')
    def limit_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('limit must be positive')
        if v > 100:
            return 100  # Cap at 100 for performance
        return v
    
    @validator('threshold')
    def threshold_must_be_valid(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('threshold must be between 0.0 and 1.0')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": "test_project",
                "query": "sample memory content",
                "limit": 5,
                "tags": ["test", "memory"],
                "agent_id": "test_agent",
                "threshold": 0.7
            }
        }


class MemorySearchResponse(BaseModel):
    """Response schema for searching memory entries."""
    status: str = Field(..., description="Status of the operation (success or error)")
    message: str = Field(..., description="Message describing the result of the operation")
    results: List[MemoryEntry] = Field(default=[], description="Memory entries found")
    count: int = Field(..., description="Number of results returned")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the response"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Memory search completed successfully",
                "results": [
                    {
                        "memory_id": "mem_12345",
                        "content": "This is a sample memory content for testing purposes.",
                        "metadata": {
                            "source": "user_input",
                            "importance": "high"
                        },
                        "tags": ["test", "memory", "sample"],
                        "agent_id": "test_agent",
                        "project_id": "test_project",
                        "timestamp": "2025-04-24T20:40:00Z"
                    }
                ],
                "count": 1,
                "timestamp": "2025-04-24T20:48:45Z"
            }
        }
