from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.modules.memory_writer import write_memory

router = APIRouter()

@router.post("/api/modules/memory/write")
async def memory_write(request: Request):
    try:
        body = await request.json()
        memory = write_memory(
            agent_id=body["agent_id"],
            type=body["type"],
            content=body["content"],
            tags=body.get("tags", [])
        )
        return JSONResponse(status_code=200, content={"status": "ok", "memory_id": memory["memory_id"]})
    except Exception as e:
        print(f"❌ MemoryWriter error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
