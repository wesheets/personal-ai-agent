"""
Orchestrator Module for Agent Performance Auditing

This module provides endpoints for auditing agent performance by comparing
task plans with execution results. It enables self-evaluation for agents
by analyzing what they planned to do versus what they actually logged.

Key features:
- Comparing task_plan memories with task_result execution logs
- Generating audit summaries with success/failure statistics
- Supporting reflection learning and system trust
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Import the memory database for fetching memories
from app.db.memory_db import memory_db

# Configure logging
logger = logging.getLogger("api.modules.orchestrator")

# Initialize router
router = APIRouter()

@router.get("/audit")
async def audit_agent_performance(
    agent_id: str,
    limit: int = 5,
    task_group: Optional[str] = None
):
    """
    Audit agent performance by comparing task plans with execution results.
    
    This endpoint enables self-evaluation for agents by analyzing what they
    planned to do versus what they actually logged. It supports reflection
    learning, audit trails, and system trust.
    
    Parameters:
    - agent_id: Agent whose performance we're auditing (required)
    - limit: Maximum number of task plans to analyze, default is 5
    - task_group: Optional filter by metadata.task_group
    
    Returns:
    - status: "ok" if successful
    - agent_id: The agent that was audited
    - audit_summary: Statistics about task execution performance
    - task_report: Detailed report of each task with plan and result
    """
    try:
        logger.info(f"🔍 Auditing agent performance: agent_id={agent_id}, limit={limit}, task_group={task_group}")
        
        # Fetch latest task_plan memories for the given agent
        task_plans = memory_db.read_memories(
            agent_id=agent_id,
            memory_type="task_plan",
            limit=limit
        )
        
        # Filter by task_group if provided
        if task_group and task_plans:
            task_plans = [
                plan for plan in task_plans 
                if plan.get("metadata", {}).get("task_group") == task_group
            ]
        
        # Initialize counters for audit summary
        total_planned = len(task_plans)
        total_attempted = 0
        successes = 0
        failures = 0
        unattempted = 0
        
        # Initialize task report list
        task_report = []
        
        # Process each task plan
        for plan in task_plans:
            # Extract task_id from metadata or directly from task_id field
            # First try to get from metadata (new format)
            task_id = plan.get("metadata", {}).get("task_id")
            
            # If not found in metadata, try to get from top-level task_id field (old format)
            if not task_id:
                task_id = plan.get("task_id")
            
            if not task_id:
                logger.warning(f"⚠️ Task plan missing task_id in both metadata and top-level fields: {plan.get('memory_id')}")
                continue
            
            logger.info(f"🔍 Looking for task_result with task_id: {task_id}")
            
            # Look up matching task_result with same agent_id and task_id
            # First try direct query using task_id parameter
            task_results = memory_db.read_memories(
                agent_id=agent_id,
                memory_type="task_result",
                task_id=task_id,
                limit=1
            )
            
            # If no results found, try a broader search and filter manually
            if not task_results:
                logger.info(f"🔍 No direct match found, trying broader search for task_id: {task_id}")
                # Get all task results for this agent
                all_task_results = memory_db.read_memories(
                    agent_id=agent_id,
                    memory_type="task_result",
                    limit=10  # Reasonable limit to avoid performance issues
                )
                
                # Filter manually by checking metadata
                task_results = [
                    result for result in all_task_results
                    if (result.get("metadata", {}).get("task_id", "").lower() == task_id.lower() or 
                        (result.get("task_id") and result.get("task_id").lower() == task_id.lower()))
                ]
                
                # Take only the first result if multiple found
                if task_results:
                    task_results = [task_results[0]]
                    logger.info(f"✅ Found match in metadata for task_id: {task_id}")
                else:
                    logger.info(f"❌ No match found in broader search for task_id: {task_id}")
            else:
                logger.info(f"✅ Found direct match for task_id: {task_id}")
            
            # Determine status based on result
            status = "unattempted"
            result_content = None
            
            if task_results:
                total_attempted += 1
                result = task_results[0]
                result_content = result.get("content")
                
                # Classify the result
                if result.get("status") == "success":
                    status = "success"
                    successes += 1
                else:
                    status = "failure"
                    failures += 1
            else:
                unattempted += 1
            
            # Add to task report
            task_report.append({
                "task_id": task_id,
                "status": status,
                "planned_content": plan.get("content"),
                "result_content": result_content
            })
        
        # Create audit summary
        audit_summary = {
            "total_planned": total_planned,
            "total_attempted": total_attempted,
            "successes": successes,
            "failures": failures,
            "unattempted": unattempted
        }
        
        # Return the complete audit report
        return {
            "status": "ok",
            "agent_id": agent_id,
            "audit_summary": audit_summary,
            "task_report": task_report
        }
    
    except Exception as e:
        logger.error(f"❌ Error auditing agent performance: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error auditing agent performance: {str(e)}"
            }
        )
