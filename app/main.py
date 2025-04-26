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
# Removed import to fix deployment issue
# from app.routes import upload_base64_routes

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
from app.routes.plan_generate_routes import router as plan_generate_router
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

# Import previously orphaned routes
try:
    from app.routes.dashboard_routes import router as dashboard_routes_router
    dashboard_routes_loaded = True
    print("✅ Directly loaded dashboard_routes_router")
except ImportError:
    dashboard_routes_loaded = False
    print("⚠️ Could not load dashboard_routes_router directly")

try:
    from app.routes.drift_routes import router as drift_routes_router
    drift_routes_loaded = True
    print("✅ Directly loaded drift_routes_router")
except ImportError:
    drift_routes_loaded = False
    print("⚠️ Could not load drift_routes_router directly")

try:
    from app.routes.forge_routes import router as forge_routes_router
    forge_routes_loaded = True
    print("✅ Directly loaded forge_routes_router")
except ImportError:
    forge_routes_loaded = False
    print("⚠️ Could not load forge_routes_router directly")

try:
    from app.routes.loop_validation_routes import router as loop_validation_routes_router
    loop_validation_routes_loaded = True
    print("✅ Directly loaded loop_validation_routes_router")
except ImportError:
    loop_validation_routes_loaded = False
    print("⚠️ Could not load loop_validation_routes_router directly")

try:
    from app.routes.output_policy_routes import router as output_policy_routes_router
    output_policy_routes_loaded = True
    print("✅ Directly loaded output_policy_routes_router")
except ImportError:
    output_policy_routes_loaded = False
    print("⚠️ Could not load output_policy_routes_router directly")

try:
    from app.routes.pessimist_evaluation_routes import router as pessimist_evaluation_routes_router
    pessimist_evaluation_routes_loaded = True
    print("✅ Directly loaded pessimist_evaluation_routes_router")
except ImportError:
    pessimist_evaluation_routes_loaded = False
    print("⚠️ Could not load pessimist_evaluation_routes_router directly")

# Try to import other routes
try:
    from app.routes.hal_routes import router as hal_routes
    hal_routes_loaded = True
    print("✅ Directly loaded hal_routes")
except Exception as e:
    hal_routes_loaded = False
    print(f"⚠️ Could not load hal_routes directly: {e}")
    # Create logs directory if it doesn't exist
    import os
    import json
    import datetime
    os.makedirs("logs", exist_ok=True)
    
    # Log the failure
    try:
        log_file = "logs/hal_route_failures.json"
        log_entry = {
            "timestamp": str(datetime.datetime.now()),
            "event": "import_failure",
            "error": str(e)
        }
        
        # Check if log file exists
        if os.path.exists(log_file):
            # Read existing logs
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = [logs]
            except json.JSONDecodeError:
                logs = []
        else:
            logs = []
        
        # Append new log entry
        logs.append(log_entry)
        
        # Write updated logs
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as log_error:
        print(f"⚠️ Failed to log HAL routes failure: {log_error}")

try:
    from app.routes.memory_router import router as memory_router
    memory_routes_loaded = True
    print("✅ Directly loaded memory_router")
except ImportError:
    memory_routes_loaded = False
    print("⚠️ Could not load memory_router directly")

# Load Memory API Routes
try:
    from app.routes.memory_api_routes import router as memory_api_router
    memory_api_routes_loaded = True
    print("✅ Directly loaded memory_api_router")
except ImportError:
    memory_api_routes_loaded = False
    print("⚠️ Could not load memory_api_router directly")

try:
    from app.routes.loop_router import router as loop_router
    loop_routes_loaded = True
    print("✅ Directly loaded loop_router")
except ImportError:
    loop_routes_loaded = False
    print("⚠️ Could not load loop_router directly")

try:
    from app.routes.orchestrator_routes import router as orchestrator_routes
    routes_orchestrator_loaded = True
    print("✅ Directly loaded routes/orchestrator_routes")
except ImportError:
    routes_orchestrator_loaded = False
    print("⚠️ Could not load routes/orchestrator_routes directly")

try:
    from app.routes.core_router import router as core_router
    core_routes_loaded = True
    print("✅ Directly loaded core_router")
