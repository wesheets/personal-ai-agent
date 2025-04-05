from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.core.openai_client import get_openai_client
from app.core.prompt_manager import PromptManager
from app.core.memory_manager import MemoryManager
from app.core.vector_memory import VectorMemorySystem
from app.db.database import get_database
from app.db.supabase_manager import get_supabase_client

router = APIRouter()
prompt_manager = PromptManager()
memory_manager = MemoryManager()
vector_memory = VectorMemorySystem()

class PlannerRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None
    save_to_memory: Optional[bool] = True
    model: Optional[str] = None  # Allow model override via API parameter

class PlannerResponse(BaseModel):
    output: str
    metadata: Dict[str, Any]

async def save_interaction_to_memory(input_text: str, output_text: str, metadata: Dict[str, Any]):
    """Background task to save interaction to memory"""
    # Save to regular memory
    await memory_manager.store(
        input_text=input_text,
        output_text=output_text,
        metadata=metadata
    )
    
    # Save to vector memory
    combined_text = f"User: {input_text}\nPlanner: {output_text}"
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

async def execute(
    input_text: str,
    context: Optional[Dict[str, Any]] = None,
    save_to_memory: bool = True,
    model: Optional[str] = None,
    openai_client = None,
    db = None,
    supabase_client = None
) -> Dict[str, Any]:
    """
    Execute the Planner agent with the given input
    
    Args:
        input_text: The user input text
        context: Optional context information
        save_to_memory: Whether to save the interaction to memory
        model: Optional model override
        openai_client: OpenAI client instance
        db: Database connection
        supabase_client: Supabase client instance
        
    Returns:
        Dict containing output text and metadata
    """
    try:
        # Load the planner prompt chain
        prompt_chain = prompt_manager.get_prompt_chain("planner")
        
        # Retrieve relevant memories
        memory_context = await retrieve_relevant_memories(input_text)
        
        # If we have memory context, prepend it to the system prompt
        if memory_context:
            original_system = prompt_chain.get("system_prompt", "")
            prompt_chain["system_prompt"] = f"{memory_context}\n\n{original_system}"
        
        # Override model if specified
        if model:
            prompt_chain["model"] = model
        
        # Process the input through the prompt chain
        result = await openai_client.process_with_prompt_chain(
            prompt_chain=prompt_chain,
            user_input=input_text,
            context=context
        )
        
        # Prepare metadata
        metadata = {
            "agent": "planner",
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
            "timestamp": result.get("timestamp"),
            "model": prompt_chain.get("model", "gpt-4"),
            "priority": context.get("priority", False) if context else False
        }
        
        # Save to memory if requested
        if save_to_memory:
            await save_interaction_to_memory(
                input_text,
                result["content"],
                metadata
            )
        
        # Return the processed result
        return {
            "output": result["content"],
            "metadata": metadata
        }
    except Exception as e:
        raise Exception(f"Error executing planner agent: {str(e)}")

@router.post("/", response_model=PlannerResponse)
async def process_planner_request(
    request: PlannerRequest, 
    background_tasks: BackgroundTasks,
    openai_client=Depends(get_openai_client),
    db=Depends(get_database),
    supabase_client=Depends(get_supabase_client)
):
    """
    Process a request using the Planner agent
    """
    try:
        # Call the execute function
        result = await execute(
            input_text=request.input,
            context=request.context,
            save_to_memory=request.save_to_memory,
            model=request.model,
            openai_client=openai_client,
            db=db,
            supabase_client=supabase_client
        )
        
        return PlannerResponse(
            output=result["output"],
            metadata=result["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing planner request: {str(e)}")

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_planner_history(limit: int = 10, db=Depends(get_database)):
    """
    Get history of planner agent interactions
    """
    try:
        # Query the memory for planner agent interactions
        results = await memory_manager.query(
            query="agent:planner",
            limit=limit
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving planner history: {str(e)}")
