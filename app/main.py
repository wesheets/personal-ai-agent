"""
Main application module for the Personal AI Agent system.

This module initializes the FastAPI application and registers all routes.
"""
import os
import sys
import datetime
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI(
    title="Personal AI Agent API",
    description="API for the Personal AI Agent system",
    version="0.1.0"
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

# Agent routes
try:
    from app.routes.agent_routes import router as agent_router
    loaded_routes.append("agent")
    print("✅ Agent routes loaded")
except ImportError as e:
    print(f"⚠️ Failed to load agent routes: {e}")
    failed_routes.append("agent")

# Memory routes
try:
    from app.routes.memory_routes import router as memory_router
    memory_routes_loaded = True
    loaded_routes.append("memory")
    print("✅ Memory routes loaded")
except ImportError as e:
    memory_routes_loaded = False
    print(f"⚠️ Failed to load memory routes: {e}")
    failed_routes.append("memory")

# Upload file routes
try:
    from app.routes.upload_file_routes import router as upload_file_router
    upload_file_routes_loaded = True
    loaded_routes.append("upload_file")
    print("✅ Upload file routes loaded")
except ImportError as e:
    upload_file_routes_loaded = False
    print(f"⚠️ Failed to load upload file routes: {e}")
    failed_routes.append("upload_file")

# Loop validation routes
try:
    from app.routes.loop_validation_routes import router as loop_validation_router
    loop_validation_routes_loaded = True
    loaded_routes.append("loop_validation")
    print("✅ Loop validation routes loaded")
except ImportError as e:
    loop_validation_routes_loaded = False
    print(f"⚠️ Failed to load loop validation routes: {e}")
    failed_routes.append("loop_validation")

# Plan generate routes
try:
    from app.routes.plan_generate_routes import router as plan_generate_router
    plan_generate_routes_loaded = True
    loaded_routes.append("plan_generate")
    print("✅ Plan generate routes loaded")
except ImportError as e:
    plan_generate_routes_loaded = False
    print(f"⚠️ Failed to load plan generate routes: {e}")
    failed_routes.append("plan_generate")

# Memory API routes
try:
    from app.routes.memory_api_routes import router as memory_api_router
    memory_api_routes_loaded = True
    loaded_routes.append("memory_api")
    print("✅ Memory API routes loaded")
except ImportError as e:
    memory_api_routes_loaded = False
    print(f"⚠️ Failed to load memory API routes: {e}")
    failed_routes.append("memory_api")

# Forge build routes
try:
    from app.routes.forge_build_routes import router as forge_build_router
    forge_build_routes_loaded = True
    loaded_routes.append("forge_build")
    print("✅ Forge build routes loaded")
except ImportError as e:
    forge_build_routes_loaded = False
    print(f"⚠️ Failed to load forge build routes: {e}")
    failed_routes.append("forge_build")

# Critic review routes
try:
    from app.routes.critic_review_routes import router as critic_review_router
    critic_review_routes_loaded = True
    loaded_routes.append("critic_review")
    print("✅ Critic review routes loaded")
except ImportError as e:
    critic_review_routes_loaded = False
    print(f"⚠️ Failed to load critic review routes: {e}")
    failed_routes.append("critic_review")

# Pessimist evaluation routes
try:
    from app.routes.pessimist_evaluation_routes import router as pessimist_evaluation_router
    pessimist_evaluation_routes_loaded = True
    loaded_routes.append("pessimist_evaluation")
    print("✅ Pessimist evaluation routes loaded")
except ImportError as e:
    pessimist_evaluation_routes_loaded = False
    print(f"⚠️ Failed to load pessimist evaluation routes: {e}")
    failed_routes.append("pessimist_evaluation")

# Sage beliefs routes
try:
    from app.routes.sage_beliefs_routes import router as sage_beliefs_router
    sage_beliefs_routes_loaded = True
    loaded_routes.append("sage_beliefs")
    print("✅ Sage beliefs routes loaded")
except ImportError as e:
    sage_beliefs_routes_loaded = False
    print(f"⚠️ Failed to load sage beliefs routes: {e}")
    failed_routes.append("sage_beliefs")

# Health monitor routes - Hard-wired registration
try:
    from app.routes.health_monitor_routes import router as health_monitor_router
    # Only include if not already included above
    if "health_monitor" not in loaded_routes:
        app.include_router(health_monitor_router)
        loaded_routes.append("health_monitor")
        print("✅ Health monitor routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load health monitor routes: {e}")
    if "health_monitor" not in failed_routes:
        failed_routes.append("health_monitor")

# Orchestrator contract routes - Hard-wired registration
try:
    from app.routes.orchestrator_contract_routes import router as orchestrator_contract_router
    # Only include if not already included above
    if "orchestrator_contract" not in loaded_routes:
        app.include_router(orchestrator_contract_router)
        loaded_routes.append("orchestrator_contract")
        print("✅ Orchestrator contract routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load orchestrator contract routes: {e}")
    if "orchestrator_contract" not in failed_routes:
        failed_routes.append("orchestrator_contract")

# Snapshot routes - Hard-wired registration
try:
    from app.routes.snapshot_routes import router as snapshot_router
    # Only include if not already included above
    if "snapshot" not in loaded_routes:
        app.include_router(snapshot_router)
        loaded_routes.append("snapshot")
        print("✅ Snapshot routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load snapshot routes: {e}")
    if "snapshot" not in failed_routes:
        failed_routes.append("snapshot")

# Forge routes - Hard-wired registration (kept for backward compatibility)
try:
    from app.routes.forge_routes import router as forge_router
    # Only include if not already included above
    if "forge" not in loaded_routes:
        app.include_router(forge_router)
        loaded_routes.append("forge")
        print("✅ Forge routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load forge routes: {e}")
    if "forge" not in failed_routes:
        failed_routes.append("forge")

# Debug Analyzer routes - Hard-wired registration
try:
    from app.routes.debug_routes import router as debug_analyzer_router
    # Only include if not already included above
    if "debug_analyzer" not in loaded_routes:
        app.include_router(debug_analyzer_router)
        loaded_routes.append("debug_analyzer")
        print("✅ Debug Analyzer routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load Debug Analyzer routes: {e}")
    if "debug_analyzer" not in failed_routes:
        failed_routes.append("debug_analyzer")

# Drift routes - Hard-wired registration (kept for backward compatibility)
try:
    from app.routes.drift_routes import router as drift_router
    # Only include if not already included above
    if "drift_routes" not in loaded_routes:
        app.include_router(drift_router)
        loaded_routes.append("drift")
        print("✅ Drift routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load Drift routes: {e}")
    if "drift" not in failed_routes:
        failed_routes.append("drift")

# Output Policy routes - Hard-wired registration (kept for backward compatibility)
try:
    from app.routes.output_policy_routes import router as output_policy_router
    # Only include if not already included above
    if "output_policy_routes" not in loaded_routes:
        app.include_router(output_policy_router)
        loaded_routes.append("output_policy")
        print("✅ Output Policy routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load Output Policy routes: {e}")
    if "output_policy" not in failed_routes:
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
    # Compile response from internal state and log files
    response = {
        "loaded_routes": loaded_routes,
        "failed_routes": failed_routes,
        "fallbacks_triggered": fallbacks_triggered,
        "timestamp": str(datetime.datetime.now())
    }
    
    # Save diagnostics to log file
    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/final_route_status.json", "w") as f:
            json.dump(response, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save route diagnostics: {e}")
    
    return response

app.include_router(diagnostics_router)
app.include_router(agent_router)
app.include_router(memory_router)
app.include_router(upload_file_router)

# Include the new endpoint routers with proper error handling
if forge_build_routes_loaded:
    try:
        app.include_router(forge_build_router)
        print("✅ Included forge_build_router")
    except Exception as e:
        print(f"⚠️ Failed to include forge_build_router: {e}")

if critic_review_routes_loaded:
    try:
        app.include_router(critic_review_router)
        print("✅ Included critic_review_router")
    except Exception as e:
        print(f"⚠️ Failed to include critic_review_router: {e}")

if pessimist_evaluation_routes_loaded:
    try:
        app.include_router(pessimist_evaluation_router)
        print("✅ Included pessimist_evaluation_router")
    except Exception as e:
        print(f"⚠️ Failed to include pessimist_evaluation_router: {e}")

if sage_beliefs_routes_loaded:
    try:
        app.include_router(sage_beliefs_router)
        print("✅ Included sage_beliefs_router")
    except Exception as e:
        print(f"⚠️ Failed to include sage_beliefs_router: {e}")

loaded_routes.append("diagnostics_routes")
print("✅ Included diagnostics_router")

# Register loaded routes in manifest if manifest is initialized
if manifest_initialized:
    try:
        register_loaded_routes(loaded_routes)
        print(f"✅ Registered {len(loaded_routes)} routes in system manifest")
    except Exception as e:
        print(f"⚠️ Failed to register loaded routes in system manifest: {e}")

# Log final route status
try:
    import os
    import json
    os.makedirs("logs", exist_ok=True)
    
    final_status = {
        "timestamp": str(datetime.datetime.now()),
        "loaded_routes": loaded_routes,
        "failed_routes": failed_routes,
        "fallbacks_triggered": fallbacks_triggered
    }
    
    with open("logs/final_route_status.json", "w") as f:
        json.dump(final_status, f, indent=2)
    
    print(f"✅ Logged final route status: {len(loaded_routes)} loaded, {len(failed_routes)} failed")
except Exception as e:
    print(f"⚠️ Failed to log final route status: {e}")

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# clean deploy
# force clean rebuild Fri Apr 25 20:26:00 UTC 2025
# force clean build Fri Apr 25 20:53:47 UTC 2025
