"""
Manifest Manager Utility

This module provides utilities for managing the system manifest,
which serves as a single source of truth for system introspection.
"""

import json
import os
import logging
import datetime
import hashlib
from typing import Dict, Any, List, Optional, Union

# Configure logging
logger = logging.getLogger("manifest_manager")

# Constants
MANIFEST_PATH = os.path.join("app", "system_manifest.json")
MANIFEST_VERSION = "1.0.0"

# Global manifest cache
_manifest_cache = None

def initialize_manifest() -> Dict[str, Any]:
    """
    Initialize the system manifest.
    If the manifest doesn't exist, create it with default values.
    
    Returns:
        The manifest data as a dictionary
    """
    global _manifest_cache
    
    try:
        # Load or create manifest
        manifest_data = load_manifest()
        
        # Update hardening layers
        manifest_data["hardening_layers"]["schema_checksum_tracking"] = True
        manifest_data["hardening_layers"]["schema_discovery_fallback"] = True
        
        # Save updated manifest
        save_manifest(manifest_data)
        
        # Cache manifest
        _manifest_cache = manifest_data
        
        logger.info("✅ System manifest initialized successfully")
        return manifest_data
    except Exception as e:
        logger.error(f"❌ Error initializing manifest: {str(e)}")
        return create_default_manifest()

def get_manifest() -> Dict[str, Any]:
    """
    Get the current system manifest.
    If the manifest is not cached, load it from disk.
    
    Returns:
        The manifest data as a dictionary
    """
    global _manifest_cache
    
    if _manifest_cache is None:
        _manifest_cache = load_manifest()
    
    return _manifest_cache

def register_system_boot() -> bool:
    """
    Register a system boot event in the manifest.
    
    Returns:
        True if the event was registered successfully, False otherwise
    """
    try:
        # Load current manifest
        manifest_data = get_manifest()
        
        # Ensure manifest_meta section exists
        if "manifest_meta" not in manifest_data:
            manifest_data["manifest_meta"] = {
                "version": MANIFEST_VERSION,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "last_updated": datetime.datetime.utcnow().isoformat()
            }
        
        # Add boot event
        if "boot_events" not in manifest_data["manifest_meta"]:
            manifest_data["manifest_meta"]["boot_events"] = []
        
        boot_event = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "version": MANIFEST_VERSION
        }
        
        manifest_data["manifest_meta"]["boot_events"].append(boot_event)
        
        # Save updated manifest
        return save_manifest(manifest_data)
    except Exception as e:
        logger.error(f"❌ Error registering system boot: {str(e)}")
        return False

def register_loaded_routes(route_modules: List[str]) -> bool:
    """
    Register loaded route modules in the manifest.
    
    Args:
        route_modules: List of route module names
        
    Returns:
        True if the routes were registered successfully, False otherwise
    """
    try:
        # Load current manifest
        manifest_data = get_manifest()
        
        # Ensure manifest_meta section exists
        if "manifest_meta" not in manifest_data:
            manifest_data["manifest_meta"] = {
                "version": MANIFEST_VERSION,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "last_updated": datetime.datetime.utcnow().isoformat()
            }
        
        # Update loaded routes
        manifest_data["manifest_meta"]["loaded_routes"] = route_modules
        
        # Save updated manifest
        return save_manifest(manifest_data)
    except Exception as e:
        logger.error(f"❌ Error registering loaded routes: {str(e)}")
        return False

def load_manifest() -> Dict[str, Any]:
    """
    Load the system manifest from disk.
    If the manifest doesn't exist, create it with default values.
    
    Returns:
        The manifest data as a dictionary
    """
    try:
        # Check if manifest exists
        if not os.path.exists(MANIFEST_PATH):
            logger.info(f"🔍 Manifest not found at {MANIFEST_PATH}, creating default manifest")
            return create_default_manifest()
        
        # Load manifest from disk
        with open(MANIFEST_PATH, "r") as f:
            manifest_data = json.load(f)
            
        logger.info(f"✅ Successfully loaded manifest from {MANIFEST_PATH}")
        return manifest_data
    except Exception as e:
        logger.error(f"❌ Error loading manifest: {str(e)}")
        logger.info("🔄 Creating default manifest due to load error")
        return create_default_manifest()

