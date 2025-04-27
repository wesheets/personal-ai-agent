"""
Module Validator

This module validates modules listed in the Product/Infrastructure Cognition Engine (PICE).
It checks if modules exist and can be imported without errors.
"""

import os
import importlib.util
import sys
import logging
from typing import Dict, List, Any, Tuple

# Configure logging
logger = logging.getLogger('startup_validation.module_validator')

def validate_modules(pice_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Validate all modules listed in the PICE.
    
    Args:
        pice_data: The loaded PICE data
        
    Returns:
        Tuple containing:
        - Health score as a percentage (0-100)
        - List of drift issues detected
    """
    logger.info("Starting module validation")
    
    if "modules" not in pice_data:
        logger.error("PICE data does not contain 'modules' key")
        return 0.0, [{"type": "module", "path": "PICE", "issue": "Missing 'modules' key in PICE"}]
    
    modules = pice_data["modules"]
    if not modules:
        logger.warning("No modules found in PICE")
        return 100.0, []
    
    valid_count = 0
    drift_issues = []
    
    for module in modules:
        if "name" not in module:
            logger.error("Module missing 'name' attribute")
            drift_issues.append({
                "type": "module",
                "path": "unknown",
                "issue": "Module missing 'name' attribute"
            })
            continue
        
        module_name = module["name"]
        logger.info(f"Validating module: {module_name}")
        
        # Check if module exists
        if not check_module_exists(module_name):
            logger.error(f"Module {module_name} does not exist")
            drift_issues.append({
                "type": "module",
                "path": module_name,
                "issue": "Module file does not exist"
            })
            continue
        
        # Check if module is importable
        if not check_module_importable(module_name):
            logger.error(f"Module {module_name} is not importable")
            drift_issues.append({
                "type": "module",
                "path": module_name,
                "issue": "Module cannot be imported (syntax errors or missing dependencies)"
            })
            continue
        
        # If we get here, the module is valid
        valid_count += 1
        logger.info(f"Module {module_name} validated successfully")
    
    # Calculate health score
    health_score = (valid_count / len(modules)) * 100 if modules else 100.0
    logger.info(f"Module validation complete. Health score: {health_score:.1f}%")
    
    return health_score, drift_issues

def check_module_exists(module_name: str) -> bool:
    """
    Check if a module file exists.
    
    Args:
        module_name: Name of the module to check
        
    Returns:
        True if the module file exists, False otherwise
    """
    # Convert module name to file path
    module_path = convert_module_name_to_path(module_name)
    
    # Check if file exists
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    full_path = os.path.join(base_path, module_path.lstrip('/'))
    
    exists = os.path.isfile(full_path)
    logger.debug(f"Module file check for {module_name}: {'exists' if exists else 'not found'} at {full_path}")
    return exists

def check_module_importable(module_name: str) -> bool:
    """
    Check if a module can be imported without errors.
    
    Args:
        module_name: Name of the module to check
        
    Returns:
        True if the module can be imported, False otherwise
    """
    # Convert module name to file path and import path
    file_path = convert_module_name_to_path(module_name)
    import_path = convert_module_name_to_import_path(module_name)
    
    # Get full path to module file
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    full_path = os.path.join(base_path, file_path.lstrip('/'))
    
    if not os.path.isfile(full_path):
        logger.debug(f"Cannot import {module_name}: file not found at {full_path}")
        return False
    
    try:
        # Try to import the module
        spec = importlib.util.spec_from_file_location(import_path, full_path)
        if spec is None:
            logger.debug(f"Cannot import {module_name}: spec_from_file_location returned None")
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        logger.debug(f"Successfully imported {module_name}")
        return True
    except Exception as e:
        logger.debug(f"Error importing {module_name}: {str(e)}")
        return False

def convert_module_name_to_path(module_name: str) -> str:
    """
    Convert a module name to its file path.
    
    Args:
        module_name: Name of the module (e.g., "auth.login")
        
    Returns:
        File path for the module (e.g., "/app/modules/auth/login.py")
    """
    # Replace dots with slashes and add .py extension
    path_parts = module_name.split('.')
    
    # Handle different module patterns
    if len(path_parts) == 1:
        # Single module name, likely in /app/modules/
        return f"/app/modules/{path_parts[0]}.py"
    elif len(path_parts) > 1:
        # Nested module, construct path accordingly
        return f"/app/modules/{'/'.join(path_parts)}.py"
    else:
        # Fallback for empty module name
        return "/app/modules/unknown.py"

def convert_module_name_to_import_path(module_name: str) -> str:
    """
    Convert a module name to its import path.
    
    Args:
        module_name: Name of the module (e.g., "auth.login")
        
    Returns:
        Import path for the module (e.g., "app.modules.auth.login")
    """
    # Add app.modules prefix
    return f"app.modules.{module_name}"
