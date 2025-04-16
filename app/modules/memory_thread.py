"""
Memory Thread Module

This module provides functionality to store and retrieve memory threads.

MODIFIED: Added enhanced logging for debugging memory thread issues  
MODIFIED: Fixed thread key format to use double colons  
MODIFIED: Added support for batch memory operations via ThreadRequest  
MODIFIED: Updated to use schema models from app.schemas.memory  
"""

import json
import datetime
import logging
import traceback
from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, HTTPException, Request
from app.schemas.memory import ThreadRequest, MemoryItem, StepType

# Configure logging
logger = logging.getLogger("modules.memory_thread")

# In-memory database to store memory threads
THREAD_DB: Dict[str, List[Dict[str, Any]]] = {}

# Create router for memory thread endpoints
router = APIRouter()

def get_current_timestamp() -> str:
    return datetime.datetime.now().isoformat() + "Z"

@router.post("/api/memory/thread")
async def thread_memory(request: Union[ThreadRequest, Dict[str, Any]]) -> Dict[str, Any]:
    logger.info(f"📝 Memory Thread: Batch endpoint called")
    
    try:
        if isinstance(request, dict):
            project_id = request.get("project_id")
            chain_id = request.get("chain_id")
            agent_id = request.get("agent_id")
            memories = request.get("memories", [])
            if not project_id or not chain_id or not agent_id or not memories:
                raise HTTPException(status_code=400, detail="Missing required fields in request")
        else:
            project_id = request.project_id
            chain_id = request.chain_id
            agent_id = request.agent_id
            memories = request.memories

        thread_key = f"{project_id}::{chain_id}"
        if thread_key not in THREAD_DB:
            THREAD_DB[thread_key] = []

        memory_ids = []
        for memory in memories:
            if isinstance(memory, dict):
                agent = memory.get("agent")
                role = memory.get("role")
                content = memory.get("content")
                step_type = memory.get("step_type")
            else:
                agent = memory.agent
                role = memory.role
                content = memory.content
                step_type = memory.step_type

            memory_id = f"mem-{datetime.datetime.now().timestamp()}-{len(THREAD_DB[thread_key])}"
            memory_ids.append(memory_id)

            THREAD_DB[thread_key].append({
                "memory_id": memory_id,
                "agent": agent,
                "role": role,
                "content": content,
                "step_type": step_type,
                "timestamp": get_current_timestamp(),
                "project_id": project_id,
                "chain_id": chain_id
            })

        logger.info(f"📝 Memory Thread: Stored {len(memories)} memories under key {thread_key}")
        return { "status": "added", "thread_length": len(THREAD_DB[thread_key]), "memory_ids": memory_ids }

    except Exception as e:
        logger.error(f"Unexpected error in thread_memory: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/memory/thread")
async def add_memory_thread(memory_entry: Dict[str, Any], request: Request = None) -> Dict[str, Any]:
    logger.info(f"DEBUG: Legacy POST /memory/thread endpoint called")

    try:
        required_fields = ["project_id", "chain_id", "agent", "role", "content", "step_type"]
        missing_fields = [field for field in required_fields if field not in memory_entry]

        if missing_fields:
            raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}")

        try:
            memory_entry["step_type"] = StepType(memory_entry["step_type"])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid step_type value: {memory_entry['step_type']}")

        if "timestamp" not in memory_entry:
            memory_entry["timestamp"] = get_current_timestamp()

        thread_key = f"{memory_entry['project_id']}::{memory_entry['chain_id']}"
        if thread_key not in THREAD_DB:
            THREAD_DB[thread_key] = []

        memory_id = f"mem-{datetime.datetime.now().timestamp()}-{len(THREAD_DB[thread_key])}"
        memory_entry["memory_id"] = memory_id

        THREAD_DB[thread_key].append(memory_entry)

        return {
            "status": "added",
            "thread_length": len(THREAD_DB[thread_key]),
            "memory_id": memory_id
        }

    except Exception as e:
        logger.error(f"Unexpected error in add_memory_thread: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/thread/{project_id}/{chain_id}")
async def get_memory_thread(project_id: str, chain_id: str) -> List[Dict[str, Any]]:
    logger.info(f"📝 Memory Thread: Received read request for project_id={project_id}, chain_id={chain_id}")

    try:
        thread_key = f"{project_id}::{chain_id}"
        thread_key_alt = f"{project_id}:{chain_id}"

        if thread_key in THREAD_DB:
            return THREAD_DB[thread_key]
        elif thread_key_alt in THREAD_DB:
            return THREAD_DB[thread_key_alt]
        return []

    except Exception as e:
        logger.error(f"Unexpected error in get_memory_thread: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

def clear_all_threads() -> None:
    logger.debug(f"Clearing all threads. Current count: {len(THREAD_DB)}")
    THREAD_DB.clear()
    logger.debug(f"All threads cleared. New count: {len(THREAD_DB)}")
