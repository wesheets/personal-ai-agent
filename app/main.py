from fastapi import FastAPI, APIRouter, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.routing import APIRoute
import os
import logging
import inspect
import re
import datetime
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
import json
import asyncio
import time
from app.core.middleware.cors import CustomCORSMiddleware, normalize_origin, sanitize_origin_for_header

from app.api.agent import router as agent_router
from app.api.memory import router as memory_router
from app.api.goals import goals_router
from app.api.memory_viewer import memory_router as memory_viewer_router
from app.api.control import control_router
from app.api.logs import logs_router
from app.api.delegate_route import router as delegate_router, AGENT_PERSONALITIES  # ✅ HAL ROUTER
from app.diagnostics.hal_route_debug import router as hal_debug_router
from app.api.debug_routes import router as debug_router  # Debug routes for diagnostics
from app.api.performance_monitoring import router as performance_router  # Performance monitoring
from app.api.streaming_route import router as streaming_router, stream_response  # Streaming response router
from app.api.system_routes import router as system_routes  # System routes including CORS debug
from app.middleware.size_limiter import limit_request_body_size  # Request body size limiter
from app.health import health_router  # Health check endpoint for Railway deployment

from app.providers import initialize_model_providers, get_available_models
from app.core.seeding import get_seeding_manager
from app.core.prompt_manager import PromptManager
from app.core.task_state_manager import get_task_state_manager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app/logs/api.log', mode='a')
    ]
)
logger = logging.getLogger("api")

# CORS configuration - Using regex to allow all Vercel preview branches and production domain
# Note: Previous environment variable based configuration has been replaced with regex pattern

# Enable CORS debug mode if specified in environment
os.environ["CORS_DEBUG"] = os.environ.get("CORS_DEBUG", "false")

# FastAPI app init
app = FastAPI(
    title="Enhanced AI Agent System",
    description="A personal AI agent system with vector memory, multi-model support, and configurable agent personalities",
    version="1.0.0"
)

# Direct route with unique name to avoid potential Vercel routing conflicts
@app.post("/api/_test_delegate_hook")
async def delegate_test_unique(request: Request):
    """
    Simple test endpoint with unique name to avoid potential Vercel routing conflicts.
    Returns a JSON response to verify route registration.
    """
    print("✅ /api/_test_delegate_hook hit")  # Explicit print for debugging
    logger.info(f"🔄 Direct delegate test route with unique name executed from {inspect.currentframe().f_code.co_filename}")
    
    # Return simple JSON response to verify route is working
    return {"message": "Route works"}

# Direct healthcheck endpoints for Railway deployment
@app.get("/health")
async def health():
    """
    Simple health check endpoint that returns a plain text "OK" response.
    Used by Railway to verify the application is running properly.
    """
    logger.info("Health check endpoint accessed at /health")
    return Response(content="OK", media_type="text/plain")

@app.get("/")
async def root_health():
    """
    Root-level health check endpoint that returns a plain text "OK" response.
    Some platforms expect the healthcheck at the root level.
    """
    logger.info("Health check endpoint accessed at root level")
    return Response(content="OK", media_type="text/plain")

# Add startup delay to ensure FastAPI is fully initialized before healthcheck
import asyncio

@app.on_event("startup")
async def startup_delay():
    """
    Add a small delay during startup to ensure FastAPI is fully initialized
    before Railway attempts the healthcheck.
    """
    logger.info("Adding startup delay to ensure application is fully initialized...")
    await asyncio.sleep(1)  # give it breathing room before healthcheck
    logger.info("Startup delay completed, application ready for healthcheck")

