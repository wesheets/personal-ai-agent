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
MODIFIED: Fixed AGENT_RUNNERS dictionary definition for /api/agent/run endpoint
MODIFIED: Added try/except block for importing agent modules to handle missing modules
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

# Import agent modules with try/except block to handle missing modules
try:
    from app.agents.hal import run_hal_agent
    from app.agents.nova import run_nova_agent
    from app.agents.ash import run_ash_agent
    from app.agents.critic import run_critic_agent
    from app.agents.orchestrator import run_orchestrator_agent
    from app.agents.sage import run_sage_agent

    AGENT_RUNNERS = {
        "hal": run_hal_agent,
        "nova": run_nova_agent,
        "ash": run_ash_agent,
        "critic": run_critic_agent,
        "orchestrator": run_orchestrator_agent,
        "sage": run_sage_agent
    }
    print(f"✅ AGENT_RUNNERS initialized with: {list(AGENT_RUNNERS.keys())}")
except Exception as e:
    print(f"❌ Failed to load AGENT_RUNNERS: {e}")
    AGENT_RUNNERS = {}

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
