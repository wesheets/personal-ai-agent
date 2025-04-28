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

# Core Router Wiring - Phase 2.6 Batch 1.1 # memory_tag: phase2.6_batch1.1_core_router_wiring
try:
    from app.routes.agent_routes import router as agent_router
    from app.routes.memory_routes import router as memory_router
    from app.routes.loop_routes import router as loop_router
    
    # Include core routers with proper API prefixes
    app.include_router(agent_router, prefix="/api/agent")
    app.include_router(memory_router, prefix="/api/memory")
    app.include_router(loop_router, prefix="/api/loop")
    
    loaded_routes.extend(["agent", "memory", "loop"])
    print("✅ Core routers (agent, memory, loop) loaded with proper API prefixes")
except ImportError as e:
    print(f"⚠️ Failed to load core routers: {e}")
    failed_routes.extend(["agent", "memory", "loop"])

# Reflection and Drift Router Wiring - Phase 2.6 Batch 1.2 # memory_tag: phase2.6_batch1.2_reflection_drift_wiring
try:
    from app.routes.reflection_routes import router as reflection_router
    from app.routes.drift_routes import router as drift_router
    
    # Include reflection and drift routers with proper API prefixes
    app.include_router(reflection_router, prefix="/api/reflection")
    app.include_router(drift_router, prefix="/api/drift")
    
    loaded_routes.extend(["reflection", "drift"])
    print("✅ Reflection and Drift routers loaded with proper API prefixes")
except ImportError as e:
    print(f"⚠️ Failed to load reflection and drift routers: {e}")
    failed_routes.extend(["reflection", "drift"])

# Execution and Planning Router Wiring - Phase 2.6 Batch 1.3 # memory_tag: phase2.6_batch1.3_execution_planning_router_wiring
try:
    from app.routes.plan_routes import router as plan_router
    from app.routes.train_routes import router as train_router
    from app.routes.execute_routes import router as execute_router
    
    # Include execution and planning routers with proper API prefixes
    app.include_router(plan_router, prefix="/api/plan")
    app.include_router(train_router, prefix="/api/train")
    app.include_router(execute_router, prefix="/api/execute")
    
    loaded_routes.extend(["plan", "train", "execute"])
    print("✅ Execution and Planning routers (plan, train, execute) loaded with proper API prefixes")
except ImportError as e:
    print(f"⚠️ Failed to load execution and planning routers: {e}")
    failed_routes.extend(["plan", "train", "execute"])

# Memory Utility Router Wiring - Phase 2.6 Batch 1.4 # memory_tag: phase2.6_batch1.4_memory_utility_router_wiring
try:
    from app.routes.snapshot_routes import router as snapshot_router
    
    # Include memory utility router with proper API prefix
    app.include_router(snapshot_router, prefix="/api/snapshot")
    
    loaded_routes.append("snapshot")
    print("✅ Memory Utility router (snapshot) loaded with proper API prefix")
except ImportError as e:
    print(f"⚠️ Failed to load memory utility router: {e}")
    failed_routes.append("snapshot")

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

# Health monitor routes
try:
    from app.routes.health_monitor_routes import router as health_monitor_router
    health_monitor_routes_loaded = True
    loaded_routes.append("health_monitor")
    print("✅ Health monitor routes loaded")
except ImportError as e:
    health_monitor_routes_loaded = False
    print(f"⚠️ Failed to load health monitor routes: {e}")
    failed_routes.append("health_monitor")

# Orchestrator contract routes
try:
    from app.routes.orchestrator_contract_routes import router as orchestrator_contract_router
    orchestrator_contract_routes_loaded = True
    loaded_routes.append("orchestrator_contract")
    print("✅ Orchestrator contract routes loaded")
except ImportError as e:
    orchestrator_contract_routes_loaded = False
    print(f"⚠️ Failed to load orchestrator contract routes: {e}")
    failed_routes.append("orchestrator_contract")

# Forge routes (kept for backward compatibility)
try:
    from app.routes.forge_routes import router as forge_router
    forge_routes_loaded = True
    loaded_routes.append("forge")
    print("✅ Forge routes loaded")
except ImportError as e:
    forge_routes_loaded = False
    print(f"⚠️ Failed to load forge routes: {e}")
    failed_routes.append("forge")

# Debug Analyzer routes
try:
    from app.routes.debug_routes import router as debug_analyzer_router
    debug_analyzer_routes_loaded = True
    loaded_routes.append("debug_analyzer")
    print("✅ Debug Analyzer routes loaded")
except ImportError as e:
    debug_analyzer_routes_loaded = False
    print(f"⚠️ Failed to load Debug Analyzer routes: {e}")
    failed_routes.append("debug_analyzer")

# Output Policy routes (kept for backward compatibility)
try:
    from app.routes.output_policy_routes import router as output_policy_router
    output_policy_routes_loaded = True
    loaded_routes.append("output_policy")
    print("✅ Output Policy routes loaded")
except ImportError as e:
    output_policy_routes_loaded = False
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

# Include all routers with proper error handling
# First include the diagnostics router
app.include_router(diagnostics_router)
loaded_routes.append("diagnostics_routes")
print("✅ Included diagnostics_router")

# Include upload file router
if upload_file_routes_loaded:
    try:
        app.include_router(upload_file_router)
        print("✅ Included upload_file_router")
    except Exception as e:
        print(f"⚠️ Failed to include upload_file_router: {e}")

# Include API endpoint routers
if memory_api_routes_loaded:
    try:
        app.include_router(memory_api_router)
        print("✅ Included memory_api_router")
    except Exception as e:
        print(f"⚠️ Failed to include memory_api_router: {e}")

if loop_validation_routes_loaded:
    try:
        app.include_router(loop_validation_router)
        print("✅ Included loop_validation_router")
    except Exception as e:
        print(f"⚠️ Failed to include loop_validation_router: {e}")

if plan_generate_routes_loaded:
    try:
        app.include_router(plan_generate_router)
        print("✅ Included plan_generate_router")
    except Exception as e:
        print(f"⚠️ Failed to include plan_generate_router: {e}")

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

# Include legacy routers
if health_monitor_routes_loaded:
    try:
        app.include_router(health_monitor_router)
        print("✅ Included health_monitor_router")
    except Exception as e:
        print(f"⚠️ Failed to include health_monitor_router: {e}")

if orchestrator_contract_routes_loaded:
    try:
        app.include_router(orchestrator_contract_router)
        print("✅ Included orchestrator_contract_router")
    except Exception as e:
        print(f"⚠️ Failed to include orchestrator_contract_router: {e}")

if forge_routes_loaded:
    try:
        app.include_router(forge_router)
        print("✅ Included forge_router")
    except Exception as e:
        print(f"⚠️ Failed to include forge_router: {e}")

if debug_analyzer_routes_loaded:
    try:
        app.include_router(debug_analyzer_router)
        print("✅ Included debug_analyzer_router")
    except Exception as e:
        print(f"⚠️ Failed to include debug_analyzer_router: {e}")

if output_policy_routes_loaded:
    try:
        app.include_router(output_policy_router)
        print("✅ Included output_policy_router")
    except Exception as e:
        print(f"⚠️ Failed to include output_policy_router: {e}")

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
# comprehensive endpoint fix Sat Apr 26 10:41:30 UTC 2025
# core router wiring Mon Apr 28 01:12:00 UTC 2025
# reflection and drift router wiring Mon Apr 28 01:19:45 UTC 2025
# execution and planning router wiring Mon Apr 28 02:13:00 UTC 2025
# memory utility router wiring Mon Apr 28 02:30:00 UTC 2025
