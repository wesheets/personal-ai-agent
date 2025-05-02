# memory_tag: phase4.0_sprint1_cognitive_reflection_chain_activation

"""
Plan Routes Module

This module defines the API routes for plan operations, including creation,
retrieval, update, execution, status checking, and chaining.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import traceback
import uuid

# Import plan chain schemas and module
from app.schemas.plan_chain_schemas import PlanChainRequest, PlanChainResponse, PlanStep
from app.modules.plan_chainer import generate_plan_chain

# Import plan execution schemas and module
from app.schemas.plan_execution_schemas import PlanExecutionRequest, PlanExecutionResponse
from app.modules.plan_executor import execute_plan as execute_plan_module

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
        register_route("/plan/execute", "POST", "PlanExecutionRequest", "active")
        register_route("/plan/status/{execution_id}", "GET", "PlanStatusRequest", "active")
        register_route("/plan/chain", "POST", "PlanChainRequest", "active")
        logging.info("✅ Plan routes registered with manifest")
    except Exception as e:
        logging.error(f"❌ Failed to register plan routes with manifest: {str(e)}")

class PlanCreateRequest(BaseModel):
    """
    Schema for plan creation requests.
    
    This schema defines the structure of requests to create a new plan.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
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
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
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
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
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

# Note: PlanExecuteRequest and PlanExecutionResponse are now imported from app.schemas.plan_execution_schemas

class PlanExecutionStatusResponse(BaseModel):
    """
    Schema for plan execution status responses.
    
    This schema defines the structure of responses from plan execution status operations.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
    """
    execution_id: str = Field(..., description="Unique identifier for the execution")
    plan_id: str = Field(..., description="Identifier of the executed plan")
    status: str = Field(..., description="Execution status")
    progress: float = Field(..., description="Execution progress (0-100)")
    current_step: Optional[str] = Field(None, description="Current execution step")
    message: str = Field(..., description="Status message")
    started_at: str = Field(..., description="Execution start timestamp")
    updated_at: str = Field(..., description="Status update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "execution_id": "exec_abc123",
                "plan_id": "plan_123",
                "status": "in_progress",
                "progress": 45.5,
                "current_step": "Implementation",
                "message": "Executing step 3 of 5",
                "started_at": "2025-04-28T07:54:00Z",
                "updated_at": "2025-04-28T08:15:30Z"
            }
        }

@router.post("/create")
async def create_plan(request: PlanCreateRequest):
    """
    Create a new plan.
    
    This endpoint creates a new plan with the specified title, description, and steps.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
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
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
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
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
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

@router.post("/execute", response_model=PlanExecutionResponse)
async def execute_plan_endpoint(request: PlanExecutionRequest):
    """
    Execute a plan.
    
    This endpoint initiates the execution of a plan with the specified parameters
    using the PlanExecutor module. Returns a unique execution_id that can be
    used to retrieve the execution status.
    
    memory_tag: phase4.0_sprint1_cognitive_reflection_chain_activation
    """
    try:
        # Log the request
        logger.info(f"Executing plan: {request.plan_id}")
        
        # Call the plan executor module
        response = await execute_plan_module(request)
        
        return response
    
    except Exception as e:
        logger.error(f"❌ Error executing plan: {str(e)}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Error executing plan: {str(e)}"
        )

@router.get("/status/{execution_id}", response_model=PlanExecutionStatusResponse)
async def get_execution_status(execution_id: str):
    """
    Retrieve plan execution status.
    
    This endpoint retrieves the status of a previously initiated plan execution.
    
    memory_tag: phase3.0_sprint4_cognitive_reflection_plan_chaining
    """
    try:
        # Log the request
        logger.info(f"Getting execution status: {execution_id}")
        
        # In a real implementation, this would retrieve execution status from storage
        # For now, return a mock response
        
        # Extract plan_id from execution_id (in a real implementation, this would be retrieved from storage)
        plan_id = f"plan_{execution_id.split('_')[1][:6]}"
        return PlanExecutionStatusResponse(
            execution_id=execution_id,
            plan_id=plan_id,
            status="in_progress",
            progress=65.0,
            current_step="Testing",
            message="Executing step 4 of 5",
            started_at=(datetime.utcnow().replace(minute=datetime.utcnow().minute-30)).isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"❌ Error getting execution status: {str(e)}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Error getting execution status: {str(e)}"
        )


@router.post("/chain", response_model=PlanChainResponse)
async def create_plan_chain(request: PlanChainRequest):
    """
    Generate a plan chain based on reflection results.
    
    This endpoint creates a multi-step plan chain based on a reflection ID and optional goal.
    It uses the reflection results to generate a sequence of steps that can be executed to achieve the goal.
    
    memory_tag: phase3.0_sprint4_cognitive_reflection_plan_chaining
    """
    try:
        # Log the request
        logger.info(f"Generating plan chain for reflection ID: {request.reflection_id}")
        
        # Generate the plan chain using the plan_chainer module
        plan_chain = await generate_plan_chain(request)
        
        # Return the generated plan chain
        return plan_chain
    
    except Exception as e:
        logger.error(f"❌ Error generating plan chain: {str(e)}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Error generating plan chain: {str(e)}"
        )

