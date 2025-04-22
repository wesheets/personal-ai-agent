"""
Orchestrator Routes Module

This module defines the orchestrator-related routes for the Promethios API.
It integrates the cognitive control layer to ensure all loops adhere to
core beliefs and operational thresholds.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
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
    determine_rerun_depth_with_controls,
    determine_rerun_mode_with_controls
)
from app.modules.loop_validator import validate_loop
from app.modules.core_beliefs_integration import inject_belief_references
from app.modules.loop_execution_guard import loop_execution_guard

# Import tiered orchestrator components
from app.modules.tiered_orchestrator import (
    determine_optimal_mode,
    get_mode_config,
    get_available_modes
)

# Import visualization and memory inspection components
from app.modules.loop_map_visualizer import (
    create_visualizer,
    visualize_loop,
    VisualizationFormat
)
from app.modules.live_memory_inspection import (
    create_memory_inspector,
    inspect_memory,
    MemoryFilter,
    MemoryFormat
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["orchestrator"])

class LoopCompleteRequest(BaseModel):
    """Request model for loop-complete endpoint."""
    loop_id: str
    reflection_status: str
    orchestrator_persona: Optional[str] = None
    mode: Optional[str] = "balanced"

class LoopValidateRequest(BaseModel):
    """Request model for loop-validate endpoint."""
    loop_id: str
    loop_data: Dict[str, Any]
    mode: Optional[str] = None
    complexity: Optional[float] = None
    sensitivity: Optional[float] = None
    time_constraint: Optional[float] = None
    user_preference: Optional[str] = None

class ModeSelectionRequest(BaseModel):
    """Request model for mode-selection endpoint."""
    task_description: str
    complexity: Optional[float] = None
    sensitivity: Optional[float] = None
    time_constraint: Optional[float] = None
    user_preference: Optional[str] = None

class VisualizationRequest(BaseModel):
    """Request model for visualization endpoints."""
    loop_id: str
    mode: Optional[str] = "balanced"
    color_scheme: Optional[str] = "default"
    output_format: Optional[str] = "html"
    output_file: Optional[str] = None

class MemoryInspectionRequest(BaseModel):
    """Request model for memory inspection endpoints."""
    loop_id: str
    mode: Optional[str] = "balanced"
    filter_options: Optional[Dict[str, Any]] = None

class MemorySnapshotRequest(BaseModel):
    """Request model for memory snapshot endpoints."""
    loop_id: str
    timestamp: Optional[str] = None
    baseline_timestamp: Optional[str] = None

class MemoryExportRequest(BaseModel):
    """Request model for memory export endpoint."""
    loop_id: str
    format: str = "json"
    filename: Optional[str] = None

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
    logger.info(f"Processing loop-complete for loop {request.loop_id} in {request.mode} mode")
    
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
        
        # Apply cognitive controls to the reflection result with specified mode
        controlled_reflection = process_reflection_with_controls(
            request.loop_id, 
            {
                "loop_id": request.loop_id, 
                "orchestrator_persona": orchestrator_persona,
                "mode": request.mode
            },
            reflection_result
        )
        
        # Evaluate whether to rerun the loop based on alignment and drift scores
        rerun_decision = await evaluate_rerun_decision(
            request.loop_id, 
            controlled_reflection
        )
        
        # If rerun is needed, determine the appropriate depth and mode
        if rerun_decision.get("decision") == "rerun":
            rerun_reason = rerun_decision.get("rerun_reason", "unknown")
            
            # Determine appropriate depth and mode for rerun
            rerun_depth = determine_rerun_depth_with_controls(
                request.loop_id,
                {
                    "loop_id": request.loop_id, 
                    "orchestrator_persona": orchestrator_persona,
                    "mode": request.mode
                },
                rerun_reason
            )
            
            rerun_mode = determine_rerun_mode_with_controls(
                request.loop_id,
                {
                    "loop_id": request.loop_id, 
                    "orchestrator_persona": orchestrator_persona,
                    "mode": request.mode
                },
                rerun_reason
            )
            
            rerun_decision["depth"] = rerun_depth
            rerun_decision["mode"] = rerun_mode
            
            # Add mode configuration for the rerun
            rerun_decision["mode_config"] = get_mode_config(rerun_mode)
        
        logger.info(f"Completed loop-complete processing for loop {request.loop_id}")
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "orchestrator_persona": orchestrator_persona,
            "mode": request.mode,
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
    it with depth information, mode settings, and belief references.
    """
    logger.info(f"Validating loop {request.loop_id}")
    
    try:
        # If mode is not specified, determine optimal mode based on task characteristics
        mode = request.mode
        if not mode and "task_description" in request.loop_data:
            task_description = request.loop_data.get("task_description", "")
            mode = determine_optimal_mode(
                task_description,
                request.complexity,
                request.sensitivity,
                request.time_constraint,
                request.user_preference
            )
            logger.info(f"Determined optimal mode {mode} for loop {request.loop_id}")
        
        # Execute the loop execution guard to check safety constraints
        guard_result = loop_execution_guard(request.loop_data)
        if guard_result["status"] != "ok":
            logger.warning(f"Loop execution guard rejected loop {request.loop_id}: {guard_result['reason']}")
            return {
                "status": "rejected",
                "loop_id": request.loop_id,
                "guard_result": guard_result,
                "processed_by": "loop_execution_guard",
                "processed_at": datetime.utcnow().isoformat()
            }
        
        # Apply cognitive controls to the loop with specified or determined mode
        prepared_loop = integrate_with_orchestrator(request.loop_id, request.loop_data, mode)
        
        logger.info(f"Completed loop validation for loop {request.loop_id} in {mode} mode")
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "mode": mode,
            "validation_result": prepared_loop.get("validation_status", {}),
            "prepared_loop": prepared_loop,
            "mode_config": get_mode_config(mode) if mode else None,
            "processed_by": "cognitive_control_layer",
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error validating loop: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validating loop: {str(e)}")

