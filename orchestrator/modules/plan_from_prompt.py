"""
Plan From Prompt Module

This module provides functionality to convert natural language prompts into structured loop plans.
"""

import json
import os
import sys
from datetime import datetime
import re

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.plan_validator import validate_and_log

# Available agent types
AVAILABLE_AGENTS = ["hal", "nova", "critic", "ash", "operator", "cto", "orchestrator"]

def generate_plan_from_prompt(prompt: str, loop_id: int) -> dict:
    """
    Generates a structured loop plan from a natural language prompt.
    
    Args:
        prompt (str): The natural language prompt from the operator
        loop_id (int): The unique identifier for this loop
        
    Returns:
        dict: A structured loop plan object
    """
    if not prompt or len(prompt.strip()) < 10:
        raise ValueError("Prompt is too short or empty. Please provide a more detailed prompt.")
    
    # Extract goals from the prompt
    goals = extract_goals(prompt)
    if not goals:
        goals = ["Process and execute operator request"]
    
    # Determine appropriate agents based on the prompt content
    agents = determine_agents(prompt)
    
    # Predict files that will be created or modified
    planned_files = predict_files(prompt)
    
    # Determine if any specific tools are required
    tools_required = predict_tools(prompt)
    
    # Create the loop plan object
    loop_plan = {
        "loop_id": loop_id,
        "agents": agents,
        "goals": goals,
        "planned_files": planned_files,
        "confirmed": False,
        "confirmed_by": "",
        "confirmed_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Add optional fields if they have values
    if tools_required:
        loop_plan["tool_requirements"] = tools_required
    
    return loop_plan

def extract_goals(prompt: str) -> list:
    """
    Extracts goals from the prompt.
    
    Args:
        prompt (str): The natural language prompt
        
    Returns:
        list: Extracted goals
    """
    # Look for explicit goal statements
    goal_patterns = [
        r"(?:goal|objective|aim|purpose|task)(?:s)?\s*(?:is|are|:)?\s*(?:to)?\s*(.*?)(?:\.|$)",
        r"(?:I want|I need|I'd like|Please|Can you)\s+(.*?)(?:\.|$)",
        r"(?:Create|Build|Develop|Implement|Make)\s+(.*?)(?:\.|$)"
    ]
    
    goals = []
    for pattern in goal_patterns:
        matches = re.finditer(pattern, prompt, re.IGNORECASE)
        for match in matches:
            goal = match.group(1).strip()
            if goal and len(goal) > 5 and goal not in goals:
                goals.append(goal)
    
    # If no explicit goals found, break the prompt into potential tasks
    if not goals and len(prompt) > 10:
        sentences = re.split(r'[.!?]', prompt)
        for sentence in sentences:
            if len(sentence.strip()) > 10:
                goals.append(sentence.strip())
                if len(goals) >= 3:  # Limit to 3 goals if extracting from sentences
                    break
    
    return goals

def determine_agents(prompt: str) -> list:
    """
    Determines which agents should be involved based on the prompt content.
    
    Args:
        prompt (str): The natural language prompt
        
    Returns:
        list: List of agent names
    """
    # Default agent sequence for most tasks
    default_agents = ["hal", "nova", "critic"]
    
    # Check if specific agents are mentioned or implied
    prompt_lower = prompt.lower()
    
    # Check for specific development tasks
    if any(term in prompt_lower for term in ["code", "develop", "implement", "programming", "software", "application"]):
        return ["hal", "nova", "critic"]
    
    # Check for design or UI tasks
    if any(term in prompt_lower for term in ["design", "ui", "interface", "layout", "visual", "css", "style"]):
        return ["nova", "hal", "critic"]
    
    # Check for analysis or research tasks
    if any(term in prompt_lower for term in ["analyze", "research", "investigate", "study", "report", "data"]):
        return ["hal", "critic", "nova"]
    
    # Check for system or architecture tasks
    if any(term in prompt_lower for term in ["system", "architecture", "infrastructure", "performance", "optimize"]):
        return ["hal", "critic", "cto"]
    
    # If specific agents are mentioned, include them
    mentioned_agents = []
    for agent in AVAILABLE_AGENTS:
        if agent in prompt_lower:
            mentioned_agents.append(agent)
    
    if mentioned_agents:
        # Ensure we have at least the three core agents
        for agent in default_agents:
            if agent not in mentioned_agents:
                mentioned_agents.append(agent)
        return mentioned_agents[:5]  # Limit to 5 agents
    
    return default_agents

def predict_files(prompt: str) -> list:
    """
    Predicts which files will be created or modified based on the prompt.
    
    Args:
        prompt (str): The natural language prompt
        
    Returns:
        list: List of predicted file paths
    """
    prompt_lower = prompt.lower()
    planned_files = []
    
    # Look for explicit file mentions
    file_patterns = [
        r'(?:file|document|code)\s+(?:called|named)?\s*["\']?([a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9]+)["\']?',
        r'([a-zA-Z0-9_\-\.\/]+\.[a-zA-Z0-9]+)',
        r'([a-zA-Z0-9_\-]+\.(js|py|jsx|ts|tsx|html|css|json|md|txt))'
    ]
    
    for pattern in file_patterns:
        matches = re.finditer(pattern, prompt)
        for match in matches:
            file = match.group(1).strip()
            if file and file not in planned_files:
                planned_files.append(file)
    
    # Predict files based on task type
    if not planned_files:
        # UI/Frontend tasks
        if any(term in prompt_lower for term in ["ui", "interface", "component", "react", "frontend"]):
            planned_files.extend(["src/components/Component.jsx", "src/styles/component.css"])
        
        # Backend tasks
        elif any(term in prompt_lower for term in ["api", "backend", "server", "database"]):
            planned_files.extend(["src/api/endpoint.js", "src/models/model.js"])
        
        # Documentation tasks
        elif any(term in prompt_lower for term in ["document", "readme", "documentation"]):
            planned_files.extend(["docs/README.md", "docs/usage.md"])
        
        # Data analysis tasks
        elif any(term in prompt_lower for term in ["data", "analysis", "report"]):
            planned_files.extend(["data/analysis.py", "reports/findings.md"])
        
        # Default case
        else:
            planned_files.extend(["src/main.js", "README.md"])
    
    return planned_files

def predict_tools(prompt: str) -> list:
    """
    Predicts which tools might be required based on the prompt.
    
    Args:
        prompt (str): The natural language prompt
        
    Returns:
        list: List of predicted required tools
    """
    prompt_lower = prompt.lower()
    tools_required = []
    
    # Map keywords to tools
    tool_keywords = {
        "form": "form_builder",
        "chart": "chart_generator",
        "graph": "chart_generator",
        "visualization": "chart_generator",
        "database": "database_connector",
        "sql": "database_connector",
        "api": "api_client",
        "http": "api_client",
        "fetch": "api_client",
        "authentication": "auth_service",
        "login": "auth_service",
        "file upload": "file_uploader",
        "upload": "file_uploader",
        "markdown": "markdown_parser",
        "pdf": "pdf_generator",
        "report": "pdf_generator",
        "email": "email_service",
        "notification": "notification_service",
        "alert": "notification_service",
        "map": "map_service",
        "location": "map_service",
        "geocode": "map_service",
        "payment": "payment_processor",
        "checkout": "payment_processor",
        "search": "search_engine",
        "filter": "search_engine",
        "analytics": "analytics_tracker",
        "tracking": "analytics_tracker",
        "image": "image_processor",
        "photo": "image_processor",
        "video": "video_processor",
        "audio": "audio_processor",
        "sound": "audio_processor",
        "chat": "chat_service",
        "message": "chat_service",
        "calendar": "calendar_service",
        "schedule": "calendar_service",
        "appointment": "calendar_service"
    }
    
    for keyword, tool in tool_keywords.items():
        if keyword in prompt_lower and tool not in tools_required:
            tools_required.append(tool)
    
    return tools_required

def plan_from_prompt_driver(project_id: str, prompt: str):
    """
    Orchestrator-facing entrypoint for generating loop plans from prompts.
    
    Args:
        project_id (str): The project identifier
        prompt (str): The natural language prompt
        
    Returns:
        dict or None: The validated loop plan or None if validation fails
    """
    try:
        # Generate a loop ID (in a real system, this would be from a sequence or database)
        loop_id = int(datetime.now().timestamp()) % 1000
        
        # Generate the plan from the prompt
        loop_plan = generate_plan_from_prompt(prompt, loop_id)
        
        # Validate the plan
        is_valid, errors, trace = validate_and_log(loop_plan)
        
        # Log the trace to memory
        log_to_memory(project_id, {
            "orchestrator_traces": [trace]
        })
        
        if not is_valid:
            # Log validation errors to memory and chat
            error_message = "; ".join(errors)
            log_to_memory(project_id, {
                "orchestrator_warnings": [{
                    "type": "plan_validation_failed",
                    "timestamp": trace["timestamp"],
                    "errors": errors
                }]
            })
            
            log_to_chat(project_id, {
                "role": "orchestrator",
                "message": f"Failed to create loop plan: {error_message}",
                "timestamp": trace["timestamp"]
            })
            
            return None
        
        # Log the successful plan to memory
        log_to_memory(project_id, {
            "loop_plans": [loop_plan]
        })
        
        # Log to chat
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"Created loop plan with {len(loop_plan['goals'])} goals and {len(loop_plan['agents'])} agents.",
            "timestamp": trace["timestamp"],
            "loop_plan": loop_plan
        })
        
        # Log to sandbox
        log_to_sandbox(project_id, loop_plan)
        
        return loop_plan
        
    except ValueError as e:
        # Handle errors in plan generation
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        log_to_memory(project_id, {
            "orchestrator_warnings": [{
                "type": "plan_generation_failed",
                "timestamp": timestamp,
                "error": str(e)
            }]
        })
        
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"Failed to generate loop plan: {str(e)}. Please provide a more detailed prompt.",
            "timestamp": timestamp
        })
        
        return None
    except Exception as e:
        # Handle unexpected errors
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        log_to_memory(project_id, {
            "orchestrator_errors": [{
                "type": "unexpected_error",
                "timestamp": timestamp,
                "error": str(e)
            }]
        })
        
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"An unexpected error occurred: {str(e)}. Please try again.",
            "timestamp": timestamp
        })
        
        return None

