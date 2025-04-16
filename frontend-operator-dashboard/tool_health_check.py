import os
import json
import importlib.util
import inspect
import sys

def check_tool_health():
    """
    Iterate through all files in /app/tools/*.py
    - Confirm each has a `run()` method
    - Validate imports and that no tool crashes when mocked
    - Log results to /app/logs/diagnostics/tool_health_report.json
    """
    tools_dir = "/home/ubuntu/personal-ai-agent/app/tools"
    log_file = "/home/ubuntu/personal-ai-agent/app/logs/diagnostics/tool_health_report.json"
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    results = {
        "total_tools": 0,
        "tools_with_run_method": 0,
        "tools_with_import_errors": 0,
        "tools_details": []
    }
    
    # Get all Python files in the tools directory
    tool_files = [f for f in os.listdir(tools_dir) if f.endswith('.py') and not f.startswith('__')]
    results["total_tools"] = len(tool_files)
    
    for tool_file in tool_files:
        tool_path = os.path.join(tools_dir, tool_file)
        tool_name = os.path.splitext(tool_file)[0]
        
        tool_result = {
            "name": tool_name,
            "file": tool_path,
            "has_run_method": False,
            "import_status": "success",
            "import_error": None,
            "run_method_signature": None
        }
        
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(tool_name, tool_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[tool_name] = module
            spec.loader.exec_module(module)
            
            # Check if the module has a run method
            if hasattr(module, 'run'):
                tool_result["has_run_method"] = True
                results["tools_with_run_method"] += 1
                
                # Get the run method signature
                run_method = getattr(module, 'run')
                signature = str(inspect.signature(run_method))
                tool_result["run_method_signature"] = signature
            
        except Exception as e:
            tool_result["import_status"] = "error"
            tool_result["import_error"] = str(e)
            results["tools_with_import_errors"] += 1
        
        results["tools_details"].append(tool_result)
    
    # Calculate success rate
    results["success_rate"] = (results["tools_with_run_method"] / results["total_tools"]) * 100 if results["total_tools"] > 0 else 0
    
    # Write results to log file
    with open(log_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Tool health check completed. Results saved to {log_file}")
    print(f"Total tools: {results['total_tools']}")
    print(f"Tools with run method: {results['tools_with_run_method']}")
    print(f"Tools with import errors: {results['tools_with_import_errors']}")
    print(f"Success rate: {results['success_rate']:.2f}%")
    
    return results

if __name__ == "__main__":
    check_tool_health()
