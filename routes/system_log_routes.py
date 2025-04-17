from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from memory.system_log import get_system_log, log_event, clear_system_log

# Create router
system_log_router = APIRouter(tags=["system"])

@system_log_router.get("/system/log")
async def get_system_delegation_log(
    project_id: Optional[str] = Query(None, description="Filter logs by project ID"),
    limit: int = Query(100, description="Maximum number of log entries to return"),
    agent: Optional[str] = Query(None, description="Filter logs by agent name (HAL, NOVA, CRITIC, ASH)")
) -> Dict[str, Any]:
    """
    Get system delegation log entries.
    
    Returns a list of log entries showing agent activities and delegations.
    Can be filtered by project_id and agent name.
    """
    try:
        logs = get_system_log(project_id=project_id, limit=limit, agent_filter=agent)
        return {
            "status": "success",
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system log: {str(e)}")

@system_log_router.post("/system/log")
async def add_system_log_entry(
    agent_name: str = Query(..., description="Name of the agent (HAL, NOVA, CRITIC, ASH)"),
    event: str = Query(..., description="Description of the event"),
    project_id: str = Query(..., description="Project ID"),
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add an entry to the system delegation log.
    
    This endpoint is primarily for testing and manual entries.
    Most entries should be created automatically by agent hooks.
    """
    try:
        log_entry = log_event(agent_name, event, project_id, metadata)
        return {
            "status": "success",
            "message": "Log entry added successfully",
            "log_entry": log_entry
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding log entry: {str(e)}")

@system_log_router.delete("/system/log")
async def clear_system_delegation_log() -> Dict[str, Any]:
    """
    Clear all system delegation log entries.
    
    This endpoint is primarily for testing and maintenance.
    Use with caution as it permanently deletes all log entries.
    """
    try:
        success = clear_system_log()
        if success:
            return {
                "status": "success",
                "message": "System log cleared successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear system log")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing system log: {str(e)}")
