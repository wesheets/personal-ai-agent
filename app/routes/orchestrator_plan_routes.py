"""
Orchestrator Plan Route with CRITIC Rejection Integration

This module extends the orchestrator routes with CRITIC rejection handling,
enabling the system to block auto-delegation when loop rejections exist.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import traceback

# Import orchestrator critic integration
try:
    from app.modules.orchestrator_critic_integration import check_for_rejections, handle_rejection
    critic_integration_available = True
except ImportError:
    critic_integration_available = False
    logging.warning("⚠️ CRITIC integration not available, orchestrator will not check for rejections")

# Import project state
try:
    from app.modules.project_state import get_project_state
    project_state_available = True
except ImportError:
    project_state_available = False
    logging.warning("⚠️ Project state not available, using basic state management")

# Import manifest manager if available
try:
    from app.utils.manifest_manager import register_route
    manifest_available = True
except ImportError:
    manifest_available = False
    logging.warning("⚠️ Manifest manager not available, routes will not be registered")

# Configure logging
logger = logging.getLogger("app.routes.orchestrator_plan_routes")

# Create router
router = APIRouter(tags=["orchestrator"])

# Register routes with manifest if available
if manifest_available:
    try:
        register_route("/orchestrator/plan", "POST", "OrchestratorPlanRequest", "active")
        logging.info("✅ Orchestrator plan route registered with manifest")
    except Exception as e:
        logging.error(f"❌ Failed to register orchestrator plan route with manifest: {str(e)}")

class OrchestratorPlanRequest(BaseModel):
    """
    Schema for orchestrator plan requests.
    
    This schema defines the structure of requests to the orchestrator
    for planning the next steps in a loop.
    """
    loop_id: str = Field(..., description="Unique identifier for the loop")
    current_agent: Optional[str] = Field(None, description="Current agent in the loop")
    force_proceed: bool = Field(False, description="Whether to force proceeding despite rejections")
    
    class Config:
        schema_extra = {
            "example": {
                "loop_id": "loop_003",
                "current_agent": "hal",
                "force_proceed": False
            }
        }

@router.post("/orchestrator/plan")
async def plan_next_steps(request: OrchestratorPlanRequest):
    """
    Plan the next steps in a loop, checking for CRITIC rejections first.
    
    This endpoint checks if there are any CRITIC rejections for the loop
    and blocks auto-delegation if rejections exist, unless force_proceed is True.
    """
    try:
        # Check for CRITIC rejections if integration is available
        if critic_integration_available:
            rejection = await check_for_rejections(request.loop_id)
            
            if rejection and not request.force_proceed:
                # Rejection found and not forcing proceed - block delegation
                logger.warning(f"⚠️ Blocking auto-delegation for loop {request.loop_id} due to CRITIC rejection")
                
                # Handle the rejection
                response = await handle_rejection(request.loop_id, rejection)
                return response
        
        # No rejections or forcing proceed - continue with normal planning
        logger.info(f"✅ No rejections found for loop {request.loop_id}, proceeding with planning")
        
        # Get project state if available
        if project_state_available:
            project_state = await get_project_state(request.loop_id)
            
            # Determine next agent based on current agent
            current_agent = request.current_agent or project_state.get("last_agent")
            
            if current_agent == "hal":
                next_agent = "critic"
                next_task = "Review HAL output"
            elif current_agent == "critic":
                next_agent = "orchestrator"
                next_task = "Plan next steps"
            elif current_agent == "orchestrator":
                next_agent = "hal"
                next_task = "Generate code"
            else:
                next_agent = "hal"
                next_task = "Start loop"
            
            return {
                "status": "success",
                "loop_id": request.loop_id,
                "next_agent": next_agent,
                "next_task": next_task,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            # Fallback planning logic
            return {
                "status": "success",
                "loop_id": request.loop_id,
                "next_agent": "hal",
                "next_task": "Continue loop",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    except Exception as e:
        logger.error(f"❌ Error planning next steps: {str(e)}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error planning next steps: {str(e)}",
            "loop_id": request.loop_id,
            "timestamp": datetime.utcnow().isoformat()
        }
