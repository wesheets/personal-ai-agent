from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.modules.memory_writer import write_memory
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import uuid
from datetime import datetime

class DelegationRequest(BaseModel):
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_name: str
    memory_trace_id: Optional[str] = None
    objective: str
    required_capabilities: Optional[List[str]] = []
    input_data: Optional[Dict[str, Any]] = {}
    auto_execute: Optional[bool] = False
    from_agent: Optional[str] = None  # For backward compatibility

router = APIRouter()

@router.post("/delegate")
async def delegate_task(request: Request):
    try:
        # Parse request body
        body = await request.json()
        delegation_request = DelegationRequest(**body)
        
        # Generate task_id if not provided
        if not delegation_request.task_id:
            delegation_request.task_id = str(uuid.uuid4())
            
        # Generate memory_trace_id if not provided
        if not delegation_request.memory_trace_id:
            delegation_request.memory_trace_id = str(uuid.uuid4())
            
        # Generate delegation_id for tracking
        delegation_id = str(uuid.uuid4())
        
        # Validate required fields
        if not delegation_request.agent_name or not delegation_request.objective:
            raise HTTPException(status_code=400, detail="Missing required fields: agent_name and objective are required")
        
        # Check agent capabilities if required_capabilities is provided
        if delegation_request.required_capabilities and len(delegation_request.required_capabilities) > 0:
            # Import here to avoid circular imports
            from app.core.agent_registry import agent_registry
            
            # Check if agent exists
            if delegation_request.agent_name not in agent_registry:
                return JSONResponse(content={
                    "status": "error",
                    "log": f"Agent '{delegation_request.agent_name}' not found."
                })
                
            # Get agent capabilities
            agent_data = agent_registry[delegation_request.agent_name]
            agent_capabilities = agent_data.get("tools", [])
            
            # Check if agent has all required capabilities
            missing_capabilities = [cap for cap in delegation_request.required_capabilities if cap not in agent_capabilities]
            if missing_capabilities:
                return JSONResponse(content={
                    "status": "error",
                    "log": f"Agent '{delegation_request.agent_name}' lacks required capability: {', '.join(missing_capabilities)}."
                })
        
        # Format the delegation message
        from_agent = delegation_request.from_agent.upper() if delegation_request.from_agent else "SYSTEM"
        delegation_message = f"Received task from {from_agent}: {delegation_request.objective}"
        
        # Write delegation memory for the receiving agent
        memory = write_memory(
            agent_id=delegation_request.agent_name,
            type="delegation_log",
            content=delegation_message,
            tags=[f"from:{delegation_request.from_agent}" if delegation_request.from_agent else "from:system"],
            project_id=delegation_request.project_id,
            status="pending",
            task_type="delegation",
            task_id=delegation_request.task_id,
            memory_trace_id=delegation_request.memory_trace_id
        )
        
        result_summary = "Agent accepted task."
        
        # Handle auto-execute if enabled
        if delegation_request.auto_execute:
            try:
                # Import here to avoid circular imports
                import httpx
                
                # Determine which endpoint to use based on complexity
                if "summarize" in delegation_request.objective.lower() or "analyze" in delegation_request.objective.lower():
                    # Use loop for more complex tasks
                    async with httpx.AsyncClient() as client:
                        loop_response = await client.post(
                            "http://localhost:3000/api/modules/agent/loop",
                            json={
                                "agent_id": delegation_request.agent_name,
                                "loop_type": "task",
                                "project_id": delegation_request.project_id,
                                "task_id": delegation_request.task_id,
                                "memory_trace_id": delegation_request.memory_trace_id
                            }
                        )
                        
                        if loop_response.status_code == 200:
                            loop_result = loop_response.json()
                            result_summary = f"Agent executed task via loop: {loop_result.get('loop_summary', '')[:100]}..."
                            
                            # Log the delegated response
                            write_memory(
                                agent_id=delegation_request.agent_name,
                                type="delegated_response",
                                content=f"Loop execution result: {loop_result.get('loop_result', '')}",
                                tags=["auto_execute", "loop"],
                                project_id=delegation_request.project_id,
                                status="completed",
                                task_type="delegated_response",
                                task_id=delegation_request.task_id,
                                memory_trace_id=delegation_request.memory_trace_id
                            )
                else:
                    # Use run for simpler tasks
                    async with httpx.AsyncClient() as client:
                        run_response = await client.post(
                            "http://localhost:3000/api/modules/agent/run",
                            json={
                                "agent_id": delegation_request.agent_name,
                                "prompt": delegation_request.objective
                            }
                        )
                        
                        if run_response.status_code == 200:
                            run_result = run_response.json()
                            result_summary = f"Agent executed task: {run_result.get('response', '')[:100]}..."
                            
                            # Log the delegated response
                            write_memory(
                                agent_id=delegation_request.agent_name,
                                type="delegated_response",
                                content=f"Execution result: {run_result.get('response', '')}",
                                tags=["auto_execute", "run"],
                                project_id=delegation_request.project_id,
                                status="completed",
                                task_type="delegated_response",
                                task_id=delegation_request.task_id,
                                memory_trace_id=delegation_request.memory_trace_id
                            )
            except Exception as e:
                print(f"❌ Auto-execute error: {str(e)}")
                result_summary = f"Task accepted but auto-execute failed: {str(e)}"
        
        # Return structured response
        return {
            "status": "success",
            "delegation_id": delegation_id,
            "to_agent": delegation_request.agent_name,
            "task_id": delegation_request.task_id,
            "result_summary": result_summary,
            "feedback_required": False
        }
    except HTTPException as e:
        print(f"❌ Delegation Engine error: {str(e.detail)}")
        return JSONResponse(status_code=e.status_code, content={
            "status": "error",
            "log": e.detail
        })
    except Exception as e:
        print(f"❌ Delegation Engine error: {str(e)}")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "log": str(e)
        })
