from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.agent_registry import AGENT_REGISTRY
from app.providers.openai_provider import OpenAIProvider
from app.agents.memory_agent import handle_memory_task
from app.schemas.delegate.delegate_stream_schema import DelegateStreamRequest
import logging
import os
import json
import uuid

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
    
    # Validate request against schema
    try:
        request_data = DelegateStreamRequest(**body)
        agent_id = request_data.agent_id
        prompt = request_data.prompt
        history = request_data.history
        thread_id = request_data.thread_id or str(uuid.uuid4())
    except Exception as e:
        logger.error(f"Request validation error: {str(e)}")
        return JSONResponse(status_code=400, content={"error": f"Invalid request format: {str(e)}"})
    
    if agent_id not in AGENT_REGISTRY:
        return JSONResponse(status_code=404, content={"error": f"Agent '{agent_id}' not found"})
    
    if not openai_provider:
        return JSONResponse(status_code=500, content={"error": "OpenAI provider not initialized"})
    
    config = AGENT_REGISTRY[agent_id]
    system_prompt = {
        "role": "system",
        "content": config["system_prompt"]
    }
    
    # Construct trimmed, scoped message array
    messages = [{"role": "system", "content": config["system_prompt"]}]
    
    # Get recent memory and inject it into the conversation
    recent_memory = handle_memory_task("SHOW")
    if recent_memory:
        messages.append({"role": "system", "content": f"Recent system memory:\n{recent_memory}"})
    
    # Optional: Add summarization if available
    # This is experimental as mentioned in the requirements
    try:
        if history and len(history) > 5:
            # Simple summarization by extracting key points
            # In a real implementation, this would use a more sophisticated approach
            summary = f"Previous conversation includes {len(history)} messages about: {history[-1]['content'][:50]}..."
            messages.insert(1, {"role": "system", "content": f"Memory summary: {summary}"})
    except Exception as e:
        logger.warning(f"Summarization failed: {e}")
    
    # Trim history if needed (keep last 10 messages)
    if history:
        messages += history[-10:]
    
    # Add the current user prompt
    messages.append({"role": "user", "content": prompt})
    
    async def stream():
        try:
            # Create a prompt chain for OpenAIProvider
            prompt_chain = {
                "model": config.get("model", "gpt-4"),
                "temperature": 0.7,
                "stream": True
            }
            
            # Use the OpenAIProvider for streaming
            logger.info(f"🔄 Streaming response for agent: {agent_id} with {len(history)} history items and thread ID: {thread_id}")
            
            response = await openai_provider.client.chat.completions.create(
                model=prompt_chain["model"],
                messages=messages,
                temperature=prompt_chain["temperature"],
                stream=True
            )
            
            full_response = ""
            async for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
                    full_response += delta.content
            
            # Log reflection and summary after completion
            handle_memory_task(f"LOG: {agent_id} replied: {full_response[:60]}")
            handle_memory_task(f"SUMMARY: {agent_id} reflected: {full_response[:80]}")
                    
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(f"🔥 Streaming error for {agent_id}: {error_msg}")
            yield f"[ERROR] {error_msg}"
    
    return StreamingResponse(stream(), media_type="text/plain")
