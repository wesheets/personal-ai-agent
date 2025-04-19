"""
Agent Loop Module
This module provides functionality for executing cognitive loops and agent autonomy.

MODIFIED: Refactored to use unified agent registry instead of AGENT_RUNNERS
MODIFIED: Fixed determine_agent_from_step to prioritize exact agent ID matches
MODIFIED: Added enhanced logging for agent resolution and fallback behavior
MODIFIED: Added automatic loop continuation when loop_complete=true
MODIFIED: Added timeout guard to stuck loops
MODIFIED: Added agent registry validation before execution
"""

import logging
import uuid
import traceback
import requests
import re
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi.responses import JSONResponse

# Import the agent registry instead of AGENT_RUNNERS
from app.modules.agent_registry import get_registered_agent, list_agents
from app.modules.project_state import read_project_state, update_project_state

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
    5. Checks if loop is complete and triggers next loop if conditions are met
    
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
            
            # NEW: If project doesn't exist, stop loop execution
            if not project_state:
                logger.warning(f"[LOOP] Ignoring loop trigger for unknown project_id: {project_id}")
                print(f"⚠️ [LOOP] Ignoring loop trigger for unknown project_id: {project_id}")
                return {
                    "status": "error",
                    "message": f"Project '{project_id}' not found. Loop ignored.",
                    "project_id": project_id
                }
            
            # NEW: Check for timeout - if last_agent_triggered_at is more than 5 minutes ago
            last_triggered_at = project_state.get("last_agent_triggered_at")
            if last_triggered_at:
                try:
                    last_triggered_time = datetime.fromisoformat(last_triggered_at)
                    current_time = datetime.utcnow()
                    time_diff = current_time - last_triggered_time
                    
                    # If more than 5 minutes have passed, consider the loop stalled
                    if time_diff > timedelta(minutes=5):
                        logger.warning(f"[LOOP] Agent timeout detected for project {project_id}. Last triggered: {last_triggered_at}")
                        print(f"⚠️ [LOOP] Agent timeout detected for project {project_id}. Last triggered: {last_triggered_at}")
                        
                        # Update project state with stalled status
                        update_project_state(project_id, {
                            "loop_status": "stalled",
                            "halt_reason": "Agent timeout"
                        })
                        
                        return {
                            "status": "error",
                            "message": f"Agent timeout detected. Loop halted.",
                            "project_id": project_id,
                            "loop_status": "stalled",
                            "halt_reason": "Agent timeout"
                        }
                except Exception as e:
                    logger.error(f"Error parsing last_agent_triggered_at: {str(e)}")
            
            # Update last_agent_triggered_at timestamp
            update_project_state(project_id, {
                "last_agent_triggered_at": datetime.utcnow().isoformat(),
                "loop_status": "running"
            })
            
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
            
        # NEW: Validate agent registry before execution
        if agent_id not in registered_agents:
            error_msg = f"Resolved agent '{agent_id}' not found in registry. Available agents: {registered_agents}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            # Update project state with halted status
            update_project_state(project_id, {
                "loop_status": "halted",
                "error": "Invalid agent_id referenced"
            })
            
            # Do not silently rerun the last agent - abort with clear error
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "available_agents": registered_agents,
                "loop_status": "halted",
                "error": "Invalid agent_id referenced"
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
                
                # Update project state with halted status
                update_project_state(project_id, {
                    "loop_status": "halted",
                    "error": "Invalid agent_id referenced"
                })
                
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id,
                    "loop_status": "halted",
                    "error": "Invalid agent_id referenced"
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
                
                # Update project state with error status
                update_project_state(project_id, {
                    "loop_status": "error",
                    "error": error_msg
                })
                
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id,
                    "agent": agent_id
                }
                
            logger.info(f"Agent run successful: {agent_id}")
            print(f"✅ Agent run successful: {agent_id}")
            
            # 🧠 Re-fetch updated state to avoid stale memory
            project_state = read_project_state(project_id)  # Re-fetch updated state
            
            # Now determine next step from fresh memory
            step_description = project_state.get("next_recommended_step", "")
            logger.info(f"Updated next recommended step: {step_description}")
            print(f"🔄 Updated next recommended step: {step_description}")
            
            # Update loop status to completed for this agent
            update_project_state(project_id, {
                "loop_status": "completed",
                "last_agent_triggered_at": datetime.utcnow().isoformat()
            })
            
            # Step 5: Check if loop is complete and trigger next loop if conditions are met
            check_and_trigger_next_loop(project_id)
            
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
            
            # Update project state with error status
            update_project_state(project_id, {
                "loop_status": "error",
                "error": error_msg
            })
            
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

