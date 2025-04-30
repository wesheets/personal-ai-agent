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

# Added missing class definition
class ForgeBuildSpec(BaseModel):
    """Placeholder for Forge build specifications."""
    # Define fields later as needed
    pass



# Added missing result class definition
class ForgeBuildResult(AgentResult):
    """Placeholder for Forge build results."""
    # Define fields later as needed
    pass

