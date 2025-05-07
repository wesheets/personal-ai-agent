"""
ArchitectAgent is the foundational recursive planner of the Promethios system.
Its purpose is to bootstrap the cognitive loop itself by analyzing the existing
execution plan, generating required scaffolding (schemas, stubs, contracts), 
and preparing tools for downstream agents.
"""

import json
import os
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.schemas.agent_input.architect_agent_input import ArchitectInstruction
from app.schemas.agent_output.architect_agent_output import ArchitectPlanResult
from app.core.agent_registry import register, AgentCapability
from app.schemas.core.agent_result import AgentResult # Cleanup Patch: Import AgentResult
# Removed toolkit_registry import as it wasn't used
from app.utils.memory import read_memory, log_memory # Placeholder imports
from app.utils.status import ResultStatus

# Define path relative to the project root (assuming agent runs from project root or path is adjusted)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JUSTIFICATION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_justification_log.json")

def log_justification(entry: dict):
    """Appends a justification entry to the log file."""
    try:
        # Load existing log or initialize
        try:
            with open(JUSTIFICATION_LOG_PATH, 'r') as f:
                content = f.read()
                log_data = json.loads(content) if content else []
        except FileNotFoundError:
            log_data = []
        except json.JSONDecodeError:
            print(f"Warning: Error decoding {JUSTIFICATION_LOG_PATH}. Reinitializing.")
            log_data = []

        if not isinstance(log_data, list):
            print(f"Warning: {JUSTIFICATION_LOG_PATH} is not a list. Reinitializing.")
            log_data = []

        # Append new entry
        log_data.append(entry)

        # Save updated log
        os.makedirs(os.path.dirname(JUSTIFICATION_LOG_PATH), exist_ok=True)
        with open(JUSTIFICATION_LOG_PATH, 'w') as f:
            json.dump(log_data, f, indent=2)
            f.write('\n')
        print(f"Successfully logged justification for agent: {entry.get('agent_id')}")

    except Exception as e:
        print(f"Error logging justification: {e}")

@register(
    key="architect",
    name="ArchitectAgent",
    capabilities=[
        AgentCapability.ARCHITECTURE,
        AgentCapability.MEMORY_WRITE,
        AgentCapability.PLANNING
    ]
)
class ArchitectAgent(BaseAgent):
    input_schema = ArchitectInstruction # Added for consistent payload processing
    
    async def run(self, payload: ArchitectInstruction) -> AgentResult: # Cleanup Patch: Changed return type hint
        """
        Generates a plan based on intent and logs justification.
        """
        
        loop_id = payload.loop_id
        intent_description = payload.intent_description
        # Corrected plan file path to be relative to project root
        plan_file_path = os.path.join(PROJECT_ROOT, f"app/memory/proposed_plan_{loop_id}.json")
        
        # Simple plan generation based on loop_0006/0007 intent
        plan = [
            {
                "step": 1,
                "action": "create_file",
                "details": "Create app/agents/example_agent.py with basic structure inheriting from BaseAgent."
            },
            {
                "step": 2,
                "action": "implement_capability",
                "details": "Implement file reading capability within ExampleAgent."
            },
            {
                "step": 3,
                "action": "register_agent",
                "details": "Register ExampleAgent in app/registry.py."
            },
            {
                "step": 4,
                "action": "update_schemas",
                "details": "Create necessary input/output schemas for ExampleAgent."
            }
        ]
        
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(plan_file_path), exist_ok=True)
            
            # Save the plan to the specified file
            with open(plan_file_path, 'w') as f:
                json.dump(plan, f, indent=2)
            print(f"Architect saved plan to: {plan_file_path}")

            # --- Batch 17.1: Log Justification --- 
            justification_entry = {
                "loop_id": loop_id,
                "timestamp": datetime.utcnow().isoformat() + "Z", # Add Z for UTC
                "agent_id": "architect",
                "action_decision": f"Generated plan for loop {loop_id} based on intent.",
                "justification_text": f"Created a 4-step plan to address the intent: 	'{intent_description}	'. Plan involves creating agent file, implementing capability, registering agent, and updating schemas.",
                "confidence_score": 0.95 # High confidence in the generated plan structure
            }
            log_justification(justification_entry)
            # --- End Batch 17.1 --- 
            
            plan_output_dict = ArchitectPlanResult(
                suggested_components=[],
                tool_scaffold_plan=[],
                memory_update={"plan_file": plan_file_path},
                status=ResultStatus.SUCCESS
            ).model_dump()
            
            return AgentResult(
                status="SUCCESS",  # Cleanup Patch: Use string value
                output=plan_output_dict
            )
        except Exception as e:
            # Log error appropriately
            error_message = f"Error generating/saving plan or logging justification for {loop_id}: {e}"
            print(error_message)
            # Optionally log justification for the failure
            failure_justification = {
                "loop_id": loop_id,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "agent_id": "architect",
                "action_decision": f"Failed to generate plan for loop {loop_id}.",
                "justification_text": f"Encountered error: {e}",
                "confidence_score": 1.0 # Confident about the failure
            }
            log_justification(failure_justification)
            
            return AgentResult(
                status="FAILURE",  # Cleanup Patch: Use string value
                errors=[str(e)]
            )

