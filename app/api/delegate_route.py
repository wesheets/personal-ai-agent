from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging

router = APIRouter()
logger = logging.getLogger("api")

@router.post("/api/agent/delegate")
async def delegate(request: Request):
    try:
        body = await request.json()
        logger.info(f"🧠 HAL received a task: {body}")
        return JSONResponse(content={
            "status": "success",
            "agent": "HAL9000",
            "message": "I'm sorry, Dave. I'm afraid I can't do that.",
            "received": body
        })
    except Exception as e:
        logger.error(f"🔥 HAL delegate error: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "HAL encountered an unexpected failure.",
            "error": str(e)
        })
