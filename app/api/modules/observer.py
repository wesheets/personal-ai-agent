from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.modules.memory_writer import memory_store
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ReportRequest(BaseModel):
    agent_id: str
    limit: int = 5
    project_id: Optional[str] = None

router = APIRouter()

@router.post("/observer/report")
async def observer_report(request: Request):
    """
    Summarize an agent's recent actions including loops, delegations, reflections, and memory changes.
    
    This endpoint retrieves recent actions for the specified agent and generates a natural language
    summary of those actions along with structured details.
    
    Request body:
    - agent_id: ID of the agent whose actions to report
    - limit: (Optional) Maximum number of actions to include, default is 5
    - project_id: (Optional) Filter by project_id
    
    Returns:
    - status: "ok" if successful
    - agent_id: ID of the agent whose actions were reported
    - summary: Natural language summary of the agent's recent actions
    - actions: List of action entries with type, result, and timestamp
    """
    try:
        # Parse request body
        body = await request.json()
        report_request = ReportRequest(**body)
        
        # Get agent actions from memory store
        agent_actions = get_agent_actions(report_request.agent_id, report_request.limit, report_request.project_id)
        
        # Generate summary
        summary = generate_action_summary(report_request.agent_id, agent_actions)
        
        # Return response
        return {
            "status": "ok",
            "agent_id": report_request.agent_id,
            "summary": summary,
            "actions": agent_actions
        }
    except HTTPException as e:
        print(f"❌ Observer Report error: {str(e.detail)}")
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})
    except Exception as e:
        print(f"❌ Observer Report error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

def get_agent_actions(agent_id: str, limit: int, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve recent actions for the specified agent from the memory store.
    
    Args:
        agent_id: ID of the agent whose actions to retrieve
        limit: Maximum number of actions to retrieve
        project_id: Optional project_id to filter by
        
    Returns:
        List of action entries with type, result, and timestamp
    """
    if not agent_id:
        raise HTTPException(status_code=400, detail="agent_id is required")
    
    # Filter memories by agent_id
    agent_memories = [m for m in memory_store if m["agent_id"] == agent_id]
    
    # Apply project_id filter if provided
    if project_id:
        agent_memories = [
            m for m in agent_memories 
            if "project_id" in m and m["project_id"] == project_id
        ]
    
    # Sort by timestamp (newest first)
    agent_memories.sort(key=lambda m: m["timestamp"], reverse=True)
    
    # Extract action entries from memories
    actions = []
    for memory in agent_memories:
        action_type = get_action_type(memory)
        if action_type:
            action = {
                "type": action_type,
                "result": get_action_result(memory),
                "timestamp": memory["timestamp"]
            }
            
            # Add additional fields based on action type
            if action_type == "delegate":
                # Extract delegation target from tags
                for tag in memory["tags"]:
                    if tag.startswith("from:"):
                        action["from"] = tag[5:]  # Extract agent ID after "from:"
                    if tag.startswith("to:"):
                        action["to"] = tag[3:]  # Extract agent ID after "to:"
                
                # Extract task from content
                if "task" not in action and "Received task from" in memory["content"]:
                    task_start = memory["content"].find(": ") + 2
                    action["task"] = memory["content"][task_start:]
            
            actions.append(action)
            
            # Stop once we have enough actions
            if len(actions) >= limit:
                break
    
    return actions

def get_action_type(memory: Dict[str, Any]) -> Optional[str]:
    """
    Determine the action type based on memory type and tags.
    
    Args:
        memory: Memory entry from memory store
        
    Returns:
        Action type or None if not an action
    """
    memory_type = memory.get("type", "")
    memory_type_lower = memory_type.lower() if memory_type else ""
    tags = memory.get("tags", [])
    
    # Check for loop-related memory types
    if memory_type == "cognitive_loop" or memory_type_lower == "loop":
        return "loop"
    # Check for delegation-related memory types
    elif memory_type == "delegation" or memory_type_lower == "delegate" or "delegation" in tags:
        return "delegate"
    # Check for reflection-related memory types
    elif memory_type == "reflection" or memory_type_lower == "reflect":
        return "reflection"
    # Check for write-related memory types
    elif memory_type == "write" or memory_type == "memory" or memory_type_lower == "write":
        return "write"
    # Return the memory type as a fallback to ensure all memories are captured
    return memory_type

def get_action_result(memory: Dict[str, Any]) -> str:
    """
    Extract the result or summary of an action from a memory entry.
    
    Args:
        memory: Memory entry from memory store
        
    Returns:
        Result or summary of the action
    """
    memory_type = memory.get("type", "")
    memory_type_lower = memory_type.lower() if memory_type else ""
    content = memory.get("content", "")
    
    # Handle loop-related memory types
    if memory_type == "cognitive_loop" or memory_type_lower == "loop":
        # Extract the first line of the reflection as the result
        if "Reflection: " in content and "\n\n" in content:
            reflection_start = content.find("Reflection: ") + 12
            reflection_end = content.find("\n\n", reflection_start)
            return content[reflection_start:reflection_end]
        return "Reflected on system modules and generated plan"
    
    # Handle delegation-related memory types
    elif memory_type == "delegation" or memory_type_lower == "delegate":
        if "Received task from" in content:
            return "Received delegation task"
        elif "Executed delegated task from" in content:
            return "Executed delegation task"
        return "Delegation action"
    
    # Handle reflection-related memory types
    elif memory_type == "reflection" or memory_type_lower == "reflect":
        # Return first 100 characters of content as summary
        return content[:100] + ("..." if len(content) > 100 else "")
    
    # Handle write-related memory types
    elif memory_type == "write" or memory_type == "memory" or memory_type_lower == "write":
        return "Wrote memory: " + content[:50] + ("..." if len(content) > 50 else "")
    
    # Default case for other memory types
    return content[:100] + ("..." if len(content) > 100 else "")

def generate_action_summary(agent_id: str, actions: List[Dict[str, Any]]) -> str:
    """
    Generate a natural language summary of an agent's recent actions.
    
    Args:
        agent_id: ID of the agent whose actions to summarize
        actions: List of action entries to summarize
        
    Returns:
        Natural language summary of the agent's recent actions
    """
    if not actions:
        return f"No recent actions found for agent {agent_id}."
    
    # Count action types
    action_counts = {}
    for action in actions:
        action_type = action["type"]
        action_counts[action_type] = action_counts.get(action_type, 0) + 1
    
    # Generate summary
    agent_id_upper = agent_id.upper()
    summary_parts = []
    
    for action_type, count in action_counts.items():
        if count == 1:
            summary_parts.append(f"executed a {action_type}")
        else:
            summary_parts.append(f"executed {count} {action_type}s")
    
    # Join summary parts
    if len(summary_parts) == 1:
        action_summary = summary_parts[0]
    elif len(summary_parts) == 2:
        action_summary = f"{summary_parts[0]} and {summary_parts[1]}"
    else:
        action_summary = ", ".join(summary_parts[:-1]) + f", and {summary_parts[-1]}"
    
    # Add specific details for important actions
    details = []
    for action in actions:
        if action["type"] == "delegate" and "to" in action:
            details.append(f"delegated a task to {action['to']}")
        elif action["type"] == "loop":
            details.append("reflected on system modules and generated a plan")
    
    # Add details to summary if available
    if details:
        if len(details) == 1:
            detail_summary = details[0]
        elif len(details) == 2:
            detail_summary = f"{details[0]} and {details[1]}"
        else:
            detail_summary = ", ".join(details[:-1]) + f", and {details[-1]}"
        
        return f"In the last {len(actions)} steps, {agent_id_upper} {action_summary}, including {detail_summary}."
    
    return f"In the last {len(actions)} steps, {agent_id_upper} {action_summary}."
