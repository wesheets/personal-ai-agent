# app/core/loop_controller.py
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
    AWAITING_OPERATOR = "AWAITING_OPERATOR" # Added state for intervention
    HALTED = "HALTED" # Added state for intervention
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
        if not getattr(initial_payload, "loop_id", None):
             initial_payload.loop_id = self.current_loop_id # Add loop_id if missing

        return await self._run_step(initial_agent_key, initial_payload)

    async def _run_step(self, agent_key: str, payload: BaseTaskPayload) -> BaseAgentResult:
        """Runs a single step in the loop by invoking an agent."""

        # --- Loop Trace Validation ---
        if hasattr(payload, "loop_id") and payload.loop_id and self.current_loop_id and payload.loop_id != self.current_loop_id:
            error_msg = f"Loop Trace Mismatch! Payload loop_id ({payload.loop_id}) does not match controller's current_loop_id ({self.current_loop_id}). Halting loop."
            logger.critical(error_msg)
            self.current_state = LoopState.ERROR
            error_result = BaseAgentResult(
                task_id=payload.task_id,
                status=ResultStatus.ERROR,
                errors=[error_msg]
            )
            # Add to history before returning
            self.history.append({"agent": agent_key, "payload": payload.model_dump(), "result": error_result.model_dump()})
            return error_result
        # --- End Loop Trace Validation ---

        self.history.append({"agent": agent_key, "payload": payload.model_dump()})
        logger.info(f"Loop {self.current_loop_id}: Running agent {agent_key} with task {payload.task_id}")

        try:
            # Use agent_runner to execute the agent
            # Agent runner should now call execute_and_validate internally
            result: BaseAgentResult = await agent_runner.run_agent(agent_key, payload)
            self.history[-1]["result"] = result.model_dump()
            logger.info(f"Loop {self.current_loop_id}: Agent {agent_key} finished with status {result.status}")

            return await self._handle_result(agent_key, result)

        except Exception as e:
            logger.error(f"Loop {self.current_loop_id}: Error running agent {agent_key}: {e}", exc_info=True)
            self.current_state = LoopState.ERROR
            # Create a generic error result
            error_result = BaseAgentResult(
                task_id=payload.task_id,
                status=ResultStatus.ERROR,
                errors=[f"LoopController error running {agent_key}: {e}"]
            )
            self.history[-1]["result"] = error_result.model_dump()
            return error_result

    async def _handle_result(self, current_agent_key: str, result: BaseAgentResult) -> BaseAgentResult:
        """Handles the result from an agent and determines the next step."""

        # --- Reflection Enforcement Check (Critic/Sage) ---
        # Check for a hypothetical intervention flag or specific status
        requires_intervention = getattr(result, "requires_intervention", False)
        intervention_reason = getattr(result, "intervention_reason", "No reason specified")

        if requires_intervention and current_agent_key in ["critic", "sage"]:
            logger.warning(f"REFLECTION_ENFORCEMENT: Agent {current_agent_key} requires intervention for loop {self.current_loop_id}. Reason: {intervention_reason}")
            # Halt the loop or set state awaiting operator
            self.current_state = LoopState.AWAITING_OPERATOR # Or HALTED based on policy
            # Modify result status to reflect intervention need if not already set
            if result.status not in [ResultStatus.REQUIRES_OPERATOR, ResultStatus.HALT]:
                 result.status = ResultStatus.REQUIRES_OPERATOR # Default intervention status
            result.errors = (result.errors or []) + [f"Intervention required by {current_agent_key}: {intervention_reason}"]
            logger.info(f"Loop {self.current_loop_id} state changed to {self.current_state}. Halting further execution.")
            return result # Return the result indicating intervention needed

        # --- Standard Result Handling ---
        if result.status == ResultStatus.ERROR:
            self.current_state = LoopState.ERROR
            logger.error(f"Loop {self.current_loop_id}: Agent {current_agent_key} reported error: {result.errors}")
            # Potentially trigger error handling agent or stop
            return result

        elif result.status == ResultStatus.DELEGATED:
            next_agent_key = getattr(result, "delegated_to", None)
            next_payload_dict = getattr(result, "next_task_payload", None)

            # --- Delegation Validation ---
            if not next_agent_key or not isinstance(next_agent_key, str):
                error_msg = f"Delegation failed: Invalid or missing 'delegated_to' key: {next_agent_key}"
                logger.error(f"Loop {self.current_loop_id}: {error_msg}")
                self.current_state = LoopState.ERROR
                result.status = ResultStatus.ERROR
                result.errors = (result.errors or []) + [error_msg]
                return result

            if not next_payload_dict or not isinstance(next_payload_dict, dict):
                error_msg = f"Delegation failed: Invalid or missing 'next_task_payload' dictionary for agent {next_agent_key}"
                logger.error(f"Loop {self.current_loop_id}: {error_msg}")
                self.current_state = LoopState.ERROR
                result.status = ResultStatus.ERROR
                result.errors = (result.errors or []) + [error_msg]
                return result

            # Check if target agent exists in registry
            if not agent_registry.get_agent_class(next_agent_key):
                error_msg = f"Delegation failed: Target agent '{next_agent_key}' not found in registry."
                logger.error(f"Loop {self.current_loop_id}: {error_msg}")
                self.current_state = LoopState.ERROR
                result.status = ResultStatus.ERROR
                result.errors = (result.errors or []) + [error_msg]
                return result
            # --- End Delegation Validation ---

            # Update state based on agent type (example)
            self._update_loop_state(next_agent_key)

            logger.info(f"Loop {self.current_loop_id}: Delegating from {current_agent_key} to {next_agent_key}")

            # Attempt to create the specific payload object for the next agent
            next_payload = await self._prepare_next_payload(next_agent_key, next_payload_dict, current_agent_key, result)
            if next_payload:
                return await self._run_step(next_agent_key, next_payload)
            else:
                # Payload preparation failed, error handled in _prepare_next_payload
                result.status = ResultStatus.ERROR # Ensure result reflects the failure
                result.errors = (result.errors or []) + ["Failed to prepare payload for delegated agent."]
                return result

        elif result.status == ResultStatus.SUCCESS:
            # Determine next step based on workflow or agent logic
            next_agent_key = self._determine_next_agent(current_agent_key, result)

            if next_agent_key:
                # Update state based on agent type
                self._update_loop_state(next_agent_key)

                # Create payload for the next agent based on current result
                next_payload_dict = self._create_payload_dict_for_next(current_agent_key, result, next_agent_key)

                next_payload = await self._prepare_next_payload(next_agent_key, next_payload_dict, current_agent_key, result)
                if next_payload:
                    logger.info(f"Loop {self.current_loop_id}: Proceeding from {current_agent_key} to {next_agent_key}")
                    return await self._run_step(next_agent_key, next_payload)
                else:
                    # Payload preparation failed
                    result.status = ResultStatus.ERROR
                    result.errors = (result.errors or []) + ["Failed to prepare payload for next agent in workflow."]
                    return result
            else:
                # No next agent defined, loop finishes
                self.current_state = LoopState.FINISHED
                logger.info(f"Loop {self.current_loop_id}: Finished successfully after agent {current_agent_key}.")
                return result

        # Handle specific intervention statuses if needed (e.g., REQUIRES_OPERATOR)
        elif result.status in [ResultStatus.REQUIRES_OPERATOR, ResultStatus.HALT]:
             logger.warning(f"Loop {self.current_loop_id}: Execution halted by agent {current_agent_key} with status {result.status}. Reason: {result.errors}")
             self.current_state = LoopState.AWAITING_OPERATOR if result.status == ResultStatus.REQUIRES_OPERATOR else LoopState.HALTED
             return result # Return the result indicating halt/wait

        else:
            # Handle other statuses if necessary
            logger.warning(f"Loop {self.current_loop_id}: Unhandled status {result.status} from agent {current_agent_key}")
            self.current_state = LoopState.ERROR # Treat unexpected status as error
            result.errors = (result.errors or []) + [f"Unhandled status {result.status}"]
            return result

    def _update_loop_state(self, next_agent_key: str):
        """Updates the loop state based on the type of the next agent."""
        if next_agent_key in ["hal", "forge", "nova"]:
            self.current_state = LoopState.EXECUTING
        elif next_agent_key == "critic":
            self.current_state = LoopState.VALIDATING
        elif next_agent_key == "sage":
            self.current_state = LoopState.REFLECTING
        else:
            self.current_state = LoopState.PLANNING # Default if unknown

    def _create_payload_dict_for_next(self, current_agent_key: str, result: BaseAgentResult, next_agent_key: str) -> Dict[str, Any]:
        """Creates a dictionary payload for the next agent based on the current result."""
        # Basic context passing: Use previous result dict, add new task_id, keep loop_id
        next_payload_data = result.model_dump(exclude_none=True)
        next_payload_data["task_id"] = f"task_{uuid.uuid4()}" # Generate new task ID
        next_payload_data["loop_id"] = self.current_loop_id
        next_payload_data["previous_agent_key"] = current_agent_key

        # --- Agent-Specific Payload Mapping (Needs Refinement/Standardization) ---
        # Example: Critic expects output_payload from the agent it reviews
        if next_agent_key == "critic":
            next_payload_data = {
                "task_id": next_payload_data["task_id"],
                "loop_id": self.current_loop_id,
                "project_id": getattr(result, "project_id", None), # Pass project_id if available
                "source_agent": current_agent_key,
                "output_payload": result.model_dump(exclude_none=True) # Pass the full previous result
            }
        # Example: Sage expects context/summary from Critic
        elif next_agent_key == "sage" and current_agent_key == "critic":
            # Assuming Critic result has fields like 'passed', 'review_notes'
            summary = "Review passed." if getattr(result, "passed", True) else "Review failed."
            summary += " Notes: " + "\n".join(getattr(result, "review_notes", []))
            next_payload_data = {
                "task_id": next_payload_data["task_id"],
                "loop_id": self.current_loop_id,
                "project_id": getattr(result, "project_id", None),
                "source_agent": current_agent_key,
                "output_summary": summary,
                "critic_result": result.model_dump(exclude_none=True) # Pass full critic result for context
            }
        # Add more mappings as needed
        # ----------------------------------------------------------------------

        return next_payload_data

    async def _prepare_next_payload(self, next_agent_key: str, payload_dict: Dict[str, Any], current_agent_key: str, current_result: BaseAgentResult) -> Optional[BaseTaskPayload]:
        """Validates and creates the specific Pydantic payload object for the next agent."""
        next_agent_class = agent_registry.get_agent_class(next_agent_key)
        if not next_agent_class:
            logger.error(f"Loop {self.current_loop_id}: Cannot find agent class for key 
{next_agent_key}
")
            self.current_state = LoopState.ERROR
            return None

        input_schema = getattr(next_agent_class, "input_schema", None)
        if not input_schema:
            logger.error(f"Loop {self.current_loop_id}: Agent {next_agent_key} has no input_schema defined.")
            self.current_state = LoopState.ERROR
            return None

        try:
            # Ensure loop_id is present
            if "loop_id" not in payload_dict or not payload_dict["loop_id"]:
                 payload_dict["loop_id"] = self.current_loop_id
            # Ensure task_id is present
            if "task_id" not in payload_dict or not payload_dict["task_id"]:
                 payload_dict["task_id"] = f"task_{uuid.uuid4()}"

            # Attempt to create the specific payload object using model_validate for Pydantic v2
            next_payload = input_schema.model_validate(payload_dict)
            return next_payload
        except ValidationError as validation_error:
            logger.error(f"Loop {self.current_loop_id}: Failed payload validation for {next_agent_key} from {current_agent_key}. Error: {validation_error}. Payload Dict: {payload_dict}", exc_info=True)
            self.current_state = LoopState.ERROR
            return None
        except Exception as creation_error:
            logger.error(f"Loop {self.current_loop_id}: Failed to create payload object for {next_agent_key}. Error: {creation_error}. Payload Dict: {payload_dict}", exc_info=True)
            self.current_state = LoopState.ERROR
            return None

    def _determine_next_agent(self, current_agent_key: str, result: BaseAgentResult) -> Optional[str]:
        """Determines the next agent based on the workflow and result."""
        # Simple workflow logic based on predefined dictionary
        # Add more complex logic here if needed, e.g., based on result details
        # Example: If critic failed, maybe stop or reroute? (Handled by intervention check now)
        return self.workflow.get(current_agent_key)

# Global instance (or manage via dependency injection)
loop_controller = LoopController()

