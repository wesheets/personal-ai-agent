from datetime import datetime

# Mock memory module for development and testing
PROJECT_MEMORY = {}

def initialize_project_memory(project_id: str):
    """
    Initialize project memory for a new project.
    """
    if project_id not in PROJECT_MEMORY:
        PROJECT_MEMORY[project_id] = {
            "loop_count": 0,
            "completed_steps": [],
            "planned_steps": [],
            "last_reflection": {},
            "reflections_history": [],
            "tool_history": [],
            "cto_reflections": [],
            "system_flags": []
        }
    return PROJECT_MEMORY[project_id]

def get_project_memory(project_id: str):
    """
    Get project memory for an existing project.
    """
    if project_id not in PROJECT_MEMORY:
        return initialize_project_memory(project_id)
    return PROJECT_MEMORY[project_id]

def update_project_memory(project_id: str, key: str, value):
    """
    Update a specific key in project memory.
    """
    if project_id not in PROJECT_MEMORY:
        initialize_project_memory(project_id)
    
    PROJECT_MEMORY[project_id][key] = value
    return PROJECT_MEMORY[project_id]