def save_manifest(manifest_data: Dict[str, Any]) -> bool:
    """
    Save the system manifest to disk with validation.
    
    Args:
        manifest_data: The manifest data to save
        
    Returns:
        True if the manifest was saved successfully, False otherwise
    """
    try:
        # Validate manifest structure
        if not validate_manifest_structure(manifest_data):
            logger.error("❌ Invalid manifest structure, not saving")
            return False
        
        # Update last_updated timestamp
        if "manifest_meta" in manifest_data:
            manifest_data["manifest_meta"]["last_updated"] = datetime.datetime.utcnow().isoformat()
        
        # Save manifest to disk
        with open(MANIFEST_PATH, "w") as f:
            json.dump(manifest_data, f, indent=2)
            
        logger.info(f"✅ Successfully saved manifest to {MANIFEST_PATH}")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving manifest: {str(e)}")
        return False

def update_manifest(section: str, key: str, data: Any) -> bool:
    """
    Update a specific section of the manifest.
    
    Args:
        section: The section to update (e.g., "agents", "schemas")
        key: The key within the section to update
        data: The data to update
        
    Returns:
        True if the manifest was updated successfully, False otherwise
    """
    try:
        # Load current manifest
        manifest_data = load_manifest()
        
        # Ensure section exists
        if section not in manifest_data:
            manifest_data[section] = {}
        
        # Update section
        manifest_data[section][key] = data
        
        # Save updated manifest
        return save_manifest(manifest_data)
    except Exception as e:
        logger.error(f"❌ Error updating manifest: {str(e)}")
        return False

def get_manifest_section(section: str) -> Dict[str, Any]:
    """
    Retrieve a specific section of the manifest.
    
    Args:
        section: The section to retrieve (e.g., "agents", "schemas")
        
    Returns:
        The requested section as a dictionary
    """
    try:
        # Load manifest
        manifest_data = load_manifest()
        
        # Return section if it exists
        if section in manifest_data:
            return manifest_data[section]
        
        # Return empty dict if section doesn't exist
        logger.warning(f"⚠️ Section '{section}' not found in manifest")
        return {}
    except Exception as e:
        logger.error(f"❌ Error getting manifest section: {str(e)}")
        return {}

def validate_manifest_structure(manifest_data: Dict[str, Any]) -> bool:
    """
    Validate the structure of the manifest.
    
    Args:
        manifest_data: The manifest data to validate
        
    Returns:
        True if the manifest structure is valid, False otherwise
    """
    try:
        # Check required sections
        required_sections = ["agents", "schemas", "routes", "modules", "memory", "hardening_layers"]
        for section in required_sections:
            if section not in manifest_data:
                logger.error(f"❌ Missing required section: {section}")
                return False
        
        # Check manifest_meta section
        if "manifest_meta" not in manifest_data:
            logger.warning("⚠️ Missing manifest_meta section, will be added")
            manifest_data["manifest_meta"] = {
                "version": MANIFEST_VERSION,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "last_updated": datetime.datetime.utcnow().isoformat()
            }
        
        logger.info("✅ Manifest structure validated successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error validating manifest structure: {str(e)}")
        return False

def create_default_manifest() -> Dict[str, Any]:
    """
    Create a default manifest with basic structure.
    
    Returns:
        The default manifest as a dictionary
    """
    current_time = datetime.datetime.utcnow().isoformat()
    
    default_manifest = {
        "agents": {
            "hal": {
                "tools": ["openai_generate_code", "memory_read", "memory_write"],
                "schema_wrapped": True,
                "fallbacks": ["openai_fallback", "schema_fallback"],
                "checksum": "initial"
            },
            "orchestrator": {
                "tools": ["memory_read", "memory_write", "plan_next_agent"],
                "schema_wrapped": True,
                "fallbacks": ["schema_fallback"],
                "checksum": "initial"
            }
        },
        "schemas": {
            "LoopResponseRequest": {
                "file": "app/schemas/loop_schema.py",
                "bound_to_routes": ["/loop/respond"],
                "version": "v1.0.0",
                "checksum": "initial"
            },
            "LoopResponseResult": {
                "file": "app/schemas/loop_schema.py",
                "bound_to_routes": ["/loop/respond"],
                "version": "v1.0.0",
                "checksum": "initial"
            }
        },
        "routes": {
            "/loop/respond": {
                "method": "POST",
                "schema": "LoopResponseRequest",
                "status": "registered",
                "errors": []
            }
        },
        "modules": {
            "hal_openai": {
                "file": "app/modules/hal_openai.py",
                "wrapped_with_schema": True,
                "last_updated": current_time
            }
        },
        "memory": {
            "schema_hashes": {},
            "fallback_logging_enabled": True
        },
        "hardening_layers": {
            "schema_checksum_tracking": True,
            "schema_discovery_fallback": True,
            "test_route_integrity": False
        },
        "manifest_meta": {
            "version": MANIFEST_VERSION,
            "created_at": current_time,
            "last_updated": current_time
        }
    }
    
    # Save default manifest
    with open(MANIFEST_PATH, "w") as f:
        json.dump(default_manifest, f, indent=2)
    
    logger.info(f"✅ Created default manifest at {MANIFEST_PATH}")
    return default_manifest

