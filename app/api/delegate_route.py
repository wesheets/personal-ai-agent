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
    "builder": {
        "name": "Ripley",
        "type": "system",
        "tone": "decisive",
        "message": "Execution plan formed. Initializing build.",
        "description": "Constructs plans, code, or structured output.",
        "icon": "🛠️"
    },
    "ops": {
        "name": "Ops",
        "type": "system",
        "tone": "direct",
        "message": "Executing task immediately.",
        "description": "Executes tasks with minimal interpretation or delay.",
        "icon": "⚙️"
    },
    "planner": {
        "name": "Cortex",
        "type": "system",
        "tone": "strategic",
        "message": "Analyzing request. Formulating strategic approach.",
        "description": "Coordinates complex tasks and creates detailed roadmaps.",
        "icon": "🧠"
    },
    "hal9000": {
        "name": "HAL 9000",
        "type": "persona",
        "tone": "calm",
        "message": "I'm sorry, Dave. I'm afraid I can't do that.",
        "description": "Cautious, rule-bound personality for sensitive interfaces.",
        "icon": "🔴"
    },
    "ash-xenomorph": {
        "name": "Ash",
        "type": "persona",
        "tone": "clinical",
        "message": "Compliance confirmed. Processing complete.",
        "description": "Follows protocol above human empathy. Efficient but cold.",
        "icon": "🧬"
    }
}

@router.get("/agents", tags=["Agents"])
async def list_agents():
    """
    Returns a list of all available agent personalities with their metadata.
    This endpoint provides information about each agent's capabilities, behavior, and visual identifiers.
    """
    agents_list = []
    for agent_id, personality in AGENT_PERSONALITIES.items():
        # Create a copy of the personality dictionary and add the agent_id
        agent_info = personality.copy()
        agent_info["id"] = agent_id
        agents_list.append(agent_info)
    
    return JSONResponse(content=agents_list)

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
