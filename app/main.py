"""
Main application module for the Personal AI Agent system.

This module initializes the FastAPI application and registers all routes.
"""
import os
import sys

# Add project root to Python path to resolve import issues
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import datetime
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# --- Import Agent Modules to Trigger Registration --- 
# This ensures the @register decorators run when the app starts.
print("Importing agent modules for registration...")
try:
    import app.agents.forge_agent
    print("✅ Imported forge_agent")
except ImportError as e:
    print(f"⚠️ Failed to import forge_agent: {e}")
try:
    import app.agents.orchestrator_agent
    print("✅ Imported orchestrator_agent")
except ImportError as e:
    print(f"⚠️ Failed to import orchestrator_agent: {e}")
try:
    import app.agents.hal_agent
    print("✅ Imported hal_agent")
except ImportError as e:
    print(f"⚠️ Failed to import hal_agent: {e}")
try:
    import app.agents.nova_agent
    print("✅ Imported nova_agent")
except ImportError as e:
    print(f"⚠️ Failed to import nova_agent: {e}")
try:
    import app.agents.critic_agent
    print("✅ Imported critic_agent")
except ImportError as e:
    print(f"⚠️ Failed to import critic_agent: {e}")
try:
    import app.agents.sage_agent
    print("✅ Imported sage_agent")
except ImportError as e:
    print(f"⚠️ Failed to import sage_agent: {e}")
print("Finished importing agent modules.")
# --- End Agent Module Imports --- 

