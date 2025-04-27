"""
Agent Validator Module

This module validates agents listed in the Agent Cognition Index (ACI).
It checks if agents exist in /app/agents/, are importable, and match their memory contract.
"""

import os
import importlib.util
import sys
import logging
from typing import Dict, List, Any, Tuple

# Configure logging
logger = logging.getLogger('startup_validation.agent_validator')

def validate_agents(aci_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Validate all agents listed in the ACI.
    
    Args:
        aci_data: The loaded Agent Cognition Index data
        
    Returns:
        Tuple containing:
        - Health score as a percentage (0-100)
        - List of drift issues detected
    """
    logger.info("Starting agent validation")
    
    if "agents" not in aci_data:
        logger.error("ACI data does not contain 'agents' key")
        return 0.0, [{"type": "agent", "path": "ACI", "issue": "Missing 'agents' key in ACI"}]
    
    agents = aci_data["agents"]
    if not agents:
        logger.warning("No agents found in ACI")
        return 100.0, []
    
    valid_count = 0
    drift_issues = []
    
    for agent in agents:
        if "name" not in agent:
            logger.error("Agent missing 'name' attribute")
            drift_issues.append({
                "type": "agent",
                "path": "unknown",
                "issue": "Agent missing 'name' attribute"
            })
            continue
        
        agent_name = agent["name"]
        logger.info(f"Validating agent: {agent_name}")
        
        # Check if agent exists
        if not check_agent_exists(agent_name):
            logger.error(f"Agent {agent_name} does not exist in /app/agents/")
            drift_issues.append({
                "type": "agent",
                "path": agent_name,
                "issue": "Agent file does not exist in /app/agents/"
            })
            continue
        
        # Check if agent is importable
        if not check_agent_importable(agent_name):
            logger.error(f"Agent {agent_name} is not importable")
            drift_issues.append({
                "type": "agent",
                "path": agent_name,
                "issue": "Agent cannot be imported (syntax errors or missing dependencies)"
            })
            continue
        
        # Check if agent matches memory contract
        if not check_agent_contract(agent_name, agent):
            logger.error(f"Agent {agent_name} does not match memory contract")
            drift_issues.append({
                "type": "agent",
                "path": agent_name,
                "issue": "Agent does not match memory contract (missing required attributes)"
            })
            continue
        
        # If we get here, the agent is valid
        valid_count += 1
        logger.info(f"Agent {agent_name} validated successfully")
    
    # Calculate health score
    health_score = (valid_count / len(agents)) * 100 if agents else 100.0
    logger.info(f"Agent validation complete. Health score: {health_score:.1f}%")
    
    return health_score, drift_issues

def check_agent_exists(agent_name: str) -> bool:
    """
    Check if an agent file exists in the /app/agents/ directory.
    
    Args:
        agent_name: Name of the agent to check
        
    Returns:
        True if the agent file exists, False otherwise
    """
    # Convert agent name to file name (e.g., "CEOAgent" -> "ceo_agent.py")
    file_name = convert_agent_name_to_file_name(agent_name)
    
    # Check if file exists in /app/agents/
    agent_path = os.path.join("/app/agents", file_name)
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    full_path = os.path.join(base_path, agent_path.lstrip('/'))
    
    exists = os.path.isfile(full_path)
    logger.debug(f"Agent file check for {agent_name}: {'exists' if exists else 'not found'} at {full_path}")
    return exists

def check_agent_importable(agent_name: str) -> bool:
    """
    Check if an agent can be imported without errors.
    
    Args:
        agent_name: Name of the agent to check
        
    Returns:
        True if the agent can be imported, False otherwise
    """
    # Convert agent name to file name and module name
    file_name = convert_agent_name_to_file_name(agent_name)
    module_name = file_name[:-3] if file_name.endswith('.py') else file_name
    
    # Get full path to agent file
    agent_path = os.path.join("/app/agents", file_name)
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    full_path = os.path.join(base_path, agent_path.lstrip('/'))
    
    if not os.path.isfile(full_path):
        logger.debug(f"Cannot import {agent_name}: file not found at {full_path}")
        return False
    
    try:
        # Try to import the module
        spec = importlib.util.spec_from_file_location(module_name, full_path)
        if spec is None:
            logger.debug(f"Cannot import {agent_name}: spec_from_file_location returned None")
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        logger.debug(f"Successfully imported {agent_name}")
        return True
    except Exception as e:
        logger.debug(f"Error importing {agent_name}: {str(e)}")
        return False

def check_agent_contract(agent_name: str, expected_contract: Dict[str, Any]) -> bool:
    """
    Check if an agent matches its memory contract.
    
    Args:
        agent_name: Name of the agent to check
        expected_contract: The expected contract for the agent
        
    Returns:
        True if the agent matches its contract, False otherwise
    """
    # Required attributes for an agent
    required_attributes = ["name", "description", "tools"]
    
    # Check if all required attributes are present
    for attr in required_attributes:
        if attr not in expected_contract:
            logger.debug(f"Agent {agent_name} missing required attribute: {attr}")
            return False
    
    # Additional checks could be performed here, such as:
    # - Checking if the agent class has required methods
    # - Checking if the agent's tools match the expected tools
    # - Checking if the agent's schemas match the expected schemas
    
    logger.debug(f"Agent {agent_name} matches memory contract")
    return True

def convert_agent_name_to_file_name(agent_name: str) -> str:
    """
    Convert an agent name to its corresponding file name.
    
    Args:
        agent_name: Name of the agent (e.g., "CEOAgent")
        
    Returns:
        File name for the agent (e.g., "ceo_agent.py")
    """
    # Handle special cases
    if agent_name == "CEOAgent":
        return "ceo_agent.py"
    if agent_name == "Core.Forge":
        return "core_forge.py"
    
    # General case: convert CamelCase to snake_case
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', agent_name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    # Remove "agent" suffix if present in the name itself
    s3 = s2.replace('_agent', '') if s2.endswith('_agent') else s2
    
    # Add .py extension and ensure "agent" is in the filename
    if "agent" not in s3:
        return f"{s3}_agent.py"
    else:
        return f"{s3}.py"
