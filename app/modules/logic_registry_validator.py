"""
Logic Registry Validator Module
This module provides functionality for validating logic module registry schemas.
"""

import logging
import json
import os
import jsonschema
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("app.modules.logic_registry_validator")

def load_registry_schema() -> Optional[Dict[str, Any]]:
    """
    Load the logic module registry schema.
    
    Returns:
        Dict containing the schema or None if loading fails
    """
    try:
        schema_path = os.path.join(os.path.dirname(__file__), "logic_module_registry.json")
        
        if not os.path.exists(schema_path):
            logger.error(f"Schema file not found: {schema_path}")
            print(f"❌ Schema file not found: {schema_path}")
            return None
        
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            
        logger.info(f"Successfully loaded registry schema")
        return schema
        
    except Exception as e:
        error_msg = f"Error loading registry schema: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return None

def validate_logic_modules(modules_dict: Dict[str, str]) -> bool:
    """
    Validate a dictionary of logic modules against the schema.
    
    Args:
        modules_dict: Dictionary mapping agent IDs to module paths
            
    Returns:
        Boolean indicating whether the modules dictionary is valid
    """
    try:
        schema = load_registry_schema()
        if not schema:
            return False
        
        # Create a registry object to validate
        registry = {
            "version": "1.0.0",
            "modules": modules_dict
        }
        
        # Validate against the schema
        jsonschema.validate(instance=registry, schema=schema)
        
        logger.info(f"Logic modules validated successfully")
        print(f"✅ Logic modules validated successfully")
        return True
        
    except jsonschema.exceptions.ValidationError as e:
        error_msg = f"Logic modules validation failed: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return False
    except Exception as e:
        error_msg = f"Error validating logic modules: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return False

def get_default_modules() -> Dict[str, str]:
    """
    Get the default logic modules from the registry schema.
    
    Returns:
        Dict mapping agent IDs to default module paths
    """
    try:
        schema = load_registry_schema()
        if not schema:
            return {}
        
        # Extract examples from the schema
        examples = schema.get("examples", [])
        if not examples:
            logger.warning("No examples found in schema")
            return {}
        
        # Use the first example as the default
        default_example = examples[0]
        default_modules = default_example.get("default_modules", {})
        
        logger.info(f"Loaded default modules: {default_modules}")
        return default_modules
        
    except Exception as e:
        error_msg = f"Error getting default modules: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return {}
