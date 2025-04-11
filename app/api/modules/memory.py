from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from app.modules.memory_writer import write_memory, memory_store, generate_reflection
from app.modules.memory_summarizer import summarize_memories
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class MemoryEntry(BaseModel):
    agent_id: str
    memory_type: str
    content: str
    tags: List[str] = []
    project_id: Optional[str] = None
    status: Optional[str] = None
    task_type: Optional[str] = None

class ReflectionRequest(BaseModel):
    agent_id: str
    goal: str
    context: Optional[Dict] = None
    task_id: str
    project_id: str
    memory_trace_id: str
    type: Optional[str] = "memory"
    limit: int = 5
    
class SummarizeRequest(BaseModel):
    agent_id: str
    goal: str
    task_id: str
    project_id: str
    memory_trace_id: str
    context: Optional[List[Dict]] = None
    type: Optional[str] = None
    limit: int = 10

class ThreadRequest(BaseModel):
    agent_id: str
    limit: Optional[int] = 100
    project_id: Optional[str] = None

class SearchRequest(BaseModel):
    agent_id: str
    query: str
    role: Optional[str] = None
    memory_type: Optional[str] = None
    limit: Optional[int] = 25
    project_id: Optional[str] = None

router = APIRouter()

@router.post("/write")
async def memory_write(request: Request):
    try:
        body = await request.json()
        memory_entry = MemoryEntry(**body)
        
        memory = write_memory(
            agent_id=memory_entry.agent_id,
            type=memory_entry.memory_type,  # Pass memory_type to type parameter
            content=memory_entry.content,
            tags=memory_entry.tags,
            project_id=memory_entry.project_id,
            status=memory_entry.status,
            task_type=memory_entry.task_type
        )
        return JSONResponse(status_code=200, content={"status": "ok", "memory_id": memory["memory_id"]})
    except Exception as e:
        print(f"❌ MemoryWriter error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.get("/read")
async def read_memory(
    agent_id: str,
    type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = 10,
    since: Optional[str] = None,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    thread_id: Optional[str] = None
):
    """
    Read memories for a specific agent with various filtering options.
    
    This endpoint retrieves memories for the specified agent, with optional filtering
    by type, tag, timestamp, project_id, task_id, and thread_id.
    
    Parameters:
    - agent_id: ID of the agent whose memories to retrieve (required)
    - type: (Optional) Filter by memory type
    - tag: (Optional) Filter by tag
    - limit: (Optional) Maximum number of memories to return, default is 10
    - since: (Optional) ISO 8601 timestamp to filter memories after a specific time
    - project_id: (Optional) Filter by project context
    - task_id: (Optional) Filter by specific task
    - thread_id: (Optional) Filter by conversation thread
    
    Returns:
    - status: "ok" if successful
    - memories: List of memory entries sorted by timestamp (newest first)
    """
    try:
        if not agent_id:
            raise HTTPException(status_code=400, detail="agent_id is required")
        
        # Filter memories by agent_id
        filtered_memories = [m for m in memory_store if m["agent_id"] == agent_id]
        
        # Apply type filter if provided
        if type:
            filtered_memories = [m for m in filtered_memories if m["type"] == type]
        
        # Apply tag filter if provided
        if tag:
            filtered_memories = [m for m in filtered_memories if tag in m["tags"]]
        
        # Apply since filter if provided
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
                filtered_memories = [
                    m for m in filtered_memories 
                    if datetime.fromisoformat(m["timestamp"]) > since_dt
                ]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid ISO 8601 format for 'since' parameter")
        
        # Apply project_id filter if provided
        if project_id:
            filtered_memories = [
                m for m in filtered_memories 
                if "project_id" in m and m["project_id"] == project_id
            ]
        
        # Apply task_id filter if provided
        if task_id:
            filtered_memories = [
                m for m in filtered_memories 
                if "task_id" in m and m["task_id"] == task_id
            ]
        
        # Apply thread_id filter if provided
        if thread_id:
            filtered_memories = [
                m for m in filtered_memories 
                if "thread_id" in m and m["thread_id"] == thread_id
            ]
        
        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        if limit and limit > 0:
            filtered_memories = filtered_memories[:limit]
        
        return {
            "status": "ok",
            "memories": filtered_memories
        }
    except HTTPException as e:
        print(f"❌ MemoryReader error: {str(e.detail)}")
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})
    except Exception as e:
        print(f"❌ MemoryReader error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.post("/reflect")
async def reflect_on_memories(request: Request):
    """
    Generate a reflection based on agent memories and store it with SDK-compliant metadata.
    
    This endpoint complies with Promethios_Module_Contract_v1.0.0 by:
    - Validating required input fields (agent_id, goal, task_id, project_id, memory_trace_id)
    - Returning a structured response with all required fields
    - Writing memory with memory_type="reflection" and all trace fields
    - Providing proper logging for failures or validation errors
    
    Request body:
    - agent_id: ID of the agent to generate reflection for (required)
    - goal: Purpose of the reflection (required)
    - context: Optional additional context for reflection
    - task_id: Task identifier for tracing (required)
    - project_id: Project identifier for context (required)
    - memory_trace_id: Memory trace identifier for linking (required)
    - type: Memory type to reflect on (optional, defaults to "memory")
    - limit: Maximum number of memories to consider (optional, defaults to 5)
    
    Returns:
    - status: "success" if successful, "failure" if error occurred
    - reflection: Generated reflection text
    - task_id: Task identifier (echoed from request)
    - project_id: Project identifier (echoed from request)
    - memory_trace_id: Memory trace identifier (echoed from request)
    - agent_id: Agent identifier (echoed from request)
    """
    try:
        # Parse request body
        body = await request.json()
        reflection_request = ReflectionRequest(**body)
        
        # Get recent memories using similar logic to /read endpoint
        filtered_memories = [m for m in memory_store if m["agent_id"] == reflection_request.agent_id]
        
        # Apply type filter if type is provided
        if reflection_request.type:
            filtered_memories = [m for m in filtered_memories if m["type"] == reflection_request.type]
        
        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        filtered_memories = filtered_memories[:reflection_request.limit]
        
        # Generate reflection
        reflection_text = generate_reflection(filtered_memories)
        
        # Write reflection as a new memory with all trace fields
        memory = write_memory(
            agent_id=reflection_request.agent_id,
            type="reflection",
            content=reflection_text,
            tags=["reflection", f"based_on_{reflection_request.type}", "sdk_compliant"],
            project_id=reflection_request.project_id,
            task_id=reflection_request.task_id,
            memory_trace_id=reflection_request.memory_trace_id,
            status="completed"
        )
        
        # Log successful reflection generation
        print(f"✅ Reflection generated for agent {reflection_request.agent_id} with task_id {reflection_request.task_id}")
        
        # Return SDK-compliant structured response
        return {
            "status": "success",
            "reflection": reflection_text,
            "task_id": reflection_request.task_id,
            "project_id": reflection_request.project_id,
            "memory_trace_id": reflection_request.memory_trace_id,
            "agent_id": reflection_request.agent_id
        }
    except Exception as e:
        # Log error details
        print(f"❌ Reflection Engine error: {str(e)}")
        
        # Return SDK-compliant error response
        return JSONResponse(status_code=500, content={
            "status": "failure",
            "reflection": f"Error generating reflection: {str(e)}",
            "task_id": body.get("task_id", "unknown"),
            "project_id": body.get("project_id", "unknown"),
            "memory_trace_id": body.get("memory_trace_id", "unknown"),
            "agent_id": body.get("agent_id", "unknown")
        })

@router.post("/summarize")
async def summarize_memories_endpoint(request: Request):
    """
    Summarize recent memories for an agent into a coherent natural language summary.
    
    This endpoint complies with Promethios_Module_Contract_v1.0.0 by:
    - Validating required input fields (agent_id, goal, task_id, project_id, memory_trace_id)
    - Returning a structured response with all required fields
    - Writing memory with memory_type="summary" and all trace fields
    - Providing proper logging for failures or validation errors
    
    Request body:
    - agent_id: ID of the agent to generate summary for (required)
    - goal: Purpose of the summary (required)
    - task_id: Task identifier for tracing (required)
    - project_id: Project identifier for context (required)
    - memory_trace_id: Memory trace identifier for linking (required)
    - context: Optional list of memory or raw notes
    - type: Memory type to summarize (optional)
    - limit: Maximum number of memories to consider (optional, defaults to 10)
    
    Returns:
    - status: "success" if successful, "failure" if error occurred
    - summary: Generated summary text
    - task_id: Task identifier (echoed from request)
    - project_id: Project identifier (echoed from request)
    - memory_trace_id: Memory trace identifier (echoed from request)
    - agent_id: Agent identifier (echoed from request)
    """
    try:
        # Parse request body
        body = await request.json()
        summarize_request = SummarizeRequest(**body)
        
        # Get recent memories using similar logic to /read endpoint
        filtered_memories = [m for m in memory_store if m["agent_id"] == summarize_request.agent_id]
        
        # Apply type filter if provided
        if summarize_request.type:
            filtered_memories = [m for m in filtered_memories if m["type"] == summarize_request.type]
        
        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        filtered_memories = filtered_memories[:summarize_request.limit]
        
        # Use context if provided
        if summarize_request.context:
            # If context is provided, use it instead of filtered memories
            context_content = [item.get("content", str(item)) for item in summarize_request.context if item]
            summary_text = summarize_memories(context_content)
        else:
            # Generate summary from filtered memories
            summary_text = summarize_memories(filtered_memories)
        
        # Write summary to memory with all trace fields
        memory = write_memory(
            agent_id=summarize_request.agent_id,
            type="summary",
            content=summary_text,
            tags=["summary", "compressed", "sdk_compliant"],
            project_id=summarize_request.project_id,
            task_id=summarize_request.task_id,
            memory_trace_id=summarize_request.memory_trace_id,
            status="completed"
        )
        
        # Log successful summary generation
        print(f"✅ Summary generated for agent {summarize_request.agent_id} with task_id {summarize_request.task_id}")
        
        # Return SDK-compliant structured response
        return {
            "status": "success",
            "summary": summary_text,
            "task_id": summarize_request.task_id,
            "project_id": summarize_request.project_id,
            "memory_trace_id": summarize_request.memory_trace_id,
            "agent_id": summarize_request.agent_id
        }
    except Exception as e:
        # Log error details
        print(f"❌ Memory Summarization error: {str(e)}")
        
        # Return SDK-compliant error response
        return JSONResponse(status_code=500, content={
            "status": "failure",
            "summary": f"Error generating summary: {str(e)}",
            "task_id": body.get("task_id", "unknown"),
            "project_id": body.get("project_id", "unknown"),
            "memory_trace_id": body.get("memory_trace_id", "unknown"),
            "agent_id": body.get("agent_id", "unknown")
        })

@router.post("/thread")
async def memory_thread_endpoint(request: Request):
    """
    Return a full chronological list of all memory entries for a given agent.
    
    This endpoint retrieves all memories for the specified agent and returns them
    in chronological order (oldest to newest).
    
    Request body:
    - agent_id: ID of the agent whose memory thread to retrieve
    - limit: (Optional) Maximum number of memories to return, default is 100
    - project_id: (Optional) Filter by project_id
    
    Returns:
    - status: "ok" if successful
    - agent_id: ID of the agent whose memory thread was retrieved
    - memory_thread: List of memory entries in chronological order
    """
    try:
        # Parse request body
        body = await request.json()
        thread_request = ThreadRequest(**body)
        
        # Filter memories by agent_id
        filtered_memories = [m for m in memory_store if m["agent_id"] == thread_request.agent_id]
        
        # Apply project_id filter if provided
        if thread_request.project_id:
            filtered_memories = [
                m for m in filtered_memories 
                if "project_id" in m and m["project_id"] == thread_request.project_id
            ]
        
        # Transform memories to the expected format
        memory_thread = []
        for memory in filtered_memories:
            # Extract role from memory type or use default
            role = "user" if memory["type"] == "user_message" else memory["agent_id"]
            
            # Create thread entry
            thread_entry = {
                "timestamp": memory["timestamp"],
                "role": role,
                "content": memory["content"],
                "project_id": memory.get("project_id"),
                "status": memory.get("status"),
                "task_type": memory.get("task_type")
            }
            memory_thread.append(thread_entry)
        
        # Sort by timestamp (oldest first for chronological order)
        memory_thread.sort(key=lambda m: m["timestamp"])
        
        # Apply limit if specified
        if thread_request.limit and thread_request.limit > 0:
            memory_thread = memory_thread[:thread_request.limit]
        
        # Return response
        return {
            "status": "ok",
            "agent_id": thread_request.agent_id,
            "project_id": thread_request.project_id,
            "memory_thread": memory_thread
        }
    except Exception as e:
        print(f"❌ Memory Thread error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.post("/search")
async def memory_search_endpoint(request: Request):
    """
    Search an agent's memory for matching entries based on keywords, tags, roles, or memory type.
    
    This endpoint searches the content of memories for the specified agent and returns
    matches based on the provided query, optionally filtered by role, memory type, and project_id.
    
    Request body:
    - agent_id: ID of the agent whose memories to search
    - query: Search term to match in memory content
    - role: (Optional) Filter by role (e.g., "user", "hal")
    - memory_type: (Optional) Filter by memory type
    - limit: (Optional) Maximum number of results to return, default is 25
    - project_id: (Optional) Filter by project_id
    
    Returns:
    - status: "ok" if successful
    - agent_id: ID of the agent whose memories were searched
    - results: List of matching memory entries sorted by most recent first
    """
    try:
        # Parse request body
        body = await request.json()
        search_request = SearchRequest(**body)
        
        # Filter memories by agent_id
        filtered_memories = [m for m in memory_store if m["agent_id"] == search_request.agent_id]
        
        # Filter by query (basic substring match)
        if search_request.query:
            filtered_memories = [m for m in filtered_memories if search_request.query.lower() in m["content"].lower()]
        
        # Apply role filter if provided
        if search_request.role:
            # Extract role from memory type or use default
            filtered_memories = [
                m for m in filtered_memories 
                if (m["type"] == "user_message" and search_request.role == "user") or 
                   (m["type"] != "user_message" and search_request.role == m["agent_id"])
            ]
        
        # Apply memory_type filter if provided
        if search_request.memory_type:
            filtered_memories = [m for m in filtered_memories if m["type"] == search_request.memory_type]
        
        # Apply project_id filter if provided
        if search_request.project_id:
            filtered_memories = [
                m for m in filtered_memories 
                if "project_id" in m and m["project_id"] == search_request.project_id
            ]
        
        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit (default to 25 if not provided)
        limit = search_request.limit if search_request.limit is not None else 25
        filtered_memories = filtered_memories[:limit]
        
        # Transform memories to the expected format
        results = []
        for memory in filtered_memories:
            # Extract role from memory type or use default
            role = "user" if memory["type"] == "user_message" else memory["agent_id"]
            
            # Create result entry
            result_entry = {
                "timestamp": memory["timestamp"],
                "role": role,
                "memory_type": memory["type"],
                "content": memory["content"],
                "project_id": memory.get("project_id"),
                "status": memory.get("status"),
                "task_type": memory.get("task_type")
            }
            results.append(result_entry)
        
        # Return response
        return {
            "status": "ok",
            "agent_id": search_request.agent_id,
            "results": results
        }
    except Exception as e:
        print(f"❌ Memory Search error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
