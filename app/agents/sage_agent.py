# app/agents/sage_agent.py
import logging
import uuid # Import uuid for unique IDs
from typing import List, Literal, Optional

from app.core.registration_utils import register
from app.core.agent_types import AgentCapability
from app.core.base_agent import BaseAgent
from app.schemas.agents.sage.sage_schemas import SageReflectionRequest, SageReflectionResult
from app.schemas.core.agent_result import ResultStatus, AgentResult

logger = logging.getLogger(__name__)

@register(
    key="sage",
    name="Sage",
    capabilities=[
        AgentCapability.REFLECTION,
        AgentCapability.TONE_ANALYSIS,
        AgentCapability.MEMORY_READ,
        AgentCapability.MEMORY_WRITE,
        AgentCapability.INTENT_ALIGNMENT
    ]
)
class SageAgent(BaseAgent):
    """Sage is the philosophical and emotional validator of Promethios..."""
    input_schema = SageReflectionRequest
    output_schema = SageReflectionResult

    async def run(self, payload: SageReflectionRequest) -> SageReflectionResult:
        """
        Provides high-level reflection, tone alignment, and intention-based analysis.
        1. Load loop context and tone history (placeholder)
        2. Analyze output_summary for emotional and philosophical tone (placeholder)
        3. Compare to past reflections, current operator persona (placeholder)
        4. If alignment is strong, pass and generate tone_summary
        5. If misalignment detected:
            - Add philosophical notes
            - Suggest deeper operator reflection (placeholder)
            - Optionally trigger future DriftWatcher or Trainer agents (placeholder)
        6. Log reflection thread and return result (placeholder)
        """
        logger.info(f"Sage agent received task: {payload.task_id} for loop {payload.loop_id}")
        passed = True
        tone_summary = None
        philosophical_notes = None
        improvement_suggestions = []
        status = ResultStatus.SUCCESS
        
        # Generate a more structured reflection ID including loop and step info
        # Assuming step_index might be available in payload or context in future
        step_index = getattr(payload, "step_index", "unknown_step") 
        reflection_id = f"reflect_sage_{payload.loop_id}_{step_index}_{payload.task_id}_{uuid.uuid4().hex[:8]}"

        try:
            # --- Placeholder Logic --- 
            logger.info(f"Reflecting on output from {payload.source_agent} for persona {payload.operator_persona}")
            summary = payload.output_summary or "No summary provided."

            # Simulate tone analysis and philosophical check
            if "error" in summary.lower() or "failed" in summary.lower():
                tone_summary = "Concerned, Problem-focused"
                philosophical_notes = "Acknowledging failure is important for learning."
                logger.info("Detected error tone in summary.")
            elif payload.operator_persona == "deep" and "simple" in summary.lower():
                passed = False # Example: Deep persona might expect more depth
                philosophical_notes = "Is this output sufficiently deep for the current persona context?"
                improvement_suggestions.append("Consider adding more detail or exploring alternatives.")
                logger.warning("Output seems too simple for deep persona.")
                status = ResultStatus.ERROR # Or FAILED_ALIGNMENT
            else:
                tone_summary = "Neutral, Constructive"
                philosophical_notes = "Output appears aligned with general goals."
                logger.info("Simulated reflection: Output seems aligned.")
            
            # --- End Placeholder Logic ---

        except Exception as e:
            logger.error(f"Error during Sage reflection: {e}", exc_info=True)
            status = ResultStatus.ERROR
            passed = False
            philosophical_notes = f"Reflection process failed: {e}"

        result = SageReflectionResult(
            task_id=payload.task_id,
            status=status,
            passed=passed,
            tone_summary=tone_summary,
            philosophical_notes=philosophical_notes,
            improvement_suggestions=improvement_suggestions,
            reflection_id=reflection_id # Pass the structured ID
        )

        # Log reflection memory with enhanced context
        log_value = result.model_dump(exclude_none=True)
        log_value["loop_id"] = payload.loop_id # Explicitly add loop_id to logged value
        log_value["step_index"] = step_index # Explicitly add step_index
        log_value["source_agent"] = payload.source_agent # Add source agent for context
        log_value["operator_persona"] = payload.operator_persona # Add persona for context

        await self.log_memory(
            agent_id="sage",
            memory_type="reflection_sage",
            tag=f"reflection_{payload.operator_persona}",
            value=log_value, # Log the enhanced value dictionary
            project_id=payload.project_id,
            reflection_id=reflection_id
        )

        logger.info(f"Sage agent finished task: {payload.task_id} with status {status}, Passed: {passed}")
        return result

