"""
Tool Predictor Module

This module provides functionality to predict required tools for loop execution,
check their availability, and flag missing tools.
"""

import json
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Tool prediction heuristics
AGENT_TOOL_MAPPING = {
    "hal": ["file_writer", "code_generator", "api_client", "database_connector"],
    "nova": ["component_builder", "form_validator", "ui_renderer", "style_generator"],
    "critic": ["plan_validator", "schema_checker", "code_reviewer", "test_runner"],
    "ash": ["memory_manager", "context_tracker", "knowledge_base"],
    "operator": ["input_processor", "command_executor"],
    "cto": ["system_analyzer", "performance_monitor", "architecture_planner"],
    "orchestrator": ["loop_manager", "agent_coordinator", "plan_generator"]
}

FILE_TOOL_MAPPING = {
    ".jsx": ["component_builder", "file_writer", "ui_renderer"],
    ".js": ["file_writer", "code_generator", "api_client"],
    ".ts": ["file_writer", "code_generator", "type_checker"],
    ".tsx": ["component_builder", "file_writer", "ui_renderer", "type_checker"],
    ".py": ["file_writer", "code_generator", "api_client"],
    ".html": ["file_writer", "ui_renderer"],
    ".css": ["file_writer", "style_generator"],
    ".scss": ["file_writer", "style_generator"],
    ".json": ["file_writer", "schema_checker"],
    ".md": ["file_writer", "document_generator"],
    ".sql": ["database_connector", "query_builder"],
    ".yml": ["file_writer", "config_manager"],
    ".yaml": ["file_writer", "config_manager"],
    ".xml": ["file_writer", "data_parser"],
    ".csv": ["file_writer", "data_parser", "data_analyzer"]
}

GOAL_TOOL_MAPPING = {
    "api": ["api_client", "http_client", "request_builder"],
    "database": ["database_connector", "query_builder", "data_migrator"],
    "ui": ["component_builder", "ui_renderer", "style_generator"],
    "component": ["component_builder", "ui_renderer"],
    "form": ["form_validator", "input_processor"],
    "validation": ["form_validator", "schema_checker", "data_validator"],
    "test": ["test_runner", "code_reviewer"],
    "review": ["code_reviewer", "plan_validator"],
    "document": ["document_generator", "file_writer"],
    "report": ["document_generator", "data_analyzer"],
    "analyze": ["data_analyzer", "system_analyzer"],
    "performance": ["performance_monitor", "system_analyzer"],
    "style": ["style_generator", "ui_renderer"],
    "auth": ["auth_service", "user_manager"],
    "user": ["user_manager", "profile_service"],
    "file": ["file_writer", "file_reader"],
    "image": ["image_processor", "file_writer"],
    "video": ["video_processor", "file_writer"],
    "audio": ["audio_processor", "file_writer"],
    "chart": ["chart_generator", "data_visualizer"],
    "graph": ["chart_generator", "data_visualizer"],
    "visualization": ["data_visualizer", "chart_generator"],
    "search": ["search_engine", "query_builder"],
    "filter": ["data_filter", "search_engine"],
    "sort": ["data_sorter", "array_processor"],
    "email": ["email_service", "notification_service"],
    "notification": ["notification_service", "event_handler"],
    "schedule": ["scheduler", "calendar_service"],
    "payment": ["payment_processor", "financial_service"],
    "map": ["map_service", "location_service"],
    "chat": ["chat_service", "message_handler"],
    "translate": ["translation_service", "language_processor"],
    "deploy": ["deployment_service", "build_system"]
}

# Mock tool registry for checking availability
# In a real implementation, this would be fetched from a database or memory
MOCK_TOOL_REGISTRY = [
    "file_writer", "code_generator", "api_client", "database_connector",
    "component_builder", "ui_renderer", "style_generator",
    "plan_validator", "schema_checker", "code_reviewer", "test_runner",
    "memory_manager", "context_tracker", "knowledge_base",
    "input_processor", "command_executor",
    "system_analyzer", "performance_monitor", "architecture_planner",
    "loop_manager", "agent_coordinator", "plan_generator",
    "document_generator", "data_analyzer", "chart_generator",
    "search_engine", "data_filter", "data_sorter"
]

