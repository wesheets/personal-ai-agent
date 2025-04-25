"""
Debug Status Endpoint

This module provides a comprehensive status endpoint that checks all critical components
of the application and returns detailed diagnostics about their status.
"""

import logging
import os
import sys
import importlib.util
import datetime
import json
import requests
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger("app.routes.debug_status")

# Create router
router = APIRouter(
    tags=["debug"],
    responses={404: {"description": "Not found"}},
)

@router.get("/trap")
async def manual_debug_trap():
    """
    Failsafe endpoint for direct access to confirm router registration.
    
    This endpoint provides a non-conditional route to confirm router registration.
    
    Returns:
        Dict containing trap status
    """
    # Failsafe endpoint trap
    print("🧠 /debug/trap route is triggered.")
    logger.info("🧠 /debug/trap route is triggered.")
    return {"trap": "triggered"}

@router.get("/status")
async def get_deployment_status(request: Request):
    """
    Get comprehensive status of all critical components.
    
    This endpoint checks:
    - HAL schema file existence and path resolution
    - HAL agent registration status
    - Memory module availability
    - Orchestrator router status
    - Import paths for all critical modules
    - All core system endpoints accessibility
    
    Returns:
        Dict containing detailed status information
    """
    # Route registration confirmation trap
    print("🧠 /debug/status route is registered.")
    logger.info("🧠 /debug/status route is registered.")
    
    status_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": get_environment_info(),
        "components": {
            "hal": check_hal_status(),
            "memory": check_memory_status(),
            "orchestrator": check_orchestrator_status(),
            "dashboard": check_dashboard_status()
        },
        "import_paths": check_import_paths(),
        "file_paths": check_file_paths(),
        "endpoints": check_all_endpoints(request),
        "overall_status": "unknown"  # Will be updated based on component statuses
    }
    
    # Determine overall status
    component_statuses = [
        status_report["components"]["hal"]["status"],
        status_report["components"]["memory"]["status"],
        status_report["components"]["orchestrator"]["status"],
        status_report["components"]["dashboard"]["status"]
    ]
    
    # Include endpoint status in overall status determination
    endpoint_statuses = [
        endpoint["status"] for endpoint in status_report["endpoints"].values()
    ]
    all_statuses = component_statuses + endpoint_statuses
    
    if all(status == "operational" for status in component_statuses) and all(status == "accessible" for status in endpoint_statuses):
        status_report["overall_status"] = "operational"
    elif any(status == "failed" for status in component_statuses) or any(status == "inaccessible" for status in endpoint_statuses):
        status_report["overall_status"] = "degraded"
    else:
        status_report["overall_status"] = "partial"
    
    # Log the status report
    log_status_report(status_report)
    
    return status_report