except ImportError:
    core_routes_loaded = False
    print("⚠️ Could not load core_router directly")

try:
    from app.routes.agent_router import router as agent_router
    agent_routes_loaded = True
    print("✅ Directly loaded agent_router")
except ImportError:
    agent_routes_loaded = False
    print("⚠️ Could not load agent_router directly")

try:
    from app.routes.persona_router import router as persona_router
    persona_routes_loaded = True
    print("✅ Directly loaded persona_router")
except ImportError:
    persona_routes_loaded = False
    print("⚠️ Could not load persona_router directly")

try:
    from app.routes.debug_router import router as debug_router
    debug_routes_loaded = True
    print("✅ Directly loaded debug_router")
except ImportError:
    debug_routes_loaded = False
    print("⚠️ Could not load debug_router directly")

try:
    from app.routes.historian_router import router as historian_router
    historian_routes_loaded = True
    print("✅ Directly loaded historian_router")
except ImportError:
    historian_routes_loaded = False
    print("⚠️ Could not load historian_router directly")

try:
    from app.routes.debugger_router import router as debugger_router
    debugger_routes_loaded = True
    print("✅ Directly loaded debugger_router")
except ImportError:
    debugger_routes_loaded = False
    print("⚠️ Could not load debugger_router directly")

try:
    from app.routes.orchestrator_router import router as orchestrator_router
    orchestrator_routes_loaded = True
    print("✅ Directly loaded orchestrator_router")
except ImportError:
    orchestrator_routes_loaded = False
    print("⚠️ Could not load orchestrator_router directly")

try:
    from app.routes.critic_router import router as critic_router
    critic_routes_loaded = True
    print("✅ Directly loaded critic_router")
except ImportError:
    critic_routes_loaded = False
    print("⚠️ Could not load critic_router directly")

# Load CRITIC Review Routes
try:
    from app.routes.critic_review_routes import router as critic_review_router
    critic_review_routes_loaded = True
    print("✅ Directly loaded critic_review_router")
except ImportError:
    critic_review_routes_loaded = False
    print("⚠️ Could not load critic_review_router directly")

# Load PESSIMIST Evaluation Routes
try:
    from app.routes.pessimist_evaluation_routes import router as pessimist_evaluation_router
    pessimist_evaluation_routes_loaded = True
    print("✅ Directly loaded pessimist_evaluation_router")
except ImportError:
    pessimist_evaluation_routes_loaded = False
    print("⚠️ Could not load pessimist_evaluation_router directly")

# Load SAGE Beliefs Routes
try:
    from app.routes.sage_beliefs_routes import router as sage_beliefs_router
    sage_beliefs_routes_loaded = True
    print("✅ Directly loaded sage_beliefs_router")
except ImportError:
    sage_beliefs_routes_loaded = False
    print("⚠️ Could not load sage_beliefs_router directly")

try:
    from app.routes.sage_router import router as sage_router
    sage_routes_loaded = True
    print("✅ Directly loaded sage_router")
except ImportError:
    sage_routes_loaded = False
    print("⚠️ Could not load sage_router directly")

try:
    from app.routes.guardian_router import router as guardian_router
    guardian_routes_loaded = True
    print("✅ Directly loaded guardian_router")
except ImportError:
    guardian_routes_loaded = False
    print("⚠️ Could not load guardian_router directly")

try:
    from app.routes.pessimist_router import router as pessimist_router
    pessimist_routes_loaded = True
    print("✅ Directly loaded pessimist_router")
except ImportError:
    pessimist_routes_loaded = False
    print("⚠️ Could not load pessimist_router directly")

try:
    from app.routes.nova_router import router as nova_router
    nova_routes_loaded = True
    print("✅ Directly loaded nova_router")
except ImportError:
    nova_routes_loaded = False
    print("⚠️ Could not load nova_router directly")

try:
    from app.routes.cto_router import router as cto_router
    cto_routes_loaded = True
    print("✅ Directly loaded cto_router")
except ImportError:
    cto_routes_loaded = False
    print("⚠️ Could not load cto_router directly")