def predict_required_tools(plan: dict) -> list:
    """
    Predicts the tools required for a loop plan based on agents, goals, and planned files.
    
    Args:
        plan (dict): The loop plan object
        
    Returns:
        list: List of predicted required tools
    """
    if not plan or not isinstance(plan, dict):
        raise ValueError("Invalid plan object")
    
    required_tools = set()
    
    # Predict tools based on agents
    agents = plan.get("agents", [])
    for agent in agents:
        if agent in AGENT_TOOL_MAPPING:
            for tool in AGENT_TOOL_MAPPING[agent]:
                required_tools.add(tool)
    
    # Predict tools based on file extensions
    planned_files = plan.get("planned_files", [])
    for file_path in planned_files:
        _, ext = os.path.splitext(file_path)
        if ext in FILE_TOOL_MAPPING:
            for tool in FILE_TOOL_MAPPING[ext]:
                required_tools.add(tool)
    
    # Predict tools based on goals
    goals = plan.get("goals", [])
    for goal in goals:
        goal_lower = goal.lower()
        for keyword, tools in GOAL_TOOL_MAPPING.items():
            if keyword in goal_lower:
                for tool in tools:
                    required_tools.add(tool)
    
    # Check if plan already has tool_requirements
    if "tool_requirements" in plan and isinstance(plan["tool_requirements"], list):
        for tool in plan["tool_requirements"]:
            required_tools.add(tool)
    
    return sorted(list(required_tools))

def check_tool_availability(tools: list) -> dict:
    """
    Checks if the required tools are available in the tool registry.
    
    Args:
        tools (list): List of required tools
        
    Returns:
        dict: Dictionary mapping tool names to availability status
    """
    if not tools or not isinstance(tools, list):
        return {}
    
    availability = {}
    for tool in tools:
        if tool in MOCK_TOOL_REGISTRY:
            availability[tool] = "available"
        else:
            availability[tool] = "missing"
    
    return availability

def tool_check_driver(project_id: str, loop_plan: dict):
    """
    Orchestrator-facing entrypoint for checking tool requirements.
    
    Args:
        project_id (str): The project identifier
        loop_plan (dict): The loop plan object
        
    Returns:
        dict: The updated loop plan with tool requirements and availability
    """
    try:
        # Predict required tools
        required_tools = predict_required_tools(loop_plan)
        
        # Check tool availability
        tool_availability = check_tool_availability(required_tools)
        
        # Update the loop plan with tool requirements
        updated_plan = loop_plan.copy()
        updated_plan["tool_requirements"] = required_tools
        updated_plan["tools_available"] = tool_availability
        
        # Create a timestamp for logging
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Log to memory
        memory_entry = {
            "loop_id": loop_plan.get("loop_id"),
            "tools_required": required_tools,
            "tools_available": tool_availability,
            "timestamp": timestamp
        }
        log_to_memory(project_id, {"tool_requirements": [memory_entry]})
        
        # Log to chat
        missing_tools = [tool for tool, status in tool_availability.items() if status == "missing"]
        if missing_tools:
            log_to_chat(project_id, {
                "role": "orchestrator",
                "message": f"Warning: Missing tools required for loop execution: {', '.join(missing_tools)}",
                "timestamp": timestamp
            })
            
            # Log missing tools to memory for action
            for tool in missing_tools:
                missing_tool_entry = {
                    "loop_id": loop_plan.get("loop_id"),
                    "tool": tool,
                    "status": "missing",
                    "action_required": "generate_tool",
                    "timestamp": timestamp
                }
                log_to_memory(project_id, {"missing_tools": [missing_tool_entry]})
        else:
            log_to_chat(project_id, {
                "role": "orchestrator",
                "message": f"All required tools are available for loop execution.",
                "timestamp": timestamp
            })
        
        # Log to trace
        trace_entry = {
            "trace_id": f"loop_{loop_plan.get('loop_id')}_tools",
            "action": "tool_check",
            "status": "completed",
            "tools_required": len(required_tools),
            "tools_missing": len(missing_tools),
            "timestamp": timestamp
        }
        log_to_memory(project_id, {"orchestrator_tool_trace": [trace_entry]})
        
        return updated_plan
        
    except ValueError as e:
        # Handle errors in tool prediction
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        log_to_memory(project_id, {
            "orchestrator_warnings": [{
                "type": "tool_prediction_failed",
                "timestamp": timestamp,
                "error": str(e)
            }]
        })
        
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"Failed to predict required tools: {str(e)}.",
            "timestamp": timestamp
        })
        
        return loop_plan
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
            "message": f"An unexpected error occurred during tool prediction: {str(e)}.",
            "timestamp": timestamp
        })
        
        return loop_plan

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

if __name__ == "__main__":
    # Example usage
    example_plan = {
        "loop_id": 29,
        "agents": ["hal", "nova", "critic"],
        "goals": ["Create a React component for user profile", "Implement form validation"],
        "planned_files": ["src/components/UserProfile.jsx", "src/utils/validation.js"]
    }
    
    project_id = "lifetree_001"
    
    updated_plan = tool_check_driver(project_id, example_plan)
    
    print("\nUpdated loop plan:")
    print(json.dumps(updated_plan, indent=2))
