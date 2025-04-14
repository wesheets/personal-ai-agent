"""
Project-scoped memory summarization endpoint for generating concise summaries of memory traces.

This module provides an endpoint to summarize memory entries filtered by project_id
and optional parameters like agent_id and memory_type.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import logging

from app.modules.memory_writer import write_memory, memory_store
from app.modules.memory_summarizer_project import summarize_project_memories

# Configure logging
logger = logging.getLogger("project_summary")

# Define the router
router = APIRouter()

# Define the input schema
class ProjectSummarizeRequest(BaseModel):
    project_id: str
    agent_id: Optional[str] = None
    memory_type: Optional[str] = None
    store_summary: Optional[bool] = False
    limit: Optional[int] = 50

@router.post("/project-summarize")
async def summarize_project_endpoint(request: Request):
    """
    Summarize memory entries filtered by project_id and optional parameters.
    
    This endpoint generates a concise summary of memory entries for a specific project,
    optionally filtered by agent_id and memory_type.
    
    Request body:
    - project_id: Project identifier for filtering memories (required)
    - agent_id: Optional agent identifier for filtering memories
    - memory_type: Optional memory type for filtering memories
    - store_summary: Whether to store the summary as a memory entry (default: false)
    - limit: Maximum number of memories to consider (default: 50)
    
    Returns:
    - status: "success" if successful, "failure" if error occurred
    - summary: Generated summary text
    - project_id: Project identifier (echoed from request)
    - memory_count: Number of memories summarized
    """
    try:
        # Parse request body
        body = await request.json()
        summarize_request = ProjectSummarizeRequest(**body)
        
        # Filter memories by project_id
        filtered_memories = [
            m for m in memory_store 
            if "project_id" in m and m["project_id"] == summarize_request.project_id
        ]
        
        # Apply agent_id filter if provided
        if summarize_request.agent_id:
            filtered_memories = [
                m for m in filtered_memories 
                if m["agent_id"] == summarize_request.agent_id
            ]
        
        # Apply memory_type filter if provided
        if summarize_request.memory_type:
            filtered_memories = [
                m for m in filtered_memories 
                if m["type"] == summarize_request.memory_type
            ]
        
        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        if summarize_request.limit and summarize_request.limit > 0:
            filtered_memories = filtered_memories[:summarize_request.limit]
        
        # Generate summary
        summary_result = summarize_project_memories(filtered_memories, summarize_request.project_id)
        
        # Store summary as a memory entry if requested
        if summarize_request.store_summary and filtered_memories:
            # Use the agent_id from the request or from the first memory
            agent_id = summarize_request.agent_id or filtered_memories[0]["agent_id"]
            
            memory = write_memory(
                agent_id=agent_id,
                type="project_summary",
                content=summary_result["summary"],
                tags=["project_summary", "compressed", summarize_request.project_id],
                project_id=summarize_request.project_id,
                status="completed"
            )
            
            # Add memory_id to the response
            summary_result["memory_id"] = memory["memory_id"]
        
        # Log successful summary generation
        logger.info(f"✅ Project summary generated for project {summarize_request.project_id} with {summary_result['memory_count']} memories")
        
        # Return structured response
        return {
            "status": "success",
            **summary_result
        }
    except Exception as e:
        # Log error details
        logger.error(f"❌ Project Summary error: {str(e)}")
        
        # Return error response
        return JSONResponse(status_code=500, content={
            "status": "failure",
            "summary": f"Error generating project summary: {str(e)}",
            "project_id": body.get("project_id", "unknown"),
            "memory_count": 0
        })
