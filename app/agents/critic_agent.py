import logging
from typing import List, Literal, Optional, Dict

from app.core.agent_registry import register, AgentCapability
from app.core.base_agent import BaseAgent
# Use the incrementally restored schema
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
    """Critic is the cognitive validation layer of Promethios... (Fully Restored Test Version)"""
    input_schema = CriticReviewRequest
    output_schema = CriticReviewResult # Use fully restored output schema

    async def run(self, payload: CriticReviewRequest) -> CriticReviewResult:
        """Run method using fully restored schema for testing registration."""
        logger.info(f"Restored Critic agent received task: {payload.task_id} for loop {payload.loop_id}")
        
        # Return the fully restored result structure
        result = CriticReviewResult(
            task_id=payload.task_id,
            status=ResultStatus.SUCCESS, # Include status
            passed=True, # Include passed
            review_notes=["Test note"], # Include review_notes
            issues_detected=["Test issue"], # Include issues_detected
            reroute_recommended="forge", # Include reroute_recommended
            reflection_id=f"reflect_{payload.task_id}" # Include reflection_id
        )

        logger.info(f"Restored Critic agent finished task: {payload.task_id}")
        # Return dict as required by controller
        return result.model_dump() 