try:
    from app.routes.observer_router import router as observer_router
    observer_routes_loaded = True
    print("✅ Directly loaded observer_router")
except ImportError:
    observer_routes_loaded = False
    print("⚠️ Could not load observer_router directly")

try:
    from app.routes.sitegen_router import router as sitegen_router
    sitegen_routes_loaded = True
    print("✅ Directly loaded sitegen_router")
except ImportError:
    sitegen_routes_loaded = False
    print("⚠️ Could not load sitegen_router directly")

try:
    from app.routes.reflection_router import router as reflection_router
    reflection_routes_loaded = True
    print("✅ Directly loaded reflection_router")
except ImportError:
    reflection_routes_loaded = False
    print("⚠️ Could not load reflection_router directly")

try:
    from app.routes.trust_router import router as trust_router
    trust_routes_loaded = True
    print("✅ Directly loaded trust_router")
except ImportError:
    trust_routes_loaded = False
    print("⚠️ Could not load trust_router directly")

try:
    from app.routes.self_router import router as self_router
    self_routes_loaded = True
    print("✅ Directly loaded self_router")
except ImportError:
    self_routes_loaded = False
    print("⚠️ Could not load self_router directly")

# Create FastAPI app
app = FastAPI(
    title="Promethios API",
    description="API for the Promethios Cognitive System",
    version="1.0.0",
)

# Add schema validation middleware if loaded
if schema_validation_loaded:
    try:
        add_schema_validation_middleware(app)
        print("✅ Schema validation middleware added to application")
    except Exception as e:
        print(f"⚠️ Failed to add schema validation middleware: {e}")

# Initialize system manifest
try:
    from app.utils.manifest_manager import initialize_manifest, register_system_boot, register_loaded_routes
    
    # Initialize manifest at boot
    initialize_manifest()
    
    # Register system boot in manifest
    register_system_boot()
    
    print("✅ System manifest initialized")
    manifest_initialized = True
except ImportError as e:
    print(f"⚠️ Failed to initialize system manifest: {e}")
    manifest_initialized = False

# Setup dashboard static files
try:
    from app.utils.dashboard_setup import setup_dashboard_static_files
    setup_result = setup_dashboard_static_files()
    print(f"✅ Dashboard static files setup: {setup_result['message']}")
except ImportError as e:
    print(f"⚠️ Failed to setup dashboard static files: {e}")

# Mount static files directory
try:
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    print("✅ Static files directory mounted")
except Exception as e:
    print(f"⚠️ Failed to mount static files directory: {e}")

# Initialize loaded_routes list to track all registered routes
loaded_routes = []
failed_routes = []
fallbacks_triggered = {
    "memory": False,
    "hal": False
}

# Include floating module routers
app.include_router(agent_config_router)
loaded_routes.append("agent_config_routes")
print("✅ Included agent_config_router")

app.include_router(agent_context_router)
loaded_routes.append("agent_context_routes")
print("✅ Included agent_context_router")

app.include_router(memory_recall_router)
loaded_routes.append("memory_recall_routes")
print("✅ Included memory_recall_router")

app.include_router(memory_embed_router)
loaded_routes.append("memory_embed_routes")
print("✅ Included memory_embed_router")

app.include_router(plan_generate_router)
loaded_routes.append("plan_generate_routes")
print("✅ Included plan_generate_router")

app.include_router(train_router)
loaded_routes.append("train_routes")
print("✅ Included train_router")

app.include_router(export_router)
loaded_routes.append("export_routes")
print("✅ Included export_router")

app.include_router(fix_router)
loaded_routes.append("fix_routes")
print("✅ Included fix_router")

app.include_router(delegate_stream_router)
loaded_routes.append("delegate_stream_routes")
print("✅ Included delegate_stream_router")

# Include HAL routes with priority (first)
if hal_routes_loaded:
    app.include_router(hal_routes, prefix="/api")
    loaded_routes.append("hal_routes")
    print("✅ Included hal_routes")
