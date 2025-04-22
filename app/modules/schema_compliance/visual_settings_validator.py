"""
Visual Settings Validator Module

This module provides functions for validating visual settings against the schema.
It ensures that all visual settings conform to the defined schema before use.
"""

import json
import os
import logging
from datetime import datetime
import sys

# Import schema validation module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.schema_validation import validate_schema

# Configure logging
logging.basicConfig(
    filename='/debug/schema_trace.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('visual_settings_validator')

# Default settings for each mode
DEFAULT_SETTINGS = {
    "fast": {
        "detail_level": "minimal",
        "node_types_to_show": [
            "agent", "loop_start", "loop_end", "rerun", "mode_change"
        ],
        "edge_types_to_show": [
            "execution", "rerun", "mode_transition"
        ],
        "include_timestamps": False,
        "include_memory_details": False,
        "include_agent_details": False,
        "include_decision_details": False,
        "update_frequency": "end_only"
    },
    "balanced": {
        "detail_level": "standard",
        "node_types_to_show": [
            "agent", "memory", "decision", "reflection", 
            "loop_start", "loop_end", "rerun", "mode_change", "depth_change"
        ],
        "edge_types_to_show": [
            "execution", "memory_access", "decision", "reflection", 
            "rerun", "mode_transition", "depth_transition"
        ],
        "include_timestamps": True,
        "include_memory_details": True,
        "include_agent_details": True,
        "include_decision_details": True,
        "update_frequency": "agent_completion"
    },
    "thorough": {
        "detail_level": "detailed",
        "node_types_to_show": [
            "agent", "memory", "decision", "reflection", 
            "loop_start", "loop_end", "rerun", "operator",
            "mode_change", "depth_change"
        ],
        "edge_types_to_show": [
            "execution", "memory_access", "decision", "reflection", 
            "rerun", "operator", "mode_transition", "depth_transition"
        ],
        "include_timestamps": True,
        "include_memory_details": True,
        "include_agent_details": True,
        "include_decision_details": True,
        "update_frequency": "real_time"
    },
    "research": {
        "detail_level": "comprehensive",
        "node_types_to_show": [
            "agent", "memory", "decision", "reflection", 
            "loop_start", "loop_end", "rerun", "operator",
            "mode_change", "depth_change"
        ],
        "edge_types_to_show": [
            "execution", "memory_access", "decision", "reflection", 
            "rerun", "operator", "mode_transition", "depth_transition"
        ],
        "include_timestamps": True,
        "include_memory_details": True,
        "include_agent_details": True,
        "include_decision_details": True,
        "include_uncertainty": True,
        "track_alternatives": True,
        "update_frequency": "real_time"
    }
}

def validate_visual_settings(settings, mode=None):
    """
    Validate visual settings against the schema.
    
    Args:
        settings: The visual settings to validate
        mode: The mode these settings are for (for logging purposes)
        
    Returns:
        tuple: (is_valid, validated_settings, error_message)
    """
    # Validate settings against schema
    is_valid, error = validate_schema(settings, 'visual_settings')
    
    if not is_valid:
        mode_str = f" for mode {mode}" if mode else ""
        logger.error(f"Invalid visual settings{mode_str}: {error}")
        
        # If mode is provided, return default settings for that mode
        if mode and mode in DEFAULT_SETTINGS:
            logger.warning(f"Using default visual settings for mode {mode}")
            return False, DEFAULT_SETTINGS[mode], error
        else:
            # Otherwise return default balanced settings
            logger.warning("Using default balanced visual settings")
            return False, DEFAULT_SETTINGS["balanced"], error
    
    logger.info(f"Visual settings validated successfully{' for mode ' + mode if mode else ''}")
    
    # Add validation metadata
    validated_settings = settings.copy()
    validated_settings["schema_validated"] = True
    validated_settings["validation_timestamp"] = datetime.utcnow().isoformat()
    
    return True, validated_settings, None

def get_validated_settings_for_mode(mode):
    """
    Get validated visual settings for a specific mode.
    
    Args:
        mode: The orchestrator mode (fast, balanced, thorough, research)
        
    Returns:
        dict: Validated visual settings for the specified mode
    """
    if mode not in DEFAULT_SETTINGS:
        logger.warning(f"Unknown mode: {mode}, using balanced mode settings")
        mode = "balanced"
    
    settings = DEFAULT_SETTINGS[mode]
    is_valid, validated_settings, error = validate_visual_settings(settings, mode)
    
    return validated_settings

def validate_custom_settings(custom_settings, base_mode="balanced"):
    """
    Validate custom visual settings, falling back to base mode defaults if invalid.
    
    Args:
        custom_settings: Custom visual settings to validate
        base_mode: Base mode to use for defaults if validation fails
        
    Returns:
        dict: Validated visual settings
    """
    is_valid, validated_settings, error = validate_visual_settings(custom_settings)
    
    if not is_valid:
        logger.warning(f"Custom settings validation failed, using {base_mode} mode defaults")
        return get_validated_settings_for_mode(base_mode)
    
    return validated_settings
