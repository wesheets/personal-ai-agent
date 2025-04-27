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
        "path": "/delegate-stream",
        "method": "POST",
        "input_schema": "Request",
        "output_schema": None,
        "module": "api/streaming_route.py",
        "status": "active"
    },
    {
        "path": "/delete/{memory_id}",
        "method": "DELETE",
        "input_schema": None,
        "output_schema": None,
        "module": "api/memory.py",
        "status": "planned"
    },
    {
        "path": "/diagnostics/routes",
        "method": "GET",
        "input_schema": None,
        "output_schema": None,
        "module": "routes/diagnostics_routes.py",
        "status": "planned"
    },
    {
        "path": "/drift-summary",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": None,
        "module": "routes/agent_routes.py",
        "status": "active"
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
        "path": "/echo",
        "method": "POST",
        "input_schema": "EchoRequest",
        "output_schema": "EchoResponse",
        "module": "routes/echo_routes.py",
        "status": "active"
    },
    {
        "path": "/edit",
        "method": "POST",
        "input_schema": "EditRequest",
        "output_schema": "EditResponse",
        "module": "routes/edit_routes.py",
        "status": "active"
    },
    {
        "path": "/embed",
        "method": "POST",
        "input_schema": "EmbedRequest",
        "output_schema": "EmbedResponse",
        "module": "routes/embed_routes.py",
        "status": "active"
    },
    {
        "path": "/evaluate",
        "method": "POST",
        "input_schema": "EvaluateRequest",
        "output_schema": "EvaluateResponse",
        "module": "routes/evaluate_routes.py",
        "status": "active"
    },
    {
        "path": "/execute",
        "method": "POST",
        "input_schema": "ExecuteRequest",
        "output_schema": "ExecuteResponse",
        "module": "routes/execute_routes.py",
        "status": "active"
    },
    {
        "path": "/explain",
        "method": "POST",
        "input_schema": "ExplainRequest",
        "output_schema": "ExplainResponse",
        "module": "routes/explain_routes.py",
        "status": "active"
    },
    {
        "path": "/extract",
        "method": "POST",
        "input_schema": "ExtractRequest",
        "output_schema": "ExtractResponse",
        "module": "routes/extract_routes.py",
        "status": "active"
    },
    {
        "path": "/filter",
        "method": "POST",
        "input_schema": "FilterRequest",
        "output_schema": "FilterResponse",
        "module": "routes/filter_routes.py",
        "status": "active"
    },
    {
        "path": "/fix",
        "method": "POST",
        "input_schema": "FixRequest",
        "output_schema": "FixResponse",
        "module": "routes/fix_routes.py",
        "status": "active"
    },
    {
        "path": "/generate",
        "method": "POST",
        "input_schema": "GenerateRequest",
        "output_schema": "GenerateResponse",
        "module": "routes/generate_routes.py",
        "status": "active"
    },
    {
        "path": "/get",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/memory.py",
        "status": "active"
    },
    {
        "path": "/get/{memory_id}",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/memory.py",
        "status": "active"
    },
    {
        "path": "/goal/{task_id}",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/goal/{task_id}/edit-prompt",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/goal/{task_id}/edit-system",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/goal/{task_id}/restart",
        "method": "POST",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/goal/{task_id}/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/goal/{task_id}/stop",
        "method": "POST",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/goals",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/goals/create",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "api/control.py",
        "status": "active"
    },
    {
        "path": "/hal/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/hal_router.py",
        "status": "planned"
    },
    {
        "path": "/health",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "api/health.py",
        "status": "planned"
    },
    {
        "path": "/historian/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/historian_router.py",
        "status": "planned"
    },
    {
        "path": "/history",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "api/history.py",
        "status": "planned"
    },
    {
        "path": "/history/{session_id}",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "api/history.py",
        "status": "planned"
    },
    {
        "path": "/init",
        "method": "POST",
        "input_schema": "StreamInitRequest",
        "output_schema": "StreamInitResponse",
        "module": "routes/delegate_stream_routes.py",
        "status": "active"
    },
    {
        "path": "/inspect",
        "method": "POST",
        "input_schema": "InspectRequest",
        "output_schema": "InspectResponse",
        "module": "routes/inspect_routes.py",
        "status": "active"
    },
    {
        "path": "/list",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/agent.py",
        "status": "active"
    },
    {
        "path": "/loop/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/loop_router.py",
        "status": "planned"
    },
    {
        "path": "/memory",
        "method": "POST",
        "input_schema": "MemoryRequest",
        "output_schema": "MemoryResponse",
        "module": "routes/memory_routes.py",
        "status": "active"
    },
    {
        "path": "/memory/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/memory_router.py",
        "status": "planned"
    },
    {
        "path": "/message",
        "method": "POST",
        "input_schema": "MessageRequest",
        "output_schema": "MessageResponse",
        "module": "routes/message_routes.py",
        "status": "active"
    },
    {
        "path": "/message/{session_id}",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/message.py",
        "status": "active"
    },
    {
        "path": "/message/{session_id}",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "api/message.py",
        "status": "active"
    },
    {
        "path": "/message/{session_id}/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/message.py",
        "status": "active"
    },
    {
        "path": "/messages",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/message.py",
        "status": "active"
    },
    {
        "path": "/messages/create",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "api/message.py",
        "status": "active"
    },
    {
        "path": "/nova/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/nova_router.py",
        "status": "planned"
    },
    {
        "path": "/orchestrator/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/orchestrator_router.py",
        "status": "planned"
    },
    {
        "path": "/parse",
        "method": "POST",
        "input_schema": "ParseRequest",
        "output_schema": "ParseResponse",
        "module": "routes/parse_routes.py",
        "status": "active"
    },
    {
        "path": "/pessimist/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/pessimist_router.py",
        "status": "planned"
    },
    {
        "path": "/plan",
        "method": "POST",
        "input_schema": "PlanRequest",
        "output_schema": "PlanResponse",
        "module": "routes/plan_routes.py",
        "status": "active"
    },
    {
        "path": "/planner/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/planner_router.py",
        "status": "planned"
    },
    {
        "path": "/predict",
        "method": "POST",
        "input_schema": "PredictRequest",
        "output_schema": "PredictResponse",
        "module": "routes/predict_routes.py",
        "status": "active"
    },
    {
        "path": "/process",
        "method": "POST",
        "input_schema": "ProcessRequest",
        "output_schema": "ProcessResponse",
        "module": "routes/process_routes.py",
        "status": "active"
    },
    {
        "path": "/project",
        "method": "POST",
        "input_schema": "ProjectRequest",
        "output_schema": "ProjectResponse",
        "module": "routes/project_routes.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}/tasks",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/project/{project_id}/tasks/create",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/projects",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/projects/create",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "api/projects/projects.py",
        "status": "active"
    },
    {
        "path": "/query",
        "method": "POST",
        "input_schema": "QueryRequest",
        "output_schema": "QueryResponse",
        "module": "routes/query_routes.py",
        "status": "active"
    },
    {
        "path": "/rank",
        "method": "POST",
        "input_schema": "RankRequest",
        "output_schema": "RankResponse",
        "module": "routes/rank_routes.py",
        "status": "active"
    },
    {
        "path": "/read",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/memory.py",
        "status": "active"
    },
    {
        "path": "/read/{memory_id}",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/memory.py",
        "status": "active"
    },
    {
        "path": "/reason",
        "method": "POST",
        "input_schema": "ReasonRequest",
        "output_schema": "ReasonResponse",
        "module": "routes/reason_routes.py",
        "status": "active"
    },
    {
        "path": "/reflect",
        "method": "POST",
        "input_schema": "ReflectRequest",
        "output_schema": "ReflectResponse",
        "module": "routes/reflect_routes.py",
        "status": "active"
    },
    {
        "path": "/reflection/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/reflection_router.py",
        "status": "planned"
    },
    {
        "path": "/register",
        "method": "POST",
        "input_schema": "AgentRegisterRequest",
        "output_schema": "AgentRegisterResponse",
        "module": "routes/agent_register_routes.py",
        "status": "active"
    },
    {
        "path": "/registry/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/registry_router.py",
        "status": "planned"
    },
    {
        "path": "/render",
        "method": "POST",
        "input_schema": "RenderRequest",
        "output_schema": "RenderResponse",
        "module": "routes/render_routes.py",
        "status": "active"
    },
    {
        "path": "/respond",
        "method": "POST",
        "input_schema": "RespondRequest",
        "output_schema": "RespondResponse",
        "module": "routes/respond_routes.py",
        "status": "active"
    },
    {
        "path": "/review",
        "method": "POST",
        "input_schema": "ReviewRequest",
        "output_schema": "ReviewResponse",
        "module": "routes/review_routes.py",
        "status": "active"
    },
    {
        "path": "/route",
        "method": "POST",
        "input_schema": "RouteRequest",
        "output_schema": "RouteResponse",
        "module": "routes/route_routes.py",
        "status": "active"
    },
    {
        "path": "/sage/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/sage_router.py",
        "status": "planned"
    },
    {
        "path": "/scan",
        "method": "POST",
        "input_schema": "ScanRequest",
        "output_schema": "ScanResponse",
        "module": "routes/scan_routes.py",
        "status": "active"
    },
    {
        "path": "/search",
        "method": "POST",
        "input_schema": "SearchRequest",
        "output_schema": "SearchResponse",
        "module": "routes/search_routes.py",
        "status": "active"
    },
    {
        "path": "/self/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/self_router.py",
        "status": "planned"
    },
    {
        "path": "/send",
        "method": "POST",
        "input_schema": "StreamSendRequest",
        "output_schema": "StreamSendResponse",
        "module": "routes/delegate_stream_routes.py",
        "status": "active"
    },
    {
        "path": "/session",
        "method": "POST",
        "input_schema": "SessionRequest",
        "output_schema": "SessionResponse",
        "module": "routes/session_routes.py",
        "status": "active"
    },
    {
        "path": "/session/{session_id}",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/session.py",
        "status": "active"
    },
    {
        "path": "/session/{session_id}/messages",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/session.py",
        "status": "active"
    },
    {
        "path": "/session/{session_id}/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/session.py",
        "status": "active"
    },
    {
        "path": "/sessions",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/session.py",
        "status": "active"
    },
    {
        "path": "/sessions/create",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "api/session.py",
        "status": "active"
    },
    {
        "path": "/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "api/status.py",
        "status": "planned"
    },
    {
        "path": "/stream",
        "method": "POST",
        "input_schema": "StreamRequest",
        "output_schema": "StreamResponse",
        "module": "routes/stream_routes.py",
        "status": "active"
    },
    {
        "path": "/summarize",
        "method": "POST",
        "input_schema": "SummarizeRequest",
        "output_schema": "SummarizeResponse",
        "module": "routes/summarize_routes.py",
        "status": "active"
    },
    {
        "path": "/system/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/system_router.py",
        "status": "planned"
    },
    {
        "path": "/task",
        "method": "POST",
        "input_schema": "TaskRequest",
        "output_schema": "TaskResponse",
        "module": "routes/task_routes.py",
        "status": "active"
    },
    {
        "path": "/task/{task_id}",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/task.py",
        "status": "active"
    },
    {
        "path": "/task/{task_id}/status",
        "method": "GET",
        "input_schema": null,
        "output_schema": "Dict",
        "module": "api/task.py",
        "status": "active"
    },
    {
        "path": "/tasks",
        "method": "GET",
        "input_schema": null,
        "output_schema": "List",
        "module": "api/task.py",
        "status": "active"
    },
    {
        "path": "/tasks/create",
        "method": "POST",
        "input_schema": "Dict",
        "output_schema": "Dict",
        "module": "api/task.py",
        "status": "active"
    },
    {
        "path": "/test",
        "method": "POST",
        "input_schema": "TestRequest",
        "output_schema": "TestResponse",
        "module": "routes/test_routes.py",
        "status": "active"
    },
    {
        "path": "/trace",
        "method": "POST",
        "input_schema": "TraceRequest",
        "output_schema": "TraceResponse",
        "module": "routes/trace_routes.py",
        "status": "active"
    },
    {
        "path": "/transform",
        "method": "POST",
        "input_schema": "TransformRequest",
        "output_schema": "TransformResponse",
        "module": "routes/transform_routes.py",
        "status": "active"
    },
    {
        "path": "/translate",
        "method": "POST",
        "input_schema": "TranslateRequest",
        "output_schema": "TranslateResponse",
        "module": "routes/translate_routes.py",
        "status": "active"
    },
    {
        "path": "/upload",
        "method": "POST",
        "input_schema": null,
        "output_schema": null,
        "module": "routes/upload_file_routes.py",
        "status": "planned"
    },
    {
        "path": "/validate",
        "method": "POST",
        "input_schema": "ValidateRequest",
        "output_schema": "ValidateResponse",
        "module": "routes/validate_routes.py",
        "status": "active"
    },
    {
        "path": "/verify",
        "method": "POST",
        "input_schema": "VerifyRequest",
        "output_schema": "VerifyResponse",
        "module": "routes/verify_routes.py",
        "status": "active"
    },
    {
        "path": "/version",
        "method": "GET",
        "input_schema": null,
        "output_schema": null,
        "module": "api/version.py",
        "status": "planned"
    },
    {
        "path": "/write",
        "method": "POST",
        "input_schema": "MemoryWriteRequest",
        "output_schema": null,
        "module": "api/memory.py",
        "status": "active"
    }
]

# For backward compatibility, also provide the endpoints as a list
ENDPOINT_LIST = ENDPOINT_REGISTRY
