"""
Plan Routes Module

This module defines the API routes for plan operations.

memory_tag: phase3.0_sprint2_reflection_drift_plan_activation
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import traceback

# Import manifest manager if available
try:
    from app.utils.manifest_manager import register_route
    manifest_available = True
except ImportError:
    manifest_available = False
    logging.warning("⚠️ Manifest manager not available, routes will not be registered")

# Configure logging
logger = logging.getLogger("app.routes.plan_routes")

# Create router
router = APIRouter(tags=["plan"])

# Register routes with manifest if available
if manifest_available:
    try:
        register_route("/plan/create", "POST", "PlanCreateRequest", "active")
        register_route("/plan/{plan_id}", "GET", "PlanGetRequest", "active")
        register_route("/plan/update", "PUT", "PlanUpdateRequest", "active")
        logging.info("✅ Plan routes registered with manifest")
    except Exception as e:
        logging.error(f"❌ Failed to register plan routes with manifest: {str(e)}")

class PlanCreateRequest(BaseModel):
    """
    Schema for plan creation requests.
    
    This schema defines the structure of requests to create a new plan.
    
    memory_tag: phase3.0_sprint2_reflection_drift_plan_activation
    """
    title: str = Field(..., description="Title of the plan")
    description: Optional[str] = Field(None, description="Description of the plan")
    steps: List[str] = Field(..., description="List of steps in the plan")
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Project Implementation Plan",
                "description": "A plan for implementing the project",
                "steps": ["Research", "Design", "Implementation", "Testing", "Deployment"]
            }
        }

class PlanGetRequest(BaseModel):
    """
    Schema for plan retrieval requests.
    
    This schema defines the structure of requests to retrieve a plan.
    
    memory_tag: phase3.0_sprint2_reflection_drift_plan_activation
    """
    plan_id: str = Field(..., description="Unique identifier for the plan")
    
    class Config:
        schema_extra = {
            "example": {
                "plan_id": "plan_123"
            }
        }

class PlanUpdateRequest(BaseModel):
    """
    Schema for plan update requests.
    
    This schema defines the structure of requests to update a plan.
    """
    plan_id: str = Field(..., description="Unique identifier for the plan")
    title: Optional[str] = Field(None, description="Updated title of the plan")
    description: Optional[str] = Field(None, description="Updated description of the plan")
    steps: Optional[List[str]] = Field(None, description="Updated list of steps in the plan")
    
    class Config:
        schema_extra = {
            "example": {
                "plan_id": "plan_123",
                "title": "Updated Project Implementation Plan",
                "steps": ["Research", "Design", "Implementation", "Testing", "Deployment", "Maintenance"]
            }
        }

@router.post("/create")
async def create_plan(request: PlanCreateRequest):
    """
    Create a new plan.
    
    This endpoint creates a new plan with the specified title, description, and steps.
    
    memory_tag: phase3.0_sprint2_reflection_drift_plan_activation
    """
    try:
        # Log the request
        logger.info(f"Creating plan: {request.title}")
        
        # Create a new plan (placeholder implementation)
        plan_id = f"plan_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Return the created plan
        return {
            "status": "success",
            "message": "Plan created successfully",
            "plan_id": plan_id,
            "title": request.title,
            "description": request.description,
            "steps": request.steps,
            "created_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Error creating plan: {str(e)}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Error creating plan: {str(e)}"
        )

@router.get("/{plan_id}")
async def get_plan(plan_id: str):
    """
    Get a plan by ID.
    
    This endpoint retrieves a plan with the specified ID.
    
    memory_tag: phase3.0_sprint2_reflection_drift_plan_activation
    """
    try:
        # Log the request
        logger.info(f"Getting plan: {plan_id}")
        
        # Get the plan (placeholder implementation)
        # In a real implementation, this would retrieve the plan from a database
        
        # Return a placeholder plan
        return {
            "status": "success",
            "plan_id": plan_id,
            "title": "Sample Plan",
            "description": "This is a sample plan",
            "steps": ["Step 1", "Step 2", "Step 3"],
            "created_at": "2025-04-28T00:00:00Z"
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting plan: {str(e)}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Error getting plan: {str(e)}"
        )

@router.put("/update")
async def update_plan(request: PlanUpdateRequest):
    """
    Update a plan.
    
    This endpoint updates a plan with the specified ID.
    """
    try:
        # Log the request
        logger.info(f"Updating plan: {request.plan_id}")
        
        # Update the plan (placeholder implementation)
        # In a real implementation, this would update the plan in a database
        
        # Return the updated plan
        return {
            "status": "success",
            "message": "Plan updated successfully",
            "plan_id": request.plan_id,
            "title": request.title or "Sample Plan",
            "description": request.description or "This is a sample plan",
            "steps": request.steps or ["Step 1", "Step 2", "Step 3"],
            "updated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Error updating plan: {str(e)}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Error updating plan: {str(e)}"
        )
