"""
Tool Router Connectivity Checker for the System Integration Validator Agent.

This module tests the connectivity of the tool router by attempting to route and run
commands through specific tools.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_tool_router_connectivity() -> Dict[str, Any]:
    """
    Test tool router connectivity by attempting to route and run commands through specific tools.
    
    Returns:
        Dictionary containing validation results
    """
    # Import the tool router
    try:
        from app.core.tool_router import get_router
        router = get_router()
        logger.info("Successfully imported tool router")
    except Exception as e:
        return {
            "check_name": "Tool Router Connectivity Check",
            "success": False,
            "error": f"Failed to import tool router: {str(e)}",
            "recommendations": ["Verify that app/core/tool_router.py exists and is properly implemented"]
        }
    
    # Define tools to test
    tools_to_test = [
        {
            "name": "web_search",
            "params": {"query": "latest AI developments"}
        },
        {
            "name": "code_executor",
            "params": {"language": "python", "code": "print('Hello, world!')"}
        },
        {
            "name": "pdf_ingest",
            "params": {"file_path": "test.pdf", "test_mode": True}
        },
        {
            "name": "email_drafter",
            "params": {"recipient": "test@example.com", "subject": "Test Email", "context": "This is a test email", "test_mode": True}
        },
        {
            "name": "autonomous_research_chain",
            "params": {"topic": "renewable energy", "depth": 1, "test_mode": True}
        }
    ]
    
    # Test each tool
    results = []
    for tool_info in tools_to_test:
        tool_name = tool_info["name"]
        params = tool_info["params"]
        
        try:
            logger.info(f"Testing tool: {tool_name}")
            
            # Add test_mode parameter to avoid actual execution
            if "test_mode" not in params:
                params["test_mode"] = True
                
            # Route and run the tool
            result = await router.route_tool(tool_name, **params)
            
            # Check if result is structured properly
            if isinstance(result, dict) and "status" in result:
                success = True
                error = None
            else:
                success = False
                error = f"Tool {tool_name} did not return a properly structured result"
            
        except Exception as e:
            success = False
            error = str(e)
        
        # Record result
        results.append({
            "tool": tool_name,
            "success": success,
            "error": error
        })
    
    # Check if logs were created
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app", "logs", "tool_logs")
    logs_exist = os.path.exists(logs_dir) and len(os.listdir(logs_dir)) > 0
    
    # Prepare overall result
    overall_success = all(result["success"] for result in results)
    
    result = {
        "check_name": "Tool Router Connectivity Check",
        "success": overall_success,
        "logs_created": logs_exist,
        "tool_results": results
    }
    
    # Add recommendations if there are issues
    if not overall_success:
        recommendations = []
        
        for tool_result in results:
            if not tool_result["success"]:
                recommendations.append(f"Fix connectivity issues with {tool_result['tool']}: {tool_result['error']}")
        
        if not logs_exist:
            recommendations.append("Verify that tool logging is properly configured")
        
        result["recommendations"] = recommendations
    
    return result

if __name__ == "__main__":
    # Run the check directly if this script is executed
    result = asyncio.run(check_tool_router_connectivity())
    print(json.dumps(result, indent=2))
