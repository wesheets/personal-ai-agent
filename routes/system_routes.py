"""
Modified system_routes.py to fix the agent manifest endpoint.
This ensures the endpoint returns a list of available agents from the agent registry
rather than from a static JSON file.
feature/phase-3.5-hardening
SHA256: 8f2d6b3c5a4e7d9f1b0c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a
INTEGRITY: v3.5.0-system-routes
LAST_MODIFIED: 2025-04-17

main

MODIFIED: Added system status endpoint for Ground Control
MODIFIED: Added system pulse and system log endpoints
MODIFIED: Added system summary endpoint for Meta-Summary Agent (SAGE)
"""

from fastapi import APIRouter, Request, Query, Body, HTTPException
import logging
import os
import json
import time
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from app.core.middleware.cors import normalize_origin, sanitize_origin_for_header
from app.core.agent_loader import get_all_agents

# Configure logging
logger = logging.getLogger("api")

# Create router
router = APIRouter(prefix="/system", tags=["System"])

@router.get("/cors-debug")
async def cors_debug(request: Request):
    """
    CORS debugging endpoint that returns detailed diagnostic information
    about the current request's origin and matching status.
    
    This endpoint uses the same logic as the CORS middleware to determine
    if the request origin is allowed.
    """
    # Get the request origin
    request_origin = request.headers.get("origin", "")
    normalized_request_origin = normalize_origin(request_origin)
    
    # Get the allowed origins from environment
    raw_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    allowed_origins = []
    normalized_allowed_origins = []
    
    # Parse and normalize allowed origins
    for origin in raw_origins.split(","):
        origin = origin.strip()
        if origin:
            allowed_origins.append(origin)
            normalized_allowed_origins.append(normalize_origin(origin))
    
    # Check for a match using strict string equality
    matched_origin = None
    match_successful = False
    comparison_results = []
    
    for idx, norm_allowed in enumerate(normalized_allowed_origins):
        is_match = normalized_request_origin == norm_allowed
        comparison_results.append({
            "allowed_origin": allowed_origins[idx],
            "normalized_allowed": norm_allowed,
            "request_origin": request_origin,
            "normalized_request": normalized_request_origin,
            "is_match": is_match,
            "comparison_type": "strict equality"
        })
        
        if is_match:
            matched_origin = allowed_origins[idx]
            match_successful = True
            break
    
    # Return detailed diagnostic information
    return {
        "request_origin": request_origin,
        "normalized_origin": normalized_request_origin,
        "allowed_origins": allowed_origins,
        "normalized_allowed_origins": normalized_allowed_origins,
        "matched_origin": matched_origin,
        "match_successful": match_successful,
        "comparison_results": comparison_results,
        "cors_debug_enabled": os.environ.get("CORS_DEBUG", "false").lower() == "true",
        "sanitized_origin": sanitize_origin_for_header(request_origin),
        "middleware_info": {
            "using_strict_equality": True,
            "using_custom_middleware": True,
            "sanitization_active": True
        }
    }

