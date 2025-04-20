"""
Integration with plan_from_prompt.py

This module demonstrates how to integrate the plan validator with plan_from_prompt.py.
"""

import json
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from orchestrator.modules.plan_validator import validate_and_log

def plan_from_prompt(prompt, project_id):
    """
    Generate a loop plan from a prompt.
    
    Args:
        prompt (str): The operator prompt
        project_id (str): The project ID
        
    Returns:
        dict: The generated loop plan or None if validation fails
    """
    # In a real implementation, this would generate a plan based on the prompt
    # For demonstration purposes, we'll create a mock plan
    loop_plan = {
        "loop_id": 26,
        "agents": ["hal", "nova", "critic"],
        "goals": ["implement feature from prompt", "ensure code quality"],
        "planned_files": ["src/components/Feature.jsx", "src/utils/helpers.js"],
        "confirmed": False,
        "confirmed_by": "",
        "confirmed_at": ""
    }
    
    # Validate the plan
    is_valid, errors, trace = validate_and_log(loop_plan)
    
    # Log the validation result
    print(f"Plan validation: {'PASSED' if is_valid else 'FAILED'}")
    if not is_valid:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        
        # Log to memory and chat
        log_to_memory(project_id, {
            "orchestrator_warnings": [{
                "type": "plan_validation_failed",
                "timestamp": trace["timestamp"],
                "errors": errors
            }]
        })
        
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"Failed to create loop plan: {'; '.join(errors)}",
            "timestamp": trace["timestamp"]
        })
        
        return None
    
    # Log the trace to memory
    log_to_memory(project_id, {
        "orchestrator_traces": [trace]
    })
    
    return loop_plan

def log_to_memory(project_id, data):
    """
    Log data to project memory.
    
    Args:
        project_id (str): The project ID
        data (dict): The data to log
    """
    # In a real implementation, this would store data in a database or file
    print(f"Logging to memory for project {project_id}:")
    print(json.dumps(data, indent=2))

def log_to_chat(project_id, message):
    """
    Log a message to the chat.
    
    Args:
        project_id (str): The project ID
        message (dict): The message to log
    """
    # In a real implementation, this would add the message to the chat
    print(f"Logging to chat for project {project_id}:")
    print(json.dumps(message, indent=2))

if __name__ == "__main__":
    # Example usage
    prompt = "Create a new feature for the dashboard"
    project_id = "lifetree_001"
    
    plan = plan_from_prompt(prompt, project_id)
    
    if plan:
        print("\nSuccessfully created loop plan:")
        print(json.dumps(plan, indent=2))
    else:
        print("\nFailed to create loop plan due to validation errors.")
