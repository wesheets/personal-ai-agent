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
        
        # Calculate endpoint health score as percentage of passing endpoints
        endpoint_health_score = (passed_endpoints / total_endpoints) * 100 if total_endpoints > 0 else 0
        
        # Calculate payload health metrics
        endpoints_with_payload = sum(1 for result in validation_results 
                                    if result["status_code"] is not None and 200 <= result["status_code"] < 300)
        passed_payloads = sum(1 for result in validation_results if result["payload_validation_status"] == "pass")
        failed_payloads = endpoints_with_payload - passed_payloads
        
        # Calculate payload health score as percentage of passing payloads
        payload_health_score = (passed_payloads / endpoints_with_payload) * 100 if endpoints_with_payload > 0 else 0
        
        # Count drift types
        drift_type_counts = {}
        for result in validation_results:
            if result.get("payload_drift_type"):
                drift_type = result["payload_drift_type"]
                drift_type_counts[drift_type] = drift_type_counts.get(drift_type, 0) + 1
        
        # Get details of failed endpoints
        failed_endpoint_details = [
            {
                "url": result["url"],
                "method": result["method"],
                "status_code": result["status_code"],
                "failure_reason": result["failure_reason"],
                "payload_validation_status": result.get("payload_validation_status", "fail"),
                "payload_drift_type": result.get("payload_drift_type"),
                "missing_fields": result.get("missing_fields", [])
            }
            for result in validation_results if result["validation_status"] == "fail"
        ]
        
        # Generate report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_endpoints_checked": total_endpoints,
            "total_endpoints_failed": failed_endpoints,
            "endpoint_health_score": round(endpoint_health_score, 1),
            "endpoints_with_payload": endpoints_with_payload,
            "passed_payloads": passed_payloads,
            "failed_payloads": failed_payloads,
            "payload_health_score": round(payload_health_score, 1),
            "drift_type_counts": drift_type_counts,
            "failed_endpoint_details": failed_endpoint_details,
            "validation_results": validation_results
        }
        
        logger.info(f"Generated drift report: {total_endpoints} endpoints, {passed_endpoints} passed, {failed_endpoints} failed")
        logger.info(f"Endpoint health score: {endpoint_health_score:.1f}%, Payload health score: {payload_health_score:.1f}%")
        logger.info(f"Drift types detected: {drift_type_counts}")
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
        payload_health_score = report["payload_health_score"]
        failed_endpoints = report["total_endpoints_failed"]
        failed_payloads = report["failed_payloads"]
        total_endpoints = report["total_endpoints_checked"]
        endpoints_with_payload = report["endpoints_with_payload"]
        
        # Create validation summary
        validation_summary = (
            f"Endpoint validation: {endpoint_health_score:.1f}% endpoint health, "
            f"{payload_health_score:.1f}% payload health. "
            f"{failed_endpoints} of {total_endpoints} endpoints failed, "
            f"{failed_payloads} of {endpoints_with_payload} payloads failed."
        )
        
        # Create drift categories
        drift_categories = ["endpoint_health"]
        if report["drift_type_counts"]:
            drift_categories.append("payload_validation")
            for drift_type in report["drift_type_counts"].keys():
                drift_categories.append(f"payload_{drift_type.lower()}")
        
        # Create drift history entry
        drift_entry = {
            "timestamp": timestamp,
            "surface_health_score": endpoint_health_score,  # Keep endpoint health as primary score for consistency
            "drift_issues_detected": failed_endpoints + failed_payloads,
            "validation_source": "endpoint_payload",
            "validation_summary": validation_summary,
            "endpoint_health_score": endpoint_health_score,
            "payload_health_score": payload_health_score,
            "failed_endpoints": failed_endpoints,
            "failed_payloads": failed_payloads,
            "total_endpoints": total_endpoints,
            "endpoints_with_payload": endpoints_with_payload,
            "drift_categories": drift_categories,
            "drift_type_counts": report["drift_type_counts"]
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
        
        # Add payload validation metrics
        manifest["system_manifest"]["last_payload_validation_timestamp"] = report["timestamp"]
        manifest["system_manifest"]["last_payload_health_score"] = report["payload_health_score"]
        manifest["system_manifest"]["last_payload_drift_report_path"] = report_path
        
        # Update Phase 3.1 status if it exists
        if "phase_3" in manifest["system_manifest"]["deployment_phases"]:
            if "subphases" in manifest["system_manifest"]["deployment_phases"]["phase_3"]:
                # Update Phase 3.1 status
                if "phase_3.1" in manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]:
                    manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]["phase_3.1"]["status"] = "completed"
                    manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]["phase_3.1"]["completed_date"] = datetime.datetime.now().strftime('%Y-%m-%d')
                    manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]["phase_3.1"]["notes"] = (
                        f"Endpoint Health Verification completed with {report['endpoint_health_score']}% health score. "
                        f"{report['total_endpoints_failed']} of {report['total_endpoints_checked']} endpoints failed."
                    )
                
                # Add Phase 3.2 status
                if "phase_3.2" not in manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]:
                    manifest["system_manifest"]["deployment_phases"]["phase_3"]["subphases"]["phase_3.2"] = {
                        "name": "Endpoint Payload Validation",
                        "status": "in_progress",
                        "started_date": datetime.datetime.now().strftime('%Y-%m-%d'),
                        "components": [
                            "Payload Validator",
                            "Payload Drift Report",
                            "Drift History Integration",
                            "System Manifest Expansion"
                        ],
                        "notes": (
                            f"Implementing endpoint payload validation to verify API response payloads. "
                            f"Current payload health score: {report['payload_health_score']}%. "
                            f"{report['failed_payloads']} of {report['endpoints_with_payload']} payloads failed. "
                            f"No automatic repairs are performed."
                        )
                    }
        
        # Save updated manifest
        try:
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            logger.info(f"Updated system manifest with endpoint and payload validation results")
        except Exception as e:
            logger.error(f"Error saving system manifest: {str(e)}")
