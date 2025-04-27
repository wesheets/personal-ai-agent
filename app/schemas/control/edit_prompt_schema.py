from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# memory_tag: stubbed_phase2.5
class EditPromptRequest(BaseModel):
    """
    Request model for the Edit Prompt endpoint.
    Contains the new prompt text to be applied to the task.
    """
    prompt: str
    metadata: Optional[Dict[str, Any]] = None
