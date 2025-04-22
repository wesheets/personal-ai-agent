"""
Project Manifest System Module

This module implements the Project Manifest System for Promethios, which tracks
and versions all project modules over time. It provides a central repository
of information about the state of the system, which can be used by the Rebuilder
Agent to detect drift and degradation.

The Project Manifest System is responsible for:
1. Tracking module metadata (creation, updates, versions)
2. Recording CI test results
3. Tracking belief versions
4. Flagging modules that need rebuilding
5. Providing an API for accessing and updating manifest data
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PROJECT_MANIFEST_DIR = "/home/ubuntu/repo/personal-ai-agent/data/project_manifest"

def ensure_manifest_dir():
    """Ensure the project manifest directory exists."""
    os.makedirs(PROJECT_MANIFEST_DIR, exist_ok=True)
    logger.info(f"Ensured project manifest directory exists: {PROJECT_MANIFEST_DIR}")

def get_manifest_path(project_id: str) -> str:
    """
    Get the path to a project manifest file.
    
    Args:
        project_id: ID of the project
        
    Returns:
        Path to the project manifest file
    """
    ensure_manifest_dir()
    return os.path.join(PROJECT_MANIFEST_DIR, f"{project_id}.json")

def load_manifest(project_id: str) -> Dict[str, Any]:
    """
    Load a project manifest.
    
    Args:
        project_id: ID of the project
        
    Returns:
        Project manifest data
    """
    manifest_path = get_manifest_path(project_id)
    
    if not os.path.exists(manifest_path):
        logger.warning(f"Project manifest not found for project: {project_id}")
        return create_manifest(project_id)
    
    try:
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
        
        logger.info(f"Loaded project manifest for project: {project_id}")
        return manifest_data
    
    except Exception as e:
        logger.error(f"Error loading project manifest: {e}")
        return create_manifest(project_id)

def save_manifest(project_id: str, manifest_data: Dict[str, Any]) -> bool:
    """
    Save a project manifest.
    
    Args:
        project_id: ID of the project
        manifest_data: Project manifest data
        
    Returns:
        Boolean indicating success
    """
    manifest_path = get_manifest_path(project_id)
    
    try:
        # Update timestamp
        manifest_data["updated_at"] = datetime.datetime.utcnow().isoformat()
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        logger.info(f"Saved project manifest for project: {project_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving project manifest: {e}")
        return False

def create_manifest(project_id: str) -> Dict[str, Any]:
    """
    Create a new project manifest.
    
    Args:
        project_id: ID of the project
        
    Returns:
        New project manifest data
    """
    manifest_data = {
        "project_id": project_id,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "modules": {},
        "last_stability_score": 1.0,
        "last_rebuild_check": {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "needs_rebuild": False,
            "rebuild_events": [],
            "recommendations": []
        }
    }
    
    manifest_path = get_manifest_path(project_id)
    
    try:
        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        logger.info(f"Created new project manifest for project: {project_id}")
        return manifest_data
    
    except Exception as e:
        logger.error(f"Error creating project manifest: {e}")
        return manifest_data

def get_module(project_id: str, module_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a module from a project manifest.
    
    Args:
        project_id: ID of the project
        module_name: Name of the module
        
    Returns:
        Module data, or None if not found
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return None
    
    if module_name not in manifest_data["modules"]:
        logger.warning(f"Module not found in project manifest: {module_name}")
        return None
    
    return manifest_data["modules"][module_name]

def add_module(
    project_id: str,
    module_name: str,
    loop_id: str,
    agent_id: str,
    belief_version: str,
    module_type: str = "standard",
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Add a new module to a project manifest.
    
    Args:
        project_id: ID of the project
        module_name: Name of the module
        loop_id: ID of the loop that created the module
        agent_id: ID of the agent that created the module
        belief_version: Version of the belief system used by the module
        module_type: Type of the module (standard, plugin, core, etc.)
        metadata: Additional metadata for the module
        
    Returns:
        Boolean indicating success
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        manifest_data["modules"] = {}
    
    # Check if module already exists
    if module_name in manifest_data["modules"]:
        logger.warning(f"Module already exists in project manifest: {module_name}")
        return False
    
    # Create module data
    module_data = {
        "module_name": module_name,
        "module_type": module_type,
        "loop_id_created": loop_id,
        "agent_created_by": agent_id,
        "belief_version": belief_version,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat(),
        "last_audited_loop_id": None,
        "last_ci_result": None,
        "needs_rebuild": False
    }
    
    # Add metadata if provided
    if metadata:
        module_data["metadata"] = metadata
    
    # Add module to manifest
    manifest_data["modules"][module_name] = module_data
    
    # Save manifest
    success = save_manifest(project_id, manifest_data)
    
    if success:
        logger.info(f"Added module to project manifest: {module_name}")
    
    return success

def update_module(
    project_id: str,
    module_name: str,
    updates: Dict[str, Any]
) -> bool:
    """
    Update a module in a project manifest.
    
    Args:
        project_id: ID of the project
        module_name: Name of the module
        updates: Dictionary of updates to apply to the module
        
    Returns:
        Boolean indicating success
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return False
    
    if module_name not in manifest_data["modules"]:
        logger.warning(f"Module not found in project manifest: {module_name}")
        return False
    
    # Update module data
    module_data = manifest_data["modules"][module_name]
    
    for key, value in updates.items():
        if key not in ["module_name", "created_at", "loop_id_created", "agent_created_by"]:
            module_data[key] = value
    
    # Update timestamp
    module_data["updated_at"] = datetime.datetime.utcnow().isoformat()
    
    # Save manifest
    success = save_manifest(project_id, manifest_data)
    
    if success:
        logger.info(f"Updated module in project manifest: {module_name}")
    
    return success

def delete_module(project_id: str, module_name: str) -> bool:
    """
    Delete a module from a project manifest.
    
    Args:
        project_id: ID of the project
        module_name: Name of the module
        
    Returns:
        Boolean indicating success
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return False
    
    if module_name not in manifest_data["modules"]:
        logger.warning(f"Module not found in project manifest: {module_name}")
        return False
    
    # Delete module
    del manifest_data["modules"][module_name]
    
    # Save manifest
    success = save_manifest(project_id, manifest_data)
    
    if success:
        logger.info(f"Deleted module from project manifest: {module_name}")
    
    return success

def update_ci_result(
    project_id: str,
    module_name: str,
    ci_result: Dict[str, Any]
) -> bool:
    """
    Update CI result for a module.
    
    Args:
        project_id: ID of the project
        module_name: Name of the module
        ci_result: CI result data
        
    Returns:
        Boolean indicating success
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return False
    
    if module_name not in manifest_data["modules"]:
        logger.warning(f"Module not found in project manifest: {module_name}")
        return False
    
    # Update CI result
    manifest_data["modules"][module_name]["last_ci_result"] = ci_result
    
    # Update timestamp
    manifest_data["modules"][module_name]["updated_at"] = datetime.datetime.utcnow().isoformat()
    
    # Set needs_rebuild flag if CI failed
    if ci_result.get("status") == "failed":
        manifest_data["modules"][module_name]["needs_rebuild"] = True
    
    # Save manifest
    success = save_manifest(project_id, manifest_data)
    
    if success:
        logger.info(f"Updated CI result for module: {module_name}")
    
    return success

def update_belief_version(
    project_id: str,
    module_name: str,
    belief_version: str
) -> bool:
    """
    Update belief version for a module.
    
    Args:
        project_id: ID of the project
        module_name: Name of the module
        belief_version: New belief version
        
    Returns:
        Boolean indicating success
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return False
    
    if module_name not in manifest_data["modules"]:
        logger.warning(f"Module not found in project manifest: {module_name}")
        return False
    
    # Update belief version
    manifest_data["modules"][module_name]["belief_version"] = belief_version
    
    # Update timestamp
    manifest_data["modules"][module_name]["updated_at"] = datetime.datetime.utcnow().isoformat()
    
    # Save manifest
    success = save_manifest(project_id, manifest_data)
    
    if success:
        logger.info(f"Updated belief version for module: {module_name}")
    
    return success

def mark_for_rebuild(
    project_id: str,
    module_name: str,
    needs_rebuild: bool = True,
    reason: Optional[str] = None
) -> bool:
    """
    Mark a module for rebuild.
    
    Args:
        project_id: ID of the project
        module_name: Name of the module
        needs_rebuild: Whether the module needs rebuilding
        reason: Reason for marking the module for rebuild
        
    Returns:
        Boolean indicating success
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return False
    
    if module_name not in manifest_data["modules"]:
        logger.warning(f"Module not found in project manifest: {module_name}")
        return False
    
    # Update needs_rebuild flag
    manifest_data["modules"][module_name]["needs_rebuild"] = needs_rebuild
    
    # Add reason if provided
    if reason:
        manifest_data["modules"][module_name]["rebuild_reason"] = reason
    
    # Update timestamp
    manifest_data["modules"][module_name]["updated_at"] = datetime.datetime.utcnow().isoformat()
    
    # Save manifest
    success = save_manifest(project_id, manifest_data)
    
    if success:
        if needs_rebuild:
            logger.info(f"Marked module for rebuild: {module_name}")
        else:
            logger.info(f"Cleared rebuild flag for module: {module_name}")
    
    return success

