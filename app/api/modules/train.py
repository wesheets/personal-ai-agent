"""
API endpoint for the Agent Training module.

This module provides REST API endpoints for training agents with datasets,
viewing training history, and managing scheduled training.
"""

print("📁 Loaded: train.py (Agent Training route file)")

from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import logging
import traceback
import os
import time
import json
import uuid
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger("api.modules.train")

# Create router
router = APIRouter(prefix="/train", tags=["Training Modules"])
print("🧠 Route defined: /api/modules/train -> train_agent_endpoint")
print("🧠 Route defined: /api/modules/train/history -> get_training_history_endpoint")

# Path for training logs and queue
TRAINING_LOGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "training_logs.json")
TRAINING_QUEUE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "training_queue.json")

# Initialize training logs and queue
training_logs = []
training_queue = []

# Load existing training logs if file exists
def load_training_logs():
    global training_logs
    try:
        if os.path.exists(TRAINING_LOGS_FILE):
            with open(TRAINING_LOGS_FILE, 'r') as f:
                training_logs = json.load(f)
            print(f"📚 Loaded {len(training_logs)} training logs")
    except Exception as e:
        print(f"⚠️ Error loading training logs: {str(e)}")
        training_logs = []

# Save training logs to file
def save_training_logs():
    try:
        with open(TRAINING_LOGS_FILE, 'w') as f:
            json.dump(training_logs, f, indent=2)
        print(f"💾 Saved {len(training_logs)} training logs")
    except Exception as e:
        print(f"⚠️ Error saving training logs: {str(e)}")

# Load existing training queue if file exists
def load_training_queue():
    global training_queue
    try:
        if os.path.exists(TRAINING_QUEUE_FILE):
            with open(TRAINING_QUEUE_FILE, 'r') as f:
                training_queue = json.load(f)
            print(f"📚 Loaded {len(training_queue)} training queue items")
    except Exception as e:
        print(f"⚠️ Error loading training queue: {str(e)}")
        training_queue = []

# Save training queue to file
def save_training_queue():
    try:
        with open(TRAINING_QUEUE_FILE, 'w') as f:
            json.dump(training_queue, f, indent=2)
        print(f"💾 Saved {len(training_queue)} training queue items")
    except Exception as e:
        print(f"⚠️ Error saving training queue: {str(e)}")

# Load data on module import
load_training_logs()
load_training_queue()

# Pydantic model for training request
class TrainingRequest(BaseModel):
    agent_id: str
    dataset: List[Dict[str, Any]]
    goal: str
    tags: Optional[List[str]] = []
    auto_reflect: Optional[bool] = False
    repeat_interval: Optional[str] = None
    preview: Optional[bool] = False
    staged: Optional[bool] = False

# Function to generate memory entries from dataset
def generate_memory_entries(agent_id: str, dataset: List[Dict[str, Any]]):
    memory_entries = []
    total_words = 0
    
    for item in dataset:
        # Create a memory entry for each item in the dataset
        memory_entry = {
            "memory_id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "type": item.get("type", "training"),
            "content": item.get("content", ""),
            "tags": item.get("tags", []),
            "timestamp": item.get("timestamp", datetime.now().isoformat())
        }
        
        # Count words in content
        if "content" in item:
            total_words += len(item["content"].split())
        
        memory_entries.append(memory_entry)
    
    return memory_entries, total_words

# Function to trigger reflection after training
async def trigger_reflection(agent_id: str, memory_type: str = "training", limit: int = 5):
    from app.modules.memory_writer import generate_reflection
    
    try:
        # Import memory module to access memory_store
        from app.modules.memory_writer import memory_store, write_memory
        
        # Check if memory_store is a list or a dictionary
        if isinstance(memory_store, list):
            # If it's a list, filter directly
            filtered_memories = [
                memory for memory in memory_store
                if memory["agent_id"] == agent_id and memory["type"] == memory_type
            ]
        else:
            # If it's a dictionary, use values() method
            filtered_memories = [
                memory for memory in memory_store.values()
                if memory["agent_id"] == agent_id and memory["type"] == memory_type
            ]
        
        # Sort by timestamp (newest first) and limit
        filtered_memories.sort(key=lambda x: x["timestamp"], reverse=True)
        filtered_memories = filtered_memories[:limit]
        
        if not filtered_memories:
            return "No memories found to reflect on."
        
        # Generate reflection
        reflection = generate_reflection(filtered_memories)
        
        # Write reflection to memory
        reflection_memory = write_memory(
            agent_id=agent_id,
            type="reflection",
            content=reflection,
            tags=["auto-reflection", "training"]
        )
        
        return reflection
    except Exception as e:
        logger.error(f"Error triggering reflection: {str(e)}")
        logger.error(traceback.format_exc())
        return f"Error triggering reflection: {str(e)}"