def check_and_trigger_next_loop(project_id: str) -> Dict[str, Any]:
    """
    Check if loop is complete and trigger next loop if conditions are met.
    
    This function:
    1. Reads the current project state
    2. Checks if loop_complete=true
    3. Looks for next_loop_goal or proposed_next_task
    4. Generates a unique project ID for the new loop
    5. Triggers a new project via POST to /api/project/start
    6. Immediately follows with POST to /api/agent/loop
    
    Args:
        project_id: The current project identifier
        
    Returns:
        Dict containing the result of the operation
    """
    try:
        # Read the current project state
        project_state = read_project_state(project_id)
        
        # Check if loop is complete
        loop_complete = project_state.get("loop_complete", False)
        if not loop_complete:
            # Loop is not complete, nothing to do
            return {
                "status": "skipped",
                "message": "Loop is not complete, skipping next loop trigger",
                "project_id": project_id
            }
        
        # Check if we have a next_loop_goal or proposed_next_task
        next_loop_goal = project_state.get("next_loop_goal")
        proposed_next_task = project_state.get("proposed_next_task")
        
        if not next_loop_goal and not proposed_next_task:
            # No next loop goal or task, nothing to do
            logger.info(f"No next_loop_goal or proposed_next_task found for project {project_id}")
            print(f"ℹ️ No next_loop_goal or proposed_next_task found for project {project_id}")
            return {
                "status": "skipped",
                "message": "No next_loop_goal or proposed_next_task found, skipping next loop trigger",
                "project_id": project_id
            }
        
        # Generate a unique project ID for the new loop
        # Use the format suggested in the requirements: loop_004_autospawned
        loop_count = project_state.get("loop_count", 1)
        new_project_id = f"loop_{loop_count + 1:03d}_autospawned"
        
        # Determine the goal for the new project
        goal = ""
        challenge_mode = "off"
        
        if next_loop_goal:
            # Use next_loop_goal directly
            goal = next_loop_goal
        elif proposed_next_task and isinstance(proposed_next_task, dict):
            # Convert proposed_next_task into a lightweight project
            goal = proposed_next_task.get("task", "")
            challenge_mode = proposed_next_task.get("challenge_mode", "off")
        
        if not goal:
            # No valid goal, nothing to do
            logger.warning(f"No valid goal found in next_loop_goal or proposed_next_task for project {project_id}")
            print(f"⚠️ No valid goal found in next_loop_goal or proposed_next_task for project {project_id}")
            return {
                "status": "skipped",
                "message": "No valid goal found, skipping next loop trigger",
                "project_id": project_id
            }
        
        # Log the auto-spawning of the next loop
        logger.info(f"[LOOP ENGINE] Auto-spawning next loop: {new_project_id} → goal: {goal}")
        print(f"[LOOP ENGINE] Auto-spawning next loop: {new_project_id} → goal: {goal}")
        
        # Trigger a new project via POST to /api/project/start
        try:
            # Prepare the request data
            project_start_data = {
                "project_id": new_project_id,
                "goal": goal,
                "agent": "orchestrator",
                "challenge_mode": challenge_mode
            }
            
            # Make the request to start the new project
            # Using internal API call to avoid network overhead
            from routes.project_routes import project_start
            project_start_result = project_start(project_start_data)
            
            # Check if project start was successful
            if project_start_result.get("status") != "success":
                error_msg = f"Failed to start new project: {project_start_result.get('message', 'Unknown error')}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id,
                    "new_project_id": new_project_id
                }
            
            # Immediately follow with POST to /api/agent/loop
            from routes.agent_routes import agent_loop
            agent_loop_result = agent_loop({"project_id": new_project_id})
            
            # Check if agent loop was successful
            if agent_loop_result.get("status") not in ["success", "running"]:
                error_msg = f"Failed to trigger agent loop for new project: {agent_loop_result.get('message', 'Unknown error')}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id,
                    "new_project_id": new_project_id
                }
            
            # Success!
            logger.info(f"Successfully triggered next loop for project {new_project_id}")
            print(f"✅ Successfully triggered next loop for project {new_project_id}")
            return {
                "status": "success",
                "message": f"Successfully triggered next loop for project {new_project_id}",
                "project_id": project_id,
                "new_project_id": new_project_id,
                "goal": goal
            }
            
        except Exception as e:
            error_msg = f"Error triggering next loop: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "new_project_id": new_project_id if 'new_project_id' in locals() else None
            }
            
    except Exception as e:
        error_msg = f"Error checking for next loop: {str(e)}"
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
