# Minimal ASH agent stub
import logging

logger = logging.getLogger("agents.ash")

def run_ash_agent(task: str, project_id: str):
    logger.warning(f"Minimal ASH agent called for task: {task}, project: {project_id}")
    # Return a placeholder response
    return {
        "status": "success",
        "result": f"ASH minimal implementation processed task: {task}",
        "project_id": project_id
    }