def register_schema(schema_name: str, file_path: str, routes: List[str], version: str = "v1.0.0", checksum: Optional[str] = None) -> bool:
    """
    Register a schema in the manifest.
    
    Args:
        schema_name: The name of the schema class
        file_path: The file path where the schema is defined
        routes: List of routes that use this schema
        version: The schema version
        checksum: Optional checksum of the schema
        
    Returns:
        True if the schema was registered successfully, False otherwise
    """
    try:
        # If checksum is not provided, use "initial"
        if not checksum:
            checksum = "initial"
        
        # Create schema data
        schema_data = {
            "file": file_path,
            "bound_to_routes": routes,
            "version": version,
            "checksum": checksum
        }
        
        # Update manifest
        return update_manifest("schemas", schema_name, schema_data)
    except Exception as e:
        logger.error(f"❌ Error registering schema: {str(e)}")
        return False

def register_route(route_path: str, method: str, schema_name: str, status: str = "registered") -> bool:
    """
    Register a route in the manifest.
    
    Args:
        route_path: The path of the route (e.g., "/loop/respond")
        method: The HTTP method (e.g., "POST", "GET")
        schema_name: The name of the schema used by the route
        status: The status of the route (e.g., "registered", "tested")
        
    Returns:
        True if the route was registered successfully, False otherwise
    """
    try:
        # Create route data
        route_data = {
            "method": method,
            "schema": schema_name,
            "status": status,
            "errors": []
        }
        
        # Update manifest
        return update_manifest("routes", route_path, route_data)
    except Exception as e:
        logger.error(f"❌ Error registering route: {str(e)}")
        return False

def register_agent(agent_name: str, tools: List[str], schema_wrapped: bool = True, fallbacks: List[str] = None) -> bool:
    """
    Register an agent in the manifest.
    
    Args:
        agent_name: The name of the agent
        tools: List of tools used by the agent
        schema_wrapped: Whether the agent is wrapped with schemas
        fallbacks: List of fallbacks used by the agent
        
    Returns:
        True if the agent was registered successfully, False otherwise
    """
    try:
        # If fallbacks is not provided, use empty list
        if fallbacks is None:
            fallbacks = []
        
        # Create agent data
        agent_data = {
            "tools": tools,
            "schema_wrapped": schema_wrapped,
            "fallbacks": fallbacks,
            "checksum": "initial"
        }
        
        # Update manifest
        return update_manifest("agents", agent_name, agent_data)
    except Exception as e:
        logger.error(f"❌ Error registering agent: {str(e)}")
        return False

def register_module(module_name: str, file_path: str, wrapped_with_schema: bool = True) -> bool:
    """
    Register a module in the manifest.
    
    Args:
        module_name: The name of the module
        file_path: The file path where the module is defined
        wrapped_with_schema: Whether the module is wrapped with schemas
        
    Returns:
        True if the module was registered successfully, False otherwise
    """
    try:
        # Create module data
        module_data = {
            "file": file_path,
            "wrapped_with_schema": wrapped_with_schema,
            "last_updated": datetime.datetime.utcnow().isoformat()
        }
        
        # Update manifest
        return update_manifest("modules", module_name, module_data)
    except Exception as e:
        logger.error(f"❌ Error registering module: {str(e)}")
        return False

