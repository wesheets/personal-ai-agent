"""
API routes for accessing system logs
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from app.core.logging_manager import get_logging_manager, LogEntry
from pydantic import BaseModel

# Create router
router = APIRouter()

class LogsResponse(BaseModel):
    """Response model for logs endpoint"""
    logs: List[LogEntry]
    count: int
    metadata: Dict[str, Any]

@router.get("/latest", response_model=LogsResponse)
async def get_latest_logs(
    limit: Optional[int] = Query(20, ge=1, le=100, description="Maximum number of logs to return")
):
    """
    Get the latest API request/response logs
    
    This endpoint returns the most recent API logs, including request and response details,
    processing time, and any errors that occurred. Sensitive information is automatically redacted.
    
    Args:
        limit: Maximum number of logs to return (default: 20, max: 100)
        
    Returns:
        List of log entries and metadata
    """
    try:
        # Get logging manager
        logging_manager = get_logging_manager()
        
        # Get latest logs
        logs = logging_manager.get_latest_logs(limit=limit)
        
        # Return response
        return LogsResponse(
            logs=logs,
            count=len(logs),
            metadata={
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving logs: {str(e)}")

# Export router
logs_router = router
