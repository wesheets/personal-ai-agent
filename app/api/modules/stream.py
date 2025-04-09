from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.modules.memory_writer import memory_store
from typing import Optional
from datetime import datetime

router = APIRouter()

@router.get("/stream")
async def stream_memories(
    agent_id: Optional[str] = None,
    type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = 20
):
    try:
        # Start with all memories
        filtered_memories = memory_store.copy()
        
        # Filter memories by agent_id if provided
        if agent_id:
            filtered_memories = [m for m in filtered_memories if m["agent_id"] == agent_id]
        
        # Apply type filter if provided
        if type:
            filtered_memories = [m for m in filtered_memories if m["type"] == type]
        
        # Apply tag filter if provided
        if tag:
            filtered_memories = [m for m in filtered_memories if tag in m["tags"]]
        
        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        if limit and limit > 0:
            filtered_memories = filtered_memories[:limit]
        
        return {
            "status": "ok",
            "stream": filtered_memories
        }
    except Exception as e:
        print(f"❌ Memory Stream error: {str(e)}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
