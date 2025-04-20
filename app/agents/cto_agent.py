from datetime import datetime
from app.memory import PROJECT_MEMORY

def run_cto_agent(project_id: str):
    """
    Core CTO agent function that performs post-loop system audits.
    
    Args:
        project_id (str): The ID of the project to audit
        
    Returns:
        dict: Audit results with issues found
    """
    memory = PROJECT_MEMORY.get(project_id, {})
    loop = memory.get("loop_count", 0)
    reflection = memory.get("last_reflection", {})
    validation = validate_project_memory(project_id, PROJECT_MEMORY)

    issues = {}

    if validation:
        issues["schema_violations"] = validation

    if reflection.get("confidence", 1.0) < 0.5:
        issues["weak_reflection"] = reflection

    if len(memory.get("completed_steps", [])) < 3:
        issues["agent_shortfall"] = memory.get("completed_steps", [])

    result = {
        "loop": loop,
        "timestamp": datetime.utcnow().isoformat(),
        "issues_found": bool(issues),
        "issues": issues,
        "summary": f"CTO audit after loop {loop}: {'issues found' if issues else 'clean'}"
    }

    PROJECT_MEMORY[project_id].setdefault("cto_reflections", []).append(result)

    if issues:
        PROJECT_MEMORY[project_id].setdefault("system_flags", []).append({
            "timestamp": result["timestamp"],
            "level": "warning",
            "origin": "cto",
            "issues": issues
        })
        
    # After single-loop audit, analyze multi-loop trends
    analyze_system_trends(project_id)

    return result

def analyze_system_trends(project_id: str):
    """
    Analyzes system trends across multiple loops to detect systemic issues.
    
    Args:
        project_id (str): The ID of the project to analyze
        
    Returns:
        dict: System health analysis with score and issues
    """
    memory = PROJECT_MEMORY[project_id]
    reflections = memory.get("reflection_scores", [])
    drifts = memory.get("drift_logs", [])
    loops = memory.get("loop_snapshots", [])
    flags = memory.get("system_flags", [])

    score = 1.0
    issues = []

    # Trend: Declining reflection confidence
    if reflections:
        avg_confidence = sum(r["score"] for r in reflections[-5:]) / min(len(reflections), 5)
        if avg_confidence < 0.6:
            score -= 0.3
            issues.append("Reflection quality declining")

    # Trend: Frequent drift logs
    if len(drifts) > 3:
        score -= 0.2
        issues.append("Schema drift frequent")

    # Trend: Agent underuse or loop skips
    recent_loops = loops[-5:] if loops else []
    agent_skip_flags = 0
    for l in recent_loops:
        if len(l.get("snapshot", {}).get("completed_steps", [])) < 3:
            agent_skip_flags += 1
    if agent_skip_flags >= 3:
        score -= 0.2
        issues.append("Agents being skipped frequently")

    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "project_id": project_id,
        "system_health_score": max(0, round(score, 2)),
        "issues": issues,
        "loop_count": memory.get("loop_count", 0)
    }

    PROJECT_MEMORY[project_id]["system_health_score"] = result["system_health_score"]
    PROJECT_MEMORY[project_id].setdefault("cto_audit_history", []).append(result)

    if result["system_health_score"] < 0.5:
        PROJECT_MEMORY[project_id].setdefault("cto_warnings", []).append({
            "timestamp": result["timestamp"],
            "warning": "System trending unhealthy",
            "detail": result
        })

    return result

def validate_project_memory(project_id, project_memory):
    """
    Validates the project memory against schema requirements.
    This is a placeholder for the actual validation logic.
    
    Args:
        project_id (str): The ID of the project
        project_memory (dict): The project memory to validate
        
    Returns:
        list: Validation errors or None if validation passes
    """
    # Placeholder for validation logic
    # In a real implementation, this would check against schema registry
    return None
