"""
Core Routes Module

This module defines the core infrastructure routes for the Promethios API.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional

router = APIRouter(tags=["core"])

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "ok"}

@router.get("/system/status")
async def system_status():
    """
    Get system status including environment and module load state.
    """
    return {
        "status": "operational",
        "environment": "production",
        "modules": {
            "core": "loaded",
            "memory": "loaded",
            "agents": "loaded",
            "loop": "loaded",
            "persona": "loaded"
        },
        "version": "1.0.0"
    }

@router.post("/memory/read")
async def read_memory(key: str):
    """
    Retrieve memory by key.
    """
    # This would normally interact with a memory store
    # For now, return a mock response
    return {
        "key": key,
        "value": f"Value for {key}",
        "timestamp": "2025-04-21T12:28:00Z"
    }

@router.post("/memory/write")
async def write_memory(data: Dict[str, Any]):
    """
    Direct memory injection.
    """
    key = data.get("key")
    value = data.get("value")
    
    if not key or not value:
        raise HTTPException(status_code=400, detail="Both key and value are required")
    
    # This would normally write to a memory store
    # For now, return a success response
    return {
        "status": "success",
        "key": key,
        "memory": {
            "key": key,
            "value": value,
            "timestamp": "2025-04-21T12:28:00Z"
        }
    }

@router.post("/memory/delete")
async def delete_memory(data: Dict[str, str]):
    """
    Clear keys from memory.
    """
    key = data.get("key")
    
    if not key:
        raise HTTPException(status_code=400, detail="Key is required")
    
    # This would normally delete from a memory store
    # For now, return a success response
    return {
        "status": "success",
        "key": key,
        "message": f"Key {key} deleted from memory"
    }
