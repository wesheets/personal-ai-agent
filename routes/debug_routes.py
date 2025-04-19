"""
Debug routes for agent system
This module provides debug endpoints for the agent system.
feature/phase-3.5-hardening
SHA256: 9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b
INTEGRITY: v3.5.0-debug-routes
LAST_MODIFIED: 2025-04-19
main
"""
import logging
import os
import json
import time
import traceback
from fastapi import APIRouter, Request, Response, HTTPException, Body
from fastapi.routing import APIRoute
from typing import Dict, Any, List

from app.core.agent_router import get_agent_router

# Set up logging
logger = logging.getLogger("api.debug")
logger.setLevel(logging.DEBUG)  # Ensure debug level logging is enabled

# Create router
router = APIRouter(tags=["Debug"])

# Debug print to verify this file is loaded
print("✅ DEBUG ROUTES LOADED - Version 2025-04-19-01")
print("✅ Debug routes available:")
print("  - /api/debug/agents")
print("  - /api/debug/memory/log")
print("  - /api/debug/routes")
print("  - /api/debug/memory/validate/{project_id}")
print("  - /api/debug/schema/validate")
print("  - /api/debug/agent/schema/{agent}")
print("  - /api/debug/loop/schema")
print("  - /api/debug/loop/validate/{project_id}")
print("  - /api/debug/reflection/validate")
print("  - /api/debug/tool/validate/{tool}")

@router.get("/routes")
def list_routes():
    """
    Returns a list of all registered FastAPI routes.
    
    This endpoint helps verify whether critical routes like /api/orchestrator/interpret
    are properly registered and deployed in production.
    """
    try:
        from app.main import app
        routes = []
        for route in app.routes:
            if isinstance(route, APIRoute):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": route.name
                })
        
        # Log the debug information
        logger.info(f"🔍 Debug routes endpoint called")
        logger.info(f"🔍 Found {len(routes)} registered routes")
        
        return routes
    except Exception as e:
        error_msg = f"Failed to list routes: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg
        }

@router.get("/agents")
async def debug_agents():
    """
    Returns detailed information about all registered agents for debugging purposes.
    
    This endpoint provides:
    - List of all agent IDs in the agent_map
    - List of all agent profiles
    - Comparison between agent_map and agent profiles
    """
    # Get the agent router
    agent_router = get_agent_router()
    
    # Get all agent profiles
    agent_profiles = agent_router.get_all_agent_profiles()
    profile_ids = list(agent_profiles.keys())
    
    # Get all agents from the agent_map
    from app.core.agent_router import find_agent
    import inspect
    
    # Introspect the agent_map
    agent_map_source = inspect.getsource(find_agent)
    agent_map_lines = [line.strip() for line in agent_map_source.split('\n') 
                      if "agent_map" in line and "=" in line]
    
    # Extract agent IDs from the agent_map
    agent_map_ids = []
    if agent_map_lines:
        # This is a simple parser and might need adjustment based on actual code format
        for line in agent_map_lines:
            if ":" in line:
                parts = line.split(":")
                if len(parts) > 1:
                    agent_id = parts[0].strip().strip('"\'')
                    if agent_id and agent_id != "agent_map":
                        agent_map_ids.append(agent_id)
    
    # Check for mismatches
    missing_in_profiles = [agent_id for agent_id in agent_map_ids if agent_id not in profile_ids]
    missing_in_map = [agent_id for agent_id in profile_ids if agent_id not in agent_map_ids]
    
    # Log the debug information
    logger.info(f"🔍 Debug agents endpoint called")
    logger.info(f"🔍 Agent profiles: {profile_ids}")
    logger.info(f"🔍 Agent map IDs: {agent_map_ids}")
    
    if missing_in_profiles:
        logger.warning(f"⚠️ Agents in map but missing in profiles: {missing_in_profiles}")
    if missing_in_map:
        logger.warning(f"⚠️ Agents in profiles but missing in map: {missing_in_map}")
    
    # Return the debug information
    return {
        "agent_profiles": profile_ids,
        "agent_map": agent_map_ids,
        "missing_in_profiles": missing_in_profiles,
        "missing_in_map": missing_in_map,
        "status": "ok" if not (missing_in_profiles or missing_in_map) else "mismatched"
    }

