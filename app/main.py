"""
Update to main.py to register SAGE routes, Dashboard routes, FORGE routes, and Debug Analyzer routes
"""
from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
import datetime
from app.routes.agent_routes import router as agent_router
# Load memory routes with try/except for proper variable definition
try:
    from app.routes.memory_routes import router as memory_router
    routes_memory_loaded = True
    print("✅ Loaded memory_router")
except ImportError:
    routes_memory_loaded = False
    print("⚠️ Failed to load memory_router")
# Import file upload routes with try-except for safer handling
try:
    from app.routes.upload_file_routes import router as upload_file_router
    upload_file_routes_loaded = True
    print("✅ Directly loaded upload_file_routes")
except ImportError:
    upload_file_routes_loaded = False
    print("⚠️ Could not load upload_file_routes directly")
# Import the new endpoint routers with try-except for safer handling
try:
    from app.routes.forge_build_routes import router as forge_build_router
    forge_build_routes_loaded = True
    print("✅ Loaded forge_build_router")
except ImportError:
    forge_build_routes_loaded = False
    print("⚠️ Failed to load forge_build_router")

try:
    from app.routes.critic_review_routes import router as critic_review_router
    critic_review_routes_loaded = True
    print("✅ Loaded critic_review_router")
except ImportError:
    critic_review_routes_loaded = False
    print("⚠️ Failed to load critic_review_router")

try:
    from app.routes.pessimist_evaluation_routes import router as pessimist_evaluation_router
    pessimist_evaluation_routes_loaded = True
    print("✅ Loaded pessimist_evaluation_router")
except ImportError:
    pessimist_evaluation_routes_loaded = False
    print("⚠️ Failed to load pessimist_evaluation_router")

try:
    from app.routes.sage_beliefs_routes import router as sage_beliefs_router
    sage_beliefs_routes_loaded = True
    print("✅ Loaded sage_beliefs_router")
except ImportError:
    sage_beliefs_routes_loaded = False
    print("⚠️ Failed to load sage_beliefs_router")

try:
    from app.routes.plan_generate_routes import router as plan_generate_router
    plan_generate_routes_loaded = True
    print("✅ Loaded plan_generate_router")
except ImportError:
    plan_generate_routes_loaded = False
    print("⚠️ Failed to load plan_generate_router")

# Import schema validation integration
try:
    from app.core.schema_validation_integration import add_schema_validation_middleware
    schema_validation_loaded = True
    print("✅ Schema validation middleware loaded")
except ImportError:
    schema_validation_loaded = False
    print("⚠️ Could not load schema validation middleware")
# Import routes
from app.routes.agent_config_routes import router as agent_config_router
from app.routes.agent_context_routes import router as agent_context_router
from app.routes.memory_recall_routes import router as memory_recall_router
from app.routes.memory_embed_routes import router as memory_embed_router
from app.routes.train_routes import router as train_router
from app.routes.export_routes import router as export_router
from app.routes.fix_routes import router as fix_router
from app.routes.delegate_stream_routes import router as delegate_stream_router
# Import file upload routes
try:
    from app.routes.upload_file_routes import router as upload_file_router
    upload_file_routes_loaded = True
    print("✅ Directly loaded upload_file_routes")
except ImportError:
    upload_file_routes_loaded = False
    print("⚠️ Could not load upload_file_routes directly")
# Import missing routes identified in diagnostic report
try:
    from app.routes.snapshot_routes import router as snapshot_router
    snapshot_routes_loaded = True
    print("✅ Directly loaded snapshot_routes")
except ImportError:
    snapshot_routes_loaded = False
    print("⚠️ Could not load snapshot_routes directly")
try:
    from app.routes.orchestrator_plan_routes import router as orchestrator_plan_router
    orchestrator_plan_routes_loaded = True
    print("✅ Directly loaded orchestrator_plan_routes")
except ImportError:
    orchestrator_plan_routes_loaded = False
    print("⚠️ Could not load orchestrator_plan_routes directly")
try:
    from app.routes.health_monitor_routes import router as health_monitor_router
    health_monitor_routes_loaded = True
    print("✅ Directly loaded health_monitor_routes")
except ImportError:
    health_monitor_routes_loaded = False
    print("⚠️ Could not load health_monitor_routes directly")
