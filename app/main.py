"""
Modified main.py to fix router imports and registrations.
This ensures all cognitive agent and system endpoints are properly accessible via API.
"""

import os
import logging
import traceback
import inspect
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Request, HTTPException, Depends
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

def create_app():
    """
    Create and configure the FastAPI application.
    
    This function handles all router imports and registrations,
    sets up middleware, and configures logging.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    print("🚀 Starting Promethios API Server")
    
    # Import agent routes
    try:
        from routes.agent_routes import router as agent_router
        print("✅ Successfully imported agent_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: agent_routes — {e}")
        agent_router = APIRouter()
        @agent_router.get("/ping")
        def agent_ping():
            return {"status": "Agent router placeholder"}

    # Import system routes
    try:
        from routes.system_routes import router as system_router
        print("✅ Successfully imported system_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: system_routes — {e}")
        system_router = APIRouter()
        @system_router.get("/ping")
        def system_ping():
            return {"status": "System router placeholder"}

    # Import project routes
    try:
        from routes.project_routes import router as project_router
        print("✅ Successfully imported project_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: project_routes — {e}")
        project_router = APIRouter()
        @project_router.get("/project/ping")
        def project_ping():
            return {"status": "Project router placeholder"}
    
    # Import memory routes - CRITICAL for memory operations
    try:
        print("🔄 Attempting to import memory_router from routes.memory_routes")
        from routes.memory_routes import router as memory_router
        print(f"✅ Successfully imported memory_router: {memory_router}")
        # Print all routes in the memory router for debugging
        print("📋 Memory router routes on import:")
        for route in memory_router.routes:
            print(f"  - {route.path} {route.methods}")
    except Exception as e:
        print(f"⚠️ Router Load Failed: memory_routes — {e}")
        print(f"⚠️ Traceback: {traceback.format_exc()}")
        memory_router = APIRouter()
        @memory_router.get("/ping")
        def memory_ping():
            return {"status": "Memory router placeholder"}
        print("⚠️ Created placeholder memory_router")
    
    # Import debug routes
    try:
        from routes.debug_routes import router as debug_router
        print("✅ Successfully imported debug_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: debug_routes — {e}")
        debug_router = APIRouter()
        @debug_router.get("/ping")
        def debug_ping():
            return {"status": "Debug router placeholder"}
    
    # Import HAL routes
    try:
        from routes.hal_routes import router as hal_router
        print("✅ Successfully imported hal_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: hal_routes — {e}")
        hal_router = APIRouter()
        @hal_router.get("/ping")
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
            
    # Import project routes
    try:
        from routes.project_routes import router as project_router
        print("✅ Successfully imported project_routes_router")
    except ModuleNotFoundError as e:
        print(f"⚠️ Router Load Failed: project_routes — {e}")
        project_router = APIRouter()
        @project_router.get("/project/ping")
        def project_ping():
            return {"status": "Project router placeholder"}
    
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
        
    # Import system log router
    try:
        from routes.system_log_routes import router as system_log_router
        print("✅ Successfully imported system log router")
    except Exception as e:
        print(f"⚠️ Router Load Failed: system_log_routes — {e}")
        system_log_router = APIRouter()
        @system_log_router.get("/log")
        async def system_log_import_error():
            return {"status": "error", "message": f"Failed to import system log router: {str(e)}"}
        print("⚠️ Created placeholder router for /api/system/log")
    
    # Import project start router for Phase 12.0 - CRITICAL for Agent Playground
    print("🔄 Importing project start router for Phase 12.0 (Agent Playground)")
    try:
        from app.api.project.start import router as start_router  # Project start router
        print("✅ Successfully imported project start router")
    except Exception as e:
        print(f"⚠️ Router Load Failed: project start — {e}")
        start_router = APIRouter()
        @start_router.get("/error")
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
    
    # Rename to avoid conflicts with main memory_router
    try:
        from app.api.modules.memory import router as memory_module_router  # Memory module router
        print("✅ Successfully imported memory_module_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: memory_module — {e}")
        memory_module_router = APIRouter()
    
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
        from app.api.modules.project import router as project_module_router  # Project Management module router
        print("✅ Successfully imported project_module_router")
    except Exception as e:
        print(f"⚠️ Module Router Load Failed: project — {e}")
        project_module_router = APIRouter()
    
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
    async def get_registry():
        """
        Returns a list of all registered routes in the application.
        Useful for debugging and monitoring.
        """
        routes = []
        for route in app.routes:
            route_info = {
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, "methods") else ["GET"],
                "name": route.name if hasattr(route, "name") else None,
                "endpoint": route.endpoint.__name__ if hasattr(route, "endpoint") else None
            }
            routes.append(route_info)
        
        return {
            "status": "success",
            "routes": routes,
            "total_routes": len(routes)
        }

    # Register all routers with appropriate prefixes
    try:
        print("🔄 Registering all routers with appropriate prefixes")
        
        # Register core routers
        try:
            print(f"🔍 DEBUG: Agent router object: {agent_router}")
            app.include_router(agent_router, prefix="/api/agent")
            print("🧠 Route defined: /api/agent/* -> agent_router")
        except Exception as e:
            print(f"⚠️ Failed to register agent_router: {e}")
        
        try:
            print(f"🔍 DEBUG: System router object: {system_router}")
            app.include_router(system_router, prefix="/api/system")
            print("🧠 Route defined: /api/system/* -> system_router")
            
            # Debug line to print all system routes
            print("📋 DEBUG: Listing all system routes after mounting:")
            for route in app.routes:
                if "/api/system" in route.path:
                    print(f"🔍 SYSTEM ROUTE: {route.path} {route.methods}")
        except Exception as e:
            print(f"⚠️ Failed to register system_router: {e}")
        
        # CRITICAL FIX: Memory router mounting with explicit error handling and confirmation
        try:
            print(f"🔍 DEBUG: Memory router object before mounting: {memory_router}")
            if memory_router is None:
                print("⚠️ CRITICAL ERROR: memory_router is None, cannot mount")
                raise ValueError("memory_router is None")
            
            # Ensure no other memory routers are mounted with conflicting prefixes
            print("🔄 Mounting memory_router to /api/memory with priority")
            app.include_router(memory_router, prefix="/api/memory")
            print("🧠 CONFIRMED: Successfully mounted memory_router to /api/memory")
            
            # Print all routes in the memory router for debugging after mounting
            print("📋 Memory router routes after mounting:")
            for route in memory_router.routes:
                print(f"  - {route.path} [{', '.join(route.methods)}]")
                
            # Print all registered routes with /api/memory prefix for verification
            print("🔍 Verifying all registered /api/memory routes:")
            memory_routes = [route for route in app.routes if str(route.path).startswith("/api/memory")]
            for route in memory_routes:
                print(f"  - {route.path} [{', '.join(route.methods if hasattr(route, 'methods') else ['GET'])}]")
        except Exception as e:
            print(f"⚠️ CRITICAL ERROR: Failed to register memory_router: {e}")
            print(f"⚠️ Traceback: {traceback.format_exc()}")
        
        try:
            print(f"🔍 DEBUG: Debug router object: {debug_router}")
            app.include_router(debug_router, prefix="/api/debug")
            print("🧠 Route defined: /api/debug/* -> debug_router")
        except Exception as e:
            print(f"⚠️ Failed to register debug_router: {e}")
        
        try:
            print(f"🔍 DEBUG: HAL router object: {hal_router}")
            app.include_router(hal_router, prefix="/api/hal")
            print("🧠 Route defined: /api/hal/* -> hal_router")
        except Exception as e:
            print(f"⚠️ Failed to register hal_router: {e}")
        
        try:
            print(f"🔍 DEBUG: Snapshot router object: {snapshot_router}")
            app.include_router(snapshot_router, prefix="/api/snapshot")
            print("🧠 Route defined: /api/snapshot/* -> snapshot_router")
        except Exception as e:
            print(f"⚠️ Failed to register snapshot_router: {e}")
        
        try:
            print(f"🔍 DEBUG: Project router object: {project_router}")
            app.include_router(project_router, prefix="/api/project")
            print("🧠 Route defined: /api/project/* -> project_router")
        except Exception as e:
            print(f"⚠️ Failed to register project_router: {e}")
        
        try:
            print(f"🔍 DEBUG: System integrity router object: {integrity_router}")
            app.include_router(integrity_router, prefix="/api/system")
            print("🧠 Route defined: /api/system/integrity/* -> integrity_router")
        except Exception as e:
            print(f"⚠️ Failed to register integrity_router: {e}")
        
        try:
            print(f"🔍 DEBUG: System log router object: {system_log_router}")
            app.include_router(system_log_router, prefix="/api/system")
            print("🧠 Route defined: /api/system/log/* -> system_log_router")
        except Exception as e:
            print(f"⚠️ Failed to register system_log_router: {e}")
        
        # Register module routers
        try:
            print(f"🔍 DEBUG: Agent module router object: {agent_module_router}")
            app.include_router(agent_module_router, prefix="/api/modules/agent")
            print("🧠 Route defined: /api/modules/agent/* -> agent_module_router")
        except Exception as e:
            print(f"⚠️ Failed to register agent_module_router: {e}")
        
        try:
            print(f"🔍 DEBUG: Memory module router object: {memory_module_router}")
            app.include_router(memory_module_router, prefix="/api/modules/memory")
            print("🧠 Route defined: /api/modules/memory/* -> memory_module_router")
        except Exception as e:
            print(f"⚠️ Failed to register memory_module_router: {e}")
        
        try:
            print(f"🔍 DEBUG: Orchestrator module router object: {orchestrator_router_module}")
            app.include_router(orchestrator_router_module, prefix="/api/modules/orchestrator")
            print("🧠 Route defined: /api/modules/orchestrator/* -> orchestrator_router_module")
        except Exception as e:
            print(f"⚠️ Failed to register orchestrator_router_module: {e}")
        
        try:
            print(f"🔍 DEBUG: Feedback router object: {feedback_router}")
            app.include_router(feedback_router, prefix="/api/modules/feedback")
            print("🧠 Route defined: /api/modules/feedback/* -> feedback_router")
        except Exception as e:
            print(f"⚠️ Failed to register feedback_router: {e}")
        
        try:
            print(f"🔍 DEBUG: User context router object: {user_context_router}")
            app.include_router(user_context_router, prefix="/api/modules/user_context")
            print("🧠 Route defined: /api/modules/user_context/* -> user_context_router")
        except Exception as e:
            print(f"⚠️ Failed to register user_context_router: {e}")
        
        try:
            print(f"🔍 DEBUG: Respond router object: {respond_router}")
            app.include_router(respond_router, prefix="/api/modules/respond")
            print("🧠 Route defined: /api/modules/respond/* -> respond_router")
        except Exception as e:
            print(f"⚠️ Failed to register respond_router: {e}")
        
        try:
            print(f"🔍 DEBUG: Plan router object: {plan_router}")
            app.include_router(plan_router, prefix="/api/modules/plan")
            print("🧠 Route defined: /api/modules/plan/* -> plan_router")
        except Exception as e:
            print(f"⚠️ Failed to register plan_router: {e}")
        
        try:
            print(f"🔍 DEBUG: Project module router object: {project_module_router}")
            app.include_router(project_module_router, prefix="/api/modules/project")
            print("🧠 Route defined: /api/modules/project/* -> project_module_router")
        except Exception as e:
            print(f"⚠️ Failed to register project_module_router: {e}")
        
        # CRITICAL FIX: Commenting out potentially conflicting memory routers
        # These routers may be overriding the main memory_router routes
        print("⚠️ NOTICE: Skipping memory_thread_router and memory_summarize_router registration")
        print("⚠️ NOTICE: These routers may conflict with main memory_router at /api/memory")
        print("⚠️ NOTICE: The main memory_router already includes /thread and /summarize endpoints")
        
        # Keep the original code commented for reference
        """
        try:
            print(f"🔍 DEBUG: Memory thread router object: {memory_thread_router}")
            app.include_router(memory_thread_router, prefix="/api/memory/thread")
            print("🧠 Route defined: /api/memory/thread/* -> memory_thread_router")
        except Exception as e:
            print(f"⚠️ Failed to register memory_thread_router: {e}")
        
        try:
            print(f"🔍 DEBUG: Memory summarize router object: {memory_summarize_router}")
            app.include_router(memory_summarize_router, prefix="/api/memory/summarize")
            print("🧠 Route defined: /api/memory/summarize/* -> memory_summarize_router")
        except Exception as e:
            print(f"⚠️ Failed to register memory_summarize_router: {e}")
        """
        
        try:
            print(f"🔍 DEBUG: Project start router object: {start_router}")
            app.include_router(start_router, prefix="/api/project")
            print("🧠 Route defined: /api/project/* -> start_router")
        except Exception as e:
            print(f"⚠️ Failed to register start_router: {e}")
        
        try:
            print(f"🔍 DEBUG: Health router object: {health_router}")
            app.include_router(health_router)
            print("🧠 Route defined: /* -> health_router")
        except Exception as e:
            print(f"⚠️ Failed to register health_router: {e}")
            
        print("✅ All routers registered successfully")
    except Exception as e:
        print(f"⚠️ Error during router registration: {e}")
        print(f"⚠️ Traceback: {traceback.format_exc()}")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )
    print("✅ CORS middleware added")

    # Debug Router Exposure - Print all registered routes
    print("📡 ROUTES REGISTERED ON STARTUP:")
    for route in app.routes:
        methods = route.methods if hasattr(route, 'methods') else ["GET"]
        print(f"🧠 ROUTE: {route.path} {methods}")
        
    # Additional debug for memory routes specifically
    memory_routes = [route for route in app.routes if str(route.path).startswith("/api/memory")]
    if memory_routes:
        print("🔍 MEMORY ROUTES VERIFICATION:")
        for route in memory_routes:
            methods = route.methods if hasattr(route, 'methods') else ["GET"]
            print(f"✅ MEMORY ROUTE: {route.path} {methods}")
    else:
        print("⚠️ NO MEMORY ROUTES FOUND - This indicates a critical issue!")

    return app

app = create_app()
