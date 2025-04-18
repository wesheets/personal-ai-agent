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
    
    # Log event to system delegation log
    if SYSTEM_LOG_AVAILABLE:
        log_event("NOVA", f"Starting execution with task: {task}", project_id)
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if HAL has created initial files
            if "hal" not in project_state.get("agents_involved", []):
                print(f"⏩ HAL has not created initial files yet, cannot proceed")
                
                # Log blocked event to system delegation log
                if SYSTEM_LOG_AVAILABLE:
                    log_event("NOVA", "Execution blocked: HAL has not created initial files yet", project_id, {
                        "blocking_condition": "hal_not_run"
                    })
                
                return {
                    "status": "blocked",
                    "notes": "Cannot create UI - HAL has not yet created initial project files.",
                    "project_state": project_state
                }
        
        # Simulate NOVA execution
        design_action = f"Designed project architecture for {project_id}"
        
        # Log design action to system delegation log
        if SYSTEM_LOG_AVAILABLE:
            log_event("NOVA", f"Performing action: {design_action}", project_id)
        
        # Log memory entry if memory_writer is available
        if MEMORY_WRITER_AVAILABLE:
            memory_data = {
                "agent": "nova",
                "project_id": project_id,
                "action": design_action,
                "tool_used": "memory_writer",
                "design_notes": f"NOVA design for {project_id}: Created architecture blueprint."
            }
            
            write_memory(memory_data)
            print(f"✅ Memory entry created for design action")
            logger.info(f"NOVA logged memory entry for design action")
        
        # Define UI files created by NOVA
        ui_files_created = [
            "src/components/Dashboard.jsx",
            "src/components/LoginForm.jsx"
        ]
        
        # Update project state with memory updates for agent autonomy
        if PROJECT_STATE_AVAILABLE:
            # First, increment loop count and update last_completed_agent
            increment_result = increment_loop_count(project_id, "nova")
            
            if increment_result.get("status") != "success":
                print(f"⚠️ Warning: Failed to increment loop count: {increment_result.get('message', 'Unknown error')}")
                logger.warning(f"Failed to increment loop count: {increment_result.get('message', 'Unknown error')}")
            else:
                print(f"✅ Loop count incremented and last_completed_agent set to 'nova'")
                logger.info(f"Loop count incremented and last_completed_agent set to 'nova' for {project_id}")
            
            # Next, update files_created and next_recommended_step
            current_state = read_project_state(project_id)
            current_files = current_state.get("files_created", [])
            
            # Update project state with additional data
            project_state_data = {
                "agents_involved": ["nova"],
                "latest_agent_action": {
                    "agent": "nova",
                    "action": design_action
                },
                "files_created": current_files + ui_files_created,
                "next_recommended_step": "Run CRITIC to review NOVA's UI output",
                "tool_usage": {}
            }
            
            update_result = update_project_state(project_id, project_state_data)
            
            if update_result.get("status") != "success":
                print(f"⚠️ Warning: Failed to update project state: {update_result.get('message', 'Unknown error')}")
                logger.warning(f"Failed to update project state: {update_result.get('message', 'Unknown error')}")
            else:
                print(f"✅ Project state updated with files_created and next_recommended_step")
                print(f"📋 Files created: {ui_files_created}")
                print(f"➡️ Next recommended step: Run CRITIC to review NOVA's UI output")
                logger.info(f"Project state updated with files_created and next_recommended_step for {project_id}")
        
        # Log completion event to system delegation log
        if SYSTEM_LOG_AVAILABLE:
            log_event("NOVA", "Execution completed successfully", project_id, {
                "design_action": design_action,
                "files_created": ui_files_created
            })
        
        return {
            "status": "success",
            "message": f"NOVA successfully designed project {project_id}",
            "task": task,
            "tools": tools,
            "files_created": ui_files_created,
            "next_recommended_step": "Run CRITIC to review NOVA's UI output",
            "project_state": project_state
        }
    except Exception as e:
        error_msg = f"Error in run_nova_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Log error event to system delegation log
        if SYSTEM_LOG_AVAILABLE:
            log_event("NOVA", f"Execution failed: {str(e)}", project_id)
        
        return {
            "status": "error",
            "message": f"Error executing NOVA agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }
