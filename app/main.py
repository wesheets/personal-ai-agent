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
    try:
        from app.core.agent_loader import initialize_agents, get_all_agents, get_agent
        
        # Initialize all agents with failsafe error handling
        print("🔄 Initializing agent registry...")
        agents = initialize_agents()
        print(f"✅ Agent registry initialized with {len(agents)} agents")
    except Exception as e:
        print(f"⚠️ Agent Registry Load Failed: {e}")
        agents = []
    
    # Import router modules with safeguards
    # Import orchestrator routes
    try:
        from routes.orchestrator_routes import router as orchestrator_router
        print("✅ Successfully imported orchestrator_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: orchestrator_routes — {e}")
        orchestrator_router = APIRouter()
        @orchestrator_router.get("/orchestrator/ping")
        def orchestrator_ping():
            return {"status": "Orchestrator router placeholder"}
    
    # Import agent routes
    try:
        from routes.agent_routes import router as agent_router
        print("✅ Successfully imported agent_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: agent_routes — {e}")
        agent_router = APIRouter()
        @agent_router.get("/agent/ping")
        def agent_ping():
            return {"status": "Agent router placeholder"}
    
    # Import memory routes
    try:
        from routes.memory_routes import router as memory_router
        print("✅ Successfully imported memory_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: memory_routes — {e}")
        memory_router = APIRouter()
        @memory_router.get("/memory/ping")
        def memory_ping():
            return {"status": "Memory router placeholder"}
    
    # Import system routes
    try:
        from routes.system_routes import router as system_router
        print("✅ Successfully imported system_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: system_routes — {e}")
        system_router = APIRouter()
        @system_router.get("/system/ping")
        def system_ping():
            return {"status": "System router placeholder"}
    
    # Import debug routes
    try:
        from routes.debug_routes import router as debug_router
        print("✅ Successfully imported debug_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: debug_routes — {e}")
        debug_router = APIRouter()
        @debug_router.get("/debug/ping")
        def debug_ping():
            return {"status": "Debug router placeholder"}
    
    # Import HAL routes
    try:
        from routes.hal_routes import router as hal_router
        print("✅ Successfully imported hal_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: hal_routes — {e}")
        hal_router = APIRouter()
        @hal_router.get("/hal/ping")
        def hal_ping():
            return {"status": "HAL router placeholder"}
    
    # Import snapshot routes
    try:
        from routes.snapshot_routes import router as snapshot_router
        print("✅ Successfully imported snapshot_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: snapshot_routes — {e}")
        snapshot_router = APIRouter()
        @snapshot_router.get("/snapshot/ping")
        def snapshot_ping():
            return {"status": "Snapshot router placeholder"}
    
    # Import system integrity router
    try:
        from routes.system_integrity import router as integrity_router
        print("✅ Successfully imported system integrity router")
    except Exception as e:
        print(f"⚠️ Router Load Failed: system_integrity — {e}")
        integrity_router = APIRouter()
        @integrity_router.get("/integrity")
        async def integrity_import_error():
            return {"status": "error", "message": f"Failed to import system integrity router: {str(e)}"}
        print("⚠️ Created placeholder router for /api/system/integrity")
    
    # Import project start router for Phase 12.0 - CRITICAL for Agent Playground
    print("🔄 Importing project start router for Phase 12.0 (Agent Playground)")
    try:
        from app.api.project import start  # Project start router
        print("✅ Successfully imported project start router")
    except Exception as e:
        print(f"⚠️ Router Load Failed: project start — {e}")
        start = APIRouter()
        @start.get("/error")
        async def project_start_import_error():
            return {"status": "error", "message": f"Failed to import project start router: {str(e)}"}
        print("⚠️ Created placeholder router for /api/project/error")
    
    # Import modules for API routes with safeguards
    try:
        from app.api.modules.agent import router as agent_module_router  # AgentRunner module router
        print("✅ Successfully imported agent_module_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: agent_module — {e}")
        agent_module_router = APIRouter()
    
    try:
        from app.api.modules.memory import router as memory_router_module  # Memory module router
        print("✅ Successfully imported memory_router_module")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: memory_module — {e}")
        memory_router_module = APIRouter()
    
    try:
        from app.api.modules.orchestrator import router as orchestrator_router_module  # Orchestrator module router
        print("✅ Successfully imported orchestrator_router_module")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: orchestrator_module — {e}")
        orchestrator_router_module = APIRouter()
    
    try:
        from app.api.modules.feedback import router as feedback_router  # Feedback module router
        print("✅ Successfully imported feedback_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: feedback — {e}")
        feedback_router = APIRouter()
    
    try:
        from app.api.modules.user_context import router as user_context_router  # User Context module router
        print("✅ Successfully imported user_context_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: user_context — {e}")
        user_context_router = APIRouter()
    
    try:
        from app.api.modules.respond import router as respond_router  # Respond module router
        print("✅ Successfully imported respond_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: respond — {e}")
        respond_router = APIRouter()
    
    try:
        from app.api.modules.plan import router as plan_router  # Plan Generator module router
        print("✅ Successfully imported plan_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: plan — {e}")
        plan_router = APIRouter()
    
    try:
        from app.api.modules.project import router as project_router  # Project Management module router
        print("✅ Successfully imported project_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: project — {e}")
        project_router = APIRouter()
    
    # Import memory thread and summarize routers
    try:
        from app.modules.memory_thread import router as memory_thread_router
        print("✅ Successfully imported memory_thread_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: memory_thread — {e}")
        memory_thread_router = APIRouter()
    
    try:
        from app.modules.memory_summarize import router as memory_summarize_router
        print("✅ Successfully imported memory_summarize_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: memory_summarize — {e}")
        memory_summarize_router = APIRouter()
    
    try:
        from app.middleware.size_limiter import limit_request_body_size  # Request body size limiter
        print("✅ Successfully imported size_limiter middleware")
    except Exception as e:
        print(f"⚠️ Middleware Load Failed: size_limiter — {e}")
        # Define a placeholder middleware function
        def limit_request_body_size(request, call_next):
            return call_next(request)
    
    try:
        from app.health import health_router  # Health check endpoint for Railway deployment
        print("✅ Successfully imported health_router")
    except Exception as e:
        print(f"⚠️ Router Load Failed: health — {e}")
        health_router = APIRouter()

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
    print("🔓 FastAPI app object was successfully created in main.py")

    # Direct healthcheck endpoints for Railway deployment
    @app.get("/health")
    async def health():
        """
        Simple health check endpoint that returns a JSON response with {"status": "ok"}.
        Used by Railway to verify the application is running properly.
        """
        logger.info("Health check endpoint accessed at /health")
        return {"status": "ok", "mode": "production"}

    @app.get("/")
    async def root_health():
        """
        Root-level health check endpoint that returns a JSON response with {"status": "ok"}.
        Some platforms expect the healthcheck at the root level.
        """
        logger.info("Health check endpoint accessed at root level")
        return {"status": "ok", "mode": "production"}
        
    @app.get("/control/registry")
    async def control_registry():
        """
        Control Room registry endpoint that returns information about available modules
        and their UI integration status. This powers dynamic UI menus, dev dashboards,
        and Control Room builder screens.
        """
        logger.info("Control Room registry endpoint accessed")
        
        # Use standard library for timestamp to avoid import issues
        import datetime as dt
        current_time = dt.datetime.now().isoformat()
        
        return {
            "modules": [
                {"name": "Scope Planner", "route": "/orchestrator/scope", "ui": "markdown", "status": "needs_ui"},
                {"name": "Delegate Executor", "route": "/delegate", "ui": "payload_button", "status": "needs_ui"},
                {"name": "Summary Viewer", "route": "/summarize", "ui": "markdown_panel", "status": "needs_ui"},
                {"name": "Project Selector", "route": "/projects", "ui": "sidebar_dropdown", "status": "built"},
                {"name": "Tone Configurator", "route": "/agent/tone", "ui": "editable_table", "status": "future"},
                {"name": "Loop Controller", "route": "/loop", "ui": "status_panel", "status": "needs_ui"},
                {"name": "Reflection Viewer", "route": "/reflect", "ui": "text_panel", "status": "needs_ui"},
                {"name": "Memory Browser", "route": "/read", "ui": "searchable_table", "status": "in_progress"},
                {"name": "Agent Registry", "route": "/agents", "ui": "card_grid", "status": "needs_ui"},
                {"name": "System Caps Monitor", "route": "/system/caps", "ui": "settings_panel", "status": "future"}
            ],
            "ui_components": [
                {"type": "markdown", "description": "Markdown content viewer with code highlighting"},
                {"type": "payload_button", "description": "JSON payload editor with request/response handling"},
                {"type": "markdown_panel", "description": "Formatted text display with copy functionality"},
                {"type": "sidebar_dropdown", "description": "Hierarchical organization with search"},
                {"type": "editable_table", "description": "Inline editing with validation"},
                {"type": "status_panel", "description": "Visual status display with metrics"},
                {"type": "text_panel", "description": "Plain text display with search"},
                {"type": "searchable_table", "description": "Data table with filtering and sorting"},
                {"type": "card_grid", "description": "Visual card layout for entity display"},
                {"type": "settings_panel", "description": "Configuration interface with save/reset"}
            ],
            "integration_status": {
                "needs_ui": "Component needs UI implementation",
                "in_progress": "UI implementation in progress",
                "built": "UI component is implemented and functional",
                "future": "Planned for future implementation"
            },
            "last_updated": current_time
        }

    # Add debug endpoint for memory verification
    @app.get("/api/debug/memory/log")
    async def debug_memory_log():
        """
        Debug endpoint to verify memory thread database state.
        Returns thread counts and recent entries.
        """
        try:
            from app.modules.memory_thread import THREAD_DB
            import datetime

            thread_counts = {}
            for key, entries in THREAD_DB.items():
                project_id, chain_id = key.split(":")
                if project_id not in thread_counts:
                    thread_counts[project_id] = {}
                thread_counts[project_id][chain_id] = len(entries)

            recent_entries = []
            for key, entries in THREAD_DB.items():
                for entry in entries[-5:]:
                    entry_with_key = entry.copy()
                    entry_with_key["thread_key"] = key
                    recent_entries.append(entry_with_key)

            recent_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            recent_entries = recent_entries[:10]

            return {
                "status": "ok",
                "thread_count": len(THREAD_DB),
                "thread_counts_by_project": thread_counts,
                "recent_entries": recent_entries,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to access memory thread database: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat()
            }

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

    # Add new startup logging as required
    @app.on_event("startup")
    async def startup_log():
        """
        Log that the FastAPI application has started successfully.
        """
        print("✅ FastAPI application started")
        logger.info("✅ FastAPI application started successfully")

    # Route logger for debugging
    @app.on_event("startup")
    async def log_all_routes():
        print("🚀 Booting Enhanced AI Agent System...")
        print("📡 ROUTES REGISTERED ON STARTUP:")
        for route in app.routes:
            if isinstance(route, APIRoute):
                print(f"➡️ {route.path} [{', '.join(route.methods)}] from {inspect.getsourcefile(route.endpoint)}")
                print(f"🔍 DEBUG ROUTE: {route.path} [{', '.join(route.methods)}]")
                print(f"🔍 DEBUG ENDPOINT: {route.endpoint.__name__}")
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
            return response
        except asyncio.TimeoutError:
            # Handle timeout
            process_time = time.time() - start_time
            logger.error(f"Request timed out after {process_time:.4f}s: {request.method} {request.url}")
            return JSONResponse(
                status_code=504,
                content={
                    "status": "error",
                    "message": "Request timed out",
                    "process_time": f"{process_time:.4f}s"
                }
            )
        except Exception as e:
            # Handle other exceptions
            process_time = time.time() - start_time
            logger.error(f"Request failed after {process_time:.4f}s: {request.method} {request.url}")
            logger.error(f"Error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Internal server error",
                    "error": str(e),
                    "process_time": f"{process_time:.4f}s"
                }
            )
    
    # Register all routers with the /api prefix with safeguards
    # Register the orchestrator_router
    try:
        print(f"🔍 DEBUG: Orchestrator router object: {orchestrator_router}")
        app.include_router(orchestrator_router, prefix="/api")
        print("🧠 Route defined: /api/orchestrator/consult -> orchestrator_consult")
    except Exception as e:
        print(f"⚠️ Failed to register orchestrator_router: {e}")
    
    # Register the agent_router
    try:
        print(f"🔍 DEBUG: Agent router object: {agent_router}")
        app.include_router(agent_router, prefix="/api")
        print("🧠 Route defined: /api/agent/* -> agent_routes")
    except Exception as e:
        print(f"⚠️ Failed to register agent_router: {e}")
    
    # Register the memory_router
    try:
        print(f"🔍 DEBUG: Memory router object: {memory_router}")
        app.include_router(memory_router, prefix="/api")
        print("🧠 Route defined: /api/memory/* -> memory_routes")
    except Exception as e:
        print(f"⚠️ Failed to register memory_router: {e}")
    
    # Register the system_router
    try:
        print(f"🔍 DEBUG: System router object: {system_router}")
        app.include_router(system_router, prefix="/api")
        print("🧠 Route defined: /api/system/* -> system_routes")
    except Exception as e:
        print(f"⚠️ Failed to register system_router: {e}")
    
    # Register the debug_router
    try:
        print(f"🔍 DEBUG: Debug router object: {debug_router}")
        app.include_router(debug_router, prefix="/api")
        print("🧠 Route defined: /api/debug/* -> debug_routes")
    except Exception as e:
        print(f"⚠️ Failed to register debug_router: {e}")
    
    # Register the hal_router
    try:
        print(f"🔍 DEBUG: HAL router object: {hal_router}")
        app.include_router(hal_router, prefix="/api")
        print("🧠 Route defined: /api/hal/* -> hal_routes")
    except Exception as e:
        print(f"⚠️ Failed to register hal_router: {e}")
    
    # Register the snapshot_router
    try:
        print(f"🔍 DEBUG: Snapshot router object: {snapshot_router}")
        app.include_router(snapshot_router, prefix="/api")
        print("🧠 Route defined: /api/snapshot/* -> snapshot_routes")
    except Exception as e:
        print(f"⚠️ Failed to register snapshot_router: {e}")
    
    # Register the integrity_router
    try:
        print(f"🔍 DEBUG: Integrity router object: {integrity_router}")
        app.include_router(integrity_router, prefix="/api/system")
        print("🧠 Route defined: /api/system/integrity -> check_system_integrity")
    except Exception as e:
        print(f"⚠️ Failed to register integrity_router: {e}")
    
    # Register other routers with safeguards
    try:
        # Import and mount the agent module router
        print(f"🔍 DEBUG: Agent Module router object: {agent_module_router}")
        app.include_router(agent_module_router, prefix="/api/modules/agent")
        print("🧠 Route defined: /api/modules/agent/run -> run_agent")
    except Exception as e:
        print(f"⚠️ Failed to register agent_module_router: {e}")
    
    try:
        # Import and mount the memory module router
        print(f"🔍 DEBUG: Memory Module router object: {memory_router_module}")
        app.include_router(memory_router_module, prefix="/api/modules/memory")
        print("🧠 Route defined: /api/modules/memory/write -> write_memory")
    except Exception as e:
        print(f"⚠️ Failed to register memory_router_module: {e}")
    
    try:
        # Import and mount the orchestrator module router
        print(f"🔍 DEBUG: Orchestrator Module router object: {orchestrator_router_module}")
        app.include_router(orchestrator_router_module, prefix="/api/modules/orchestrator")
        print("🧠 Route defined: /api/modules/orchestrator/scope -> scope_task")
    except Exception as e:
        print(f"⚠️ Failed to register orchestrator_router_module: {e}")
    
    try:
        # Import and mount the feedback router
        print(f"🔍 DEBUG: Feedback router object: {feedback_router}")
        app.include_router(feedback_router, prefix="/api/modules/feedback")
        print("🧠 Route defined: /api/modules/feedback/submit -> submit_feedback")
    except Exception as e:
        print(f"⚠️ Failed to register feedback_router: {e}")
    
    try:
        # Import and mount the user context router
        print(f"🔍 DEBUG: User Context router object: {user_context_router}")
        app.include_router(user_context_router, prefix="/api/modules/user_context")
        print("🧠 Route defined: /api/modules/user_context/get -> get_user_context")
    except Exception as e:
        print(f"⚠️ Failed to register user_context_router: {e}")
    
    try:
        # Import and mount the respond router
        print(f"🔍 DEBUG: Respond router object: {respond_router}")
        app.include_router(respond_router, prefix="/api/modules/respond")
        print("🧠 Route defined: /api/modules/respond/generate -> generate_response")

        # ✅ Directly expose at /api/respond for frontend access
        app.include_router(respond_router, prefix="/api/respond")
        print("🧠 Route defined: /api/respond -> respond_to_operator")
    except Exception as e:
        print(f"⚠️ Failed to register respond_router: {e}")
    
    try:
        # Import and mount the plan router
        print(f"🔍 DEBUG: Plan router object: {plan_router}")
        app.include_router(plan_router, prefix="/api/modules/plan")
        print("🧠 Route defined: /api/modules/plan/generate -> generate_plan")
    except Exception as e:
        print(f"⚠️ Failed to register plan_router: {e}")
    
    try:
        # Import and mount the project router
        print(f"🔍 DEBUG: Project router object: {project_router}")
        app.include_router(project_router, prefix="/api/modules/project")
        print("🧠 Route defined: /api/modules/project/create -> create_project")
    except Exception as e:
        print(f"⚠️ Failed to register project_router: {e}")
    
    try:
        # Mount the health router
        app.include_router(health_router, prefix="/api/health")
        print("🧠 Route defined: /api/health/check -> health_check")
    except Exception as e:
        print(f"⚠️ Failed to register health_router: {e}")
    
    # Add Swagger UI with custom configuration
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - API Documentation",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )
    
    # Mount static files for Swagger UI
    try:
        app.mount("/static", StaticFiles(directory="app/static"), name="static")
        print("✅ Static files mounted for Swagger UI")
    except Exception as e:
        print(f"⚠️ Failed to mount static files: {e}")
    
    # Add a catch-all route for debugging 404 errors
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"])
    async def catch_all(request: Request, path: str):
        """
        Catch-all route for debugging 404 errors.
        This helps identify missing routes during development.
        """
        logger.warning(f"404 Not Found: {request.method} {request.url}")
        logger.warning(f"Path: {path}")
        logger.warning(f"Headers: {request.headers}")
        
        # Return a more detailed 404 response for debugging
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"Route not found: {request.method} {path}",
                "timestamp": datetime.datetime.now().isoformat(),
                "available_routes": [
                    {"path": route.path, "methods": list(route.methods) if hasattr(route, "methods") else []} 
                    for route in app.routes if isinstance(route, APIRoute)
                ]
            }
        )
    
    # Final startup message
    print("✅ All routes registered successfully")
    print("🚀 Enhanced AI Agent System is ready to serve requests")
    
except Exception as e:
    # Global error handler for startup failures
    import traceback
    print(f"❌ CRITICAL ERROR during startup: {str(e)}")
    print(f"❌ Traceback: {traceback.format_exc()}")
    
    # Create a minimal FastAPI app for error reporting
    app = FastAPI(
        title="Enhanced AI Agent System (ERROR MODE)",
        description="Error recovery mode due to startup failure",
        version="1.0.0"
    )
    
    @app.get("/")
    async def error_root():
        return {
            "status": "error",
            "message": "Application is in error recovery mode due to startup failure",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    @app.get("/health")
    async def error_health():
        return {
            "status": "error",
            "message": "Application is in error recovery mode due to startup failure",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }
