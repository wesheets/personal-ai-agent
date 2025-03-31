from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
import json
import asyncio

from app.core.prompt_manager import PromptManager
from app.core.memory_manager import get_memory_manager
from app.core.vector_memory import get_vector_memory
from app.core.rationale_logger import get_rationale_logger
from app.core.self_evaluation import get_self_evaluation_prompt
from app.core.memory_context_reviewer import get_memory_context_reviewer
from app.core.task_tagger import get_task_tagger
from app.core.orchestrator import get_orchestrator
from app.core.confidence_retry import get_confidence_retry_manager
from app.core.nudge_manager import get_nudge_manager
from app.core.task_persistence import get_task_persistence_manager
from app.core.escalation_manager import get_escalation_manager
from app.core.behavior_manager import get_behavior_manager
from app.providers.model_router import get_model_router
from app.db.database import get_db
from app.db.supabase_manager import get_supabase

router = APIRouter(prefix="/agent", tags=["agent"])

class AgentRequest(BaseModel):
    input: str
    context: Dict[str, Any] = Field(default_factory=dict)
    model: Optional[str] = None
    save_to_memory: bool = True
    auto_orchestrate: bool = False
    enable_retry_loop: bool = True
    skip_reflection: bool = False
    priority_memory: bool = False
    tools: List[str] = Field(default_factory=list)

class AgentResponse(BaseModel):
    output: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    reflection: Optional[Dict[str, Any]] = None
    retry_data: Optional[Dict[str, Any]] = None
    nudge: Optional[Dict[str, Any]] = None
    escalation: Optional[Dict[str, Any]] = None

@router.post("/{agent_type}", response_model=AgentResponse)
async def agent_endpoint(
    agent_type: str,
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    supabase_client=Depends(get_supabase)
):
    """
    Process a request with a specific agent
    
    This endpoint processes a request with a specific agent type and returns the response.
    """
    response = await process_agent_request(
        agent_type=agent_type,
        request=request,
        background_tasks=background_tasks,
        db=db,
        supabase_client=supabase_client
    )
    
    return response

@router.post("/orchestrate", response_model=Dict[str, Any])
async def orchestrate_endpoint(
    request: AgentRequest,
    agent_type: str = Query(..., description="Initial agent type to use"),
    max_steps: int = Query(5, description="Maximum number of steps in the workflow"),
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db),
    supabase_client=Depends(get_supabase)
):
    """
    Orchestrate a multi-agent workflow
    
    This endpoint orchestrates a workflow across multiple agents based on the initial input.
    """
    orchestrator = get_orchestrator()
    
    chain = await orchestrator.orchestrate(
        initial_agent=agent_type,
        initial_input=request.input,
        context=request.context,
        auto_orchestrate=True,
        max_steps=max_steps,
        background_tasks=background_tasks,
        db=db,
        supabase_client=supabase_client,
        enable_retry_loop=request.enable_retry_loop
    )
    
    return chain.dict()

class TaskExecuteRequest(BaseModel):
    task_id: str

