from fastapi import APIRouter
from app.schemas.self_reflection_schema import SelfInquiryRequest
import json
from datetime import datetime

router = APIRouter()

@router.post("/reflect")
async def reflect_on_self(request: SelfInquiryRequest):
    with open("app/memory/core_beliefs.json") as f:
        beliefs = json.load(f)

    return {
        "status": "self-reflection",
        "beliefs": beliefs,
        "origin_prompt": request.prompt,
        "loop_id": request.loop_id,
        "reflected_at": datetime.utcnow().isoformat()
    }
