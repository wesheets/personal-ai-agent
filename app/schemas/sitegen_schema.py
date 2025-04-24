"""
SITEGEN Agent Schema Definitions

This module defines the schemas for SITEGEN agent requests and responses.
The SITEGEN agent is responsible for planning commercial sites, analyzing zoning requirements,
creating optimal layouts, and evaluating market-fit for construction projects.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SiteGenTaskRequest(BaseModel):
    """
    Schema for SITEGEN agent task request.
    """
    task: str = Field(..., description="Task description or query about site planning")
    project_id: Optional[str] = Field(None, description="Project identifier if applicable")
    site_parameters: Optional[Dict[str, Any]] = Field(
        default={},
        description="Parameters for site generation (e.g., dimensions, zoning, requirements)"
    )
    tools: Optional[List[str]] = Field(
        default=["analyze_zoning", "create_layout", "evaluate_market_fit"],
        description="List of tools to use for the site generation"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "task": "Create a site plan for a commercial retail space with 5000 sq ft",
                "project_id": "proj_123",
                "site_parameters": {
                    "dimensions": {"width": 100, "depth": 50},
                    "zoning": "commercial",
                    "parking_required": True
                },
                "tools": ["analyze_zoning", "create_layout", "evaluate_market_fit"]
            }
        }

class SiteLayout(BaseModel):
    """
    Schema for a site layout.
    """
    layout_type: str = Field(..., description="Type of layout (e.g., retail, office, mixed-use)")
    dimensions: Dict[str, float] = Field(..., description="Dimensions of the site")
    zones: List[Dict[str, Any]] = Field(..., description="Different zones within the layout")
    features: List[str] = Field(..., description="Features included in the layout")
    
    class Config:
        schema_extra = {
            "example": {
                "layout_type": "retail",
                "dimensions": {"width": 100, "depth": 50, "height": 20},
                "zones": [
                    {"name": "retail_area", "size": 3000, "position": "front"},
                    {"name": "storage", "size": 1000, "position": "back"},
                    {"name": "parking", "size": 1000, "position": "side"}
                ],
                "features": ["large windows", "loading dock", "customer parking"]
            }
        }

class SiteGenTaskResult(BaseModel):
    """
    Schema for SITEGEN agent task result.
    """
    status: str = Field(..., description="Status of the task (success, error)")
    message: str = Field(..., description="Message describing the result")
    task: str = Field(..., description="Task that was performed")
    project_id: Optional[str] = Field(None, description="Project identifier if applicable")
    analysis: Optional[str] = Field(None, description="Analysis of the site requirements")
    layout: Optional[SiteLayout] = Field(None, description="Generated site layout if applicable")
    market_fit: Optional[Dict[str, Any]] = Field(None, description="Market fit evaluation if applicable")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations for the site")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the task"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "message": "Site plan created successfully",
                "task": "Create a site plan for a commercial retail space with 5000 sq ft",
                "project_id": "proj_123",
                "analysis": "The site is zoned for commercial use and meets local requirements for retail development.",
                "layout": {
                    "layout_type": "retail",
                    "dimensions": {"width": 100, "depth": 50, "height": 20},
                    "zones": [
                        {"name": "retail_area", "size": 3000, "position": "front"},
                        {"name": "storage", "size": 1000, "position": "back"},
                        {"name": "parking", "size": 1000, "position": "side"}
                    ],
                    "features": ["large windows", "loading dock", "customer parking"]
                },
                "market_fit": {
                    "score": 0.85,
                    "strengths": ["good visibility", "adequate parking"],
                    "weaknesses": ["limited storage"]
                },
                "recommendations": [
                    "Consider expanding storage area",
                    "Add more customer parking spaces",
                    "Improve loading dock accessibility"
                ],
                "timestamp": "2025-04-24T18:48:28.123456"
            }
        }

class SiteGenErrorResult(BaseModel):
    """
    Schema for SITEGEN agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    task: Optional[str] = Field(None, description="Task that was attempted")
    project_id: Optional[str] = Field(None, description="Project identifier if applicable")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
