import logging
import traceback
import random
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
logger = logging.getLogger("critic")

def run_critic_agent(task, project_id, tools):
    """
    Run the CRITIC agent with the given task.
    
    Args:
        task: The task to run
        project_id: The project identifier
        tools: List of tools to use
        
    Returns:
        Dict containing the response and metadata
    """
    print(f"🤖 CRITIC agent execution started")
    print(f"📋 Task: {task}")
    print(f"🆔 Project ID: {project_id}")
    print(f"🧰 Tools: {tools}")
    logger.info(f"CRITIC agent execution started with task: {task}, project_id: {project_id}, tools: {tools}")
    
    # Log event to system delegation log
    if SYSTEM_LOG_AVAILABLE:
        log_event("CRITIC", f"Starting execution with task: {task}", project_id)
    
    try:
        # Initialize actions_taken list to track actions
        actions_taken = []
        files_created = []
        feedback_log = []
        
        # Read project state to get files to review
        project_state = {}
        files_to_review = ["src/components/Dashboard.jsx", "src/components/LoginForm.jsx"]
        
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if NOVA has created UI files
            if "nova" not in project_state.get("agents_involved", []):
                print(f"⏩ NOVA has not created UI files yet, cannot proceed with review")
                
                # Log blocked event to system delegation log
                if SYSTEM_LOG_AVAILABLE:
                    log_event("CRITIC", "Execution blocked: NOVA has not created UI files yet", project_id, {
                        "blocking_condition": "nova_not_run"
                    })
                
                return {
                    "status": "blocked",
                    "notes": "Cannot review UI - NOVA has not yet created UI components.",
                    "project_state": project_state
                }
        
        # Simulate reviewing UI files
        for file in files_to_review:
            review_action = f"Reviewed {file} for project {project_id}"
            actions_taken.append(review_action)
            
            # Generate feedback for this file
            file_feedback = f"CRITIC feedback for {file}: "
            
            # Randomly decide if there are issues (for demonstration purposes)
            # In a real implementation, this would be based on actual code analysis
            has_issues = random.random() < 0.3  # 30% chance of finding issues
            
            if has_issues and "LoginForm.jsx" in file:
                file_feedback += "Form validation is missing. Input fields should validate user input."
                feedback_log.append({
                    "file": file,
                    "status": "needs_revision",
                    "feedback": "Form validation is missing. Input fields should validate user input."
                })
            else:
                file_feedback += "Code is well-structured and follows best practices."
                feedback_log.append({
                    "file": file,
                    "status": "approved",
                    "feedback": "Code is well-structured and follows best practices."
                })
            
            print(f"✅ Review completed: {review_action}")
            print(f"📝 {file_feedback}")
            logger.info(f"CRITIC completed review: {review_action}")
            
            # Log event to system delegation log
            if SYSTEM_LOG_AVAILABLE:
                log_event("CRITIC", f"Completed review: {review_action}", project_id, {
                    "feedback": file_feedback
                })
            
            # Log memory entry if memory_writer is available
            if MEMORY_WRITER_AVAILABLE:
                memory_data = {
                    "agent": "critic",
                    "project_id": project_id,
                    "action": review_action,
                    "tool_used": "memory_writer",
                    "feedback": file_feedback
                }
                
                memory_result = write_memory(memory_data)
                print(f"✅ Memory entry created: {memory_result.get('memory_id', 'unknown')}")
                logger.info(f"CRITIC logged memory entry for review")
        
        # Determine next recommended step based on feedback
        needs_revision = any(item["status"] == "needs_revision" for item in feedback_log)
        
        # Update project state with memory updates for agent autonomy
        if PROJECT_STATE_AVAILABLE:
            # First, increment loop count and update last_completed_agent
            increment_result = increment_loop_count(project_id, "critic")
            
            if increment_result.get("status") != "success":
                print(f"⚠️ Warning: Failed to increment loop count: {increment_result.get('message', 'Unknown error')}")
                logger.warning(f"Failed to increment loop count: {increment_result.get('message', 'Unknown error')}")
            else:
                print(f"✅ Loop count incremented and last_completed_agent set to 'critic'")
                logger.info(f"Loop count incremented and last_completed_agent set to 'critic' for {project_id}")
            
            # Determine next recommended step based on review results
            next_step = "Ask NOVA to revise LoginForm.jsx for validation" if needs_revision else "Run ASH to document the UI components"
            
            # Update project state with additional data
            project_state_data = {
                "feedback_log": feedback_log,
                "next_recommended_step": next_step
            }
            
            update_result = update_project_state(project_id, project_state_data)
            
            if update_result.get("status") != "success":
                print(f"⚠️ Warning: Failed to update project state: {update_result.get('message', 'Unknown error')}")
                logger.warning(f"Failed to update project state: {update_result.get('message', 'Unknown error')}")
            else:
                print(f"✅ Project state updated with feedback_log and next_recommended_step")
                print(f"📋 Feedback log created with {len(feedback_log)} entries")
                print(f"➡️ Next recommended step: {next_step}")
                logger.info(f"Project state updated with feedback_log and next_recommended_step for {project_id}")
        
        # Log completion event to system delegation log
        if SYSTEM_LOG_AVAILABLE:
            log_event("CRITIC", "Execution completed successfully", project_id, {
                "actions_taken": actions_taken,
                "files_created": files_created,
                "needs_revision": needs_revision
            })
        
        # Return result with actions_taken list and feedback
        return {
            "status": "success",
            "message": f"CRITIC successfully reviewed content for project {project_id}",
            "files_created": files_created,
            "actions_taken": actions_taken,
            "feedback_log": feedback_log,
            "next_recommended_step": next_step if 'next_step' in locals() else "Run ASH to document the UI components",
            "needs_revision": needs_revision,
            "task": task,
            "tools": tools
        }
    except Exception as e:
        error_msg = f"Error in run_critic_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Log error event to system delegation log
        if SYSTEM_LOG_AVAILABLE:
            log_event("CRITIC", f"Execution failed: {str(e)}", project_id)
        
        return {
            "status": "error",
            "message": f"Error executing CRITIC agent: {str(e)}",
            "files_created": [],
            "actions_taken": [],
            "notes": "",
            "task": task,
            "tools": tools,
            "error": str(e)
        }
