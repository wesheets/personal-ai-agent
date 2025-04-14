from fastapi import APIRouter, Request
import os
import logging
import platform
import sys
from typing import Dict, Any
import time
from datetime import datetime

# Create router
router = APIRouter(tags=["Environment Health"])
logger = logging.getLogger("env_health")

@router.get("/env/health")
async def environment_health_check(request: Request) -> Dict[str, Any]:
    """
    Comprehensive environment health check endpoint that returns detailed information
    about the current environment, including:
    - Environment variables (sanitized)
    - System information
    - Python version
    - Deployment platform detection
    - Request information
    
    This endpoint is useful for diagnosing deployment issues.
    """
    # Start time for performance measurement
    start_time = time.time()
    
    # Get environment variables (sanitized)
    env_vars = {}
    sensitive_keys = ["KEY", "SECRET", "PASSWORD", "TOKEN", "CREDENTIAL"]
    
    for key, value in os.environ.items():
        # Skip internal environment variables
        if key.startswith("_") or key.startswith("PYTHON"):
            continue
            
        # Sanitize sensitive values
        is_sensitive = any(sensitive_word in key.upper() for sensitive_word in sensitive_keys)
        if is_sensitive and value:
            # Show first and last character with length indicator
            sanitized_value = f"{value[0]}...{value[-1]} ({len(value)} chars)"
            env_vars[key] = sanitized_value
        else:
            env_vars[key] = value
    
    # Detect deployment platform
    platform_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "deployment_platform": "unknown"
    }
    
    # Detect common deployment platforms
    if os.environ.get("RAILWAY_ENVIRONMENT"):
        platform_info["deployment_platform"] = "Railway"
    elif os.environ.get("VERCEL"):
        platform_info["deployment_platform"] = "Vercel"
    elif os.environ.get("HEROKU_APP_ID"):
        platform_info["deployment_platform"] = "Heroku"
    elif os.environ.get("RENDER"):
        platform_info["deployment_platform"] = "Render"
    elif os.environ.get("DETA_RUNTIME"):
        platform_info["deployment_platform"] = "Deta"
    elif os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        platform_info["deployment_platform"] = "AWS Lambda"
    
    # Get request information
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "headers": {k: v for k, v in request.headers.items() if k.lower() not in ["authorization", "cookie"]},
        "client_host": request.client.host if request.client else None,
        "client_port": request.client.port if request.client else None,
    }
    
    # Check for critical environment variables
    critical_vars = ["OPENAI_API_KEY", "PORT", "HOST", "CORS_ALLOWED_ORIGINS"]
    missing_vars = [var for var in critical_vars if not os.environ.get(var)]
    
    # Check port configuration
    port_config = {
        "env_port": os.environ.get("PORT"),
        "default_port": "8000",
        "is_using_env_port": os.environ.get("PORT") is not None,
    }
    
    # Prepare response
    response = {
        "status": "healthy" if not missing_vars else "degraded",
        "timestamp": datetime.now().isoformat(),
        "environment": env_vars,
        "platform": platform_info,
        "request": request_info,
        "port_config": port_config,
        "missing_critical_vars": missing_vars,
        "response_time_ms": round((time.time() - start_time) * 1000, 2)
    }
    
    # Log the health check
    logger.info(f"Environment health check: {response['status']}")
    if missing_vars:
        logger.warning(f"Missing critical environment variables: {missing_vars}")
    
    return response
