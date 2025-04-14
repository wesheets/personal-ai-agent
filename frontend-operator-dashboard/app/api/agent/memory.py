from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.core.memory_manager import MemoryManager
from app.core.prompt_manager import PromptManager
from app.core.openai_client import get_openai_client
from app.core.vector_memory import VectorMemorySystem
from app.db.database import get_database
from app.db.supabase_manager import get_supabase_client

router = APIRouter()
memory_manager = MemoryManager()
prompt_manager = PromptManager()
vector_memory = VectorMemorySystem()

class MemoryAgentRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None
    save_to_memory: Optional[bool] = True
    model: Optional[str] = None

class MemoryAgentResponse(BaseModel):
    output: str
    metadata: Dict[str, Any]

class MemoryStoreRequest(BaseModel):
    input: str
    output: str
    metadata: Optional[Dict[str, Any]] = None

class MemoryQueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class MemoryItem(BaseModel):
    id: str
    input: str
    output: str
    metadata: Dict[str, Any]
    timestamp: str

class MemoryQueryResponse(BaseModel):
    results: List[MemoryItem]
    metadata: Dict[str, Any]

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
    Execute the Memory agent with the given input
    
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
        # Load the memory prompt chain
        prompt_chain = prompt_manager.get_prompt_chain("memory")
        
        # Retrieve relevant memories
        memories = await vector_memory.search_memories(
            query=input_text,
            limit=5
        )
        
        # Format memories as context
        memory_context = await vector_memory.format_memories_as_context(memories)
        
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
            "agent": "memory",
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
            "timestamp": result.get("timestamp"),
            "model": prompt_chain.get("model", "gpt-4"),
            "priority": context.get("priority", False) if context else False
        }
        
        # Save to memory if requested
        if save_to_memory:
            combined_text = f"User: {input_text}\nAssistant: {result['content']}"
            await vector_memory.store_memory(
                content=combined_text,
                metadata=metadata,
                priority=metadata.get("priority", False)
            )
            
            await memory_manager.store(
                input_text=input_text,
                output_text=result["content"],
                metadata=metadata
            )
        
        # Return the processed result
        return {
            "output": result["content"],
            "metadata": metadata
        }
    except Exception as e:
        raise Exception(f"Error executing memory agent: {str(e)}")

@router.post("/agent", response_model=MemoryAgentResponse)
async def process_memory_agent_request(
    request: MemoryAgentRequest,
    background_tasks: BackgroundTasks,
    openai_client=Depends(get_openai_client),
    db=Depends(get_database),
    supabase_client=Depends(get_supabase_client)
):
    """
    Process a request using the Memory agent
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
        
        return MemoryAgentResponse(
            output=result["output"],
            metadata=result["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing memory agent request: {str(e)}")

@router.post("/store", status_code=201)
async def store_memory(request: MemoryStoreRequest, db=Depends(get_database)):
    """
    Store an interaction in the memory system
    """
    try:
        memory_id = await memory_manager.store(
            input_text=request.input,
            output_text=request.output,
            metadata=request.metadata
        )
        
        return {"message": "Memory stored successfully", "memory_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing memory: {str(e)}")

@router.post("/query", response_model=MemoryQueryResponse)
async def query_memory(request: MemoryQueryRequest, db=Depends(get_database)):
    """
    Query the memory system for relevant past interactions
    """
    try:
        results = await memory_manager.query(
            query=request.query,
            limit=request.limit
        )
        
        return MemoryQueryResponse(
            results=results,
            metadata={
                "query": request.query,
                "limit": request.limit,
                "result_count": len(results)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying memory: {str(e)}")

@router.get("/item/{memory_id}", response_model=MemoryItem)
async def get_memory_item(memory_id: str, db=Depends(get_database)):
    """
    Get a specific memory item by ID
    """
    try:
        memory_item = await memory_manager.get_by_id(memory_id)
        
        if not memory_item:
            raise HTTPException(status_code=404, detail=f"Memory item with ID {memory_id} not found")
        
        return memory_item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory item: {str(e)}")

@router.delete("/item/{memory_id}", status_code=204)
async def delete_memory_item(memory_id: str, db=Depends(get_database)):
    """
    Delete a specific memory item by ID
    """
    try:
        success = await memory_manager.delete(memory_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Memory item with ID {memory_id} not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting memory item: {str(e)}")

@router.get("/stats", response_model=Dict[str, Any])
async def get_memory_stats(db=Depends(get_database)):
    """
    Get statistics about the memory system
    """
    try:
        # This is a placeholder for actual statistics
        # In a real implementation, this would query the database for statistics
        return {
            "total_memories": len(memory_manager.memories),
            "agent_counts": {
                "builder": sum(1 for m in memory_manager.memories if m.get("metadata", {}).get("agent") == "builder"),
                "ops": sum(1 for m in memory_manager.memories if m.get("metadata", {}).get("agent") == "ops"),
                "research": sum(1 for m in memory_manager.memories if m.get("metadata", {}).get("agent") == "research")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory stats: {str(e)}")