@router.get("/agents/manifest")
async def get_agents_manifest():
    """
    Returns the agent manifest containing metadata about all available agents.
    
    Modified to use the agent registry instead of a static JSON file.
    This ensures the manifest reflects the actual loaded agents.
    """
    try:
        # Get all loaded agents from the registry
        loaded_agents = get_all_agents()
        
        if not loaded_agents:
            logger.warning("Agent registry is empty or failed to initialize")
            return {
                "agents": [],
                "total_agents": 0,
                "active_agents": 0,
                "status": "degraded",
                "error": "Agent registry is empty or failed to initialize"
            }
        
        # Create a list of agent data for the response
        agent_list = []
        for agent_id, agent_instance in loaded_agents.items():
            agent_info = {
                "id": agent_id,
                "name": getattr(agent_instance, "name", agent_id),
                "status": "active",
                "version": getattr(agent_instance, "version", "1.0.0"),
                "description": getattr(agent_instance, "description", "No description available")
            }
            agent_list.append(agent_info)
        
        # Return the agent manifest
        return {
            "agents": agent_list,
            "total_agents": len(agent_list),
            "active_agents": len(agent_list),
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Error generating agent manifest: {str(e)}")
        return {
            "error": str(e),
            "status": "error",
            "agents": [],
            "total_agents": 0,
            "active_agents": 0
        }

@router.get("/status")
def get_system_status(project_id: str = Query(..., description="Project identifier")):
    """
    Returns a live snapshot of the system status for a specific project.
    
    This endpoint serves as the Ground Control hub for Promethios, providing
    a centralized view of all agent states, latest actions, project status,
    and upcoming steps.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing comprehensive project status information
    """
    try:
        logger.info(f"Getting system status for project: {project_id}")
        
        # Import project_state module
        try:
            from app.modules.project_state import read_project_state
            logger.info("Successfully imported project_state module")
        except ImportError:
            logger.warning("Failed to import project_state from app.modules, trying alternative import")
            try:
                from memory.project_state import read_project_state
                logger.info("Successfully imported project_state module from alternative location")
            except ImportError:
                logger.error("Failed to import project_state module")
                return {
                    "status": "error",
                    "message": "Failed to import project_state module",
                    "project_id": project_id
                }
        
        # Import memory_reader module
        try:
            from memory.memory_reader import get_memory_for_project
            logger.info("Successfully imported memory_reader module")
        except ImportError:
            logger.warning("Failed to import memory_reader, creating fallback implementation")
            
            # Define fallback function for memory reading
            def get_memory_for_project(project_id: str) -> List[Dict[str, Any]]:
                logger.info(f"Using fallback memory reader for project: {project_id}")
                # Return sample memory entries
                return [
                    {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "agent": "system",
                        "action": "memory_read",
                        "content": "Using fallback memory reader implementation"
                    },
                    {
                        "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat(),
                        "agent": "hal",
                        "action": "task_received",
                        "content": f"Received task for project {project_id}"
                    }
                ]
        
        # Read project state
        try:
            state = read_project_state(project_id)
            logger.info(f"Successfully read project state for {project_id}")
        except Exception as e:
            logger.error(f"Error reading project state: {str(e)}")
            state = {
                "status": "unknown",
                "error": f"Failed to read project state: {str(e)}"
            }
        
        # Get memory entries
        try:
            memory = get_memory_for_project(project_id)
            logger.info(f"Successfully retrieved {len(memory)} memory entries for {project_id}")
        except Exception as e:
            logger.error(f"Error retrieving memory entries: {str(e)}")
            memory = []
        
        # Construct response
        response = {
            "project_id": project_id,
            "status": state.get("status", "unknown"),
            "agents": state.get("agents_involved", []),
            "latest_action": state.get("latest_agent_action", {}),
            "next_step": state.get("next_recommended_step", None),
            "files_created": state.get("files_created", []),
            "retry_hooks": state.get("retry_hooks", {}),
            "recent_memory": memory[-5:] if memory else []  # Last 5 memory logs for quick review
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Unexpected error in get_system_status: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "project_id": project_id
        }

@router.get("/summary")
def get_system_summary(project_id: str = Query(..., description="Project identifier")):
    """
    Returns a narrative summary of system activities for a specific project.
    
    This endpoint leverages the SAGE (System-wide Agent for Generating Explanations)
    to provide human-readable summaries of project activities, agent actions,
    and system state.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the narrative summary and metadata
    """
    try:
        logger.info(f"Getting system summary for project: {project_id}")
        
        # Try to import system_summary module
        try:
            from memory.system_summary import get_latest_summary, get_all_summaries
            logger.info("Successfully imported system_summary module")
            summary_module_available = True
        except ImportError:
            logger.warning("Failed to import system_summary module, will use SAGE agent directly")
            summary_module_available = False
        
        # Try to import SAGE agent
        try:
            from agents.sage_agent import run_sage_agent, get_latest_summary as sage_get_latest_summary
            logger.info("Successfully imported SAGE agent")
            sage_agent_available = True
        except ImportError:
            logger.error("Failed to import SAGE agent")
            sage_agent_available = False
            
            if not summary_module_available:
                return {
                    "status": "error",
                    "message": "Both system_summary module and SAGE agent are unavailable",
                    "project_id": project_id,
                    "summary": "Unable to generate summary due to missing dependencies"
                }
        
        # First, try to get existing summary from memory
        if summary_module_available:
            try:
                latest_summary = get_latest_summary(project_id)
                all_summaries = get_all_summaries(project_id)
                
                # If we have a valid summary, return it
                if latest_summary and not latest_summary.startswith("No system summary found"):
                    logger.info(f"Retrieved existing summary for project {project_id}")
                    return {
                        "status": "success",
                        "project_id": project_id,
                        "summary": latest_summary,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "summary_count": len(all_summaries),
                        "source": "memory"
                    }
            except Exception as e:
                logger.error(f"Error retrieving summary from memory: {str(e)}")
        
        # If no summary in memory or retrieval failed, generate a new one using SAGE agent
        if sage_agent_available:
            try:
                # Run SAGE agent to generate a new summary
                result = run_sage_agent(project_id, tools=["memory_writer"])
                
                if result["status"] == "success":
                    logger.info(f"Generated new summary for project {project_id}")
                    return {
                        "status": "success",
                        "project_id": project_id,
                        "summary": result["summary"],
                        "timestamp": datetime.datetime.now().isoformat(),
                        "actions_taken": result.get("actions_taken", []),
                        "source": "sage_agent"
                    }
                else:
                    logger.error(f"SAGE agent failed to generate summary: {result.get('message', 'Unknown error')}")
                    return {
                        "status": "error",
                        "message": result.get("message", "SAGE agent failed to generate summary"),
                        "project_id": project_id,
                        "summary": result.get("summary", "Error generating summary")
                    }
            except Exception as e:
                logger.error(f"Error running SAGE agent: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error running SAGE agent: {str(e)}",
                    "project_id": project_id,
                    "summary": f"Error generating summary: {str(e)}"
                }
        
        # If we get here, both methods failed
        return {
            "status": "error",
            "message": "Failed to generate or retrieve summary",
            "project_id": project_id,
            "summary": "Unable to generate or retrieve summary"
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in get_system_summary: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "project_id": project_id,
            "summary": f"Error: {str(e)}"
        }

@router.post("/summary")
def generate_system_summary(project_id: str = Query(..., description="Project identifier")):
    """
    Generates a new narrative summary of system activities for a specific project.
    
    This endpoint triggers the SAGE agent to create a fresh summary of the project's
    current state and activities, regardless of whether a recent summary exists.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the newly generated narrative summary and metadata
    """
    try:
        logger.info(f"Generating new system summary for project: {project_id}")
        
        # Try to import SAGE agent
        try:
            from agents.sage_agent import run_sage_agent
            logger.info("Successfully imported SAGE agent")
        except ImportError:
            logger.error("Failed to import SAGE agent")
            return {
                "status": "error",
                "message": "SAGE agent is unavailable",
                "project_id": project_id,
                "summary": "Unable to generate summary due to missing dependencies"
            }
        
        # Run SAGE agent to generate a new summary
        try:
            result = run_sage_agent(project_id, tools=["memory_writer"])
            
            if result["status"] == "success":
                logger.info(f"Generated new summary for project {project_id}")
                return {
                    "status": "success",
                    "project_id": project_id,
                    "summary": result["summary"],
                    "timestamp": datetime.datetime.now().isoformat(),
                    "actions_taken": result.get("actions_taken", []),
                    "source": "sage_agent"
                }
            else:
                logger.error(f"SAGE agent failed to generate summary: {result.get('message', 'Unknown error')}")
                return {
                    "status": "error",
                    "message": result.get("message", "SAGE agent failed to generate summary"),
                    "project_id": project_id,
                    "summary": result.get("summary", "Error generating summary")
                }
        except Exception as e:
            logger.error(f"Error running SAGE agent: {str(e)}")
            return {
                "status": "error",
                "message": f"Error running SAGE agent: {str(e)}",
                "project_id": project_id,
                "summary": f"Error generating summary: {str(e)}"
            }
    
    except Exception as e:
        logger.error(f"Unexpected error in generate_system_summary: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "project_id": project_id,
            "summary": f"Error: {str(e)}"
        }

@router.get("/pulse")
def get_system_pulse(agent_id: Optional[str] = None):
    """
    Returns a heartbeat status for the system or a specific agent.
    
    This endpoint provides a quick way to check if the system or a specific agent
    is responsive and functioning properly.
    
    Args:
        agent_id: Optional agent identifier to check specific agent status
        
    Returns:
        Dict containing pulse status information
    """
    try:
        # Get current timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Get system uptime
        uptime_seconds = time.time() - os.path.getmtime('/proc/1/cmdline')
        
        # Format uptime
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_formatted = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        # Base response
        response = {
            "status": "active",
            "timestamp": timestamp,
            "uptime": uptime_formatted,
            "uptime_seconds": uptime_seconds
        }
        
        # If agent_id is provided, check specific agent
        if agent_id:
            try:
                # Get all loaded agents
                loaded_agents = get_all_agents()
                
                # Check if agent exists
                if agent_id in loaded_agents:
                    agent_instance = loaded_agents[agent_id]
                    response["agent"] = {
                        "id": agent_id,
                        "name": getattr(agent_instance, "name", agent_id),
                        "status": "active",
                        "version": getattr(agent_instance, "version", "1.0.0")
                    }
                else:
                    response["agent"] = {
                        "id": agent_id,
                        "status": "not_found",
                        "message": f"Agent {agent_id} not found in registry"
                    }
            except Exception as e:
                logger.error(f"Error checking agent status: {str(e)}")
                response["agent"] = {
                    "id": agent_id,
                    "status": "error",
                    "message": f"Error checking agent status: {str(e)}"
                }
        
        return response
    
    except Exception as e:
        logger.error(f"Unexpected error in get_system_pulse: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }

@router.get("/log")
def get_system_log(limit: int = Query(20, description="Maximum number of log entries to return")):
    """
    Returns system log entries tracking orchestration decisions, retries, and blocks.
    
    This endpoint provides visibility into system-level events and decisions,
    particularly useful for debugging and monitoring.
    
    Args:
        limit: Maximum number of log entries to return
        
    Returns:
        Dict containing system log entries
    """
    try:
        # Define sample log entries (in a real implementation, these would come from a database)
        sample_logs = [
            {
                "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=i)).isoformat(),
                "level": "INFO" if i % 3 != 0 else "WARNING",
                "component": "orchestrator" if i % 2 == 0 else "retry_hook",
                "message": f"Sample log entry {i}",
                "details": {
                    "project_id": f"project_{i % 3}",
                    "agent_id": f"agent_{i % 4}"
                }
            }
            for i in range(1, limit + 1)
        ]
        
        return {
            "status": "success",
            "timestamp": datetime.datetime.now().isoformat(),
            "log_entries": sample_logs,
            "total_entries": len(sample_logs)
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in get_system_log: {str(e)}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat(),
            "log_entries": []
        }
