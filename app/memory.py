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
            "system_flags": [],
            "reflection_scores": [],
            "drift_logs": [],
            "loop_snapshots": [],
            "cto_audit_history": [],
            "cto_warnings": [],
            "system_health_score": 1.0
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

def add_reflection_score(project_id: str, score: float, summary: str = ""):
    """
    Add a reflection score to the project memory.
    """
    if project_id not in PROJECT_MEMORY:
        initialize_project_memory(project_id)
    
    reflection_score = {
        "timestamp": datetime.utcnow().isoformat(),
        "score": score,
        "summary": summary
    }
    
    PROJECT_MEMORY[project_id].setdefault("reflection_scores", []).append(reflection_score)
    return reflection_score

def log_schema_drift(project_id: str, drift_type: str, details: dict):
    """
    Log a schema drift event.
    """
    if project_id not in PROJECT_MEMORY:
        initialize_project_memory(project_id)
    
    drift_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": drift_type,
        "details": details
    }
    
    PROJECT_MEMORY[project_id].setdefault("drift_logs", []).append(drift_log)
    return drift_log

def snapshot_loop(project_id: str):
    """
    Take a snapshot of the current loop state.
    """
    if project_id not in PROJECT_MEMORY:
        initialize_project_memory(project_id)
    
    memory = PROJECT_MEMORY[project_id]
    
    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "loop_count": memory.get("loop_count", 0),
        "snapshot": {
            "completed_steps": memory.get("completed_steps", []),
            "planned_steps": memory.get("planned_steps", []),
            "last_reflection": memory.get("last_reflection", {})
        }
    }
    
    PROJECT_MEMORY[project_id].setdefault("loop_snapshots", []).append(snapshot)
    return snapshot