def update_schema_checksum(schema_name: str, checksum: str) -> bool:
    """
    Update the checksum of a schema in the manifest.
    
    Args:
        schema_name: The name of the schema class
        checksum: The new checksum
        
    Returns:
        True if the checksum was updated successfully, False otherwise
    """
    try:
        # Load current manifest
        manifest_data = load_manifest()
        
        # Ensure schemas section exists
        if "schemas" not in manifest_data:
            manifest_data["schemas"] = {}
        
        # Ensure schema exists
        if schema_name not in manifest_data["schemas"]:
            logger.warning(f"⚠️ Schema '{schema_name}' not found in manifest, creating new entry")
            manifest_data["schemas"][schema_name] = {
                "file": "unknown",
                "bound_to_routes": [],
                "version": "v1.0.0",
                "checksum": checksum
            }
        else:
            # Update checksum
            manifest_data["schemas"][schema_name]["checksum"] = checksum
        
        # Update memory section
        if "memory" not in manifest_data:
            manifest_data["memory"] = {"schema_hashes": {}}
        if "schema_hashes" not in manifest_data["memory"]:
            manifest_data["memory"]["schema_hashes"] = {}
        
        manifest_data["memory"]["schema_hashes"][schema_name] = checksum
        
        # Save updated manifest
        return save_manifest(manifest_data)
    except Exception as e:
        logger.error(f"❌ Error updating schema checksum: {str(e)}")
        return False

def log_route_error(route_path: str, error_message: str) -> bool:
    """
    Log an error for a route in the manifest.
    
    Args:
        route_path: The path of the route (e.g., "/loop/respond")
        error_message: The error message
        
    Returns:
        True if the error was logged successfully, False otherwise
    """
    try:
        # Load current manifest
        manifest_data = load_manifest()
        
        # Ensure routes section exists
        if "routes" not in manifest_data:
            manifest_data["routes"] = {}
        
        # Ensure route exists
        if route_path not in manifest_data["routes"]:
            logger.warning(f"⚠️ Route '{route_path}' not found in manifest, creating new entry")
            manifest_data["routes"][route_path] = {
                "method": "UNKNOWN",
                "schema": "unknown",
                "status": "error",
                "errors": []
            }
        
        # Add error to route
        error_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "message": error_message
        }
        
        manifest_data["routes"][route_path]["errors"].append(error_entry)
        
        # Update route status
        manifest_data["routes"][route_path]["status"] = "error"
        
        # Save updated manifest
        return save_manifest(manifest_data)
    except Exception as e:
        logger.error(f"❌ Error logging route error: {str(e)}")
        return False

def update_hardening_layer(layer_name: str, enabled: bool) -> bool:
    """
    Update the status of a hardening layer in the manifest.
    
    Args:
        layer_name: The name of the hardening layer
        enabled: Whether the layer is enabled
        
    Returns:
        True if the layer was updated successfully, False otherwise
    """
    try:
        # Load current manifest
        manifest_data = load_manifest()
        
        # Ensure hardening_layers section exists
        if "hardening_layers" not in manifest_data:
            manifest_data["hardening_layers"] = {}
        
        # Update hardening layer
        manifest_data["hardening_layers"][layer_name] = enabled
        
        # Save updated manifest
        return save_manifest(manifest_data)
    except Exception as e:
        logger.error(f"❌ Error updating hardening layer: {str(e)}")
        return False

def get_manifest_checksum() -> str:
    """
    Generate a checksum for the entire manifest.
    
    Returns:
        A hexadecimal string representing the SHA-256 hash of the manifest
    """
    try:
        # Load manifest
        manifest_data = load_manifest()
        
        # Convert to JSON string
        manifest_json = json.dumps(manifest_data, sort_keys=True)
        
        # Generate SHA-256 hash
        checksum = hashlib.sha256(manifest_json.encode()).hexdigest()
        
        logger.info(f"✅ Generated manifest checksum: {checksum[:8]}...")
        return checksum
    except Exception as e:
        logger.error(f"❌ Error generating manifest checksum: {str(e)}")
        return f"error-{hashlib.sha256(str(e).encode()).hexdigest()[:16]}"
