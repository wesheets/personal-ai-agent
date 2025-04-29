# app/toolkit/registry/__init__.py
# Implements the toolkit registry logic for Cognitive Expansion v1.0

import os
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

TOOL_DIR = "/home/ubuntu/personal-ai-agent/app/tools"
SCM_PATH = "/home/ubuntu/personal-ai-agent/system/system_component_map.json"

# Dictionary to cache available tools {tool_name: module_path}
AVAILABLE_TOOLS: Dict[str, str] = {}

def _load_available_tools():
    """Scans the TOOL_DIR and populates AVAILABLE_TOOLS."""
    global AVAILABLE_TOOLS
    if AVAILABLE_TOOLS: # Avoid reloading if already populated
        return
    
    logger.info(f"Loading available tools from {TOOL_DIR}...")
    loaded_tools = {}
    try:
        if not os.path.isdir(TOOL_DIR):
            logger.error(f"Tool directory not found: {TOOL_DIR}")
            return
            
        for filename in os.listdir(TOOL_DIR):
            if filename.endswith(".py") and not filename.startswith("__"):
                tool_name = filename[:-3] # Remove .py
                module_path = os.path.join(TOOL_DIR, filename)
                loaded_tools[tool_name] = module_path
                logger.debug(f"Discovered tool module: {tool_name} at {module_path}")
        AVAILABLE_TOOLS = loaded_tools
        logger.info(f"Successfully loaded {len(AVAILABLE_TOOLS)} tool modules.")
    except Exception as e:
        logger.error(f"Error loading tools from {TOOL_DIR}: {e}", exc_info=True)
        AVAILABLE_TOOLS = {} # Reset on error

def get_agent_authorized_tools(agent_name: str) -> List[str]:
    """Reads SCM and returns the list of authorized tool names for the agent."""
    try:
        # Ensure SCM path is correct
        if not os.path.exists(SCM_PATH):
            logger.error(f"SCM file not found at {SCM_PATH}. Cannot determine authorized tools for 	{agent_name}.")
            return []
            
        with open(SCM_PATH, 'r') as f:
            scm_data = json.load(f)

        agent_component = None
        # Find agent by name (primary key expected in SCM for agents)
        for component in scm_data.get("components", []):
             if component.get("type") == "agent" and component.get("name") == agent_name:
                 agent_component = component
                 break

        if agent_component:
            # Look for 'tools' within 'metadata'
            authorized_tools = agent_component.get("metadata", {}).get("tools", [])
            if isinstance(authorized_tools, list):
                 logger.info(f"Found {len(authorized_tools)} authorized tools for agent 	{agent_name}	 in SCM: {authorized_tools}")
                 # Ensure tool names are strings
                 return [str(tool) for tool in authorized_tools]
            else:
                 logger.warning(f"SCM entry for agent 	{agent_name}	 has invalid 	metadata.tools	 format. Expected list, got {type(authorized_tools)}. Returning empty list.")
                 return []
        else:
            logger.warning(f"Agent 	{agent_name}	 not found in SCM ({SCM_PATH}). Cannot determine authorized tools.")
            return []

    except FileNotFoundError:
        # This case is handled by os.path.exists check above, but kept for robustness
        logger.error(f"SCM file not found at {SCM_PATH}. Cannot determine authorized tools for 	{agent_name}.")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding SCM JSON from {SCM_PATH}. Cannot determine authorized tools for 	{agent_name}.")
        return []
    except Exception as e:
        logger.error(f"Error reading SCM or finding agent 	{agent_name}	: {e}", exc_info=True)
        return []

def get_agent_toolkit(agent_name: str) -> Dict[str, str]:
    """
    Gets the toolkit (dictionary of tool_name: module_path) authorized for a specific agent.
    Loads available tools from the filesystem if not already loaded.
    Retrieves authorized tool names from SCM for the given agent.
    Returns a dictionary containing only the authorized tools and their paths.
    """
    # Ensure available tools are loaded
    if not AVAILABLE_TOOLS:
        _load_available_tools()
        if not AVAILABLE_TOOLS:
             logger.error("No tools available. Cannot provide toolkit.")
             return {}

    # Get authorized tool names from SCM
    authorized_tool_names = get_agent_authorized_tools(agent_name)
    
    # Filter available tools based on authorization
    agent_toolkit = {}
    for tool_name in authorized_tool_names:
        if tool_name in AVAILABLE_TOOLS:
            agent_toolkit[tool_name] = AVAILABLE_TOOLS[tool_name]
        else:
            logger.warning(f"Agent 	{agent_name}	 is authorized for tool 	{tool_name}	, but it was not found in {TOOL_DIR}.")

    logger.info(f"Providing toolkit with {len(agent_toolkit)} authorized tools for agent 	{agent_name}	.")
    return agent_toolkit

# Initialize tools on module load
_load_available_tools()

# --- Fallback functions from original file - kept with warnings --- 
# These might be needed temporarily if other modules import them directly from here.
# Ideally, these should be refactored or removed if not used.

def get_agent_role(agent_id):
    logger.warning("Using fallback get_agent_role implementation from toolkit registry.")
    return {
        "hal": "builder",
        "nova": "designer",
        "ash": "executor",
        "critic": "reviewer",
        "orchestrator": "planner"
    }.get(agent_id, "generalist")

def format_tools_prompt(tools):
    logger.warning("Using fallback format_tools_prompt implementation from toolkit registry.")
    if not tools:
        return "No tools assigned."
    # Assuming tools is now a dict {name: path}, extract names
    tool_names = list(tools.keys()) if isinstance(tools, dict) else tools
    return f"Agent has access to the following tools: {", ".join(tool_names)}"

def format_nova_prompt(ui_task):
    logger.warning("Using fallback format_nova_prompt implementation from toolkit registry.")
    return f"NOVA, design this UI component: {ui_task}"

def get_agent_themes():
    logger.warning("Using fallback get_agent_themes implementation from toolkit registry.")
    return {
        "hal": "precision + recursion",
        "nova": "creativity + clarity",
        "ash": "speed + automation",
        "critic": "caution + refinement",
        "orchestrator": "strategy + delegation"
    }

