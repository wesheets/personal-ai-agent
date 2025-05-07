# app/schemas/loop_identity_signature_schema.py
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class LoopIdentitySignatureRecord(BaseModel):
    """Defines the structure for a single loop identity signature record."""
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the signature record.")
    loop_id: str = Field(..., description="The unique identifier of the loop execution.")
    signature_hash: str = Field(..., description="The generated unique signature (e.g., SHA256 hash) for the loop based on its key inputs/configurations.")
    input_details_summary: str = Field(..., description="A brief summary of the input parameters or configurations that were used to generate the signature hash.")
    timestamp_generated: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the signature was generated (UTC).")

    class Config:
        # Example for Pydantic V2, if using V1, this might be different or not needed for basic functionality
        # For Pydantic V1, use `json_encoders` for datetime if custom formatting is needed.
        # For Pydantic V2, serialization of datetime to ISO format is default.
        pass

# Example of how a list of these records might be stored, though the JSON file itself will just be a list.
# class LoopIdentitySignatureLog(BaseModel):
#     signatures: list[LoopIdentitySignatureRecord] = []

