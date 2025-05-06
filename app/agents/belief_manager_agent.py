from app.core.base_agent import BaseAgent
# --- Batch 21.5 Remediation: Import AgentResult and ResultStatus ---
from app.schemas.core.agent_result import AgentResult, ResultStatus
# --- End Remediation ---
from app.schemas.agents.belief_manager.belief_manager_schemas import BeliefManagerInput, BeliefManagerOutput, BeliefChangeProposal
import json
import os
from app.core.agent_registry import register, AgentCapability

BELIEF_SURFACE_PATH = "/home/ubuntu/personal-ai-agent-phase21/app/memory/belief_surface.json"

def load_json(file_path):
    """Loads JSON data from a file."""
    if not os.path.exists(file_path):
        return {}
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {file_path}: {e}")
        return {}

@register(
    key="belief_manager", 
    name="Belief Manager Agent", 
    capabilities=[AgentCapability.MEMORY_READ, AgentCapability.MEMORY_WRITE]
)
class BeliefManagerAgent(BaseAgent):
    agent_config_path = None

    async def run(self, input_data: BeliefManagerInput, current_loop_id: str) -> AgentResult:
        """Generates a belief change proposal based on input."""
        print(f"BeliefManagerAgent invoked for loop {current_loop_id}...")

        try:
            # Load current belief value if modifying or removing
            current_value = None
            if input_data.proposed_change_type in ["modified", "removed"]:
                belief_surface = load_json(BELIEF_SURFACE_PATH)
                current_value = belief_surface.get(input_data.target_belief_key)

            # Create the proposal object
            proposal = BeliefChangeProposal(
                loop_id=current_loop_id,
                proposing_agent_id=self.__class__.agent_key,
                target_belief_key=input_data.target_belief_key,
                proposed_change_type=input_data.proposed_change_type,
                current_value=current_value,
                proposed_value=input_data.proposed_value,
                justification=input_data.justification,
            )

            print(f"Generated Belief Change Proposal: {proposal.proposal_id}")

            # Prepare output
            output_data = BeliefManagerOutput(proposal=proposal)

            # --- Batch 21.5 Remediation: Correct AgentResult construction ---
            return AgentResult(
                status=ResultStatus.SUCCESS, # Add the required status field
                output=output_data.model_dump(), # Use output field for primary result
                # agent_key=self.__class__.agent_key, # agent_key is not part of AgentResult model
                # status_code=200, # status_code is not part of AgentResult model
                # result=output_data.model_dump(), # Use 'output' field instead of 'result'
                # errors=[] # error_message field is for errors
            )
            # --- End Remediation ---
        except Exception as e:
            print(f"Error in BeliefManagerAgent: {e}")
            return AgentResult(
                status=ResultStatus.FAILURE,
                error_message=str(e)
            )

