"""
Logic Loader Module
This module provides functionality for loading logic modules dynamically based on project context.
It enables modular agent behavior by loading different strategy implementations at runtime.

MODIFIED: Enhanced to support project memory-based module resolution and task logging
"""

import logging
import importlib.util
import sys
import os
import json
from typing import Dict, Any, Optional, Callable

# Configure logging
logger = logging.getLogger("app.modules.logic_loader")

def load_logic_module(path: str) -> Optional[Any]:
    """
    Dynamically load a logic module from a file path.
    
    Args:
        path: Path to the module file (e.g., "modules/logic/nova_strategy_default.py")
            
    Returns:
        The loaded module object or None if loading fails
    """
    try:
        logger.info(f"Loading logic module from path: {path}")
        print(f"🔍 Loading logic module from path: {path}")
        
        # Ensure the path exists
        if not os.path.exists(path):
            logger.warning(f"Logic module path does not exist: {path}")
            print(f"⚠️ Logic module path does not exist: {path}")
            return None
        
        # Extract module name from path
        module_name = os.path.splitext(os.path.basename(path))[0]
        
        # Load the module spec
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            logger.error(f"Failed to create module spec for: {path}")
            print(f"❌ Failed to create module spec for: {path}")
            return None
        
        # Create the module
        module = importlib.util.module_from_spec(spec)
        
        # Add the module to sys.modules
        sys.modules[module_name] = module
        
        # Execute the module
        spec.loader.exec_module(module)
        
        logger.info(f"Successfully loaded logic module: {module_name}")
        print(f"✅ Successfully loaded logic module: {module_name}")
        
        return module
        
    except Exception as e:
        error_msg = f"Error loading logic module from {path}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return None

def validate_logic_module(module: Any) -> bool:
    """
    Validate that a loaded module has the required interface.
    
    Args:
        module: The loaded module object
            
    Returns:
        Boolean indicating whether the module has the required interface
    """
    try:
        # Check if the module has a run method
        if not hasattr(module, 'run') or not callable(getattr(module, 'run')):
            logger.warning(f"Module does not have a run method")
            print(f"⚠️ Module does not have a run method")
            return False
        
        # Check if the run method has the correct signature
        # This is a basic check and may not catch all issues
        run_method = getattr(module, 'run')
        
        logger.info(f"Module has valid interface")
        print(f"✅ Module has valid interface")
        return True
        
    except Exception as e:
        error_msg = f"Error validating logic module: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return False

def run_agent_default(agent_id: str, task: str, project_id: str) -> Dict[str, Any]:
    """
    Run the default agent implementation when no custom logic module is specified.
    
    Args:
        agent_id: The agent identifier (e.g., "hal", "nova")
        task: The task to perform
        project_id: The project identifier
            
    Returns:
        Dict containing the execution results
    """
    try:
        # Import the agent registry
        from app.modules.agent_registry import get_registered_agent
        
        # Get the agent handler function from the registry
        agent_fn = get_registered_agent(agent_id)
        
        # Check if agent exists in registry
        if not agent_fn:
            error_msg = f"Agent {agent_id} not found in registry"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent": agent_id
            }
        
        # Call agent run
        logger.info(f"Running default agent {agent_id} with task: {task}")
        print(f"🏃 Running default agent {agent_id} with task: {task}")
        
        # Execute the agent directly
        result = agent_fn(task, project_id)
        
        # Log the task execution with default logic module
        log_task_execution(project_id, agent_id, task, "default")
        
        return result
        
    except Exception as e:
        error_msg = f"Error running default agent {agent_id}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id,
            "agent": agent_id
        }

def log_task_execution(project_id: str, agent_id: str, task: str, logic_module: str) -> None:
    """
    Log the task execution with the logic module used.
    
    Args:
        project_id: The project identifier
        agent_id: The agent identifier
        task: The task performed
        logic_module: The logic module used (key or "default")
    """
    try:
        # Import project_state here to avoid circular imports
        from app.modules.project_state import read_project_state, update_project_state
        
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Initialize task_log if it doesn't exist
        if "task_log" not in project_state:
            project_state["task_log"] = []
        
        # Create task log entry
        task_entry = {
            "agent": agent_id,
            "task": task,
            "logic_module": logic_module,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add entry to task log
        project_state["task_log"].append(task_entry)
        
        # Update project state
        update_project_state(project_id, {"task_log": project_state["task_log"]})
        
        logger.info(f"Task execution logged for project {project_id}: {agent_id} using {logic_module}")
        print(f"📝 Task execution logged: {agent_id} using {logic_module}")
        
    except Exception as e:
        error_msg = f"Error logging task execution: {str(e)}"
        logger.error(error_msg)
        print(f"⚠️ {error_msg}")

def get_logic_module_from_registry(project_id: str, agent_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the logic module entry from the project registry based on the agent ID.
    
    Args:
        project_id: The project identifier
        agent_id: The agent identifier
            
    Returns:
        Dict containing the logic module entry or None if not found
    """
    try:
        # Import project_state here to avoid circular imports
        from app.modules.project_state import read_project_state
        
        # Read current project state
        project_state = read_project_state(project_id)
        
        # Check if logic_modules and registry exist
        if "logic_modules" not in project_state or "registry" not in project_state:
            logger.info(f"No logic modules or registry found for project {project_id}")
            return None
        
        # Get the logic module key for this agent
        logic_module_key = project_state["logic_modules"].get(agent_id)
        if not logic_module_key:
            logger.info(f"No logic module key found for agent {agent_id}")
            return None
        
        # Get the logic module entry from the registry
        logic_entry = project_state["registry"].get(logic_module_key)
        if not logic_entry:
            logger.warning(f"Logic module key {logic_module_key} not found in registry")
            return None
        
        return {
            "key": logic_module_key,
            "entry": logic_entry
        }
        
    except Exception as e:
        error_msg = f"Error getting logic module from registry: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return None

# Import datetime for timestamp in log_task_execution
from datetime import datetime
