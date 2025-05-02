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
        logger.info(f"🔁 AGENT LOOP TRIGGER: Called for {agent_id} in project {project_id}")
        print(f"🔁 AGENT LOOP TRIGGER: Called for {agent_id} in project {project_id}")
        
        # Check if project_state module is available
        if not PROJECT_STATE_AVAILABLE:
            error_msg = "Project state module not available, cannot trigger agent loop"
            logger.error(f"❌ {error_msg}")
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent_id": agent_id
            }
        
        # Increment loop count and update last completed agent
        logger.info(f"Incrementing loop count for project {project_id}, last agent: {agent_id}")
        print(f"Incrementing loop count for project {project_id}, last agent: {agent_id}")
        increment_result = increment_loop_count(project_id, agent_id)
        logger.info(f"Incremented loop count result: {increment_result}")
        print(f"Incremented loop count result: {increment_result}")
        
        # Check if loop should continue
        logger.info(f"Checking if loop should continue for project {project_id}")
        print(f"Checking if loop should continue for project {project_id}")
        should_continue = should_continue_loop(project_id)
        logger.info(f"Should continue loop: {should_continue}")
        print(f"Should continue loop: {should_continue}")
        
        if not should_continue:
            logger.info(f"🛑 Loop stopped for {project_id}: max loops reached or status complete")
            print(f"🛑 Loop stopped for {project_id}: max loops reached or status complete")
            
            # Trigger SAGE reflection hook
            logger.info(f"Triggering SAGE reflection for completed project {project_id}")
            print(f"Triggering SAGE reflection for completed project {project_id}")
            try:
                sage_result = trigger_sage_reflection(project_id)
                logger.info(f"SAGE reflection result: {sage_result}")
                print(f"SAGE reflection result status: {sage_result.get('status', 'unknown')}")
            except Exception as e:
                logger.error(f"❌ Error triggering SAGE reflection: {str(e)}")
                logger.error(traceback.format_exc())
                print(f"❌ Error triggering SAGE reflection: {str(e)}")
            
            return {
                "status": "complete",
                "message": "Agent loop completed",
                "project_id": project_id,
                "agent_id": agent_id,
                "loop_continued": False
            }
        
        # If handoff_to is specified, call that agent directly
        if handoff_to:
            logger.info(f"🤝 Handoff requested from {agent_id} to {handoff_to} for project {project_id}")
            print(f"🤝 Handoff requested from {agent_id} to {handoff_to} for project {project_id}")
            try:
                logger.info(f"Calling agent {handoff_to} directly")
                print(f"Calling agent {handoff_to} directly")
                handoff_result = call_agent(handoff_to, project_id)
                
                # Validate handoff result
                if not handoff_result:
                    logger.error(f"❌ Handoff to {handoff_to} returned no result")
                    print(f"❌ Handoff to {handoff_to} returned no result")
                    return {
                        "status": "error",
                        "message": f"Handoff to {handoff_to} returned no result",
                        "project_id": project_id,
                        "agent_id": agent_id,
                        "handoff_to": handoff_to,
                        "loop_continued": False
                    }
                
                logger.info(f"Handoff result: {handoff_result}")
                print(f"Handoff result status: {handoff_result.get('status', 'unknown')}")
                
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
                logger.error(f"❌ Error in handoff to {handoff_to}: {str(e)}")
                logger.error(traceback.format_exc())
                print(f"❌ Error in handoff to {handoff_to}: {str(e)}")
                logger.info(f"Falling back to orchestrator.consult()")
                print(f"Falling back to orchestrator.consult()")
                # Fall back to orchestrator.consult()
        
        # Call orchestrator.consult()
        try:
            logger.info(f"🧠 Calling orchestrator.consult() for project {project_id}")
            print(f"🧠 Calling orchestrator.consult() for project {project_id}")
            consult_result = call_orchestrator_consult(project_id)
            
            # Validate consult result
            if not consult_result:
                logger.error(f"❌ orchestrator.consult() returned no result")
                print(f"❌ orchestrator.consult() returned no result")
                return {
                    "status": "error",
                    "message": "orchestrator.consult() returned no result",
                    "project_id": project_id,
                    "agent_id": agent_id,
                    "loop_continued": False
                }
            
            if consult_result.get("status") == "error":
                logger.error(f"❌ orchestrator.consult() returned error: {consult_result.get('message')}")
                print(f"❌ orchestrator.consult() returned error: {consult_result.get('message')}")
                return {
                    "status": "error",
                    "message": f"orchestrator.consult() returned error: {consult_result.get('message')}",
                    "project_id": project_id,
                    "agent_id": agent_id,
                    "consult_result": consult_result,
                    "loop_continued": False
                }
            
            logger.info(f"Consult result: {consult_result}")
            print(f"Consult result status: {consult_result.get('status', 'unknown')}")
            
            # Check if next agent was triggered
            next_agent = consult_result.get("next_agent")
            if next_agent:
                logger.info(f"✅ Next agent {next_agent} was triggered")
                print(f"✅ Next agent {next_agent} was triggered")
            else:
                logger.warning(f"⚠️ No next agent was specified in consult result")
                print(f"⚠️ No next agent was specified in consult result")
            
            return {
                "status": "success",
                "message": "Called orchestrator.consult()",
                "project_id": project_id,
                "agent_id": agent_id,
                "next_agent": next_agent,
                "consult_result": consult_result,
                "loop_continued": True
            }
        except Exception as e:
            error_msg = f"Error calling orchestrator.consult(): {str(e)}"
            logger.error(f"❌ {error_msg}")
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent_id": agent_id,
                "loop_continued": False,
                "error_details": traceback.format_exc()
            }
    except Exception as e:
        error_msg = f"Error in trigger_agent_loop: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "agent_id": agent_id,
            "loop_continued": False,
            "error_details": traceback.format_exc()
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
        logger.info(f"🧠 ORCHESTRATOR CONSULT: Calling endpoint for project {project_id}")
        print(f"🧠 ORCHESTRATOR CONSULT: Calling endpoint for project {project_id}")
        
        # Prepare request data
        data = {
            "agent": "orchestrator",
            "goal": f"Determine next steps for project {project_id}",
            "expected_outputs": ["next_agent", "next_task"],
            "goal_id": project_id
        }
        logger.info(f"Request data: {data}")
        
        # Make API call to orchestrator.consult endpoint
        logger.info(f"Sending POST request to /api/orchestrator/consult")
        print(f"Sending POST request to /api/orchestrator/consult")
        response = requests.post(
            "http://localhost:8000/api/orchestrator/consult",
            json=data
        )
        
        # Check if request was successful
        logger.info(f"Response status code: {response.status_code}")
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"✅ orchestrator.consult() successful for {project_id}")
            print(f"✅ orchestrator.consult() successful for {project_id}")
            
            # Parse response
            try:
                result = response.json()
                logger.info(f"Response parsed successfully: {result}")
                
                # Validate response contains expected fields
                if not result:
                    logger.error(f"❌ Empty response from orchestrator.consult()")
                    print(f"❌ Empty response from orchestrator.consult()")
                    return {
                        "status": "error",
                        "message": "Empty response from orchestrator.consult()",
                        "response_text": response.text
                    }
                
                # Check for required fields
                if "status" not in result:
                    logger.warning(f"⚠️ Response missing 'status' field")
                    print(f"⚠️ Response missing 'status' field")
                
                if "next_agent" not in result:
                    logger.warning(f"⚠️ Response missing 'next_agent' field")
                    print(f"⚠️ Response missing 'next_agent' field")
                
                # Return the parsed result
                return result
            except Exception as json_error:
                logger.error(f"❌ Failed to parse JSON response: {str(json_error)}")
                logger.error(f"Response text: {response.text}")
                print(f"❌ Failed to parse JSON response: {str(json_error)}")
                
                return {
                    "status": "error",
                    "message": f"Failed to parse orchestrator.consult() response: {str(json_error)}",
                    "response_text": response.text
                }
        else:
            error_msg = f"orchestrator.consult() failed with status {response.status_code}"
            logger.error(f"❌ {error_msg}: {response.text}")
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "response_text": response.text
            }
    except Exception as e:
        error_msg = f"Error calling orchestrator.consult(): {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg,
            "error_details": traceback.format_exc()
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
        logger.info(f"🤖 AGENT CALL: Calling agent {agent_id} for project {project_id}")
        print(f"🤖 AGENT CALL: Calling agent {agent_id} for project {project_id}")
        
        # Prepare request data
        data = {
            "agent_id": agent_id,
            "project_id": project_id,
            "task": f"Continue work on project {project_id}"
        }
        logger.info(f"Request data: {data}")
        
        # Make API call to agent run endpoint
        logger.info(f"Sending POST request to /api/agent/run")
        print(f"Sending POST request to /api/agent/run")
        response = requests.post(
            "http://localhost:8000/api/agent/run",
            json=data
        )
        
        # Check if request was successful
        logger.info(f"Response status code: {response.status_code}")
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"✅ Agent {agent_id} call successful for {project_id}")
            print(f"✅ Agent {agent_id} call successful for {project_id}")
            
            # Parse response
            try:
                result = response.json()
                logger.info(f"Response parsed successfully")
                
                # Validate response contains expected fields
                if not result:
                    logger.error(f"❌ Empty response from agent {agent_id}")
                    print(f"❌ Empty response from agent {agent_id}")
                    return {
                        "status": "error",
                        "message": f"Empty response from agent {agent_id}",
                        "response_text": response.text
                    }
                
                # Check for required fields
                if "status" not in result:
                    logger.warning(f"⚠️ Response missing 'status' field")
                    print(f"⚠️ Response missing 'status' field")
                
                # Log key parts of the response
                logger.info(f"Agent response status: {result.get('status', 'unknown')}")
                if "message" in result:
                    logger.info(f"Agent message: {result['message']}")
                
                # Check if memory was written
                memory_written = False
                if "memory_written" in result:
                    memory_written = result["memory_written"]
                    logger.info(f"Memory written: {memory_written}")
                    print(f"Memory written: {memory_written}")
                
                # Return the parsed result
                return result
            except Exception as json_error:
                logger.error(f"❌ Failed to parse JSON response: {str(json_error)}")
                logger.error(f"Response text: {response.text}")
                print(f"❌ Failed to parse JSON response: {str(json_error)}")
                
                return {
                    "status": "error",
                    "message": f"Failed to parse agent {agent_id} response: {str(json_error)}",
                    "response_text": response.text
                }
        else:
            error_msg = f"Agent {agent_id} call failed with status {response.status_code}"
            logger.error(f"❌ {error_msg}: {response.text}")
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "response_text": response.text
            }
    except Exception as e:
        error_msg = f"Error calling agent {agent_id}: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg,
            "error_details": traceback.format_exc()
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
        logger.info(f"🧠 SAGE REFLECTION: Triggering for project {project_id}")
        print(f"🧠 SAGE REFLECTION: Triggering for project {project_id}")
        
        # Make API call to system summary endpoint
        logger.info(f"Sending POST request to /api/system/summary")
        print(f"Sending POST request to /api/system/summary")
        response = requests.post(
            "http://localhost:8000/api/system/summary",
            params={"project_id": project_id}
        )
        
        # Check if request was successful
        logger.info(f"Response status code: {response.status_code}")
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"✅ SAGE reflection successful for {project_id}")
            print(f"✅ SAGE reflection successful for {project_id}")
            
            # Parse response
            try:
                result = response.json()
                logger.info(f"Response parsed successfully")
                
                # Validate response contains expected fields
                if not result:
                    logger.error(f"❌ Empty response from SAGE reflection")
                    print(f"❌ Empty response from SAGE reflection")
                    return {
                        "status": "error",
                        "message": "Empty response from SAGE reflection",
                        "response_text": response.text
                    }
                
                # Return the parsed result
                return result
            except Exception as json_error:
                logger.error(f"❌ Failed to parse JSON response: {str(json_error)}")
                logger.error(f"Response text: {response.text}")
                print(f"❌ Failed to parse JSON response: {str(json_error)}")
                
                return {
                    "status": "error",
                    "message": f"Failed to parse SAGE reflection response: {str(json_error)}",
                    "response_text": response.text
                }
        else:
            error_msg = f"SAGE reflection failed with status {response.status_code}"
            logger.error(f"❌ {error_msg}: {response.text}")
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "response_text": response.text
            }
    except Exception as e:
        error_msg = f"Error triggering SAGE reflection: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(traceback.format_exc())
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg,
            "error_details": traceback.format_exc()
        }
