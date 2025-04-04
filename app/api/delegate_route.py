from fastapi import APIRouter, Request
import logging

router = APIRouter()
logger = logging.getLogger("api")

@router.post("/api/agent/delegate")
async def delegate(request: Request):
    body = await request.json()
    logger.info(f"🧠 HAL received a task: {body}")
    return {
        "status": "success",
        "agent": "HAL9000",
        "message": "I'm sorry, Dave. I'm afraid I can't do that.",
        "received": body
    }
