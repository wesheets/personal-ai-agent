"""
Export Schema

This module defines the schemas for data export endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class ExportFormat(str, Enum):
    """Export formats supported by the system."""
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    XML = "xml"


class ExportType(str, Enum):
    """Types of data that can be exported."""
    MEMORY = "memory"
    LOOP = "loop"
    AGENT = "agent"
    MODEL = "model"
    PROJECT = "project"
    REPORT = "report"
    CUSTOM = "custom"


class ExportRequest(BaseModel):
    """Request schema for data export."""
    export_type: ExportType = Field(
        ..., 
        description="Type of data to export"
    )
    export_id: str = Field(
        ..., 
        description="Identifier for the data to export (e.g., loop_id, agent_id)"
    )
    format: ExportFormat = Field(
        ExportFormat.JSON, 
        description="Format for the exported data"
    )
    include_metadata: bool = Field(
        True, 
        description="Whether to include metadata in the export"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Filters to apply to the exported data"
    )
    start_date: Optional[str] = Field(
        None, 
        description="Start date for time-based filtering (ISO format)"
    )
    end_date: Optional[str] = Field(
        None, 
        description="End date for time-based filtering (ISO format)"
    )
    max_items: Optional[int] = Field(
        None, 
        description="Maximum number of items to export"
    )
    agent_id: Optional[str] = Field(
        None, 
        description="Agent ID requesting the export"
    )
    loop_id: Optional[str] = Field(
        None, 
        description="Loop ID associated with the export"
    )
    
    @validator('export_id')
    def export_id_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('export_id must not be empty')
        return v
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('date must be in ISO format (YYYY-MM-DDTHH:MM:SSZ)')
        return v
    
    @validator('max_items')
    def max_items_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('max_items must be positive')
        if v is not None and v > 10000:
            return 10000  # Cap at 10000 for performance
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "export_type": "loop",
                "export_id": "loop_12345",
                "format": "json",
                "include_metadata": True,
                "filters": {
                    "status": "completed",
                    "tags": ["important", "production"]
                },
                "start_date": "2025-01-01T00:00:00Z",
                "end_date": "2025-04-24T00:00:00Z",
                "max_items": 1000,
                "agent_id": "EXPORTER",
                "loop_id": "loop_12345"
            }
        }


class ExportResponse(BaseModel):
    """Response schema for data export."""
    export_id: str = Field(..., description="Unique identifier for the export")
    export_type: ExportType = Field(..., description="Type of data exported")
    format: ExportFormat = Field(..., description="Format of the exported data")
    file_name: str = Field(..., description="Name of the exported file")
    file_size: int = Field(..., description="Size of the exported file in bytes")
    download_url: str = Field(..., description="URL to download the exported file")
    expires_at: str = Field(..., description="Expiration time of the download URL (ISO format)")
    items_exported: int = Field(..., description="Number of items exported")
    include_metadata: bool = Field(..., description="Whether metadata was included in the export")
    agent_id: Optional[str] = Field(None, description="Agent ID that requested the export")
    loop_id: Optional[str] = Field(None, description="Loop ID associated with the export")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the export"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "export_id": "export_12345",
                "export_type": "loop",
                "format": "json",
                "file_name": "loop_12345_export.json",
                "file_size": 15360,
                "download_url": "https://api.example.com/downloads/export_12345",
                "expires_at": "2025-04-25T21:00:00Z",
                "items_exported": 42,
                "include_metadata": True,
                "agent_id": "EXPORTER",
                "loop_id": "loop_12345",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class ExportError(BaseModel):
    """Error response schema for data export."""
    message: str = Field(..., description="Error message")
    export_type: Optional[ExportType] = Field(None, description="Requested export type if available")
    export_id: Optional[str] = Field(None, description="Requested export ID if available")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Failed to export data: Resource not found",
                "export_type": "loop",
                "export_id": "loop_12345",
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }


class ExportStatusRequest(BaseModel):
    """Request schema for checking export status."""
    export_id: str = Field(..., description="Unique identifier for the export")
    
    class Config:
        schema_extra = {
            "example": {
                "export_id": "export_12345"
            }
        }


class ExportStatusResponse(BaseModel):
    """Response schema for export status."""
    export_id: str = Field(..., description="Unique identifier for the export")
    status: str = Field(..., description="Export status (e.g., 'queued', 'in_progress', 'completed', 'failed')")
    progress: Optional[float] = Field(None, description="Export progress as a percentage")
    items_processed: Optional[int] = Field(None, description="Number of items processed so far")
    total_items: Optional[int] = Field(None, description="Total number of items to process")
    estimated_completion: Optional[str] = Field(None, description="Estimated completion time (ISO format)")
    error_message: Optional[str] = Field(None, description="Error message if export failed")
    download_url: Optional[str] = Field(None, description="URL to download the exported file if completed")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the status check"
    )
    version: str = Field("1.0.0", description="Schema version")
    
    class Config:
        schema_extra = {
            "example": {
                "export_id": "export_12345",
                "status": "in_progress",
                "progress": 65.0,
                "items_processed": 273,
                "total_items": 420,
                "estimated_completion": "2025-04-24T21:05:00Z",
                "error_message": None,
                "download_url": None,
                "timestamp": "2025-04-24T21:00:00Z",
                "version": "1.0.0"
            }
        }