else:
    # Create fallback router for HAL routes
    try:
        from fastapi import APIRouter
        fallback_router = APIRouter(prefix="/api/hal", tags=["hal"])
        
        @fallback_router.get("/status")
        async def hal_status_fallback():
            return {"status": "HAL routes not loaded, using fallback", "timestamp": str(datetime.datetime.now())}
        
        app.include_router(fallback_router)
        loaded_routes.append("hal_fallback")
        fallbacks_triggered["hal"] = True
        print("✅ Included HAL fallback router")
    except Exception as e:
        print(f"⚠️ Failed to create HAL fallback router: {e}")
        if "hal_fallback" not in failed_routes:
            failed_routes.append("hal_fallback")

# Include memory routes with priority (second)
if routes_memory_loaded:
    app.include_router(memory_router, prefix="/api")
    loaded_routes.append("memory_routes")
    print("✅ Included memory_routes")
else:
    # Create fallback router for memory routes
    try:
        from fastapi import APIRouter
        memory_fallback_router = APIRouter(prefix="/api/memory", tags=["memory"])
        
        @memory_fallback_router.get("/status")
        async def memory_status_fallback():
            return {"status": "Memory routes not loaded, using fallback", "timestamp": str(datetime.datetime.now())}
        
        app.include_router(memory_fallback_router)
        loaded_routes.append("memory_fallback")
        fallbacks_triggered["memory"] = True
        print("✅ Included memory fallback router")
    except Exception as e:
        print(f"⚠️ Failed to create memory fallback router: {e}")
        if "memory_fallback" not in failed_routes:
            failed_routes.append("memory_fallback")

# Include memory router if loaded
if memory_routes_loaded:
    app.include_router(memory_router)  # No prefix as routes already include /api/
    loaded_routes.append("memory_router")
    print("✅ Included memory_router")
else:
    if "memory_router" not in failed_routes:
        failed_routes.append("memory_router")

# Include memory API router if loaded
if memory_api_routes_loaded:
    app.include_router(memory_api_router)  # No prefix as routes already include /api/
    loaded_routes.append("memory_api_router")
    print("✅ Included memory_api_router")
else:
    if "memory_api_router" not in failed_routes:
        failed_routes.append("memory_api_router")

# Include pessimist evaluation router if loaded
if pessimist_evaluation_routes_loaded:
    app.include_router(pessimist_evaluation_router)  # No prefix as routes already include /api/
    loaded_routes.append("pessimist_evaluation_router")
    print("✅ Included pessimist_evaluation_router")
else:
    if "pessimist_evaluation_router" not in failed_routes:
        failed_routes.append("pessimist_evaluation_router")

# Include sage beliefs router if loaded
if sage_beliefs_routes_loaded:
    app.include_router(sage_beliefs_router)  # No prefix as routes already include /api/
    loaded_routes.append("sage_beliefs_router")
    print("✅ Included sage_beliefs_router")
else:
    if "sage_beliefs_router" not in failed_routes:
        failed_routes.append("sage_beliefs_router")

# Include loop router if loaded
if loop_routes_loaded:
    app.include_router(loop_router)  # No prefix as routes already include /api/
    loaded_routes.append("loop_router")
    print("✅ Included loop_router")
else:
    if "loop_router" not in failed_routes:
        failed_routes.append("loop_router")

# Include orchestrator routes if loaded
if routes_orchestrator_loaded:
    app.include_router(orchestrator_routes, prefix="/api")
    loaded_routes.append("orchestrator_routes")
    print("✅ Included orchestrator_routes")
else:
    if "orchestrator_routes" not in failed_routes:
        failed_routes.append("orchestrator_routes")

# Include core router if loaded
if core_routes_loaded:
    app.include_router(core_router)
    loaded_routes.append("core_router")
    print("✅ Included core_router")
else:
    if "core_router" not in failed_routes:
        failed_routes.append("core_router")

# Include agent router if loaded
if agent_routes_loaded:
    app.include_router(agent_router)
    loaded_routes.append("agent_router")
    print("✅ Included agent_router")
else:
    if "agent_router" not in failed_routes:
        failed_routes.append("agent_router")

# Include persona router if loaded
if persona_routes_loaded:
    app.include_router(persona_router)
    loaded_routes.append("persona_router")
    print("✅ Included persona_router")
else:
    if "persona_router" not in failed_routes:
        failed_routes.append("persona_router")

