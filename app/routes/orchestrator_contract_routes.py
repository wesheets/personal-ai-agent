"""
Orchestrator Routes with Contract Enforcement

This module provides API routes for the orchestrator with contract enforcement,
ensuring agents operate within well-defined, verifiable bounds.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import traceback

# Import schemas
try:
    from app.schemas.agent_contract_schema import (
        ContractValidationRequest,
        ContractValidationResponse
    )
    schema_available = True
except ImportError:
    schema_available = False
    logging.warning("⚠️ Agent contract schema not available, using basic validation")

# Import contract enforcement
try:
    from app.core.agent_registry_enhanced import validate_agent_operation
    from app.modules.orchestrator_contract_integration import (
        validate_delegation,
        handle_contract_violation,
        check_recovery_authorization
    )
    contract_enforcement_available = True
except ImportError:
    contract_enforcement_available = False
    logging.warning("⚠️ Contract enforcement not available, orchestrator will not enforce contracts")

# Import manifest manager if available
try:
    from app.utils.manifest_manager import register_route, update_hardening_layer
    manifest_available = True
except ImportError:
    manifest_available = False
    logging.warning("⚠️ Manifest manager not available, routes will not be registered")

# Configure logging
logger = logging.getLogger("app.routes.orchestrator_contract_routes")

# Create router
router = APIRouter(tags=["orchestrator"])

# Register routes with manifest if available
if manifest_available:
    try:
        register_route("/orchestrator/validate_contract", "POST", "ContractValidationRequest", "active")
        register_route("/orchestrator/validate_delegation", "POST", "DelegationValidationRequest", "active")
        update_hardening_layer("agent_contract_enforcement", True)
        logging.info("✅ Orchestrator contract routes registered with manifest")
    except Exception as e:
        logging.error(f"❌ Failed to register orchestrator contract routes with manifest: {str(e)}")

@router.post("/orchestrator/validate_contract", response_model=ContractValidationResponse if schema_available else None)
async def validate_contract(request: ContractValidationRequest if schema_available else Dict[str, Any]):
    """
    Validate an agent operation against its contract.
    
    This endpoint validates that an agent's operation (input, output, or tool usage)
    complies with its contract.
    """
    if not contract_enforcement_available:
        raise HTTPException(
            status_code=501,
            detail="Contract enforcement not available"
        )
    
    try:
        # Extract request parameters
        if schema_available:
            # Use getattr for safe access to potentially optional fields in Pydantic model
            agent_id = getattr(request, "agent_id", None)
            input_schema = getattr(request, "input_schema", None)
            output_schema = getattr(request, "output_schema", None)
            tool_used = getattr(request, "tool_used", None)
            loop_id = getattr(request, "loop_id", None)
        else:
            # Fallback for when schema is not available (request is Dict)
            agent_id = request.get("agent_id")
            input_schema = request.get("input_schema")
            output_schema = request.get("output_schema")
            tool_used = request.get("tool_used")
            loop_id = request.get("loop_id")

        # Ensure required fields are present even in Dict case
        if not agent_id:
             raise HTTPException(status_code=400, detail="Missing required field: agent_id")
        
        # Determine operation type
        operation_type = None
        if input_schema:
            operation_type = "input"
        elif output_schema:
            operation_type = "output"
        elif tool_used:
            operation_type = "tool"
        else:
            raise HTTPException(
                status_code=400,
                detail="Must specify input_schema, output_schema, or tool_used"
            )
        
        # Validate operation
        validation_result = await validate_agent_operation(
            agent_id=agent_id,
            operation_type=operation_type,
            input_schema=input_schema,
            output_schema=output_schema,
            tool_used=tool_used,
            loop_id=loop_id
        )
        
        # Return validation result
        if schema_available:
            return ContractValidationResponse(
                agent_id=agent_id,
                valid=validation_result["valid"],
                violations=validation_result["violations"]
            )
        else:
            return validation_result
    
    except Exception as e:
        logger.error(f"❌ Error validating contract: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error validating contract: {str(e)}"
        )

@router.post("/orchestrator/validate_delegation")
async def validate_delegation_route(request: Dict[str, Any]):
    """
    Validate delegation from one agent to another based on contract compatibility.
    
    This endpoint validates that the output schema of the delegating agent
    matches the input schema of the receiving agent.
    """
    if not contract_enforcement_available:
        raise HTTPException(
            status_code=501,
            detail="Contract enforcement not available"
        )
    
    try:
        # Extract request parameters
        from_agent = request.get("from_agent")
        to_agent = request.get("to_agent")
        output_schema = request.get("output_schema")
        loop_id = request.get("loop_id")
        
        if not from_agent or not to_agent or not output_schema:
            raise HTTPException(
                status_code=400,
                detail="Must specify from_agent, to_agent, and output_schema"
            )
        
        # Validate delegation
        validation_result = await validate_delegation(
            from_agent=from_agent,
            to_agent=to_agent,
            output_schema=output_schema,
            loop_id=loop_id
        )
        
        # Return validation result
        return validation_result
    
    except Exception as e:
        logger.error(f"❌ Error validating delegation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error validating delegation: {str(e)}"
        )

@router.post("/orchestrator/handle_violation")
async def handle_violation(request: Dict[str, Any]):
    """
    Handle a contract violation by determining appropriate action.
    
    This endpoint determines the appropriate action to take in response
    to a contract violation.
    """
    if not contract_enforcement_available:
        raise HTTPException(
            status_code=501,
            detail="Contract enforcement not available"
        )
    
    try:
        # Extract request parameters
        agent_id = request.get("agent_id")
        violation = request.get("violation")
        loop_id = request.get("loop_id")
        
        if not agent_id or not violation:
            raise HTTPException(
                status_code=400,
                detail="Must specify agent_id and violation"
            )
        
        # Handle violation
        handling_result = await handle_contract_violation(
            agent_id=agent_id,
            violation=violation,
            loop_id=loop_id
        )
        
        # Return handling result
        return handling_result
    
    except Exception as e:
        logger.error(f"❌ Error handling violation: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error handling violation: {str(e)}"
        )

@router.post("/orchestrator/check_recovery_authorization")
async def check_recovery_auth(request: Dict[str, Any]):
    """
    Check if an agent is authorized to initiate a recovery procedure.
    
    This endpoint checks if an agent is authorized to initiate a specific
    type of recovery procedure.
    """
    if not contract_enforcement_available:
        raise HTTPException(
            status_code=501,
            detail="Contract enforcement not available"
        )
    
    try:
        # Extract request parameters
        agent_id = request.get("agent_id")
        recovery_type = request.get("recovery_type")
        
        if not agent_id or not recovery_type:
            raise HTTPException(
                status_code=400,
                detail="Must specify agent_id and recovery_type"
            )
        
        # Check authorization
        authorized = await check_recovery_authorization(
            agent_id=agent_id,
            recovery_type=recovery_type
        )
        
        # Return authorization result
        return {
            "agent_id": agent_id,
            "recovery_type": recovery_type,
            "authorized": authorized
        }
    
    except Exception as e:
        logger.error(f"❌ Error checking recovery authorization: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error checking recovery authorization: {str(e)}"
        )
