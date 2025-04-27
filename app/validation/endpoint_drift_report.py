"""
Endpoint Drift Report Generator

This module provides functionality to generate drift reports from endpoint validation results
and update the drift history log.
"""

import os
import json
import datetime
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import the drift trend logger from Phase 2.3
from app.utils.drift_trend_logger import log_drift_event, get_recent_drift_history

# Configure logging
logger = logging.getLogger('endpoint_drift_report')

class EndpointDriftReportGenerator:
    """
    Generates drift reports from endpoint validation results and updates drift history.
    """
    
    def __init__(self, base_path: str = ""):
        """
        Initialize the endpoint drift report generator.
        
        Args:
            base_path: Base path to prepend to file paths
        """
        self.base_path = base_path
        self.logs_dir = os.path.join(base_path, "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
    def generate_report(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a drift report from validation results.
        
        Args:
            validation_results: List of validation result dictionaries
            
        Returns:
            Drift report dictionary
        """
        total_endpoints = len(validation_results)
        passed_endpoints = sum(1 for result in validation_results if result["validation_status"] == "pass")
        failed_endpoints = total_endpoints - passed_endpoints
        
        # Calculate health score as percentage of passing endpoints
        health_score = (passed_endpoints / total_endpoints) * 100 if total_endpoints > 0 else 0
        
        # Get details of failed endpoints
        failed_endpoint_details = [
            {
                "url": result["url"],
                "method": result["method"],
                "status_code": result["status_code"],
                "failure_reason": result["failure_reason"]
            }
            for result in validation_results if result["validation_status"] == "fail"
        ]
        
        # Generate report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_endpoints_checked": total_endpoints,
            "total_endpoints_failed": failed_endpoints,
            "endpoint_health_score": round(health_score, 1),
            "failed_endpoint_details": failed_endpoint_details,
            "validation_results": validation_results
        }
        
        logger.info(f"Generated drift report: {total_endpoints} endpoints, {passed_endpoints} passed, {failed_endpoints} failed, {health_score:.1f}% health score")
        return report
    
    def save_report(self, report: Dict[str, Any]) -> str:
        """
        Save the drift report to a file.
        
        Args:
            report: Drift report dictionary
            
        Returns:
            Path to the saved report file
        """
        # Generate filename with current date
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        report_file = os.path.join(self.logs_dir, f"endpoint_drift_report_{date_str}.json")
        
        # Save report
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Saved drift report to {report_file}")
        return report_file
    
    def update_drift_history(self, report: Dict[str, Any]) -> None:
        """
        Update the drift history log with the endpoint validation results.
        
        Args:
            report: Drift report dictionary
        """
        # Extract data for drift history entry
        timestamp = report["timestamp"]
        endpoint_health_score = report["endpoint_health_score"]
        failed_endpoints = report["total_endpoints_failed"]
        total_endpoints = report["total_endpoints_checked"]
        
        # Create validation summary
        validation_summary = f"Endpoint validation: {endpoint_health_score:.1f}% health score, {failed_endpoints} of {total_endpoints} endpoints failed"
        
        # Create drift history entry
        drift_entry = {
            "timestamp": timestamp,
            "surface_health_score": endpoint_health_score,
            "drift_issues_detected": failed_endpoints,
            "validation_source": "endpoint",
            "validation_summary": validation_summary,
            "endpoint_health_score": endpoint_health_score,
            "failed_endpoints": failed_endpoints,
            "total_endpoints": total_endpoints,
            "drift_categories": ["endpoint_health"]
        }
        
        # Log drift event
        log_drift_event(drift_entry)
        
        logger.info(f"Updated drift history with endpoint validation results: {validation_summary}")
    
    def update_system_manifest(self, report: Dict[str, Any], report_path: str) -> None:
        """
        Update the system manifest with endpoint validation results.
        
        Args:
            report: Drift report dictionary
            report_path: Path to the saved report file
        """
        # Load system manifest
        manifest_path = os.path.join(self.base_path, "system", "system_manifest.json")
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except Exception as e:
            logger.error(f"Error loading system manifest: {str(e)}")
            return
        
        # Update manifest with endpoint validation results
        manifest["system_manifest"]["last_endpoint_validation_timestamp"] = report["timestamp"]
        manifest["system_manifest"]["last_endpoint_health_score"] = report["endpoint_health_score"]
        manifest["system_manifest"]["last_endpoint_drift_report_path"] = report_path
        
        # Update Phase 3.1 status if it exists
        if "phase_3" in manifest["system_manifest"]["deployment_phases"]:
            if "subphases" in manifest["system_manifest"]["deployment_phases"]["phase_3"]:
                if "phase_3.1" in manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]:
                    manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]["phase_3.1"]["status"] = "completed"
                    manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]["phase_3.1"]["completed_date"] = datetime.datetime.now().strftime('%Y-%m-%d')
                    manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]["phase_3.1"]["notes"] = f"Endpoint Health Verification completed with {report['endpoint_health_score']}% health score. {report['total_endpoints_failed']} of {report['total_endpoints_checked']} endpoints failed."
        
        # Save updated manifest
        try:
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            logger.info(f"Updated system manifest with endpoint validation results")
        except Exception as e:
            logger.error(f"Error saving system manifest: {str(e)}")
