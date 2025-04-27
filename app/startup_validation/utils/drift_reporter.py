"""
Drift Reporter Module

This module handles the reporting of surface drift detected during validation.
It generates detailed reports and saves them to the appropriate locations.
"""

import os
import json
import datetime
import logging
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger('startup_validation.drift_reporter')

def generate_drift_report(
    surface_health_score: float,
    agents_health: float,
    modules_health: float,
    schemas_health: float,
    endpoints_health: float,
    components_health: float,
    surface_drift: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate a drift report based on validation results.
    
    Args:
        surface_health_score: Overall health score as a percentage
        agents_health: Health score for agents as a percentage
        modules_health: Health score for modules as a percentage
        schemas_health: Health score for schemas as a percentage
        endpoints_health: Health score for endpoints as a percentage
        components_health: Health score for components as a percentage
        surface_drift: List of drift issues detected
        
    Returns:
        Dictionary containing the drift report
    """
    logger.info("Generating drift report")
    
    # Format health scores as strings
    agents_health_str = f"{agents_health:.1f}%"
    modules_health_str = f"{modules_health:.1f}%"
    schemas_health_str = f"{schemas_health:.1f}%"
    endpoints_health_str = f"{endpoints_health:.1f}%"
    components_health_str = f"{components_health:.1f}%"
    
    # Create report
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    report = {
        "startup_validation_date": today,
        "surface_health_score": round(surface_health_score, 1),
        "agents_health": agents_health_str,
        "modules_health": modules_health_str,
        "schemas_health": schemas_health_str,
        "endpoints_health": endpoints_health_str,
        "components_health": components_health_str,
        "surface_drift": surface_drift,
        "memory_tag": f"startup_surface_{'drift_detected' if surface_drift else 'validated'}_{today.replace('-', '')}"
    }
    
    logger.info(f"Drift report generated with health score: {surface_health_score:.1f}%")
    logger.debug(f"Report contains {len(surface_drift)} drift issues")
    
    return report

def save_drift_report(report: Dict[str, Any], drift_detected: bool) -> str:
    """
    Save the drift report to the appropriate location.
    
    Args:
        report: The drift report to save
        drift_detected: Whether drift was detected
        
    Returns:
        Path to the saved report file
    """
    logger.info("Saving drift report")
    
    # Determine report filename based on whether drift was detected
    today = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"startup_{'drift_report' if drift_detected else 'surface_verified'}_{today}.json"
    
    # Ensure logs directory exists
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    logs_dir = os.path.join(base_path, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Save report
    report_path = os.path.join(logs_dir, filename)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Drift report saved to {report_path}")
    
    return report_path

def format_drift_issue(
    surface_type: str,
    item_id: str,
    issue_description: str
) -> Dict[str, Any]:
    """
    Format a drift issue for inclusion in the report.
    
    Args:
        surface_type: Type of surface (agent, module, schema, endpoint, component)
        item_id: Identifier of the item with drift
        issue_description: Description of the drift issue
        
    Returns:
        Dictionary containing the formatted drift issue
    """
    return {
        "type": surface_type,
        "path": item_id,
        "issue": issue_description
    }
