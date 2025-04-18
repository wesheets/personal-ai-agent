import logging
import traceback
from typing import Dict, List, Any

# Import memory_writer for logging agent actions
try:
    from app.modules.memory_writer import write_memory
    MEMORY_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_WRITER_AVAILABLE = False
    print("❌ memory_writer import failed")

# Import project_state for tracking project status
try:
    from app.modules.project_state import update_project_state, read_project_state, increment_loop_count
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ project_state import failed")

# Import system log module
try:
    from memory.system_log import log_event
    SYSTEM_LOG_AVAILABLE = True
except ImportError:
    SYSTEM_LOG_AVAILABLE = False
    print("❌ system_log import failed")

# Configure logging
logger = logging.getLogger("nova")

def run_nova_agent(task, project_id, tools):
    """
    Run the NOVA agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 NOVA agent execution started")
    print(f"📋 Task: {task}")
    print(f"🆔 Project ID: {project_id}")
    print(f"🧰 Tools: {tools}")
    logger.info(f"NOVA agent execution started with task: {task}, project_id: {project_id}, tools: {tools}")
    
    if SYSTEM_LOG_AVAILABLE:
        log_event("NOVA", f"Starting execution with task: {task}", project_id)
    
    try:
        # Read current project state - avoid generating a default object, use what's already written by HAL
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            print(f"📊 Initial state: loop_count={project_state.get('loop_count')}, last_agent={project_state.get('last_completed_agent')}")
            print(f"📊 Initial completed_steps: {project_state.get('completed_steps', [])}")
            print(f"📊 Initial files_created: {project_state.get('files_created', [])}")
            
            if "hal" not in project_state.get("agents_involved", []):
                print("⏩ HAL has not created initial files yet, cannot proceed")
                if SYSTEM_LOG_AVAILABLE:
                    log_event("NOVA", "Blocked: HAL has not yet run", project_id, {"blocking_condition": "hal_not_run"})
                return {
                    "status": "blocked",
                    "notes": "Cannot proceed — HAL has not yet initialized the project.",
                    "project_state": project_state
                }

        # Simulate UI file generation
        design_action = f"Created core UI components for {project_id}"
        ui_files_created = [
            "src/components/Dashboard.jsx",
            "src/components/LoginForm.jsx"
        ]

        if SYSTEM_LOG_AVAILABLE:
            log_event("NOVA", f"Design action: {design_action}", project_id)

        if MEMORY_WRITER_AVAILABLE:
            memory_data = {
                "agent": "nova",
                "project_id": project_id,
                "action": design_action,
                "tool_used": "memory_writer",
                "design_notes": "NOVA designed the core UI structure for the app."
            }
            write_memory(memory_data)
            print("✅ Memory logged for NOVA UI generation")

        if PROJECT_STATE_AVAILABLE:
            # 1. Increment loop count
            increment_result = increment_loop_count(project_id, "nova")
            if increment_result.get("status") == "success":
                print("✅ Loop count incremented and agent set to nova")
            else:
                print(f"❌ Loop count increment failed: {increment_result}")

            # 2. Read current memory
            state = read_project_state(project_id)
            print("📥 Current project state (before update):", state)

            # 3. Merge UI files and update keys
            ui_files_created = [
                "src/components/Dashboard.jsx",
                "src/components/LoginForm.jsx"
            ]

            state["files_created"] = state.get("files_created", []) + ui_files_created
            state["completed_steps"] = state.get("completed_steps", []) + ["nova"]
            state["last_completed_agent"] = "nova"
            state["next_recommended_step"] = "Run CRITIC to review NOVA's UI output"

            # 4. Write memory
            update_result = update_project_state(project_id, state)

            if update_result.get("status") != "success":
                print("❌ Failed to persist NOVA update:", update_result)
            else:
                print("✅ NOVA memory successfully persisted")
                print("📤 Files created:", ui_files_created)
                print("➡️ Next step:", state["next_recommended_step"])

            # 5. Double-check final state
            new_state = read_project_state(project_id)
            print("🧠 Final memory snapshot:", new_state)

        if SYSTEM_LOG_AVAILABLE:
            log_event("NOVA", "Execution complete", project_id, {
                "files_created": ui_files_created
            })

        return {
            "status": "success",
            "message": f"NOVA completed task for {project_id}",
            "files_created": ui_files_created,
            "next_recommended_step": "Run CRITIC to review NOVA's UI output",
            "project_state": project_state
        }

    except Exception as e:
        error_msg = f"Error in run_nova_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        if SYSTEM_LOG_AVAILABLE:
            log_event("NOVA", f"Error: {str(e)}", project_id)

        return {
            "status": "error",
            "message": f"Execution failed for NOVA agent: {str(e)}",
            "project_state": project_state if 'project_state' in locals() else {}
        }
