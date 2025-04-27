"""
Endpoint Validator

This module validates endpoints listed in the Product/Infrastructure Cognition Engine (PICE).
It performs a light check to verify that the path exists in router maps.
"""

import os
import importlib.util
import sys
import logging
import re
from typing import Dict, List, Any, Tuple

# Configure logging
logger = logging.getLogger('startup_validation.endpoint_validator')

def validate_endpoints(pice_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Validate all endpoints listed in the PICE.
    
    Args:
        pice_data: The loaded PICE data
        
    Returns:
        Tuple containing:
        - Health score as a percentage (0-100)
        - List of drift issues detected
    """
    logger.info("Starting endpoint validation")
    
    if "endpoints" not in pice_data:
        logger.warning("PICE data does not contain 'endpoints' key - this is optional")
        return 100.0, []
    
    endpoints = pice_data["endpoints"]
    if not endpoints:
        logger.warning("No endpoints found in PICE")
        return 100.0, []
    
    valid_count = 0
    drift_issues = []
    
    for endpoint in endpoints:
        if "path" not in endpoint:
            logger.error("Endpoint missing 'path' attribute")
            drift_issues.append({
                "type": "endpoint",
                "path": "unknown",
                "issue": "Endpoint missing 'path' attribute"
            })
            continue
            
        if "method" not in endpoint:
            logger.error(f"Endpoint {endpoint['path']} missing 'method' attribute")
            drift_issues.append({
                "type": "endpoint",
                "path": endpoint['path'],
                "issue": "Endpoint missing 'method' attribute"
            })
            continue
        
        endpoint_path = endpoint["path"]
        endpoint_method = endpoint["method"]
        logger.info(f"Validating endpoint: {endpoint_method} {endpoint_path}")
        
        # Check if endpoint exists in router maps
        if not check_endpoint_exists(endpoint_path, endpoint_method):
            logger.error(f"Endpoint {endpoint_method} {endpoint_path} does not exist in router maps")
            drift_issues.append({
                "type": "endpoint",
                "path": endpoint_path,
                "issue": f"Endpoint {endpoint_method} {endpoint_path} not found in router maps"
            })
            continue
        
        # Check if endpoint has schema validation
        if not check_endpoint_schema_validation(endpoint_path, endpoint_method):
            logger.warning(f"Endpoint {endpoint_method} {endpoint_path} does not have schema validation")
            drift_issues.append({
                "type": "endpoint",
                "path": endpoint_path,
                "issue": "Missing schema validation (response model not attached)"
            })
            # Continue validation - this is a warning, not an error
        
        # If we get here, the endpoint exists (even if it lacks schema validation)
        valid_count += 1
        logger.info(f"Endpoint {endpoint_method} {endpoint_path} validated successfully")
    
    # Calculate health score
    health_score = (valid_count / len(endpoints)) * 100 if endpoints else 100.0
    logger.info(f"Endpoint validation complete. Health score: {health_score:.1f}%")
    
    return health_score, drift_issues

def check_endpoint_exists(endpoint_path: str, method: str) -> bool:
    """
    Check if an endpoint path exists in router maps.
    
    Args:
        endpoint_path: Path of the endpoint to check
        method: HTTP method of the endpoint
        
    Returns:
        True if the endpoint exists in router maps, False otherwise
    """
    # This is a light check - we're just looking for router definitions
    # that match the endpoint path, not actually making HTTP requests
    
    # Find router files that might contain this endpoint
    router_files = find_router_files_for_endpoint(endpoint_path)
    
    if not router_files:
        logger.debug(f"No router files found for endpoint {method} {endpoint_path}")
        return False
    
    # Check each router file for the endpoint
    for router_file in router_files:
        if check_endpoint_in_router_file(router_file, endpoint_path, method):
            logger.debug(f"Endpoint {method} {endpoint_path} found in router file {router_file}")
            return True
    
    logger.debug(f"Endpoint {method} {endpoint_path} not found in any router files")
    return False

def check_endpoint_schema_validation(endpoint_path: str, method: str) -> bool:
    """
    Check if an endpoint has schema validation.
    
    Args:
        endpoint_path: Path of the endpoint to check
        method: HTTP method of the endpoint
        
    Returns:
        True if the endpoint has schema validation, False otherwise
    """
    # Find router files that might contain this endpoint
    router_files = find_router_files_for_endpoint(endpoint_path)
    
    if not router_files:
        logger.debug(f"No router files found for endpoint {method} {endpoint_path}")
        return False
    
    # Check each router file for schema validation
    for router_file in router_files:
        if check_schema_validation_in_router_file(router_file, endpoint_path, method):
            logger.debug(f"Schema validation found for endpoint {method} {endpoint_path} in {router_file}")
            return True
    
    logger.debug(f"No schema validation found for endpoint {method} {endpoint_path}")
    return False

def find_router_files_for_endpoint(endpoint_path: str) -> List[str]:
    """
    Find router files that might contain the specified endpoint.
    
    Args:
        endpoint_path: Path of the endpoint
        
    Returns:
        List of router file paths
    """
    # Extract the first part of the path to determine the module
    path_parts = endpoint_path.strip('/').split('/')
    if not path_parts:
        return []
    
    module_name = path_parts[0]
    
    # Look for router files in the module directory
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    module_dir = os.path.join(base_path, "app", "modules", module_name)
    router_files = []
    
    if os.path.isdir(module_dir):
        # Look for router.py, routes.py, api.py, etc.
        router_patterns = ["router.py", "routes.py", "api.py", "endpoints.py"]
        for pattern in router_patterns:
            router_path = os.path.join(module_dir, pattern)
            if os.path.isfile(router_path):
                router_files.append(router_path)
        
        # Also check for nested routers
        if len(path_parts) > 1:
            nested_dir = os.path.join(module_dir, path_parts[1])
            if os.path.isdir(nested_dir):
                for pattern in router_patterns:
                    router_path = os.path.join(nested_dir, pattern)
                    if os.path.isfile(router_path):
                        router_files.append(router_path)
    
    # If no specific router files found, look for any Python files in the module
    if not router_files and os.path.isdir(module_dir):
        for file in os.listdir(module_dir):
            if file.endswith(".py"):
                router_files.append(os.path.join(module_dir, file))
    
    return router_files

def check_endpoint_in_router_file(router_file: str, endpoint_path: str, method: str) -> bool:
    """
    Check if an endpoint is defined in a router file.
    
    Args:
        router_file: Path to the router file
        endpoint_path: Path of the endpoint
        method: HTTP method of the endpoint
        
    Returns:
        True if the endpoint is defined in the router file, False otherwise
    """
    try:
        with open(router_file, 'r') as f:
            content = f.read()
        
        # Look for FastAPI route definitions
        # This is a simple check that looks for patterns like:
        # @router.get("/path")
        # @app.post("/path")
        # etc.
        
        # Escape special characters in the endpoint path for regex
        escaped_path = re.escape(endpoint_path)
        
        # Create patterns to match different route definition styles
        patterns = [
            rf'@\w+\.{method.lower()}\s*\(\s*[\'"]({escaped_path}|{escaped_path.lstrip("/")})[\'"]',
            rf'@\w+\.route\s*\(\s*[\'"]({escaped_path}|{escaped_path.lstrip("/")})[\'"].*?methods=\s*\[.*?[\'"]({method.upper()}|{method.lower()})[\'"]'
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.DOTALL):
                return True
        
        return False
    except Exception as e:
        logger.debug(f"Error checking endpoint in router file {router_file}: {str(e)}")
        return False

def check_schema_validation_in_router_file(router_file: str, endpoint_path: str, method: str) -> bool:
    """
    Check if an endpoint has schema validation in a router file.
    
    Args:
        router_file: Path to the router file
        endpoint_path: Path of the endpoint
        method: HTTP method of the endpoint
        
    Returns:
        True if the endpoint has schema validation, False otherwise
    """
    try:
        with open(router_file, 'r') as f:
            content = f.read()
        
        # Escape special characters in the endpoint path for regex
        escaped_path = re.escape(endpoint_path)
        
        # Look for route definition with response_model or similar schema validation
        patterns = [
            rf'@\w+\.{method.lower()}\s*\(\s*[\'"]({escaped_path}|{escaped_path.lstrip("/")})[\'"].*?response_model\s*=',
            rf'@\w+\.{method.lower()}\s*\(\s*[\'"]({escaped_path}|{escaped_path.lstrip("/")})[\'"].*?responses\s*=',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.DOTALL):
                return True
        
        return False
    except Exception as e:
        logger.debug(f"Error checking schema validation in router file {router_file}: {str(e)}")
        return False
