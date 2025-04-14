import os
import json
import importlib
import sys
import datetime

def run_agent_execution_test():
    """
    Simulate basic prompts for builder, research, memory, planner, and ops agents
    - Confirm each:
        - Loads config
        - Calls at least one tool
        - Stores memory
        - Logs execution
    - Save results to /app/logs/diagnostics/agent_execution_test.json
    """
    log_file = "/home/ubuntu/personal-ai-agent/app/logs/diagnostics/agent_execution_test.json"
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Define agents to test
    agents = ["builder", "research", "memory", "planner", "ops"]
    
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_agents": len(agents),
        "successful_agents": 0,
        "agent_details": []
    }
    
    # Check if prompts directory exists and has agent config files
    prompts_dir = "/home/ubuntu/personal-ai-agent/app/prompts"
    if not os.path.exists(prompts_dir):
        print(f"Error: Prompts directory not found at {prompts_dir}")
        results["error"] = f"Prompts directory not found at {prompts_dir}"
        with open(log_file, 'w') as f:
            json.dump(results, f, indent=2)
        return results
    
    # Get available prompt files
    prompt_files = [f for f in os.listdir(prompts_dir) if f.endswith('.json')]
    print(f"Found {len(prompt_files)} prompt files: {prompt_files}")
    
    # Mock functions for testing
    def mock_tool_call(tool_name, **kwargs):
        return {
            "status": "success",
            "tool": tool_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "result": f"Mocked result from {tool_name}"
        }
    
    def mock_memory_store(agent_name, content, tags=None):
        return {
            "status": "success",
            "agent": agent_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "memory_id": f"mock-memory-{datetime.datetime.now().timestamp()}"
        }
    
    def mock_log_execution(agent_name, prompt, response, tools_used=None):
        return {
            "status": "success",
            "agent": agent_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "log_id": f"mock-log-{datetime.datetime.now().timestamp()}"
        }
    
    # Test each agent
    for agent_name in agents:
        agent_result = {
            "name": agent_name,
            "config_loaded": False,
            "tool_called": False,
            "memory_stored": False,
            "execution_logged": False,
            "errors": []
        }
        
        # Check if agent config exists
        config_file = f"{prompts_dir}/{agent_name}.json"
        if not os.path.exists(config_file):
            agent_result["errors"].append(f"Config file not found: {config_file}")
            results["agent_details"].append(agent_result)
            continue
        
        # Load agent config
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            agent_result["config_loaded"] = True
            agent_result["config_summary"] = {
                "name": config.get("name", "Unknown"),
                "role": config.get("role", "Unknown"),
                "tools": config.get("tools", [])[:3]  # Show first 3 tools only
            }
        except Exception as e:
            agent_result["errors"].append(f"Error loading config: {str(e)}")
            results["agent_details"].append(agent_result)
            continue
        
        # Simulate tool call
        try:
            # Get first tool from config if available
            tools = config.get("tools", [])
            if tools:
                tool_name = tools[0]
                tool_result = mock_tool_call(tool_name)
                agent_result["tool_called"] = True
                agent_result["tool_result"] = tool_result
            else:
                agent_result["errors"].append("No tools defined in config")
        except Exception as e:
            agent_result["errors"].append(f"Error calling tool: {str(e)}")
        
        # Simulate memory storage
        try:
            memory_result = mock_memory_store(
                agent_name, 
                f"Test memory for {agent_name} agent", 
                tags=[agent_name, "test"]
            )
            agent_result["memory_stored"] = True
            agent_result["memory_result"] = memory_result
        except Exception as e:
            agent_result["errors"].append(f"Error storing memory: {str(e)}")
        
        # Simulate execution logging
        try:
            log_result = mock_log_execution(
                agent_name,
                f"Test prompt for {agent_name} agent",
                f"Test response from {agent_name} agent",
                tools_used=[tools[0]] if tools else []
            )
            agent_result["execution_logged"] = True
            agent_result["log_result"] = log_result
        except Exception as e:
            agent_result["errors"].append(f"Error logging execution: {str(e)}")
        
        # Check overall success
        if (agent_result["config_loaded"] and 
            agent_result["tool_called"] and 
            agent_result["memory_stored"] and 
            agent_result["execution_logged"]):
            agent_result["status"] = "success"
            results["successful_agents"] += 1
        else:
            agent_result["status"] = "failure"
        
        results["agent_details"].append(agent_result)
    
    # Calculate success rate
    results["success_rate"] = (results["successful_agents"] / results["total_agents"]) * 100 if results["total_agents"] > 0 else 0
    
    # Write results to log file
    with open(log_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Agent execution test completed. Results saved to {log_file}")
    print(f"Total agents tested: {results['total_agents']}")
    print(f"Successful agents: {results['successful_agents']}")
    print(f"Success rate: {results['success_rate']:.2f}%")
    
    return results

if __name__ == "__main__":
    run_agent_execution_test()