# Include debug router if loaded
if debug_routes_loaded:
    app.include_router(debug_router)
    loaded_routes.append("debug_router")
    print("✅ Included debug_router")
else:
    if "debug_router" not in failed_routes:
        failed_routes.append("debug_router")

# Include historian router if loaded
if historian_routes_loaded:
    app.include_router(historian_router)
    loaded_routes.append("historian_router")
    print("✅ Included historian_router")
else:
    if "historian_router" not in failed_routes:
        failed_routes.append("historian_router")

# Include debugger router if loaded
if debugger_routes_loaded:
    app.include_router(debugger_router)
    loaded_routes.append("debugger_router")
    print("✅ Included debugger_router")
else:
    if "debugger_router" not in failed_routes:
        failed_routes.append("debugger_router")

# Include orchestrator router if loaded
if orchestrator_routes_loaded:
    app.include_router(orchestrator_router)
    loaded_routes.append("orchestrator_router")
    print("✅ Included orchestrator_router")
else:
    if "orchestrator_router" not in failed_routes:
        failed_routes.append("orchestrator_router")

# Include critic router if loaded
if critic_routes_loaded:
    app.include_router(critic_router)
    loaded_routes.append("critic_router")
    print("✅ Included critic_router")
else:
    if "critic_router" not in failed_routes:
        failed_routes.append("critic_router")

# Include critic review router if loaded
if critic_review_routes_loaded:
    app.include_router(critic_review_router)
    loaded_routes.append("critic_review_router")
    print("✅ Included critic_review_router")
else:
    if "critic_review_router" not in failed_routes:
        failed_routes.append("critic_review_router")

# Include sage router if loaded
if sage_routes_loaded:
    app.include_router(sage_router)
    loaded_routes.append("sage_router")
    print("✅ Included sage_router")
else:
    if "sage_router" not in failed_routes:
        failed_routes.append("sage_router")

# Include guardian router if loaded
if guardian_routes_loaded:
    app.include_router(guardian_router)
    loaded_routes.append("guardian_router")
    print("✅ Included guardian_router")
else:
    if "guardian_router" not in failed_routes:
        failed_routes.append("guardian_router")

# Include pessimist router if loaded
if pessimist_routes_loaded:
    app.include_router(pessimist_router)
    loaded_routes.append("pessimist_router")
    print("✅ Included pessimist_router")
else:
    if "pessimist_router" not in failed_routes:
        failed_routes.append("pessimist_router")

# Include nova router if loaded
if nova_routes_loaded:
    app.include_router(nova_router)
    loaded_routes.append("nova_router")
    print("✅ Included nova_router")
else:
    if "nova_router" not in failed_routes:
        failed_routes.append("nova_router")

# Include cto router if loaded
if cto_routes_loaded:
    app.include_router(cto_router)
    loaded_routes.append("cto_router")
    print("✅ Included cto_router")
else:
    if "cto_router" not in failed_routes:
        failed_routes.append("cto_router")

# Include observer router if loaded
if observer_routes_loaded:
    app.include_router(observer_router)
    loaded_routes.append("observer_router")
    print("✅ Included observer_router")
else:
    if "observer_router" not in failed_routes:
        failed_routes.append("observer_router")

# Include sitegen router if loaded
if sitegen_routes_loaded:
    app.include_router(sitegen_router)
    loaded_routes.append("sitegen_router")
    print("✅ Included sitegen_router")
else:
    if "sitegen_router" not in failed_routes:
        failed_routes.append("sitegen_router")

# Include reflection router if loaded
if reflection_routes_loaded:
    app.include_router(reflection_router)
    loaded_routes.append("reflection_router")
    print("✅ Included reflection_router")
else:
    if "reflection_router" not in failed_routes:
        failed_routes.append("reflection_router")

# Include trust router if loaded
if trust_routes_loaded:
    app.include_router(trust_router)
    loaded_routes.append("trust_router")
    print("✅ Included trust_router")
else:
    if "trust_router" not in failed_routes:
        failed_routes.append("trust_router")

