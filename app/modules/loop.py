"""
Agent Loop Module
This module provides functionality for executing cognitive loops and agent autonomy.

MODIFIED: Refactored to use unified agent registry instead of AGENT_RUNNERS
MODIFIED: Fixed determine_agent_from_step to prioritize exact agent ID matches
MODIFIED: Added enhanced logging for agent resolution and fallback behavior
"""

import logging
import uuid
import traceback
import requests
import re
from typing import Dict, Any, List, Optional
from fastapi.responses import JSONResponse

# Import the agent registry instead of AGENT_RUNNERS
from app.modules.agent_registry import get_registered_agent, list_agents

# Configure logging
logger = logging.getLogger("modules.loop")

def run_agent_from_loop(project_id: str) -> Dict[str, Any]:
    """
    Run the appropriate agent based on the project's next recommended step.
    
    This function:
    1. Calls GET /api/system/status to get the project state
    2. Extracts next_recommended_step from the project state
    3. Determines which agent to run based on the step description
    4. Triggers the appropriate agent via the agent registry
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the execution results
    """
    try:
        logger.info(f"Starting agent loop for project: {project_id}")
        print(f"🔄 Starting agent loop for project: {project_id}")
        
        # Step 1: Get project state from system status endpoint
        try:
            # Using internal API call to avoid network overhead
            from routes.system_routes import get_system_status
            status_response = get_system_status(project_id=project_id)
            
            # Check if status call was successful
            if status_response.get("status") != "success":
                error_msg = f"Failed to get system status: {status_response.get('message', 'Unknown error')}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
                
            project_state = status_response.get("project_state", {})
            
        except Exception as e:
            error_msg = f"Error getting system status: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id
            }
        
        # Step 2: Extract next_recommended_step from project state
        next_step = project_state.get("next_recommended_step")
        if not next_step:
            logger.info(f"No next recommended step found for project {project_id}")
            print(f"ℹ️ No next recommended step found for project {project_id}")
            return {
                "status": "idle",
                "message": "No next recommended step available",
                "project_id": project_id
            }
            
        logger.info(f"Next recommended step: {next_step}")
        print(f"[LOOP] next_recommended_step: {next_step}")
        
        # Step 3: Determine which agent to run based on the step description
        agent_id = determine_agent_from_step(next_step)
        print(f"[LOOP] resolved agent_id: {agent_id}")
        
        # Get list of registered agents for verification
        registered_agents = list_agents()
        print(f"[LOOP] agent_id in registered_agents: {agent_id in registered_agents}")
        
        if not agent_id:
            logger.warning(f"Could not determine agent from step: {next_step}")
            print(f"⚠️ Could not determine agent from step: {next_step}")
            return {
                "status": "error",
                "message": f"Could not determine agent from step: {next_step}",
                "project_id": project_id
            }
            
        # Verify agent exists in registry before proceeding
        if agent_id not in registered_agents:
            error_msg = f"Resolved agent '{agent_id}' not found in registry. Available agents: {registered_agents}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            # Do not silently rerun the last agent - abort with clear error
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "available_agents": registered_agents
            }
            
        logger.info(f"Determined agent: {agent_id}")
        print(f"🤖 Determined agent: {agent_id}")
        
        # Step 4: Trigger the agent via the agent registry
        try:
            # Get the agent handler function from the registry
            agent_fn = get_registered_agent(agent_id)
            
            # Double-check if agent exists in registry (should never fail at this point)
            if not agent_fn:
                error_msg = f"Agent {agent_id} not found in registry despite earlier check"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            
            # Prepare request data
            request_data = {
                "agent_id": agent_id,
                "project_id": project_id,
                "task": next_step
            }
            
            # Call agent run
            logger.info(f"Running agent {agent_id} with task: {next_step}")
            print(f"🏃 Running agent {agent_id} with task: {next_step}")
            
            # Execute the agent directly
            result = agent_fn(next_step, project_id)
            
            # Check if agent run was successful
            if result.get("status") != "success":
                error_msg = f"Agent run failed: {result.get('message', 'Unknown error')}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id,
                    "agent": agent_id
                }
                
            logger.info(f"Agent run successful: {agent_id}")
            print(f"✅ Agent run successful: {agent_id}")
            
            return {
                "status": "running",
                "message": f"Agent {agent_id} triggered successfully",
                "project_id": project_id,
                "agent": agent_id,
                "task": next_step
            }
            
        except Exception as e:
            error_msg = f"Error running agent: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent": agent_id if 'agent_id' in locals() else "unknown"
            }
            
    except Exception as e:
        error_msg = f"Error in agent loop: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id
        }

def determine_agent_from_step(step_description: str) -> Optional[str]:
    """
    Determine which agent to run based on the step description.
    
    Args:
        step_description: The step description from next_recommended_step
        
    Returns:
        The agent_id to run, or None if no agent could be determined
    """
    # Get list of registered agents
    registered_agents = list_agents()
    print(f"📋 Registered agents: {registered_agents}")
    
    # First, check if step_description is an exact match with a registered agent ID
    # This handles the case where agents set clean agent IDs as next_recommended_step
    if step_description in registered_agents:
        print(f"✅ Found exact agent ID match: {step_description}")
        return step_description
    
    # Convert to lowercase for case-insensitive matching
    step_lower = step_description.lower()
    
    # Check for exact lowercase matches with agent IDs
    for agent_id in registered_agents:
        if step_lower == agent_id.lower():
            print(f"✅ Found case-insensitive agent ID match: {agent_id}")
            return agent_id
    
    # Enhanced logging for debugging
    print(f"⚠️ No exact match found for '{step_description}', trying pattern matching")
    
    # Check for explicit agent mentions - these take highest priority
    # Direct agent name mentions
    if "hal" in step_lower:
        print(f"✅ Found pattern match: 'hal' in '{step_lower}'")
        return "hal"
    elif "nova" in step_lower:
        print(f"✅ Found pattern match: 'nova' in '{step_lower}'")
        return "nova"
    elif "ash" in step_lower:
        print(f"✅ Found pattern match: 'ash' in '{step_lower}'")
        return "ash"
    elif "critic" in step_lower:
        print(f"✅ Found pattern match: 'critic' in '{step_lower}'")
        return "critic"
    elif "sage" in step_lower:
        print(f"✅ Found pattern match: 'sage' in '{step_lower}'")
        return "sage"
    elif "orchestrator" in step_lower:
        print(f"✅ Found pattern match: 'orchestrator' in '{step_lower}'")
        return "orchestrator"
    
    # Check for task-based patterns - these are secondary priority
    task_patterns = {
        "hal": ["create", "generate", "build", "develop", "implement", "code"],
        "nova": ["design", "ui", "interface", "layout", "component"],
        "ash": ["document", "documentation", "explain", "describe"],
        "critic": ["review", "evaluate", "assess", "critique"],
        "sage": ["summarize", "summary", "overview"],
        "orchestrator": ["coordinate", "orchestrate", "manage", "plan"]
    }
    
    for agent, patterns in task_patterns.items():
        for pattern in patterns:
            if pattern in step_lower:
                print(f"✅ Found task pattern match: '{pattern}' in '{step_lower}' -> {agent}")
                return agent
    
    # If we get here, no pattern matched
    print(f"⚠️ No pattern match found for '{step_description}'")
    
    # Default to orchestrator if no specific agent could be determined
    logger.warning(f"Could not determine specific agent from step: {step_description}, defaulting to orchestrator")
    print(f"ℹ️ Defaulting to orchestrator for step: '{step_description}'")
    return "orchestrator"

# Original execute_cognitive_loop function remains unchanged
# ... (rest of the original file)
