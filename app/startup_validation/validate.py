"""
Startup Surface Validation Script

This is the main script for the Startup Surface Validation system.
It validates cognitive surfaces at system boot, generates health scores,
creates drift reports, and adds memory tags without performing any repairs.

Usage:
    python -m app.startup_validation.validate

This script should be integrated into the system boot process.
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
    Configure logging for the startup validation system.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    # Create logs directory if it doesn't exist
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    log_file = os.path.join(log_dir, f"startup_validation_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('startup_validation')
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
    logger = logging.getLogger('startup_validation')
    logger.info("Starting cognitive surface validation")
    
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
    
    logger.info(f"Validation complete. Health score: {surface_health_score:.1f}%. Drift detected: {drift_detected}")
    
    return report, drift_detected

def main():
    """
    Main entry point for the startup validation system.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Promethios Startup Surface Validation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--base-path", default="", help="Base path to prepend to file paths")
    args = parser.parse_args()
    
    # Set base path environment variable
    if args.base_path:
        os.environ["PROMETHIOS_BASE_PATH"] = args.base_path
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    try:
        logger.info("Starting Promethios Startup Surface Validation")
        
        # Validate cognitive surfaces
        report, drift_detected = validate_cognitive_surfaces(args.base_path)
        
        # Create memory tag
        memory_tag = create_memory_tag(drift_detected)
        report["memory_tag"] = memory_tag
        
        # Save report
        report_path = save_drift_report(report, drift_detected)
        
        # Save memory tag file
        tag_file_path = save_memory_tag_file(memory_tag, report)
        
        # Update system status
        update_system_status(memory_tag, report)
        
        # Log drift event to drift history
        drift_event = {
            "surface_health_score": report["surface_health_score"],
            "drift_issues_detected": len(report.get("surface_drift", [])),
            "validation_source": "startup",
            "validation_summary": f"Startup validation - {'Drift detected' if drift_detected else 'No drift detected'}"
        }
        drift_history_file = log_drift_event(drift_event)
        logger.info(f"Drift event logged to {drift_history_file}")
        
        # Log completion
        if drift_detected:
            logger.warning(f"Surface drift detected. Report saved to {report_path}")
            logger.warning(f"Memory tag created: {memory_tag}")
            print(f"\n⚠️  SURFACE DRIFT DETECTED: {report['surface_health_score']:.1f}% health score")
            print(f"⚠️  Report saved to {report_path}")
            print(f"⚠️  Memory tag: {memory_tag}")
            print(f"⚠️  {len(report['surface_drift'])} drift issues found")
            print(f"⚠️  Drift history updated: {drift_history_file}")
            print("\nTop 5 drift issues:")
            for i, issue in enumerate(report['surface_drift'][:5]):
                print(f"  {i+1}. {issue['type'].upper()}: {issue['path']} - {issue['issue']}")
            print("\nNo automatic repairs will be performed. Operator intervention required.")
        else:
            logger.info(f"All surfaces validated. Report saved to {report_path}")
            logger.info(f"Memory tag created: {memory_tag}")
            print(f"\n✅ ALL SURFACES VALIDATED: {report['surface_health_score']:.1f}% health score")
            print(f"✅ Report saved to {report_path}")
            print(f"✅ Memory tag: {memory_tag}")
            print(f"✅ Drift history updated: {drift_history_file}")
            print(f"✅ All cognitive surfaces are healthy")
        
        return 0 if not drift_detected else 1
    
    except Exception as e:
        logger.error(f"Error during startup validation: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: Startup validation failed: {str(e)}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