@router.post("/orchestrator/determine-mode")
async def determine_mode_endpoint(request: ModeSelectionRequest):
    """
    Determine the optimal orchestrator mode based on task characteristics.
    
    This endpoint analyzes the task description and other factors to recommend
    the most appropriate orchestrator mode.
    """
    logger.info(f"Determining optimal mode for task: {request.task_description[:50]}...")
    
    try:
        # Determine optimal mode based on task characteristics
        mode = determine_optimal_mode(
            request.task_description,
            request.complexity,
            request.sensitivity,
            request.time_constraint,
            request.user_preference
        )
        
        # Get mode configuration
        mode_config = get_mode_config(mode)
        
        logger.info(f"Determined optimal mode {mode} for task")
        
        return {
            "status": "success",
            "mode": mode,
            "mode_config": mode_config,
            "factors": {
                "task_description": request.task_description,
                "complexity": request.complexity,
                "sensitivity": request.sensitivity,
                "time_constraint": request.time_constraint,
                "user_preference": request.user_preference
            },
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error determining mode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error determining mode: {str(e)}")

@router.get("/orchestrator/available-modes")
async def available_modes_endpoint():
    """
    Get a list of all available orchestrator modes with their descriptions.
    
    This endpoint returns information about all supported orchestrator modes.
    """
    logger.info("Getting available orchestrator modes")
    
    try:
        # Get available modes
        modes = get_available_modes()
        
        return {
            "status": "success",
            "modes": modes,
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting available modes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting available modes: {str(e)}")

@router.post("/orchestrator/visualize-loop")
async def visualize_loop_endpoint(request: VisualizationRequest):
    """
    Generate a visualization of a loop execution.
    
    This endpoint creates a visual representation of the loop execution path,
    agent interactions, and memory state transitions.
    """
    logger.info(f"Visualizing loop {request.loop_id} in {request.mode} mode")
    
    try:
        # Get loop trace data (in a real implementation, this would fetch from a database)
        # For this implementation, we'll use a placeholder
        loop_trace = {
            "loop_id": request.loop_id,
            "mode": request.mode,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "status": "completed",
            "loop_count": 1,
            "trace": []  # This would contain the actual trace items
        }
        
        # Generate visualization
        visualization = visualize_loop(
            request.loop_id,
            loop_trace,
            request.output_format,
            request.output_file
        )
        
        logger.info(f"Generated visualization for loop {request.loop_id}")
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "mode": request.mode,
            "visualization": visualization.get("visualization", {}),
            "output_file": request.output_file,
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error visualizing loop: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error visualizing loop: {str(e)}")

@router.post("/orchestrator/inspect-memory")
async def inspect_memory_endpoint(request: MemoryInspectionRequest):
    """
    Inspect the memory state of a running loop.
    
    This endpoint provides access to the memory state of a loop, allowing for
    inspection, debugging, and analysis of memory contents during execution.
    """
    logger.info(f"Inspecting memory for loop {request.loop_id} in {request.mode} mode")
    
    try:
        # Inspect memory
        memory_state = await inspect_memory(
            request.loop_id,
            request.mode,
            request.filter_options
        )
        
        logger.info(f"Inspected memory for loop {request.loop_id}")
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "mode": request.mode,
            "memory_state": memory_state,
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error inspecting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inspecting memory: {str(e)}")

@router.post("/orchestrator/memory-snapshot")
async def memory_snapshot_endpoint(request: MemorySnapshotRequest):
    """
    Get a memory snapshot for a specific timestamp.
    
    This endpoint retrieves a snapshot of the memory state at a specific point in time.
    """
    logger.info(f"Getting memory snapshot for loop {request.loop_id}")
    
    try:
        # Create memory inspector
        inspector = create_memory_inspector(request.loop_id)
        
        # Get memory snapshot
        if request.timestamp:
            snapshot = await inspector.get_memory_snapshot(request.timestamp)
        else:
            # Get current memory state
            snapshot = await inspector.get_memory_state()
        
        logger.info(f"Retrieved memory snapshot for loop {request.loop_id}")
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "snapshot": snapshot,
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting memory snapshot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting memory snapshot: {str(e)}")

@router.post("/orchestrator/memory-diff")
async def memory_diff_endpoint(request: MemorySnapshotRequest):
    """
    Get the difference between current memory state and a baseline snapshot.
    
    This endpoint computes the difference between the current memory state and
    a baseline snapshot, showing added, removed, and modified keys.
    """
    logger.info(f"Getting memory diff for loop {request.loop_id}")
    
    try:
        # Create memory inspector
        inspector = create_memory_inspector(request.loop_id)
        
        # Get memory diff
        diff = await inspector.get_memory_diff(request.baseline_timestamp)
        
        logger.info(f"Retrieved memory diff for loop {request.loop_id}")
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "diff": diff,
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting memory diff: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting memory diff: {str(e)}")

@router.post("/orchestrator/export-memory")
async def export_memory_endpoint(request: MemoryExportRequest):
    """
    Export memory data to a file.
    
    This endpoint exports the memory state to a file in the specified format.
    """
    logger.info(f"Exporting memory for loop {request.loop_id} in {request.format} format")
    
    try:
        # Create memory inspector
        inspector = create_memory_inspector(request.loop_id)
        
        # Export memory
        try:
            format_enum = MemoryFormat(request.format.lower())
        except ValueError:
            format_enum = MemoryFormat.JSON
            
        result = await inspector.export_memory(format_enum, request.filename)
        
        logger.info(f"Exported memory for loop {request.loop_id}")
        
        return {
            "status": "success",
            "loop_id": request.loop_id,
            "export_result": result,
            "processed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error exporting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting memory: {str(e)}")
