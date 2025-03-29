from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.core.openai_client import get_openai_client
from app.core.prompt_manager import PromptManager
from app.core.memory_manager import MemoryManager
from app.db.database import get_database

router = APIRouter()
prompt_manager = PromptManager()
memory_manager = MemoryManager()

class BuilderRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None
    save_to_memory: Optional[bool] = True

class BuilderResponse(BaseModel):
    output: str
    metadata: Dict[str, Any]

async def save_interaction_to_memory(input_text: str, output_text: str, metadata: Dict[str, Any]):
    """Background task to save interaction to memory"""
    await memory_manager.store(
        input_text=input_text,
        output_text=output_text,
        metadata=metadata
    )

@router.post("/", response_model=BuilderResponse)
async def process_builder_request(
    request: BuilderRequest, 
    background_tasks: BackgroundTasks,
    openai_client=Depends(get_openai_client),
    db=Depends(get_database)
):
    """
    Process a request using the Builder agent
    """
    try:
        # Load the builder prompt chain
        prompt_chain = prompt_manager.get_prompt_chain("builder")
        
        # Process the input through the prompt chain
        result = await openai_client.process_with_prompt_chain(
            prompt_chain=prompt_chain,
            user_input=request.input,
            context=request.context
        )
        
        # Prepare metadata
        metadata = {
            "agent": "builder",
            "tokens_used": result.get("usage", {}).get("total_tokens", 0),
            "timestamp": result.get("timestamp")
        }
        
        # Save to memory if requested
        if request.save_to_memory:
            background_tasks.add_task(
                save_interaction_to_memory,
                request.input,
                result["content"],
                metadata
            )
        
        # Return the processed result
        return BuilderResponse(
            output=result["content"],
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing builder request: {str(e)}")

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_builder_history(limit: int = 10, db=Depends(get_database)):
    """
    Get history of builder agent interactions
    """
    try:
        # Query the memory for builder agent interactions
        results = await memory_manager.query(
            query="agent:builder",
            limit=limit
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving builder history: {str(e)}")