@router.post("")
async def train_agent(
    request: TrainingRequest,
    preview: Optional[bool] = Query(None)
):
    try:
        # Use query parameter if provided, otherwise use body parameter
        is_preview = preview if preview is not None else request.preview
        is_staged = request.staged
        
        # Generate memory entries from dataset
        memory_entries, total_words = generate_memory_entries(request.agent_id, request.dataset)
        
        # Create training log entry
        training_log_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        training_log = {
            "training_log_id": training_log_id,
            "agent_id": request.agent_id,
            "goal": request.goal,
            "tags": request.tags,
            "memories_written": len(memory_entries),
            "timestamp": timestamp,
            "total_words": total_words
        }
        
        # Add scheduled training fields if provided
        if request.repeat_interval:
            training_log["repeat_interval"] = request.repeat_interval
            training_log["last_run"] = timestamp
            
            # Calculate next run based on interval
            next_run = datetime.now()
            if request.repeat_interval == "hourly":
                next_run += timedelta(hours=1)
            elif request.repeat_interval == "daily":
                next_run += timedelta(days=1)
            elif request.repeat_interval == "weekly":
                next_run += timedelta(weeks=1)
            
            training_log["next_run"] = next_run.isoformat()
        
        # If preview mode, return memory entries without saving
        if is_preview:
            return {
                "status": "preview",
                "training_log_id": training_log_id,
                "agent_id": request.agent_id,
                "memory_entries": memory_entries,
                "estimated_chunks": len(memory_entries),
                "total_words": total_words,
                "tags": request.tags
            }
        
        # If staged mode, save to training queue
        if is_staged:
            queue_item = {
                "training_log_id": training_log_id,
                "agent_id": request.agent_id,
                "goal": request.goal,
                "tags": request.tags,
                "dataset": request.dataset,
                "timestamp": timestamp,
                "memory_preview": memory_entries[:5]  # Include first 5 memories as preview
            }
            
            training_queue.append(queue_item)
            save_training_queue()
            
            training_log["staged"] = True
            training_logs.append(training_log)
            save_training_logs()
            
            return {
                "status": "staged",
                "training_log_id": training_log_id,
                "agent_id": request.agent_id,
                "queued_memories": len(memory_entries),
                "message": "Training data staged for later execution"
            }
        
        # Otherwise, inject memories using memory_writer
        from app.modules.memory_writer import write_memory
        
        # Write each memory entry to both local and shared memory store
        for memory_entry in memory_entries:
            write_memory(
                agent_id=memory_entry["agent_id"],
                type=memory_entry["type"],
                content=memory_entry["content"],
                tags=memory_entry["tags"]
            )
            
        print(f"🧠 Training agent {request.agent_id} with {len(memory_entries)} memories written to memory stores")
        
        # Add to training logs
        training_logs.append(training_log)
        save_training_logs()
        
        # If auto_reflect is true, trigger reflection
        reflection_result = None
        if request.auto_reflect:
            reflection_result = await trigger_reflection(request.agent_id)
            training_log["summary"] = reflection_result
            save_training_logs()
        
        return {
            "status": "ok",
            "training_log_id": training_log_id,
            "agent_id": request.agent_id,
            "memories_written": len(memory_entries),
            "reflection": reflection_result
        }
    except Exception as e:
        logger.error(f"Error training agent: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to train agent: {str(e)}"
            }
        )

@router.get("/history")
async def get_training_history(limit: int = 10):
    try:
        # Sort logs by timestamp (newest first) and limit
        sorted_logs = sorted(training_logs, key=lambda x: x["timestamp"], reverse=True)
        limited_logs = sorted_logs[:limit]
        
        return {
            "status": "ok",
            "history": limited_logs
        }
    except Exception as e:
        logger.error(f"Error getting training history: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get training history: {str(e)}"
            }
        )

@router.post("/execute_staged")
async def execute_staged_training(training_log_id: str = None):
    try:
        # If training_log_id is provided, execute only that item
        # Otherwise, execute all items in the queue
        items_to_execute = []
        
        if training_log_id:
            items_to_execute = [item for item in training_queue if item["training_log_id"] == training_log_id]
            if not items_to_execute:
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": "error",
                        "message": f"No staged training found with ID: {training_log_id}"
                    }
                )
        else:
            items_to_execute = training_queue.copy()
        
        results = []
        for item in items_to_execute:
            # In a real implementation, this would call the memory_writer module
            # For now, we'll simulate this by just logging
            print(f"🧠 Executing staged training for agent {item['agent_id']} with {len(item['dataset'])} memories")
            
            # Update training log
            for log in training_logs:
                if log["training_log_id"] == item["training_log_id"]:
                    log["staged"] = False
                    log["executed_at"] = datetime.now().isoformat()
                    break
            
            # Remove from queue
            training_queue[:] = [q for q in training_queue if q["training_log_id"] != item["training_log_id"]]
            
            results.append({
                "training_log_id": item["training_log_id"],
                "agent_id": item["agent_id"],
                "status": "executed"
            })
        
        # Save updated logs and queue
        save_training_logs()
        save_training_queue()
        
        return {
            "status": "ok",
            "executed": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error executing staged training: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to execute staged training: {str(e)}"
            }
        )
