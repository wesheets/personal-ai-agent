# app/schemas/agents/nova/nova_schemas.py
from pydantic import BaseModel
from app.schemas.core.agent_result import AgentResult
from app.schemas.core.task_payload import BaseTaskPayload

class NovaInput(BaseTaskPayload):
    # Minimal placeholder
    pass

class NovaOutput(AgentResult):
    # Minimal placeholder
    pass



# Added missing class definition
class NovaInstruction(BaseModel):
    """Placeholder for Nova instructions."""
    # Define fields later as needed
    pass



# Added missing result class definition
class NovaResult(AgentResult):
    """Placeholder for Nova results."""
    # Define fields later as needed
    pass

