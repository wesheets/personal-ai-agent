"""
System routes for the Personal AI Agent system.
"""
from fastapi import APIRouter, Request
import logging
import os
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
