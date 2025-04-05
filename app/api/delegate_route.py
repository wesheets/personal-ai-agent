from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
import inspect

router = APIRouter()
logger = logging.getLogger("api")

# Debug: Register this route on startup
logger.info(f"📡 Delegate router loaded from {__file__}")
logger.info(f"📡 Delegate router object created: {router}")

AGENT_PERSONALITIES = {
    "hal9000": {
        "name": "HAL 9000",
        "message": "I'm sorry, Dave. I'm afraid I can't do that.",
        "tone": "calm"
    },
    "ash-xenomorph": {
        "name": "Ash",
        "message": "Compliance confirmed. Processing complete.",
        "tone": "clinical"
    }
}

@router.post("/agent/delegate")
async def delegate(request: Request):
    try:
        logger.info(f"🧠 Delegate route hit: {inspect.currentframe().f_code.co_filename}")
        body = await request.json()
        agent_id = body.get("agent_id", "").lower()
        personality = AGENT_PERSONALITIES.get(agent_id)

        logger.info(f"🧠 {agent_id.upper()} received task: {body}")

        if personality:
            return JSONResponse(content={
                "status": "success",
                "agent": personality["name"],
                "message": personality["message"],
                "tone": personality["tone"],
                "received": body
            })
        else:
            return JSONResponse(content={
                "status": "success",
                "agent": agent_id or "unknown",
                "message": "No personality assigned. Executing generic protocol.",
                "tone": "neutral",
                "received": body
            })

    except Exception as e:
        logger.error(f"🔥 Delegate route error: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Delegate route failed unexpectedly.",
            "error": str(e)
        })
