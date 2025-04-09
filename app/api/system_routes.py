"""
System routes for the Personal AI Agent system.
"""
from fastapi import APIRouter, Request
import logging
import os
import json
from pathlib import Path
from app.core.middleware.cors import normalize_origin, sanitize_origin_for_header

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
    
    The manifest includes agent status, version, and capabilities.
    """
    try:
        # Path to the agent manifest file
        manifest_path = Path(__file__).parents[2] / "config" / "agent_manifest.json"
        
        # Check if the file exists
        if not manifest_path.exists():
            logger.error(f"Agent manifest file not found at {manifest_path}")
            return {"error": "Agent manifest file not found", "status": "error"}
        
        # Load the manifest file
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
        
        # Add additional runtime information to each agent
        for agent_id, agent_info in manifest_data.items():
            # Check if the entrypoint file exists
            entrypoint = agent_info.get("entrypoint", "")
            if entrypoint:
                entrypoint_path = Path(__file__).parents[2] / entrypoint
                agent_info["entrypoint_exists"] = entrypoint_path.exists()
            
            # Add runtime status if not present
            if "status" not in agent_info:
                agent_info["status"] = "unknown"
            
            # Add capabilities field if not present
            if "capabilities" not in agent_info:
                agent_info["capabilities"] = []
        
        return {
            "agents": manifest_data,
            "total_agents": len(manifest_data),
            "active_agents": sum(1 for agent in manifest_data.values() if agent.get("status") == "active"),
            "status": "success"
        }
    
    except Exception as e:
        logger.error(f"Error loading agent manifest: {str(e)}")
        return {"error": str(e), "status": "error"}
