"""
Agent Loop Trigger Module

This module provides functionality for triggering the agent loop autonomy system.
It handles automatically calling orchestrator.consult() after an agent runs,
based on project state conditions.
"""

import logging
import json
import os
import traceback
import requests
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("app.modules.agent_loop_trigger")

# Import project_state module
try:
    from app.modules.project_state import should_continue_loop, increment_loop_count
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    logger.error("Failed to import project_state module")

def trigger_agent_loop(project_id: str, agent_id: str, handoff_to: Optional[str] = None) -> Dict[str, Any]:
    """
    Trigger the agent loop autonomy system after an agent completes.
    
    This function:
    1. Increments the loop count in project state
    2. Checks if the loop should continue
    3. Calls orchestrator.consult() if the loop should continue
    
    Args:
        project_id: The project identifier
        agent_id: The agent that just completed
        handoff_to: Optional agent to hand off to directly
            
    Returns:
        Dict containing the result of the operation
    """
    try:
        logger.info(f"Agent loop trigger called for {agent_id} in project {project_id}")
        
        # Check if project_state module is available
        if not PROJECT_STATE_AVAILABLE:
            logger.error("Project state module not available, cannot trigger agent loop")
            return {
                "status": "error",
                "message": "Project state module not available",
                "project_id": project_id,
                "agent_id": agent_id
            }
        
        # Increment loop count and update last completed agent
        increment_result = increment_loop_count(project_id, agent_id)
        logger.info(f"Incremented loop count for {project_id}: {increment_result}")
        
        # Check if loop should continue
        if not should_continue_loop(project_id):
            logger.info(f"Loop stopped for {project_id}: max loops reached or status complete")
            
            # Trigger SAGE reflection hook
            try:
                trigger_sage_reflection(project_id)
            except Exception as e:
                logger.error(f"Error triggering SAGE reflection: {str(e)}")
            
            return {
                "status": "complete",
                "message": "Agent loop completed",
                "project_id": project_id,
                "agent_id": agent_id,
                "loop_continued": False
            }
        
        # If handoff_to is specified, call that agent directly
        if handoff_to:
            logger.info(f"Handoff requested from {agent_id} to {handoff_to} for project {project_id}")
            try:
                handoff_result = call_agent(handoff_to, project_id)
                return {
                    "status": "success",
                    "message": f"Handed off to {handoff_to}",
                    "project_id": project_id,
                    "agent_id": agent_id,
                    "handoff_to": handoff_to,
                    "handoff_result": handoff_result,
                    "loop_continued": True
                }
            except Exception as e:
                logger.error(f"Error in handoff to {handoff_to}: {str(e)}")
                # Fall back to orchestrator.consult()
        
        # Call orchestrator.consult()
        try:
            consult_result = call_orchestrator_consult(project_id)
            return {
                "status": "success",
                "message": "Called orchestrator.consult()",
                "project_id": project_id,
                "agent_id": agent_id,
                "consult_result": consult_result,
                "loop_continued": True
            }
        except Exception as e:
            logger.error(f"Error calling orchestrator.consult(): {str(e)}")
            return {
                "status": "error",
                "message": f"Error calling orchestrator.consult(): {str(e)}",
                "project_id": project_id,
                "agent_id": agent_id,
                "loop_continued": False
            }
    except Exception as e:
        error_msg = f"Error in trigger_agent_loop: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "agent_id": agent_id,
            "loop_continued": False
        }

def call_orchestrator_consult(project_id: str) -> Dict[str, Any]:
    """
    Call the orchestrator.consult() endpoint.
    
    Args:
        project_id: The project identifier
            
    Returns:
        Dict containing the response from the orchestrator
    """
    try:
        logger.info(f"Calling orchestrator.consult() for project {project_id}")
        
        # Prepare request data
        data = {
            "agent": "orchestrator",
            "goal": f"Determine next steps for project {project_id}",
            "expected_outputs": ["next_agent", "next_task"],
            "goal_id": project_id
        }
        
        # Make API call to orchestrator.consult endpoint
        response = requests.post(
            "http://localhost:8000/api/orchestrator/consult",
            json=data
        )
        
        # Check if request was successful
        if response.status_code == 200:
            logger.info(f"orchestrator.consult() successful for {project_id}")
            return response.json()
        else:
            logger.error(f"orchestrator.consult() failed with status {response.status_code}: {response.text}")
            return {
                "status": "error",
                "message": f"orchestrator.consult() failed with status {response.status_code}",
                "response_text": response.text
            }
    except Exception as e:
        error_msg = f"Error calling orchestrator.consult(): {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg
        }

def call_agent(agent_id: str, project_id: str) -> Dict[str, Any]:
    """
    Call a specific agent directly.
    
    Args:
        agent_id: The agent to call
        project_id: The project identifier
            
    Returns:
        Dict containing the response from the agent
    """
    try:
        logger.info(f"Calling agent {agent_id} for project {project_id}")
        
        # Prepare request data
        data = {
            "agent_id": agent_id,
            "project_id": project_id,
            "task": f"Continue work on project {project_id}"
        }
        
        # Make API call to agent run endpoint
        response = requests.post(
            "http://localhost:8000/api/agent/run",
            json=data
        )
        
        # Check if request was successful
        if response.status_code == 200:
            logger.info(f"Agent {agent_id} call successful for {project_id}")
            return response.json()
        else:
            logger.error(f"Agent {agent_id} call failed with status {response.status_code}: {response.text}")
            return {
                "status": "error",
                "message": f"Agent {agent_id} call failed with status {response.status_code}",
                "response_text": response.text
            }
    except Exception as e:
        error_msg = f"Error calling agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg
        }

def trigger_sage_reflection(project_id: str) -> Dict[str, Any]:
    """
    Trigger the SAGE reflection hook.
    
    This is called when the agent loop completes (max loops reached or status complete).
    
    Args:
        project_id: The project identifier
            
    Returns:
        Dict containing the response from the SAGE agent
    """
    try:
        logger.info(f"Triggering SAGE reflection for project {project_id}")
        
        # Make API call to system summary endpoint
        response = requests.post(
            "http://localhost:8000/api/system/summary",
            params={"project_id": project_id}
        )
        
        # Check if request was successful
        if response.status_code == 200:
            logger.info(f"SAGE reflection successful for {project_id}")
            return response.json()
        else:
            logger.error(f"SAGE reflection failed with status {response.status_code}: {response.text}")
            return {
                "status": "error",
                "message": f"SAGE reflection failed with status {response.status_code}",
                "response_text": response.text
            }
    except Exception as e:
        error_msg = f"Error triggering SAGE reflection: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg
        }
