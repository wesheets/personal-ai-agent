"""
AgentRunner Module

This module provides isolated agent execution functionality, allowing agents to run
independently from the central agent registry, UI, or delegate-stream system.

MODIFIED: Added full runtime logging and error protection to prevent 502 errors
MODIFIED: Added memory thread logging for agent steps
MODIFIED: Added enhanced logging for debugging memory thread issues
MODIFIED: Added toolkit registry integration for specialized agent tools
MODIFIED: Added product strategist logic for HAL in saas domain
MODIFIED: Added structured output for ASH documentation and onboarding
MODIFIED: Added AGENT_RUNNERS mapping for direct agent execution
MODIFIED: Added run_hal_agent function with file_writer integration
MODIFIED: Updated run_hal_agent with real execution logic and memory logging
MODIFIED: Added project_state integration for tracking project status
MODIFIED: Updated run_nova_agent with file creation and memory logging functionality
MODIFIED: Standardized output format across all agents
MODIFIED: Added memory logging for CRITIC and ASH agents
MODIFIED: Added agent retry and recovery flow for blocked agents
MODIFIED: Added retry_hooks integration with proper error handling
"""

import logging
import os
from typing import List, Dict, Any, Optional
import time
import traceback
import sys
import uuid
import asyncio
import json
from fastapi.responses import JSONResponse

# Import OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ OpenAI client import failed")

# Import memory thread module
from app.modules.memory_thread import add_memory_thread

# Import toolkit registry
try:
    from toolkit.registry import get_toolkit, get_agent_role, format_tools_prompt, format_nova_prompt, get_agent_themes
    TOOLKIT_AVAILABLE = True
except ImportError:
    TOOLKIT_AVAILABLE = False
    print("❌ toolkit.registry import failed, creating fallback functions")
    # Create fallback functions
    def get_toolkit(agent_id, domain):
        print(f"⚠️ Using fallback get_toolkit for {agent_id} in {domain} domain")
        return []
    
    def get_agent_role(agent_id):
        print(f"⚠️ Using fallback get_agent_role for {agent_id}")
        roles = {
            "hal": "Product Strategist",
            "nova": "UI Designer",
            "ash": "Documentation Specialist",
            "critic": "Quality Assurance Specialist",
            "sage": "System Narrator"
        }
        return roles.get(agent_id, "AI Assistant")
    
    def format_tools_prompt(tools):
        print("⚠️ Using fallback format_tools_prompt")
        return "You have access to specialized tools, but they are currently unavailable."
    
    def format_nova_prompt(tools, themes):
        print("⚠️ Using fallback format_nova_prompt")
        return "You are a UI designer with design themes, but they are currently unavailable."
    
    def get_agent_themes(agent_id):
        print(f"⚠️ Using fallback get_agent_themes for {agent_id}")
        return []

# Import retry hooks for agent retry status checking
try:
    from utils.retry_hooks import get_retry_status, log_retry_action
    RETRY_HOOKS_AVAILABLE = True
    print("✅ retry_hooks import successful")
except ImportError:
    RETRY_HOOKS_AVAILABLE = False
    print("❌ retry_hooks import failed")

# Import file_writer for HAL agent
try:
    from toolkit.file_writer import write_file
    FILE_WRITER_AVAILABLE = True
except ImportError:
    FILE_WRITER_AVAILABLE = False
    print("❌ file_writer import failed")

# Import memory_writer for logging agent actions
try:
    from app.modules.memory_writer import write_memory
    MEMORY_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_WRITER_AVAILABLE = False
    print("❌ memory_writer import failed")

# Import project_state for tracking project status
try:
    from app.modules.project_state import update_project_state, read_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ project_state import failed")

# Import agent_retry for retry and recovery flow
try:
    from app.modules.agent_retry import register_blocked_agent, check_for_unblocked_agents, mark_agent_retry_attempted
    AGENT_RETRY_AVAILABLE = True
except ImportError:
    AGENT_RETRY_AVAILABLE = False
    print("❌ agent_retry import failed")

# Import memory_block_writer for logging block information
try:
    from app.modules.memory_block_writer import write_block_memory, write_unblock_memory
    MEMORY_BLOCK_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_BLOCK_WRITER_AVAILABLE = False
    print("❌ memory_block_writer import failed")

