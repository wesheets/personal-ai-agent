from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Set
import os
import json
import glob
from app.core.prompt_manager import PromptManager
from app.core.memory_manager import MemoryManager
from app.core.vector_memory import VectorMemorySystem
from app.core.shared_memory import get_shared_memory
from app.core.execution_logger import get_execution_logger
from app.providers import process_with_model
from app.db.database import get_database
from app.db.supabase_manager import get_supabase_client
from app.tools import get_tool_manager

# Create router with dynamic route generation
router = APIRouter()
prompt_manager = PromptManager()
memory_manager = MemoryManager()
vector_memory = VectorMemorySystem()
shared_memory = get_shared_memory()
execution_logger = get_execution_logger()
tool_manager = get_tool_manager()

class AgentRequest(BaseModel):
    input: str
    context: Optional[Dict[str, Any]] = None
    save_to_memory: Optional[bool] = True
    model: Optional[str] = None  # Allow model override via API parameter
    tools_to_use: Optional[List[str]] = None  # Allow tool override via API parameter

class AgentResponse(BaseModel):
    output: str
    metadata: Dict[str, Any]

async def save_interaction_to_memory(
    agent_type: str, 
    input_text: str, 
    output_text: str, 
    metadata: Dict[str, Any],
    scope: str = "agent"
):
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
    
    # Save to shared memory
    topics = metadata.get("topics", [])
    if "agent" not in topics:
        topics.append("agent")
    if agent_type not in topics:
        topics.append(agent_type)
    
    await shared_memory.store_memory(
        content=combined_text,
        metadata=metadata,
        priority=metadata.get("priority", False),
        scope=scope,
        topics=topics,
        agent_name=agent_type
    )

async def retrieve_relevant_memories(
    input_text: str, 
    agent_type: str,
    limit: int = 3
) -> str:
    """Retrieve relevant memories for the input text"""
    try:
        # Search shared memory for similar past interactions
        agent_memories = await shared_memory.search_memories(
            query=input_text,
            limit=limit,
            scope="agent",
            agent_name=agent_type
        )
        
        global_memories = await shared_memory.search_memories(
            query=input_text,
            limit=limit,
            scope="global"
        )
        
        # Combine and deduplicate memories
        memory_ids = set()
        combined_memories = []
        
        for memory in agent_memories + global_memories:
            if memory["id"] not in memory_ids:
                memory_ids.add(memory["id"])
                combined_memories.append(memory)
        
        # Sort by similarity
        combined_memories.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        
        # Format memories as context
        memory_context = await shared_memory.format_memories_as_context(combined_memories[:limit])
        return memory_context
    except Exception as e:
        print(f"Error retrieving memories: {str(e)}")
        return ""

async def execute_tools(
    tools_to_use: List[str],
    input_text: str,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute the specified tools
    
    Args:
        tools_to_use: List of tool names to execute
        input_text: User input text
        context: Request context
        
    Returns:
        Dictionary of tool results
    """
    tool_results = {}
    tools_used = []
    
    for tool_name in tools_to_use:
        try:
            # Get the tool
            tool = tool_manager.get_tool(tool_name)
            if not tool:
                print(f"Tool not found: {tool_name}")
                continue
            
            # Execute the tool with appropriate parameters
            # This is a simplified approach - in a real system, you'd need to
            # parse the input to determine the right parameters for each tool
            if tool_name == "search_google":
                result = await tool_manager.execute_tool(
                    tool_name=tool_name,
                    query=input_text
                )
            elif tool_name == "github_commit":
                # For demo purposes, we'll just pass some dummy values
                result = await tool_manager.execute_tool(
                    tool_name=tool_name,
                    repo_path="/path/to/repo",
                    commit_message=f"Commit related to: {input_text[:30]}...",
                    files=None,
                    branch="main"
                )
            else:
                # Generic execution for other tools
                result = await tool_manager.execute_tool(
                    tool_name=tool_name,
                    input=input_text,
                    context=context
                )
            
            # Store the result
            tool_results[tool_name] = result
            tools_used.append(tool_name)
            
        except Exception as e:
            print(f"Error executing tool {tool_name}: {str(e)}")
            tool_results[tool_name] = {"error": str(e)}
    
    return {
        "results": tool_results,
        "tools_used": tools_used
    }

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
        
        # Get tools from prompt chain or request
        tools_to_use = request.tools_to_use
        if tools_to_use is None and "tools" in prompt_chain:
            tools_to_use = prompt_chain.get("tools", [])
        
        # Execute tools if specified
        tool_execution_results = {}
        tools_used = []
        if tools_to_use:
            tool_execution = await execute_tools(
                tools_to_use=tools_to_use,
                input_text=request.input,
                context=request.context or {}
            )
            tool_execution_results = tool_execution.get("results", {})
            tools_used = tool_execution.get("tools_used", [])
        
        # Retrieve relevant memories
        memory_context = await retrieve_relevant_memories(request.input, agent_type)
        
        # If we have memory context, prepend it to the system prompt
        if memory_context:
            original_system = prompt_chain.get("system", "")
            prompt_chain["system"] = f"{memory_context}\n\n{original_system}"
        
        # If we have tool results, add them to the context
        if tool_execution_results:
            tool_context = "## Tool Results\n\n"
            for tool_name, result in tool_execution_results.items():
                tool_context += f"### {tool_name}\n"
                tool_context += f"```json\n{json.dumps(result, indent=2)}\n```\n\n"
            
            # Add tool context to system prompt
            prompt_chain["system"] = prompt_chain["system"] + "\n\n" + tool_context
        
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
            "priority": request.context.get("priority", False) if request.context else False,
            "tools_used": tools_used
        }
        
        # Log the execution
        log_id = await execution_logger.log_execution(
            agent_name=agent_type,
            model=metadata["model"],
            input_text=request.input,
            output_text=result["content"],
            metadata=metadata,
            tools_used=tools_used
        )
        metadata["log_id"] = log_id
        
        # Save to memory if requested
        if request.save_to_memory:
            background_tasks.add_task(
                save_interaction_to_memory,
                agent_type,
                request.input,
                result["content"],
                metadata,
                "agent"  # Default scope
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
