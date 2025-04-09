from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from app.modules.memory_writer import write_memory, memory_store
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MemoryEntry(BaseModel):
    agent_id: str
    memory_type: str
    content: str
    tags: List[str] = []

router = APIRouter()

@router.post("/write")
async def memory_write(request: Request):
    try:
        body = await request.json()
        memory_entry = MemoryEntry(**body)
        
        memory = write_memory(
            agent_id=memory_entry.agent_id,
            type=memory_entry.memory_type,  # Pass memory_type to type parameter
            content=memory_entry.content,
            tags=memory_entry.tags
        )
        return JSONResponse(status_code=200, content={"status": "ok", "memory_id": memory["memory_id"]})
    except Exception as e:
        print(f"❌ MemoryWriter error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.get("/read")
async def read_memory(
    agent_id: str,
    type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = 10,
    since: Optional[str] = None
):
    try:
        if not agent_id:
            raise HTTPException(status_code=400, detail="agent_id is required")
        
        # Filter memories by agent_id
        filtered_memories = [m for m in memory_store if m["agent_id"] == agent_id]
        
        # Apply type filter if provided
        if type:
            filtered_memories = [m for m in filtered_memories if m["type"] == type]
        
        # Apply tag filter if provided
        if tag:
            filtered_memories = [m for m in filtered_memories if tag in m["tags"]]
        
        # Apply since filter if provided
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
                filtered_memories = [
                    m for m in filtered_memories 
                    if datetime.fromisoformat(m["timestamp"]) > since_dt
                ]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid ISO 8601 format for 'since' parameter")
        
        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        if limit and limit > 0:
            filtered_memories = filtered_memories[:limit]
        
        return {
            "status": "ok",
            "memories": filtered_memories
        }
    except HTTPException as e:
        print(f"❌ MemoryReader error: {str(e.detail)}")
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})
    except Exception as e:
        print(f"❌ MemoryReader error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
