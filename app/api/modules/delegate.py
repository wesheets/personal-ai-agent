from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.modules.memory_writer import write_memory
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from src.utils.debug_logger import log_test_result
from app.core.agent_loader import get_all_agents

router = APIRouter()

class DelegationRequest(BaseModel):
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_name: str
    memory_trace_id: Optional[str] = None
    objective: str
    required_capabilities: Optional[List[str]] = []
    input_data: Optional[Dict[str, Any]] = {}
    auto_execute: Optional[bool] = False
    from_agent: Optional[str] = None

@router.post("/delegate")
async def delegate_task(request: Request):
    try:
        body = await request.json()
        delegation_request = DelegationRequest(**body)

        # Fill in defaults
        delegation_request.task_id = delegation_request.task_id or str(uuid.uuid4())
        delegation_request.memory_trace_id = delegation_request.memory_trace_id or str(uuid.uuid4())
        delegation_id = str(uuid.uuid4())

        # Validation
        if not delegation_request.agent_name or not delegation_request.objective:
            raise HTTPException(status_code=400, detail="Missing required fields: agent_name and objective are required")
        
        # Check agent capabilities if required_capabilities is provided
        if delegation_request.required_capabilities and len(delegation_request.required_capabilities) > 0:
            # Get agent registry
            agent_registry = get_all_agents()
            
            # Check if agent exists
            if delegation_request.agent_name not in agent_registry:
                log_test_result("Delegation", "/api/delegate", "FAIL", f"Agent '{delegation_request.agent_name}' not found", "Agent not in registry")
                return JSONResponse(content={
                    "status": "error",
                    "log": f"Agent '{delegation_request.agent_name}' not found."
                })
                
            # Check capabilities
            capabilities = agent_registry[delegation_request.agent_name].get("tools", [])
            missing = [cap for cap in delegation_request.required_capabilities if cap not in capabilities]
            if missing:
                return JSONResponse(content={
                    "status": "error",
                    "log": f"Missing capabilities: {', '.join(missing)}"
                })

        # Save memory for delegated task
        from_agent = delegation_request.from_agent or "system"
        memory = write_memory(
            agent_id=delegation_request.agent_name,
            type="delegation_log",
            content=f"Task from {from_agent.upper()}: {delegation_request.objective}",
            tags=[f"from:{from_agent}"],
            project_id=delegation_request.project_id,
            task_id=delegation_request.task_id,
            memory_trace_id=delegation_request.memory_trace_id,
            task_type="delegation",
            status="pending"
        )

        # Save memory for from_agent if defined
        if delegation_request.from_agent:
            write_memory(
                agent_id=delegation_request.from_agent,
                type="delegation_log",
                content=f"Delegated to {delegation_request.agent_name.upper()}: {delegation_request.objective}",
                tags=[f"to:{delegation_request.agent_name}"],
                project_id=delegation_request.project_id,
                task_id=delegation_request.task_id,
                memory_trace_id=delegation_request.memory_trace_id,
                task_type="delegation",
                status="delegated"
            )

        result_summary = "Agent accepted task."

        # Auto-execute if requested
        if delegation_request.auto_execute:
            import httpx
            url = "https://web-production-2639.up.railway.app"

            try:
                async with httpx.AsyncClient() as client:
                    endpoint = "/api/modules/agent/run"
                    payload = {
                        "agent_id": delegation_request.agent_name,
                        "prompt": delegation_request.objective
                    }

                    if "summarize" in delegation_request.objective.lower():
                        endpoint = "/api/modules/agent/loop"
                        payload = {
                            "agent_id": delegation_request.agent_name,
                            "loop_type": "task",
                            "project_id": delegation_request.project_id,
                            "task_id": delegation_request.task_id,
                            "memory_trace_id": delegation_request.memory_trace_id
                        }

                    response = await client.post(f"{url}{endpoint}", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        result_summary = data.get("response") or data.get("loop_summary", "")[:150]

                        write_memory(
                            agent_id=delegation_request.agent_name,
                            type="delegated_response",
                            content=result_summary,
                            tags=["auto_execute"],
                            project_id=delegation_request.project_id,
                            task_id=delegation_request.task_id,
                            memory_trace_id=delegation_request.memory_trace_id,
                            task_type="delegated_response",
                            status="completed"
                        )
            except Exception as e:
                result_summary = f"Task accepted, auto-execute failed: {str(e)}"

        return {
            "status": "success",
            "delegation_id": delegation_id,
            "to_agent": delegation_request.agent_name,
            "task_id": delegation_request.task_id,
            "result_summary": result_summary,
            "feedback_required": False
        }

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={
            "status": "error",
            "log": e.detail
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error",
            "log": str(e)
        })
