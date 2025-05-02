"""
Memory Embed Schema

This module defines the schemas for memory embedding endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class EmbeddingModel(str, Enum):
    """Models available for embedding generation."""
    DEFAULT = "default"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    MULTILINGUAL = "multilingual"


class EmbeddingDimension(int, Enum):
    """Dimensions available for embeddings."""
    D_128 = 128
    D_256 = 256
    D_512 = 512
    D_768 = 768
    D_1024 = 1024
    D_1536 = 1536


class MemoryEmbedRequest(BaseModel):
    """Request schema for memory embedding."""
    content: Union[str, Dict[str, Any]] = Field(
        ..., 
        description="Content to embed (string or structured data)"
    )
    model: EmbeddingModel = Field(
        EmbeddingModel.DEFAULT, 
        description="Model to use for embedding generation"
    )
    dimension: Optional[EmbeddingDimension] = Field(
        None, 
        description="Dimension of the embedding (if None, uses model default)"
    )
    tags: List[str] = Field(
        [], 
        description="Tags to associate with the embedded memory"
    )
    agent_id: Optional[str] = Field(
        None, 
        description="Agent ID to associate with the embedded memory"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Loop ID to associate with the embedded memory"
    )
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError('content must not be empty')
        if isinstance(v, dict) and not v:
            raise ValueError('content must not be empty')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "content": "This is a sample text to embed in the vector database for semantic search.",
                "model": "default",
                "dimension": 512,
                "tags": ["sample", "text", "embedding"],
                "agent_id": "MEMORY",
                "loop_id": "loop_12345"
            }
        }


class MemoryEmbedResponse(BaseModel):
    """Response schema for memory embedding."""
    memory_id: str = Field(..., description="Unique identifier for the embedded memory")
    embedding_size: int = Field(..., description="Size of the generated embedding")
    model_used: EmbeddingModel = Field(..., description="Model used for embedding generation")
    tags: List[str] = Field(..., description="Tags associated with the embedded memory")
    agent_id: Optional[str] = Field(None, description="Agent ID associated with the embedded memory")
    loop_id: Optional[str] = Field(None, description="Loop ID associated with the embedded memory")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the embedding"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "memory_id": "mem_embed_12345",
                "embedding_size": 512,
                "model_used": "default",
                "tags": ["sample", "text", "embedding"],
                "agent_id": "MEMORY",
                "loop_id": "loop_12345",
                "timestamp": "2025-04-24T20:51:30Z",
                "version": "1.0.0"
            }
        }


class MemoryEmbedError(BaseModel):
    """Error response schema for memory embedding."""
    message: str = Field(..., description="Error message")
    model: Optional[EmbeddingModel] = Field(None, description="Model requested if available")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Failed to embed memory: Content too large",
                "model": "default",
                "timestamp": "2025-04-24T20:51:30Z",
                "version": "1.0.0"
            }
        }


class MemoryEmbedBatchRequest(BaseModel):
    """Request schema for batch memory embedding."""
    items: List[MemoryEmbedRequest] = Field(
        ..., 
        description="List of items to embed"
    )
    
    @validator('items')
    def items_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('items must not be empty')
        if len(v) > 100:
            raise ValueError('maximum 100 items allowed per batch')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "content": "First sample text to embed.",
                        "model": "default",
                        "dimension": 512,
                        "tags": ["sample", "text", "embedding"],
                        "agent_id": "MEMORY",
                        "loop_id": "loop_12345"
                    },
                    {
                        "content": "Second sample text to embed.",
                        "model": "default",
                        "dimension": 512,
                        "tags": ["sample", "text", "embedding"],
                        "agent_id": "MEMORY",
                        "loop_id": "loop_12345"
                    }
                ]
            }
        }


class MemoryEmbedBatchResponse(BaseModel):
    """Response schema for batch memory embedding."""
    results: List[MemoryEmbedResponse] = Field(
        ..., 
        description="List of embedding results"
    )
    errors: List[Dict[str, Any]] = Field(
        [], 
        description="List of errors encountered during batch processing"
    )
    total_items: int = Field(..., description="Total number of items in the batch")
    successful_items: int = Field(..., description="Number of items successfully embedded")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the response"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "results": [
                    {
                        "memory_id": "mem_embed_12345",
                        "embedding_size": 512,
                        "model_used": "default",
                        "tags": ["sample", "text", "embedding"],
                        "agent_id": "MEMORY",
                        "loop_id": "loop_12345",
                        "timestamp": "2025-04-24T20:51:30Z",
                        "version": "1.0.0"
                    },
                    {
                        "memory_id": "mem_embed_12346",
                        "embedding_size": 512,
                        "model_used": "default",
                        "tags": ["sample", "text", "embedding"],
                        "agent_id": "MEMORY",
                        "loop_id": "loop_12345",
                        "timestamp": "2025-04-24T20:51:30Z",
                        "version": "1.0.0"
                    }
                ],
                "errors": [],
                "total_items": 2,
                "successful_items": 2,
                "timestamp": "2025-04-24T20:51:30Z",
                "version": "1.0.0"
            }
        }
