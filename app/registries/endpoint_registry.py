"""
Endpoint Registry
This module defines the registry of all endpoints in the Promethios system.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class EndpointEntry(BaseModel):
    """Endpoint entry in the registry."""
    path: str = Field(..., description="Path of the endpoint")
    method: str = Field(..., description="HTTP method of the endpoint")
    input_schema: Optional[str] = Field(None, description="Input schema of the endpoint")
    output_schema: Optional[str] = Field(None, description="Output schema of the endpoint")
    module: str = Field(..., description="Module hosting the endpoint")
    status: str = Field(..., description="Status of the endpoint (active or planned)")

# Initialize the endpoint registry
ENDPOINT_REGISTRY = [

    {
        "path": "/api/reflection/chain",
        "method": "POST",
        "input_schema": "ReflectionChainRequest",
        "output_schema": "ReflectionChainResponse",
        "module": "app/routes/reflection_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_sprint1_cognitive_reflection_chain_activation"
    },
    {
        "path": "/api/plan/execute",
        "method": "POST",
        "input_schema": "PlanExecutionRequest",
        "output_schema": "PlanExecutionResponse",
        "module": "app/routes/plan_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_sprint1_cognitive_reflection_chain_activation"
    },
    {
        "path": "/api/drift/auto-heal",
        "method": "POST",
        "input_schema": "DriftHealingRequest",
        "output_schema": "DriftHealingResult",
        "module": "app/routes/drift_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_sprint1_cognitive_reflection_chain_activation"
    },
    {
        "path": "/api/plan/chain",
        "method": "POST",
        "input_schema": "PlanChainRequest",
        "output_schema": "PlanChainResponse",
        "module": "app/routes/plan_routes.py",
        "status": "active",
        "memory_tag": "phase3.0_sprint4_cognitive_reflection_plan_chaining"
    },
    {
        "path": "/api/reflection/trigger-scan-deep",
        "method": "POST",
        "input_schema": "ReflectionScanRequest",
        "output_schema": "ReflectionScanResponse",
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/api/reflection/analyze/{reflection_id}",
        "method": "GET",
        "output_schema": "ReflectionAnalysisResult",
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/api/agent/ping",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/agent_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/agent/run",
        "method": "POST",
        "input_schema": "dict",
        "output_schema": "Dict",
        "module": "app/routes/agent_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/agent/loop",
        "method": "POST",
        "input_schema": "dict",
        "output_schema": "Dict",
        "module": "app/routes/agent_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/agent/list",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/agent_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/agent/delegate",
        "method": "POST",
        "input_schema": "dict",
        "output_schema": "Dict",
        "module": "app/routes/agent_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/agent/analyze-prompt",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "app/routes/agent_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/agent/ceo-review",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "app/routes/agent_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/agent/cto-review",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "app/routes/agent_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/agent/generate-code",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "app/routes/agent_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/memory/ping",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/memory_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/memory/write",
        "method": "POST",
        "input_schema": "dict",
        "output_schema": "Dict",
        "module": "app/routes/memory_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/memory/read",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/memory_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/memory/thread",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/memory_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/start",
        "method": "POST",
        "input_schema": "StartLoopRequest",
        "output_schema": "Dict",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/debug",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/complete",
        "method": "POST",
        "input_schema": "LoopCompletionRequest",
        "output_schema": "LoopCompletionResponse",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/persona-reflect",
        "method": "POST",
        "input_schema": "PersonaReflectRequest",
        "output_schema": "PersonaReflectResponse",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/plan",
        "method": "POST",
        "input_schema": "LoopPlanRequest",
        "output_schema": "LoopPlanResponse",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/reset",
        "method": "POST",
        "output_schema": "LoopResetResponse",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/respond",
        "method": "POST",
        "input_schema": "LoopResponseRequest",
        "output_schema": "LoopResponseResult",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/trace",
        "method": "GET",
        "output_schema": "LoopTraceResponse",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/trace",
        "method": "POST",
        "input_schema": "LoopTraceRequest",
        "output_schema": "LoopResetResponse",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/loop/validate",
        "method": "POST",
        "input_schema": "LoopValidateRequest",
        "output_schema": "LoopValidateResponse",
        "module": "app/routes/loop_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/reflection/trigger-scan",
        "method": "POST",
        "input_schema": "ReflectionScanRequest",
        "output_schema": "ReflectionResponse",
        "module": "app/routes/reflection_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/reflection/result/{reflection_id}",
        "method": "GET",
        "output_schema": "ReflectionResultResponse",
        "module": "app/routes/reflection_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/reflection/trigger",
        "method": "POST",
        "input_schema": "ReflectionTriggerRequest",
        "output_schema": "ReflectionResponse",
        "module": "app/routes/reflection_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/reflection/{reflection_id}",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/reflection_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/reflection/{project_id}",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/reflection_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/reflection/{project_id}",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "app/routes/reflection_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/reflection/{project_id}/history",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/reflection_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/reflection/{project_id}",
        "method": "DELETE",
        "output_schema": "Dict",
        "module": "app/routes/reflection_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/drift/report",
        "method": "POST",
        "input_schema": "DriftMonitorRequest",
        "output_schema": "DriftMonitorResponse",
        "module": "app/routes/drift_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/drift/monitor",
        "method": "POST",
        "input_schema": "DriftMonitorRequest",
        "output_schema": "DriftMonitorResponse",
        "module": "app/routes/drift_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/drift/log",
        "method": "GET",
        "output_schema": "DriftLogResponse",
        "module": "app/routes/drift_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/drift/history/{loop_id}",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/drift_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/plan/create",
        "method": "POST",
        "input_schema": "PlanCreateRequest",
        "output_schema": "Dict",
        "module": "app/routes/plan_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/plan/{plan_id}",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/plan_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/plan/update",
        "method": "PUT",
        "input_schema": "PlanUpdateRequest",
        "output_schema": "Dict",
        "module": "app/routes/plan_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/plan/status/{execution_id}",
        "method": "GET",
        "output_schema": "PlanExecutionStatusResponse",
        "module": "app/routes/plan_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/snapshot/save",
        "method": "POST",
        "input_schema": "SnapshotSaveRequest",
        "output_schema": "SnapshotResponse",
        "module": "app/routes/snapshot_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/snapshot/restore",
        "method": "POST",
        "input_schema": "SnapshotRestoreRequest",
        "output_schema": "SnapshotResponse",
        "module": "app/routes/snapshot_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/snapshot/list/{loop_id}",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/routes/snapshot_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/snapshot/{loop_id}",
        "method": "DELETE",
        "output_schema": "Dict",
        "module": "app/routes/snapshot_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/ash/analyze",
        "method": "POST",
        "input_schema": "AshAnalysisRequest",
        "output_schema": "AshAnalysisResult",
        "module": "app/routes/ash_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/ash/execute",
        "method": "POST",
        "input_schema": "ExecuteRequest",
        "output_schema": "ExecuteResponse",
        "module": "app/routes/ash_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/debug/analyze-loop",
        "method": "POST",
        "input_schema": "LoopDebugRequest",
        "output_schema": "LoopDebugResult",
        "module": "app/routes/debug_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/debugger/trace",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "DebuggerTraceResult",
        "module": "app/routes/debugger_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/historian/log",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "HistorianDriftResult",
        "module": "app/routes/historian_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_patch_complete"
    },
    {
        "path": "/api/train/placeholder",
        "method": "GET",
        "module": "app/routes/train_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/api/execute/placeholder",
        "method": "GET",
        "module": "app/routes/execute_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/api/project/placeholder",
        "method": "GET",
        "module": "routes/project_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/upload/placeholder",
        "method": "GET",
        "module": "app/routes/upload_file_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/memory_api/placeholder",
        "method": "GET",
        "module": "app/routes/memory_api_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/loop_validation/placeholder",
        "method": "GET",
        "module": "app/routes/loop_validation_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/plan_generate/placeholder",
        "method": "GET",
        "module": "app/routes/plan_generate_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/forge_build/placeholder",
        "method": "GET",
        "module": "app/routes/forge_build_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/critic_review/placeholder",
        "method": "GET",
        "module": "app/routes/critic_review_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/pessimist_evaluation/placeholder",
        "method": "GET",
        "module": "app/routes/pessimist_evaluation_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/sage_beliefs/placeholder",
        "method": "GET",
        "module": "app/routes/sage_beliefs_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/health_monitor/placeholder",
        "method": "GET",
        "module": "app/routes/health_monitor_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/orchestrator_contract/placeholder",
        "method": "GET",
        "module": "app/routes/orchestrator_contract_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/forge/placeholder",
        "method": "GET",
        "module": "app/routes/forge_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/debug_analyzer/placeholder",
        "method": "GET",
        "module": "app/routes/debug_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/output_policy/placeholder",
        "method": "GET",
        "module": "app/routes/output_policy_routes.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
    {
        "path": "/diagnostics/routes",
        "method": "GET",
        "output_schema": "Dict",
        "module": "app/main.py",
        "status": "active",
        "memory_tag": "phase4.0_holistic_router_registry_sync"
    },
]