def update_audit_info(
    project_id: str,
    module_name: str,
    loop_id: str,
    audit_info: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Update audit information for a module.
    
    Args:
        project_id: ID of the project
        module_name: Name of the module
        loop_id: ID of the loop that performed the audit
        audit_info: Audit information
        
    Returns:
        Boolean indicating success
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return False
    
    if module_name not in manifest_data["modules"]:
        logger.warning(f"Module not found in project manifest: {module_name}")
        return False
    
    # Update audit information
    manifest_data["modules"][module_name]["last_audited_loop_id"] = loop_id
    
    if audit_info:
        manifest_data["modules"][module_name]["last_audit_info"] = audit_info
    
    # Update timestamp
    manifest_data["modules"][module_name]["updated_at"] = datetime.datetime.utcnow().isoformat()
    
    # Save manifest
    success = save_manifest(project_id, manifest_data)
    
    if success:
        logger.info(f"Updated audit information for module: {module_name}")
    
    return success

def get_modules_needing_rebuild(project_id: str) -> List[str]:
    """
    Get a list of modules that need rebuilding.
    
    Args:
        project_id: ID of the project
        
    Returns:
        List of module names that need rebuilding
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return []
    
    # Find modules that need rebuilding
    modules_needing_rebuild = []
    
    for module_name, module_data in manifest_data["modules"].items():
        if module_data.get("needs_rebuild", False):
            modules_needing_rebuild.append(module_name)
    
    logger.info(f"Found {len(modules_needing_rebuild)} modules needing rebuild for project: {project_id}")
    return modules_needing_rebuild

def get_modules_by_belief_version(project_id: str, belief_version: str) -> List[str]:
    """
    Get a list of modules with a specific belief version.
    
    Args:
        project_id: ID of the project
        belief_version: Belief version to filter by
        
    Returns:
        List of module names with the specified belief version
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return []
    
    # Find modules with the specified belief version
    modules = []
    
    for module_name, module_data in manifest_data["modules"].items():
        if module_data.get("belief_version") == belief_version:
            modules.append(module_name)
    
    logger.info(f"Found {len(modules)} modules with belief version {belief_version} for project: {project_id}")
    return modules

def get_modules_by_ci_status(project_id: str, status: str) -> List[str]:
    """
    Get a list of modules with a specific CI status.
    
    Args:
        project_id: ID of the project
        status: CI status to filter by (passed, failed, etc.)
        
    Returns:
        List of module names with the specified CI status
    """
    manifest_data = load_manifest(project_id)
    
    if "modules" not in manifest_data:
        logger.warning(f"No modules found in project manifest: {project_id}")
        return []
    
    # Find modules with the specified CI status
    modules = []
    
    for module_name, module_data in manifest_data["modules"].items():
        if "last_ci_result" in module_data and module_data["last_ci_result"].get("status") == status:
            modules.append(module_name)
    
    logger.info(f"Found {len(modules)} modules with CI status {status} for project: {project_id}")
    return modules

def get_manifest_summary(project_id: str) -> Dict[str, Any]:
    """
    Get a summary of a project manifest.
    
    Args:
        project_id: ID of the project
        
    Returns:
        Summary of the project manifest
    """
    manifest_data = load_manifest(project_id)
    
    # Count modules by type
    module_counts = {}
    belief_versions = set()
    modules_needing_rebuild = []
    modules_with_failed_ci = []
    
    if "modules" in manifest_data:
        for module_name, module_data in manifest_data["modules"].items():
            # Count by type
            module_type = module_data.get("module_type", "standard")
            if module_type not in module_counts:
                module_counts[module_type] = 0
            module_counts[module_type] += 1
            
            # Collect belief versions
            if "belief_version" in module_data:
                belief_versions.add(module_data["belief_version"])
            
            # Check for modules needing rebuild
            if module_data.get("needs_rebuild", False):
                modules_needing_rebuild.append(module_name)
            
            # Check for modules with failed CI
            if "last_ci_result" in module_data and module_data["last_ci_result"].get("status") == "failed":
                modules_with_failed_ci.append(module_name)
    
    # Create summary
    summary = {
        "project_id": project_id,
        "total_modules": len(manifest_data.get("modules", {})),
        "module_counts": module_counts,
        "belief_versions": list(belief_versions),
        "modules_needing_rebuild": modules_needing_rebuild,
        "modules_with_failed_ci": modules_with_failed_ci,
        "last_stability_score": manifest_data.get("last_stability_score", 1.0),
        "last_updated": manifest_data.get("updated_at")
    }
    
    logger.info(f"Generated manifest summary for project: {project_id}")
    return summary

def list_projects() -> List[str]:
    """
    List all projects with manifests.
    
    Returns:
        List of project IDs
    """
    ensure_manifest_dir()
    
    try:
        # List all JSON files in the manifest directory
        project_ids = []
        
        for filename in os.listdir(PROJECT_MANIFEST_DIR):
            if filename.endswith(".json"):
                project_id = filename[:-5]  # Remove .json extension
                project_ids.append(project_id)
        
        logger.info(f"Found {len(project_ids)} projects with manifests")
        return project_ids
    
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return []

def update_stability_score(project_id: str, stability_score: float) -> bool:
    """
    Update the stability score for a project.
    
    Args:
        project_id: ID of the project
        stability_score: New stability score
        
    Returns:
        Boolean indicating success
    """
    manifest_data = load_manifest(project_id)
    
    # Update stability score
    manifest_data["last_stability_score"] = stability_score
    
    # Save manifest
    success = save_manifest(project_id, manifest_data)
    
    if success:
        logger.info(f"Updated stability score for project: {project_id}")
    
    return success

def update_rebuild_check(
    project_id: str,
    needs_rebuild: bool,
    rebuild_events: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]]
) -> bool:
    """
    Update the rebuild check information for a project.
    
    Args:
        project_id: ID of the project
        needs_rebuild: Whether the project needs rebuilding
        rebuild_events: List of rebuild events
        recommendations: List of recommendations
        
    Returns:
        Boolean indicating success
    """
    manifest_data = load_manifest(project_id)
    
    # Update rebuild check information
    manifest_data["last_rebuild_check"] = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "needs_rebuild": needs_rebuild,
        "rebuild_events": rebuild_events,
        "recommendations": recommendations
    }
    
    # Save manifest
    success = save_manifest(project_id, manifest_data)
    
    if success:
        logger.info(f"Updated rebuild check information for project: {project_id}")
    
    return success
