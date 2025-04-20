"""
Plan Validator Module

This module provides functionality to validate loop plans against the defined schema.
"""

import json
import os
import jsonschema
from datetime import datetime

# Path to the schema file
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                          'schemas', 'orchestrator', 'loop_plan.schema.json')

def load_schema():
    """
    Load the loop plan schema from the schema file.
    
    Returns:
        dict: The loaded schema
    """
    try:
        with open(SCHEMA_PATH, 'r') as schema_file:
            return json.load(schema_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Error loading schema: {str(e)}")

def validate_loop_plan(plan_object: dict) -> list:
    """
    Validates the given loop plan against the schema.
    Returns a list of errors, or an empty list if valid.
    
    Args:
        plan_object (dict): The loop plan to validate
        
    Returns:
        list: List of validation errors, empty if valid
    """
    errors = []
    
    try:
        schema = load_schema()
        validator = jsonschema.Draft7Validator(schema)
        validation_errors = list(validator.iter_errors(plan_object))
        
        for error in validation_errors:
            # Format the error message
            if error.path:
                path = '.'.join(str(p) for p in error.path)
                errors.append(f"Error at '{path}': {error.message}")
            else:
                errors.append(f"Error: {error.message}")
                
    except ValueError as e:
        errors.append(str(e))
    except Exception as e:
        errors.append(f"Unexpected error during validation: {str(e)}")
    
    return errors

def log_validation_result(plan_object: dict, errors: list) -> dict:
    """
    Logs the validation result to a trace object.
    
    Args:
        plan_object (dict): The loop plan that was validated
        errors (list): List of validation errors
        
    Returns:
        dict: Trace object with validation result
    """
    loop_id = plan_object.get('loop_id', 'unknown')
    status = "passed" if not errors else "failed"
    
    trace = {
        "trace_id": f"loop_{loop_id}_plan",
        "action": "plan_validated",
        "status": status,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    if errors:
        trace["errors"] = errors
    
    return trace

def validate_and_log(plan_object: dict) -> tuple:
    """
    Validates the loop plan and logs the result.
    
    Args:
        plan_object (dict): The loop plan to validate
        
    Returns:
        tuple: (is_valid, errors, trace)
    """
    errors = validate_loop_plan(plan_object)
    trace = log_validation_result(plan_object, errors)
    is_valid = len(errors) == 0
    
    return is_valid, errors, trace
