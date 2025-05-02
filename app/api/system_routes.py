"""
Modified system_routes.py to register /respond and expose agent manifest and CORS debug endpoints.
"""

from fastapi import APIRouter, Request
import logging
import os
from app.core.middleware.cors import normalize_origin, sanitize_origin_for_header
from app.core.agent_loader import get_all_agents
from app.api import respond  # ✅ NEW

# Configure logging
logger = logging.getLogger("api")

# Create router
router = APIRouter()

# ✅ Register respond.py from app/api/respond.py
router.include_router(respond.router, prefix="/api")

@router.get("/system/cors-debug")
async def cors_debug(request: Request):
    request_origin = request.headers.get("origin", "")
    normalized_request_origin = normalize_origin(request_origin)

    raw_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    allowed_origins = []
    normalized_allowed_origins = []

    for origin in raw_origins.split(","):
        origin = origin.strip()
        if origin:
            allowed_origins.append(origin)
            normalized_allowed_origins.append(normalize_origin(origin))

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

@router.get("/system/agents/manifest")
async def get_agents_manifest():
    try:
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
