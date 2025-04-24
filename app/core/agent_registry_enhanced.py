"""
Agent Registry with Contract Enforcement

This module provides a registry for agents with contract enforcement,
ensuring agents operate within well-defined, verifiable bounds.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import traceback

# Import schemas
try:
    from app.schemas.agent_contract_schema import AgentContract, ContractViolation
    schema_available = True
except ImportError:
    schema_available = False
    logging.warning("⚠️ Agent contract schema not available, using basic validation")

# Import memory operations
try:
    from app.modules.memory_writer import write_memory
    memory_available = True
except ImportError:
    memory_available = False
    logging.warning("⚠️ Could not import memory operations, using mock implementations")
    # Mock implementation for testing
    async def write_memory(project_id, tag, value):
        return {"status": "success", "message": "Mock write successful"}

# Import manifest manager if available
try:
    from app.utils.manifest_manager import update_hardening_layer, register_agent
    manifest_available = True
except ImportError:
    manifest_available = False
    logging.warning("⚠️ Manifest manager not available, agents will not be registered")

# Configure logging
logger = logging.getLogger("app.core.agent_registry")

# Base directory for agent contracts
CONTRACTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "contracts")

# Agent registry
AGENT_REGISTRY = {}

# Agent contracts
AGENT_CONTRACTS = {}

def load_agent_contracts():
    """
    Load agent contracts from the contracts directory.
    
    Returns:
        Dict containing agent contracts
    """
    contracts = {}
    
    try:
        # Create contracts directory if it doesn't exist
        if not os.path.exists(CONTRACTS_DIR):
            os.makedirs(CONTRACTS_DIR)
            logger.info(f"✅ Created contracts directory at {CONTRACTS_DIR}")
        
        # Load all contract files
        for filename in os.listdir(CONTRACTS_DIR):
            if filename.endswith(".json"):
                agent_id = filename.split(".")[0]
                contract_path = os.path.join(CONTRACTS_DIR, filename)
                
                with open(contract_path, "r") as f:
                    contract_data = json.load(f)
                    
                    # Convert to AgentContract if schema is available
                    if schema_available:
                        contract = AgentContract(**contract_data)
                        contracts[agent_id] = contract
                    else:
                        contracts[agent_id] = contract_data
                    
                    logger.info(f"✅ Loaded contract for agent {agent_id}")
        
        return contracts
    
    except Exception as e:
        logger.error(f"❌ Error loading agent contracts: {str(e)}")
        logger.error(traceback.format_exc())
        return {}

def register_agent_with_contract(agent_id: str, agent_data: Dict[str, Any]) -> bool:
    """
    Register an agent with contract enforcement.
    
    Args:
        agent_id: Unique identifier for the agent
        agent_data: Agent data including capabilities and configuration
        
    Returns:
        Boolean indicating whether registration was successful
    """
    global AGENT_CONTRACTS  # Moved to top of function
    try:
        # Load agent contract if not already loaded
        if not AGENT_CONTRACTS:
            AGENT_CONTRACTS = load_agent_contracts()
        
        # Check if contract exists for this agent
        if agent_id not in AGENT_CONTRACTS:
            logger.warning(f"⚠️ No contract found for agent {agent_id}, using default constraints")
            
            # Create default contract
            if schema_available:
                default_contract = AgentContract(
                    agent_id=agent_id,
                    accepted_input_schema="GenericInput",
                    expected_output_schema="GenericOutput",
                    allowed_tools=agent_data.get("tools", []),
                    fallback_behaviors=["log_error"],
                    output_must_be_wrapped=True,
                    can_initiate_recovery=False,
                    version="1.0.0"
                )
                AGENT_CONTRACTS[agent_id] = default_contract
            else:
                AGENT_CONTRACTS[agent_id] = {
                    "agent_id": agent_id,
                    "accepted_input_schema": "GenericInput",
                    "expected_output_schema": "GenericOutput",
                    "allowed_tools": agent_data.get("tools", []),
                    "fallback_behaviors": ["log_error"],
                    "output_must_be_wrapped": True,
                    "can_initiate_recovery": False,
                    "version": "1.0.0"
                }
        
        # Register agent in registry
        AGENT_REGISTRY[agent_id] = agent_data
        
        # Register agent with manifest if available
        if manifest_available:
            try:
                contract = AGENT_CONTRACTS[agent_id]
                register_agent(
                    agent_id=agent_id,
                    input_schema=contract.accepted_input_schema if hasattr(contract, "accepted_input_schema") else contract["accepted_input_schema"],
                    output_schema=contract.expected_output_schema if hasattr(contract, "expected_output_schema") else contract["expected_output_schema"],
                    tools=agent_data.get("tools", [])
                )
                logger.info(f"✅ Registered agent {agent_id} with manifest")
            except Exception as e:
                logger.error(f"❌ Error registering agent with manifest: {str(e)}")
        
        logger.info(f"✅ Registered agent {agent_id} with contract enforcement")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error registering agent {agent_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return False

async def validate_agent_operation(
    agent_id: str,
    operation_type: str,
    input_schema: Optional[str] = None,
    output_schema: Optional[str] = None,
    tool_used: Optional[str] = None,
    loop_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate an agent operation against its contract.
    
    Args:
        agent_id: Unique identifier for the agent
        operation_type: Type of operation (input, output, tool)
        input_schema: Input schema to validate
        output_schema: Output schema to validate
        tool_used: Tool to validate
        loop_id: Loop ID for logging violations
        
    Returns:
        Dictionary containing validation results
    """
    global AGENT_CONTRACTS  # Moved to top of function
    try:
        # Load agent contract if not already loaded
        if not AGENT_CONTRACTS:
            AGENT_CONTRACTS = load_agent_contracts()
        
        # Check if contract exists for this agent
        if agent_id not in AGENT_CONTRACTS:
            logger.warning(f"⚠️ No contract found for agent {agent_id}, validation skipped")
            return {
                "valid": True,
                "message": f"No contract found for agent {agent_id}, validation skipped",
                "violations": []
            }
        
        # Get agent contract
        contract = AGENT_CONTRACTS[agent_id]
        violations = []
        
        # Validate input schema
        if operation_type == "input" and input_schema:
            expected_input = contract.accepted_input_schema if hasattr(contract, "accepted_input_schema") else contract["accepted_input_schema"]
            
            if input_schema != expected_input:
                violation = {
                    "agent_id": agent_id,
                    "violation_type": "input_schema_mismatch",
                    "details": f"Agent received input schema {input_schema} but expects {expected_input}",
                    "input_schema": input_schema,
                    "output_schema": None,
                    "tool_used": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
                violations.append(violation)
                
                # Log violation to memory if available
                if memory_available and loop_id:
                    await write_memory(
                        loop_id,
                        f"agent_contract_violation_{agent_id}",
                        violation
                    )
        
        # Validate output schema
        if operation_type == "output" and output_schema:
            expected_output = contract.expected_output_schema if hasattr(contract, "expected_output_schema") else contract["expected_output_schema"]
            output_wrapped = contract.output_must_be_wrapped if hasattr(contract, "output_must_be_wrapped") else contract["output_must_be_wrapped"]
            
            if output_schema != expected_output:
                violation = {
                    "agent_id": agent_id,
                    "violation_type": "output_schema_mismatch",
                    "details": f"Agent produced output schema {output_schema} but expected {expected_output}",
                    "input_schema": None,
                    "output_schema": output_schema,
                    "tool_used": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
                violations.append(violation)
                
                # Log violation to memory if available
                if memory_available and loop_id:
                    await write_memory(
                        loop_id,
                        f"agent_contract_violation_{agent_id}",
                        violation
                    )
            
            if output_wrapped is False and output_schema is not None:
                violation = {
                    "agent_id": agent_id,
                    "violation_type": "unwrapped_output",
                    "details": f"Agent output must not be schema-wrapped but received {output_schema}",
                    "input_schema": None,
                    "output_schema": output_schema,
                    "tool_used": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
                violations.append(violation)
                
                # Log violation to memory if available
                if memory_available and loop_id:
                    await write_memory(
                        loop_id,
                        f"agent_contract_violation_{agent_id}",
                        violation
                    )
        
        # Validate tool usage
        if operation_type == "tool" and tool_used:
            allowed_tools = contract.allowed_tools if hasattr(contract, "allowed_tools") else contract["allowed_tools"]
            
            if tool_used not in allowed_tools:
                violation = {
                    "agent_id": agent_id,
                    "violation_type": "unauthorized_tool_usage",
                    "details": f"Agent used unauthorized tool {tool_used}",
                    "input_schema": None,
                    "output_schema": None,
                    "tool_used": tool_used,
                    "timestamp": datetime.utcnow().isoformat()
                }
                violations.append(violation)
                
                # Log violation to memory if available
                if memory_available and loop_id:
                    await write_memory(
                        loop_id,
                        f"agent_contract_violation_{agent_id}",
                        violation
                    )
        
        # Return validation results
        return {
            "valid": len(violations) == 0,
            "message": "Validation successful" if len(violations) == 0 else f"Found {len(violations)} contract violations",
            "violations": violations
        }
    
    except Exception as e:
        logger.error(f"❌ Error validating agent operation: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "valid": False,
            "message": f"Error validating agent operation: {str(e)}",
            "violations": [{
                "agent_id": agent_id,
                "violation_type": "validation_error",
                "details": f"Error validating agent operation: {str(e)}",
                "input_schema": input_schema,
                "output_schema": output_schema,
                "tool_used": tool_used,
                "timestamp": datetime.utcnow().isoformat()
            }]
        }

def get_agent_contract(agent_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the contract for an agent.
    
    Args:
        agent_id: Unique identifier for the agent
        
    Returns:
        Agent contract if found, None otherwise
    """
    global AGENT_CONTRACTS  # Moved to top of function
    try:
        # Load agent contract if not already loaded
        if not AGENT_CONTRACTS:
            AGENT_CONTRACTS = load_agent_contracts()
        
        # Check if contract exists for this agent
        if agent_id not in AGENT_CONTRACTS:
            logger.warning(f"⚠️ No contract found for agent {agent_id}")
            return None
        
        return AGENT_CONTRACTS[agent_id]
    
    except Exception as e:
        logger.error(f"❌ Error getting agent contract: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def get_agent_fallback_behaviors(agent_id: str) -> List[str]:
    """
    Get the fallback behaviors for an agent.
    
    Args:
        agent_id: Unique identifier for the agent
        
    Returns:
        List of fallback behaviors
    """
    try:
        contract = get_agent_contract(agent_id)
        
        if not contract:
            return ["log_error"]
        
        return contract.fallback_behaviors if hasattr(contract, "fallback_behaviors") else contract["fallback_behaviors"]
    
    except Exception as e:
        logger.error(f"❌ Error getting agent fallback behaviors: {str(e)}")
        logger.error(traceback.format_exc())
        return ["log_error"]

def can_agent_initiate_recovery(agent_id: str) -> bool:
    """
    Check if an agent can initiate recovery procedures.
    
    Args:
        agent_id: Unique identifier for the agent
        
    Returns:
        Boolean indicating whether the agent can initiate recovery
    """
    try:
        contract = get_agent_contract(agent_id)
        
        if not contract:
            return False
        
        return contract.can_initiate_recovery if hasattr(contract, "can_initiate_recovery") else contract["can_initiate_recovery"]
    
    except Exception as e:
        logger.error(f"❌ Error checking if agent can initiate recovery: {str(e)}")
        logger.error(traceback.format_exc())
        return False

# Initialize agent contracts
AGENT_CONTRACTS = load_agent_contracts()

# Enable contract enforcement in manifest
if manifest_available:
    try:
        update_hardening_layer("agent_contract_enforcement", True)
        logger.info("✅ Enabled agent contract enforcement in manifest")
    except Exception as e:
        logger.error(f"❌ Error enabling agent contract enforcement in manifest: {str(e)}")