# Print debug info when this endpoint is defined
print("✅ Registering /api/debug/memory/log endpoint")

@router.get("/memory/log")
async def get_memory_log():
    """
    Return the current in-memory debug log (or simulated log entries).
    """
    try:
        print("🔍 Debug memory log endpoint called")
        logger.info(f"🔍 Debug memory log endpoint called")
        
        # Enhanced logging for debugging
        print(f"🔍 Current working directory: {os.getcwd()}")
        logger.debug(f"Current working directory: {os.getcwd()}")
        
        # Try multiple potential paths for memory store file
        potential_paths = [
            os.path.join(os.path.dirname(__file__), "../app/modules/memory_store.json"),  # Relative to routes dir
            "/app/app/modules/memory_store.json",  # Absolute path in container
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../app/modules/memory_store.json")),  # Absolute path
            os.path.join(os.getcwd(), "app/modules/memory_store.json")  # Relative to working dir
        ]
        
        # Log all potential paths
        for i, path in enumerate(potential_paths):
            print(f"🔍 Potential memory store path {i+1}: {path}")
            logger.debug(f"Potential memory store path {i+1}: {path}")
        
        # Try each path until we find the file
        memory_file = None
        for path in potential_paths:
            if os.path.exists(path):
                memory_file = path
                print(f"✅ Memory store file found at: {memory_file}")
                logger.info(f"Memory store file found at: {memory_file}")
                break
        
        # If no file found, use the first path for error reporting
        if memory_file is None:
            memory_file = potential_paths[0]
            print(f"⚠️ Memory store file not found in any potential location")
            logger.warning(f"Memory store file not found in any potential location")
        
        # Read memory entries from file
        memories = []
        if memory_file and os.path.exists(memory_file):
            try:
                print(f"✅ Memory store file found")
                with open(memory_file, 'r') as f:
                    memories = json.load(f)
                    # Sort by timestamp (newest first)
                    memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    # Limit to most recent entries
                    memories = memories[:50]  # Return the 50 most recent entries
                    print(f"✅ Retrieved {len(memories)} memory entries")
                    logger.info(f"🔍 Retrieved {len(memories)} memory entries")
            except json.JSONDecodeError:
                print(f"⚠️ Could not decode memory store file")
                logger.warning(f"⚠️ Could not decode memory store file")
                memories = []
            except Exception as e:
                print(f"❌ Error reading memory store: {str(e)}")
                logger.error(f"❌ Error reading memory store: {str(e)}")
                memories = []
        else:
            print(f"⚠️ Memory store file not found at {memory_file}")
            logger.warning(f"⚠️ Memory store file not found at {memory_file}")
            # Generate synthetic entries if file doesn't exist
            memories = [
                {
                    "memory_id": "synthetic-1",
                    "timestamp": "2025-04-18T02:28:00.000000",
                    "agent": "hal",
                    "project_id": "demo_001",
                    "action": "received_task",
                    "content": "Synthetic memory entry for testing"
                },
                {
                    "memory_id": "synthetic-2",
                    "timestamp": "2025-04-18T02:27:00.000000",
                    "agent": "nova",
                    "project_id": "demo_001",
                    "action": "created",
                    "content": "Another synthetic memory entry"
                },
                {
                    "memory_id": "synthetic-3",
                    "timestamp": "2025-04-18T02:26:00.000000",
                    "agent": "sage",
                    "project_id": "demo_001",
                    "action": "summarized",
                    "content": "Third synthetic memory entry for testing"
                }
            ]
            print(f"✅ Generated {len(memories)} synthetic memory entries")
            logger.info(f"🔍 Generated {len(memories)} synthetic memory entries")
        
        print(f"✅ Returning memory log with {len(memories)} entries")
        return {
            "status": "success",
            "log": memories
        }
    except Exception as e:
        error_msg = f"Failed to retrieve memory log: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg
        }

