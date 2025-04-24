"""
Debugger Routes Module

This module defines the API routes for the debugger agent operations.

Includes:
- /debugger/trace endpoint for failure debugging
- Fallback schema support for request validation
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.schemas.debugger_schema import (
    DebuggerTraceRequest, 
    DebuggerTraceResult,
    validate_debugger_trace_request
)
from app.agents.debugger_agent import debug_loop_failure

# Create router
router = APIRouter()
logger = logging.getLogger("api")

@router.post("/api/debugger/trace", response_model=DebuggerTraceResult)
async def trace_failure(request: Dict[str, Any] = Body(...)):
    """
    Trace and debug loop failures.
    
    This endpoint analyzes failure logs to diagnose issues and
    injects debugger reports into memory.
    
    Args:
        request: Dictionary containing the request data
        
    Returns:
        DebuggerTraceResult: Result of the failure diagnosis
    """
    try:
        # Validate request with fallback support
        validated_request = validate_debugger_trace_request(request)
        
        # Extract parameters
        loop_id = validated_request.loop_id
        failure_logs = validated_request.failure_logs
        memory = validated_request.memory
        loop_context = validated_request.loop_context or {}
        
        # Set memory tag if provided, otherwise use default
        memory_tag = validated_request.memory_tag
        if not memory_tag:
            memory_tag = f"debugger_trace_{loop_id}"
        
        # Log request
        logger.info(f"🛠 Debugger agent processing failure for loop: {loop_id}")
        
        # Call debugger agent to analyze failure
        updated_memory = debug_loop_failure(
            loop_id=loop_id,
            failure_logs=failure_logs,
            memory=memory,
            loop_context=loop_context
        )
        
        # Extract the latest debugger report
        debugger_reports = updated_memory.get("debugger_reports", [])
        latest_report = debugger_reports[-1] if debugger_reports else None
        
        if not latest_report:
            raise HTTPException(status_code=500, detail="Failed to generate debugger report")
        
        # Create result
        result = DebuggerTraceResult(
            updated_memory=updated_memory,
            failure_type=latest_report.get("failure_type", "unknown"),
            patch_plan=latest_report.get("patch_plan", {"steps": [], "confidence": 0.5}),
            next_agent=latest_report.get("next_agent", "critic"),
            suggested_fix=latest_report.get("suggested_fix", ""),
            report=latest_report
        )
        
        # Log success
        logger.info(f"✅ Debugger agent successfully processed failure for loop: {loop_id}")
        
        return result
    
    except Exception as e:
        # Log error
        logger.error(f"❌ Error in debugger agent: {str(e)}")
        
        # Raise HTTP exception
        raise HTTPException(
            status_code=500,
            detail=f"Error processing debugger request: {str(e)}"
        )
