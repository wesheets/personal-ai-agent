"""
Orchestrator Contract Integration Module

This module extends the orchestrator with contract enforcement capabilities,
ensuring agents operate within well-defined, verifiable bounds.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import traceback

# Import agent registry with contract enforcement
try:
    from app.core.agent_registry_enhanced import (
        validate_agent_operation,
        get_agent_contract,
        can_agent_initiate_recovery
    )
    contract_enforcement_available = True
except ImportError:
    contract_enforcement_available = False
    logging.warning("⚠️ Agent contract enforcement not available, orchestrator will not enforce contracts")

# Configure logging
logger = logging.getLogger("app.modules.orchestrator_contract_integration")

async def validate_delegation(
    from_agent: str,
    to_agent: str,
    output_schema: str,
    loop_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate delegation from one agent to another based on contract compatibility.
    
    Args:
        from_agent: Agent delegating the task
        to_agent: Agent receiving the delegation
        output_schema: Schema of the output from the delegating agent
        loop_id: Loop ID for logging violations
        
    Returns:
        Dictionary containing validation results
    """
    if not contract_enforcement_available:
        logger.warning("⚠️ Contract enforcement not available, skipping delegation validation")
        return {
            "valid": True,
            "message": "Contract enforcement not available, delegation allowed",
            "violations": []
        }
    
    try:
        # Validate that the output schema of the delegating agent matches the input schema of the receiving agent
        to_agent_validation = await validate_agent_operation(
            agent_id=to_agent,
            operation_type="input",
            input_schema=output_schema,
            loop_id=loop_id
        )
        
        if not to_agent_validation["valid"]:
            logger.warning(f"⚠️ Invalid delegation from {from_agent} to {to_agent}: {to_agent_validation['message']}")
            return {
                "valid": False,
                "message": f"Invalid delegation from {from_agent} to {to_agent}: {to_agent_validation['message']}",
                "violations": to_agent_validation["violations"]
            }
        
        logger.info(f"✅ Valid delegation from {from_agent} to {to_agent}")
        return {
            "valid": True,
            "message": f"Valid delegation from {from_agent} to {to_agent}",
            "violations": []
        }
    
    except Exception as e:
        logger.error(f"❌ Error validating delegation: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "valid": False,
            "message": f"Error validating delegation: {str(e)}",
            "violations": [{
                "agent_id": to_agent,
                "violation_type": "delegation_validation_error",
                "details": f"Error validating delegation from {from_agent} to {to_agent}: {str(e)}",
                "input_schema": output_schema,
                "output_schema": None,
                "tool_used": None,
                "timestamp": datetime.utcnow().isoformat()
            }]
        }

async def handle_contract_violation(
    agent_id: str,
    violation: Dict[str, Any],
    loop_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle a contract violation by determining appropriate action.
    
    Args:
        agent_id: Agent that violated its contract
        violation: The contract violation
        loop_id: Loop ID for logging
        
    Returns:
        Dictionary containing the response to the violation
    """
    if not contract_enforcement_available:
        logger.warning("⚠️ Contract enforcement not available, skipping violation handling")
        return {
            "status": "warning",
            "message": "Contract enforcement not available, violation ignored",
            "action": "continue"
        }
    
    try:
        # Get agent contract to determine fallback behaviors
        contract = get_agent_contract(agent_id)
        
        if not contract:
            logger.warning(f"⚠️ No contract found for agent {agent_id}, using default fallback")
            return {
                "status": "warning",
                "message": f"No contract found for agent {agent_id}, using default fallback",
                "action": "log_error"
            }
        
        # Get fallback behaviors
        fallback_behaviors = contract.fallback_behaviors if hasattr(contract, "fallback_behaviors") else contract["fallback_behaviors"]
        
        # Determine appropriate action based on violation type
        violation_type = violation.get("violation_type", "unknown")
        
        if violation_type == "input_schema_mismatch":
            # Input schema mismatch - try to convert or reject
            if "log_error" in fallback_behaviors:
                return {
                    "status": "error",
                    "message": f"Input schema mismatch for agent {agent_id}",
                    "action": "log_error",
                    "violation": violation
                }
            else:
                return {
                    "status": "error",
                    "message": f"Input schema mismatch for agent {agent_id}",
                    "action": "reject",
                    "violation": violation
                }
        
        elif violation_type == "output_schema_mismatch":
            # Output schema mismatch - try to convert or reject
            if "generate_fallback_jsx" in fallback_behaviors:
                return {
                    "status": "warning",
                    "message": f"Output schema mismatch for agent {agent_id}, generating fallback",
                    "action": "generate_fallback_jsx",
                    "violation": violation
                }
            elif "log_schema_violation" in fallback_behaviors:
                return {
                    "status": "error",
                    "message": f"Output schema mismatch for agent {agent_id}",
                    "action": "log_schema_violation",
                    "violation": violation
                }
            else:
                return {
                    "status": "error",
                    "message": f"Output schema mismatch for agent {agent_id}",
                    "action": "reject",
                    "violation": violation
                }
        
        elif violation_type == "unauthorized_tool_usage":
            # Unauthorized tool usage - block and log
            return {
                "status": "error",
                "message": f"Unauthorized tool usage by agent {agent_id}",
                "action": "block_tool",
                "violation": violation
            }
        
        else:
            # Unknown violation type - use first fallback behavior
            if fallback_behaviors:
                return {
                    "status": "warning",
                    "message": f"Unknown violation type {violation_type} for agent {agent_id}",
                    "action": fallback_behaviors[0],
                    "violation": violation
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown violation type {violation_type} for agent {agent_id}",
                    "action": "log_error",
                    "violation": violation
                }
    
    except Exception as e:
        logger.error(f"❌ Error handling contract violation: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Error handling contract violation: {str(e)}",
            "action": "log_error",
            "violation": violation
        }

async def check_recovery_authorization(
    agent_id: str,
    recovery_type: str
) -> bool:
    """
    Check if an agent is authorized to initiate a recovery procedure.
    
    Args:
        agent_id: Agent attempting to initiate recovery
        recovery_type: Type of recovery procedure
        
    Returns:
        Boolean indicating whether the agent is authorized
    """
    if not contract_enforcement_available:
        logger.warning("⚠️ Contract enforcement not available, allowing recovery")
        return True
    
    try:
        # Check if agent can initiate recovery
        can_recover = can_agent_initiate_recovery(agent_id)
        
        if not can_recover:
            logger.warning(f"⚠️ Agent {agent_id} is not authorized to initiate recovery")
            return False
        
        logger.info(f"✅ Agent {agent_id} is authorized to initiate {recovery_type} recovery")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error checking recovery authorization: {str(e)}")
        logger.error(traceback.format_exc())
        return False