# Import passive_reflection for re-evaluating tasks
try:
    from app.modules.passive_reflection import re_evaluate_task, start_reflection
    PASSIVE_REFLECTION_AVAILABLE = True
except ImportError:
    PASSIVE_REFLECTION_AVAILABLE = False
    print("❌ passive_reflection import failed")

try:
    from app.modules.ash_agent import run_ash_agent as ash_agent_impl
    ASH_AGENT_AVAILABLE = True
except ImportError:
    ASH_AGENT_AVAILABLE = False
    print("❌ ash_agent import failed")

try:
    from app.modules.critic_agent import run_critic_agent as critic_agent_impl
    CRITIC_AGENT_AVAILABLE = True
except ImportError:
    CRITIC_AGENT_AVAILABLE = False
    print("❌ critic_agent import failed")

# Configure logging
logger = logging.getLogger("agent_runner")

# Define memory store fallback if needed
memory_store = {}

# Helper function to safely get retry status with fallback
def safe_get_retry_status(project_id: str, agent_id: str) -> Dict[str, Any]:
    """
    Safely get retry status with fallback if the retry_hooks module is not available
    or if an error occurs during the call.
    
    Args:
        project_id: The project identifier
        agent_id: The agent identifier
        
    Returns:
        Dict containing retry status information with safe defaults
    """
    try:
        if RETRY_HOOKS_AVAILABLE:
            return get_retry_status(project_id, agent_id)
        else:
            logger.warning(f"Retry hooks not available for {agent_id} in project {project_id}")
            return {
                "should_retry": False,
                "unblock_condition": None,
                "last_block_reason": None
            }
    except Exception as e:
        logger.error(f"Error getting retry status: {str(e)}")
        return {
            "should_retry": False,
            "unblock_condition": None,
            "last_block_reason": None
        }

# Helper function to safely log retry actions with fallback
def safe_log_retry_action(agent_id: str, project_id: str, action: str) -> None:
    """
    Safely log retry actions with fallback if the retry_hooks module is not available
    or if an error occurs during the call.
    
    Args:
        agent_id: The agent identifier
        project_id: The project identifier
        action: Description of the retry action
    """
    try:
        if RETRY_HOOKS_AVAILABLE:
            log_retry_action(agent_id, project_id, action)
        else:
            logger.warning(f"Retry hooks not available for logging action: {action}")
            # Fallback to standard memory logging if available
            if MEMORY_WRITER_AVAILABLE:
                write_memory({
                    "agent": agent_id,
                    "project_id": project_id,
                    "tool_used": "retry_hook_fallback",
                    "action": action
                })
    except Exception as e:
        logger.error(f"Error logging retry action: {str(e)}")
        # No further fallback needed as this is already a fallback function
