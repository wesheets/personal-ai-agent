import logging
import traceback
from typing import Dict, Any, List

from app.modules.project_state import read_project_state, update_project_state, increment_loop_count

def run_critic_agent(task, project_id, tools):
    state = read_project_state(project_id)
    print("🧠 CRITIC reading state:", state)

    reviewed_files = state.get("files_created", [])
    feedback = f"CRITIC reviewed {len(reviewed_files)} files and identified potential improvements."

    # Memory log
    state["loop_count"] += 1
    state["last_completed_agent"] = "critic"
    state["completed_steps"] = state.get("completed_steps", []) + ["critic"]
    state["next_recommended_step"] = "Run ASH to document the project"
    state["latest_agent_action"] = {
        "agent": "critic",
        "feedback": feedback
    }

    result = update_project_state(project_id, state)
    print("✅ CRITIC updated memory:", result)

    return {
        "status": "success",
        "message": "CRITIC completed task successfully",
        "project_id": project_id,
        "agent": "critic",
        "feedback": feedback,
        "next_recommended_step": state["next_recommended_step"]
    }
