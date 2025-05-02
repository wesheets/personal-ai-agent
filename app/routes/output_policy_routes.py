"""
Output Policy Routes Module

This module provides API routes for output policy enforcement,
ensuring agents operate within system-wide constraints.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends

# Import schemas
from app.schemas.output_policy_schema import (
    OutputPolicyRequest,
    OutputPolicyResult,
    PolicyLogRequest,
    PolicyLogResponse
)

# Import policy enforcer
from app.modules.output_policy_enforcer import (
    enforce_output_policy,
    get_policy_logs
)

# Import manifest manager if available
try:
    from app.utils.manifest_manager import register_route
    manifest_available = True
except ImportError:
    manifest_available = False
    logging.warning("⚠️ Manifest manager not available, routes will not be registered")

# Configure logging
logger = logging.getLogger("app.routes.output_policy_routes")

# Create router
router = APIRouter(
    prefix="/policy",
    tags=["policy"],
    responses={404: {"description": "Not found"}}
)

# Register routes with manifest if available
if manifest_available:
    register_route("/policy/enforce", "POST", "OutputPolicyRequest", "tested")
    register_route("/policy/logs", "POST", "PolicyLogRequest", "tested")
    logger.info("✅ Registered output policy routes with manifest")

@router.post("/enforce", response_model=OutputPolicyResult)
async def enforce_policy(request: OutputPolicyRequest) -> OutputPolicyResult:
    """
    Enforce output policy on agent-generated content.
    
    Args:
        request: Output policy enforcement request
        
    Returns:
        Output policy enforcement result
    """
    try:
        logger.info(f"🔍 Enforcing output policy for agent {request.agent_id}")
        
        # Enforce policy
        result = await enforce_output_policy(
            agent_id=request.agent_id,
            content=request.content,
            output_type=request.output_type,
            context=request.context,
            loop_id=request.loop_id
        )
        
        # Log result
        if result.action != "allowed":
            logger.warning(f"⚠️ Output policy enforcement triggered for agent {request.agent_id}: {result.action}")
        else:
            logger.info(f"✅ Output policy check passed for agent {request.agent_id}")
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Error enforcing output policy: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error enforcing output policy: {str(e)}"
        )

@router.post("/logs", response_model=PolicyLogResponse)
async def get_logs(request: PolicyLogRequest) -> PolicyLogResponse:
    """
    Get policy enforcement logs.
    
    Args:
        request: Policy log request
        
    Returns:
        Policy log response
    """
    try:
        logger.info(f"🔍 Getting policy logs")
        
        # Get logs
        logs_result = await get_policy_logs(
            agent_id=request.agent_id,
            output_type=request.output_type,
            action=request.action,
            limit=request.limit
        )
        
        # Return response
        return PolicyLogResponse(
            logs=logs_result["logs"],
            total=logs_result["total"]
        )
    
    except Exception as e:
        logger.error(f"❌ Error getting policy logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting policy logs: {str(e)}"
        )
