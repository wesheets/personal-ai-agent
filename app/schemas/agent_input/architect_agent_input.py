from pydantic import BaseModel
from typing import Optional

class ArchitectInstruction(BaseModel):
    loop_id: str
    intent_description: str
    # Add other fields as needed based on future architect requirements