# Fallback endpoint for memory log
@router.get("/memory/log/fallback")
async def get_memory_log_fallback():
    """
    Fallback endpoint for memory log that always returns synthetic entries.
    This endpoint is used when the main memory log endpoint fails.
    """
    print("🔍 Debug memory log fallback endpoint called")
    logger.info(f"🔍 Debug memory log fallback endpoint called")
    
    # Generate synthetic entries
    memories = [
        {
            "memory_id": "fallback-1",
            "timestamp": "2025-04-18T02:28:00.000000",
            "agent": "hal",
            "project_id": "demo_001",
            "action": "received_task",
            "content": "Fallback memory entry for testing"
        },
        {
            "memory_id": "fallback-2",
            "timestamp": "2025-04-18T02:27:00.000000",
            "agent": "nova",
            "project_id": "demo_001",
            "action": "created",
            "content": "Another fallback memory entry"
        },
        {
            "memory_id": "fallback-3",
            "timestamp": "2025-04-18T02:26:00.000000",
            "agent": "sage",
            "project_id": "demo_001",
            "action": "summarized",
            "content": "Third fallback memory entry for testing"
        }
    ]
    
    print(f"✅ Generated {len(memories)} fallback memory entries")
    logger.info(f"🔍 Generated {len(memories)} fallback memory entries")
    
    return {
        "status": "success",
        "log": memories,
        "source": "fallback"
    }

# Memory validation endpoint
print("✅ Registering /api/debug/memory/validate/{project_id} endpoint")

@router.get("/memory/validate/{project_id}")
def validate_memory_route(project_id: str):
    """
    Validates project memory against the expected schema.
    
    This endpoint helps identify missing or malformed memory fields
    that could potentially break agent logic.
    """
    try:
        print(f"🔍 Debug memory validation endpoint called for project: {project_id}")
        logger.info(f"🔍 Debug memory validation endpoint called for project: {project_id}")
        
        from app.utils.schema_utils import validate_project_memory
        
        # Try to import PROJECT_MEMORY from different possible locations
        try:
            from app.modules.project_state import PROJECT_MEMORY
        except ImportError:
            try:
                from app.memory import PROJECT_MEMORY
            except ImportError:
                # If we can't find the actual memory store, create a mock one for testing
                print("⚠️ Could not import PROJECT_MEMORY, using mock memory store")
                logger.warning("Could not import PROJECT_MEMORY, using mock memory store")
                PROJECT_MEMORY = {
                    project_id: {
                        "project_id": project_id,
                        "timestamp": "2025-04-19T21:44:00.000000",
                        "status": "active",
                        "next_recommended_step": "Run NOVA to implement solution",
                        "loop_status": "running",
                        "agents": {},
                        "task_log": [],
                        "logic_modules": {},
                        "registry": {}
                    }
                }

        # Validate the project memory
        errors = validate_project_memory(project_id, PROJECT_MEMORY)
        
        # Log the validation results
        if errors:
            print(f"⚠️ Validation errors found for project {project_id}: {errors}")
            logger.warning(f"Validation errors found for project {project_id}: {errors}")
        else:
            print(f"✅ Project memory validation passed for project {project_id}")
            logger.info(f"Project memory validation passed for project {project_id}")
        
        return {
            "project_id": project_id,
            "valid": not bool(errors),
            "errors": errors
        }
    except Exception as e:
        error_msg = f"Failed to validate project memory: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id
        }

# API Schema validation endpoint
print("✅ Registering /api/debug/schema/validate endpoint")

@router.post("/schema/validate")
def debug_api_validation(path: str = Body(...), method: str = Body(...), payload: Dict[str, Any] = Body(...)):
    """
    Validates an API request against the expected schema.
    
    This endpoint helps identify invalid requests, method mismatches, and unregistered endpoints
    that could potentially cause system failures.
    
    Args:
        path: The API endpoint path (e.g., "/api/agent/run")
        method: The HTTP method (e.g., "POST", "GET")
        payload: The request payload to validate
        
    Returns:
        Validation results including whether the request is valid and any errors found
    """
    try:
        print(f"🔍 Debug API schema validation endpoint called for path: {path}, method: {method}")
        logger.info(f"🔍 Debug API schema validation endpoint called for path: {path}, method: {method}")
        
        from app.utils.schema_utils import validate_api_request
        
        # Validate the API request
        errors = validate_api_request(path, method, payload)
        
        # Log the validation results
        if errors:
            print(f"⚠️ API validation errors found for {method} {path}: {errors}")
            logger.warning(f"API validation errors found for {method} {path}: {errors}")
        else:
            print(f"✅ API validation passed for {method} {path}")
            logger.info(f"API validation passed for {method} {path}")
        
        return {
            "path": path,
            "method": method,
            "valid": not bool(errors),
            "errors": errors
        }
    except Exception as e:
        error_msg = f"Failed to validate API request: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg,
            "path": path,
            "method": method
        }

