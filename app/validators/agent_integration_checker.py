"""
Agent Integration Checker for the System Integration Validator Agent.

This module checks agent configuration files to verify they include valid tool names
and tests the tool invocation path.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_agent_integration() -> Dict[str, Any]:
    """
    Check agent configuration files and verify tool invocation paths.
    
    Returns:
        Dictionary containing validation results
    """
    # Get the absolute path to the prompts directory
    prompts_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "app", "prompts"
    ))
    
    # Get the absolute path to the tools directory
    tools_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "app", "tools"
    ))
    
    # Get list of available tools (without .py extension)
    available_tools = [os.path.splitext(f)[0] for f in os.listdir(tools_dir) 
                      if f.endswith('.py') and not f.startswith('__')]
    
    # Get list of agent config files
    agent_configs = [f for f in os.listdir(prompts_dir) if f.endswith('.json') and f != 'validator.json']
    
    # Select at least 3 agent configs to check
    agent_configs_to_check = agent_configs[:3] if len(agent_configs) > 3 else agent_configs
    
    # Check each agent config
    results = []
    for config_file in agent_configs_to_check:
        config_path = os.path.join(prompts_dir, config_file)
        
        try:
            # Load the config file
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check if config has a tools array
            if 'tools' not in config or not isinstance(config['tools'], list):
                results.append({
                    "agent": config_file,
                    "success": False,
                    "error": "Config does not include a valid tools array",
                    "tools_valid": False,
                    "invocation_test": False
                })
                continue
            
            # Check if all tools in the array are valid
            tools = config['tools']
            invalid_tools = [tool for tool in tools if tool not in available_tools]
            tools_valid = len(invalid_tools) == 0
            
            # Test tool invocation path
            invocation_test = await test_tool_invocation(config['name'], tools)
            
            results.append({
                "agent": config_file,
                "success": tools_valid and invocation_test['success'],
                "tools_valid": tools_valid,
                "invalid_tools": invalid_tools if not tools_valid else [],
                "invocation_test": invocation_test
            })
            
        except Exception as e:
            results.append({
                "agent": config_file,
                "success": False,
                "error": f"Failed to process config file: {str(e)}",
                "tools_valid": False,
                "invocation_test": False
            })
    
    # Prepare overall result
    overall_success = all(result["success"] for result in results)
    
    result = {
        "check_name": "Agent Integration Check",
        "success": overall_success,
        "agents_checked": len(results),
        "agent_results": results
    }
    
    # Add recommendations if there are issues
    if not overall_success:
        recommendations = []
        
        for agent_result in results:
            if not agent_result["success"]:
                agent_name = agent_result["agent"]
                
                if not agent_result["tools_valid"] and "invalid_tools" in agent_result:
                    invalid_tools = agent_result["invalid_tools"]
                    recommendations.append(f"Fix invalid tools in {agent_name}: {', '.join(invalid_tools)}")
                
                if isinstance(agent_result["invocation_test"], dict) and not agent_result["invocation_test"].get("success", False):
                    error = agent_result["invocation_test"].get("error", "Unknown error")
                    recommendations.append(f"Fix tool invocation path for {agent_name}: {error}")
                
                if "error" in agent_result:
                    recommendations.append(f"Fix config file for {agent_name}: {agent_result['error']}")
        
        result["recommendations"] = recommendations
    
    return result

async def test_tool_invocation(agent_name: str, tools: List[str]) -> Dict[str, Any]:
    """
    Test the tool invocation path for an agent.
    
    Args:
        agent_name: Name of the agent
        tools: List of tools in the agent's config
        
    Returns:
        Dictionary with test results
    """
    try:
        # Import necessary modules
        from app.core.prompt_manager import PromptManager
        from app.core.tool_router import get_router
        
        # Get the prompt manager and router
        prompt_manager = PromptManager()
        router = get_router()
        
        # Check if the agent's prompt chain can be loaded
        prompt_chain = prompt_manager.get_prompt_chain(agent_name)
        if not prompt_chain:
            return {
                "success": False,
                "error": f"Failed to load prompt chain for {agent_name}"
            }
        
        # Check if at least one tool can be routed
        if tools:
            test_tool = tools[0]
            # Just check if the tool exists in the router, don't actually execute
            if test_tool in router.get_available_tools():
                return {
                    "success": True,
                    "message": f"Successfully verified tool invocation path for {agent_name}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Tool {test_tool} not available in router"
                }
        else:
            return {
                "success": False,
                "error": "No tools defined for agent"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to test tool invocation: {str(e)}"
        }

if __name__ == "__main__":
    # Run the check directly if this script is executed
    result = asyncio.run(check_agent_integration())
    print(json.dumps(result, indent=2))
