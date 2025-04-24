"""
Schema Discovery Utility

This module provides utilities for discovering schema classes when imports fail,
helping to make the system more resilient to schema drift and import issues.
"""

import logging
from pathlib import Path
import os
import importlib
from typing import Optional, List, Dict, Any, Tuple

# Configure logging
logger = logging.getLogger("schema_discovery")

def locate_schema_class(class_name: str) -> Optional[str]:
    """
    Locate a schema class in the app/schemas directory.
    
    Args:
        class_name: The name of the class to locate
        
    Returns:
        The file path where the class was found, or None if not found
    """
    # Check in app/schemas directory
    schema_dir = Path("app/schemas")
    if schema_dir.exists():
        logger.info(f"🔍 Searching for {class_name} in {schema_dir}")
        for file in schema_dir.glob("*.py"):
            try:
                with open(file, "r") as f:
                    content = f.read()
                    if f"class {class_name}" in content:
                        logger.info(f"✅ Fallback found {class_name} in {file}")
                        return str(file)
            except Exception as e:
                logger.warning(f"⚠️ Error reading file {file}: {e}")
    
    # Check in schemas directory (without app/ prefix)
    schema_dir = Path("schemas")
    if schema_dir.exists():
        logger.info(f"🔍 Searching for {class_name} in {schema_dir}")
        for file in schema_dir.glob("*.py"):
            try:
                with open(file, "r") as f:
                    content = f.read()
                    if f"class {class_name}" in content:
                        logger.info(f"✅ Fallback found {class_name} in {file}")
                        return str(file)
            except Exception as e:
                logger.warning(f"⚠️ Error reading file {file}: {e}")
    
    # Check in current directory
    current_dir = Path(".")
    logger.info(f"🔍 Searching for {class_name} in current directory")
    for file in current_dir.glob("*.py"):
        try:
            with open(file, "r") as f:
                content = f.read()
                if f"class {class_name}" in content:
                    logger.info(f"✅ Fallback found {class_name} in {file}")
                    return str(file)
        except Exception as e:
            logger.warning(f"⚠️ Error reading file {file}: {e}")
    
    logger.warning(f"❌ Could not locate schema class {class_name} in any known paths")
    return None

def import_schema_class(class_name: str, module_path: Optional[str] = None) -> Any:
    """
    Import a schema class from a module path.
    
    Args:
        class_name: The name of the class to import
        module_path: Optional module path to import from
        
    Returns:
        The imported class, or None if import failed
    """
    if module_path:
        try:
            # Convert file path to module path
            if module_path.endswith(".py"):
                module_path = module_path[:-3]
            module_path = module_path.replace("/", ".")
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the class from the module
            if hasattr(module, class_name):
                logger.info(f"✅ Successfully imported {class_name} from {module_path}")
                return getattr(module, class_name)
        except Exception as e:
            logger.warning(f"⚠️ Failed to import {class_name} from {module_path}: {e}")
    
    # Try common schema modules
    common_modules = [
        "app.schemas.loop_schema",
        "schemas.loop_schema",
        "app.schemas.hal_schema",
        "schemas.hal_schema",
        "app.schemas.orchestrator_schema",
        "schemas.orchestrator_schema",
        "app.schemas.common",
        "schemas.common"
    ]
    
    for module_path in common_modules:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, class_name):
                logger.info(f"✅ Successfully imported {class_name} from {module_path}")
                return getattr(module, class_name)
        except Exception:
            pass
    
    logger.warning(f"❌ Failed to import {class_name} from any known modules")
    return None

def discover_and_import_schema(class_name: str) -> Tuple[Any, str]:
    """
    Discover and import a schema class.
    
    Args:
        class_name: The name of the class to discover and import
        
    Returns:
        A tuple of (imported_class, import_statement) or (None, error_message)
    """
    # First, try to locate the schema class
    file_path = locate_schema_class(class_name)
    
    if file_path:
        # Convert file path to module path
        if file_path.endswith(".py"):
            file_path = file_path[:-3]
        module_path = file_path.replace("/", ".")
        
        # Try to import the class
        schema_class = import_schema_class(class_name, module_path)
        
        if schema_class:
            import_statement = f"from {module_path} import {class_name}"
            logger.info(f"🛠️ Suggested import: {import_statement}")
            return schema_class, import_statement
    
    # If we couldn't locate or import the class, return None with an error message
    error_message = f"Could not locate schema '{class_name}' in any known schema paths."
    return None, error_message

def log_schema_error_to_memory(loop_id: str, class_name: str, error_message: str) -> None:
    """
    Log a schema error to memory for self-debugging.
    
    Args:
        loop_id: The loop ID to log the error for
        class_name: The name of the class that couldn't be found
        error_message: The error message
    """
    try:
        # Import memory module
        from app.modules.orchestrator_memory import log_loop_event
        
        # Log the error
        log_loop_event(
            loop_id=loop_id,
            project_id=loop_id,
            agent="schema_discovery",
            task=f"Locate schema class {class_name}",
            status="failed",
            additional_data={
                "error": error_message,
                "schema_class": class_name
            }
        )
        
        logger.info(f"✅ Logged schema error to memory for loop {loop_id}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to log schema error to memory: {e}")

def get_structured_error(class_name: str, error_message: str) -> Dict[str, Any]:
    """
    Get a structured error response for a missing schema.
    
    Args:
        class_name: The name of the class that couldn't be found
        error_message: The error message
        
    Returns:
        A structured error response
    """
    return {
        "error": "MissingSchema",
        "schema": class_name,
        "message": error_message,
        "hints": [
            "Check the module for a valid import path",
            "Ensure schema file exists under app/schemas/",
            "Verify that the class name is spelled correctly",
            "Consider creating a fallback schema class"
        ]
    }