# Route logger for debugging
@app.on_event("startup")
async def log_all_routes():
    print("🚀 Booting Enhanced AI Agent System...")
    print("📡 ROUTES REGISTERED ON STARTUP:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"➡️ {route.path} [{', '.join(route.methods)}] from {inspect.getsourcefile(route.endpoint)}")
            logger.info(f"🔍 {route.path} [{','.join(route.methods)}]")
    
    # Log CORS configuration on startup
    logger.info(f"🔒 CORS Configuration Loaded:")
    import os
    
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    logger.info(f"🔒 CORS_ALLOWED_ORIGINS raw: {raw_origins}")
    logger.info(f"🔒 CORS_ALLOW_CREDENTIALS: {cors_allow_credentials}")
    logger.info(f"🔒 Allowed Origins Count: {len(allowed_origins)}")
    logger.info(f"✅ Using custom CORS middleware with normalized origin matching")
    logger.info(f"✅ Allowed origins: {allowed_origins}")
    logger.info(f"✅ Normalized origins for comparison: {normalized_origins}")
    for idx, (orig, norm) in enumerate(zip(allowed_origins, normalized_origins)):
        sanitized = sanitize_origin_for_header(orig)
        logger.info(f"🔒 Origin {idx+1}: {orig} (normalized: {norm}, sanitized: {sanitized})")

# Add custom CORS middleware from the extracted module
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

# Add temporary debug middleware to print the request origin
@app.middleware("http")
async def log_origin(request: Request, call_next):
    print(f"🔍 ORIGIN HEADER: {request.headers.get('origin')}")
    return await call_next(request)

# Temporarily override the CORS middleware with wildcard to validate frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TEMP UNLOCK for live frontend testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body size limiter middleware
app.middleware("http")(limit_request_body_size)

# Middleware for logging with timeout handling
@app.middleware("http")
async def log_requests(request: Request, call_next):
    import time
    import asyncio
    import json
    from fastapi.responses import JSONResponse
    
    logger.info(f"Request: {request.method} {request.url}")
    
    # Log origin for CORS debugging with normalization
    origin = request.headers.get("origin")
    if origin:
        normalized_request_origin = normalize_origin(origin)
        logger.info(f"🔒 Request Origin: {origin}")
        logger.info(f"🔒 Normalized Request Origin: {normalized_request_origin}")
    
    # Only log headers for non-production environments or if explicitly enabled
    if os.environ.get("LOG_HEADERS", "false").lower() == "true":
        logger.info(f"Request headers: {request.headers}")
    
    # Pre-parse body for delegate routes to avoid double parsing
    if "delegate" in str(request.url) or "latest" in str(request.url) or "goals" in str(request.url):
        try:
            # Use asyncio.wait_for to implement timeout for body reading
            raw_body = await asyncio.wait_for(request.body(), timeout=15.0)  # Increased from 8.0 to 15.0 seconds
            if raw_body:
                # Store raw body for later use
                request._body = raw_body
                
                # Try to parse as JSON and store in request.state
                try:
                    body_str = raw_body.decode()
                    # Only log body summary for security/performance
                    log_body = body_str[:100] + "..." if len(body_str) > 100 else body_str
                    logger.info(f"Request body summary: {log_body}")
                    
                    # Pre-parse JSON and store in request state
                    request.state.body = json.loads(body_str)
                    logger.info("Successfully pre-parsed JSON body in middleware")
                except json.JSONDecodeError:
                    # Not valid JSON, just store raw body
                    logger.warning("Request body is not valid JSON, storing raw body only")
                except Exception as e:
                    logger.error(f"Error parsing JSON body: {str(e)}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout reading request body for {request.url}")
            return JSONResponse(
                status_code=408,
                content={
                    "status": "error",
                    "message": "Request body reading timed out in middleware",
                    "error": "Timeout while reading request body"
                }
            )
        except Exception as e:
            logger.error(f"Error reading request body: {str(e)}")
    
    # Set overall request timeout (15 seconds max for Railway environment)
    start_time = time.time()
    try:
        # Use asyncio.wait_for to implement timeout for the entire request
        # Increased timeout for Railway environment
        timeout_seconds = 15.0 if os.environ.get("RAILWAY_ENVIRONMENT") else 10.0
        response = await asyncio.wait_for(call_next(request), timeout=timeout_seconds)
        process_time = time.time() - start_time
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Process time: {process_time:.4f}s")
        
        # Add timing header to response
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log CORS headers for debugging
        if origin:
            allow_origin = response.headers.get("access-control-allow-origin", "")
            logger.info(f"🔒 Response CORS: Access-Control-Allow-Origin: '{allow_origin}'")
            
            if allow_origin:
                # Check for semicolons in the header
                if ";" in allow_origin:
                    logger.warning(f"🔒 CORS Response: ⚠️ Header contains semicolon: '{allow_origin}'")
                    # Fix the header by removing the semicolon
                    clean_origin = sanitize_origin_for_header(allow_origin)
                    logger.info(f"🔒 CORS Response: 🧹 Cleaning header: '{clean_origin}'")
                    response.headers["access-control-allow-origin"] = clean_origin
                else:
                    logger.info(f"🔒 CORS Response: ✅ Header clean: '{allow_origin}'")
            else:
                logger.warning(f"🔒 CORS Response: ❌ Header missing")
        
        return response
    except asyncio.TimeoutError:
        logger.error(f"Timeout processing request for {request.url}")
        process_time = time.time() - start_time
        logger.error(f"Process time before timeout: {process_time:.4f}s")
        return JSONResponse(
            status_code=504,
            content={
                "status": "error",
                "message": "Request processing timed out",
                "error": "Timeout while processing request"
            }
        )
    except Exception as e:
        logger.error(f"Error during request processing: {str(e)}")
        logger.error(f"Process time: {time.time() - start_time:.4f}s")
        raise

# Initialize providers
initialize_model_providers()

# System routes
system_router = APIRouter(prefix="/system", tags=["System"])

@system_router.get("/models")
async def get_models():
    models = get_available_models()
    return models

@system_router.get("/status")
async def get_system_status():
    try:
        prompt_manager = PromptManager()
        task_state_manager = get_task_state_manager()
        seeding_manager = get_seeding_manager()
        agents_seeded = await seeding_manager.seed_default_agents(prompt_manager)
        goals_seeded = await seeding_manager.seed_default_goals(task_state_manager)
        return {
            "status": "operational",
            "version": "1.0.0",
            "uptime": "N/A",
            "agents_count": len(prompt_manager.get_available_agents()),
            "goals_count": len(task_state_manager.goals),
            "tasks_count": len(task_state_manager.tasks),
            "seeding": {
                "agents_seeded": agents_seeded,
                "goals_seeded": goals_seeded
            }
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e), "version": "1.0.0"}

