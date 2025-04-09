from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.agent_registry import AGENT_REGISTRY
from app.providers.openai_provider import OpenAIProvider
import logging
import os
import json

router = APIRouter()
logger = logging.getLogger("api")

# Initialize OpenAI provider
try:
    openai_provider = OpenAIProvider()
    logger.info("✅ OpenAI provider initialized successfully for streaming")
except Exception as e:
    logger.error(f"❌ Failed to initialize OpenAI provider for streaming: {str(e)}")
    openai_provider = None

@router.post("/api/delegate-stream")
async def delegate_stream(request: Request):
    body = await request.json()
    agent_id = body.get("agent_id", "core-forge").lower()
    prompt = body.get("prompt", "")
    history = body.get("history", [])

    if agent_id not in AGENT_REGISTRY:
        return JSONResponse(status_code=404, content={"error": f"Agent '{agent_id}' not found"})

    if not openai_provider:
        return JSONResponse(status_code=500, content={"error": "OpenAI provider not initialized"})

    config = AGENT_REGISTRY[agent_id]

    system_prompt = {
        "role": "system",
        "content": config["system_prompt"]
    }

    messages = [system_prompt] + history + [{"role": "user", "content": prompt}]

    async def stream():
        try:
            # Create a prompt chain for OpenAIProvider
            prompt_chain = {
                "model": config.get("model", "gpt-4"),
                "temperature": 0.7,
                "stream": True
            }
            
            # Use the OpenAIProvider for streaming
            # For core-forge, ensure we're using the full conversation history
            logger.info(f"🔄 Streaming response for agent: {agent_id} with {len(history)} history items")
            
            response = await openai_provider.client.chat.completions.create(
                model=prompt_chain["model"],
                messages=messages,
                temperature=prompt_chain["temperature"],
                stream=True
            )
            
            async for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
                    
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(f"🔥 Streaming error for {agent_id}: {error_msg}")
            yield f"[ERROR] {error_msg}"

    return StreamingResponse(stream(), media_type="text/plain")
