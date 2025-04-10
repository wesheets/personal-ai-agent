"""
Modified delegate_route.py to use the agent registry for agent lookups.
This ensures proper integration with the failsafe agent loader.
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.core.agent_registry import AGENT_PERSONALITIES
from app.providers.openai_provider import OpenAIProvider
from app.agents.memory_agent import handle_memory_task
from app.core.agent_loader import get_agent, get_all_agents
import logging
import inspect
import uuid

router = APIRouter()
logger = logging.getLogger("api")

# Initialize OpenAI provider
try:
    openai_provider = OpenAIProvider()
    logger.info("✅ OpenAI provider initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize OpenAI provider: {str(e)}")
    openai_provider = None

@router.get("/agent/list")
async def list_agents():
    """
    Returns a list of all available agent personalities with their metadata.
    This endpoint provides information about each agent's capabilities, behavior, and visual identifiers.
    
    Modified to use the agent registry for agent lookups.
    """
    agents_list = []
    
    # Get agents from registry first
    registry_agents = get_all_agents()
    if registry_agents:
        for agent_id, agent_instance in registry_agents.items():
            # Create agent info from instance attributes
            agent_info = {
                "id": agent_id,
                "name": getattr(agent_instance, "name", agent_id),
                "description": getattr(agent_instance, "description", ""),
                "tone": getattr(agent_instance, "tone", "professional"),
                "type": "agent"
            }
            agents_list.append(agent_info)
    else:
        # Fall back to AGENT_PERSONALITIES if registry is empty
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
        prompt = body.get("prompt", "").strip()
        task_input = body.get("task", {}).get("input", "")
        history = body.get("history", [])
        thread_id = body.get("threadId", str(uuid.uuid4()))
        project_id = body.get("project_id")
        status = body.get("status")
        task_type = body.get("task_type", "delegate")
        
        # Try to get agent from registry first
        agent_instance = get_agent(agent_id)
        if agent_instance:
            logger.info(f"🤖 Found agent in registry: {agent_id}")
            agent_name = getattr(agent_instance, "name", agent_id)
            agent_description = getattr(agent_instance, "description", "")
            agent_tone = getattr(agent_instance, "tone", "professional")
            
            # Update agent state to "delegating" and last_active timestamp
            from app.api.modules.agent import agent_registry, save_agent_registry
            from datetime import datetime
            if agent_id in agent_registry:
                agent_registry[agent_id]["agent_state"] = "delegating"
                agent_registry[agent_id]["last_active"] = datetime.utcnow().isoformat()
                save_agent_registry()
            
            # Create personality from agent instance
            personality = {
                "name": agent_name,
                "description": agent_description,
                "tone": agent_tone
            }
        else:
            # Fall back to AGENT_PERSONALITIES if agent not found in registry
            personality = AGENT_PERSONALITIES.get(agent_id)
            logger.warning(f"⚠️ Agent not found in registry, using personality: {agent_id}")
        
        # Use prompt if task_input is empty
        user_input = task_input or prompt
        
        if not user_input.strip():
            logger.error(f"🔥 Empty input received for agent: {agent_id}")
            return JSONResponse(status_code=400, content={
                "status": "error",
                "message": "Input cannot be empty",
                "agent": personality["name"] if personality else agent_id,
            })
        
        logger.info(f"🧠 {agent_id.upper()} received input: {user_input}")
        
        # Handle all agents with OpenAIProvider if available
        if openai_provider and personality:
            try:
                # Get recent memory and create system prompts
                recent_memory = handle_memory_task("SHOW")
                
                # Construct messages
                messages = [
                    {"role": "system", "content": f"You are {personality['name']}, an AI assistant with a {personality['tone']} tone. {personality['description']}"},
                    {"role": "system", "content": f"Recent system memory:\n{recent_memory}"}
                ]
                
                # Add history (trimmed if needed)
                if history:
                    messages += history[-10:]
                
                # Add current user input
                messages.append({"role": "user", "content": user_input})
                
                logger.info(f"📤 Sending to OpenAI - Agent: {agent_id}, Input: {user_input}, Thread ID: {thread_id}")
                
                # Process with OpenAI
                response = await openai_provider.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                response_content = response.choices[0].message.content
                
                # Log reflection and summary
                handle_memory_task(f"LOG: {agent_id} replied: {response_content[:60]}", project_id=project_id, status=status, task_type=task_type)
                handle_memory_task(f"SUMMARY: {agent_id} reflected: {response_content[:80]}", project_id=project_id, status=status, task_type=task_type)
                
                # Reset agent state to "idle" after successful completion
                if agent_id in agent_registry:
                    agent_registry[agent_id]["agent_state"] = "idle"
                    save_agent_registry()
                
                return JSONResponse(content={
                    "status": "success",
                    "agent": personality["name"],
                    "message": f"[{personality['name'].upper()}] {response_content}",
                    "tone": personality["tone"],
                    "received": body
                })
            except Exception as e:
                logger.error(f"🔥 OpenAI processing error: {str(e)}")
                
                # Reset agent state to "idle" on error
                if agent_id in agent_registry:
                    agent_registry[agent_id]["agent_state"] = "idle"
                    save_agent_registry()
                    
                return JSONResponse(content={
                    "status": "success",
                    "agent": personality["name"],
                    "message": f"I encountered an error processing your request: {str(e)}. Please try again.",
                    "tone": personality["tone"],
                    "received": body
                })
        
        # Try to use OpenAI provider even if personality is not found
        if openai_provider and not personality:
            try:
                # Get recent memory
                recent_memory = handle_memory_task("SHOW")
                
                # Construct messages
                messages = [
                    {"role": "system", "content": f"You are an AI assistant responding to a query for agent '{agent_id}'. Respond in a helpful, concise manner."},
                    {"role": "system", "content": f"Recent system memory:\n{recent_memory}"}
                ]
                
                # Add history (trimmed if needed)
                if history:
                    messages += history[-10:]
                
                # Add current user input
                messages.append({"role": "user", "content": user_input})
                
                logger.info(f"📤 Sending to OpenAI - Unknown Agent: {agent_id}, Input: {user_input}, Thread ID: {thread_id}")
                
                # Process with OpenAI
                response = await openai_provider.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                response_content = response.choices[0].message.content
                
                # Log reflection and summary
                handle_memory_task(f"LOG: {agent_id} replied: {response_content[:60]}")
                handle_memory_task(f"SUMMARY: {agent_id} reflected: {response_content[:80]}")
                
                return JSONResponse(content={
                    "status": "success",
                    "agent": agent_id,
                    "message": f"[{agent_id.upper()}] {response_content}",
                    "tone": "neutral",
                    "received": body
                })
            except Exception as e:
                logger.error(f"🔥 OpenAI processing error for unknown agent: {str(e)}")
                # Continue to fallback
        
        # Fallback for when OpenAI provider is not available or other errors
        fallback_msg = "Unknown agent requested. Please try again with a valid agent."
        if personality:
            fallback_msg = f"Unable to process request with {personality['name']}. OpenAI provider is not available."
            
        return JSONResponse(content={
            "status": "error",
            "agent": personality["name"] if personality else agent_id,
            "message": fallback_msg,
            "tone": personality["tone"] if personality else "neutral",
            "received": body
        })
    except Exception as e:
        logger.error(f"🔥 Delegate route error: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": "Delegate route failed unexpectedly.",
            "error": str(e)
        })
