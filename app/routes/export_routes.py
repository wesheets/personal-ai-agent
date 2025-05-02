"""
Export Routes

This module defines the FastAPI routes for data export operations.
"""

from fastapi import APIRouter, HTTPException, Body, Query, Path
from typing import Dict, Any, Optional

from app.modules.export import export_data, get_export_status
from app.schemas.export_schema import (
    ExportRequest,
    ExportResponse,
    ExportError,
    ExportStatusRequest,
    ExportStatusResponse,
    ExportFormat,
    ExportType
)

# Create router
router = APIRouter(
    prefix="/api/export",
    tags=["export"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=ExportResponse)
async def export_data_endpoint(request: ExportRequest = Body(...)):
    """
    Export data based on the provided parameters.
    
    This endpoint initiates an export job for the specified data type and format.
    
    Args:
        request: Export request
        
    Returns:
        Export response with export ID and initial status
    """
    try:
        result = export_data(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = ExportError(
            message=f"Error exporting data: {str(e)}",
            export_type=request.export_type,
            export_id=request.export_id
        )
        return error_response

@router.get("/status/{export_id}", response_model=ExportStatusResponse)
async def get_export_status_endpoint(
    export_id: str = Path(..., description="Unique identifier for the export")
):
    """
    Get the status of an export job.
    
    This endpoint returns the current status, progress, and download URL of an export job.
    
    Args:
        export_id: Unique identifier for the export
        
    Returns:
        Export status response
    """
    try:
        request_data = {"export_id": export_id}
        result = get_export_status(request_data)
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=404 if "not found" in result["message"].lower() else 400,
                detail=result["message"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting export status: {str(e)}"
        )

@router.post("/status", response_model=ExportStatusResponse)
async def check_export_status_endpoint(request: ExportStatusRequest = Body(...)):
    """
    Check the status of an export job using POST.
    
    This endpoint returns the current status, progress, and download URL of an export job.
    
    Args:
        request: Export status request
        
    Returns:
        Export status response
    """
    try:
        result = get_export_status(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=404 if "not found" in result["message"].lower() else 400,
                detail=result["message"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_response = ExportError(
            message=f"Error checking export status: {str(e)}"
        )
        return error_response
