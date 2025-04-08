from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.agent_registry import AGENT_REGISTRY
import openai
import os
import json

router = APIRouter()

openai.api_key = os.getenv("OPENAI_API_KEY")

@router.post("/delegate-stream")
async def delegate_stream(request: Request):
    body = await request.json()
    agent_id = body.get("agent_id", "core-forge").lower()
    prompt = body.get("prompt", "")
    history = body.get("history", [])

    if agent_id not in AGENT_REGISTRY:
        return JSONResponse(status_code=404, content={"error": "Agent not found"})

    config = AGENT_REGISTRY[agent_id]

    system_prompt = {
        "role": "system",
        "content": config["system_prompt"]
    }

    messages = [system_prompt] + history + [{"role": "user", "content": prompt}]

    def stream():
        try:
            response = openai.ChatCompletion.create(
                model=config["model"],
                messages=messages,
                temperature=0.7,
                stream=True
            )
            for chunk in response:
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    yield delta["content"]
        except Exception as e:
            yield f"[Error: {str(e)}]"

    return StreamingResponse(stream(), media_type="text/plain")
