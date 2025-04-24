from pydantic import BaseModel

class ValidateSchemaHashRequest(BaseModel):
    route_path: str
    expected_hash: str

class ValidateSchemaHashResult(BaseModel):
    valid: bool
    actual_hash: str
    message: str
