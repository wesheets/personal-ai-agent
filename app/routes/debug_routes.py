"""
Debug Routes Module

This module defines the routes for the Debug Analyzer agent, which acts as a diagnostic tool
for analyzing failed or incomplete loop executions within the Promethios architecture.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional

# Import schemas
from app.schemas.debug_schema import LoopDebugRequest, LoopDebugResult

# Import agent
from app.agents.debug_analyzer_agent import DebugAnalyzerAgent

# Create router
router = APIRouter(tags=["debug"])

# Initialize agent
debug_analyzer = DebugAnalyzerAgent()

@router.post("/debug/analyze-loop", response_model=LoopDebugResult)
async def analyze_loop(request: LoopDebugRequest):
    """
    Analyze a failed or incomplete loop execution.
    
    This endpoint accepts a loop_id and project_id, scans system memory and logs,
    and returns a structured diagnosis of what failed, why it failed, which agent
    was responsible, what memory tags were involved, and what repair or rerun is
    recommended.
    
    Args:
        request: The debug request containing loop_id, project_id, and optional filters
        
    Returns:
        LoopDebugResult containing the diagnosis of the loop execution
    """
    try:
        # Call the Debug Analyzer agent
        result = await debug_analyzer.analyze_loop(request)
        return result
    except Exception as e:
        # Handle exceptions and return appropriate error response
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing loop: {str(e)}"
        )
