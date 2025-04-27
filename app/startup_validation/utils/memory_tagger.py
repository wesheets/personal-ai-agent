"""
Memory Tagger Module

This module handles the creation and management of memory tags for the validation system.
It updates the system status file with appropriate memory tags based on validation results.
"""

import os
import json
import datetime
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger('startup_validation.memory_tagger')

# Define memory tag templates
MEMORY_TAG_VALIDATED = "startup_surface_validated_{date}"
MEMORY_TAG_DRIFT_DETECTED = "startup_surface_drift_detected_{date}"

def create_memory_tag(drift_detected: bool) -> str:
    """
    Create a memory tag based on validation results.
    
    Args:
        drift_detected: Whether drift was detected during validation
        
    Returns:
        The created memory tag
    """
    logger.info("Creating memory tag")
    
    # Get current date in YYYYMMDD format
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    # Create memory tag based on validation result
    if drift_detected:
        memory_tag = MEMORY_TAG_DRIFT_DETECTED.format(date=today)
        logger.info(f"Created drift detected memory tag: {memory_tag}")
    else:
        memory_tag = MEMORY_TAG_VALIDATED.format(date=today)
        logger.info(f"Created validation success memory tag: {memory_tag}")
    
    return memory_tag

def update_system_status(memory_tag: str, health_data: Dict[str, Any]) -> bool:
    """
    Update the system status file with the memory tag and health data.
    
    Args:
        memory_tag: The memory tag to add to the status file
        health_data: Health data to include in the status file
        
    Returns:
        True if the update was successful, False otherwise
    """
    logger.info(f"Updating system status with memory tag: {memory_tag}")
    
    try:
        # Load current system status
        status_data = load_system_status()
        
        # If status file doesn't exist or couldn't be loaded, create a new one
        if not status_data:
            status_data = {
                "system_health": {
                    "status": "healthy" if health_data["surface_health_score"] >= 95 else "degraded",
                    "last_checked": datetime.datetime.now().isoformat(),
                    "memory_surface": {},
                    "memory_tags": {}
                }
            }
        
        # Update memory surface health data
        status_data["system_health"]["memory_surface"] = {
            "total_agents": health_data.get("agents_count", 0),
            "total_modules": health_data.get("modules_count", 0),
            "total_schemas": health_data.get("schemas_count", 0),
            "total_endpoints": health_data.get("endpoints_count", 0),
            "total_components": health_data.get("components_count", 0),
            "health_score": health_data["surface_health_score"]
        }
        
        # Update memory tags
        if "memory_tags" not in status_data["system_health"]:
            status_data["system_health"]["memory_tags"] = {}
        
        status_data["system_health"]["memory_tags"]["startup_validation"] = memory_tag
        status_data["system_health"]["last_checked"] = datetime.datetime.now().isoformat()
        
        # Update system status based on health score
        if health_data["surface_health_score"] < 80:
            status_data["system_health"]["status"] = "critical"
        elif health_data["surface_health_score"] < 95:
            status_data["system_health"]["status"] = "degraded"
        else:
            status_data["system_health"]["status"] = "healthy"
        
        # Save updated status
        base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
        system_dir = os.path.join(base_path, "system")
        os.makedirs(system_dir, exist_ok=True)
        
        status_path = os.path.join(system_dir, "status.json")
        with open(status_path, 'w') as f:
            json.dump(status_data, f, indent=2)
        
        logger.info(f"System status updated successfully at {status_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating system status: {str(e)}")
        return False

def load_system_status() -> Dict[str, Any]:
    """
    Load the current system status file.
    
    Returns:
        Dictionary containing the system status data
    """
    logger.info("Loading system status")
    
    try:
        base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
        status_path = os.path.join(base_path, "system", "status.json")
        
        if not os.path.isfile(status_path):
            logger.warning(f"System status file not found at {status_path}")
            return {}
        
        with open(status_path, 'r') as f:
            status_data = json.load(f)
        
        logger.info("System status loaded successfully")
        return status_data
    
    except json.JSONDecodeError:
        logger.error("System status file contains invalid JSON")
        return {}
    
    except Exception as e:
        logger.error(f"Error loading system status: {str(e)}")
        return {}

def save_memory_tag_file(memory_tag: str, report_data: Dict[str, Any]) -> str:
    """
    Save a memory tag file with the report data.
    
    Args:
        memory_tag: The memory tag to use for the filename
        report_data: Report data to include in the file
        
    Returns:
        Path to the saved memory tag file
    """
    logger.info(f"Saving memory tag file for {memory_tag}")
    
    try:
        # Ensure logs directory exists
        base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
        logs_dir = os.path.join(base_path, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Save memory tag file
        tag_file_path = os.path.join(logs_dir, f"{memory_tag}.txt")
        
        with open(tag_file_path, 'w') as f:
            f.write(f"Memory Tag: {memory_tag}\n")
            f.write(f"Created: {datetime.datetime.now().isoformat()}\n")
            f.write(f"Surface Health Score: {report_data['surface_health_score']}%\n")
            f.write(f"Agents Health: {report_data['agents_health']}\n")
            f.write(f"Modules Health: {report_data['modules_health']}\n")
            f.write(f"Schemas Health: {report_data['schemas_health']}\n")
            f.write(f"Endpoints Health: {report_data['endpoints_health']}\n")
            f.write(f"Components Health: {report_data['components_health']}\n")
            
            if report_data['surface_drift']:
                f.write(f"\nDrift Issues ({len(report_data['surface_drift'])}):\n")
                for issue in report_data['surface_drift']:
                    f.write(f"- {issue['type'].upper()}: {issue['path']} - {issue['issue']}\n")
            else:
                f.write("\nNo drift issues detected.\n")
        
        logger.info(f"Memory tag file saved to {tag_file_path}")
        return tag_file_path
    
    except Exception as e:
        logger.error(f"Error saving memory tag file: {str(e)}")
        return ""
