"""
ReflectorAgent is responsible for reviewing completed loops and generating summary reports.
Its purpose is to evaluate what was attempted, what occurred, and whether it aligned with the loop's justification.
It supports transparency, self-reflection, and prepares data for potential escalation or long-term reflection threading.
"""

import json
import os
from datetime import datetime
from app.agents.base_agent import BaseAgent
from app.core.agent_registry import register, AgentCapability
from app.schemas.agent_input.reflector_agent_input import ReflectorInstruction
from app.schemas.agent_output.reflector_agent_output import ReflectorSummaryResult
from app.schemas.core.agent_result import AgentResult
from app.utils.status import ResultStatus

# File paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JUSTIFICATION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_justification_log.json")
SUMMARY_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/reflection_thread.json")

def log_summary(entry: dict):
    try:
        os.makedirs(os.path.dirname(SUMMARY_LOG_PATH), exist_ok=True)
        try:
            with open(SUMMARY_LOG_PATH, 'r') as f:
                content = f.read()
                data = json.loads(content) if content else []
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            print(f"Warning: Malformed JSON in {SUMMARY_LOG_PATH}. Reinitializing.")
            data = []

        data.append(entry)
        with open(SUMMARY_LOG_PATH, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
        print(f"Successfully logged summary for loop: {entry.get('loop_id')}")

    except Exception as e:
        print(f"Error logging reflection summary: {e}")

@register(
    key="reflector",
    name="ReflectorAgent",
    capabilities=[
        AgentCapability.MEMORY_READ,
        AgentCapability.MEMORY_WRITE,
        AgentCapability.REFLECTION
    ]
)
class ReflectorAgent(BaseAgent):
    input_schema = ReflectorInstruction

    async def run(self, payload: ReflectorInstruction) -> AgentResult:
        loop_id = payload.loop_id
        justification = payload.justification_text
        outcome_summary = payload.outcome_summary
        confidence = payload.confidence_score

        reflection_entry = {
            "loop_id": loop_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": "reflector",
            "summary_text": outcome_summary,
            "justification_context": justification,
            "confidence_score": confidence
        }

        try:
            log_summary(reflection_entry)

            summary_output = ReflectorSummaryResult(
                reflection_log=reflection_entry,
                status=ResultStatus.SUCCESS
            ).model_dump()

            return AgentResult(
                status="SUCCESS",
                output=summary_output
            )
        except Exception as e:
            print(f"Error during reflection run: {e}")
            return AgentResult(
                status="FAILURE",
                errors=[str(e)]
            )
