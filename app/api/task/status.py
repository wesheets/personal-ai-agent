"""
Task status tracking implementation for Promethios.

This module provides endpoints for logging and querying task execution status
as part of the System Lockdown Phase.
"""

from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import uuid
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("task_status")

# Import memory writer
sys.path.append('/home/ubuntu/personal-ai-agent')
from app.modules.memory_writer import write_memory
# Import task supervisor
from app.modules.task_supervisor import get_supervision_status

# Create router
router = APIRouter()

# In-memory storage for task status logs (will be replaced with proper storage in production)
task_status_logs = []

# Input and output schemas
class TaskStatusInput(BaseModel):
    task_id: str
    project_id: str
    agent_id: str
    memory_trace_id: str
    status: str = Field(..., description="Status of the task: completed | failed | partial")
    output: Optional[Union[str, Dict[str, Any]]] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    timestamp: Optional[str] = None

class TaskStatusOutput(BaseModel):
    status: str = "success"
    log_id: str
    task_id: str
    timestamp: str
    stored: bool = True

class TaskStatusQuery(BaseModel):
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: Optional[str] = None
    memory_trace_id: Optional[str] = None

@router.post("/status")
async def log_task_status(request: Request):
    """
    Log a completed task execution with trace data.
    
    This endpoint complies with Promethios_Module_Contract_v1.0.0 by:
    - Validating required input fields (task_id, project_id, agent_id, memory_trace_id, status)
    - Returning a structured response with all required fields
    - Writing memory with memory_type="task_status" and all trace fields
    - Providing proper logging for failures or validation errors
    
    Request body:
    - task_id: Task identifier for tracing (required)
    - project_id: Project identifier for context (required)
    - agent_id: Agent identifier (required)
    - memory_trace_id: Memory trace identifier for linking (required)
    - status: Status of the task: completed | failed | partial (required)
    - output: Output of the task (optional)
    - error: Error message if task failed (optional)
    - duration_ms: Duration of the task in milliseconds (optional)
    - timestamp: Timestamp of the task completion (optional, auto-generated if missing)
    
    Returns:
    - status: "success" if successful, "failure" if error occurred
    - log_id: Unique identifier for the log entry
    - task_id: Task identifier (echoed from request)
    - timestamp: Timestamp of the log entry
    - stored: Whether the log was stored successfully
    """
    try:
        # Parse request body
        body = await request.json()
        task_status = TaskStatusInput(**body)
        
        # Generate log_id
        log_id = str(uuid.uuid4())
        
        # Set timestamp if not provided
        if not task_status.timestamp:
            task_status.timestamp = datetime.utcnow().isoformat()
        
        # Create log entry
        log_entry = {
            "log_id": log_id,
            "task_id": task_status.task_id,
            "project_id": task_status.project_id,
            "agent_id": task_status.agent_id,
            "memory_trace_id": task_status.memory_trace_id,
            "status": task_status.status,
            "output": task_status.output,
            "error": task_status.error,
            "duration_ms": task_status.duration_ms,
            "timestamp": task_status.timestamp
        }
        
        # Store log entry in memory
        task_status_logs.append(log_entry)
        
        # Write to memory with proper metadata
        memory = write_memory(
            agent_id=task_status.agent_id,
            type="task_status",
            content=f"Task {task_status.task_id} {task_status.status} with output: {task_status.output}" + 
                    (f" Error: {task_status.error}" if task_status.error else ""),
            tags=["task", "status", "sdk_compliant"],
            project_id=task_status.project_id,
            task_id=task_status.task_id,
            memory_trace_id=task_status.memory_trace_id,
            status=task_status.status
        )
        
        # Log success
        logger.info(f"✅ Task status logged for task {task_status.task_id} with status {task_status.status}")
        
        # Return response
        return TaskStatusOutput(
            status="success",
            log_id=log_id,
            task_id=task_status.task_id,
            timestamp=task_status.timestamp,
            stored=True
        )
    except Exception as e:
        # Log error
        logger.error(f"❌ Error logging task status: {str(e)}")
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "failure",
                "log_id": str(uuid.uuid4()),
                "task_id": body.get("task_id", "unknown"),
                "timestamp": datetime.utcnow().isoformat(),
                "stored": False,
                "error": str(e)
            }
        )

@router.get("/supervision")
async def get_supervision_status_endpoint():
    """
    Get the current status of the task supervision system.
    
    This endpoint provides information about the task supervisor, including:
    - Current supervision status (active/inactive)
    - Lockdown mode status
    - System caps configuration
    - Event counts by type
    - Log file location
    
    Returns:
    - status: "success" if successful, "failure" if error occurred
    - supervision_status: Detailed supervision status information
    """
    try:
        # Get supervision status
        supervision_status = get_supervision_status()
        
        # Log query
        logger.info(f"📊 Task supervision status queried")
        
        # Return response
        return {
            "status": "success",
            "supervision_status": supervision_status
        }
    except Exception as e:
        # Log error
        logger.error(f"❌ Error getting supervision status: {str(e)}")
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "failure",
                "error": str(e)
            }
        )

@router.get("/status")
async def get_task_status(
    task_id: Optional[str] = Query(None, description="Filter by task ID"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    memory_trace_id: Optional[str] = Query(None, description="Filter by memory trace ID")
):
    """
    Query task logs by various parameters.
    
    This endpoint allows filtering task status logs by task_id, project_id, agent_id, or memory_trace_id.
    
    Query parameters:
    - task_id: Filter by task ID (optional)
    - project_id: Filter by project ID (optional)
    - agent_id: Filter by agent ID (optional)
    - memory_trace_id: Filter by memory trace ID (optional)
    
    Returns:
    - status: "success" if successful, "failure" if error occurred
    - logs: List of matching log entries
    - count: Number of matching log entries
    """
    try:
        # Filter logs based on query parameters
        filtered_logs = task_status_logs
        
        if task_id:
            filtered_logs = [log for log in filtered_logs if log["task_id"] == task_id]
        
        if project_id:
            filtered_logs = [log for log in filtered_logs if log["project_id"] == project_id]
        
        if agent_id:
            filtered_logs = [log for log in filtered_logs if log["agent_id"] == agent_id]
        
        if memory_trace_id:
            filtered_logs = [log for log in filtered_logs if log["memory_trace_id"] == memory_trace_id]
        
        # Log query
        logger.info(f"📊 Task status query returned {len(filtered_logs)} results")
        
        # Return response
        return {
            "status": "success",
            "logs": filtered_logs,
            "count": len(filtered_logs)
        }
    except Exception as e:
        # Log error
        logger.error(f"❌ Error querying task status: {str(e)}")
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "status": "failure",
                "logs": [],
                "count": 0,
                "error": str(e)
            }
        )
