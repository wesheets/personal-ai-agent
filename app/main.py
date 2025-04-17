from fastapi import FastAPI, APIRouter, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.routing import APIRoute
import os
import logging
import inspect
import re
import datetime
# Import dotenv with fallback
try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️ python-dotenv not installed, creating fallback")
    def load_dotenv():
        print("⚠️ Using fallback load_dotenv function")
        return None
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
    
    # Import project routes
    try:
        from routes.project_routes import router as project_routes_router
        print("✅ Successfully imported project_routes_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: project_routes — {e}")
        project_routes_router = APIRouter()
        @project_routes_router.get("/project/ping")
        def project_ping():
            return {"status": "Project router placeholder"}
    
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
            
    # Import system summary routes
    try:
        from routes.system_summary_routes import router as system_summary_router
        print("✅ Successfully imported system_summary_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: system_summary_routes — {e}")
        system_summary_router = APIRouter()
        @system_summary_router.get("/system/summary/ping")
        def system_summary_ping():
            return {"status": "System summary router placeholder"}
    
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

    # Add startup delay to ensure FastAPI is fully initialized before healthch
    
    # Register all routers with the API prefix
    print("🔄 Registering all routers with API prefix...")
    
    # Register orchestrator router
    app.include_router(orchestrator_router, prefix="/api")
    print("✅ Registered orchestrator_router at /api")
    
    # Register agent router
    app.include_router(agent_router, prefix="/api")
    print("✅ Registered agent_router at /api")
    
    # Register memory router
    app.include_router(memory_router, prefix="/api")
    print("✅ Registered memory_router at /api")
    
    # Register project routes router
    app.include_router(project_routes_router, prefix="/api")
    print("✅ Registered project_routes_router at /api")
    
    # Register system router
    app.include_router(system_router, prefix="/api")
    print("✅ Registered system_router at /api")
    
    # Register system summary router
    app.include_router(system_summary_router, prefix="/api/system")
    print("✅ Registered system_summary_router at /api/system")
    
    # Register debug router
    app.include_router(debug_router, prefix="/api")
    print("✅ Registered debug_router at /api")
    
    # Register HAL router
    app.include_router(hal_router, prefix="/api")
    print("✅ Registered hal_router at /api")
    
    # Register snapshot router
    app.include_router(snapshot_router, prefix="/api")
    print("✅ Registered snapshot_router at /api")
    
    # Register system integrity router
    app.include_router(integrity_router, prefix="/api/system")
    print("✅ Registered integrity_router at /api/system")
    
    # Register project start router
    app.include_router(start, prefix="/api/project")
    print("✅ Registered project start router at /api/project")
    
    # Register module routers
    app.include_router(agent_module_router, prefix="/api/modules")
    app.include_router(memory_router_module, prefix="/api/modules")
    app.include_router(orchestrator_router_module, prefix="/api/modules")
    app.include_router(feedback_router, prefix="/api/modules")
    app.include_router(user_context_router, prefix="/api/modules")
    app.include_router(respond_router, prefix="/api/modules")
    app.include_router(plan_router, prefix="/api/modules")
    app.include_router(project_router, prefix="/api/modules")
    print("✅ Registered all module routers at /api/modules")
    
    # Register memory thread and summarize routers
    app.include_router(memory_thread_router, prefix="/api")
    app.include_router(memory_summarize_router, prefix="/api")
    print("✅ Registered memory thread and summarize routers at /api")
    
    # Register health router
    app.include_router(health_router)
    print("✅ Registered health router")
    
    # Add catch-all route for debugging 404 errors
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
    
    # Debug aid for route validation - Phase 6.3.3
    print("\n🔍 DEBUG: Validating route registration for summary endpoints...")
    for route in app.routes:
        if "summary" in str(route.path):
            print(f"✅ ROUTE LOADED: {route.path} {route.methods}")
    print("🔍 DEBUG: Route validation complete\n")
    
    print("🚀 Enhanced AI Agent System is ready to serve requests")
    
except Exception as startup_error:
    # Global error handler for startup failures
    import traceback
    print(f"❌ CRITICAL ERROR during startup: {str(startup_error)}")
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
            "error": str(startup_error) if 'startup_error' in locals() else "unknown",
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    @app.get("/health")
    async def error_health():
        return {
            "status": "error",
            "message": "Application is in error recovery mode due to startup failure",
            "error": str(startup_error) if 'startup_error' in locals() else "unknown",
            "timestamp": datetime.datetime.now().isoformat()
        }
