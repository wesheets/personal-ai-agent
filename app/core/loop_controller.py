import logging
import uuid
from enum import Enum
from typing import Dict, Any, Optional, List

from app.core.agent_registry import agent_registry
from app.modules import agent_runner # Assuming agent_runner module exists
from app.schemas.core.agent_result import BaseAgentResult, ResultStatus
from app.schemas.core.task_payload import BaseTaskPayload

logger = logging.getLogger(__name__)

class LoopState(Enum):
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    REFLECTING = "REFLECTING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"

class LoopController:
    """Manages the execution flow (loop) between different agents."""

    def __init__(self):
        self.current_loop_id: Optional[str] = None
        self.current_state: LoopState = LoopState.IDLE
        self.history: List[Dict[str, Any]] = []
        # Basic workflow definition (can be made more dynamic)
        self.workflow: Dict[str, Optional[str]] = {
            "orchestrator": "hal", # Default next step after planning
            "hal": "critic",
            "forge": "critic",
            "nova": "critic",
            "critic": "sage",
            "sage": None # End of loop after reflection
        }

    async def start_loop(self, initial_payload: BaseTaskPayload) -> BaseAgentResult:
        """Starts a new execution loop."""
        self.current_loop_id = f"loop_{uuid.uuid4()}"
        self.current_state = LoopState.PLANNING
        self.history = []
        logger.info(f"Starting new loop: {self.current_loop_id}")

        # Assume the first task always goes to the orchestrator
        initial_agent_key = "orchestrator"
        initial_payload.loop_id = self.current_loop_id # Add loop_id to payload
        
        return await self._run_step(initial_agent_key, initial_payload)

    async def _run_step(self, agent_key: str, payload: BaseTaskPayload) -> BaseAgentResult:
        """Runs a single step in the loop by invoking an agent."""
        self.history.append({"agent": agent_key, "payload": payload.dict()})
        logger.info(f"Loop {self.current_loop_id}: Running agent 
{agent_key}
 with task {payload.task_id}")

        try:
            # Use agent_runner to execute the agent
            result: BaseAgentResult = await agent_runner.run_agent(agent_key, payload)
            self.history[-1]["result"] = result.dict()
            logger.info(f"Loop {self.current_loop_id}: Agent {agent_key} finished with status {result.status}")

            return await self._handle_result(agent_key, result)

        except Exception as e:
            logger.error(f"Loop {self.current_loop_id}: Error running agent {agent_key}: {e}", exc_info=True)
            self.current_state = LoopState.ERROR
            # Create a generic error result
            error_result = BaseAgentResult(
                task_id=payload.task_id,
                status=ResultStatus.ERROR,
                details=f"LoopController error running {agent_key}: {e}"
            )
            self.history[-1]["result"] = error_result.dict()
            return error_result

    async def _handle_result(self, current_agent_key: str, result: BaseAgentResult) -> BaseAgentResult:
        """Handles the result from an agent and determines the next step."""
        if result.status == ResultStatus.ERROR:
            self.current_state = LoopState.ERROR
            logger.error(f"Loop {self.current_loop_id}: Agent {current_agent_key} reported error: {result.details}")
            # Potentially trigger error handling agent or stop
            return result
        
        elif result.status == ResultStatus.DELEGATED:
            next_agent_key = result.delegated_to
            next_payload = result.next_task_payload

            if not next_agent_key or not next_payload:
                logger.error(f"Loop {self.current_loop_id}: Agent {current_agent_key} delegated but missing next agent key or payload.")
                self.current_state = LoopState.ERROR
                result.status = ResultStatus.ERROR
                result.details = "Delegation failed: Missing next agent key or payload."
                return result
            
            # Update state based on agent type (example)
            if next_agent_key in ["hal", "forge", "nova"]:
                self.current_state = LoopState.EXECUTING
            elif next_agent_key == "critic":
                self.current_state = LoopState.VALIDATING
            elif next_agent_key == "sage":
                self.current_state = LoopState.REFLECTING
            else:
                 self.current_state = LoopState.PLANNING # Default if unknown

            logger.info(f"Loop {self.current_loop_id}: Delegating from {current_agent_key} to {next_agent_key}")
            next_payload.loop_id = self.current_loop_id # Ensure loop_id propagates
            return await self._run_step(next_agent_key, next_payload)

        elif result.status == ResultStatus.SUCCESS:
            # Determine next step based on workflow or agent logic
            next_agent_key = self._determine_next_agent(current_agent_key, result)

            if next_agent_key:
                 # Update state based on agent type (example)
                if next_agent_key in ["hal", "forge", "nova"]:
                    self.current_state = LoopState.EXECUTING
                elif next_agent_key == "critic":
                    self.current_state = LoopState.VALIDATING
                elif next_agent_key == "sage":
                    self.current_state = LoopState.REFLECTING
                else:
                    self.current_state = LoopState.PLANNING # Default if unknown

                # Create payload for the next agent (needs refinement)
                # This is a placeholder - how to pass context/results?
                next_payload_data = result.dict() # Pass previous result as context? Needs schema.
                next_payload_data["task_id"] = f"task_{uuid.uuid4()}" # New task ID
                next_payload_data["loop_id"] = self.current_loop_id
                
                # Need to map result to the next agent's input schema
                # This requires more sophisticated logic or standardized context passing
                logger.warning(f"Loop {self.current_loop_id}: Auto-creating payload for {next_agent_key}. Payload mapping logic needed.")
                # Example: Critic expects output_payload
                if next_agent_key == "critic":
                     next_payload_data = {
                         "task_id": f"task_{uuid.uuid4()}",
                         "loop_id": self.current_loop_id,
                         "source_agent": current_agent_key,
                         "output_payload": result.dict()
                     }
                # Example: Sage expects output_summary
                elif next_agent_key == "sage":
                     # Assuming Critic result has review_notes
                     summary = "Review passed." if getattr(result, "passed", True) else "Review failed."
                     summary += " Notes: " + "\n".join(getattr(result, "review_notes", []))
                     next_payload_data = {
                         "task_id": f"task_{uuid.uuid4()}",
                         "loop_id": self.current_loop_id,
                         "project_id": getattr(result, "project_id", "unknown"), # Need project_id
                         "source_agent": current_agent_key,
                         "output_summary": summary
                     }
                
                # Find the next agent's input schema to validate/create payload
                next_agent = agent_registry.get_agent_class(next_agent_key)
                if next_agent and hasattr(next_agent, "input_schema"):
                    try:
                        # Attempt to create the specific payload object
                        next_payload = next_agent.input_schema(**next_payload_data)
                        logger.info(f"Loop {self.current_loop_id}: Proceeding from {current_agent_key} to {next_agent_key}")
                        return await self._run_step(next_agent_key, next_payload)
                    except Exception as validation_error:
                        logger.error(f"Loop {self.current_loop_id}: Failed to create payload for {next_agent_key}: {validation_error}", exc_info=True)
                        self.current_state = LoopState.ERROR
                        result.status = ResultStatus.ERROR
                        result.details = f"Failed to prepare payload for next agent {next_agent_key}: {validation_error}"
                        return result
                else:
                    logger.error(f"Loop {self.current_loop_id}: Cannot find agent or input schema for {next_agent_key}")
                    self.current_state = LoopState.ERROR
                    result.status = ResultStatus.ERROR
                    result.details = f"Cannot find agent or input schema for next step: {next_agent_key}"
                    return result
            else:
                # No next agent defined, loop finishes
                self.current_state = LoopState.FINISHED
                logger.info(f"Loop {self.current_loop_id}: Finished successfully after agent {current_agent_key}.")
                return result
        else:
            # Handle other statuses if necessary
            logger.warning(f"Loop {self.current_loop_id}: Unhandled status {result.status} from agent {current_agent_key}")
            self.current_state = LoopState.ERROR # Treat unexpected status as error
            return result

    def _determine_next_agent(self, current_agent_key: str, result: BaseAgentResult) -> Optional[str]:
        """Determines the next agent based on the workflow and result."""
        # Simple workflow logic
        if current_agent_key == "critic":
            # If critic failed, maybe stop or reroute? For now, proceed to Sage.
            if not getattr(result, "passed", True):
                 logger.warning(f"Loop {self.current_loop_id}: Critic validation failed, but proceeding to Sage.")
            return self.workflow.get(current_agent_key)
        
        # Add more complex logic here if needed, e.g., based on result details
        return self.workflow.get(current_agent_key)

# Global instance (or manage via dependency injection)
loop_controller = LoopController()