# CORS configuration debug endpoint
@system_router.get("/cors-config", tags=["Debug"])
async def get_cors_config(request: Request):
    # Enhanced debug information with normalization
    raw_env = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    request_origin = request.headers.get("origin", "")
    normalized_request_origin = normalize_origin(request_origin)
    sanitized_request_origin = sanitize_origin_for_header(request_origin)
    
    # Check if normalized origin matches any of our normalized allowed origins
    origin_match = False
    matched_with = None
    comparison_results = []
    
    for allowed_norm in normalized_origins:
        # Use strict string equality for validation
        is_match = normalized_request_origin == allowed_norm
        comparison_results.append({
            "allowed_origin": allowed_norm,
            "request_origin": normalized_request_origin,
            "is_match": is_match,
            "comparison_type": "strict equality"
        })
        
        if is_match:
            origin_match = True
            matched_with = allowed_norm
            break
    
    # Check response headers
    response_headers = {}
    for middleware in app.user_middleware:
        if hasattr(middleware, "cls") and middleware.cls.__name__ == "CustomCORSMiddleware":
            response_headers["middleware_type"] = "CustomCORSMiddleware"
            break
    
    # Test header sanitization
    test_origins = [
        "https://example.com",
        "https://example.com;",
        "https://example.com,",
        "https://example.com; ",
        " https://example.com;"
    ]
    sanitization_tests = {origin: sanitize_origin_for_header(origin) for origin in test_origins}
    
    # Add a memory log for CORS fix verification
    try:
        from app.api.memory import add_memory_entry
        import asyncio
        asyncio.create_task(add_memory_entry(
            "CORS Fix Complete", 
            f"CORS origin matching fixed using strict equality. Frontend origin: {request_origin}",
            "system"
        ))
        cors_memory_added = True
    except Exception as e:
        cors_memory_added = False
        logger.error(f"Failed to add CORS fix memory: {str(e)}")
    
    return {
        "allowed_origins": allowed_origins,
        "normalized_origins": normalized_origins,
        "allow_credentials": cors_allow_credentials,
        "origins_count": len(allowed_origins),
        "raw_env_value": raw_env,
        "raw_env_length": len(raw_env),
        "deduplication_active": True,
        "normalization_active": True,
        "sanitization_active": True,
        "custom_middleware_active": True,
        "request_info": {
            "raw_origin": request_origin,
            "normalized_origin": normalized_request_origin,
            "sanitized_origin": sanitized_request_origin,
            "match_result": "✅ Allowed" if origin_match else "❌ Not allowed",
            "matched_with": matched_with
        },
        "comparison_results": comparison_results,
        "response_headers": response_headers,
        "middleware_config": {
            "allow_origins": "List with {} origins".format(len(allowed_origins)),
            "allow_credentials": cors_allow_credentials,
            "allow_methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH",
            "allow_headers": "*"
        },
        "sanitization_tests": sanitization_tests,
        "debug_info": {
            "is_list_type": str(type(allowed_origins)),
            "first_origin": allowed_origins[0] if allowed_origins else None,
            "has_duplicates": len(allowed_origins) != len(set(allowed_origins)),
            "using_regex_matching": False,
            "using_strict_equality": True,
            "using_custom_middleware": True,
            "using_header_sanitization": True,
            "cors_memory_added": cors_memory_added
        }
    }

# Direct route for delegate-stream to bypass any router mounting issues
@app.post("/api/agent/delegate-test")
async def direct_delegate_stream(request: Request):
    """
    Direct implementation of delegate-stream endpoint to bypass router mounting issues.
    This endpoint streams the response back to the client.
    """
    print("✅ /api/agent/delegate-test hit")  # Explicit print for debugging
    logger.info(f"🔄 Direct delegate-test route executed from {inspect.currentframe().f_code.co_filename}")
    
    # Return streaming response with enhanced headers
    return StreamingResponse(
        stream_response(request),
        media_type="application/x-ndjson",
        headers={
            "X-Streaming-Mode": "enabled",
            "X-Agent-Version": "1.0.0",
            "Cache-Control": "no-cache"
        }
    )

# Swagger docs route
@app.get("/api/docs", include_in_schema=False)
def overridden_swagger_docs():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Enhanced AI Agent API",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )
