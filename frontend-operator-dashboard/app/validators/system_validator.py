"""
System Integration Validator for the Personal AI Agent System.

This module runs all validation tests and generates a comprehensive validation report.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

# Import validation checkers
from app.validators.tool_availability_checker import check_tool_availability
from app.validators.tool_router_connectivity_checker import check_tool_router_connectivity
from app.validators.agent_integration_checker import check_agent_integration
from app.validators.memory_retry_logic_checker import check_memory_retry_logic

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_validation_tests() -> Dict[str, Any]:
    """
    Run all validation tests and generate a comprehensive report.
    
    Returns:
        Dictionary containing validation results
    """
    logger.info("Starting system validation tests...")
    
    # Run all validation tests
    results = []
    
    # Test 1: Tool Availability Check
    logger.info("Running Tool Availability Check...")
    tool_availability_result = check_tool_availability()
    results.append(tool_availability_result)
    
    # Test 2: Tool Router Connectivity Check
    logger.info("Running Tool Router Connectivity Check...")
    tool_router_result = await check_tool_router_connectivity()
    results.append(tool_router_result)
    
    # Test 3: Agent Integration Check
    logger.info("Running Agent Integration Check...")
    agent_integration_result = await check_agent_integration()
    results.append(agent_integration_result)
    
    # Test 4: Memory and Retry Logic Check
    logger.info("Running Memory and Retry Logic Check...")
    memory_retry_result = await check_memory_retry_logic()
    results.append(memory_retry_result)
    
    # Determine overall success
    overall_success = all(result.get("success", False) for result in results)
    
    # Generate comprehensive report
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_success": overall_success,
        "tests_run": len(results),
        "tests_passed": sum(1 for result in results if result.get("success", False)),
        "tests_failed": sum(1 for result in results if not result.get("success", False)),
        "test_results": results
    }
    
    # Collect all recommendations
    all_recommendations = []
    for result in results:
        if not result.get("success", False) and "recommendations" in result:
            all_recommendations.extend(result["recommendations"])
    
    if all_recommendations:
        report["recommendations"] = all_recommendations
    
    # Save report to file
    logs_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "app", "logs"
    ))
    os.makedirs(logs_dir, exist_ok=True)
    
    report_path = os.path.join(logs_dir, "system_validation_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Validation report saved to {report_path}")
    
    return report

if __name__ == "__main__":
    # Run the validation tests directly if this script is executed
    asyncio.run(run_validation_tests())