# Initialize FastAPI app
app = FastAPI(
    title="Personal AI Agent API",
    description="API for the Personal AI Agent system",
    version="0.1.1" # Incremented version for routing fixes
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tracking variables
loaded_routes = []
failed_routes = []
fallbacks_triggered = []
manifest_initialized = False

# Try to initialize system manifest
try:
    from app.core.system_manifest import register_loaded_routes
    manifest_initialized = True
    print("✅ System manifest initialized")
except ImportError as e:
    print(f"⚠️ Failed to initialize system manifest: {e}")

# Add status debug router for Render health check
try:
    from app.routes.status_debug import router as status_debug_router
    app.include_router(status_debug_router)
    loaded_routes.append("status_debug")
    print("✅ Status debug routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load status debug routes: {e}")
    failed_routes.append("status_debug")

# Core Router Wiring (Agent, Memory, Loop)
try:
    # --- Modified: Removed direct agent_routes import, using loop_controller now --- 
    # from app.routes.agent_routes import router as agent_router 
    # from app.modules.memory_writer import memory_store # Removed - Caused import error, functionality via memory_engine
    from app.routes.memory_routes import router as memory_router
    from app.routes.loop_routes import router as loop_router

    # Include core routers with proper API prefixes
    # app.include_router(agent_router, prefix="/api/agent") # Replaced by loop_router or specific agent endpoints
    app.include_router(memory_router, prefix="/api/memory")
    app.include_router(loop_router, prefix="/api/loop") # Assuming loop_routes handles loop initiation

    loaded_routes.extend(["memory", "loop"])
    print("✅ Core routers (memory, loop) loaded with proper API prefixes")
except ImportError as e:
    print(f"⚠️ Failed to load core routers: {e}")
    failed_routes.extend(["memory", "loop"])

# --- Removed HAL Router Wiring - Functionality should be via LoopController/AgentRegistry --- 
# try:
#     from app.routes.hal_routes import router as hal_router
#     app.include_router(hal_router, prefix="/api/agent")
#     loaded_routes.append("hal_agent_run") 
#     print("✅ HAL router loaded under /api/agent prefix")
# except ImportError as e:
#     print(f"⚠️ Failed to load HAL router: {e}")
#     failed_routes.append("hal_agent_run")

# Reflection and Drift Router Wiring
try:
    from app.routes.reflection_routes import router as reflection_router
    from app.routes.drift_routes import router as drift_router

    app.include_router(reflection_router, prefix="/api/reflection")
    app.include_router(drift_router, prefix="/api/drift")

    loaded_routes.extend(["reflection", "drift"])
    print("✅ Reflection and Drift routers loaded with proper API prefixes")
except ImportError as e:
    print(f"⚠️ Failed to load reflection and drift routers: {e}")
    failed_routes.extend(["reflection", "drift"])

# Execution and Planning Router Wiring
try:
    from app.routes.plan_routes import router as plan_router
    from app.routes.train_routes import router as train_router
    from app.routes.execute_routes import router as execute_router

    app.include_router(plan_router, prefix="/api/plan")
    app.include_router(train_router, prefix="/api/train")
    app.include_router(execute_router, prefix="/api/execute")

    loaded_routes.extend(["plan", "train", "execute"])
    print("✅ Execution and Planning routers (plan, train, execute) loaded with proper API prefixes")
except ImportError as e:
    print(f"⚠️ Failed to load execution and planning routers: {e}")
    failed_routes.extend(["plan", "train", "execute"])

# Memory Utility Router Wiring
try:
    from app.routes.snapshot_routes import router as snapshot_router
    app.include_router(snapshot_router, prefix="/api/snapshot")
    loaded_routes.append("snapshot")
    print("✅ Memory Utility router (snapshot) loaded with proper API prefix")
except ImportError as e:
    print(f"⚠️ Failed to load memory utility router: {e}")
    failed_routes.append("snapshot")

# Extended System Router Wiring (Project)
try:
    from routes.project_routes import router as project_router # Check path: might be app.routes.project_routes
    app.include_router(project_router, prefix="/api/project")
    loaded_routes.append("project")
    print("✅ Extended System router (project) loaded with proper API prefix")
except ImportError as e:
    print(f"⚠️ Failed to load extended system router: {e}")
    failed_routes.append("project")

# Upload file routes
try:
    from app.routes.upload_file_routes import router as upload_file_router
    app.include_router(upload_file_router, prefix="/api/upload")
    loaded_routes.append("upload_file")
    print("✅ Upload file routes loaded with /api/upload prefix")
except ImportError as e:
    print(f"⚠️ Failed to load upload file routes: {e}")
    failed_routes.append("upload_file")

# Memory API routes
try:
    from app.routes.memory_api_routes import router as memory_api_router
    app.include_router(memory_api_router, prefix="/api/memory_api")
    loaded_routes.append("memory_api")
    print("✅ Memory API routes loaded with /api/memory_api prefix")
except ImportError as e:
    print(f"⚠️ Failed to load memory API routes: {e}")
    failed_routes.append("memory_api")

# Loop validation routes
try:
    from app.routes.loop_validation_routes import router as loop_validation_router
    app.include_router(loop_validation_router, prefix="/api/validation")
    loaded_routes.append("loop_validation")
    print("✅ Loop validation routes loaded with /api/validation prefix")
except ImportError as e:
    print(f"⚠️ Failed to load loop validation routes: {e}")
    failed_routes.append("loop_validation")

# Plan generate routes
try:
    from app.routes.plan_generate_routes import router as plan_generate_router
    app.include_router(plan_generate_router, prefix="/api/plan/generate")
    loaded_routes.append("plan_generate")
    print("✅ Plan generate routes loaded with /api/plan/generate prefix")
except ImportError as e:
    print(f"⚠️ Failed to load plan generate routes: {e}")
    failed_routes.append("plan_generate")

# --- Removed specific agent routes (Forge, Critic, Sage) - Handled by LoopController --- 
# try:
#     from app.routes.forge_routes import router as forge_router
#     app.include_router(forge_router, prefix="/api/forge")
#     loaded_routes.append("forge")
#     print("✅ Forge routes loaded with /api/forge prefix")
# except ImportError as e:
#     print(f"⚠️ Failed to load forge routes: {e}")
#     failed_routes.append("forge")
# try:
#     from app.routes.critic_routes import router as critic_router
#     app.include_router(critic_router, prefix="/api/critic")
#     loaded_routes.append("critic")
#     print("✅ Critic routes loaded with /api/critic prefix")
# except ImportError as e:
#     print(f"⚠️ Failed to load critic routes: {e}")
#     failed_routes.append("critic")
# try:
#     from app.routes.sage_routes import router as sage_router
#     app.include_router(sage_router, prefix="/api/sage")
#     loaded_routes.append("sage")
#     print("✅ Sage routes loaded with /api/sage prefix")
# except ImportError as e:
#     print(f"⚠️ Failed to load sage routes: {e}")
#     failed_routes.append("sage")

# Pessimist evaluation routes
try:
    from app.routes.pessimist_evaluation_routes import router as pessimist_evaluation_router
    app.include_router(pessimist_evaluation_router, prefix="/api/pessimist")
    loaded_routes.append("pessimist_evaluation")
    print("✅ Pessimist evaluation routes loaded with /api/pessimist prefix")
except ImportError as e:
    print(f"⚠️ Failed to load pessimist evaluation routes: {e}")
    failed_routes.append("pessimist_evaluation")

# Health monitor routes
try:
    from app.routes.health_monitor_routes import router as health_monitor_router
    app.include_router(health_monitor_router, prefix="/api/health")
    loaded_routes.append("health_monitor")
    print("✅ Health monitor routes loaded with /api/health prefix")
except ImportError as e:
    print(f"⚠️ Failed to load health monitor routes: {e}")
    failed_routes.append("health_monitor")

# Orchestrator contract routes
try:
    from app.routes.orchestrator_contract_routes import router as orchestrator_contract_router
    app.include_router(orchestrator_contract_router, prefix="/api/orchestrator/contract")
    loaded_routes.append("orchestrator_contract")
    print("✅ Orchestrator contract routes loaded with /api/orchestrator/contract prefix")
except ImportError as e:
    print(f"⚠️ Failed to load orchestrator contract routes: {e}")
    failed_routes.append("orchestrator_contract")

# Debug Analyzer routes
try:
    from app.routes.debug_routes import router as debug_analyzer_router
    app.include_router(debug_analyzer_router, prefix="/api/debug")
    loaded_routes.append("debug_analyzer")
    print("✅ Debug Analyzer routes loaded with /api/debug prefix")
except ImportError as e:
    print(f"⚠️ Failed to load Debug Analyzer routes: {e}")
    failed_routes.append("debug_analyzer")

# Output Policy routes
try:
    from app.routes.output_policy_routes import router as output_policy_router
    app.include_router(output_policy_router, prefix="/api/policy")
    loaded_routes.append("output_policy")
    print("✅ Output Policy routes loaded with /api/policy prefix")
except ImportError as e:
    print(f"⚠️ Failed to load Output Policy routes: {e}")
    failed_routes.append("output_policy")

# Add diagnostics endpoint
from fastapi import APIRouter
import os
import json
diagnostics_router = APIRouter(tags=["diagnostics"])

@diagnostics_router.get("/diagnostics/routes")
async def get_routes_diagnostics():
    """
    Get diagnostics information about loaded and failed routes.
    """
    response = {
        "loaded_routes": sorted(list(set(loaded_routes))), 
        "failed_routes": sorted(list(set(failed_routes))), 
        "fallbacks_triggered": fallbacks_triggered,
        "timestamp": str(datetime.datetime.now())
    }
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/final_route_status.json", "w") as f:
            json.dump(response, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save route diagnostics: {e}")
    return response

app.include_router(diagnostics_router)
loaded_routes.append("diagnostics_routes")
print("✅ Included diagnostics_router")

# Register loaded routes in manifest if manifest is initialized
if manifest_initialized:
    try:
        register_loaded_routes(sorted(list(set(loaded_routes))))
        print(f"✅ Registered {len(set(loaded_routes))} unique routes in system manifest")
    except Exception as e:
        print(f"⚠️ Failed to register loaded routes in system manifest: {e}")

# Log final route status
try:
    import os
    import json
    os.makedirs("logs", exist_ok=True)
    final_status = {
        "timestamp": str(datetime.datetime.now()),
        "loaded_routes": sorted(list(set(loaded_routes))),
        "failed_routes": sorted(list(set(failed_routes))),
        "fallbacks_triggered": fallbacks_triggered
    }
    with open("logs/final_route_status.json", "w") as f:
        json.dump(final_status, f, indent=2)
    print(f"✅ Logged final route status: {len(set(loaded_routes))} loaded, {len(set(failed_routes))} failed")
except Exception as e:
    print(f"⚠️ Failed to log final route status: {e}")

# Run the application
if __name__ == "__main__":
    # Ensure necessary directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("memory", exist_ok=True) 
    
    # Configure logging (basic example)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)
    logger.info("Starting Personal AI Agent API...")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False) # Use string format for uvicorn