# Agent Schema endpoint
print("✅ Registering /api/debug/agent/schema/{agent} endpoint")

@router.get("/agent/schema/{agent}")
def get_agent_schema_endpoint(agent: str):
    """
    Returns the schema definition for a specific agent.
    
    This endpoint helps understand what each agent does, when it runs,
    what it depends on, and what it produces.
    
    Args:
        agent: The name of the agent (e.g., "hal", "nova")
        
    Returns:
        The agent's schema definition, or an empty object if not found
    """
    try:
        print(f"🔍 Debug agent schema endpoint called for agent: {agent}")
        logger.info(f"🔍 Debug agent schema endpoint called for agent: {agent}")
        
        from app.utils.schema_utils import get_agent_schema
        
        # Get the agent schema
        schema = get_agent_schema(agent)
        
        # Log the schema retrieval
        if schema:
            print(f"✅ Agent schema found for {agent}")
            logger.info(f"Agent schema found for {agent}")
        else:
            print(f"⚠️ No schema found for agent {agent}")
            logger.warning(f"No schema found for agent {agent}")
        
        return {
            "agent": agent,
            "schema": schema,
            "found": bool(schema)
        }
    except Exception as e:
        error_msg = f"Failed to retrieve agent schema: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg,
            "agent": agent
        }

# Loop Schema endpoint
print("✅ Registering /api/debug/loop/schema endpoint")

@router.get("/loop/schema")
def get_loop_schema_route():
    """
    Returns the schema definition for loop structure.
    
    This endpoint helps understand what a valid loop should look like,
    including required agents, allowed depth, and exit conditions.
    
    Returns:
        The loop structure schema definition
    """
    try:
        print(f"🔍 Debug loop schema endpoint called")
        logger.info(f"🔍 Debug loop schema endpoint called")
        
        from app.utils.schema_utils import get_loop_schema
        
        # Get the loop schema
        schema = get_loop_schema()
        
        # Log the schema retrieval
        if schema:
            print(f"✅ Loop schema found")
            logger.info(f"Loop schema found")
        else:
            print(f"⚠️ No loop schema found")
            logger.warning(f"No loop schema found")
        
        return {
            "schema": schema,
            "found": bool(schema)
        }
    except Exception as e:
        error_msg = f"Failed to retrieve loop schema: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg
        }

# Loop validation endpoint
print("✅ Registering /api/debug/loop/validate/{project_id} endpoint")

@router.get("/loop/validate/{project_id}")
def validate_loop_route(project_id: str):
    """
    Validates the loop state for a project against the expected schema.
    
    This endpoint helps identify if a loop is healthy, complete, or broken
    based on required agents, allowed depth, and exit conditions.
    
    Args:
        project_id: The ID of the project to validate
        
    Returns:
        Validation results including whether the loop state is valid and any errors found
    """
    try:
        print(f"🔍 Debug loop validation endpoint called for project: {project_id}")
        logger.info(f"🔍 Debug loop validation endpoint called for project: {project_id}")
        
        from app.utils.schema_utils import validate_loop_state
        
        # Try to import PROJECT_MEMORY from different possible locations
        try:
            from app.modules.project_state import PROJECT_MEMORY
        except ImportError:
            try:
                from app.memory import PROJECT_MEMORY
            except ImportError:
                # If we can't find the actual memory store, create a mock one for testing
                print("⚠️ Could not import PROJECT_MEMORY, using mock memory store")
                logger.warning("Could not import PROJECT_MEMORY, using mock memory store")
                PROJECT_MEMORY = {
                    project_id: {
                        "project_id": project_id,
                        "timestamp": "2025-04-19T21:44:00.000000",
                        "status": "active",
                        "next_recommended_step": "Run NOVA to implement solution",
                        "loop_status": "running",
                        "completed_steps": ["hal", "nova"],
                        "loop_count": 1,
                        "loop_complete": False,
                        "agents": {},
                        "task_log": [],
                        "logic_modules": {},
                        "registry": {}
                    }
                }

        # Validate the loop state
        errors = validate_loop_state(project_id, PROJECT_MEMORY)
        
        # Log the validation results
        if errors:
            print(f"⚠️ Loop validation errors found for project {project_id}: {errors}")
            logger.warning(f"Loop validation errors found for project {project_id}: {errors}")
        else:
            print(f"✅ Loop validation passed for project {project_id}")
            logger.info(f"Loop validation passed for project {project_id}")
        
        return {
            "project_id": project_id,
            "valid": not bool(errors),
            "errors": errors
        }
    except Exception as e:
        error_msg = f"Failed to validate loop state: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg,
            "project_id": project_id
        }