try:
    from app.routes.orchestrator_contract_routes import router as orchestrator_contract_router
    orchestrator_contract_routes_loaded = True
    print("✅ Directly loaded orchestrator_contract_routes")
except ImportError:
    orchestrator_contract_routes_loaded = False
    print("⚠️ Could not load orchestrator_contract_routes directly")
try:
    from app.routes.ash_routes import router as ash_router
    ash_routes_loaded = True
    print("✅ Directly loaded ash_routes")
except ImportError:
    ash_routes_loaded = False
    print("⚠️ Could not load ash_routes directly")
# Import loop validation routes
try:
    from app.routes.loop_validation_routes import router as loop_validation_router
    loop_validation_routes_loaded = True
    print("✅ Directly loaded loop_validation_routes")
except ImportError:
    loop_validation_routes_loaded = False
    print("⚠️ Could not load loop_validation_routes directly")
# Import memory API routes
try:
    from app.routes.memory_api_routes import router as memory_api_router
    memory_api_routes_loaded = True
    print("✅ Directly loaded memory_api_routes")
except ImportError:
    memory_api_routes_loaded = False
    print("⚠️ Could not load memory_api_routes directly")
# Initialize FastAPI app
app = FastAPI(
    title="Personal AI Agent",
    description="API for Personal AI Agent system",
    version="0.1.0",
)
# Initialize tracking variables
loaded_routes = []
failed_routes = []
fallbacks_triggered = []
# Add schema validation middleware if available
if schema_validation_loaded:
    try:
        add_schema_validation_middleware(app)
        print("✅ Added schema validation middleware to app")
    except Exception as e:
        print(f"⚠️ Failed to add schema validation middleware: {e}")
# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("✅ Mounted static files")
except Exception as e:
    print(f"⚠️ Failed to mount static files: {e}")
# Initialize system manifest
manifest_initialized = False
try:
    from app.core.system_manifest import register_loaded_routes
    manifest_initialized = True
    print("✅ Initialized system manifest")
except ImportError:
    print("⚠️ Failed to initialize system manifest")
# Register routes
# Agent Config routes
try:
    app.include_router(agent_config_router)
    loaded_routes.append("agent_config")
    print("✅ Agent Config routes loaded")
except Exception as e:
    print(f"⚠️ Failed to load Agent Config routes: {e}")
    failed_routes.append("agent_config")
# Agent Context routes
try:
    app.include_router(agent_context_router)
    loaded_routes.append("agent_context")
    print("✅ Agent Context routes loaded")
except Exception as e:
    print(f"⚠️ Failed to load Agent Context routes: {e}")
    failed_routes.append("agent_context")
# Memory Recall routes
try:
    app.include_router(memory_recall_router)
    loaded_routes.append("memory_recall")
    print("✅ Memory Recall routes loaded")
except Exception as e:
    print(f"⚠️ Failed to load Memory Recall routes: {e}")
    failed_routes.append("memory_recall")
# Memory Embed routes
try:
    app.include_router(memory_embed_router)
    loaded_routes.append("memory_embed")
    print("✅ Memory Embed routes loaded")
except Exception as e:
    print(f"⚠️ Failed to load Memory Embed routes: {e}")
    failed_routes.append("memory_embed")
# Plan Generate routes
try:
    app.include_router(plan_generate_router)
    loaded_routes.append("plan_generate")
    print("✅ Plan Generate routes loaded")
except Exception as e:
    print(f"⚠️ Failed to load Plan Generate routes: {e}")
    failed_routes.append("plan_generate")
# Train routes
try:
    app.include_router(train_router)
    loaded_routes.append("train")
    print("✅ Train routes loaded")
except Exception as e:
    print(f"⚠️ Failed to load Train routes: {e}")
    failed_routes.append("train")
# Export routes
try:
    app.include_router(export_router)
    loaded_routes.append("export")
    print("✅ Export routes loaded")
except Exception as e:
    print(f"⚠️ Failed to load Export routes: {e}")
    failed_routes.append("export")
# Fix routes
try:
    app.include_router(fix_router)
    loaded_routes.append("fix")
    print("✅ Fix routes loaded")
except Exception as e:
    print(f"⚠️ Failed to load Fix routes: {e}")
    failed_routes.append("fix")
# Delegate Stream routes
try:
    app.include_router(delegate_stream_router)
    loaded_routes.append("delegate_stream")
    print("✅ Delegate Stream routes loaded")
