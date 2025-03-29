from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import json
import glob
from app.core.prompt_manager import PromptManager
from app.core.memory_manager import MemoryManager
from app.core.vector_memory import VectorMemorySystem
from app.providers import process_with_model
from app.db.database import get_database
from app.db.supabase_manager import get_supabase_client

# Create router with dynamic route generation
router = APIRouter()
prompt_manager = PromptManager()
memory_manager = MemoryManager()
vector_memory = VectorMemorySystem()

class AgentRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None
    save_to_memory: Optional[bool] = True
    model: Optional[str] = None  # Allow model override via API parameter

class AgentResponse(BaseModel):
    output: str
    metadata: Dict[str, Any]

async def save_interaction_to_memory(agent_type: str, input_text: str, output_text: str, metadata: Dict[str, Any]):
    """Background task to save interaction to memory"""
    # Save to regular memory
    await memory_manager.store(
        input_text=input_text,
        output_text=output_text,
        metadata=metadata
    )
    
    # Save to vector memory
    combined_text = f"User: {input_text}\nAssistant: {output_text}"
    await vector_memory.store_memory(
        content=combined_text,
        metadata=metadata,
        priority=metadata.get("priority", False)
    )

async def retrieve_relevant_memories(input_text: str, limit: int = 3) -> str:
    """Retrieve relevant memories for the input text"""
    try:
        # Search vector memory for similar past interactions
        memories = await vector_memory.search_memories(
            query=input_text,
            limit=limit
        )
        
        # Format memories as context
        memory_context = await vector_memory.format_memories_as_context(memories)
        return memory_context
    except Exception as e:
        print(f"Error retrieving memories: {str(e)}")
        return ""

async def process_agent_request(
    agent_type: str,
    request: AgentRequest, 
    background_tasks: BackgroundTasks,
    db=None,
    supabase_client=None
):
    """
    Process a request using the specified agent type
    
    Args:
        agent_type: The type of agent to use
        request: The agent request
        background_tasks: FastAPI background tasks
        db: Database connection
        supabase_client: Supabase client
        
    Returns:
        The processed result
    """
    try:
        # Load the agent prompt chain
        prompt_chain = prompt_manager.get_prompt_chain(agent_type)
        
        # Retrieve relevant memories
        memory_context = await retrieve_relevant_memories(request.input)
        
        # If we have memory context, prepend it to the system prompt
        if memory_context:
            original_system = prompt_chain.get("system", "")
            prompt_chain["system"] = f"{memory_context}\n\n{original_system}"
        
        # Override model if specified in request
        if request.model:
            prompt_chain["model"] = request.model
        
        # Process the input through the prompt chain
        result = await process_with_model(
            model=prompt_chain.get("model", "gpt-4"),
            prompt_chain=prompt_chain,
            user_input=request.input,
            context=request.context
        )
        
        # Prepare metadata
        metadata = {
            "agent": agent_type,
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
            "timestamp": result.get("timestamp"),
            "model": result.get("model", prompt_chain.get("model", "gpt-4")),
            "provider": result.get("provider", "unknown"),
            "priority": request.context.get("priority", False) if request.context else False
        }
        
        # Save to memory if requested
        if request.save_to_memory:
            background_tasks.add_task(
                save_interaction_to_memory,
                agent_type,
                request.input,
                result["content"],
                metadata
            )
        
        # Return the processed result
        return AgentResponse(
            output=result["content"],
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing {agent_type} request: {str(e)}")

async def get_agent_history(agent_type: str, limit: int = 10, db=None):
    """
    Get history of agent interactions
    
    Args:
        agent_type: The type of agent
        limit: Maximum number of results to return
        db: Database connection
        
    Returns:
        List of agent interactions
    """
    try:
        # Query the memory for agent interactions
        results = await memory_manager.query(
            query=f"agent:{agent_type}",
            limit=limit
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving {agent_type} history: {str(e)}")

# Dynamically register routes for all agent types based on prompt files
def register_agent_routes():
    """Register routes for all agent types based on prompt files"""
    # Get the prompts directory
    prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
    
    # Find all JSON prompt files
    prompt_files = glob.glob(os.path.join(prompts_dir, "*.json"))
    
    # Register a route for each agent type
    for prompt_file in prompt_files:
        agent_type = os.path.splitext(os.path.basename(prompt_file))[0]
        
        # Register the main agent endpoint
        @router.post(f"/{agent_type}", response_model=AgentResponse)
        async def process_request(
            request: AgentRequest,
            background_tasks: BackgroundTasks,
            db=Depends(get_database),
            supabase_client=Depends(get_supabase_client),
            agent_type=agent_type
        ):
            return await process_agent_request(
                agent_type=agent_type,
                request=request,
                background_tasks=background_tasks,
                db=db,
                supabase_client=supabase_client
            )
        
        # Register the history endpoint
        @router.get(f"/{agent_type}/history", response_model=List[Dict[str, Any]])
        async def get_history(
            limit: int = 10,
            db=Depends(get_database),
            agent_type=agent_type
        ):
            return await get_agent_history(
                agent_type=agent_type,
                limit=limit,
                db=db
            )
        
        print(f"Registered agent routes for: {agent_type}")

# Register all agent routes
register_agent_routes()
