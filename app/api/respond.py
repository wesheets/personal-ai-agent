from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

class RespondRequest(BaseModel):
    message: str

@router.post("/respond")
async def respond_to_operator(req: RespondRequest) -> Dict[str, str]:
    operator_message = req.message

    agent_response = (
        f"🤖 HAL received: \"{operator_message}\".\n\n"
        "Planning scope... ✅\n"
        "Would you like to delegate to ASH or NOVA next?"
    )

    return {"output": agent_response}
