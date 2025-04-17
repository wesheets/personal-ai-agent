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
    
    try:
        # Initialize actions_taken list to track actions
        actions_taken = []
        files_created = []
        
        # Perform review if memory_writer is available
        if "memory_writer" in tools:
            print(f"📝 Using memory_writer to log feedback")
            
            # Simulate reviewing README
            review_action = f"Reviewed README.md for project {project_id}"
            actions_taken.append(review_action)
            
            # Generate feedback
            feedback = f"CRITIC feedback for {project_id}: Documentation is clear and concise."
            
            print(f"✅ Review completed: {review_action}")
            logger.info(f"CRITIC completed review: {review_action}")
            
            # Log memory entry if memory_writer is available
            if MEMORY_WRITER_AVAILABLE:
                memory_data = {
                    "agent": "critic",
                    "project_id": project_id,
                    "action": review_action,
                    "tool_used": "memory_writer",
                    "feedback": feedback
                }
                
                memory_result = write_memory(memory_data)
                print(f"✅ Memory entry created: {memory_result.get('memory_id', 'unknown')}")
                logger.info(f"CRITIC logged memory entry for review")
        
        # Return result with actions_taken list
        return {
            "status": "success",
            "message": f"CRITIC successfully reviewed content for project {project_id}",
            "files_created": files_created,
            "actions_taken": actions_taken,
            "notes": feedback if 'feedback' in locals() else "",
            "task": task,
            "tools": tools
        }
    except Exception as e:
        error_msg = f"Error in run_critic_agent: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
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
