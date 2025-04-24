"""
Fix Routes

This module defines the FastAPI routes for applying fixes to various system components.
"""

from fastapi import APIRouter, HTTPException, Body, Query, Path
from typing import Dict, Any, Optional

from app.modules.fix import apply_fix, get_fix_status, rollback_fix
from app.schemas.fix_schema import (
    FixRequest,
    FixResponse,
    FixError,
    FixStatusRequest,
    FixStatusResponse,
    FixRollbackRequest,
    FixRollbackResponse,
    FixType
)

# Create router
router = APIRouter(
    prefix="/api/fix",
    tags=["fix"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=FixResponse)
async def apply_fix_endpoint(request: FixRequest = Body(...)):
    """
    Apply a fix based on the provided parameters.
    
    This endpoint initiates a fix for the specified target and type.
    
    Args:
        request: Fix request
        
    Returns:
        Fix response with fix ID and status
    """
    try:
        result = apply_fix(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = FixError(
            message=f"Error applying fix: {str(e)}",
            fix_type=request.fix_type,
            target_id=request.target_id
        )
        return error_response

@router.get("/status/{fix_id}", response_model=FixStatusResponse)
async def get_fix_status_endpoint(
    fix_id: str = Path(..., description="Unique identifier for the fix")
):
    """
    Get the status of a fix.
    
    This endpoint returns the current status, progress, and details of a fix.
    
    Args:
        fix_id: Unique identifier for the fix
        
    Returns:
        Fix status response
    """
    try:
        request_data = {"fix_id": fix_id}
        result = get_fix_status(request_data)
        
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
            detail=f"Error getting fix status: {str(e)}"
        )

@router.post("/status", response_model=FixStatusResponse)
async def check_fix_status_endpoint(request: FixStatusRequest = Body(...)):
    """
    Check the status of a fix using POST.
    
    This endpoint returns the current status, progress, and details of a fix.
    
    Args:
        request: Fix status request
        
    Returns:
        Fix status response
    """
    try:
        result = get_fix_status(request.dict())
        
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
        error_response = FixError(
            message=f"Error checking fix status: {str(e)}"
        )
        return error_response

@router.post("/rollback", response_model=FixRollbackResponse)
async def rollback_fix_endpoint(request: FixRollbackRequest = Body(...)):
    """
    Roll back a fix.
    
    This endpoint rolls back a previously applied fix.
    
    Args:
        request: Fix rollback request
        
    Returns:
        Fix rollback response
    """
    try:
        result = rollback_fix(request.dict())
        
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
        error_response = FixError(
            message=f"Error rolling back fix: {str(e)}"
        )
        return error_response
