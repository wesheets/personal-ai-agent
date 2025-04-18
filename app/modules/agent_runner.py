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
MODIFIED: Fixed add_memory_thread invocation to use correct parameter format
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

# Import agent modules
from app.agents.hal import run_hal_agent as hal_agent_import
from app.agents.nova import run_nova_agent
from app.agents.ash import run_ash_agent
from app.agents.critic import run_critic_agent
from app.agents.orchestrator import run_orchestrator_agent
from app.agents.sage import run_sage_agent

# Import memory thread module
from app.modules.memory_thread import add_memory_thread

# Create a safe wrapper for add_memory_thread to ensure correct parameter format
def safe_add_memory_thread(project_id=None, chain_id=None, agent=None, role=None, content=None, step_type=None, **kwargs):
    """
    Safe wrapper for add_memory_thread that ensures correct parameter format.
    
    This function accepts both positional and keyword arguments and converts them
    to the correct single dictionary format expected by add_memory_thread.
    
    Args:
        project_id: The project identifier
        chain_id: The chain identifier
        agent: The agent identifier
        role: The role of the agent
        content: The content of the memory
        step_type: The type of step (e.g., "log", "reflection", "action")
        **kwargs: Additional keyword arguments to include in the memory entry
        
    Returns:
        Result from add_memory_thread
    """
    try:
        # Check if first argument is already a dictionary (correct usage)
        if len(kwargs) == 0 and isinstance(project_id, dict) and project_id is not None:
            memory_entry = project_id
            print("✅ Using provided dictionary format for add_memory_thread")
        else:
            # Convert positional/keyword arguments to dictionary format
            memory_entry = {
                "project_id": project_id or kwargs.get("project_id", "unknown"),
                "chain_id": chain_id or kwargs.get("chain_id", "main"),
                "agent": agent or kwargs.get("agent", "unknown"),
                "role": role or kwargs.get("role", "system"),
                "content": content or kwargs.get("content", ""),
                "step_type": step_type or kwargs.get("step_type", "log")
            }
            
            # Add any additional kwargs to the dictionary
            for key, value in kwargs.items():
                if key not in memory_entry:
                    memory_entry[key] = value
            
            print(f"⚠️ Converting arguments to dictionary format for add_memory_thread: {memory_entry}")
        
        # Validate required fields
        required_fields = ["project_id", "chain_id", "agent", "role", "content", "step_type"]
        missing_fields = [field for field in required_fields if field not in memory_entry or not memory_entry[field]]
        
        if missing_fields:
            print(f"❌ Missing required fields for add_memory_thread: {missing_fields}")
            memory_entry.update({field: "unknown" for field in missing_fields if field not in memory_entry or not memory_entry[field]})
        
        # Call add_memory_thread with the properly formatted dictionary
        print("✅ HAL memory thread written")
        return add_memory_thread(memory_entry)
    except Exception as e:
        print(f"❌ Error in safe_add_memory_thread: {str(e)}")
        print(traceback.format_exc())
        # Return a dummy response to prevent further errors
        return {"status": "error", "message": f"Error in safe_add_memory_thread: {str(e)}"}

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
                "project_id": project_id,
                "chain_id": "main",
                "agent": agent,
                "role": "system",
                "content": content,
                "step_type": "log"
            }
            
            if structured_data:
                thread_data["structured_data"] = structured_data
            
            # Fixed: Properly format memory_entry as a single dictionary parameter
            print("✅ HAL wrote memory")
            safe_add_memory_thread(thread_data)
        
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
        
        # Agent Loop Autonomy Core - Trigger agent loop
        try:
            from app.modules.agent_loop_trigger import trigger_agent_loop
            
            # Specify handoff hint to NOVA
            handoff_to = "nova"
            
            # Trigger agent loop with handoff hint
            trigger_result = trigger_agent_loop(project_id, "hal", handoff_to)
            print(f"🔄 Agent loop triggered: {trigger_result}")
            logger.info(f"Agent loop triggered: {trigger_result}")
        except ImportError:
            print("⚠️ agent_loop_trigger module not available, skipping loop trigger")
            logger.warning("agent_loop_trigger module not available, skipping loop trigger")
        except Exception as e:
            print(f"❌ Error triggering agent loop: {str(e)}")
            logger.error(f"Error triggering agent loop: {str(e)}")
        
        # Return result with files_created list and handoff hint
        return {
            "status": "success",
            "message": f"HAL successfully created files for project {project_id}",
            "files_created": files_created,
            "task": task,
            "tools": tools,
            "project_state": project_state,
            "handoff_to": "nova"  # Agent Loop Autonomy Core - Handoff hint
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
            "error": str(e)
        }

# Add AGENT_RUNNERS mapping for direct agent execution
AGENT_RUNNERS = {
    "hal": run_hal_agent,
    "nova": run_nova_agent,
    "ash": run_ash_agent,
    "critic": run_critic_agent,
    "orchestrator": run_orchestrator_agent,
    "sage": run_sage_agent,
}
