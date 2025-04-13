from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from app.modules.memory_writer import write_memory, memory_store, generate_reflection
from app.modules.memory_summarizer import summarize_memories
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import os

class MemoryEntry(BaseModel):
    agent_id: str
    memory_type: str
    content: str
    tags: List[str] = []

class ReflectionRequest(BaseModel):
    agent_id: str
    type: str
    limit: int = 5

class SummarizationRequest(BaseModel):
    agent_id: str
    type: Optional[str] = None
    limit: int = 10

router = APIRouter()

@router.post("/write")
async def memory_write(request: Request):
    try:
        body = await request.json()
        memory_entry = MemoryEntry(**body)
        
        memory = write_memory(
            agent_id=memory_entry.agent_id,
            type=memory_entry.memory_type,
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
        
        filtered_memories = [m for m in memory_store if m["agent_id"] == agent_id]
        
        if type:
            filtered_memories = [m for m in filtered_memories if m["type"] == type]
        
        if tag:
            filtered_memories = [m for m in filtered_memories if tag in m["tags"]]
        
        if since:
            try:
                since_dt = datetime.fromisoformat(since)
                filtered_memories = [m for m in filtered_memories if datetime.fromisoformat(m["timestamp"]) > since_dt]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid ISO 8601 format for 'since' parameter")
        
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        if limit and limit > 0:
            filtered_memories = filtered_memories[:limit]
        
        return {"status": "ok", "memories": filtered_memories}
    except HTTPException as e:
        print(f"❌ MemoryReader error: {str(e.detail)}")
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})
    except Exception as e:
        print(f"❌ MemoryReader error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.post("/reflect")
async def reflect_on_memories(request: Request):
    try:
        body = await request.json()
        reflection_request = ReflectionRequest(**body)
        
        filtered_memories = [m for m in memory_store if m["agent_id"] == reflection_request.agent_id]
        filtered_memories = [m for m in filtered_memories if m["type"] == reflection_request.type]
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        filtered_memories = filtered_memories[:reflection_request.limit]
        
        reflection_text = generate_reflection(filtered_memories)
        
        memory = write_memory(
            agent_id=reflection_request.agent_id,
            type="reflection",
            content=reflection_text,
            tags=["reflection", f"based_on_{reflection_request.type}"]
        )
        
        return {
            "status": "ok",
            "reflection": reflection_text,
            "memory_id": memory["memory_id"]
        }
    except Exception as e:
        print(f"❌ Reflection Engine error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.post("/summarize")
async def summarize_memory(request: Request):
    try:
        body = await request.json()
        summarize_request = SummarizationRequest(**body)

        filtered_memories = [m for m in memory_store if m["agent_id"] == summarize_request.agent_id]
        if summarize_request.type:
            filtered_memories = [m for m in filtered_memories if m["type"] == summarize_request.type]

        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        filtered_memories = filtered_memories[:summarize_request.limit]

        summary = summarize_memories(filtered_memories)

        return {
            "status": "ok",
            "summary": summary,
            "memory_count": len(filtered_memories)
        }
    except Exception as e:
        print(f"❌ MemorySummarizer error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@router.post("/admin/reset-memory-db")
async def reset_memory_db():
    try:
        os.remove("/app/db/memory.db")
        print("🧨 memory.db deleted from /app/db/")
        return {"status": "ok", "message": "Memory DB deleted. Restart app to rebuild schema."}
    except FileNotFoundError:
        return {"status": "ok", "message": "DB already deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/thread")
async def memory_thread(goal_id: str):
    try:
        filtered = [m for m in memory_store if m.get("goal_id") == goal_id]
        return {"status": "ok", "thread": filtered}
    except Exception as e:
        print(f"❌ MemoryThread error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
