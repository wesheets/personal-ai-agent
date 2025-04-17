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
        files_created = []
        
        # Perform deployment simulation if memory_writer is available
        if "memory_writer" in tools:
            print(f"📝 Using memory_writer to log deployment simulation")
            
            # Simulate deployment
            deployment_action = f"Simulated deployment for project {project_id}"
            actions_taken.append(deployment_action)
            
            # Generate deployment notes
            deployment_notes = f"ASH deployment simulation for {project_id}: Successfully deployed to staging environment."
            
            print(f"✅ Deployment simulation completed: {deployment_action}")
            logger.info(f"ASH completed deployment simulation: {deployment_action}")
            
            # Log event to system delegation log
            if SYSTEM_LOG_AVAILABLE:
                log_event("ASH", f"Completed deployment: {deployment_action}", project_id, {
                    "deployment_notes": deployment_notes
                })
            
            # Log memory entry if memory_writer is available
            if MEMORY_WRITER_AVAILABLE:
                memory_data = {
                    "agent": "ash",
                    "project_id": project_id,
                    "action": deployment_action,
                    "tool_used": "memory_writer",
                    "deployment_notes": deployment_notes
                }
                
                memory_result = write_memory(memory_data)
                print(f"✅ Memory entry created: {memory_result.get('memory_id', 'unknown')}")
                logger.info(f"ASH logged memory entry for deployment simulation")
        
        # Log event to system delegation log for completion
        if SYSTEM_LOG_AVAILABLE:
            log_event("ASH", f"Execution completed successfully", project_id, {
                "actions_taken": actions_taken,
                "files_created": files_created
            })
        
        # Return result with actions_taken list
        return {
            "status": "success",
            "message": f"ASH successfully simulated deployment for project {project_id}",
            "files_created": files_created,
            "actions_taken": actions_taken,
            "notes": deployment_notes if 'deployment_notes' in locals() else "",
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
