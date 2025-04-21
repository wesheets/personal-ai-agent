"""
Orchestrator Routes Module

This module defines the orchestrator-related routes for the Promethios API.
It integrates the cognitive control layer to ensure all loops adhere to
core beliefs and operational thresholds.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging
from datetime import datetime

# Import the post_loop_summary_handler and rerun_decision_engine modules
from app.modules.post_loop_summary_handler import process_loop_reflection
from app.modules.rerun_decision_engine import evaluate_rerun_decision
from app.utils.persona_utils import get_current_persona

# Import cognitive control layer components
from app.modules.orchestrator_integration import (
    integrate_with_orchestrator,
    process_reflection_with_controls,
    determine_rerun_depth_with_controls
)
from app.modules.loop_validator import validate_loop
from app.modules.core_beliefs_integration import inject_belief_references

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["orchestrator"])

class LoopCompleteRequest(BaseModel):
    """Request model for loop-complete endpoint."""
    loop_id: str
    reflection_status: str
    orchestrator_persona: Optional[str] = None

class LoopValidateRequest(BaseModel):
    """Request model for loop-validate endpoint."""
    loop_id: str
    loop_data: Dict[str, Any]

@router.post("/orchestrator/loop-complete")
async def loop_complete(request: LoopCompleteRequest):
    """
    Handle post-execution signals and kick off system reflection.
    
    This endpoint is called when a loop execution is complete and triggers:
    - /run-critic
    - /pessimist-check
    - /ceo-review
    - /drift-summary
    
    It then processes the reflection results and decides whether to rerun the loop
    or finalize it based on alignment and drift scores.
    """
    logger.info(f"Processing loop-complete for loop {request.loop_id}")
    
    if not request.loop_id or not request.reflection_status:
        raise HTTPException(status_code=400, detail="loop_id and reflection_status are required")
    
    if request.reflection_status != "done":
        raise HTTPException(status_code=400, detail="reflection_status must be 'done'")
    
    # Get the current persona for this loop if not provided
    orchestrator_persona = request.orchestrator_persona
    if not orchestrator_persona:
        orchestrator_persona = get_current_persona(request.loop_id)
    
    try:
        # Process loop reflection by gathering outputs from all reflection agents
        reflection_result = await process_loop_reflection(request.loop_id)
        
        # Apply cognitive controls to the reflection result
        controlled_reflection = process_reflection_with_controls(
            request.loop_id, 
            {"loop_id": request.loop_id, "orchestrator_persona": orchestrator_persona},
            reflection_result
        )
        
        # Evaluate whether to rerun the loop based on alignment and drift scores
        rerun_decision = await evaluate_rerun_decision(
            request.loop_id, 
            controlled_reflection
        )
        
        # If rerun is needed, determine the appropriate depth
        if rerun_decision.get("decision") == "rerun":
            rerun_depth = determine_rerun_depth_with_controls(
                request.loop_id,
                {"loop_id": request.loop_id, "orchestrator_persona": orchestrator_persona},
                rerun_decision.get("rerun_reason", "unknown")
            )
            rerun_decision["depth"] = rerun_depth
        
        logger.info(f"Completed loop-complete processing for loop {request.loop_id}")
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "orchestrator_persona": orchestrator_persona,
            "reflection_result": controlled_reflection,
            "rerun_decision": rerun_decision,
            "processed_by": "cognitive_control_layer",
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing loop reflection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing loop reflection: {str(e)}")

@router.post("/orchestrator/validate-loop")
async def validate_loop_endpoint(request: LoopValidateRequest):
    """
    Validate a loop against core requirements and enrich with cognitive controls.
    
    This endpoint checks if a loop meets the minimum requirements and enriches
    it with depth information and belief references.
    """
    logger.info(f"Validating loop {request.loop_id}")
    
    try:
        # Apply cognitive controls to the loop
        prepared_loop = integrate_with_orchestrator(request.loop_id, request.loop_data)
        
        logger.info(f"Completed loop validation for loop {request.loop_id}")
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "validation_result": prepared_loop.get("validation_status", {}),
            "prepared_loop": prepared_loop,
            "processed_by": "cognitive_control_layer",
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error validating loop: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validating loop: {str(e)}")
