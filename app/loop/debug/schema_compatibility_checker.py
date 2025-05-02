"""
Schema Compatibility Checker for Loop Hardening Modules

This script verifies that all schema changes are backward compatible
and properly tagged with schema_patch_core or schema_patch_ui.
"""

import json
import os
import sys
from typing import Dict, Any, List, Set, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SCHEMA_DIR = "/home/ubuntu/repo/personal-ai-agent/app/loop/debug"
BASE_SCHEMA_FILE = "loop_trace.schema.v1.0.0.json"
CURRENT_SCHEMA_FILE = "loop_trace.schema.v1.0.2.json"
SCHEMA_PATCH_CORE_VERSION = "1.0.2"
SCHEMA_PATCH_UI_VERSION = "1.0.1"

def load_schema(file_path: str) -> Dict[str, Any]:
    """Load a JSON schema file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading schema file {file_path}: {e}")
        sys.exit(1)

def get_property_paths(schema: Dict[str, Any], prefix: str = "") -> Set[str]:
    """
    Recursively extract all property paths from a schema.
    
    Args:
        schema: The schema to extract paths from
        prefix: The current path prefix
        
    Returns:
        Set of property paths
    """
    paths = set()
    
    if not isinstance(schema, dict):
        return paths
    
    # Add current path if it's a property
    if prefix:
        paths.add(prefix)
    
    # Process properties if they exist
    if "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            new_prefix = f"{prefix}.{prop_name}" if prefix else prop_name
            paths.add(new_prefix)
            
            # Recursively process nested properties
            if isinstance(prop_schema, dict):
                if "properties" in prop_schema:
                    for nested_path in get_property_paths(prop_schema, new_prefix):
                        paths.add(nested_path)
                elif "items" in prop_schema and isinstance(prop_schema["items"], dict):
                    for nested_path in get_property_paths(prop_schema["items"], f"{new_prefix}.items"):
                        paths.add(nested_path)
    
    # Process array items if they exist
    if "items" in schema and isinstance(schema["items"], dict):
        for nested_path in get_property_paths(schema["items"], f"{prefix}.items"):
            paths.add(nested_path)
    
    return paths

def find_schema_patches(schema: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Find all properties tagged with schema_patch_core or schema_patch_ui.
    
    Args:
        schema: The schema to search
        
    Returns:
        Tuple of (core_patches, ui_patches) lists
    """
    core_patches = []
    ui_patches = []
    
    def search_for_patches(obj: Any, path: str = ""):
        if isinstance(obj, dict):
            # Check for schema patch tags in description
            if "description" in obj and isinstance(obj["description"], str):
                desc = obj["description"]
                if f"schema_patch_core: {SCHEMA_PATCH_CORE_VERSION}" in desc:
                    core_patches.append(path)
                if f"schema_patch_ui: {SCHEMA_PATCH_UI_VERSION}" in desc:
                    ui_patches.append(path)
            
            # Check for explicit schema patch properties
            if "schema_patch_core" in obj:
                core_patches.append(path)
            if "schema_patch_ui" in obj:
                ui_patches.append(path)
            
            # Recursively search nested objects
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                search_for_patches(value, new_path)
        elif isinstance(obj, list):
            # Recursively search list items
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                search_for_patches(item, new_path)
    
    search_for_patches(schema)
    return core_patches, ui_patches

