# app/schemas/agents/orchestrator/orchestrator_schemas.py
from pydantic import BaseModel
from app.schemas.core.agent_result import AgentResult
from app.schemas.core.task_payload import BaseTaskPayload

class OrchestratorInput(BaseTaskPayload):
    # Minimal placeholder
    pass

class OrchestratorOutput(AgentResult):
    # Minimal placeholder
    pass

