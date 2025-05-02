"""
Component Validator

This module validates UI components listed in the Product/Infrastructure Cognition Engine (PICE).
It checks if components are exportable (React/JSX).
"""

import os
import re
import logging
from typing import Dict, List, Any, Tuple

# Configure logging
logger = logging.getLogger('startup_validation.component_validator')

def validate_components(pice_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Validate all components listed in the PICE.
    
    Args:
        pice_data: The loaded PICE data
        
    Returns:
        Tuple containing:
        - Health score as a percentage (0-100)
        - List of drift issues detected
    """
    logger.info("Starting component validation")
    
    if "components" not in pice_data:
        logger.warning("PICE data does not contain 'components' key")
        return 100.0, []
    
    components = pice_data["components"]
    if not components:
        logger.warning("No components found in PICE")
        return 100.0, []
    
    valid_count = 0
    drift_issues = []
    
    for component in components:
        if "name" not in component:
            logger.error("Component missing 'name' attribute")
            drift_issues.append({
                "type": "component",
                "path": "unknown",
                "issue": "Component missing 'name' attribute"
            })
            continue
            
        if "path" not in component:
            logger.error(f"Component {component['name']} missing 'path' attribute")
            drift_issues.append({
                "type": "component",
                "path": component['name'],
                "issue": "Component missing 'path' attribute"
            })
            continue
        
        component_name = component["name"]
        component_path = component["path"]
        logger.info(f"Validating component: {component_name} (path: {component_path})")
        
        # Check if component exists
        if not check_component_exists(component_path):
            logger.error(f"Component file {component_path} does not exist")
            drift_issues.append({
                "type": "component",
                "path": component_path,
                "issue": "Component file does not exist"
            })
            continue
        
        # Check if component is exportable
        if not check_component_exportable(component_path):
            logger.error(f"Component {component_name} is not exportable")
            drift_issues.append({
                "type": "component",
                "path": component_path,
                "issue": "Component is not exportable (missing export statement or invalid React/JSX)"
            })
            continue
        
        # If we get here, the component is valid
        valid_count += 1
        logger.info(f"Component {component_name} validated successfully")
    
    # Calculate health score
    health_score = (valid_count / len(components)) * 100 if components else 100.0
    logger.info(f"Component validation complete. Health score: {health_score:.1f}%")
    
    return health_score, drift_issues

def check_component_exists(component_path: str) -> bool:
    """
    Check if a component file exists.
    
    Args:
        component_path: Path to the component to check
        
    Returns:
        True if the component file exists, False otherwise
    """
    # Normalize component path
    if not component_path.startswith('/'):
        component_path = f"/frontend/components/{component_path}"
    
    # Check if file exists
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    full_path = os.path.join(base_path, component_path.lstrip('/'))
    
    # Check for both .jsx and .tsx extensions if no extension is provided
    if not (full_path.endswith('.jsx') or full_path.endswith('.tsx') or full_path.endswith('.js') or full_path.endswith('.ts')):
        for ext in ['.jsx', '.tsx', '.js', '.ts']:
            if os.path.isfile(f"{full_path}{ext}"):
                full_path = f"{full_path}{ext}"
                break
    
    exists = os.path.isfile(full_path)
    logger.debug(f"Component file check: {'exists' if exists else 'not found'} at {full_path}")
    return exists

def check_component_exportable(component_path: str) -> bool:
    """
    Check if a component is exportable (React/JSX).
    
    Args:
        component_path: Path to the component to check
        
    Returns:
        True if the component is exportable, False otherwise
    """
    # Normalize component path
    if not component_path.startswith('/'):
        component_path = f"/frontend/components/{component_path}"
    
    # Get full path to component file
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    full_path = os.path.join(base_path, component_path.lstrip('/'))
    
    # Check for both .jsx and .tsx extensions if no extension is provided
    if not (full_path.endswith('.jsx') or full_path.endswith('.tsx') or full_path.endswith('.js') or full_path.endswith('.ts')):
        for ext in ['.jsx', '.tsx', '.js', '.ts']:
            if os.path.isfile(f"{full_path}{ext}"):
                full_path = f"{full_path}{ext}"
                break
    
    if not os.path.isfile(full_path):
        logger.debug(f"Cannot check if component is exportable: file not found at {full_path}")
        return False
    
    try:
        # Read the component file
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Check for export statements
        export_patterns = [
            r'export\s+default\s+',
            r'export\s+const\s+\w+\s*=',
            r'export\s+function\s+\w+\s*\(',
            r'export\s+class\s+\w+\s+',
            r'module\.exports\s*='
        ]
        
        for pattern in export_patterns:
            if re.search(pattern, content):
                logger.debug(f"Component at {full_path} is exportable")
                return True
        
        logger.debug(f"No export statement found in component at {full_path}")
        return False
    except Exception as e:
        logger.debug(f"Error checking if component is exportable: {str(e)}")
        return False
