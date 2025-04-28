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
    # --- Phase 4 Sprint 1 Endpoints ---
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
    # --- Existing Endpoints ---
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
        "input_schema": None,
        "output_schema": "ReflectionAnalysisResult",
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/modules/agent_context.py",
        "status": "active"
    },
    {
        "path": "/",
        "method": "POST",
        "input_schema": "BuilderRequest",
        "output_schema": "BuilderResponse",
        "module": "api/agent/builder.py",
        "status": "active"
    },
    {
        "path": "/",
        "method": "GET",
        "input_schema": "Optional",
        "output_schema": None,
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/add",
        "method": "POST",
        "input_schema": "MemoryAddRequest",
        "output_schema": None,
        "module": "api/memory.py",
        "status": "active"
    },
    {
        "path": "/agent",
        "method": "POST",
        "input_schema": "MemoryAgentRequest",
        "output_schema": "MemoryAgentResponse",
        "module": "api/agent/memory.py",
        "status": "active"
    },
    {
        "path": "/agent/delegate",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/delegate_route.py",
        "status": "active"
    },
    {
        "path": "/agent/goal/{task_id}/edit-prompt",
        "method": "POST",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/agent/list",
        "method": "GET",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/delegate_route.py",
        "status": "active"
    },
    {
        "path": "/agent/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/agent_status.py",
        "status": "planned"
    },
    {
        "path": "/agents",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/debug_routes.py",
        "status": "planned"
    },
    {
        "path": "/analyze",
        "method": "POST",
        "input_schema": "AshAnalysisRequest",
        "output_schema": "AshAnalysisResult",
        "module": "routes/ash_routes.py",
        "status": "active"
    },
    {
        "path": "/analyze-prompt",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": None,
        "module": "routes/agent_routes.py",
        "status": "active"
    },
    {
        "path": "/api/debugger/trace",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "DebuggerTraceResult",
        "module": "routes/debugger_routes.py",
        "status": "active"
    },
    {
        "path": "/api/delegate-stream",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/delegate_stream.py",
        "status": "active"
    },
    {
        "path": "/api/hal/generate",
        "method": "POST",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/hal_routes.py",
        "status": "planned"
    },
    {
        "path": "/api/hal/health",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "fallbacks/fix_hal_routes.py",
        "status": "planned"
    },
    {
        "path": "/api/hal/schema/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "fallbacks/fix_hal_routes.py",
        "status": "planned"
    },
    {
        "path": "/api/hal/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "fallbacks/fix_hal_routes.py",
        "status": "planned"
    },
    {
        "path": "/api/historian/log",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "HistorianDriftResult",
        "module": "routes/historian_routes.py",
        "status": "active"
    },
    {
        "path": "/api/loop/complete",
        "method": "POST",
        "input_schema": "LoopCompletionRequest",
        "output_schema": "LoopCompletionResponse",
        "module": "routes/loop_routes.py",
        "status": "active"
    },
    {
        "path": "/api/loop/persona-reflect",
        "method": "POST",
        "input_schema": "PersonaReflectRequest",
        "output_schema": "PersonaReflectResponse",
        "module": "routes/loop_routes.py",
        "status": "active"
    },
    {
        "path": "/api/loop/plan",
        "method": "POST",
        "input_schema": "LoopPlanRequest",
        "output_schema": "LoopPlanResponse",
        "module": "routes/loop_routes.py",
        "status": "active"
    },
    {
        "path": "/api/loop/reset",
        "method": "POST",
        "input_schema": None,
        "output_schema": "LoopResetResponse",
        "module": "routes/loop_routes.py",
        "status": "active"
    },
    {
        "path": "/api/loop/respond",
        "method": "POST",
        "input_schema": "LoopResponseRequest",
        "output_schema": "LoopResponseResult",
        "module": "routes/loop_routes.py",
        "status": "active"
    },
    {
        "path": "/api/loop/trace",
        "method": "GET",
        "input_schema": "Optional",
        "output_schema": "LoopTraceResponse",
        "module": "routes/loop_routes.py",
        "status": "active"
    },
    {
        "path": "/api/loop/trace",
        "method": "POST",
        "input_schema": "LoopTraceRequest",
        "output_schema": "LoopResetResponse",
        "module": "routes/loop_routes.py",
        "status": "active"
    },
    {
        "path": "/api/loop/validate",
        "method": "POST",
        "input_schema": "LoopValidateRequest",
        "output_schema": "LoopValidateResponse",
        "module": "routes/loop_routes.py",
        "status": "active"
    },
    {
        "path": "/api/memory/ping",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/memory_routes.py",
        "status": "planned"
    },
    {
        "path": "/api/memory/read",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/memory_routes.py",
        "status": "planned"
    },
    {
        "path": "/api/memory/write",
        "method": "POST",
        "input_schema": "dict",
        "output_schema": None,
        "module": "routes/memory_routes.py",
        "status": "active"
    },
    {
        "path": "/api/orchestrator/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/orchestrator/status.py",
        "status": "planned"
    },
    {
        "path": "/api/upload/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/upload_file_routes.py",
        "status": "planned"
    },
    {
        "path": "/audit",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/modules/orchestrator.py",
        "status": "planned"
    },
    {
        "path": "/audit",
        "method": "POST",
        "input_schema": "CTOAuditRequest",
        "output_schema": "CTOAuditResult",
        "module": "routes/cto_routes.py",
        "status": "active"
    },
    {
        "path": "/beliefs",
        "method": "POST",
        "input_schema": "SageBeliefRequest",
        "output_schema": "SageBeliefResponse",
        "module": "routes/sage_beliefs_routes.py",
        "status": "active"
    },
    {
        "path": "/beliefs",
        "method": "GET",
        "input_schema": "Optional",
        "output_schema": "SageBeliefResponse",
        "module": "routes/sage_beliefs_routes.py",
        "status": "active"
    },
    {
        "path": "/build",
        "method": "POST",
        "input_schema": "ForgeBuildRequest",
        "output_schema": "ForgeBuildResponse",
        "module": "routes/forge_build_routes.py",
        "status": "active"
    },
    {
        "path": "/build-ui",
        "method": "POST",
        "input_schema": "NovaUIRequest",
        "output_schema": "NovaUIResult",
        "module": "routes/nova_routes.py",
        "status": "active"
    },
    {
        "path": "/ceo-review",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": None,
        "module": "routes/agent_routes.py",
        "status": "active"
    },
    {
        "path": "/chain",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/orchestrator/chain.py",
        "status": "active"
    },
    {
        "path": "/chains",
        "method": "GET",
        "input_schema": None,
        "output_schema": "List",
        "module": "api/agent.py",
        "status": "active"
    },
    {
        "path": "/chains/{chain_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "api/agent.py",
        "status": "active"
    },
    {
        "path": "/chains/{chain_id}/steps/{step_number}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "api/agent.py",
        "status": "active"
    },
    {
        "path": "/challenge",
        "method": "POST",
        "input_schema": "BeliefChallengeRequest",
        "output_schema": None,
        "module": "routes/self_routes.py",
        "status": "active"
    },
    {
        "path": "/check",
        "method": "POST",
        "input_schema": "PessimistCheckRequest",
        "output_schema": "PessimistCheckResult",
        "module": "routes/pessimist_routes.py",
        "status": "active"
    },
    {
        "path": "/close",
        "method": "POST",
        "input_schema": "StreamCloseRequest",
        "output_schema": "StreamCloseResponse",
        "module": "routes/delegate_stream_routes.py",
        "status": "active"
    },
    {
        "path": "/config",
        "method": "POST",
        "input_schema": "AgentConfigRequest",
        "output_schema": "AgentConfigResponse",
        "module": "routes/agent_config_routes.py",
        "status": "active"
    },
    {
        "path": "/config/{agent_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "AgentConfigGetResponse",
        "module": "routes/agent_config_routes.py",
        "status": "active"
    },
    {
        "path": "/config/{agent_id}",
        "method": "DELETE",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "routes/agent_config_routes.py",
        "status": "active"
    },
    {
        "path": "/constraints",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/hal_routes.py",
        "status": "planned"
    },
    {
        "path": "/consult",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/orchestrator/consult.py",
        "status": "active"
    },
    {
        "path": "/context",
        "method": "POST",
        "input_schema": "AgentContextRequest",
        "output_schema": "AgentContextResponse",
        "module": "routes/agent_context_routes.py",
        "status": "active"
    },
    {
        "path": "/context/{agent_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "AgentContextResponse",
        "module": "routes/agent_context_routes.py",
        "status": "active"
    },
    {
        "path": "/core/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/core_router.py",
        "status": "planned"
    },
    {
        "path": "/create",
        "method": "POST",
        "input_schema": "AgentCreateRequest",
        "output_schema": None,
        "module": "api/modules/agent.py",
        "status": "active"
    },
    {
        "path": "/critic/review",
        "method": "POST",
        "input_schema": "LoopSummaryReviewRequest",
        "output_schema": "LoopReflectionRejection",
        "module": "routes/critic_routes.py",
        "status": "active"
    },
    {
        "path": "/critic/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/critic_router.py",
        "status": "planned"
    },
    {
        "path": "/cto-review",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": None,
        "module": "routes/agent_routes.py",
        "status": "active"
    },
    {
        "path": "/cto/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/cto_router.py",
        "status": "planned"
    },
    {
        "path": "/debug/analyze-loop",
        "method": "POST",
        "input_schema": "LoopDebugRequest",
        "output_schema": "LoopDebugResult",
        "module": "routes/debug_routes.py",
        "status": "active"
    },
    {
        "path": "/debug/hal-schema",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/debug_hal_schema.py",
        "status": "planned"
    },
    {
        "path": "/debug/performance",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/performance_monitoring.py",
        "status": "planned"
    },
    {
        "path": "/debug/simulate-load",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/performance_monitoring.py",
        "status": "active"
    },
    {
        "path": "/debug/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/status_debug.py",
        "status": "planned"
    },
    {
        "path": "/debugger/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/debugger_router.py",
        "status": "planned"
    },
    {
        "path": "/delegate",
        "method": "POST",
        "input_schema": None,
        "output_schema": "DelegationResponse",
        "module": "api/agent.py",
        "status": "active"
    },
    {
        "path": "/delegate",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/delegate_route.py",
        "status": "active"
    },
    {
        "path": "/delegate-stream",
        "method": "POST",
        "input_schema": "StreamRequest",
        "output_schema": "StreamResponse",
        "module": "routes/delegate_stream_routes.py",
        "status": "active"
    },
    {
        "path": "/devops",
        "method": "POST",
        "input_schema": "OpsAgentRequest",
        "output_schema": "OpsAgentResponse",
        "module": "routes/ops_agent_routes.py",
        "status": "active"
    },
    {
        "path": "/docs",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/docs.py",
        "status": "planned"
    },
    {
        "path": "/drift/report",
        "method": "POST",
        "input_schema": "DriftReportRequest",
        "output_schema": "DriftReportResponse",
        "module": "app/routes/drift_routes.py",
        "status": "active",
        "memory_tag": "phase3.0_sprint2_reflection_drift_plan_activation"
    },
    {
        "path": "/drift/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/drift_router.py",
        "status": "planned"
    },
    {
        "path": "/evaluate",
        "method": "POST",
        "input_schema": "CEOReviewRequest",
        "output_schema": "CEOReviewResult",
        "module": "routes/ceo_routes.py",
        "status": "active"
    },
    {
        "path": "/execute",
        "method": "POST",
        "input_schema": "AshExecutionRequest",
        "output_schema": "AshExecutionResult",
        "module": "routes/ash_routes.py",
        "status": "active"
    },
    {
        "path": "/execute",
        "method": "POST",
        "input_schema": "ExecuteRequest",
        "output_schema": "ExecuteResponse",
        "module": "app/routes/execute_routes.py",
        "status": "active",
        "memory_tag": "phase3.0_sprint1.1_integration_cleanup"
    },
    {
        "path": "/execute/{agent_id}",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/delegate_route.py",
        "status": "active"
    },
    {
        "path": "/forge/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/forge_router.py",
        "status": "planned"
    },
    {
        "path": "/generate",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/orchestrator/generate.py",
        "status": "active"
    },
    {
        "path": "/generate-code",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": None,
        "module": "routes/agent_routes.py",
        "status": "active"
    },
    {
        "path": "/get/{key}",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/memory.py",
        "status": "active"
    },
    {
        "path": "/goal",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/goal_route.py",
        "status": "active"
    },
    {
        "path": "/goal/{task_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/goal/{task_id}/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/guardian/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/guardian_router.py",
        "status": "planned"
    },
    {
        "path": "/hal/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/hal_router.py",
        "status": "planned"
    },
    {
        "path": "/health",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/health.py",
        "status": "planned"
    },
    {
        "path": "/historian/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/historian_router.py",
        "status": "planned"
    },
    {
        "path": "/history",
        "method": "GET",
        "input_schema": "Optional",
        "output_schema": None,
        "module": "api/memory.py",
        "status": "active"
    },
    {
        "path": "/journal",
        "method": "POST",
        "input_schema": "ObserverJournalRequest",
        "output_schema": "ObserverJournalResponse",
        "module": "routes/observer_routes.py",
        "status": "active"
    },
    {
        "path": "/journal/{entry_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "ObserverJournalEntry",
        "module": "routes/observer_routes.py",
        "status": "active"
    },
    {
        "path": "/list",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/modules/agent.py",
        "status": "active"
    },
    {
        "path": "/logs",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/logs.py",
        "status": "planned"
    },
    {
        "path": "/loop/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/loop_router.py",
        "status": "planned"
    },
    {
        "path": "/memory/get/{key}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "MemoryGetKeyResponse",
        "module": "app/routes/memory_routes.py",
        "status": "active",
        "memory_tag": "phase3.0_sprint1.1_integration_cleanup"
    },
    {
        "path": "/memory/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/memory_router.py",
        "status": "planned"
    },
    {
        "path": "/nova/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/nova_router.py",
        "status": "planned"
    },
    {
        "path": "/observer/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/observer_router.py",
        "status": "planned"
    },
    {
        "path": "/ops/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/ops_agent_router.py",
        "status": "planned"
    },
    {
        "path": "/orchestrator/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/orchestrator_router.py",
        "status": "planned"
    },
    {
        "path": "/pessimist/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/pessimist_router.py",
        "status": "planned"
    },
    {
        "path": "/plan",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/orchestrator/plan.py",
        "status": "active"
    },
    {
        "path": "/plan/activate",
        "method": "POST",
        "input_schema": "PlanActivationRequest",
        "output_schema": "PlanActivationResponse",
        "module": "app/routes/plan_routes.py",
        "status": "active",
        "memory_tag": "phase3.0_sprint2_reflection_drift_plan_activation"
    },
    {
        "path": "/plan/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/plan_router.py",
        "status": "planned"
    },
    {
        "path": "/project/{project_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}",
        "method": "POST",
        "input_schema": "ProjectUpdateRequest",
        "output_schema": None,
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}",
        "method": "DELETE",
        "input_schema": None,
        "output_schema": None,
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}/memory",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/projects/memory.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}/memory",
        "method": "POST",
        "input_schema": "MemoryUpdateRequest",
        "output_schema": None,
        "module": "api/projects/memory.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}/reflection",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}/reflection",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": None,
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}/reflection/history",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}/reflection",
        "method": "DELETE",
        "input_schema": None,
        "output_schema": None,
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/projects/status.py",
        "status": "planned"
    },
    {
        "path": "/projects",
        "method": "POST",
        "input_schema": "ProjectCreateRequest",
        "output_schema": None,
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/projects/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/project_router.py",
        "status": "planned"
    },
    {
        "path": "/prompt",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/prompt_route.py",
        "status": "active"
    },
    {
        "path": "/prompt/{prompt_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/prompt/{prompt_id}/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/query",
        "method": "POST",
        "input_schema": "MemoryQueryRequest",
        "output_schema": None,
        "module": "api/memory.py",
        "status": "active"
    },
    {
        "path": "/reflect",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/orchestrator/reflect.py",
        "status": "active"
    },
    {
        "path": "/reflection/result/{reflection_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "ReflectionResultResponse",
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/reflection/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/reflection_router.py",
        "status": "planned"
    },
    {
        "path": "/reflection/trigger",
        "method": "POST",
        "input_schema": "ReflectionTriggerRequest",
        "output_schema": "ReflectionResponse",
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/reflection/trigger-scan",
        "method": "POST",
        "input_schema": "ReflectionScanRequest",
        "output_schema": "ReflectionResponse",
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/reflection/{reflection_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "app/routes/reflection_routes.py",
        "status": "active"
    },
    {
        "path": "/register",
        "method": "POST",
        "input_schema": "AgentRegisterRequest",
        "output_schema": None,
        "module": "api/modules/agent.py",
        "status": "active"
    },
    {
        "path": "/resolve",
        "method": "POST",
        "input_schema": "AshResolutionRequest",
        "output_schema": "AshResolutionResult",
        "module": "routes/ash_routes.py",
        "status": "active"
    },
    {
        "path": "/sage/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/sage_router.py",
        "status": "planned"
    },
    {
        "path": "/scan",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/orchestrator/scan.py",
        "status": "active"
    },
    {
        "path": "/schema/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/schema_router.py",
        "status": "planned"
    },
    {
        "path": "/self/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/self_router.py",
        "status": "planned"
    },
    {
        "path": "/sitegen/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/sitegen_router.py",
        "status": "planned"
    },
    {
        "path": "/skeptic/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/skeptic_router.py",
        "status": "planned"
    },
    {
        "path": "/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/status.py",
        "status": "planned"
    },
    {
        "path": "/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/modules/agent.py",
        "status": "active"
    },
    {
        "path": "/stream",
        "method": "POST",
        "input_schema": "StreamRequest",
        "output_schema": "StreamResponse",
        "module": "routes/delegate_stream_routes.py",
        "status": "active"
    },
    {
        "path": "/stream/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/delegate_stream_router.py",
        "status": "planned"
    },
    {
        "path": "/summarize",
        "method": "POST",
        "input_schema": "SageSummaryRequest",
        "output_schema": "SageSummaryResponse",
        "module": "routes/sage_summary_routes.py",
        "status": "active"
    },
    {
        "path": "/sync",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/orchestrator/sync.py",
        "status": "active"
    },
    {
        "path": "/system/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/system_router.py",
        "status": "planned"
    },
    {
        "path": "/task",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/task_route.py",
        "status": "active"
    },
    {
        "path": "/task/{task_id}",
        "method": "GET",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/task/{task_id}/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/test",
        "method": "POST",
        "input_schema": "AshTestRequest",
        "output_schema": "AshTestResult",
        "module": "routes/ash_routes.py",
        "status": "active"
    },
    {
        "path": "/train",
        "method": "POST",
        "input_schema": "TrainerRequest",
        "output_schema": "TrainerResponse",
        "module": "routes/trainer_routes.py",
        "status": "active"
    },
    {
        "path": "/trainer/status",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/trainer_router.py",
        "status": "planned"
    },
    {
        "path": "/upload",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/upload_file.py",
        "status": "active"
    },
    {
        "path": "/validate",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/orchestrator/validate.py",
        "status": "active"
    },
    {
        "path": "/validate-schema",
        "method": "POST",
        "input_schema": "CTOSchemaRequest",
        "output_schema": "CTOSchemaResult",
        "module": "routes/cto_routes.py",
        "status": "active"
    },
    {
        "path": "/ws",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "api/websocket.py",
        "status": "planned"
    }
]

# Helper function to get endpoint by path and method
def get_endpoint(path: str, method: str) -> Optional[EndpointEntry]:
    """Get endpoint entry by path and method."""
    for entry in ENDPOINT_REGISTRY:
        if entry["path"] == path and entry["method"] == method:
            return EndpointEntry(**entry)
    return None

# Helper function to get all endpoints
def get_all_endpoints() -> List[EndpointEntry]:
    """Get all endpoint entries."""
    return [EndpointEntry(**entry) for entry in ENDPOINT_REGISTRY]

