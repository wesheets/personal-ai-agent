"""
Surface Loader Module

This module handles loading the cognitive surfaces (ACI and PICE) for validation.
It provides functions to load and parse the JSON files containing the cognitive surface data.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger('startup_validation.surface_loader')

# Define paths to cognitive surface files
ACI_PATH = "/system/agent_cognition_index.json"
PICE_PATH = "/system/system_consciousness_index.json"

def load_aci(base_path: str = "") -> Optional[Dict[str, Any]]:
    """
    Load the Agent Cognition Index (ACI) from the system directory.
    
    Args:
        base_path: Base path to prepend to the ACI path
        
    Returns:
        Dictionary containing the ACI data, or None if loading failed
    """
    full_path = os.path.join(base_path, ACI_PATH.lstrip('/'))
    logger.info(f"Loading ACI from {full_path}")
    
    try:
        with open(full_path, 'r') as f:
            aci_data = json.load(f)
        
        if validate_surface_format(aci_data, "aci"):
            logger.info("ACI loaded successfully")
            return aci_data
        else:
            logger.error("ACI has invalid format")
            return None
    except FileNotFoundError:
        logger.error(f"ACI file not found at {full_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"ACI file contains invalid JSON")
        return None
    except Exception as e:
        logger.error(f"Error loading ACI: {str(e)}")
        return None

def load_pice(base_path: str = "") -> Optional[Dict[str, Any]]:
    """
    Load the Product/Infrastructure Cognition Engine (PICE) from the system directory.
    
    Args:
        base_path: Base path to prepend to the PICE path
        
    Returns:
        Dictionary containing the PICE data, or None if loading failed
    """
    full_path = os.path.join(base_path, PICE_PATH.lstrip('/'))
    logger.info(f"Loading PICE from {full_path}")
    
    try:
        with open(full_path, 'r') as f:
            pice_data = json.load(f)
        
        if validate_surface_format(pice_data, "pice"):
            logger.info("PICE loaded successfully")
            return pice_data
        else:
            logger.error("PICE has invalid format")
            return None
    except FileNotFoundError:
        logger.error(f"PICE file not found at {full_path}")
        return None
    except json.JSONDecodeError:
        logger.error(f"PICE file contains invalid JSON")
        return None
    except Exception as e:
        logger.error(f"Error loading PICE: {str(e)}")
        return None

def load_cognitive_surfaces(base_path: str = "") -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Load both cognitive surfaces (ACI and PICE) from the system directory.
    
    Args:
        base_path: Base path to prepend to the surface paths
        
    Returns:
        Tuple containing the ACI and PICE data, or None for either if loading failed
    """
    logger.info("Loading cognitive surfaces")
    aci_data = load_aci(base_path)
    pice_data = load_pice(base_path)
    return aci_data, pice_data

def validate_surface_format(surface_data: Dict[str, Any], surface_type: str) -> bool:
    """
    Validate that a loaded surface has the expected format.
    
    Args:
        surface_data: The loaded surface data
        surface_type: Type of surface ("aci" or "pice")
        
    Returns:
        True if the surface has the expected format, False otherwise
    """
    if not isinstance(surface_data, dict):
        logger.error(f"{surface_type.upper()} data is not a dictionary")
        return False
    
    if surface_type == "aci":
        # Validate ACI format
        if "agents" not in surface_data:
            logger.error("ACI missing 'agents' key")
            return False
        if not isinstance(surface_data["agents"], list):
            logger.error("ACI 'agents' is not a list")
            return False
        return True
    
    elif surface_type == "pice":
        # Validate PICE format
        required_keys = ["modules", "schemas", "components"]
        for key in required_keys:
            if key not in surface_data:
                logger.error(f"PICE missing '{key}' key")
                return False
            if not isinstance(surface_data[key], list):
                logger.error(f"PICE '{key}' is not a list")
                return False
        return True
    
    else:
        logger.error(f"Unknown surface type: {surface_type}")
        return False