def log_to_memory(project_id: str, data: dict):
    """
    Logs data to project memory.
    
    Args:
        project_id (str): The project ID
        data (dict): The data to log
    """
    # In a real implementation, this would store data in a database or file
    print(f"Logging to memory for project {project_id}:")
    print(json.dumps(data, indent=2))

def log_to_chat(project_id: str, message: dict):
    """
    Logs a message to the chat.
    
    Args:
        project_id (str): The project ID
        message (dict): The message to log
    """
    # In a real implementation, this would add the message to the chat
    print(f"Logging to chat for project {project_id}:")
    print(json.dumps(message, indent=2))

def log_to_sandbox(project_id: str, loop_plan: dict):
    """
    Logs a loop plan to the orchestrator sandbox.
    
    Args:
        project_id (str): The project ID
        loop_plan (dict): The loop plan to log
    """
    # In a real implementation, this would update the orchestrator sandbox
    print(f"Logging to sandbox for project {project_id}:")
    print(json.dumps(loop_plan, indent=2))

if __name__ == "__main__":
    # Example usage
    prompt = "Create a new React component for displaying user profiles with avatar, name, and bio."
    project_id = "lifetree_001"
    
    plan = plan_from_prompt_driver(project_id, prompt)
    
    if plan:
        print("\nSuccessfully created loop plan:")
        print(json.dumps(plan, indent=2))
    else:
        print("\nFailed to create loop plan due to errors.")
