"""
Main Router Map

This module provides a mapping of all routers registered in the Promethios API.
It can be used for reference or debugging purposes.
"""

# Core Infrastructure Router
core_router_endpoints = [
    {"path": "/health", "methods": ["GET"], "description": "Health check endpoint"},
    {"path": "/system/status", "methods": ["GET"], "description": "System status including environment and module load state"},
    {"path": "/memory/read", "methods": ["POST"], "description": "Retrieve memory by key"},
    {"path": "/memory/write", "methods": ["POST"], "description": "Direct memory injection"},
    {"path": "/memory/delete", "methods": ["POST"], "description": "Clear keys from memory"}
]

# Loop Execution Router
loop_router_endpoints = [
    {"path": "/loop/trace", "methods": ["GET"], "description": "Get loop memory trace log"},
    {"path": "/loop/trace", "methods": ["POST"], "description": "Inject synthetic loop trace"},
    {"path": "/loop/reset", "methods": ["POST"], "description": "Memory reset for clean test runs"},
    {"path": "/loop/persona-reflect", "methods": ["POST"], "description": "Inject mode-aligned reflection trace"}
]

# Agent Router
agent_router_endpoints = [
    {"path": "/analyze-prompt", "methods": ["POST"], "description": "Thought Partner prompt analysis"},
    {"path": "/generate-variants", "methods": ["POST"], "description": "Thought Variant Generator"},
    {"path": "/plan-and-execute", "methods": ["POST"], "description": "HAL, ASH, NOVA execution"},
    {"path": "/run-critic", "methods": ["POST"], "description": "Loop summary review"},
    {"path": "/pessimist-check", "methods": ["POST"], "description": "Tone realism scoring"},
    {"path": "/ceo-review", "methods": ["POST"], "description": "Alignment + Operator satisfaction"},
    {"path": "/cto-review", "methods": ["POST"], "description": "Trust decay + loop health"},
    {"path": "/historian-check", "methods": ["POST"], "description": "Forgotten belief analysis"},
    {"path": "/drift-summary", "methods": ["POST"], "description": "Aggregated loop-level drift"},
    {"path": "/generate-weekly-drift-report", "methods": ["POST"], "description": "Weekly system meta-summary"}
]

# Persona Router
persona_router_endpoints = [
    {"path": "/persona/switch", "methods": ["POST"], "description": "Change active mode"},
    {"path": "/persona/current", "methods": ["GET"], "description": "Return current orchestrator_persona"},
    {"path": "/mode/trace", "methods": ["GET"], "description": "Trace of persona usage over loops"}
]

# Complete router map
router_map = {
    "core_router": core_router_endpoints,
    "loop_router": loop_router_endpoints,
    "agent_router": agent_router_endpoints,
    "persona_router": persona_router_endpoints
}

# Main application router registration
router_registration = """
# Import routers
from app.routes.core_routes import router as core_router
from app.routes.loop_routes import router as loop_router
from app.routes.agent_routes import router as agent_router
from app.routes.persona_routes import router as persona_router

# Include routers with correct prefixes (no /api/ prefix)
app.include_router(core_router)
app.include_router(loop_router)
app.include_router(agent_router)
app.include_router(persona_router)
"""

if __name__ == "__main__":
    # Print router map for debugging
    import json
    print(json.dumps(router_map, indent=2))
