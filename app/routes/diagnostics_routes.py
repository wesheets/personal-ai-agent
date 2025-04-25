"""
Diagnostics Routes Module

This module provides API routes for system diagnostics.
"""
from fastapi import APIRouter
import datetime
import logging
import os
import json
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger("app.routes.diagnostics_routes")

# Ensure logs directory exists
os.makedirs("/home/ubuntu/personal-ai-agent/logs", exist_ok=True)

# Create router
router = APIRouter(tags=["diagnostics"])

@router.get("/diagnostics/routes")
async def get_routes_diagnostics():
    """
    Get diagnostics information about loaded and failed routes.
    
    Returns:
        Dict containing information about loaded routes, failed routes,
        and fallbacks that were triggered.
    """
    logger.info("🔍 DEBUG: diagnostics/routes endpoint called")
    
    # Initialize response with default values
    response = {
        "loaded_routes": [],
        "failed_routes": [],
        "fallbacks_triggered": {
            "memory": False,
            "hal": False
        },
        "timestamp": str(datetime.datetime.now())
    }
    
    # Check for HAL route failures
    hal_fallback_triggered = False
    if os.path.exists("/home/ubuntu/personal-ai-agent/logs/hal_route_failures.json"):
        try:
            with open("/home/ubuntu/personal-ai-agent/logs/hal_route_failures.json", "r") as f:
                hal_logs = json.load(f)
                if isinstance(hal_logs, list) and len(hal_logs) > 0:
                    hal_fallback_triggered = any(log.get("event") == "fallback_activated" for log in hal_logs)
        except Exception as e:
            logger.error(f"Error reading HAL route failures log: {str(e)}")
    
    # Check for memory fallbacks
    memory_fallback_triggered = False
    if os.path.exists("/home/ubuntu/personal-ai-agent/logs/memory_fallback.json"):
        try:
            with open("/home/ubuntu/personal-ai-agent/logs/memory_fallback.json", "r") as f:
                memory_logs = json.load(f)
                if isinstance(memory_logs, list) and len(memory_logs) > 0:
                    memory_fallback_triggered = any(log.get("event") == "fallback_activated" for log in memory_logs)
        except Exception as e:
            logger.error(f"Error reading memory fallback log: {str(e)}")
    
    # Check for final route status
    if os.path.exists("/home/ubuntu/personal-ai-agent/logs/final_route_status.json"):
        try:
            with open("/home/ubuntu/personal-ai-agent/logs/final_route_status.json", "r") as f:
                route_status = json.load(f)
                response["loaded_routes"] = route_status.get("loaded_routes", [])
                response["failed_routes"] = route_status.get("failed_routes", [])
                
                # Use the fallbacks_triggered from the file, but override with our findings if needed
                fallbacks = route_status.get("fallbacks_triggered", {"memory": False, "hal": False})
                fallbacks["memory"] = fallbacks.get("memory", False) or memory_fallback_triggered
                fallbacks["hal"] = fallbacks.get("hal", False) or hal_fallback_triggered
                response["fallbacks_triggered"] = fallbacks
        except Exception as e:
            logger.error(f"Error reading final route status log: {str(e)}")
    else:
        # If final_route_status.json doesn't exist, use our findings
        response["fallbacks_triggered"]["memory"] = memory_fallback_triggered
        response["fallbacks_triggered"]["hal"] = hal_fallback_triggered
    
    # Save diagnostics to log file
    try:
        with open("/home/ubuntu/personal-ai-agent/logs/final_route_status.json", "w") as f:
            json.dump(response, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save route diagnostics: {str(e)}")
    
    return response
