import logging
import traceback
from typing import Dict, Any, List

from app.modules.project_state import read_project_state, update_project_state, increment_loop_count

def run_ash_agent(task, project_id, tools):
    state = read_project_state(project_id)
    print("🧠 ASH reading state:", state)

    # Read project state to see what files were reviewed
    reviewed_files = []
    if "feedback_log" in state:
        for feedback_item in state.get("feedback_log", []):
            reviewed_files.append(feedback_item.get("file"))
    
    # Generate mock documentation notes
    documentation_notes = []
    for file in reviewed_files:
        if file == "LoginForm.jsx":
            documentation_notes.append({
                "file": file,
                "documentation": "The LoginForm component handles user authentication with email and password validation."
            })
        elif file == "Dashboard.jsx":
            documentation_notes.append({
                "file": file,
                "documentation": "The Dashboard component displays user statistics and activity in a responsive grid layout."
            })
    
    # If no files were reviewed, create generic documentation
    if not documentation_notes:
        documentation_notes = [
            {
                "file": "LoginForm.jsx",
                "documentation": "Component for user authentication with form validation."
            },
            {
                "file": "Dashboard.jsx",
                "documentation": "Main dashboard interface with data visualization components."
            }
        ]
    
    # Generate summary documentation
    docs_summary = f"Documented {len(documentation_notes)} UI components with usage instructions and API references."

    # Memory log
    state["loop_count"] += 1
    state["last_completed_agent"] = "ash"
    state["completed_steps"] = state.get("completed_steps", []) + ["ash"]
    state["next_recommended_step"] = "sage"
    state["latest_agent_action"] = {
        "agent": "ash",
        "documentation": docs_summary
    }
    # Store documentation in state
    state["documentation_log"] = documentation_notes

    result = update_project_state(project_id, state)
    print("✅ ASH updated memory:", result)

    return {
        "status": "success",
        "message": "ASH completed task successfully",
        "project_id": project_id,
        "agent": "ash",
        "documentation": docs_summary,
        "documentation_log": documentation_notes,
        "next_recommended_step": state["next_recommended_step"]
    }