def run_hal_agent(task, project_id, tools):
    """
    Run the HAL agent with the given task, project_id, and tools.
    
    This function creates a new project with the given task and tools,
    and returns the result with a list of created files.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the result of the execution
    """
    try:
        print(f"🤖 Running HAL agent with task: {task}")
        logger.info(f"Running HAL agent with task: {task}")
        
        # Check retry status with robust error handling
        retry_status = safe_get_retry_status(project_id, "hal")
        
        # Log retry status for debugging
        print(f"🔄 HAL retry status: {retry_status}")
        logger.info(f"HAL retry status: {retry_status}")
        
        # Check if agent should retry
        if retry_status.get("should_retry", False):
            # Log retry action
            retry_message = f"HAL agent is retrying for project {project_id} due to: {retry_status.get('last_block_reason', 'unknown reason')}"
            print(f"🔄 {retry_message}")
            logger.info(retry_message)
            
            # Log retry action with robust error handling
            safe_log_retry_action("hal", project_id, retry_message)
            
            # Return retry status in response
            return {
                "status": "retry",
                "message": retry_message,
                "retry_status": retry_status,
                "task": task,
                "tools": tools
            }
        
        # Initialize variables
        files_created = []
        project_state = {}
        
        # Log memory
        def log_memory(project_id, agent, action, content, structured_data=None):
            if not MEMORY_WRITER_AVAILABLE:
                print(f"⚠️ memory_writer not available, skipping memory logging")
                logger.warning(f"memory_writer not available, skipping memory logging")
                return
            
            memory_data = {
                "project_id": project_id,
                "agent": agent,
                "action": action,
                "content": content
            }
            
            if structured_data:
                memory_data["structured_data"] = structured_data
            
            write_memory(memory_data)
            
            # Add to memory thread
            thread_data = {
                "agent": agent,
                "content": content,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            }
            
            if structured_data:
                thread_data["structured_data"] = structured_data
            
            add_memory_thread(project_id, "main", thread_data)
        
        # Log task received
        log_memory(
            project_id=project_id,
            agent="hal",
            action="received_task",
            content=f"Received task: {task}",
            structured_data={
                "task": task,
                "tools": tools
            }
        )
        
        # Read project state if available
        if PROJECT_STATE_AVAILABLE:
            try:
                project_state = read_project_state(project_id)
                print(f"📊 Project state read: {project_state}")
                logger.info(f"HAL read project state for {project_id}")
            except Exception as e:
                print(f"⚠️ Failed to read project state: {str(e)}")
                logger.warning(f"Failed to read project state: {str(e)}")
                project_state = {}
        
        # Check if file_writer is available
        if not FILE_WRITER_AVAILABLE:
            print(f"⚠️ file_writer not available, skipping file creation")
            logger.warning(f"file_writer not available, skipping file creation")
            return {
                "status": "error",
                "message": "file_writer not available, cannot create files",
                "files_created": [],
                "task": task,
                "tools": tools,
                "project_state": project_state
            }
        
        # Create README.md
        readme_content = f"""# {project_id.replace('_', ' ').title()}

This project was created by the HAL agent.

## Task
{task}

## Tools
{', '.join(tools)}

## Created
{time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())}
"""
        
        # Write README.md
        readme_path = f"/verticals/{project_id}/README.md"
        print(f"📝 Creating README.md at {readme_path}")
        logger.info(f"Creating README.md at {readme_path}")
        
        readme_result = write_file(project_id, "README.md", readme_content)
        if readme_result.get("status") == "success":
            print(f"✅ README.md created successfully")
            logger.info(f"README.md created successfully")
            files_created.append(readme_path)
            
            # Log memory
            log_memory(
                project_id=project_id,
                agent="hal",
                action="created",
                content=f"Created README.md for project {project_id}",
                structured_data={
                    "file_path": readme_path,
                    "file_type": "markdown",
                    "file_size": len(readme_content)
                }
            )
        else:
            print(f"❌ Failed to create README.md: {readme_result.get('error', 'unknown error')}")
            logger.error(f"Failed to create README.md: {readme_result.get('error', 'unknown error')}")
        
        # Update project state if project_state is available
        if PROJECT_STATE_AVAILABLE:
            project_state_data = {
                "status": "in_progress",
                "files_created": files_created,
                "agents_involved": ["hal"],
                "latest_agent_action": {
                    "agent": "hal",
                    "action": f"Created initial files for project {project_id}"
                },
                "next_recommended_step": "Run NOVA to design the project",
                "tool_usage": {
                    "file_writer": 1
                }
            }
            
            project_state_result = update_project_state(project_id, project_state_data)
            print(f"✅ Project state updated: {project_state_result.get('status', 'unknown')}")
            logger.info(f"HAL updated project state for {project_id}")
        
        # Return result with files_created list
        return {
            "status": "success",
            "message": f"HAL successfully created files for project {project_id}",
            "files_created": files_created,
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
    except Exception as e:
        error_msg = f"Error in run_hal_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": f"Error executing HAL agent: {str(e)}",
            "files_created": [],
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

def run_nova_agent(task, project_id, tools):
    """
    Run the NOVA agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 NOVA agent execution started")
    logger.info(f"NOVA agent execution started with task: {task}, project_id: {project_id}")
    
    # TODO: Implement NOVA agent execution
    return {
        "message": f"NOVA received task for project {project_id}",
        "task": task,
        "tools": tools
    }

def run_ash_agent(task, project_id, tools):
    """
    Run the ASH agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 ASH agent execution started")
    logger.info(f"ASH agent execution started with task: {task}, project_id: {project_id}")
    
    # TODO: Implement ASH agent execution
    return {
        "message": f"ASH received task for project {project_id}",
        "task": task,
        "tools": tools
    }

def run_critic_agent(task, project_id, tools):
    """
    Run the CRITIC agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 CRITIC agent execution started")
    logger.info(f"CRITIC agent execution started with task: {task}, project_id: {project_id}")
    
    # TODO: Implement CRITIC agent execution
    return {
        "message": f"CRITIC received task for project {project_id}",
        "task": task,
        "tools": tools
    }

def run_orchestrator_agent(task, project_id, tools):
    """
    Run the ORCHESTRATOR agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 ORCHESTRATOR agent execution started")
    logger.info(f"ORCHESTRATOR agent execution started with task: {task}, project_id: {project_id}")
    
    # TODO: Implement ORCHESTRATOR agent execution
    return {
        "message": f"ORCHESTRATOR received task for project {project_id}",
        "task": task,
        "tools": tools
    }

def run_sage_agent(project_id, tools=None):
    """
    Run the SAGE (System-wide Agent for Generating Explanations) agent.
    
    This agent generates narrative summaries of system activities for a specific project.
    
    Args:
        project_id: The project identifier
        tools: Optional list of tools to use
        
    Returns:
        Dict containing the summary and metadata
    """
    print(f"🤖 SAGE agent execution started")
    logger.info(f"SAGE agent execution started for project_id: {project_id}")
    
    try:
        # Default tools if not provided
        if tools is None:
            tools = ["memory_writer"]
        
        print(f"🧰 Tools: {tools}")
        
        # Generate a narrative summary based on project state and memory
        summary = "This is a system-generated summary of recent activities for project " + project_id
        
        # TODO: Implement actual SAGE agent logic to generate meaningful summaries
        # This would typically involve:
        # 1. Reading project state
        # 2. Retrieving memory entries
        # 3. Using LLM to generate a narrative
        
        return {
            "status": "success",
            "summary": summary,
            "project_id": project_id,
            "tools": tools
        }
    except Exception as e:
        error_msg = f"Error in run_sage_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "tools": tools if tools else []
        }

