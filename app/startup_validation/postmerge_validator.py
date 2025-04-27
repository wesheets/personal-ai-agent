"""
Post-Merge Surface Validation Script

This is the main script for the Post-Merge Surface Validation system.
It validates cognitive surfaces after code merges, generates health scores,
creates drift reports, and adds memory tags without performing any repairs.

Usage:
    python -m app.startup_validation.postmerge_validator

This script should be triggered after code merges either manually via merge_hook.sh
or automatically via GitHub Actions.
"""

import os
import sys
import json
import datetime
import logging
import argparse
from typing import Dict, Any, List, Tuple, Optional

from app.startup_validation.utils.surface_loader import load_cognitive_surfaces
from app.startup_validation.utils.health_scorer import calculate_overall_health_score, format_health_percentage
from app.startup_validation.utils.drift_reporter import generate_drift_report, save_drift_report
from app.startup_validation.utils.memory_tagger import create_memory_tag, update_system_status, save_memory_tag_file
from app.utils.drift_trend_logger import log_drift_event

from app.startup_validation.validators.agent_validator import validate_agents
from app.startup_validation.validators.module_validator import validate_modules
from app.startup_validation.validators.schema_validator import validate_schemas
from app.startup_validation.validators.endpoint_validator import validate_endpoints
from app.startup_validation.validators.component_validator import validate_components

