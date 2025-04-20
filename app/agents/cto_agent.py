from datetime import datetime
from app.schema_registry import SCHEMA_REGISTRY
from app.utils.schema_utils import validate_project_memory
from app.memory import PROJECT_MEMORY

def run_cto_agent(project_id: str):
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

    return result
