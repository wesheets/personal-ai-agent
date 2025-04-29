# app/schemas/agents/hal/hal_schemas.py
from pydantic import BaseModel
from app.schemas.core.agent_result import AgentResult
from app.schemas.core.task_payload import BaseTaskPayload

class HalInput(BaseTaskPayload):
    # Minimal placeholder
    pass

class HalOutput(AgentResult):
    # Minimal placeholder
    pass

