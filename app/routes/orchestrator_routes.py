"""
Orchestrator Routes Module

This module defines the orchestrator-related routes for the Promethios API.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

# Import the post_loop_summary_handler and rerun_decision_engine modules
from app.modules.post_loop_summary_handler import process_loop_reflection
from app.modules.rerun_decision_engine import evaluate_rerun_decision
from app.utils.persona_utils import get_current_persona

router = APIRouter(tags=["orchestrator"])

class LoopCompleteRequest(BaseModel):
    """Request model for loop-complete endpoint."""
    loop_id: str
    reflection_status: str
    orchestrator_persona: Optional[str] = None

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
        
        # Evaluate whether to rerun the loop based on alignment and drift scores
        rerun_decision = await evaluate_rerun_decision(
            request.loop_id, 
            reflection_result["alignment_score"],
            reflection_result["drift_score"],
            reflection_result["summary_valid"]
        )
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "orchestrator_persona": orchestrator_persona,
            "reflection_result": reflection_result,
            "rerun_decision": rerun_decision
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing loop reflection: {str(e)}")
