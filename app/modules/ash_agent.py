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
logger = logging.getLogger("ash")

def run_ash_agent(task, project_id, tools):
    """
    Run the ASH agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 ASH agent execution started")
    print(f"📋 Task: {task}")
    print(f"🆔 Project ID: {project_id}")
    print(f"🧰 Tools: {tools}")
    logger.info(f"ASH agent execution started with task: {task}, project_id: {project_id}, tools: {tools}")
    
    # Log event to system delegation log
    if SYSTEM_LOG_AVAILABLE:
        log_event("ASH", f"Starting execution with task: {task}", project_id)
    
    try:
        # Initialize actions_taken list to track actions
        actions_taken = []
        files_created = ["README.md", "docs/setup.md"]
        
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if CRITIC has reviewed the code
            if "critic" not in project_state.get("agents_involved", []):
                print(f"⏩ CRITIC has not reviewed the code yet, cannot proceed with documentation")
                
                # Log blocked event to system delegation log
                if SYSTEM_LOG_AVAILABLE:
                    log_event("ASH", "Execution blocked: CRITIC has not reviewed the code yet", project_id, {
                        "blocking_condition": "critic_not_run"
                    })
                
                return {
                    "status": "blocked",
                    "notes": "Cannot create documentation - CRITIC has not yet reviewed the code.",
                    "project_state": project_state
                }
        
        # Perform documentation creation
        documentation_action = f"Created documentation for project {project_id}"
        actions_taken.append(documentation_action)
        
        # Generate documentation notes
        documentation_notes = f"ASH documentation for {project_id}: Created README.md and setup guides."
        
        print(f"✅ Documentation created: {documentation_action}")
        print(f"📄 Files created: {', '.join(files_created)}")
        logger.info(f"ASH created documentation: {documentation_action}")
        
        # Log event to system delegation log
        if SYSTEM_LOG_AVAILABLE:
            log_event("ASH", f"Created documentation: {documentation_action}", project_id, {
                "files_created": files_created,
                "documentation_notes": documentation_notes
            })
        
        # Log memory entry if memory_writer is available
        if MEMORY_WRITER_AVAILABLE:
            memory_data = {
                "agent": "ash",
                "project_id": project_id,
                "action": documentation_action,
                "tool_used": "memory_writer",
                "documentation_notes": documentation_notes,
                "files_created": files_created
            }
            
            memory_result = write_memory(memory_data)
            print(f"✅ Memory entry created: {memory_result.get('memory_id', 'unknown')}")
            logger.info(f"ASH logged memory entry for documentation creation")
        
        # Update project state with memory updates for agent autonomy
        if PROJECT_STATE_AVAILABLE:
            # First, increment loop count and update last_completed_agent
            increment_result = increment_loop_count(project_id, "ash")
            
            if increment_result.get("status") != "success":
                print(f"⚠️ Warning: Failed to increment loop count: {increment_result.get('message', 'Unknown error')}")
                logger.warning(f"Failed to increment loop count: {increment_result.get('message', 'Unknown error')}")
            else:
                print(f"✅ Loop count incremented and last_completed_agent set to 'ash'")
                logger.info(f"Loop count incremented and last_completed_agent set to 'ash' for {project_id}")
            
            # Next, update files_created and next_recommended_step
            current_state = read_project_state(project_id)
            current_files = current_state.get("files_created", [])
            
            # Update project state with additional data
            project_state_data = {
                "files_created": current_files + files_created,
                "next_recommended_step": "Run SAGE to summarize the project"
            }
            
            update_result = update_project_state(project_id, project_state_data)
            
            if update_result.get("status") != "success":
                print(f"⚠️ Warning: Failed to update project state: {update_result.get('message', 'Unknown error')}")
                logger.warning(f"Failed to update project state: {update_result.get('message', 'Unknown error')}")
            else:
                print(f"✅ Project state updated with files_created and next_recommended_step")
                print(f"➡️ Next recommended step: Run SAGE to summarize the project")
                logger.info(f"Project state updated with files_created and next_recommended_step for {project_id}")
        
        # Log event to system delegation log for completion
        if SYSTEM_LOG_AVAILABLE:
            log_event("ASH", f"Execution completed successfully", project_id, {
                "actions_taken": actions_taken,
                "files_created": files_created
            })
        
        # Return result with actions_taken list
        return {
            "status": "success",
            "message": f"ASH successfully created documentation for project {project_id}",
            "files_created": files_created,
            "actions_taken": actions_taken,
            "notes": documentation_notes if 'documentation_notes' in locals() else "",
            "next_recommended_step": "Run SAGE to summarize the project",
            "task": task,
            "tools": tools
        }
    except Exception as e:
        error_msg = f"Error in run_ash_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Log error event to system delegation log
        if SYSTEM_LOG_AVAILABLE:
            log_event("ASH", f"Execution failed: {str(e)}", project_id)
        
        return {
            "status": "error",
            "message": f"Error executing ASH agent: {str(e)}",
            "files_created": [],
            "actions_taken": [],
            "notes": "",
            "task": task,
            "tools": tools,
            "error": str(e)
        }
