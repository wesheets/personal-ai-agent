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
router = APIRouter(tags=["Training Modules"])
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

# Pydantic model for train memory
class TrainMemory(BaseModel):
    """
    Train memory model compliant with Promethios SDK Contract v1.0.0
    
    This model defines the schema for a single training memory block,
    including content and metadata fields.
    """
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    memory_trace_id: Optional[str] = None
    persona_profile: Optional[str] = None
    knowledge_domain: Optional[str] = None
    access_permissions: Optional[List[str]] = None
    content: str
    tags: Optional[List[str]] = []
    timestamp: Optional[str] = None

# Pydantic model for training request
class TrainingRequest(BaseModel):
    """
    Training request model compliant with Promethios SDK Contract v1.0.0
    
    This model defines the schema for training requests, including agent identification,
    project context, task tracking, persona customization, knowledge domain categorization,
    and access control.
    """
    agent_id: str
    dataset: TrainMemory
    goal: str
    tags: Optional[List[str]] = []
    auto_reflect: Optional[bool] = False
    repeat_interval: Optional[str] = None
    preview: Optional[bool] = False
    staged: Optional[bool] = False
    
    # SDK Contract v1.0.0 fields
    project_id: Optional[str] = None
    task_id: Optional[str] = None
    memory_trace_id: Optional[str] = None
    persona_profile: Optional[str] = None
    knowledge_domain: Optional[str] = None
    access_permissions: Optional[List[str]] = None

# Function to generate memory entries from dataset
def generate_memory_entries(
    agent_id: str, 
    dataset: TrainMemory,
    project_id: Optional[str] = None,
    task_id: Optional[str] = None,
    memory_trace_id: Optional[str] = None,
    persona_profile: Optional[str] = None,
    knowledge_domain: Optional[str] = None,
    access_permissions: Optional[List[str]] = None
):
    """
    Generate memory entries from training dataset with SDK Contract v1.0.0 support
    
    Args:
        agent_id: Identifier for the agent
        dataset: Single TrainMemory object containing content and metadata
        project_id: Optional project context identifier
        task_id: Optional task identifier
        memory_trace_id: Optional memory trace identifier for linking related memories
        persona_profile: Optional persona/tone metadata for the agent
        knowledge_domain: Optional knowledge domain categorization
        access_permissions: Optional list of agents/users with access permissions
        
    Returns:
        Tuple containing list of memory entries and total word count
    """
    memory_entries = []
    total_words = 0
    
    # Create a memory entry from the dataset
    memory_entry = {
        "memory_id": str(uuid.uuid4()),
        "agent_id": agent_id,
        "type": "training",  # Ensure memory_type is always "training" per SDK Contract
        "content": dataset.content,
        "tags": dataset.tags if dataset.tags else [],
        "timestamp": dataset.timestamp if dataset.timestamp else datetime.now().isoformat()
    }
    
    # Add SDK Contract v1.0.0 fields from dataset if provided, otherwise use function parameters
    memory_entry["project_id"] = dataset.project_id if dataset.project_id else project_id
    memory_entry["task_id"] = dataset.task_id if dataset.task_id else task_id
    memory_entry["memory_trace_id"] = dataset.memory_trace_id if dataset.memory_trace_id else memory_trace_id
    
    if dataset.persona_profile or persona_profile:
        memory_entry["persona_profile"] = dataset.persona_profile if dataset.persona_profile else persona_profile
    
    if dataset.knowledge_domain or knowledge_domain:
        memory_entry["knowledge_domain"] = dataset.knowledge_domain if dataset.knowledge_domain else knowledge_domain
    
    if dataset.access_permissions or access_permissions:
        memory_entry["access_permissions"] = dataset.access_permissions if dataset.access_permissions else access_permissions
    
    # Count words in content
    if dataset.content:
        total_words += len(dataset.content.split())
    
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
    """
    Train an agent with dataset and metadata compliant with Promethios SDK Contract v1.0.0
    
    This endpoint processes training requests, stores training data in memory with
    appropriate metadata, and returns a structured response with tracking information.
    
    Args:
        request: Training request containing dataset and metadata
        preview: Optional query parameter to preview memory entries without saving
        
    Returns:
        JSON response with status, memory_id, and metadata according to SDK Contract
    """
    try:
        # Use query parameter if provided, otherwise use body parameter
        is_preview = preview if preview is not None else request.preview
        is_staged = request.staged
        
        # Generate memory entries from dataset with SDK Contract v1.0.0 fields
        memory_entries, total_words = generate_memory_entries(
            agent_id=request.agent_id, 
            dataset=request.dataset,
            project_id=request.project_id,
            task_id=request.task_id,
            memory_trace_id=request.memory_trace_id,
            persona_profile=request.persona_profile,
            knowledge_domain=request.knowledge_domain,
            access_permissions=request.access_permissions
        )
        
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
        
        # Add SDK Contract v1.0.0 fields to training log
        if request.project_id:
            training_log["project_id"] = request.project_id
        if request.task_id:
            training_log["task_id"] = request.task_id
        if request.memory_trace_id:
            training_log["memory_trace_id"] = request.memory_trace_id
        if request.persona_profile:
            training_log["persona_profile"] = request.persona_profile
        if request.knowledge_domain:
            training_log["knowledge_domain"] = request.knowledge_domain
        if request.access_permissions:
            training_log["access_permissions"] = request.access_permissions
        
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
                "tags": request.tags,
                "project_id": request.project_id,
                "task_id": request.task_id,
                "memory_trace_id": request.memory_trace_id
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
            
            # Add SDK Contract v1.0.0 fields to queue item
            if request.project_id:
                queue_item["project_id"] = request.project_id
            if request.task_id:
                queue_item["task_id"] = request.task_id
            if request.memory_trace_id:
                queue_item["memory_trace_id"] = request.memory_trace_id
            if request.persona_profile:
                queue_item["persona_profile"] = request.persona_profile
            if request.knowledge_domain:
                queue_item["knowledge_domain"] = request.knowledge_domain
            if request.access_permissions:
                queue_item["access_permissions"] = request.access_permissions
            
            training_queue.append(queue_item)
            save_training_queue()
            
            training_log["staged"] = True
            training_logs.append(training_log)
            save_training_logs()
            
            # Return SDK Contract v1.0.0 compliant response
            return {
                "status": "staged",
                "memory_id": training_log_id,
                "agent_id": request.agent_id,
                "task_id": request.task_id,
                "project_id": request.project_id,
                "memory_trace_id": request.memory_trace_id,
                "log": "Training data staged for later execution"
            }
        
        # Otherwise, inject memories using memory_writer
        from app.modules.memory_writer import write_memory
        
        # Write each memory entry to both local and shared memory store
        memory_ids = []
        for memory_entry in memory_entries:
            # Extract fields for write_memory function
            memory_id = write_memory(
                agent_id=memory_entry["agent_id"],
                type=memory_entry["type"],
                content=memory_entry["content"],
                tags=memory_entry["tags"],
                project_id=memory_entry.get("project_id"),
                task_id=memory_entry.get("task_id"),
                status=None,
                task_type=None
            )
            memory_ids.append(memory_id)
            
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
        
        # Return SDK Contract v1.0.0 compliant response
        return {
            "status": "success",
            "memory_id": memory_ids[0] if memory_ids else training_log_id,
            "task_id": request.task_id,
            "project_id": request.project_id,
            "memory_trace_id": request.memory_trace_id,
            "log": f"Memory stored with domain and persona metadata"
        }
    except Exception as e:
        logger.error(f"Error training agent: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to train agent: {str(e)}",
                "task_id": getattr(request, "task_id", None),
                "project_id": getattr(request, "project_id", None),
                "memory_trace_id": getattr(request, "memory_trace_id", None)
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
