from fastapi import Request, Response
from fastapi.responses import JSONResponse
import os
import logging

logger = logging.getLogger("api")

# Default to 1MB, but allow configuration via environment variable
MAX_REQUEST_BODY_SIZE = int(os.environ.get("MAX_REQUEST_BODY_SIZE", 1 * 1024 * 1024))  # 1MB default

async def limit_request_body_size(request: Request, call_next):
    """
    Middleware to limit request body size to prevent memory issues with large payloads.
    
    This helps prevent potential DoS attacks and memory exhaustion from extremely large requests.
    """
    # Check content length header
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BODY_SIZE:
        logger.warning(f"Request body too large: {content_length} bytes (max: {MAX_REQUEST_BODY_SIZE})")
        return JSONResponse(
            status_code=413,
            content={
                "status": "error",
                "message": "Request body too large",
                "error": f"Maximum request body size is {MAX_REQUEST_BODY_SIZE} bytes"
            }
        )
    return await call_next(request)
