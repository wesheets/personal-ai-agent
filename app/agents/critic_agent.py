import logging
from typing import List, Literal, Optional, Dict

from app.core.registration_utils import register
from app.core.agent_types import AgentCapability
from app.core.base_agent import BaseAgent
from app.schemas.agents.critic.critic_schemas import CriticReviewRequest, CriticReviewResult
from app.schemas.core.agent_result import ResultStatus

logger = logging.getLogger(__name__)

@register(
    key="critic",
    name="Critic",
    capabilities=[
        AgentCapability.VALIDATION,
        AgentCapability.REFLECTION,
        AgentCapability.MEMORY_WRITE,
        AgentCapability.MEMORY_READ,
        AgentCapability.REJECTION
    ]
)
class CriticAgent(BaseAgent):
    """Critic is the cognitive validation layer of Promethios..."""
    input_schema = CriticReviewRequest
    output_schema = CriticReviewResult

    async def run(self, payload: CriticReviewRequest) -> CriticReviewResult:
        """
        Reviews agent outputs for structural, logical, and cognitive validation.
        1. Retrieve context from loop plan and memory (placeholder)
        2. Evaluate output_payload using review rubric (placeholder)
        3. Score for structure, correctness, alignment with task_type (placeholder)
        4. If issues found:
            - Flag review_notes
            - Set passed = False
            - Optionally suggest reroute (placeholder)
        5. Log memory (loop_trace + reflection_thread) (placeholder)
        6. Return structured review result
        """
        logger.info(f"Critic agent received task: {payload.task_id} for loop {payload.loop_id}")
        passed = True
        review_notes = []
        issues_detected = []
        reroute_recommended = None
        status = ResultStatus.SUCCESS
        reflection_id = f"reflect_{payload.task_id}" # Example reflection ID

        try:
            # --- Placeholder Logic --- 
            logger.info(f"Reviewing output from {payload.source_agent} for task type {payload.task_type}")
            output_data = payload.output_payload

            # Simulate review based on a simple rubric
            if not output_data: # Example check: output exists
                passed = False
                issues_detected.append("Agent output payload is empty.")
                review_notes.append("Validation Failed: Output missing.")
                reroute_recommended = payload.source_agent # Reroute back to source
            elif payload.task_type == "build" and not output_data.get("files_created"):
                passed = False
                issues_detected.append("Build task completed but no files were listed.")
                review_notes.append("Validation Failed: Build output incomplete.")
                reroute_recommended = payload.source_agent
            elif payload.task_type == "ui" and not output_data.get("frontend_files"):
                passed = False
                issues_detected.append("UI task completed but no frontend files were listed.")
                review_notes.append("Validation Failed: UI output incomplete.")
                reroute_recommended = payload.source_agent
            else:
                review_notes.append("Basic validation passed.")
                logger.info("Simulated review: Basic checks passed.")
            
            if not passed:
                 logger.warning(f"Critic review failed for task {payload.task_id}. Issues: {issues_detected}")
                 status = ResultStatus.ERROR # Or a specific FAILED_VALIDATION status if defined
            # --- End Placeholder Logic ---

        except Exception as e:
            logger.error(f"Error during Critic review: {e}", exc_info=True)
            status = ResultStatus.ERROR
            passed = False
            review_notes.append(f"Review process failed: {e}")

        result = CriticReviewResult(
            task_id=payload.task_id,
            status=status,
            passed=passed,
            review_notes=review_notes,
            issues_detected=issues_detected,
            reroute_recommended=reroute_recommended,
            reflection_id=reflection_id
        )

        # Log reflection memory
        await self.log_memory(
            agent_id="critic",
            memory_type="reflection_critic",
            tag=f"review_{payload.source_agent}",
            value=result.model_dump(exclude_none=True),
            project_id=payload.project_id,
            reflection_id=reflection_id
        )

        logger.info(f"Critic agent finished task: {payload.task_id} with status {status}, Passed: {passed}")
        return result

