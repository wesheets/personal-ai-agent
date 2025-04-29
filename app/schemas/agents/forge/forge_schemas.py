# app/schemas/agents/forge/forge_schemas.py
from pydantic import BaseModel
from app.schemas.core.agent_result import AgentResult
from app.schemas.core.task_payload import BaseTaskPayload

class ForgeInput(BaseTaskPayload):
    # Minimal placeholder
    pass

class ForgeOutput(AgentResult):
    # Minimal placeholder
    pass

