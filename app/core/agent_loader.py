"""
Failsafe Agent Loader

This module provides a robust, fault-tolerant mechanism for loading agent classes.
It prevents a single bad agent from crashing the entire backend by wrapping each
agent initialization in try/except blocks.
"""

import logging
import importlib
import inspect
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Type

# Configure logging
logger = logging.getLogger("agents")

# Global agent registry
agents = {}

def load_agent_from_module(agent_id: str, module_path: str, class_name: Optional[str] = None) -> bool:
    """
    Safely load an agent from a module path with error handling.
    
    Args:
        agent_id: The ID to register the agent under
        module_path: The Python module path (e.g., 'app.core.forge')
        class_name: The class name to instantiate (if None, will try to infer)
        
    Returns:
        bool: True if agent was loaded successfully, False otherwise
    """
    try:
        # Import the module
        module = importlib.import_module(module_path)
        
        # If class_name is not provided, try to infer it
        if class_name is None:
            # Look for classes in the module
            classes = inspect.getmembers(module, inspect.isclass)
            
            # Filter classes defined in this module (not imported)
            module_classes = [cls for name, cls in classes 
                             if cls.__module__ == module.__name__]
            
            if not module_classes:
                logger.error(f"❌ Failed to load {agent_id}: No classes found in module {module_path}")
                return False
                
            # Use the first class found
            agent_class = module_classes[0]
        else:
            # Get the specified class
            agent_class = getattr(module, class_name)
        
        # Instantiate the agent
        agent_instance = agent_class()
        
        # Register the agent
        agents[agent_id] = agent_instance
        logger.info(f"✅ Successfully loaded agent: {agent_id} ({agent_class.__name__})")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to load {agent_id}: Module {module_path} not found - {str(e)}")
        return False
    except AttributeError as e:
        logger.error(f"❌ Failed to load {agent_id}: Class {class_name} not found in {module_path} - {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to load {agent_id}: {str(e)}")
        return False

def load_agent_from_path(agent_id: str, file_path: str, class_name: Optional[str] = None) -> bool:
    """
    Safely load an agent from a file path with error handling.
    
    Args:
        agent_id: The ID to register the agent under
        file_path: The file path relative to project root (e.g., 'app/core/forge.py')
        class_name: The class name to instantiate (if None, will try to infer)
        
    Returns:
        bool: True if agent was loaded successfully, False otherwise
    """
    try:
        # Convert file path to module path
        if file_path.endswith('.py'):
            file_path = file_path[:-3]  # Remove .py extension
        
        # Replace slashes with dots
        module_path = file_path.replace('/', '.')
        
        return load_agent_from_module(agent_id, module_path, class_name)
        
    except Exception as e:
        logger.error(f"❌ Failed to load {agent_id} from path {file_path}: {str(e)}")
        return False

def initialize_agents() -> Dict[str, Any]:
    """
    Initialize all agents with failsafe error handling.
    
    Returns:
        Dict[str, Any]: Dictionary of successfully loaded agents
    """
    global agents
    agents = {}
    
    # Load agent manifest
    manifest_path = Path(__file__).parents[2] / "config" / "agent_manifest.json"
    
    try:
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
        logger.info(f"✅ Loaded agent manifest with {len(manifest_data)} agents")
    except Exception as e:
        logger.error(f"❌ Failed to load agent manifest: {str(e)}")
        manifest_data = {}
    
    # Core.Forge agent
    try:
        from app.core.forge import CoreForge
        agents["Core.Forge"] = CoreForge()
        logger.info("✅ OpenAI provider initialized successfully for Core.Forge agent")
    except Exception as e:
        logger.error(f"❌ Failed to load Core.Forge: {str(e)}")
    
    # ObserverAgent
    try:
        from app.agents.observer_agent import ObserverAgent
        agents["ObserverAgent"] = ObserverAgent()
        logger.info("✅ OpenAI provider initialized successfully for ObserverAgent")
    except Exception as e:
        logger.error(f"❌ Failed to load ObserverAgent: {str(e)}")
    
    # MemoryAgent
    try:
        from app.agents.memory_agent import MemoryAgent
        agents["MemoryAgent"] = MemoryAgent()
        logger.info("✅ OpenAI provider initialized successfully for MemoryAgent")
    except Exception as e:
        logger.error(f"❌ Failed to load MemoryAgent: {str(e)}")
    
    # OpsAgent
    try:
        from app.agents.ops_agent import OpsAgent
        agents["OpsAgent"] = OpsAgent()
        logger.info("✅ OpenAI provider initialized successfully for OpsAgent")
    except Exception as e:
        logger.error(f"❌ Failed to load OpsAgent: {str(e)}")
    
    # HAL
    try:
        from app.agents.hal_agent import HALAgent
        agents["HAL"] = HALAgent()
        logger.info("✅ OpenAI provider initialized successfully for HAL")
    except Exception as e:
        logger.error(f"❌ Failed to load HAL: {str(e)}")
    
    # Ash
    try:
        from app.agents.ash_agent import AshAgent
        agents["Ash"] = AshAgent()
        logger.info("✅ OpenAI provider initialized successfully for Ash")
    except Exception as e:
        logger.error(f"❌ Failed to load Ash: {str(e)}")
    
    # LifeTree
    try:
        from app.agents.lifetree_agent import LifeTreeAgent
        agents["LifeTree"] = LifeTreeAgent()
        logger.info("✅ OpenAI provider initialized successfully for LifeTree")
    except Exception as e:
        logger.error(f"❌ Failed to load LifeTree: {str(e)}")
    
    # SiteGen
    try:
        from app.agents.sitegen_agent import SiteGenAgent
        agents["SiteGen"] = SiteGenAgent()
        logger.info("✅ OpenAI provider initialized successfully for SiteGen")
    except Exception as e:
        logger.error(f"❌ Failed to load SiteGen: {str(e)}")
    
    # NEUREAL
    try:
        from app.agents.neureal_agent import NEUREALAgent
        agents["NEUREAL"] = NEUREALAgent()
        logger.info("✅ OpenAI provider initialized successfully for NEUREAL")
    except Exception as e:
        logger.error(f"❌ Failed to load NEUREAL: {str(e)}")
    
    # Log summary
    logger.info(f"✅ Agent initialization complete. Loaded {len(agents)} agents successfully.")
    logger.info(f"✅ Available agents: {', '.join(agents.keys())}")
    
    return agents

def get_agent(agent_id: str) -> Optional[Any]:
    """
    Get an agent by ID with fallback handling.
    
    Args:
        agent_id: The agent ID to retrieve
        
    Returns:
        Optional[Any]: The agent instance or None if not found
    """
    # Try exact match first
    if agent_id in agents:
        return agents[agent_id]
    
    # Try case-insensitive match
    for key, agent in agents.items():
        if key.lower() == agent_id.lower():
            return agent
    
    # Try with different separators (hyphen vs period)
    if agent_id == "core-forge":
        return agents.get("Core.Forge")
    elif agent_id == "Core.Forge":
        return agents.get("core-forge")
    
    # Not found
    return None

def get_all_agents() -> Dict[str, Any]:
    """
    Get all loaded agents.
    
    Returns:
        Dict[str, Any]: Dictionary of all loaded agents
    """
    return agents
