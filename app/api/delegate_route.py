from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
import inspect

router = APIRouter()
logger = logging.getLogger("api")

# Debug logging for route registration
logger.info(f"📡 HAL Router module loaded from {__file__}")
logger.info(f"📡 HAL Router object created: {router}")

@router.post("/agent/delegate")
async def delegate(request: Request):
    try:
        # Log route execution
        logger.info(f"🧠 HAL delegate route executed from {inspect.currentframe().f_code.co_filename}")
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
