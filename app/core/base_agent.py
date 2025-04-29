# app/core/base_agent.py
"""
Base class for all agents in the Promethios system.

Defines the core interface and provides common functionality,
including schema definition, validation, and basic memory logging.
"""

import logging
from abc import ABC, abstractmethod
from typing import Type, Optional, Any # Added Any
from pydantic import BaseModel, ValidationError

# Assuming AgentResult is correctly defined elsewhere
from app.schemas.core.agent_result import AgentResult, ResultStatus

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    input_schema: Optional[Type[BaseModel]] = None
    output_schema: Optional[Type[AgentResult]] = None # Ensure this is AgentResult or a subclass

    @abstractmethod
    async def run(self, payload: BaseModel) -> AgentResult:
        """Main execution method for the agent."""
        pass

    async def execute_and_validate(self, payload: BaseModel) -> AgentResult:
        """
        Executes the agent's run method, validates the output, logs heartbeat/memory stub,
        and performs a basic mutation check.
        Incorporates schema validation, heartbeat, and mutation check from Pessimist Report.
        """
        agent_name = self.__class__.__name__
        # Attempt to get task_id and project_id from payload, provide defaults if not found
        task_id = getattr(payload, 'task_id', 'unknown_task')
        project_id = getattr(payload, 'project_id', None)

        # --- Input Validation (Basic Check) ---
        if self.input_schema and not isinstance(payload, self.input_schema):
            error_msg = f"Input payload type {type(payload).__name__} does not match expected schema {self.input_schema.__name__} for agent {agent_name}"
            logger.error(error_msg)
            # Return a generic error result if input validation fails
            return AgentResult(status=ResultStatus.ERROR, errors=[error_msg], task_id=task_id)

        # --- Agent Execution ---
        try:
            result = await self.run(payload)
            # Ensure result is an AgentResult instance
            if not isinstance(result, AgentResult):
                 if isinstance(result, dict):
                     try:
                         # Attempt to create AgentResult, preserving original dict if it fails
                         result_dict = result
                         result = AgentResult(**result_dict)
                     except Exception as coercion_error:
                         error_msg = f"Agent {agent_name} run() returned a dict that couldn't be coerced into AgentResult: {coercion_error}. Original dict: {result_dict}"
                         logger.error(error_msg, exc_info=True)
                         return AgentResult(status=ResultStatus.ERROR, errors=[error_msg], task_id=task_id)
                 else:
                    error_msg = f"Agent {agent_name} run() returned unexpected type {type(result).__name__}. Expected AgentResult or dict."
                    logger.error(error_msg)
                    return AgentResult(status=ResultStatus.ERROR, errors=[error_msg], task_id=task_id)

            # Ensure task_id is set on the result
            if not getattr(result, 'task_id', None) and task_id != 'unknown_task':
                result.task_id = task_id

        except Exception as e:
            error_msg = f"Agent {agent_name} encountered an unhandled exception during run: {e}"
            logger.error(error_msg, exc_info=True)
            # Create a minimal AgentResult for the exception
            return AgentResult(status=ResultStatus.ERROR, errors=[error_msg], task_id=task_id)

        # --- Schema Validation ---
        validated_result = result # Start with the result from run()
        if self.output_schema:
            try:
                # Use model_validate for Pydantic v2
                validated_model = self.output_schema.model_validate(validated_result.model_dump())
                # Preserve original error status if validation passes but agent intended error
                if validated_result.status == ResultStatus.ERROR and validated_model.status != ResultStatus.ERROR:
                     validated_model.status = ResultStatus.ERROR
                     validated_model.errors = validated_result.errors # Keep original errors if status was already ERROR
                validated_result = validated_model # Update result to the validated model
                logger.info(f"Agent {agent_name} output validated successfully against {self.output_schema.__name__}.")
            except ValidationError as e:
                error_msg = f"Agent {agent_name} output failed validation against schema {self.output_schema.__name__}: {e}"
                logger.error(error_msg)
                # Modify status and errors on the result object directly
                validated_result.status = ResultStatus.ERROR
                validated_result.errors = (validated_result.errors or []) + [f"SchemaValidationError: {error_msg}"]
                # Do not return yet, proceed to heartbeat/memory log
            except Exception as e:
                # Catch potential errors during validation itself (e.g., issues with model_dump)
                error_msg = f"Error during output validation process for agent {agent_name}: {e}"
                logger.error(error_msg, exc_info=True)
                validated_result.status = ResultStatus.ERROR
                validated_result.errors = (validated_result.errors or []) + [f"ValidationProcessError: {error_msg}"]
                # Do not return yet, proceed to heartbeat/memory log
        else:
            logger.warning(f"Agent {agent_name} does not have an output_schema defined. Skipping validation.")

        # --- Mutation Check (Basic Warning) ---
        if validated_result.status == ResultStatus.SUCCESS:
            meaningful_output = False
            try:
                # Check if any field beyond status/task_id/timestamp has a non-default/non-empty value
                # Simple check: are there any errors? Is there content in common fields?
                result_dict = validated_result.model_dump(exclude_defaults=True, exclude_none=True) # Exclude defaults and None
                for field, value in result_dict.items():
                    if field not in ['status', 'task_id', 'timestamp', 'errors']: # Ignore basic fields and errors
                         meaningful_output = True
                         break
                # Also consider errors as a mutation (even if status is SUCCESS, errors might indicate partial work)
                if validated_result.errors:
                    meaningful_output = True

            except Exception as mut_check_e:
                 logger.error(f"Error during mutation check for {agent_name}: {mut_check_e}")
                 meaningful_output = True # Assume output exists if check fails

            if not meaningful_output:
                 logger.warning(f"MUTATION_CHECK_WARN: Agent {agent_name} (Task: {task_id}) returned SUCCESS but no apparent meaningful output detected. Result: {validated_result.model_dump(exclude_none=True)}")


        # --- Agent Heartbeat / Memory Log Stub ---
        try:
            await self.log_memory(
                agent_id=agent_name,
                memory_type="agent_heartbeat",
                tag=f"execution_{validated_result.status.value}", # e.g., execution_success or execution_error
                value=validated_result.model_dump(exclude_none=True), # Log the final result state
                project_id=project_id
            )
        except Exception as log_e:
             logger.error(f"Agent {agent_name} (Task: {task_id}) failed to log heartbeat/memory stub: {log_e}", exc_info=True)
             # Optionally add this error to the result?
             # validated_result.errors = (validated_result.errors or []) + [f"HeartbeatLogError: {log_e}"]
             # validated_result.status = ResultStatus.ERROR # Decide if heartbeat failure is critical error

        return validated_result # Return the final result, potentially modified by validation

    async def log_memory(self, agent_id: str, memory_type: str, tag: str, value: Any, project_id: Optional[str] = None, reflection_id: Optional[str] = None):
        """
        Logs a memory entry. (Stub implementation for Batch 5)
        This acts as a placeholder for actual memory writing and serves as an agent heartbeat.
        """
        # In a real implementation (Batch 6+), this would call the memory engine/writer.
        try:
            # Attempt to serialize value safely for logging
            log_value_str = str(value)[:200] # Limit length
        except Exception:
            log_value_str = "[Value could not be serialized for log]"

        log_message = (
            f"HEARTBEAT/MEMORY_LOG_STUB: Agent=\"{agent_id}\" Task=\"{getattr(value, 'task_id', 'unknown')}\" "
            f"Project=\"{project_id}\" Type=\"{memory_type}\" Tag=\"{tag}\" "
            f"ReflectionID=\"{reflection_id}\". " # Added ReflectionID
            f"Status=\"{getattr(value, 'status', 'unknown')}\". Value Snippet: {log_value_str}..."
        )
        logger.info(log_message)
        # Simulate success for now
        return {"status": "success_stub", "message": "Memory log stub executed."}


    async def _log_tool_use(self, tool_name: str, tool_args: dict, tool_status: str, tool_result: Any):
        """
        Logs the usage of a tool by the agent. (Scaffolding for Batch 6)
        Specific agents should call this method after using a tool.
        """
        agent_name = self.__class__.__name__
        try:
            # Basic serialization for logging
            args_str = str(tool_args)[:150] # Limit arg length
            result_str = str(tool_result)[:150] # Limit result length
        except Exception:
            args_str = "[Args could not be serialized]"
            result_str = "[Result could not be serialized]"

        log_message = (
            f"TOOL_EXEC_LOG: Agent=\'{agent_name}\' Tool=\'{tool_name}\' Status=\'{tool_status}\'. "
            f"Args: {args_str}... Result: {result_str}..."
        )
        logger.info(log_message)
        # In future, this could write to a dedicated trace log or memory surface.




