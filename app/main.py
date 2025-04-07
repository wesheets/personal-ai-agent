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
from app.core.middleware.cors import CustomCORSMiddleware, normalize_origin, sanitize_origin_for_header

from app.api.auth import router as auth_router  # Import the new auth router
from app.api.agent import router as agent_router
from app.api.memory import router as memory_router
from app.api.goals import goals_router
from app.api.memory_viewer import memory_router as memory_viewer_router
from app.api.control import control_router
from app.api.logs import logs_router
from app.api.delegate_route import router as delegate_router  # ✅ HAL ROUTER
from app.diagnostics.hal_route_debug import router as hal_debug_router
from app.api.debug_routes import router as debug_router  # Debug routes for diagnostics
from app.api.performance_monitoring import router as performance_router  # Performance monitoring
from app.api.streaming_route import router as streaming_router  # Streaming response router
from app.api.system_routes import router as system_routes  # System routes including CORS debug
from app.middleware.size_limiter import limit_request_body_size  # Request body size limiter

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

# CORS configuration
raw_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:3000,https://personal-ai-agent-frontend.vercel.app,https://personal-ai-agent.vercel.app,https://personal-ai-agent-h49q98819-ted-sheets-projects.vercel.app,https://personal-ai-agent-dkmvk5af-ted-sheets-projects.vercel.app,https://personal-ai-agent-git-manus-ui-restore-ted-sheets-projects.vercel.app,https://personal-ai-agent-6knmyj63f-ted-sheets-projects.vercel.app,https://studio.manus.im")

# Clean, normalize, and deduplicate origins
allowed_origins = []
normalized_origins = []
seen_origins = set()
for origin in raw_origins.split(","):
    origin = origin.strip()
    # Sanitize origin to remove any trailing semicolons
    origin = sanitize_origin_for_header(origin)
    if origin:
        normalized = normalize_origin(origin)
        if normalized and normalized not in seen_origins:
            allowed_origins.append(origin)  # Keep original format for CORS middleware
            normalized_origins.append(normalized)  # Store normalized version for comparison
            seen_origins.add(normalized)

cors_allow_credentials = os.environ.get("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# Enable CORS debug mode if specified in environment
os.environ["CORS_DEBUG"] = os.environ.get("CORS_DEBUG", "false")

# FastAPI app init
app = FastAPI(
    title="Enhanced AI Agent System",
    description="A personal AI agent system with vector memory, multi-model support, and configurable agent personalities",
    version="1.0.0"
)

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
app.add_middleware(
    CustomCORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    allow_credentials=cors_allow_credentials,
    max_age=86400,
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

# Include routers
app.include_router(auth_router)  # Add the auth router
app.include_router(agent_router)
app.include_router(memory_router)
app.include_router(goals_router)
app.include_router(memory_viewer_router)
app.include_router(control_router)
app.include_router(logs_router)
app.include_router(delegate_router)
app.include_router(hal_debug_router)
app.include_router(debug_router)
app.include_router(performance_router)
app.include_router(streaming_router)
app.include_router(system_routes)
app.include_router(system_router)

# Mount static files
app.mount("/static", StaticFiles(directory="public"), name="static")

# Serve frontend
@app.get("/", include_in_schema=False)
async def serve_frontend():
    with open("index.html", "r") as f:
        html_content = f.read()
    return Response(content=html_content, media_type="text/html")

# Serve Swagger UI with custom CSS
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API Documentation",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}
