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
            # Call increment_loop_count and log the result
            print("🔄 Calling increment_loop_count...")
            increment_result = increment_loop_count(project_id, "nova")
            if increment_result.get("status") == "success":
                print("✅ Loop count incremented and agent updated")
                print(f"✅ increment_loop_count result: {increment_result}")
            else:
                print(f"❌ Failed to increment loop count: {increment_result.get('message')}")
                logger.error(f"Failed to increment loop count: {increment_result}")

            # Read the current state after increment
            print("🔄 Reading state after increment_loop_count...")
            state = read_project_state(project_id)
            print(f"📊 Current state after increment: loop_count={state.get('loop_count')}, last_agent={state.get('last_completed_agent')}")
            print(f"📊 Current completed_steps: {state.get('completed_steps', [])}")

            # Update these fields in memory
            print("🔄 Updating state in memory...")
            state["files_created"] = state.get("files_created", []) + ui_files_created
            state["loop_count"] = state.get("loop_count", 0) + 1  # Ensure loop_count is incremented
            state["last_completed_agent"] = "nova"
            
            # Ensure completed_steps exists and contains nova
            completed_steps = state.get("completed_steps", [])
            if "nova" not in completed_steps:
                completed_steps.append("nova")
            state["completed_steps"] = completed_steps
            
            state["next_recommended_step"] = "Run CRITIC to review NOVA's UI output"
            
            print(f"📊 Updated memory state: loop_count={state.get('loop_count')}, last_agent={state.get('last_completed_agent')}")
            print(f"📊 Updated completed_steps: {state.get('completed_steps')}")
            print(f"📊 Updated files_created: {state.get('files_created')}")
            
            # Update the project state with the modified state
            print("🔄 Calling update_project_state to persist changes...")
            update_result = update_project_state(project_id, state)
            if update_result.get("status") == "success":
                print(f"✅ Project state updated — files: {ui_files_created}")
                print(f"✅ Memory state updated: loop_count={state.get('loop_count')}, last_agent={state.get('last_completed_agent')}")
                print(f"✅ update_project_state result: {update_result}")
                print("➡️ Next: Run CRITIC to review NOVA's UI output")
            else:
                print(f"❌ Failed to update project state: {update_result.get('message')}")
                logger.error(f"Failed to update project state: {update_result}")
            
            # Verify state was persisted by reading it again
            print("🔄 Verifying state persistence by reading state again...")
            final_state = read_project_state(project_id)
            print(f"📊 Final state verification: loop_count={final_state.get('loop_count')}, last_agent={final_state.get('last_completed_agent')}")
            print(f"📊 Final completed_steps: {final_state.get('completed_steps')}")
            print(f"📊 Final files_created: {final_state.get('files_created')}")

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
