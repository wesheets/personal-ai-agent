"""
Train Routes

This module defines the FastAPI routes for model training operations.
"""

from fastapi import APIRouter, HTTPException, Body, Query, Path
from typing import Dict, Any, Optional

from app.modules.train import train_model, get_training_status
from app.schemas.train_schema import (
    TrainRequest,
    TrainResponse,
    TrainError,
    TrainStatusRequest,
    TrainStatusResponse,
    TrainingModel
)

# Create router
router = APIRouter(
    prefix="/api/train",
    tags=["train"],
    responses={404: {"description": "Not found"}},
)

@router.post("", response_model=TrainResponse)
async def train_model_endpoint(request: TrainRequest = Body(...)):
    """
    Train a model based on the provided data and parameters.
    
    This endpoint initiates a training job for the specified model type and data.
    
    Args:
        request: Training request
        
    Returns:
        Training response with model ID and initial status
    """
    try:
        result = train_model(request.dict())
        
        # Check if the result is an error
        if "message" in result:
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )
        
        return result
    except Exception as e:
        error_response = TrainError(
            message=f"Error training model: {str(e)}",
            model_type=request.model_type,
            model_name=request.model_name
        )
        return error_response

@router.get("/status/{model_id}", response_model=TrainStatusResponse)
async def get_training_status_endpoint(
    model_id: str = Path(..., description="Unique identifier for the model")
):
    """
    Get the status of a training job.
    
    This endpoint returns the current status, progress, and metrics of a training job.
    
    Args:
        model_id: Unique identifier for the model
        
    Returns:
        Training status response
    """
    try:
        request_data = {"model_id": model_id}
        result = get_training_status(request_data)
        
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
            detail=f"Error getting training status: {str(e)}"
        )

@router.post("/status", response_model=TrainStatusResponse)
async def check_training_status_endpoint(request: TrainStatusRequest = Body(...)):
    """
    Check the status of a training job using POST.
    
    This endpoint returns the current status, progress, and metrics of a training job.
    
    Args:
        request: Training status request
        
    Returns:
        Training status response
    """
    try:
        result = get_training_status(request.dict())
        
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
        error_response = TrainError(
            message=f"Error checking training status: {str(e)}"
        )
        return error_response
