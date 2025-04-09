import logging
from app.core.run import run_agent
from app.agents.memory_agent import handle_memory_task

logger = logging.getLogger("core")

class CoreForge:
    def __init__(self):
        self.agent_id = "core-forge"

    def process_task(self, task):
        """
        Process a task by routing it to the appropriate agent.
        
        Args:
            task (dict): A dictionary containing the task details
                - target_agent (str): The agent to route the task to
                - input (str): The input for the agent
                
        Returns:
            dict: A dictionary containing the task results
        """
        try:
            # Validate task input
            if not isinstance(task, dict):
                error_msg = "Task must be a dictionary"
                logger.error(f"[ERROR] {error_msg}")
                return {
                    "status": "error",
                    "executor": self.agent_id,
                    "error": error_msg,
                    "output": error_msg
                }
            
            # Extract task parameters
            agent = task.get("target_agent", "")
            task_input = task.get("input", "")

            # Validate required fields
            if not agent or not task_input:
                error_msg = "Task missing required fields."
                logger.error(f"[ERROR] {error_msg}")
                return {
                    "status": "error",
                    "executor": self.agent_id,
                    "error": error_msg,
                    "output": error_msg
                }

            # Execute the task
            logger.info(f"[Core.Forge] → Routing task to {agent}: {task_input[:50]}...")
            result = run_agent(agent, task_input)

            # Log the execution with memory integration
            log_message = f"[Core.Forge] → Routed task to {agent}: {task_input}"
            logger.info(log_message)
            print(log_message)
            
            response_log = f"[Core.Forge] ← Response: {result}"
            logger.info(response_log)
            print(response_log)
            
            # Add memory integration
            try:
                memory_entry = f"LOG: Core.Forge executed task → {agent} → Response: {result}"
                handle_memory_task(memory_entry)
            except Exception as mem_error:
                logger.error(f"[ERROR] Failed to log to memory: {str(mem_error)}")

            # Return successful result
            return {
                "status": "complete",
                "executor": self.agent_id,
                "routed_to": agent,
                "input": task_input,
                "output": result
            }
            
        except Exception as e:
            # Handle any unexpected errors
            error_msg = f"Error processing task: {str(e)}"
            logger.error(f"[ERROR] {error_msg}")
            
            return {
                "status": "error",
                "executor": self.agent_id,
                "error": str(e),
                "output": f"Core.Forge encountered an error: {str(e)}"
            }
