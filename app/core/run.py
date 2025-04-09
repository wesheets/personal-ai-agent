import logging

from app.agents.hal_agent import handle_hal_task
from app.agents.ash_agent import handle_ash_task
from app.agents.ops_agent import handle_ops_task
from app.agents.memory_agent import handle_memory_task
from app.agents.lifetree_agent import handle_lifetree_task
from app.agents.sitegen_agent import handle_sitegen_task
from app.agents.neureal_agent import handle_neureal_task
from app.agents.observer_agent import handle_observer_task
from app.agents.trainer_agent import handle_trainer_task
from app.core.error_logger import log_agent_error

logger = logging.getLogger("core")

AGENT_HANDLERS = {
    "hal": handle_hal_task,
    "ash": handle_ash_task,
    "ops-agent": handle_ops_task,
    "memory-agent": handle_memory_task,
    "lifetree": handle_lifetree_task,
    "sitegen": handle_sitegen_task,
    "neureal": handle_neureal_task,
    "observer": handle_observer_task,
    "trainer": handle_trainer_task
}

def run_agent(agent_id, task_input, debug=False, **kwargs):
    """
    Run an agent with the given task input.
    
    Args:
        agent_id (str): The ID of the agent to run
        task_input (str): The input to pass to the agent
        debug (bool): Whether to run in debug mode
        **kwargs: Additional parameters to pass to the agent
        
    Returns:
        str: The agent's response or an error message
    """
    try:
        # Check if agent exists
        if agent_id not in AGENT_HANDLERS:
            error_msg = f"Unknown agent: {agent_id}"
            logger.error(f"[ERROR] {error_msg}")
            # Log the error to memory
            log_agent_error("Core.run", error_msg)
            return error_msg
            
        # Get the handler function
        handler = AGENT_HANDLERS[agent_id]
        
        # Check if handler is callable
        if not callable(handler):
            error_msg = f"Agent handler for {agent_id} is not callable"
            logger.error(f"[ERROR] {error_msg}")
            # Log the error to memory
            log_agent_error("Core.run", error_msg)
            return error_msg
            
        # Call the handler
        logger.info(f"Running agent: {agent_id} with input: {task_input[:50]}...")
        if debug:
            logger.info(f"[DEBUG MODE] Agent {agent_id} running in debug mode")
            
        result = handler(task_input)
        
        # Check if result is valid
        if result is None:
            error_msg = f"Agent {agent_id} returned None"
            logger.error(f"[ERROR] {error_msg}")
            # Log the error to memory
            log_agent_error(agent_id, error_msg)
            return f"Error: Agent {agent_id} produced no output"
        
        # Add debug mode prefix if debug is enabled
        if debug:
            result = f"[DEBUG MODE] {result}"
            
        return result
        
    except ImportError as e:
        error_msg = f"Failed to import agent {agent_id}: {str(e)}"
        logger.error(f"[ERROR] {error_msg}")
        # Log the error to memory with the exception object
        log_agent_error(agent_id, error_msg, e)
        return f"Error: {error_msg}"
        
    except Exception as e:
        error_msg = f"Error running agent {agent_id}: {str(e)}"
        logger.error(f"[ERROR] {error_msg}")
        # Log the error to memory with the exception object
        log_agent_error(agent_id, error_msg, e)
        return f"Error: Agent {agent_id} encountered an error: {str(e)}"