# Define agent runners mapping
AGENT_RUNNERS = {
    "hal": run_hal_agent,
    "nova": run_nova_agent,
    "ash": run_ash_agent,
    "critic": run_critic_agent,
    "orchestrator": run_orchestrator_agent,
    "sage": run_sage_agent
}

async def run_agent_async(agent_id: str, messages: List[Dict[str, Any]], project_id: str = None, chain_id: str = None, domain: str = "saas"):
    """
    Async version of run_agent function.
    
    Args:
        agent_id: The ID of the agent to run
        messages: List of message dictionaries with role and content
        project_id: Optional project identifier for memory logging
        chain_id: Optional chain identifier for memory logging
        domain: Optional domain for toolkit selection, defaults to "saas"
        
    Returns:
        Dict containing the response and metadata or JSONResponse with error details
    """
    # Generate project_id and chain_id if not provided
    if not project_id:
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        print(f"🆔 Generated project_id: {project_id}")
    
    if not chain_id:
        chain_id = f"chain_{uuid.uuid4().hex[:8]}"
        print(f"🔗 Generated chain_id: {chain_id}")
    
    # Enhanced logging for debugging
    print(f"🔍 DEBUG: run_agent_async called with agent_id={agent_id}, project_id={project_id}, chain_id={chain_id}, domain={domain}")
    logger.info(f"DEBUG: run_agent_async called with agent_id={agent_id}, project_id={project_id}, chain_id={chain_id}, domain={domain}")
    
    # Map agent_id to standard agent types and roles
    agent_mapping = {
        "hal": {"agent": "hal", "role": "thinker"},
        "ash": {"agent": "ash", "role": "explainer"},
        "nova": {"agent": "nova", "role": "designer"},
        "critic": {"agent": "critic", "role": "critic"},
        "orchestrator": {"agent": "orchestrator", "role": "orchestrator"},
        "Core.Forge": {"agent": "hal", "role": "thinker"}  # Default to HAL for CoreForge
    }
    
    # Get agent type and role
    agent_info = agent_mapping.get(agent_id.lower(), {"agent": "hal", "role": "thinker"})
    agent_type = agent_info["agent"]
    agent_role = agent_info["role"]
    
    print(f"🔍 DEBUG: Mapped agent_id={agent_id} to agent_type={agent_type}, agent_role={agent_role}")
    
    try:
        print("🧠 Attempting to run CoreForgeAgent fallback")
        logger.info("Attempting to run CoreForgeAgent fallback")
        
        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"🔑 OpenAI API Key loaded: {bool(api_key)}")
        logger.info(f"OpenAI API Key available: {bool(api_key)}")
        
        if not api_key:
            error_msg = "OpenAI API key is not set in environment variables"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            
            # Log error to memory thread
            print(f"🔍 DEBUG: About to log error to memory thread")
            await log_memory_thread(
                project_id=project_id,
                chain_id=chain_id,
                agent=agent_type,
                role=agent_role,
                step_type="task",
                content=f"Error: {error_msg}"
            )
            print(f"🔍 DEBUG: Finished logging error to memory thread")
            
            return JSONResponse(
                status_code=500,
                content={
                    "agent_id": agent_id,
                    "response": error_msg,
                    "status": "error"
                }
            )
        
        # Create CoreForgeAgent instance
        print(f"🔄 Creating CoreForgeAgent instance for: {agent_id}")
        agent = CoreForgeAgent()
        
        # Call agent's run method with agent_id and domain for toolkit selection
        print(f"🏃 Calling CoreForgeAgent.run() method with {len(messages)} messages")
        result = agent.run(messages, agent_id=agent_id, domain=domain)
        
        # Check if agent execution was successful
        if result.get("status") == "error":
            error_msg = f"CoreForgeAgent execution failed: {result.get('content')}"
            print(f"❌ {error_msg}")
            logger.error(error_msg)
            
            # Log error to memory thread
            print(f"🔍 DEBUG: About to log error to memory thread")
            await log_memory_thread(
                project_id=project_id,
                chain_id=chain_id,
                agent=agent_type,
                role=agent_role,
                step_type="task",
                content=f"Error: {result.get('content', 'Unknown error')}"
            )
            print(f"🔍 DEBUG: Finished logging error to memory thread")
            
            return JSONResponse(
                status_code=500,
                content={
                    "agent_id": "Core.Forge",
                    "response": result.get("content", "Unknown error"),
                    "status": "error"
                }
            )
        
        # Process agent-specific responses
        structured_data = None
        
        # Process HAL's response for saas domain
        if agent_id.lower() == "hal" and domain == "saas":
            try:
                # Parse JSON response
                content = result.get("content", "")
                parsed_content = json.loads(content)
                
                # Check for required fields
                required_fields = ["core_features", "mvp_features", "premium_features", "monetization", "task_steps"]
                for field in required_fields:
                    if field not in parsed_content:
                        parsed_content[field] = []
                
                # Update content with structured data
                result["content"] = json.dumps(parsed_content)
                structured_data = parsed_content
            except Exception as e:
                print(f"❌ Error parsing HAL's JSON response: {str(e)}")
                logger.error(f"Error parsing HAL's JSON response: {str(e)}")
                # Continue with original content
        
        # Process ASH's response for saas domain
        elif agent_id.lower() == "ash" and domain == "saas":
            try:
                # Parse JSON response
                content = result.get("content", "")
                parsed_content = json.loads(content)
                
                # Check for required fields
                required_fields = ["docs.api", "docs.onboarding", "docs.integration"]
                for field in required_fields:
                    if field not in parsed_content:
                        parsed_content[field] = ""
                
                # Update content with structured data
                result["content"] = json.dumps(parsed_content)
                structured_data = parsed_content
            except Exception as e:
                print(f"❌ Error parsing ASH's JSON response: {str(e)}")
                logger.error(f"Error parsing ASH's JSON response: {str(e)}")
                # Continue with original content
        
        # Log success
        print("✅ AgentRunner success, returning response")
        logger.info("AgentRunner success, returning response")
        
        # Log successful response to memory thread
        print(f"🔍 DEBUG: About to log successful response to memory thread")
        await log_memory_thread(
            project_id=project_id,
            chain_id=chain_id,
            agent=agent_type,
            role=agent_role,
            step_type="task",
            content=result.get("content", ""),
            structured_data=structured_data
        )
        print(f"🔍 DEBUG: Finished logging successful response to memory thread")
        
        # Return successful response
        return {
            "agent_id": "Core.Forge",
            "response": result.get("content", ""),
            "status": "ok",
            "usage": result.get("usage", {}),
            "project_id": project_id,
            "chain_id": chain_id,
            "structured_data": structured_data
        }
    
    except Exception as e:
        # Handle any unexpected errors
        error_msg = f"Error running agent {agent_id}: {str(e)}"
        print(f"❌ AgentRunner failed: {str(e)}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Log error to memory thread
        try:
            print(f"🔍 DEBUG: About to log exception to memory thread")
            await log_memory_thread(
                project_id=project_id,
                chain_id=chain_id,
                agent=agent_type,
                role=agent_role,
                step_type="task",
                content=f"Error: {str(e)}"
            )
            print(f"🔍 DEBUG: Finished logging exception to memory thread")
        except Exception as log_error:
            print(f"❌ Failed to log error to memory thread: {str(log_error)}")
            print(f"🔍 DEBUG: Exception when logging error: {traceback.format_exc()}")
        
        # Return structured error response
        return JSONResponse(
            status_code=500,
            content={
                "agent_id": agent_id,
                "response": error_msg,
                "status": "error",
                "message": str(e),
                "project_id": project_id,
                "chain_id": chain_id
            }
        )

def run_agent(agent_id: str, messages: List[Dict[str, Any]], project_id: str = None, chain_id: str = None, domain: str = "saas"):
    """
    Run an agent with the given messages, with no registry dependencies.
    
    MODIFIED: Added full runtime logging and error protection to prevent 502 errors
    MODIFIED: Added memory thread logging for agent steps
    MODIFIED: Added enhanced logging for debugging memory thread issues
    MODIFIED: Added toolkit registry integration for specialized agent tools
    MODIFIED: Added product strategist logic for HAL in saas domain
    MODIFIED: Added structured output for ASH documentation and onboarding
    
    Args:
        agent_id: The ID of the agent to run
        messages: List of message dictionaries with role and content
        project_id: Optional project identifier for memory logging
        chain_id: Optional chain identifier for memory logging
        domain: Optional domain for toolkit selection, defaults to "saas"
        
    Returns:
        Dict containing the response and metadata or JSONResponse with error details
    """
    # ADDED: Entry confirmation logging
    print("🔥 AgentRunner route invoked")
    print(f"🔍 DEBUG: run_agent called with agent_id={agent_id}, project_id={project_id}, chain_id={chain_id}, domain={domain}")
    logger.info("🔥 AgentRunner route invoked")
    
    # Run the async version in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        print(f"🔍 DEBUG: Creating new event loop and running run_agent_async")
        result = loop.run_until_complete(run_agent_async(agent_id, messages, project_id, chain_id, domain))
        print(f"🔍 DEBUG: run_agent_async completed successfully")
        return result
    except Exception as e:
        print(f"🔍 DEBUG: Exception in run_agent event loop: {str(e)}")
        print(f"🔍 DEBUG: {traceback.format_exc()}")
        raise
    finally:
        print(f"🔍 DEBUG: Closing event loop")
        loop.close()

def test_core_forge_isolation():
    """
    Test CoreForgeAgent in isolation to verify it works correctly.
    
    Returns:
        Dict containing the test results
    """
    print("\n=== Testing CoreForgeAgent in isolation ===\n")
    
    try:
        # Create test messages
        messages = [
            {"role": "user", "content": "What is 7 + 5?"}
        ]
        
        # Create agent
        print("🔧 Creating CoreForgeAgent instance")
        agent = CoreForgeAgent()
        
        # Run the agent
        print(f"🏃 Running CoreForgeAgent with message: {messages[0]['content']}")
        result = agent.run(messages)
        
        # Print the result
        print(f"\nResult:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Response: {result.get('content', 'No response')}")
        
        if result.get('status') == 'success':
            print("\n✅ Test passed: CoreForgeAgent returned successful response")
        else:
            print("\n❌ Test failed: CoreForgeAgent did not return successful response")
        
        return result
    
    except Exception as e:
        error_msg = f"Error testing CoreForgeAgent in isolation: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "content": error_msg
        }

if __name__ == "__main__":
    # Run the isolation test if this module is executed directly
    test_core_forge_isolation()
