"""
Orchestrator Drift Integration Module

This module extends the orchestrator with drift monitoring capabilities,
enabling detection of changes in loop outputs, agent behaviors, or schema versions
before delegating to the next agent.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Import drift monitor
try:
    from app.modules.drift_monitor import determine_recommended_action
    drift_monitor_available = True
except ImportError:
    drift_monitor_available = False
    logging.warning("⚠️ Drift monitor not available, orchestrator will not check for drift")

# Configure logging
logger = logging.getLogger("app.modules.orchestrator_drift_integration")

async def check_for_drift(
    loop_id: str,
    agent: str,
    output_tag: str,
    threshold: float = 0.25
) -> Dict[str, Any]:
    """
    Check for drift in agent output before delegating to the next agent.
    
    Args:
        loop_id: Unique identifier for the loop
        agent: Agent that produced the output
        output_tag: Memory tag where the output is stored
        threshold: Threshold for drift detection
        
    Returns:
        Dictionary containing drift information if found, None otherwise
    """
    if not drift_monitor_available:
        logger.warning("⚠️ Drift monitor not available, skipping drift check")
        return None
    
    try:
        # Import here to avoid circular imports
        import httpx
        from app.schemas.drift_schema import DriftMonitorRequest
        
        # Create request to drift monitor
        request = DriftMonitorRequest(
            loop_id=loop_id,
            agent=agent,
            current_output_tag=output_tag,
            threshold=threshold
        )
        
        # Call drift monitor endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/drift/monitor",
                json=request.dict() if hasattr(request, 'dict') else vars(request)
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("status") == "drift_detected":
                    logger.warning(f"⚠️ Drift detected for loop {loop_id}, agent {agent}")
                    return result
                
                logger.info(f"✅ No significant drift detected for loop {loop_id}, agent {agent}")
                return None
            
            logger.error(f"❌ Error checking for drift: {response.status_code} {response.text}")
            return None
    
    except Exception as e:
        logger.error(f"❌ Error checking for drift: {str(e)}")
        return None

async def handle_drift(
    loop_id: str,
    drift_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle drift detection by determining appropriate action.
    
    Args:
        loop_id: Unique identifier for the loop
        drift_result: The drift detection result
        
    Returns:
        Dictionary containing the response to the drift detection
    """
    try:
        drift_log = drift_result.get("drift_log", {})
        recommended_action = drift_result.get("recommended_action")
        
        if not recommended_action or recommended_action == "continue":
            # No action needed
            return {
                "status": "continue",
                "message": "Continuing with normal execution",
                "loop_id": loop_id
            }
        
        if recommended_action == "log_warning":
            # Log warning but continue
            return {
                "status": "warning",
                "message": f"Drift detected but below critical threshold: {drift_log.get('drift_score')}",
                "loop_id": loop_id,
                "drift_log": drift_log
            }
        
        if recommended_action == "trigger_critic_review":
            # Trigger CRITIC review
            return {
                "status": "review_required",
                "message": "Significant drift detected, CRITIC review required",
                "loop_id": loop_id,
                "drift_log": drift_log,
                "next_steps": [
                    {
                        "action": "critic_review",
                        "description": "Trigger CRITIC review of the drifted output"
                    }
                ]
            }
        
        if recommended_action == "rewind_and_retry":
            # Suggest rewind
            return {
                "status": "rewind_required",
                "message": "Critical drift detected, rewind and retry recommended",
                "loop_id": loop_id,
                "drift_log": drift_log,
                "next_steps": [
                    {
                        "action": "rewind",
                        "description": "Rewind to previous state and retry with different parameters"
                    }
                ]
            }
        
        # Default response for unknown actions
        return {
            "status": "warning",
            "message": f"Unknown recommended action: {recommended_action}",
            "loop_id": loop_id,
            "drift_log": drift_log
        }
    
    except Exception as e:
        logger.error(f"❌ Error handling drift: {str(e)}")
        return {
            "status": "error",
            "message": f"Error handling drift: {str(e)}",
            "loop_id": loop_id
        }

async def trigger_critic_review(
    loop_id: str,
    agent: str,
    output_tag: str,
    drift_log: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Trigger a CRITIC review of a drifted output.
    
    Args:
        loop_id: Unique identifier for the loop
        agent: Agent that produced the output
        output_tag: Memory tag where the output is stored
        drift_log: The drift log
        
    Returns:
        Dictionary containing the result of the CRITIC review
    """
    try:
        # Import here to avoid circular imports
        import httpx
        
        # Create request to CRITIC review endpoint
        request = {
            "loop_id": loop_id,
            "agent": agent,
            "output_tag": output_tag,
            "schema_hash": None  # No schema hash validation for drift review
        }
        
        # Call CRITIC review endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/critic/review",
                json=request
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ CRITIC review completed for drifted output: {result.get('status')}")
                return result
            
            logger.error(f"❌ Error triggering CRITIC review: {response.status_code} {response.text}")
            return {
                "status": "error",
                "message": f"Error triggering CRITIC review: {response.status_code} {response.text}",
                "loop_id": loop_id
            }
    
    except Exception as e:
        logger.error(f"❌ Error triggering CRITIC review: {str(e)}")
        return {
            "status": "error",
            "message": f"Error triggering CRITIC review: {str(e)}",
            "loop_id": loop_id
        }
