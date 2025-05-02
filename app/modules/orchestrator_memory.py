"""
Orchestrator Memory Module

This module provides memory operations specifically for the orchestrator component,
allowing it to log loop events, store beliefs, and maintain a history of system interactions.
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Import memory utilities
from app.memory.project_memory import PROJECT_MEMORY
from app.api.modules.memory import write_memory, read_memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def log_loop_event(
    loop_id: str,
    project_id: str,
    agent: str,
    task: str,
    result_tag: Optional[str] = None,
    status: str = "completed",
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Log a loop event to orchestrator memory.
    
    Args:
        loop_id: Unique identifier for the loop
        project_id: Project identifier
        agent: Agent that performed the action
        task: Description of the task
        result_tag: Optional memory tag where result is stored
        status: Status of the event (e.g., "completed", "failed", "in_progress")
        additional_data: Any additional data to include in the log
        
    Returns:
        Dict containing the status of the memory write operation
    """
    try:
        # Create the log entry
        log_data = {
            "loop_id": loop_id,
            "project_id": project_id,
            "agent": agent,
            "task": task,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add result tag if provided
        if result_tag:
            log_data["result_tag"] = result_tag
            
        # Add any additional data
        if additional_data:
            log_data.update(additional_data)
            
        # Get existing log entries
        existing_log = await get_loop_log(project_id)
        
        # Append new entry to existing log
        if existing_log and "entries" in existing_log:
            existing_log["entries"].append(log_data)
            updated_log = existing_log
        else:
            # Create new log if none exists
            updated_log = {
                "entries": [log_data],
                "last_updated": datetime.utcnow().isoformat()
            }
            
        # Write updated log to memory
        result = await write_memory(
            agent_id="orchestrator",
            memory_type="loop",
            tag="orchestrator_loop_log",
            value=updated_log,
            project_id=project_id
        )
        
        logger.info(f"Logged loop event for {loop_id} in project {project_id}: {agent} {status} {task}")
        return {
            "status": "success",
            "message": "Loop event logged successfully",
            "log_entry": log_data
        }
        
    except Exception as e:
        logger.error(f"Error logging loop event: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to log loop event: {str(e)}",
            "error": str(e)
        }

async def get_loop_log(project_id: str) -> Dict[str, Any]:
    """
    Retrieve the loop event log for a specific project.
    
    Args:
        project_id: Project identifier
        
    Returns:
        Dict containing the loop event log
    """
    try:
        # Read the log from memory
        result = await read_memory(
            agent_id="orchestrator",
            memory_type="loop",
            tag="orchestrator_loop_log",
            project_id=project_id
        )
        
        # Return the log if it exists
        if result and "value" in result:
            return result["value"]
        else:
            # Return empty log if none exists
            return {
                "entries": [],
                "last_updated": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error retrieving loop log: {str(e)}")
        # Return empty log on error
        return {
            "entries": [],
            "last_updated": datetime.utcnow().isoformat(),
            "error": str(e)
        }

async def store_belief(
    project_id: str,
    belief: str,
    confidence: float = 0.8,
    evidence: Optional[List[str]] = None,
    category: str = "agent_performance"
) -> Dict[str, Any]:
    """
    Store an orchestrator belief in memory.
    
    Args:
        project_id: Project identifier
        belief: The belief statement
        confidence: Confidence level (0.0 to 1.0)
        evidence: List of evidence supporting the belief
        category: Category of the belief
        
    Returns:
        Dict containing the status of the memory write operation
    """
    try:
        # Create the belief entry
        belief_data = {
            "statement": belief,
            "confidence": confidence,
            "category": category,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add evidence if provided
        if evidence:
            belief_data["evidence"] = evidence
            
        # Get existing beliefs
        existing_beliefs = await get_beliefs(project_id)
        
        # Check if this belief already exists
        belief_exists = False
        for i, existing_belief in enumerate(existing_beliefs):
            if existing_belief.get("statement") == belief and existing_belief.get("category") == category:
                # Update existing belief
                existing_beliefs[i] = belief_data
                belief_exists = True
                break
                
        # Add new belief if it doesn't exist
        if not belief_exists:
            existing_beliefs.append(belief_data)
            
        # Write updated beliefs to memory
        result = await write_memory(
            agent_id="orchestrator",
            memory_type="state",
            tag="beliefs",
            value=existing_beliefs,
            project_id=project_id
        )
        
        logger.info(f"Stored belief for project {project_id}: {belief}")
        return {
            "status": "success",
            "message": "Belief stored successfully",
            "belief": belief_data
        }
        
    except Exception as e:
        logger.error(f"Error storing belief: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to store belief: {str(e)}",
            "error": str(e)
        }

async def get_beliefs(project_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve orchestrator beliefs from memory.
    
    Args:
        project_id: Project identifier
        category: Optional category filter
        
    Returns:
        List of belief entries
    """
    try:
        # Read beliefs from memory
        result = await read_memory(
            agent_id="orchestrator",
            memory_type="state",
            tag="beliefs",
            project_id=project_id
        )
        
        # Return beliefs if they exist
        if result and "value" in result:
            beliefs = result["value"]
            
            # Filter by category if specified
            if category and isinstance(beliefs, list):
                beliefs = [b for b in beliefs if b.get("category") == category]
                
            return beliefs
        else:
            # Return empty list if no beliefs exist
            return []
            
    except Exception as e:
        logger.error(f"Error retrieving beliefs: {str(e)}")
        # Return empty list on error
        return []

async def get_latest_loop_events(project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the most recent loop events for a project.
    
    Args:
        project_id: Project identifier
        limit: Maximum number of events to return
        
    Returns:
        List of recent loop events
    """
    try:
        # Get the full loop log
        log = await get_loop_log(project_id)
        
        # Extract entries
        entries = log.get("entries", [])
        
        # Sort by timestamp (newest first)
        sorted_entries = sorted(
            entries,
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        
        # Return limited number of entries
        return sorted_entries[:limit]
        
    except Exception as e:
        logger.error(f"Error retrieving latest loop events: {str(e)}")
        return []

async def get_agent_activity_summary(project_id: str) -> Dict[str, Any]:
    """
    Generate a summary of agent activities for a project.
    
    Args:
        project_id: Project identifier
        
    Returns:
        Dict containing agent activity summary
    """
    try:
        # Get the full loop log
        log = await get_loop_log(project_id)
        
        # Extract entries
        entries = log.get("entries", [])
        
        # Initialize summary
        summary = {
            "total_events": len(entries),
            "agents": {},
            "latest_event": None,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Process entries
        for entry in entries:
            agent = entry.get("agent")
            status = entry.get("status")
            
            # Initialize agent data if not exists
            if agent not in summary["agents"]:
                summary["agents"][agent] = {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "in_progress_tasks": 0,
                    "latest_task": None
                }
                
            # Update agent statistics
            summary["agents"][agent]["total_tasks"] += 1
            
            if status == "completed":
                summary["agents"][agent]["completed_tasks"] += 1
            elif status == "failed":
                summary["agents"][agent]["failed_tasks"] += 1
            elif status == "in_progress":
                summary["agents"][agent]["in_progress_tasks"] += 1
                
            # Update latest task for agent
            if not summary["agents"][agent]["latest_task"] or entry.get("timestamp", "") > summary["agents"][agent]["latest_task"].get("timestamp", ""):
                summary["agents"][agent]["latest_task"] = entry
                
            # Update latest event overall
            if not summary["latest_event"] or entry.get("timestamp", "") > summary["latest_event"].get("timestamp", ""):
                summary["latest_event"] = entry
                
        return summary
        
    except Exception as e:
        logger.error(f"Error generating agent activity summary: {str(e)}")
        return {
            "total_events": 0,
            "agents": {},
            "latest_event": None,
            "generated_at": datetime.utcnow().isoformat(),
            "error": str(e)
        }
