"""
Debug HAL Schema Module

This module defines a temporary debug endpoint to check if the HAL schema file
exists at runtime and return detailed filesystem information.
"""

import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# Create router
router = APIRouter(tags=["debug"])

@router.get("/debug/hal-schema")
async def check_hal_schema_existence():
    """
    Check if the HAL schema file exists at runtime and return detailed information.
    
    This endpoint verifies the existence of the HAL schema file at both the expected
    runtime path and the repository path, and returns detailed filesystem information
    to help diagnose deployment issues.
    
    Returns:
        Dict containing file existence status and detailed filesystem information
    """
    try:
        # Define paths to check
        expected_runtime_path = "/app/schemas/hal_agent.schema.json"
        repository_path = "/app/schemas/schemas/hal_agent.schema.json"
        absolute_runtime_path = os.path.abspath(expected_runtime_path)
        absolute_repo_path = os.path.abspath(repository_path)
        
        # Check if files exist
        expected_path_exists = os.path.exists(expected_runtime_path)
        repo_path_exists = os.path.exists(repository_path)
        
        # Get file details if they exist
        expected_path_details = {}
        repo_path_details = {}
        
        if expected_path_exists:
            stats = os.stat(expected_runtime_path)
            with open(expected_runtime_path, 'r') as f:
                content = f.read()
            expected_path_details = {
                "size": stats.st_size,
                "permissions": oct(stats.st_mode)[-3:],
                "last_modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "content": content,
                "is_readable": os.access(expected_runtime_path, os.R_OK)
            }
        
        if repo_path_exists:
            stats = os.stat(repository_path)
            with open(repository_path, 'r') as f:
                content = f.read()
            repo_path_details = {
                "size": stats.st_size,
                "permissions": oct(stats.st_mode)[-3:],
                "last_modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "content": content,
                "is_readable": os.access(repository_path, os.R_OK)
            }
        
        # Get environment information
        env_info = {
            "current_working_directory": os.getcwd(),
            "home_directory": os.environ.get("HOME", "Not set"),
            "user": os.environ.get("USER", "Not set"),
            "hostname": os.environ.get("HOSTNAME", "Not set"),
            "app_directory_exists": os.path.exists("/app"),
            "app_schemas_directory_exists": os.path.exists("/app/schemas"),
            "app_schemas_schemas_directory_exists": os.path.exists("/app/schemas/schemas")
        }
        
        # Check if parent directories exist and are readable
        path_analysis = {
            "app_exists": os.path.exists("/app"),
            "app_readable": os.access("/app", os.R_OK) if os.path.exists("/app") else False,
            "app_schemas_exists": os.path.exists("/app/schemas"),
            "app_schemas_readable": os.access("/app/schemas", os.R_OK) if os.path.exists("/app/schemas") else False,
            "app_schemas_schemas_exists": os.path.exists("/app/schemas/schemas"),
            "app_schemas_schemas_readable": os.access("/app/schemas/schemas", os.R_OK) if os.path.exists("/app/schemas/schemas") else False
        }
        
        # List directory contents if they exist
        dir_contents = {}
        if os.path.exists("/app/schemas"):
            dir_contents["app_schemas_contents"] = os.listdir("/app/schemas")
        if os.path.exists("/app/schemas/schemas"):
            dir_contents["app_schemas_schemas_contents"] = os.listdir("/app/schemas/schemas")
        
        # Prepare response
        response = {
            "timestamp": datetime.now().isoformat(),
            "expected_runtime_path": expected_runtime_path,
            "absolute_runtime_path": absolute_runtime_path,
            "expected_path_exists": expected_path_exists,
            "expected_path_details": expected_path_details,
            "repository_path": repository_path,
            "absolute_repo_path": absolute_repo_path,
            "repo_path_exists": repo_path_exists,
            "repo_path_details": repo_path_details,
            "environment_info": env_info,
            "path_analysis": path_analysis,
            "directory_contents": dir_contents
        }
        
        return response
    except Exception as e:
        # Handle exceptions and return appropriate error response
        raise HTTPException(
            status_code=500,
            detail=f"Error checking HAL schema existence: {str(e)}"
        )