def setup_logging(verbose: bool = False):
    """
    Configure logging for the post-merge validation system.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    # Create logs directory if it doesn't exist
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    log_file = os.path.join(log_dir, f"postmerge_validation_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('postmerge_validation')
    logger.info(f"Logging initialized at level {logging.getLevelName(log_level)}")
    logger.info(f"Log file: {log_file}")
    
    return logger

def validate_cognitive_surfaces(base_path: str = "") -> Tuple[Dict[str, Any], bool]:
    """
    Validate all cognitive surfaces and generate a comprehensive report.
    
    Args:
        base_path: Base path to prepend to file paths
        
    Returns:
        Tuple containing:
        - Dictionary with the validation report
        - Boolean indicating whether drift was detected
    """
    logger = logging.getLogger('postmerge_validation')
    logger.info("Starting post-merge cognitive surface validation")
    
    # Load cognitive surfaces
    aci_data, pice_data = load_cognitive_surfaces(base_path)
    
    if aci_data is None:
        logger.error("Failed to load ACI data")
        return {"error": "Failed to load ACI data", "surface_health_score": 0.0}, True
    
    if pice_data is None:
        logger.error("Failed to load PICE data")
        return {"error": "Failed to load PICE data", "surface_health_score": 0.0}, True
    
    logger.info("Successfully loaded cognitive surfaces")
    
    # Validate each surface type
    agents_health, agents_drift = validate_agents(aci_data)
    modules_health, modules_drift = validate_modules(pice_data)
    schemas_health, schemas_drift = validate_schemas(pice_data)
    endpoints_health, endpoints_drift = validate_endpoints(pice_data)
    components_health, components_drift = validate_components(pice_data)
    
    # Calculate overall health score
    surface_health_score = calculate_overall_health_score(
        agents_health,
        modules_health,
        schemas_health,
        endpoints_health,
        components_health
    )
    
    # Combine all drift issues
    all_drift_issues = agents_drift + modules_drift + schemas_drift + endpoints_drift + components_drift
    drift_detected = len(all_drift_issues) > 0
    
    # Count items for each surface type
    agents_count = len(aci_data.get("agents", []))
    modules_count = len(pice_data.get("modules", []))
    schemas_count = len(pice_data.get("schemas", []))
    endpoints_count = len(pice_data.get("endpoints", []))
    components_count = len(pice_data.get("components", []))
    
    # Generate report
    report = generate_drift_report(
        surface_health_score,
        agents_health,
        modules_health,
        schemas_health,
        endpoints_health,
        components_health,
        all_drift_issues
    )
    
    # Add counts to report for memory tagging
    report["agents_count"] = agents_count
    report["modules_count"] = modules_count
    report["schemas_count"] = schemas_count
    report["endpoints_count"] = endpoints_count
    report["components_count"] = components_count
    
    logger.info(f"Post-merge validation complete. Health score: {surface_health_score:.1f}%. Drift detected: {drift_detected}")
    
    return report, drift_detected

def create_postmerge_memory_tag(drift_detected: bool) -> str:
    """
    Create a memory tag for post-merge validation.
    
    Args:
        drift_detected: Whether drift was detected
        
    Returns:
        Memory tag string
    """
    date_str = datetime.datetime.now().strftime('%Y%m%d')
    if drift_detected:
        return f"postmerge_surface_drift_detected_{date_str}"
    else:
        return f"postmerge_surface_validated_{date_str}"

def save_postmerge_drift_report(report: Dict[str, Any], drift_detected: bool) -> str:
    """
    Save the post-merge drift report to a file.
    
    Args:
        report: The drift report
        drift_detected: Whether drift was detected
        
    Returns:
        Path to the saved report file
    """
    logger = logging.getLogger('postmerge_validation.drift_reporter')
    logger.info("Saving post-merge drift report")
    
    # Create logs directory if it doesn't exist
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate filename
    date_str = datetime.datetime.now().strftime('%Y%m%d')
    report_file = os.path.join(log_dir, f"postmerge_drift_report_{date_str}.json")
    
    # Save report
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Drift report saved to {report_file}")
    
    return report_file

def update_system_manifest(memory_tag: str, report: Dict[str, Any]) -> None:
    """
    Update the system manifest with post-merge validation information.
    
    Args:
        memory_tag: The memory tag
        report: The validation report
    """
    logger = logging.getLogger('postmerge_validation')
    logger.info("Updating system manifest with post-merge validation metadata")
    
    # Get base path
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    manifest_file = os.path.join(base_path, "system", "system_manifest.json")
    
    try:
        # Create system directory if it doesn't exist
        os.makedirs(os.path.dirname(manifest_file), exist_ok=True)
        
        # Load existing manifest if it exists
        if os.path.exists(manifest_file):
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
        else:
            manifest = {
                "system_manifest": {
                    "name": "Promethios Personal AI Agent",
                    "version": "0.1.0",
                    "deployment_phases": {},
                    "last_updated": "",
                    "last_updated_by": ""
                }
            }
        
        # Ensure phase 2 exists
        if "deployment_phases" not in manifest["system_manifest"]:
            manifest["system_manifest"]["deployment_phases"] = {}
            
        if "phase_2" not in manifest["system_manifest"]["deployment_phases"]:
            manifest["system_manifest"]["deployment_phases"]["phase_2"] = {
                "name": "Cognitive Surface Stabilization",
                "subphases": {},
                "status": "in_progress"
            }
            
        if "subphases" not in manifest["system_manifest"]["deployment_phases"]["phase_2"]:
            manifest["system_manifest"]["deployment_phases"]["phase_2"]["subphases"] = {}
        
        # Update phase 2.2
        phase_2_2 = {
            "name": "Post-Merge Surface Validation",
            "status": "completed",
            "completed_date": datetime.datetime.now().strftime('%Y-%m-%d'),
            "components": [
                "Post-Merge Validator",
                "Merge Hook Script",
                "GitHub Action Workflow"
            ],
            "notes": f"Completed with health score: {report['surface_health_score']:.1f}%. " +
                    (f"Drift detected: {len(report['surface_drift'])} issues." if 'surface_drift' in report and len(report['surface_drift']) > 0 else "No drift detected.")
        }
        
        manifest["system_manifest"]["deployment_phases"]["phase_2"]["subphases"]["phase_2.2"] = phase_2_2
        
        # Update last updated
        manifest["system_manifest"]["last_updated"] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        manifest["system_manifest"]["last_updated_by"] = "Post-Merge Validation System"
        
        # Save manifest
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
            
        logger.info(f"System manifest updated at {manifest_file}")
        
    except Exception as e:
        logger.error(f"Error updating system manifest: {str(e)}", exc_info=True)

def main():
    """
    Main entry point for the post-merge validation system.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Promethios Post-Merge Surface Validation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--base-path", default="", help="Base path to prepend to file paths")
    args = parser.parse_args()
    
    # Set base path environment variable
    if args.base_path:
        os.environ["PROMETHIOS_BASE_PATH"] = args.base_path
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    try:
        logger.info("Starting Promethios Post-Merge Surface Validation")
        
        # Validate cognitive surfaces
        report, drift_detected = validate_cognitive_surfaces(args.base_path)
        
        # Create memory tag
        memory_tag = create_postmerge_memory_tag(drift_detected)
        report["memory_tag"] = memory_tag
        
        # Save report
        report_path = save_postmerge_drift_report(report, drift_detected)
        
        # Save memory tag file
        tag_file_path = save_memory_tag_file(memory_tag, report)
        
        # Update system status
        update_system_status(memory_tag, report)
        
        # Update system manifest
        update_system_manifest(memory_tag, report)
        
        # Log drift event to drift history
        drift_event = {
            "surface_health_score": report["surface_health_score"],
            "drift_issues_detected": len(report.get("surface_drift", [])),
            "validation_source": "post-merge",
            "validation_summary": f"Post-merge validation - {'Drift detected' if drift_detected else 'No drift detected'}"
        }
        drift_history_file = log_drift_event(drift_event)
        logger.info(f"Drift event logged to {drift_history_file}")
        
        # Log completion
        if drift_detected:
            logger.warning(f"Post-merge surface drift detected. Report saved to {report_path}")
            logger.warning(f"Memory tag created: {memory_tag}")
            print(f"\n⚠️  POST-MERGE SURFACE DRIFT DETECTED: {report['surface_health_score']:.1f}% health score")
            print(f"⚠️  Report saved to {report_path}")
            print(f"⚠️  Memory tag: {memory_tag}")
            print(f"⚠️  {len(report['surface_drift'])} drift issues found")
            print(f"⚠️  Drift history updated: {drift_history_file}")
            print("\nTop 5 drift issues:")
            for i, issue in enumerate(report['surface_drift'][:5]):
                print(f"  {i+1}. {issue['type'].upper()}: {issue['path']} - {issue['issue']}")
            print("\nNo automatic repairs will be performed. Operator intervention required.")
        else:
            logger.info(f"All post-merge surfaces validated. Report saved to {report_path}")
            logger.info(f"Memory tag created: {memory_tag}")
            print(f"\n✅ ALL POST-MERGE SURFACES VALIDATED: {report['surface_health_score']:.1f}% health score")
            print(f"✅ Report saved to {report_path}")
            print(f"✅ Memory tag: {memory_tag}")
            print(f"✅ Drift history updated: {drift_history_file}")
            print(f"✅ All cognitive surfaces are healthy after merge")
        
        return 0 if not drift_detected else 1
    
    except Exception as e:
        logger.error(f"Error during post-merge validation: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: Post-merge validation failed: {str(e)}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
