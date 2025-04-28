# memory_tag: phase4.0_sprint1_cognitive_reflection_chain_activation

"""
Drift Routes Module

This module provides API routes for drift monitoring, reporting, and healing.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import traceback
import uuid

# Import drift monitoring schemas and module
from app.schemas.drift_schema import (
    DriftMonitorRequest,
    LoopDriftLog,
    DriftMonitorResponse,
    DriftLogEntry,
    DriftLogResponse
)
from app.modules.drift_monitor import (
    detect_loop_drift,
    log_drift,
    get_previous_output,
    determine_recommended_action
)

# Import drift healing schemas and module
from app.schemas.drift_healing_schemas import DriftHealingRequest, DriftHealingResult
from app.modules.drift_auto_healer import auto_heal_drift as auto_heal_drift_module

# Import memory operations
try:
    from app.modules.memory_writer import read_memory
    memory_available = True
except ImportError:
    memory_available = False
    logging.warning("⚠️ Could not import memory operations, using mock implementations")
    # Mock implementation for testing
    async def read_memory(project_id, tag):
        return None

# Import manifest manager if available
try:
    from app.utils.manifest_manager import register_route, update_hardening_layer
    manifest_available = True
except ImportError:
    manifest_available = False
    logging.warning("⚠️ Manifest manager not available, routes will not be registered")

# Configure logging
logger = logging.getLogger("app.routes.drift_routes")

# Create router
router = APIRouter(tags=["drift"])

# Register routes with manifest if available
if manifest_available:
    try:
        register_route("/drift/monitor", "POST", "DriftMonitorRequest", "active")
        register_route("/drift/report", "POST", "DriftMonitorRequest", "active")
        register_route("/drift/auto-heal", "POST", "DriftHealingRequest", "active") # Updated schema
        register_route("/drift/log", "GET", "DriftLogResponse", "active")
        update_hardening_layer("drift_monitor_enabled", True)
        logging.info("✅ Drift routes registered with manifest")
    except Exception as e:
        logging.error(f"❌ Failed to register drift routes with manifest: {str(e)}")

@router.post("/drift/report", response_model=DriftMonitorResponse)
async def report_drift(request: DriftMonitorRequest):
    """
    Report drift between previous and current loop outputs.
    
    This endpoint compares current output with previous output (from tag, snapshot, or history)
    and returns a drift score and recommended action.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
    """
    return await monitor_drift(request)

@router.post("/drift/monitor", response_model=DriftMonitorResponse)
async def monitor_drift(request: DriftMonitorRequest):
    """
    Monitor drift between previous and current loop outputs.
    
    This endpoint compares current output with previous output (from tag, snapshot, or history)
    and returns a drift score and recommended action.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
    """
    try:
        # Read the current output from memory
        current_output = await read_memory(request.loop_id, request.current_output_tag)
        
        if not current_output:
            raise HTTPException(
                status_code=404,
                detail=f"Current output not found in memory at tag {request.current_output_tag}"
            )
        
        # Get the previous output for comparison
        previous_output, source = await get_previous_output(
            loop_id=request.loop_id,
            current_output_tag=request.current_output_tag,
            previous_output_tag=request.previous_output_tag,
            snapshot_id=request.snapshot_id
        )
        
        if not previous_output:
            # No previous output to compare against
            return DriftMonitorResponse(
                status="no_previous_output",
                drift_log=LoopDriftLog(
                    loop_id=request.loop_id,
                    agent=request.agent,
                    snapshot_id=request.snapshot_id,
                    previous_checksum="0" * 64,  # Empty checksum
                    current_checksum="0" * 64,  # Will be replaced
                    drift_detected=False,
                    drift_score=0.0,
                    explanation=f"No previous output found for comparison. This appears to be the first run."
                ),
                recommended_action="continue"
            )
        
        # Detect drift between outputs
        drift_score, explanation, previous_checksum, current_checksum = await detect_loop_drift(
            previous_output=previous_output,
            current_output=current_output
        )
        
        # Determine if drift is above threshold
        drift_detected = drift_score > request.threshold
        
        # Determine recommended action
        recommended_action = await determine_recommended_action(
            drift_score=drift_score,
            threshold=request.threshold,
            agent=request.agent
        )
        
        # Create drift log
        drift_log = LoopDriftLog(
            loop_id=request.loop_id,
            agent=request.agent,
            snapshot_id=request.snapshot_id,
            previous_checksum=previous_checksum,
            current_checksum=current_checksum,
            drift_detected=drift_detected,
            drift_score=drift_score,
            explanation=f"Comparison with {source}: {explanation}"
        )
        
        # Log drift to memory
        await log_drift(
            loop_id=request.loop_id,
            agent=request.agent,
            previous_checksum=previous_checksum,
            current_checksum=current_checksum,
            drift_score=drift_score,
            drift_detected=drift_detected,
            explanation=drift_log.explanation,
            snapshot_id=request.snapshot_id
        )
        
        # Create response
        status = "drift_detected" if drift_detected else "no_drift"
        
        return DriftMonitorResponse(
            status=status,
            drift_log=drift_log,
            recommended_action=recommended_action
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"❌ Error monitoring drift: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return error response
        return DriftMonitorResponse(
            status="error",
            drift_log=LoopDriftLog(
                loop_id=request.loop_id,
                agent=request.agent,
                snapshot_id=request.snapshot_id,
                previous_checksum="error",
                current_checksum="error",
                drift_detected=False,
                drift_score=0.0,
                explanation=f"Error monitoring drift: {str(e)}"
            ),
            recommended_action="log_error"
        )

# memory_tag: phase4.0_sprint1_post_build_validation_activation_control
@router.post("/drift/auto-heal", response_model=DriftHealingResult)
async def auto_heal_drift_endpoint(request: DriftHealingRequest):
    """
    Attempt to automatically heal detected drift.
    
    This endpoint initiates an auto-healing process for a specific drift issue
    using the provided strategy and parameters, leveraging the DriftAutoHealer module.
    
    NOTE: This endpoint is currently frozen as part of controlled activation.
    """
    logger.info(f"Received auto-heal request for drift ID: {request.drift_id}, but endpoint is frozen")
    
    # Return a controlled response indicating the endpoint is frozen
    return DriftHealingResult(
        healing_attempt_id=f"frozen_heal_{uuid.uuid4().hex[:8]}",
        drift_id=request.drift_id,
        status="frozen",
        message="This endpoint is currently frozen as part of controlled activation. The drift auto-healing functionality is temporarily disabled.",
        timestamp=datetime.utcnow().isoformat()
    )
@router.get("/drift/log", response_model=DriftLogResponse)
async def get_drift_logs(loop_id: Optional[str] = None, agent: Optional[str] = None):
    """
    Retrieve drift logs.
    
    This endpoint returns drift logs, optionally filtered by loop_id and/or agent.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
    """
    try:
        # Log the request
        logger.info(f"Retrieving drift logs for loop: {loop_id or 'all'}, agent: {agent or 'all'}")
        
        # In a real implementation, this would retrieve drift logs from storage
        # For now, return mock data
        
        # Create mock entries
        entries = []
        
        # Add some mock entries based on filters
        if loop_id:
            # Add entries for specific loop
            entries.append(DriftLogEntry(
                log_id=f"drift_log_{uuid.uuid4().hex[:8]}",
                loop_id=loop_id,
                agent=agent or "hal",
                drift_score=0.75,
                drift_detected=True,
                timestamp=datetime.utcnow().isoformat(),
                healing_status="not_attempted"
            ))
            
            if not agent:
                # Add another entry for a different agent in the same loop
                entries.append(DriftLogEntry(
                    log_id=f"drift_log_{uuid.uuid4().hex[:8]}",
                    loop_id=loop_id,
                    agent="critic",
                    drift_score=0.15,
                    drift_detected=False,
                    timestamp=datetime.utcnow().isoformat(),
                    healing_status=None
                ))
        else:
            # Add entries for multiple loops
            for i in range(1, 4):
                mock_loop_id = f"loop_00{i}"
                mock_agent = agent or ("hal" if i % 2 == 0 else "critic")
                
                if not agent or mock_agent == agent:
                    entries.append(DriftLogEntry(
                        log_id=f"drift_log_{uuid.uuid4().hex[:8]}",
                        loop_id=mock_loop_id,
                        agent=mock_agent,
                        drift_score=0.25 * i,
                        drift_detected=i > 2,
                        timestamp=datetime.utcnow().isoformat(),
                        healing_status="completed" if i == 1 else "not_attempted"
                    ))
        
        return DriftLogResponse(
            status="success",
            loop_id=loop_id,
            agent=agent,
            entries=entries,
            count=len(entries)
        )
    
    except Exception as e:
        logger.error(f"❌ Error retrieving drift logs: {str(e)}")
        logger.error(traceback.format_exc())
        
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving drift logs: {str(e)}"
        )

@router.get("/drift/history/{loop_id}")
async def get_drift_history(loop_id: str, agent: Optional[str] = None):
    """
    Get drift history for a loop.
    
    This endpoint returns the drift history for a loop, optionally filtered by agent.
    
    memory_tag: phase3.0_sprint3_cognitive_loop_deepening
    """
    try:
        # Read all drift logs for the loop
        drift_logs = []
        
        if agent:
            # Get drift logs for specific agent
            memory_tag = f"loop_drift_log_{loop_id}_{agent}"
            drift_log = await read_memory(loop_id, memory_tag)
            if drift_log:
                drift_logs.append(drift_log)
        else:
            # Try to get a list of agents from memory
            agents = await read_memory(loop_id, "agent_sequence")
            if not agents or not isinstance(agents, list):
                agents = ["hal", "critic", "orchestrator"]  # Default agents
            
            # Get drift logs for all agents
            for agent_name in agents:
                memory_tag = f"loop_drift_log_{loop_id}_{agent_name}"
                drift_log = await read_memory(loop_id, memory_tag)
                if drift_log:
                    drift_logs.append(drift_log)
        
        # Return the drift history
        return {
            "status": "success",
            "loop_id": loop_id,
            "drift_logs": drift_logs
        }
    
    except Exception as e:
        logger.error(f"❌ Error getting drift history: {str(e)}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "loop_id": loop_id,
            "message": f"Error getting drift history: {str(e)}",
            "drift_logs": []
        }

