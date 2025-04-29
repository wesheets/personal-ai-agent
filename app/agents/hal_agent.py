import logging
from typing import List, Literal, Optional

from app.core.registration_utils import register, AgentCapability
from app.core.base_agent import BaseAgent
from app.schemas.agents.hal.hal_schemas import HALInstruction, HALResult
from app.schemas.core.agent_result import ResultStatus

logger = logging.getLogger(__name__)

@register(
    key="hal",
    name="HAL",
    capabilities=[
        AgentCapability.CODE_GENERATION,
        AgentCapability.RESEARCH,
        AgentCapability.LIGHT_BUILD,
        AgentCapability.MEMORY_WRITE,
        AgentCapability.MEMORY_READ
    ]
)
class HALAgent(BaseAgent):
    """HAL is the minimum viable builder and researcher..."""
    input_schema = HALInstruction
    output_schema = HALResult

    async def run(self, payload: HALInstruction) -> HALResult:
        """
        Executes light build or research tasks, escalating if complexity is too high.
        1. Parse task type (build, research, simple API)
        2. Attempt to complete the task (placeholder)
        3. If complexity exceeds capability, set escalation_needed = True (placeholder)
        4. If successful:
            - Log file outputs or research summaries (placeholder)
            - Prepare notes for Nova (if UX/UI) or Ash/Critic (for validation) (placeholder)
        5. Return structured result
        6. Log task outcome to memory (placeholder)
        """
        logger.info(f"HAL agent received task: {payload.task_id} of type {payload.task_type}")
        output_files = []
        research_summary = None
        escalation_needed = False
        notes_for_next_agent = None
        status = ResultStatus.SUCCESS

        try:
            # --- Placeholder Logic --- 
            logger.info(f"Attempting task: {payload.task_type} with instructions: {payload.instructions}")

            if payload.task_type == "website_build":
                # Simulate simple build
                if "complex layout" in (payload.instructions or "").lower():
                    logger.warning("Task complexity seems high for HAL. Flagging escalation.")
                    escalation_needed = True
                    status = ResultStatus.DELEGATED # Or potentially ERROR if HAL shouldn't delegate directly
                    notes_for_next_agent = "Requires complex layout, suggest Forge."
                else:
                    output_files = ["/path/to/index.html", "/path/to/style.css"]
                    notes_for_next_agent = "Basic website structure created. Needs UI refinement."
                    logger.info("Simulated simple website build.")
            elif payload.task_type == "research":
                # Simulate research
                research_summary = f"Research summary on '{payload.instructions}'. Key findings: A, B, C."
                logger.info("Simulated research task.")
            elif payload.task_type == "simple_api":
                output_files = ["/path/to/api/main.py", "/path/to/api/requirements.txt"]
                notes_for_next_agent = "Basic API structure created. Needs validation."
                logger.info("Simulated simple API build.")
            else:
                logger.error(f"Unknown task type for HAL: {payload.task_type}")
                status = ResultStatus.ERROR
            # --- End Placeholder Logic ---

        except Exception as e:
            logger.error(f"Error during HAL execution: {e}", exc_info=True)
            status = ResultStatus.ERROR

        result = HALResult(
            task_id=payload.task_id,
            status=status,
            output_files=output_files,
            research_summary=research_summary,
            escalation_needed=escalation_needed,
            notes_for_next_agent=notes_for_next_agent
        )

        # Placeholder for memory logging
        # await self.log_memory(result)

        logger.info(f"HAL agent finished task: {payload.task_id} with status {status}")
        return result

