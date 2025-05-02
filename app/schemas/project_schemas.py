"""
Schema definitions for project endpoints.

This module contains Pydantic models for request and response schemas.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

# memory_tag: phase4.0_holistic_router_registry_sync

class TestRequest(BaseModel):
    """
    Schema for GET /test request.
    """
    query: Optional[Dict[str, Any]] = Field(default={}, description="Query parameters")

class TestResponse(BaseModel):
    """
    Schema for GET /test response.
    """
    status: str = Field(..., description="Status of the operation")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(default={}, description="Response data")

class StateRequest(BaseModel):
    """
    Schema for GET /state request.
    """
    query: Optional[Dict[str, Any]] = Field(default={}, description="Query parameters")

class StateResponse(BaseModel):
    """
    Schema for GET /state response.
    """
    status: str = Field(..., description="Status of the operation")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(default={}, description="Response data")

class StatusRequest(BaseModel):
    """
    Schema for GET /{project_id}/status request.
    """
    query: Optional[Dict[str, Any]] = Field(default={}, description="Query parameters")

class StatusResponse(BaseModel):
    """
    Schema for GET /{project_id}/status response.
    """
    status: str = Field(..., description="Status of the operation")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(default={}, description="Response data")

class StatusRequest(BaseModel):
    """
    Schema for GET /status request.
    """
    query: Optional[Dict[str, Any]] = Field(default={}, description="Query parameters")

class StatusResponse(BaseModel):
    """
    Schema for GET /status response.
    """
    status: str = Field(..., description="Status of the operation")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(default={}, description="Response data")

class StartRequest(BaseModel):
    """
    Schema for POST /start request.
    """
    query: Optional[Dict[str, Any]] = Field(default={}, description="Query parameters")

class StartResponse(BaseModel):
    """
    Schema for POST /start response.
    """
    status: str = Field(..., description="Status of the operation")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(default={}, description="Response data")

class StateRequest(BaseModel):
    """
    Schema for PATCH /state request.
    """
    query: Optional[Dict[str, Any]] = Field(default={}, description="Query parameters")

class StateResponse(BaseModel):
    """
    Schema for PATCH /state response.
    """
    status: str = Field(..., description="Status of the operation")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(default={}, description="Response data")
