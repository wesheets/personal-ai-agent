import logging
import traceback
from typing import Dict, Any, List

from app.modules.project_state import read_project_state, update_project_state, increment_loop_count

def run_critic_agent(task, project_id, tools):
    state = read_project_state(project_id)
    print("🧠 CRITIC reading state:", state)

    # Mock a review of frontend files
    frontend_files = ["LoginForm.jsx", "Dashboard.jsx"]
    reviewed_files = state.get("files_created", [])
    
    # Generate feedback for each file
    feedback_log = []
    for file in frontend_files:
        if file == "LoginForm.jsx":
            feedback_log.append({
                "file": file,
                "feedback": "Form validation is well implemented. Consider adding password strength indicator."
            })
        elif file == "Dashboard.jsx":
            feedback_log.append({
                "file": file,
                "feedback": "Layout is clean. Recommend adding loading states for data fetching."
            })
    
    # Generate summary feedback
    feedback = f"CRITIC reviewed {len(frontend_files)} UI components and identified potential improvements."

    # Memory log
    state["loop_count"] += 1
    state["last_completed_agent"] = "critic"
    state["completed_steps"] = state.get("completed_steps", []) + ["critic"]
    state["next_recommended_step"] = "ash"
    state["latest_agent_action"] = {
        "agent": "critic",
        "feedback": feedback
    }
    # Add feedback log to state
    state["feedback_log"] = feedback_log

    result = update_project_state(project_id, state)
    print("✅ CRITIC updated memory:", result)

    return {
        "status": "success",
        "message": "CRITIC completed task successfully",
        "project_id": project_id,
        "agent": "critic",
        "feedback": feedback,
        "feedback_log": feedback_log,
        "next_recommended_step": state["next_recommended_step"]
    }