@router.get("/tasks/pending", response_model=List[Dict[str, Any]])
async def get_pending_tasks(
    origin_agent: Optional[str] = None,
    suggested_agent: Optional[str] = None,
    status: str = "pending",
    limit: int = 10,
    offset: int = 0
):
    """
    Get pending tasks
    
    This endpoint returns pending tasks with optional filtering.
    """
    task_manager = get_task_persistence_manager()
    
    tasks = await task_manager.get_pending_tasks(
        origin_agent=origin_agent,
        suggested_agent=suggested_agent,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return [task.dict() for task in tasks]

@router.post("/tasks/execute", response_model=Dict[str, Any])
async def execute_task(
    request: TaskExecuteRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    supabase_client=Depends(get_supabase)
):
    """
    Execute a pending task
    
    This endpoint executes a pending task by its ID.
    """
    task_manager = get_task_persistence_manager()
    
    # Get the task
    task = await task_manager.get_task(request.task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {request.task_id}")
    
    # Create a request for the suggested agent
    agent_request = AgentRequest(
        input=task.task_description,
        context={
            "origin_agent": task.origin_agent,
            "original_input": task.original_input,
            "original_output": task.original_output,
            "task_id": task.task_id,
            "is_pending_task": True,
            **(task.metadata or {})
        },
        save_to_memory=True
    )
    
    # Process the request
    response = await process_agent_request(
        agent_type=task.suggested_agent,
        request=agent_request,
        background_tasks=background_tasks,
        db=db,
        supabase_client=supabase_client
    )
    
    # Update the task status
    updated_task = await task_manager.update_task_status(
        task_id=task.task_id,
        status="executed",
        metadata={
            "execution_timestamp": datetime.now().isoformat(),
            "execution_result": response.dict()
        }
    )
    
    return {
        "task_id": task.task_id,
        "status": "executed",
        "agent": task.suggested_agent,
        "response": response.dict()
    }

@router.get("/chains", response_model=List[Dict[str, Any]])
async def get_chains(
    limit: int = 10,
    offset: int = 0
):
    """
    Get execution chains
    
    This endpoint returns execution chains with pagination.
    """
    from app.core.execution_chain_logger import get_execution_chain_logger
    
    chain_logger = get_execution_chain_logger()
    chains = await chain_logger.get_chains(limit=limit, offset=offset)
    
    return chains

@router.get("/chains/{chain_id}", response_model=Dict[str, Any])
async def get_chain(
    chain_id: str
):
    """
    Get a specific execution chain
    
    This endpoint returns details for a specific execution chain.
    """
    from app.core.execution_chain_logger import get_execution_chain_logger
    
    chain_logger = get_execution_chain_logger()
    chain = await chain_logger.get_chain(chain_id)
    
    if not chain:
        raise HTTPException(status_code=404, detail=f"Chain not found: {chain_id}")
    
    return chain

@router.get("/chains/{chain_id}/steps/{step_number}", response_model=Dict[str, Any])
async def get_chain_step(
    chain_id: str,
    step_number: int
):
    """
    Get a specific step in an execution chain
    
    This endpoint returns details for a specific step in an execution chain.
    """
    from app.core.execution_chain_logger import get_execution_chain_logger
    
    chain_logger = get_execution_chain_logger()
    step = await chain_logger.get_step(chain_id, step_number)
    
    if not step:
        raise HTTPException(status_code=404, detail=f"Step not found: {chain_id}/{step_number}")
    
    return step

async def process_agent_request(
    agent_type: str,
    request: AgentRequest,
    background_tasks: BackgroundTasks = None,
    db=None,
    supabase_client=None
) -> AgentResponse:
    """
    Process a request with a specific agent
    
    This function processes a request with a specific agent type and returns the response.
    It handles memory retrieval, prompt construction, model processing, and reflection.
    
    Args:
        agent_type: Type of agent to use
        request: Request data
        background_tasks: FastAPI background tasks
        db: Database connection
        supabase_client: Supabase client
        
    Returns:
        Agent response
    """
    # Get managers and services
    prompt_manager = PromptManager()
    memory_manager = get_memory_manager()
    vector_memory = get_vector_memory()
    rationale_logger = get_rationale_logger()
    self_evaluation = get_self_evaluation_prompt()
    memory_reviewer = get_memory_context_reviewer()
    task_tagger = get_task_tagger()
    model_router = get_model_router()
    confidence_retry_manager = get_confidence_retry_manager()
    nudge_manager = get_nudge_manager()
    task_persistence_manager = get_task_persistence_manager()
    escalation_manager = get_escalation_manager()
    behavior_manager = get_behavior_manager()
    
    # Get the prompt chain for the agent
    prompt_chain = prompt_manager.get_prompt_chain(agent_type)
    if not prompt_chain:
        raise HTTPException(status_code=404, detail=f"Agent type not found: {agent_type}")
    
    # Determine which model to use
    model = request.model or prompt_chain.get("model", "gpt-4")
    
    # Get relevant memories
    memory_context = ""
    if supabase_client:
        memories = await vector_memory.search_memories(
            query=request.input,
            agent_type=agent_type,
            limit=5,
            supabase_client=supabase_client
        )
        
        # Review memories for relevance to current task
        if memories:
            memory_context = await memory_reviewer.review_memories(
                memories=memories,
                current_task=request.input,
                agent_type=agent_type,
                model=model
            )
    
    # Get behavior feedback context
    behavior_context = await behavior_manager.get_recent_feedback_context(agent_type)
    
    # Construct the system prompt
    system_prompt = prompt_chain.get("system", "You are a helpful assistant.")
    
    # Add goal summary if available
    if "goal_summary" in prompt_chain:
        system_prompt = f"{system_prompt}\n\n## Goal\n{prompt_chain['goal_summary']}"
    
    # Add memory context if available
    if memory_context:
        system_prompt = f"{system_prompt}\n\n## Relevant Memories\n{memory_context}"
    
    # Add behavior feedback context if available
    if behavior_context:
        system_prompt = f"{system_prompt}\n\n{behavior_context}"
    
    # Add persona, role, and rules if available
    if "persona" in prompt_chain:
        persona = prompt_chain["persona"]
        system_prompt = f"{system_prompt}\n\n## Persona\nTone: {persona.get('tone', '')}\nVoice: {persona.get('voice', '')}\nTraits: {', '.join(persona.get('traits', []))}"
    
    if "role" in prompt_chain:
        system_prompt = f"{system_prompt}\n\n## Role\n{prompt_chain['role']}"
    
    if "rules" in prompt_chain:
        rules = prompt_chain["rules"]
        rules_text = "\n".join([f"- {rule}" for rule in rules])
        system_prompt = f"{system_prompt}\n\n## Rules\n{rules_text}"
    
    # Process with the model
    response_content = await model_router.process_with_model(
        model=model,
        system=system_prompt,
        user=request.input,
        context=request.context
    )
    
    # Extract the output
    output = response_content.get("content", "")
    
    # Generate metadata
    metadata = {
        "agent": agent_type,
        "model": model,
        "timestamp": datetime.now().isoformat()
    }
    
    # Skip reflection if requested
    reflection_data = {}
    if not request.skip_reflection:
        # Generate rationale
        rationale_data = await rationale_logger.generate_rationale(
            agent_type=agent_type,
            model=model,
            input_text=request.input,
            output_text=output
        )
        
        # Generate self-evaluation
        evaluation_data = await self_evaluation.generate_self_evaluation(
            agent_type=agent_type,
            model=model,
            input_text=request.input,
            output_text=output,
            rationale_data=rationale_data
        )
        
        # Combine reflection data
        reflection_data = {**rationale_data, **evaluation_data}
        
        # Log rationale
        await rationale_logger.log_rationale(
            agent_type=agent_type,
            input_text=request.input,
            output_text=output,
            reflection_data=reflection_data
        )
    
    # Tag the task
    task_tags = await task_tagger.tag_task(
        agent_type=agent_type,
        input_text=request.input,
        output_text=output,
        reflection_data=reflection_data
    )
    
    # Add tags to metadata
    metadata.update(task_tags)
    
    # Initialize additional response data
    retry_data = {}
    nudge_data = {}
    escalation_data = {}
    
    # Check for confidence-based retry if enabled
    retry_count = 0
    if request.enable_retry_loop and "confidence_level" in reflection_data:
        retry_data = await confidence_retry_manager.check_confidence(
            confidence_level=reflection_data["confidence_level"],
            agent_type=agent_type,
            model=model,
            input_text=request.input,
            output_text=output,
            reflection_data=reflection_data
        )
        
        # If retry was triggered, update the output and reflection
        if retry_data.get("retry_triggered", False):
            retry_count = 1
            output = retry_data.get("retry_response", output)
            
            # Update reflection data with retry information
            if not request.skip_reflection:
                # Generate new rationale for the retry
                new_rationale_data = await rationale_logger.generate_rationale(
                    agent_type=agent_type,
                    model=model,
                    input_text=request.input,
                    output_text=output,
                    is_retry=True
                )
                
                # Generate new self-evaluation for the retry
                new_evaluation_data = await self_evaluation.generate_self_evaluation(
                    agent_type=agent_type,
                    model=model,
                    input_text=request.input,
                    output_text=output,
                    rationale_data=new_rationale_data,
                    is_retry=True
                )
                
                # Update reflection data
                reflection_data = {**new_rationale_data, **new_evaluation_data}
    
    # Check for nudge
    if not request.skip_reflection:
        nudge_data = await nudge_manager.check_for_nudge(
            agent_name=agent_type,
            input_text=request.input,
            output_text=output,
            reflection_data=reflection_data
        )
    
    # Check for escalation
    if not request.skip_reflection:
        escalation_data = await escalation_manager.check_for_escalation(
            agent_name=agent_type,
            task_description=request.input,
            reflection_data=reflection_data,
            retry_count=retry_count,
            memory_summary=memory_context
        )
    
    # Save to memory if requested
    if request.save_to_memory and supabase_client:
        await vector_memory.add_memory(
            agent_type=agent_type,
            input_text=request.input,
            output_text=output,
            metadata={
                "reflection": reflection_data,
                "tags": metadata.get("tags", []),
                "task_category": metadata.get("task_category")
            },
            priority=request.priority_memory,
            supabase_client=supabase_client
        )
    
    # Handle suggested next step if auto_orchestrate is false
    if not request.auto_orchestrate and "suggested_next_step" in metadata:
        await task_persistence_manager.store_pending_task(
            task_description=metadata["suggested_next_step"],
            origin_agent=agent_type,
            suggested_agent=metadata.get("suggested_agent"),
            priority=request.priority_memory,
            metadata={
                "task_category": metadata.get("task_category"),
                "tags": metadata.get("tags", [])
            },
            original_input=request.input,
            original_output=output
        )
    
    # Create the response
    response = AgentResponse(
        output=output,
        metadata=metadata,
        reflection=reflection_data if not request.skip_reflection else None,
        retry_data=retry_data if retry_data else None,
        nudge=nudge_data if nudge_data else None,
        escalation=escalation_data if escalation_data else None
    )
    
    return response
