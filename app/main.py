"""
Modified main.py to integrate the failsafe agent loader and ensure the backend
doesn't crash even if some agents fail to initialize.
"""

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
from fastapi.responses import StreamingResponse, JSONResponse
import json
import asyncio
import time
import uvicorn
from app.core.middleware.cors import CustomCORSMiddleware, normalize_origin, sanitize_origin_for_header

# Wrap the entire startup in a try-except block for error trapping
try:
    print("🚀 Starting Promethios OS...")
    
    # Initialize agent registry first with failsafe loader
    from app.core.agent_loader import initialize_agents, get_all_agents, get_agent
    
    # Initialize all agents with failsafe error handling
    print("🔄 Initializing agent registry...")
    agents = initialize_agents()
    print(f"✅ Agent registry initialized with {len(agents)} agents")
    
    from app.api.agent import router as agent_router
    from app.api.memory import router as memory_router
    from app.api.goals import goals_router
    from app.api.memory_viewer import router as memory_viewer_router
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
    from app.api.agent_status import router as agent_status_router  # Agent status checker utility

    from app.providers import initialize_model_providers, get_available_models
    from app.core.seeding import get_seeding_manager
    from app.core.prompt_manager import PromptManager
    from app.core.task_state_manager import get_task_state_manager

    # Load environment variables
    load_dotenv()
    print("✅ Environment variables loaded")

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
    print("✅ Logging configured")

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
    print("✅ FastAPI app initialized")

    # Direct route for delegate-stream
    @app.post("/api/delegate-stream")
    async def delegate_stream(request: Request):
        """
        Direct implementation of delegate-stream endpoint.
        This endpoint streams the response back to the client.
        """
        print("✅ /api/delegate-stream hit")  # Explicit print for debugging
        logger.info(f"🔄 Direct delegate-stream route executed from {inspect.currentframe().f_code.co_filename}")
        
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

    # Direct healthcheck endpoints for Railway deployment
    @app.get("/health")
    async def health():
        """
        Simple health check endpoint that returns a JSON response with {"status": "ok"}.
        Used by Railway to verify the application is running properly.
        
        Modified to return degraded status if agent registry failed to initialize.
        """
        logger.info("Health check endpoint accessed at /health")
        
        # Check if agent registry is initialized
        all_agents = get_all_agents()
        if not all_agents:
            return {"status": "degraded", "error": "Agent registry failed"}
        
        return {"status": "ok", "agents": len(all_agents)}

    @app.get("/")
    async def root_health():
        """
        Root-level health check endpoint that returns a JSON response with {"status": "ok"}.
        Some platforms expect the healthcheck at the root level.
        
        Modified to return degraded status if agent registry failed to initialize.
        """
        logger.info("Health check endpoint accessed at root level")
        
        # Check if agent registry is initialized
        all_agents = get_all_agents()
        if not all_agents:
            return {"status": "degraded", "error": "Agent registry failed"}
        
        return {"status": "ok", "agents": len(all_agents)}

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
        
        cors_allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true")
        logger.info(f"🔒 CORS_ALLOW_CREDENTIALS: {cors_allow_credentials}")
        # Removed legacy allowed_origins references to fix startup issues
        logger.info(f"✅ Using CORSMiddleware with allow_origin_regex")

    # Add custom CORS middleware from the extracted module
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi import Request

    # Production CORS middleware with regex pattern to allow Vercel deploys, Railway apps, and local development
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https://(.*\.vercel\.app|.*\.railway\.app|promethios\.ai)|http://localhost:[0-9]+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("✅ CORS middleware added")

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

    # Include all routers in the app
    print("🔄 Including API routers...")
    app.include_router(agent_router, prefix="/api")
    app.include_router(memory_router, prefix="/api")
    app.include_router(goals_router, prefix="/api")
    app.include_router(memory_viewer_router, prefix="/api")
    app.include_router(control_router, prefix="/api")
    app.include_router(logs_router, prefix="/api")
    app.include_router(delegate_router, prefix="/api")
    app.include_router(hal_debug_router, prefix="/api")
    app.include_router(debug_router, prefix="/api")
    app.include_router(performance_router, prefix="/api")
    app.include_router(streaming_router, prefix="/api")
    app.include_router(system_routes, prefix="/api")
    app.include_router(agent_status_router, prefix="/api")  # Add agent status router
    app.include_router(health_router)  # Include health router without prefix
    print("✅ All API routers included")

    # Initialize providers
    print("🔄 Initializing model providers...")
    initialize_model_providers()
    print("✅ Model providers initialized")

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

    # Include system router
    app.include_router(system_router, prefix="/api")
    print("✅ System router included")

except Exception as e:
    # Global exception handler to prevent complete startup failure
    print(f"❌ ERROR DURING STARTUP: {str(e)}")
    logging.error(f"Critical startup error: {str(e)}", exc_info=True)
    
    # Create a minimal app that can at least respond to health checks
    app = FastAPI(
        title="Enhanced AI Agent System (Degraded Mode)",
        description="Running in degraded mode due to startup error",
        version="1.0.0"
    )
    
    @app.get("/health")
    async def health_degraded():
        """Emergency health check endpoint that always responds."""
        return {"status": "degraded", "error": "Startup failure", "message": str(e)}
    
    @app.get("/")
    async def root_health_degraded():
        """Emergency root endpoint that always responds."""
        return {"status": "degraded", "error": "Startup failure", "message": str(e)}
    
    @app.get("/api/system/agents/manifest")
    async def manifest_degraded():
        """Emergency manifest endpoint that always responds."""
        return {"status": "degraded", "error": "Startup failure", "agents": []}
