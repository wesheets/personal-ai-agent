"""
Logic Loader Module
This module provides functionality for loading logic modules dynamically based on project context.
It enables modular agent behavior by loading different strategy implementations at runtime.
"""

import logging
import importlib.util
import sys
import os
import json
from typing import Dict, Any, Optional, Callable

# Configure logging
logger = logging.getLogger("app.modules.logic_loader")

def load_logic_module(module_path: str) -> Optional[Any]:
    """
    Dynamically load a logic module from a file path.
    
    Args:
        module_path: Path to the module file (e.g., "modules/logic/nova_strategy_default.py")
            
    Returns:
        The loaded module object or None if loading fails
    """
    try:
        logger.info(f"Loading logic module from path: {module_path}")
        print(f"🔍 Loading logic module from path: {module_path}")
        
        # Ensure the path exists
        if not os.path.exists(module_path):
            logger.warning(f"Logic module path does not exist: {module_path}")
            print(f"⚠️ Logic module path does not exist: {module_path}")
            return None
        
        # Extract module name from path
        module_name = os.path.splitext(os.path.basename(module_path))[0]
        
        # Load the module spec
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            logger.error(f"Failed to create module spec for: {module_path}")
            print(f"❌ Failed to create module spec for: {module_path}")
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
        error_msg = f"Error loading logic module from {module_path}: {str(e)}"
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
