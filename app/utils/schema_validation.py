"""
Schema Validation Utilities

This module provides utility functions for schema validation and error handling
across all API endpoints in the application.
"""

import logging
from typing import Dict, Any, Optional, List, Union, Type
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException
import datetime
import json
import os

# Configure logging
logger = logging.getLogger("app.utils.schema_validation")

def validate_request_body(request_data: Dict[str, Any], model_class: Type[BaseModel]) -> BaseModel:
    """
    Validate request data against a Pydantic model and provide default values.
    
    Args:
        request_data: The request data to validate
        model_class: The Pydantic model class to validate against
        
    Returns:
        Validated model instance
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        # Add common default values if they're in the model fields but not in the request
        model_fields = model_class.__annotations__
        
        # Common default values for frequently required fields
        common_defaults = {
            "project_id": "default_project",
            "agent_id": "system",
            "max_loops": 5,
            "planned_agents": ["ORCHESTRATOR"],
            "tools": ["default_tool"],
            "loop_id": f"loop_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "context": {}
        }
        
        # Only add defaults for fields that exist in the model but not in the request
        for field, default_value in common_defaults.items():
            if field in model_fields and field not in request_data:
                request_data[field] = default_value
        
        # Validate with the model
        return model_class(**request_data)
    
    except ValidationError as ve:
        # Log the validation error
        logger.warning(f"Schema validation error: {str(ve)}")
        
        # Extract error details
        error_details = []
        for error in ve.errors():
            error_details.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        # Create standardized error response
        error_response = {
            "status": "error",
            "message": "Schema validation error",
            "details": error_details,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        # Log the error for analysis
        log_validation_error(error_response)
        
        # Raise HTTPException with detailed error information
        raise HTTPException(
            status_code=422,
            detail=error_response
        )
    
    except Exception as e:
        # Log the general error
        logger.error(f"Unexpected error during validation: {str(e)}")
        
        # Create standardized error response
        error_response = {
            "status": "error",
            "message": f"Unexpected error during validation: {str(e)}",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        # Log the error for analysis
        log_general_error(error_response)
        
        # Raise HTTPException with error information
        raise HTTPException(
            status_code=500,
            detail=error_response
        )

def create_error_response(message: str, status_code: int = 500, **kwargs) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        **kwargs: Additional fields to include in the response
        
    Returns:
        Standardized error response dictionary
    """
    response = {
        "status": "error",
        "message": message,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "status_code": status_code
    }
    
    # Add additional fields
    response.update(kwargs)
    
    return response

def log_validation_error(error_response: Dict[str, Any]) -> None:
    """
    Log validation errors to a file for analysis.
    
    Args:
        error_response: The error response details
    """
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs/validation_errors", exist_ok=True)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "error_details": error_response
        }
        
        # Append to log file
        log_file = "logs/validation_errors/schema_errors.json"
        
        # Check if log file exists
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
            except json.JSONDecodeError:
                logs = []
        else:
            logs = []
        
        # Append new log entry
        logs.append(log_entry)
        
        # Write updated logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
    except Exception as log_error:
        logger.error(f"Failed to log validation error: {str(log_error)}")

def log_general_error(error_response: Dict[str, Any]) -> None:
    """
    Log general errors to a file for analysis.
    
    Args:
        error_response: The error response details
    """
    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs/general_errors", exist_ok=True)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "error_details": error_response
        }
        
        # Append to log file
        log_file = "logs/general_errors/server_errors.json"
        
        # Check if log file exists
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
            except json.JSONDecodeError:
                logs = []
        else:
            logs = []
        
        # Append new log entry
        logs.append(log_entry)
        
        # Write updated logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
    except Exception as log_error:
        logger.error(f"Failed to log general error: {str(log_error)}")