except Exception as e:
    print(f"⚠️ Failed to load Delegate Stream routes: {e}")
    failed_routes.append("delegate_stream")
# Upload File routes
if upload_file_routes_loaded:
    try:
        app.include_router(upload_file_router)
        loaded_routes.append("upload_file")
        print("✅ Upload File routes loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Upload File routes: {e}")
        failed_routes.append("upload_file")
# Snapshot routes
if snapshot_routes_loaded:
    try:
        app.include_router(snapshot_router)
        loaded_routes.append("snapshot")
        print("✅ Snapshot routes loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Snapshot routes: {e}")
        failed_routes.append("snapshot")
# Orchestrator Plan routes
if orchestrator_plan_routes_loaded:
    try:
        app.include_router(orchestrator_plan_router)
        loaded_routes.append("orchestrator_plan")
        print("✅ Orchestrator Plan routes loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Orchestrator Plan routes: {e}")
        failed_routes.append("orchestrator_plan")
# Health Monitor routes
if health_monitor_routes_loaded:
    try:
        app.include_router(health_monitor_router)
        loaded_routes.append("health_monitor")
        print("✅ Health Monitor routes loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Health Monitor routes: {e}")
        failed_routes.append("health_monitor")
# Orchestrator Contract routes
if orchestrator_contract_routes_loaded:
    try:
        app.include_router(orchestrator_contract_router)
        loaded_routes.append("orchestrator_contract")
        print("✅ Orchestrator Contract routes loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Orchestrator Contract routes: {e}")
        failed_routes.append("orchestrator_contract")
# ASH routes
if ash_routes_loaded:
    try:
        app.include_router(ash_router)
        loaded_routes.append("ash")
        print("✅ ASH routes loaded")
    except Exception as e:
        print(f"⚠️ Failed to load ASH routes: {e}")
        failed_routes.append("ash")
# Loop Validation routes
if loop_validation_routes_loaded:
    try:
        app.include_router(loop_validation_router)
        loaded_routes.append("loop_validation")
        print("✅ Loop Validation routes loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Loop Validation routes: {e}")
        failed_routes.append("loop_validation")
# Memory API routes
if memory_api_routes_loaded:
    try:
        app.include_router(memory_api_router)
        loaded_routes.append("memory_api")
        print("✅ Memory API routes loaded")
    except Exception as e:
        print(f"⚠️ Failed to load Memory API routes: {e}")
        failed_routes.append("memory_api")
# Load SAGE routes - Hard-wired registration (kept for backward compatibility)
try:
    from app.routes.sage_routes import router as sage_router
    # Only include if not already included above
    if "sage_routes" not in loaded_routes:
        app.include_router(sage_router)
        loaded_routes.append("sage")
        print("✅ SAGE routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load SAGE routes: {e}")
    if "sage" not in failed_routes:
        failed_routes.append("sage")
    # Try to load SAGE routes from router module as fallback
    try:
        from app.routes.sage_router import router as sage_router_fallback
        app.include_router(sage_router_fallback)
        loaded_routes.append("sage_fallback")
        fallbacks_triggered.append("sage_fallback")
        print("✅ SAGE routes loaded from router module (fallback)")
    except ImportError as e2:
        print(f"⚠️ Failed to load SAGE routes from router module: {e2}")
        if "sage_fallback" not in failed_routes:
            failed_routes.append("sage_fallback")
# Load Dashboard routes - Hard-wired registration (kept for backward compatibility)
try:
    from app.routes.dashboard_routes import router as dashboard_router
    # Only include if not already included above
    if "dashboard_routes" not in loaded_routes:
        app.include_router(dashboard_router)
        loaded_routes.append("dashboard")
        print("✅ Dashboard routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load Dashboard routes: {e}")
    if "dashboard" not in failed_routes:
        failed_routes.append("dashboard")
# FORGE routes - Hard-wired registration (kept for backward compatibility)
try:
    from app.routes.forge_routes import router as forge_router
    # Only include if not already included above
    if "forge_routes" not in loaded_routes:
        app.include_router(forge_router)
        loaded_routes.append("forge")
        print("✅ FORGE routes loaded (legacy)")
except ImportError as e:
    print(f"⚠️ Failed to load FORGE routes: {e}")
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
