from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from app.modules.memory_writer import write_memory, memory_store, generate_reflection
from app.modules.memory_summarizer import summarize_memories
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import os
import sqlite3
from src.utils.debug_logger import log_test_result

class MemoryEntry(BaseModel):
    agent_id: str
    memory_type: str
    content: str
    tags: List[str] = []
    goal_id: Optional[str] = None

class ReflectionRequest(BaseModel):
    agent_id: str
    memory_type: str
    limit: int = 5

class SummarizationRequest(BaseModel):
    agent_id: str
    memory_type: Optional[str] = None
    limit: int = 10

router = APIRouter()

# ✅ TEMP SCHEMA DROP FIX
try:
    conn = sqlite3.connect("/app/db/memory.db")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS memories;")
    print("🔥 Dropped 'memories' table to force schema rebuild.")
    conn.commit()
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Failed to drop memory table: {e}")
    log_test_result("Memory", "/api/memory/init", "FAIL", f"Failed to drop memory table: {e}", "Database initialization error")


@router.post("/write")
async def memory_write(request: Request):
    try:
        body = await request.json()
        memory_entry = MemoryEntry(**body)

        memory = write_memory(
            agent_id=memory_entry.agent_id,
            type=memory_entry.memory_type,
            content=memory_entry.content,
            tags=memory_entry.tags,
            goal_id=memory_entry.goal_id
        )

        log_test_result("Memory", "/api/memory/write", "PASS", f"Memory logged for Agent {memory_entry.agent_id}", f"Type: {memory_entry.memory_type}")
        return JSONResponse(status_code=200, content={"status": "ok", "memory_id": memory["memory_id"]})
    except Exception as e:
        print(f"❌ MemoryWriter error: {str(e)}")
        log_test_result("Memory", "/api/memory/write", "FAIL", f"Error: {str(e)}", "Check memory payload format")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.get("/read")
async def read_memory(
    agent_id: str,
    memory_type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = 10,
    since: Optional[str] = None
):
    try:
        if not agent_id:
            log_test_result("Memory", "/api/memory/read", "FAIL", "Missing agent_id parameter", "Required parameter not provided")
            raise HTTPException(status_code=400, detail="agent_id is required")

        filtered_memories = [m for m in memory_store if m["agent_id"] == agent_id]

        if memory_type:
            filtered_memories = [m for m in filtered_memories if m["type"] == memory_type]

        if tag:
            filtered_memories = [m for m in filtered_memories if tag in m["tags"]]

        if since:
            try:
                since_dt = datetime.fromisoformat(since)
                filtered_memories = [m for m in filtered_memories if datetime.fromisoformat(m["timestamp"]) > since_dt]
            except ValueError:
                log_test_result("Memory", "/api/memory/read", "FAIL", "Invalid ISO 8601 format for 'since' parameter", "Date format error")
                raise HTTPException(status_code=400, detail="Invalid ISO 8601 format for 'since' parameter")

        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)

        if limit and limit > 0:
            filtered_memories = filtered_memories[:limit]

        log_test_result("Memory", "/api/memory/read", "PASS", f"Retrieved {len(filtered_memories)} memories for Agent {agent_id}",
                        f"Type: {memory_type or 'all'}, Tag: {tag or 'none'}, Limit: {limit}")
        return {"status": "ok", "memories": filtered_memories}
    except HTTPException as e:
        print(f"❌ MemoryReader error: {str(e.detail)}")
        log_test_result("Memory", "/api/memory/read", "FAIL", f"HTTP Exception: {str(e.detail)}", "Check request parameters")
        return JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})
    except Exception as e:
        print(f"❌ MemoryReader error: {str(e)}")
        log_test_result("Memory", "/api/memory/read", "FAIL", f"Exception: {str(e)}", "Unexpected error")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.post("/reflect")
async def reflect_on_memories(request: Request):
    try:
        body = await request.json()
        reflection_request = ReflectionRequest(**body)

        filtered_memories = [m for m in memory_store if m["agent_id"] == reflection_request.agent_id]
        filtered_memories = [m for m in filtered_memories if m["type"] == reflection_request.memory_type]
        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        filtered_memories = filtered_memories[:reflection_request.limit]

        reflection_text = generate_reflection(filtered_memories)

        memory = write_memory(
            agent_id=reflection_request.agent_id,
            type="reflection",
            content=reflection_text,
            tags=["reflection", f"based_on_{reflection_request.memory_type}"]
        )

        log_test_result("Memory", "/api/memory/reflect", "PASS", f"Generated reflection for Agent {reflection_request.agent_id}",
                        f"Based on {len(filtered_memories)} memories of type {reflection_request.memory_type}")
        return {
            "status": "ok",
            "reflection": reflection_text,
            "memory_id": memory["memory_id"]
        }
    except Exception as e:
        print(f"❌ Reflection Engine error: {str(e)}")
        log_test_result("Memory", "/api/memory/reflect", "FAIL", f"Error: {str(e)}", "Reflection generation failed")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.post("/summarize")
async def summarize_memory(request: Request):
    try:
        body = await request.json()
        summarize_request = SummarizationRequest(**body)

        filtered_memories = [m for m in memory_store if m["agent_id"] == summarize_request.agent_id]
        if summarize_request.memory_type:
            filtered_memories = [m for m in filtered_memories if m["type"] == summarize_request.memory_type]

        filtered_memories.sort(key=lambda m: m["timestamp"], reverse=True)
        filtered_memories = filtered_memories[:summarize_request.limit]

        summary = summarize_memories(filtered_memories)

        log_test_result("Memory", "/api/memory/summarize", "PASS", f"Summarized {len(filtered_memories)} memories for Agent {summarize_request.agent_id}",
                        f"Type: {summarize_request.memory_type or 'all'}")
        return {
            "status": "ok",
            "summary": summary,
            "memory_count": len(filtered_memories)
        }
    except Exception as e:
        print(f"❌ MemorySummarizer error: {str(e)}")
        log_test_result("Memory", "/api/memory/summarize", "FAIL", f"Error: {str(e)}", "Memory summarization failed")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})


@router.post("/admin/reset-memory-db")
async def reset_memory_db():
    try:
        os.remove("/app/db/memory.db")
        print("🧨 memory.db deleted from /app/db/")
        log_test_result("Memory", "/api/memory/admin/reset-memory-db", "PASS", "Memory DB deleted", "Restart app to rebuild schema")
        return {"status": "ok", "message": "Memory DB deleted. Restart app to rebuild schema."}
    except FileNotFoundError:
        log_test_result("Memory", "/api/memory/admin/reset-memory-db", "PASS", "DB already deleted", "No action needed")
        return {"status": "ok", "message": "DB already deleted"}
    except Exception as e:
        log_test_result("Memory", "/api/memory/admin/reset-memory-db", "FAIL", f"Error: {str(e)}", "DB reset failed")
        return {"status": "error", "message": str(e)}


@router.get("/thread")
async def memory_thread(goal_id: str):
    try:
        filtered = [m for m in memory_store if m.get("goal_id") == goal_id]
        log_test_result("Memory", "/api/memory/thread", "PASS", f"Retrieved thread with {len(filtered)} memories", f"Goal ID: {goal_id}")
        return {"status": "ok", "thread": filtered}
    except Exception as e:
        print(f"❌ MemoryThread error: {str(e)}")
        log_test_result("Memory", "/api/memory/thread", "FAIL", f"Error: {str(e)}", "Thread retrieval failed")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