def check_backward_compatibility(base_schema: Dict[str, Any], current_schema: Dict[str, Any]) -> bool:
    """
    Check if the current schema is backward compatible with the base schema.
    
    Args:
        base_schema: The base schema
        current_schema: The current schema
        
    Returns:
        True if backward compatible, False otherwise
    """
    # Get all property paths from both schemas
    base_paths = get_property_paths(base_schema)
    current_paths = get_property_paths(current_schema)
    
    # Check if all base paths exist in current schema
    missing_paths = base_paths - current_paths
    if missing_paths:
        logger.error(f"Backward compatibility issue: {len(missing_paths)} paths from base schema are missing in current schema")
        for path in sorted(missing_paths):
            logger.error(f"  Missing path: {path}")
        return False
    
    # Check if required fields are the same or a subset
    if "required" in base_schema and "required" in current_schema:
        base_required = set(base_schema["required"])
        current_required = set(current_schema["required"])
        
        if not base_required.issubset(current_required):
            missing_required = base_required - current_required
            logger.error(f"Backward compatibility issue: {len(missing_required)} required fields from base schema are not required in current schema")
            for field in sorted(missing_required):
                logger.error(f"  Missing required field: {field}")
            return False
    
    # Check if property types are compatible
    def check_property_types(base_prop: Dict[str, Any], current_prop: Dict[str, Any], path: str) -> bool:
        # Check type compatibility
        if "type" in base_prop and "type" in current_prop:
            base_type = base_prop["type"]
            current_type = current_prop["type"]
            
            # Handle array types
            if isinstance(base_type, list) and isinstance(current_type, list):
                if not set(base_type).issubset(set(current_type)):
                    logger.error(f"Type compatibility issue at {path}: base types {base_type} not subset of current types {current_type}")
                    return False
            # Handle single types
            elif isinstance(base_type, str) and isinstance(current_type, str):
                if base_type != current_type:
                    logger.error(f"Type compatibility issue at {path}: base type {base_type} != current type {current_type}")
                    return False
            # Handle mixed types
            elif isinstance(base_type, list) and isinstance(current_type, str):
                if current_type not in base_type:
                    logger.error(f"Type compatibility issue at {path}: current type {current_type} not in base types {base_type}")
                    return False
            elif isinstance(base_type, str) and isinstance(current_type, list):
                if base_type not in current_type:
                    logger.error(f"Type compatibility issue at {path}: base type {base_type} not in current types {current_type}")
                    return False
        
        # Check enum compatibility
        if "enum" in base_prop and "enum" in current_prop:
            base_enum = set(base_prop["enum"])
            current_enum = set(current_prop["enum"])
            
            if not base_enum.issubset(current_enum):
                logger.error(f"Enum compatibility issue at {path}: base enum values {base_enum} not subset of current enum values {current_enum}")
                return False
        
        return True
    
    # Recursively check property types
    def check_schema_types(base: Dict[str, Any], current: Dict[str, Any], path: str = "") -> bool:
        if "properties" in base and "properties" in current:
            for prop_name, base_prop in base["properties"].items():
                if prop_name in current["properties"]:
                    current_prop = current["properties"][prop_name]
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    
                    # Check this property's types
                    if not check_property_types(base_prop, current_prop, prop_path):
                        return False
                    
                    # Recursively check nested properties
                    if isinstance(base_prop, dict) and isinstance(current_prop, dict):
                        if not check_schema_types(base_prop, current_prop, prop_path):
                            return False
        
        # Check array items
        if "items" in base and "items" in current:
            base_items = base["items"]
            current_items = current["items"]
            
            if isinstance(base_items, dict) and isinstance(current_items, dict):
                items_path = f"{path}.items"
                
                # Check item types
                if not check_property_types(base_items, current_items, items_path):
                    return False
                
                # Recursively check nested items
                if not check_schema_types(base_items, current_items, items_path):
                    return False
        
        return True
    
    # Check property types
    if not check_schema_types(base_schema, current_schema):
        return False
    
    return True

def verify_patch_tagging(current_schema: Dict[str, Any]) -> bool:
    """
    Verify that all new properties are properly tagged with schema_patch_core or schema_patch_ui.
    
    Args:
        current_schema: The current schema
        
    Returns:
        True if all new properties are properly tagged, False otherwise
    """
    # Find all schema patches
    core_patches, ui_patches = find_schema_patches(current_schema)
    
    # Log found patches
    logger.info(f"Found {len(core_patches)} core schema patches:")
    for patch in sorted(core_patches):
        logger.info(f"  Core patch: {patch}")
    
    logger.info(f"Found {len(ui_patches)} UI schema patches:")
    for patch in sorted(ui_patches):
        logger.info(f"  UI patch: {patch}")
    
    # Check if any patches were found
    if not core_patches and not ui_patches:
        logger.error("No schema patches found. All new properties should be tagged with schema_patch_core or schema_patch_ui.")
        return False
    
    return True

def main():
    """Main function to check schema compatibility."""
    logger.info("Starting schema compatibility check")
    
    # Load schemas
    base_schema_path = os.path.join(SCHEMA_DIR, BASE_SCHEMA_FILE)
    current_schema_path = os.path.join(SCHEMA_DIR, CURRENT_SCHEMA_FILE)
    
    logger.info(f"Loading base schema from {base_schema_path}")
    base_schema = load_schema(base_schema_path)
    
    logger.info(f"Loading current schema from {current_schema_path}")
    current_schema = load_schema(current_schema_path)
    
    # Check backward compatibility
    logger.info("Checking backward compatibility")
    is_compatible = check_backward_compatibility(base_schema, current_schema)
    
    if is_compatible:
        logger.info("✅ Schema is backward compatible")
    else:
        logger.error("❌ Schema is not backward compatible")
        return False
    
    # Verify patch tagging
    logger.info("Verifying patch tagging")
    is_tagged = verify_patch_tagging(current_schema)
    
    if is_tagged:
        logger.info("✅ All new properties are properly tagged")
    else:
        logger.error("❌ Some new properties are not properly tagged")
        return False
    
    logger.info("Schema compatibility check completed successfully")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