# Include snapshot router if loaded
if snapshot_routes_loaded:
    app.include_router(snapshot_router)
    loaded_routes.append("snapshot_router")
    print("✅ Included snapshot_router")
else:
    if "snapshot_router" not in failed_routes:
        failed_routes.append("snapshot_router")

# Include orchestrator plan router if loaded
if orchestrator_plan_routes_loaded:
    app.include_router(orchestrator_plan_router)
    loaded_routes.append("orchestrator_plan_router")
    print("✅ Included orchestrator_plan_router")
else:
    if "orchestrator_plan_router" not in failed_routes:
        failed_routes.append("orchestrator_plan_router")

# Include health monitor router if loaded
if health_monitor_routes_loaded:
    app.include_router(health_monitor_router)
    loaded_routes.append("health_monitor_router")
    print("✅ Included health_monitor_router")
else:
    if "health_monitor_router" not in failed_routes:
        failed_routes.append("health_monitor_router")

# Include upload file router if loaded
if upload_file_routes_loaded:
    app.include_router(upload_file_router)
    loaded_routes.append("upload_file_router")
    print("✅ Included upload_file_router")
else:
    if "upload_file_router" not in failed_routes:
        failed_routes.append("upload_file_router")

# Include self router if loaded
if self_routes_loaded:
    app.include_router(self_router)
    loaded_routes.append("self_router")
    print("✅ Included self_router")
else:
    if "self_router" not in failed_routes:
        failed_routes.append("self_router")

# Include orchestrator contract router if loaded
if orchestrator_contract_routes_loaded:
    app.include_router(orchestrator_contract_router)
    loaded_routes.append("orchestrator_contract_router")
    print("✅ Included orchestrator_contract_router")
else:
    if "orchestrator_contract_router" not in failed_routes:
        failed_routes.append("orchestrator_contract_router")

# Include ash router if loaded
if ash_routes_loaded:
    app.include_router(ash_router)
    loaded_routes.append("ash_router")
    print("✅ Included ash_router")
else:
    if "ash_router" not in failed_routes:
        failed_routes.append("ash_router")

# Include dashboard routes router if loaded
if dashboard_routes_loaded:
    app.include_router(dashboard_routes_router)
    loaded_routes.append("dashboard_routes_router")
    print("✅ Included dashboard_routes_router")
else:
    if "dashboard_routes_router" not in failed_routes:
        failed_routes.append("dashboard_routes_router")

# Include drift routes router if loaded
if drift_routes_loaded:
    app.include_router(drift_routes_router)
    loaded_routes.append("drift_routes_router")
    print("✅ Included drift_routes_router")
else:
    if "drift_routes_router" not in failed_routes:
        failed_routes.append("drift_routes_router")

# Include forge routes router if loaded
if forge_routes_loaded:
    app.include_router(forge_routes_router)
    loaded_routes.append("forge_routes_router")
    print("✅ Included forge_routes_router")
else:
    if "forge_routes_router" not in failed_routes:
        failed_routes.append("forge_routes_router")

# Include loop validation routes router if loaded
if loop_validation_routes_loaded:
    app.include_router(loop_validation_routes_router)
    loaded_routes.append("loop_validation_routes_router")
    print("✅ Included loop_validation_routes_router")
else:
    if "loop_validation_routes_router" not in failed_routes:
        failed_routes.append("loop_validation_routes_router")

# Include output policy routes router if loaded
if output_policy_routes_loaded:
    app.include_router(output_policy_routes_router)
    loaded_routes.append("output_policy_routes_router")
    print("✅ Included output_policy_routes_router")
else:
    if "output_policy_routes_router" not in failed_routes:
        failed_routes.append("output_policy_routes_router")

# Include pessimist evaluation routes router if loaded
if pessimist_evaluation_routes_loaded:
    app.include_router(pessimist_evaluation_routes_router)
    loaded_routes.append("pessimist_evaluation_routes_router")
    print("✅ Included pessimist_evaluation_routes_router")
else:
    if "pessimist_evaluation_routes_router" not in failed_routes:
        failed_routes.append("pessimist_evaluation_routes_router")

# Hard-wired registrations (kept for backward compatibility)
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
# Removed upload_base64_routes.router to fix deployment issue
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