import json
import os

# Assuming AgentResult is correctly defined elsewhere
from app.schemas.core.agent_result import AgentResult, ResultStatus

logger = logging.getLogger(__name__)

# --- Tool Permissions Config Path ---
TOOL_PERMISSIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "tool_permissions.json")
# ----------------------------------

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    input_schema: Optional[Type[BaseModel]] = None
    output_schema: Optional[Type[AgentResult]] = None # Ensure this is AgentResult or a subclass
    _tool_permissions: Optional[dict] = None # Class variable to cache permissions

    def __init__(self):
        # Load permissions on initialization (stub)
        self._load_tool_permissions()

    @classmethod
    def _load_tool_permissions(cls):
        """Loads tool permissions from the config file (stub)."""
        if cls._tool_permissions is not None:
            return # Already loaded
        
        try:
            if os.path.exists(TOOL_PERMISSIONS_PATH):
                with open(TOOL_PERMISSIONS_PATH, 'r') as f:
                    cls._tool_permissions = json.load(f)
                logger.info(f"Successfully loaded tool permissions from {TOOL_PERMISSIONS_PATH}")
            else:
                logger.warning(f"Tool permissions file not found at {TOOL_PERMISSIONS_PATH}. Using default deny policy.")
                cls._tool_permissions = {"agent_permissions": {}, "default_policy": "deny"}
        except Exception as e:
            logger.error(f"Failed to load or parse tool permissions file {TOOL_PERMISSIONS_PATH}: {e}", exc_info=True)
            cls._tool_permissions = {"agent_permissions": {}, "default_policy": "deny"} # Default to deny on error

    def _check_tool_permission(self, tool_name: str) -> bool:
        """Checks if the current agent has permission to use the specified tool (stub)."""
        agent_name = self.__class__.__name__
        if self._tool_permissions is None:
            logger.error("Tool permissions not loaded. Denying tool use by default.")
            return False

        agent_perms = self._tool_permissions.get("agent_permissions", {}).get(agent_name)
        default_policy = self._tool_permissions.get("default_policy", "deny")

        if agent_perms is None: # Agent not listed
            allowed = default_policy == "allow"
            # Corrected first warning to single line
            logger.warning(f"Agent '{agent_name}' not found in tool_permissions.json. Applying default policy ('{default_policy}'): {'Allow' if allowed else 'Deny'} tool '{tool_name}'.")
            return allowed
        
        allowed = tool_name in agent_perms
        if not allowed:
             # Corrected second warning to single line
             logger.warning(f"PERMISSION_DENIED: Agent '{agent_name}' attempted to use disallowed tool '{tool_name}'.")
        # else: logger.debug(f"Permission granted for agent {agent_name} to use tool {tool_name}.") # Optional: Log success
        return allowed

    @abstractmethod
    async def run(self, payload: BaseModel) -> AgentResult:
        """Main execution method for the agent."""
        pass
