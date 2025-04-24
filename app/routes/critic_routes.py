"""
CRITIC Routes Module

This module provides API routes for CRITIC loop summary review and rejection,
enabling validation and accountability in the loop execution process.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import traceback
import json

# Import schemas
from app.schemas.critic_schema import (
    LoopSummaryReviewRequest,
    LoopReflectionRejection,
    LoopReflectionApproval
)

# Import memory operations
try:
    from app.modules.memory_writer import write_memory, read_memory
except ImportError:
    logging.warning("⚠️ Could not import memory operations, using mock implementations")
    # Mock implementations for testing
    async def write_memory(project_id, tag, value):
        return {"status": "success", "message": "Mock write successful"}
    
    async def read_memory(project_id, tag):
        return None

# Import schema integrity utilities if available
try:
    from app.utils.schema_integrity import validate_schema_hash
    schema_validation_available = True
except ImportError:
    schema_validation_available = False
    logging.warning("⚠️ Schema validation not available, using basic validation")

# Import manifest manager if available
try:
    from app.utils.manifest_manager import register_route, update_hardening_layer
    manifest_available = True
except ImportError:
    manifest_available = False
    logging.warning("⚠️ Manifest manager not available, routes will not be registered")

# Configure logging
logger = logging.getLogger("app.routes.critic_routes")

# Create router
router = APIRouter(tags=["critic"])

# Register routes with manifest if available
if manifest_available:
    try:
        register_route("/critic/review", "POST", "LoopSummaryReviewRequest", "active")
        update_hardening_layer("loop_rejection_enabled", True)
        logging.info("✅ CRITIC routes registered with manifest")
    except Exception as e:
        logging.error(f"❌ Failed to register CRITIC routes with manifest: {str(e)}")

@router.post("/critic/review", response_model=LoopReflectionRejection)
async def critic_review(request: LoopSummaryReviewRequest):
    """
    Review a loop summary and validate its integrity.
    
    This endpoint checks for schema hash match, output format, or missing memory,
    and returns a rejection payload with reason and recovery step if validation fails.
    """
    try:
        # Read the output from memory
        output = await read_memory(request.loop_id, request.output_tag)
        
        if not output:
            # Memory not found - reject
            rejection = LoopReflectionRejection(
                loop_id=request.loop_id,
                status="rejected",
                reason=f"Output not found in memory at tag {request.output_tag}",
                recommendation="Re-run agent with proper memory writing",
                timestamp=datetime.utcnow()
            )
            
            # Log the rejection to memory
            await log_rejection_to_memory(
                loop_id=request.loop_id,
                agent=request.agent,
                rejection=rejection
            )
            
            return rejection
        
        # Check schema hash if provided
        if request.schema_hash and schema_validation_available:
            is_valid = validate_schema_hash(output, request.schema_hash)
            
            if not is_valid:
                # Schema mismatch - reject
                rejection = LoopReflectionRejection(
                    loop_id=request.loop_id,
                    status="rejected",
                    reason=f"Output from {request.agent} did not match schema checksum",
                    recommendation=f"Re-run {request.agent} with fallback schema wrapping",
                    timestamp=datetime.utcnow()
                )
                
                # Log the rejection to memory
                await log_rejection_to_memory(
                    loop_id=request.loop_id,
                    agent=request.agent,
                    rejection=rejection
                )
                
                return rejection
        
        # Check for basic structure validity
        if isinstance(output, dict):
            # Check for required fields based on agent type
            if request.agent.lower() == "hal":
                if "code" not in output and "status" not in output:
                    # Missing required fields - reject
                    rejection = LoopReflectionRejection(
                        loop_id=request.loop_id,
                        status="rejected",
                        reason=f"HAL output missing required fields (code or status)",
                        recommendation="Re-run HAL with proper schema validation",
                        timestamp=datetime.utcnow()
                    )
                    
                    # Log the rejection to memory
                    await log_rejection_to_memory(
                        loop_id=request.loop_id,
                        agent=request.agent,
                        rejection=rejection
                    )
                    
                    return rejection
            
            # Add more agent-specific validations as needed
        else:
            # Not a dictionary - reject
            rejection = LoopReflectionRejection(
                loop_id=request.loop_id,
                status="rejected",
                reason=f"Output from {request.agent} is not a valid dictionary",
                recommendation=f"Re-run {request.agent} with proper output formatting",
                timestamp=datetime.utcnow()
            )
            
            # Log the rejection to memory
            await log_rejection_to_memory(
                loop_id=request.loop_id,
                agent=request.agent,
                rejection=rejection
            )
            
            return rejection
        
        # If we get here, the output is valid - approve
        approval = LoopReflectionApproval(
            loop_id=request.loop_id,
            status="approved",
            message=f"{request.agent} output validated successfully",
            timestamp=datetime.utcnow()
        )
        
        # Log the approval to memory
        await write_memory(
            request.loop_id,
            f"loop_approval_{request.loop_id}_{request.agent}",
            approval.dict() if hasattr(approval, 'dict') else vars(approval)
        )
        
        # Return as rejection type for API compatibility
        return LoopReflectionRejection(
            loop_id=request.loop_id,
            status="approved",  # Override the default "rejected"
            reason="Validation passed",
            recommendation=None,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"❌ Error reviewing loop summary: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Create rejection for the error
        rejection = LoopReflectionRejection(
            loop_id=request.loop_id,
            status="rejected",
            reason=f"Error during review: {str(e)}",
            recommendation="Check system logs and retry",
            timestamp=datetime.utcnow()
        )
        
        # Log the rejection to memory
        await log_rejection_to_memory(
            loop_id=request.loop_id,
            agent=request.agent,
            rejection=rejection
        )
        
        return rejection

async def log_rejection_to_memory(loop_id: str, agent: str, rejection: LoopReflectionRejection):
    """
    Log a rejection to memory for future reference.
    
    Args:
        loop_id: Unique identifier for the loop
        agent: Agent that produced the rejected output
        rejection: The rejection object
    """
    try:
        # Convert rejection to dictionary
        rejection_dict = rejection.dict() if hasattr(rejection, 'dict') else vars(rejection)
        
        # Add the agent information
        rejection_dict["agent"] = agent
        
        # Store in memory under the loop rejection tag
        memory_tag = f"loop_rejection_{loop_id}"
        result = await write_memory(loop_id, memory_tag, rejection_dict)
        
        # Log the operation
        if result and result.get("status") == "success":
            logger.info(f"✅ Rejection logged for loop {loop_id}, agent {agent}")
            return True
        else:
            logger.error(f"❌ Failed to log rejection for loop {loop_id}: {result}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error logging rejection: {str(e)}")
        return False
