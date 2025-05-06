import logging
from app.core.agent_registry import register, AgentCapability
from app.core.base_agent import BaseAgent
from app.schemas.agents.minimal_test.minimal_test_schemas import MinimalTestRequest, MinimalTestResult
from app.schemas.core.agent_result import ResultStatus

logger = logging.getLogger(__name__)

@register(
    key="minimal_test",
    name="Minimal Test Agent",
    capabilities=[]
)
class MinimalTestAgent(BaseAgent):
    """A minimal agent for testing registration infrastructure."""
    input_schema = MinimalTestRequest
    output_schema = MinimalTestResult

    async def run(self, payload: MinimalTestRequest) -> MinimalTestResult:
        logger.info(f"MinimalTestAgent received: {payload.message}")
        return MinimalTestResult(
            task_id=payload.task_id,
            status=ResultStatus.SUCCESS,
            response=f"Minimal agent processed: {payload.message}"
        )

