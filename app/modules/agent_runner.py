# agent_runner.py
"""
AgentRunner Module

Provides functionality to dynamically load and execute agents using the AgentRegistry.
"""

import logging
import uuid
import asyncio
import traceback
from typing import Any

from app.core.agent_registry import agent_registry
from app.schemas.core.agent_result import BaseAgentResult, ResultStatus
from app.schemas.core.task_payload import BaseTaskPayload

# Configure logging
logger = logging.getLogger(__name__)

# --- Removed direct agent imports and AGENT_RUNNERS dictionary --- 

# --- Keep necessary helper functions if needed, review later --- 
# Example: safe_add_memory_thread might be refactored or moved to BaseAgent
# For now, keep it if other parts of the system rely on it directly.

# Import memory thread module (assuming it's still needed externally)
try:
    from app.modules.memory_thread import add_memory_thread
    MEMORY_THREAD_AVAILABLE = True
except ImportError:
    MEMORY_THREAD_AVAILABLE = False
    logger.warning("❌ memory_thread module import failed")
    # Define a fallback if necessary
    def add_memory_thread(*args, **kwargs):
        logger.error("add_memory_thread called but module is unavailable.")
        return {"status": "error", "message": "Memory thread module unavailable"}

def safe_add_memory_thread(*args, **kwargs):
    """
    Safe wrapper for add_memory_thread that ensures correct parameter format.
    (Keep this function if external calls to agent_runner might use it,
     otherwise, prefer memory logging via BaseAgent methods)
    """
    try:
        if not MEMORY_THREAD_AVAILABLE:
             raise ImportError("memory_thread module is not available")
             
        # Check if first argument is already a dictionary (correct usage)
        if len(args) == 1 and isinstance(args[0], dict):
            memory_entry = args[0]
        elif len(args) > 0 and isinstance(args[0], str): # Assuming positional args if first is string
             memory_entry = {
                "project_id": args[0] if len(args) > 0 else kwargs.get("project_id", "unknown"),
                "chain_id": args[1] if len(args) > 1 else kwargs.get("chain_id", "main"),
                "agent": args[2] if len(args) > 2 else kwargs.get("agent", "unknown"),
                "role": args[3] if len(args) > 3 else kwargs.get("role", "system"),
                "content": args[4] if len(args) > 4 else kwargs.get("content", ""),
                "step_type": args[5] if len(args) > 5 else kwargs.get("step_type", "log")
            }
             memory_entry.update(kwargs)
        else: # Assume keyword args only
            memory_entry = {
                "project_id": kwargs.get("project_id", "unknown"),
                "chain_id": kwargs.get("chain_id", "main"),
                "agent": kwargs.get("agent", "unknown"),
                "role": kwargs.get("role", "system"),
                "content": kwargs.get("content", ""),
                "step_type": kwargs.get("step_type", "log")
            }
            memory_entry.update(kwargs)
            
        logger.debug(f"Calling add_memory_thread with: {memory_entry}")
        return add_memory_thread(memory_entry)
    except Exception as e:
        logger.error(f"❌ Error in safe_add_memory_thread: {str(e)}\n{traceback.format_exc()}")
        return {"status": "error", "message": f"Error in safe_add_memory_thread: {str(e)}"}

# --- End Helper Functions --- 

async def run_agent(agent_key: str, payload: BaseTaskPayload) -> BaseAgentResult:
    """
    Dynamically loads and executes the specified agent using the AgentRegistry.

    Args:
        agent_key: The registry key of the agent to run.
        payload: The input payload for the agent, conforming to BaseTaskPayload.

    Returns:
        The result from the agent execution, conforming to BaseAgentResult.
    """
    if not payload.task_id:
        payload.task_id = f"task_{uuid.uuid4()}"
        logger.warning(f"Task payload missing task_id, generated: {payload.task_id}")

    logger.info(f"Attempting to run agent 
{agent_key}
 for task {payload.task_id}")

    try:
        # Get agent instance from the registry
        agent_instance = agent_registry.get_agent_instance(agent_key)

        if agent_instance is None:
            logger.error(f"Agent with key 
{agent_key}
 not found in registry.")
            return BaseAgentResult(
                task_id=payload.task_id,
                status=ResultStatus.ERROR,
                details=f"Agent 
{agent_key}
 not found."
            )

        # Validate payload against agent's input schema (Pydantic handles this on method call)
        # logger.debug(f"Payload for {agent_key}: {payload.dict()}")

        # Execute the agent's run method
        result: BaseAgentResult = await agent_instance.run(payload)

        # Optional: Validate result against agent's output schema
        if not isinstance(result, agent_instance.output_schema):
             logger.warning(f"Agent {agent_key} returned result of type {type(result).__name__}, expected {agent_instance.output_schema.__name__}. Attempting conversion.")
             try:
                 # Try to cast/validate
                 result = agent_instance.output_schema(**result.dict())
             except Exception as validation_error:
                  logger.error(f"Failed to validate/convert result from {agent_key} to {agent_instance.output_schema.__name__}: {validation_error}")
                  # Keep original result but log error

        logger.info(f"Agent {agent_key} completed task {payload.task_id} with status: {result.status}")
        return result

    except Exception as e:
        logger.error(f"Error during execution of agent {agent_key} for task {payload.task_id}: {e}", exc_info=True)
        return BaseAgentResult(
            task_id=payload.task_id,
            status=ResultStatus.ERROR,
            details=f"An unexpected error occurred while running agent {agent_key}: {str(e)}"
        )

# Example usage (for testing purposes, remove in production):
# async def main():
#     from app.schemas.agents.orchestrator.orchestrator_schemas import OrchestratorInstruction
#     # Need to ensure agents are imported somewhere to trigger registration
#     import app.agents.orchestrator_agent 
#     
#     test_payload = OrchestratorInstruction(
#         operator_input="Plan a simple website",
#         operator_persona="medium",
#         project_id="test_project_123"
#     )
#     result = await run_agent("orchestrator", test_payload)
#     print(result)
# 
# if __name__ == "__main__":
#     asyncio.run(main())

