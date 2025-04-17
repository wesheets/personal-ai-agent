"""
Modified system_routes.py to fix the agent manifest endpoint.
This ensures the endpoint returns a list of available agents from the agent registry
rather than from a static JSON file.
feature/phase-3.5-hardening
SHA256: 8f2d6b3c5a4e7d9f1b0c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a
INTEGRITY: v3.5.0-system-routes
LAST_MODIFIED: 2025-04-17

main
"""

from fastapi import APIRouter, Request
import logging
import os
import json
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
feature/phase-3.5-hardening
}
main
