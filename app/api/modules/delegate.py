from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.modules.memory_writer import write_memory
from pydantic import BaseModel
from typing import Optional

class DelegationRequest(BaseModel):
    from_agent: str
    to_agent: str
    task: str

router = APIRouter()

@router.post("/delegate")
async def delegate_task(request: Request):
    try:
        # Parse request body
        body = await request.json()
        delegation_request = DelegationRequest(**body)
        
        # Validate required fields
        if not delegation_request.from_agent or not delegation_request.to_agent or not delegation_request.task:
            raise HTTPException(status_code=400, detail="Missing required fields: from_agent, to_agent, and task are required")
        
        # Format the delegation message
        from_agent_upper = delegation_request.from_agent.upper()
        delegation_message = f"Received task from {from_agent_upper}: {delegation_request.task}"
        
        # Write delegation memory for the receiving agent
        memory = write_memory(
            agent_id=delegation_request.to_agent,
            type="delegation",
            content=delegation_message,
            tags=[f"from:{delegation_request.from_agent}"]
        )
        
        # Return response
        return {
            "status": "ok",
            "delegated_to": delegation_request.to_agent,
            "memory_id": memory["memory_id"]
        }
    except HTTPException as e:
        print(f"❌ Delegation Engine error: {str(e.detail)}")
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})
    except Exception as e:
        print(f"❌ Delegation Engine error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
