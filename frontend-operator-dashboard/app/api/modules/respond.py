"""
Respond Module

This module provides the REST API endpoint for agent responses based on user context and memory scope.

Key features:
- User context lookup to get agent_id, memory_scope, and preferences
- Memory retrieval scoped to the user's memory_scope
- Agent response generation using the LLMEngine
- Optional memory writing for response tracking
- Personalization based on user preferences
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse

# Import models
from app.api.modules.respond_models import RespondRequest, RespondResponse

# Import user_context functions
from app.api.modules.user_context import read_user_context

# Import memory functions
from app.api.modules.memory import write_memory

# Import agent functions
from app.api.modules.agent import LLMEngine, agent_registry

# Configure logging
logger = logging.getLogger("api.modules.respond")

# Create router
router = APIRouter()
print("🧠 Route defined: /api/modules/respond -> respond_endpoint")

@router.post("")
async def respond_endpoint(request: Request):
    """
    Generate an agent response based on user context and memory scope
    
    This endpoint looks up the user's context to get their agent_id, memory_scope, and preferences,
    retrieves recent memories scoped to the user's memory_scope, generates a personalized agent
    response using the LLMEngine, and optionally writes the response back to memory.
    
    Request body:
    - user_id: ID of the user sending the message
    - message: Message content to respond to
    - log_interaction: Whether to log the interaction to memory (optional, default: false)
    - session_id: Optional session ID for multi-thread continuity
    
    Returns:
    - status: "ok" if successful
    - agent_id: ID of the agent that generated the response
    - response: Agent's response to the user's message
    - memory_id: ID of the memory created for this response (if log_interaction is true)
    - session_id: Session ID for multi-thread continuity (if provided)
    """
    try:
        # Parse request body
        body = await request.json()
        respond_request = RespondRequest(**body)
        
        # Step 1: Look up user context
        user_context = read_user_context(respond_request.user_id)
        if not user_context:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"User context not found for user_id: {respond_request.user_id}"
                }
            )
        
        # Extract user context information
        agent_id = user_context["agent_id"]
        memory_scope = user_context["memory_scope"]
        preferences = user_context["preferences"]
        
        # Step 2: Check if agent exists
        if agent_id not in agent_registry:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": f"Agent with ID '{agent_id}' not found"
                }
            )
        
        # Get agent metadata
        agent_data = agent_registry[agent_id]
        agent_name = agent_data.get("name", agent_id.upper())
        
        # Step 3: Retrieve recent memories
        try:
            # Import here to avoid circular imports
            from app.api.modules.memory import read_memory
            
            # Retrieve last 5-10 memories scoped to the user's memory_scope
            memory_limit = 10  # Default to 10 memories
            
            # Adjust memory limit based on preferences if available
            if preferences and "memory_limit" in preferences:
                memory_limit = preferences["memory_limit"]
            
            # Read memories with memory_scope filter
            memory_response = await read_memory(
                agent_id=agent_id,
                type=None,  # Include all memory types
                tag=memory_scope,  # Filter by memory_scope
                limit=memory_limit
            )
            
            recent_memories = memory_response.get("memories", [])
            
            # Format memories for context
            memory_context = ""
            for memory in recent_memories:
                memory_context += f"[{memory['type']}] {memory['content']}\n\n"
                
        except Exception as e:
            logger.warning(f"⚠️ Error retrieving memories: {str(e)}")
            memory_context = ""
            recent_memories = []
        
        # Step 4: Generate agent response
        # Update agent state to "responding"
        agent_registry[agent_id]["agent_state"] = "responding"
        agent_registry[agent_id]["last_active"] = datetime.utcnow().isoformat()
        
        # Format prompt with user message, memory context, and preferences
        formatted_prompt = f"[User {respond_request.user_id}]: {respond_request.message}\n\n"
        
        # Add memory context if available
        if memory_context:
            formatted_prompt += f"Recent context:\n{memory_context}\n"
        
        # Add personalization based on preferences
        if preferences:
            # Adjust tone based on mode preference
            if "mode" in preferences:
                mode = preferences["mode"]
                if mode == "reflective":
                    formatted_prompt += "Please respond in a thoughtful, reflective manner.\n"
                elif mode == "analytical":
                    formatted_prompt += "Please respond with analytical precision and detail.\n"
                elif mode == "creative":
                    formatted_prompt += "Please respond with creative and innovative ideas.\n"
            
            # Adjust persona based on persona preference
            if "persona" in preferences:
                persona = preferences["persona"]
                formatted_prompt += f"Adopt the {persona} persona in your response.\n"
        
        # Process the prompt with LLMEngine
        response_text = LLMEngine.infer(formatted_prompt)
        
        # Update agent state to "idle"
        agent_registry[agent_id]["agent_state"] = "idle"
        agent_registry[agent_id]["last_active"] = datetime.utcnow().isoformat()
        
        # Step 5: Write response to memory (optional)
        memory_id = None
        if respond_request.log_interaction:
            # Write user message to memory
            user_memory = write_memory(
                agent_id=agent_id,
                type="user_message",
                content=respond_request.message,
                tags=[memory_scope, "user_message"],
                metadata={
                    "user_id": respond_request.user_id,
                    "session_id": respond_request.session_id
                }
            )
            
            # Write agent response to memory
            agent_memory = write_memory(
                agent_id=agent_id,
                type="agent_reply",
                content=response_text,
                tags=[memory_scope, "agent_reply"],
                metadata={
                    "user_id": respond_request.user_id,
                    "session_id": respond_request.session_id,
                    "in_response_to": user_memory["memory_id"]
                }
            )
            
            memory_id = agent_memory["memory_id"]
        
        # Create response
        response = RespondResponse(
            status="ok",
            agent_id=agent_id,
            response=response_text,
            memory_id=memory_id,
            session_id=respond_request.session_id
        )
        
        return response.dict()
    except Exception as e:
        logger.error(f"❌ Error generating response: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to generate response: {str(e)}"
            }
        )
