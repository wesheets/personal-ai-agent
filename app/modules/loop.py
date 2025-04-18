"""
Agent Loop Module
This module provides functionality for executing cognitive loops and agent autonomy.
"""

import logging
import uuid
import traceback
import requests
import re
from typing import Dict, Any, List, Optional
from fastapi.responses import JSONResponse

# Configure logging
logger = logging.getLogger("modules.loop")

def run_agent_from_loop(project_id: str) -> Dict[str, Any]:
    """
    Run the appropriate agent based on the project's next recommended step.
    
    This function:
    1. Calls GET /api/system/status to get the project state
    2. Extracts next_recommended_step from the project state
    3. Determines which agent to run based on the step description
    4. Triggers the appropriate agent via the agent run endpoint
    
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
        print(f"📋 Next recommended step: {next_step}")
        
        # Step 3: Determine which agent to run based on the step description
        agent_id = determine_agent_from_step(next_step)
        if not agent_id:
            logger.warning(f"Could not determine agent from step: {next_step}")
            print(f"⚠️ Could not determine agent from step: {next_step}")
            return {
                "status": "error",
                "message": f"Could not determine agent from step: {next_step}",
                "project_id": project_id
            }
            
        logger.info(f"Determined agent: {agent_id}")
        print(f"🤖 Determined agent: {agent_id}")
        
        # Step 4: Trigger the agent via the agent run endpoint
        try:
            # Using internal API call to avoid network overhead
            from app.modules.agent_runner import AGENT_RUNNERS
            
            # Check if agent exists in AGENT_RUNNERS
            if agent_id not in AGENT_RUNNERS:
                error_msg = f"Agent {agent_id} not found in AGENT_RUNNERS"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            
            # Get the agent runner function
            runner_func = AGENT_RUNNERS[agent_id]
            
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
            result = runner_func(next_step, project_id)
            
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
    # Convert to lowercase for case-insensitive matching
    step_lower = step_description.lower()
    
    # Check for explicit agent mentions - these take highest priority
    # Direct agent name mentions
    if "hal" in step_lower:
        return "hal"
    elif "nova" in step_lower:
        return "nova"
    elif "ash" in step_lower:
        return "ash"
    elif "critic" in step_lower:
        return "critic"
    elif "sage" in step_lower:
        return "sage"
    elif "orchestrator" in step_lower:
        return "orchestrator"
    
    # Check for task-based patterns - these are secondary priority
    if any(term in step_lower for term in ["create", "generate", "build", "develop", "implement", "code"]):
        return "hal"
    elif any(term in step_lower for term in ["design", "ui", "interface", "layout", "component"]):
        return "nova"
    elif any(term in step_lower for term in ["document", "documentation", "explain", "describe"]):
        return "ash"
    elif any(term in step_lower for term in ["review", "evaluate", "assess", "critique"]):
        return "critic"
    elif any(term in step_lower for term in ["summarize", "summary", "overview"]):
        return "sage"
    elif any(term in step_lower for term in ["coordinate", "orchestrate", "manage", "plan"]):
        return "orchestrator"
        
    # Default to orchestrator if no specific agent could be determined
    logger.warning(f"Could not determine specific agent from step: {step_description}, defaulting to orchestrator")
    return "orchestrator"

# Original execute_cognitive_loop function remains unchanged
# ... (rest of the original file)