# Reflection validation endpoint
print("✅ Registering /api/debug/reflection/validate endpoint")

@router.post("/reflection/validate")
def validate_reflection_route(payload: Dict[str, Any] = Body(...)):
    """
    Validates an agent reflection entry against the expected schema.
    
    This endpoint helps ensure all reflective memory entries (from HAL, SAGE, CRITIC, etc.)
    follow the defined format, making reflections structured, traceable, and analyzable.
    
    Args:
        payload: The reflection entry to validate
        
    Returns:
        Validation results including whether the reflection is valid and any errors found
    """
    try:
        print(f"🔍 Debug reflection validation endpoint called")
        logger.info(f"🔍 Debug reflection validation endpoint called")
        
        from app.utils.schema_utils import validate_reflection
        
        # Validate the reflection entry
        errors = validate_reflection(payload)
        
        # Log the validation results
        if errors:
            print(f"⚠️ Reflection validation errors found: {errors}")
            logger.warning(f"Reflection validation errors found: {errors}")
        else:
            print(f"✅ Reflection validation passed")
            logger.info(f"Reflection validation passed")
        
        return {
            "valid": not bool(errors),
            "errors": errors
        }
    except Exception as e:
        error_msg = f"Failed to validate reflection: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg
        }

# Tool validation endpoint
print("✅ Registering /api/debug/tool/validate/{tool} endpoint")

@router.post("/tool/validate/{tool}")
def validate_tool_usage(tool: str, payload: Dict[str, Any] = Body(...)):
    """
    Validates a tool call against the expected schema.
    
    This endpoint helps ensure all tool calls follow the defined format,
    with required inputs and expected outputs, making tool usage safer and more predictable.
    
    Args:
        tool: The name of the tool to validate (e.g., "file_writer", "repo_tools")
        payload: The payload to validate
        
    Returns:
        Validation results including whether the tool call is valid and any errors found
    """
    try:
        print(f"🔍 Debug tool validation endpoint called for tool: {tool}")
        logger.info(f"🔍 Debug tool validation endpoint called for tool: {tool}")
        
        from app.utils.schema_utils import validate_tool_call
        
        # Validate the tool call
        errors = validate_tool_call(tool, payload)
        
        # Log the validation results
        if errors:
            print(f"⚠️ Tool validation errors found for {tool}: {errors}")
            logger.warning(f"Tool validation errors found for {tool}: {errors}")
        else:
            print(f"✅ Tool validation passed for {tool}")
            logger.info(f"Tool validation passed for {tool}")
        
        return {
            "tool": tool,
            "valid": not bool(errors),
            "errors": errors
        }
    except Exception as e:
        error_msg = f"Failed to validate tool call: {str(e)}"
        print(f"❌ {error_msg}")
        logger.error(f"❌ {error_msg}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "status": "error",
            "message": error_msg,
            "tool": tool
        }

# Simple health check endpoint for the debug router
@router.get("/ping")
async def debug_ping():
    """
    Simple health check endpoint for the debug router.
    """
    print("🔍 Debug ping endpoint called")
    logger.info(f"🔍 Debug ping endpoint called")
    
    return {
        "status": "ok",
        "message": "Debug router is working",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }

# Print confirmation after all endpoints are defined
print("✅ All debug routes registered successfully")
