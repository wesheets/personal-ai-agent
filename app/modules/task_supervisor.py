"""
Task Supervisor Module - Real-Time Agent Monitor

This module provides centralized monitoring for all agent activities,
preventing runaway execution, detecting agents exceeding system caps,
logging structured audit events, and enforcing emergency halts.

This is the backbone of the Promethios Security Framework v3.
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from fastapi import APIRouter, Request, HTTPException

# Configure logging
logger = logging.getLogger("app.modules.task_supervisor")

# Create router
router = APIRouter()
print("🧠 Route defined: /api/modules/task/status -> get_task_status")

# Path for system caps configuration
SYSTEM_CAPS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "system_caps.json")

# Path for task supervision log
TASK_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "task_log.jsonl")

# Ensure logs directory exists
os.makedirs(os.path.dirname(TASK_LOG_FILE), exist_ok=True)

# Global lockdown mode flag (will be imported from lockdown_mode.py in the future)
# For now, we'll set it to False by default
lockdown_mode = False

# Ensure system caps file exists with default values
def ensure_system_caps_file_exists():
    """
    Ensure the system caps file exists with default values.
    Creates the file if it doesn't exist.
    """
    try:
        if not os.path.exists(SYSTEM_CAPS_FILE):
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(SYSTEM_CAPS_FILE), exist_ok=True)
            
            # Default system caps
            default_caps = {
                "max_loops_per_task": 3,
                "max_delegation_depth": 2
            }
            
            # Write to file
            with open(SYSTEM_CAPS_FILE, 'w') as f:
                json.dump(default_caps, f, indent=2)
            
            logger.info(f"✅ Created system caps file at {SYSTEM_CAPS_FILE} with default values")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Error creating system caps file: {str(e)}")
        return False

# Create system caps file on module initialization
ensure_system_caps_file_exists()

# Load system caps configuration
def load_system_caps() -> Dict[str, Any]:
    """
    Load the system caps configuration from the JSON file.
    
    Returns:
        Dict[str, Any]: The system caps configuration
    """
    try:
        if os.path.exists(SYSTEM_CAPS_FILE):
            with open(SYSTEM_CAPS_FILE, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"⚠️ System caps file not found at {SYSTEM_CAPS_FILE}, using default caps")
            return {
                "max_loops_per_task": 3,
                "max_delegation_depth": 2
            }
    except Exception as e:
        logger.error(f"⚠️ Error loading system caps: {str(e)}")
        return {
            "max_loops_per_task": 3,
            "max_delegation_depth": 2
        }

# Load system caps
system_caps = load_system_caps()
logger.info(f"🔒 Task Supervisor loaded system caps: max_loops_per_task={system_caps['max_loops_per_task']}, max_delegation_depth={system_caps['max_delegation_depth']}")

# Add endpoint to get task supervision status
@router.get("/status")
async def get_task_status():
    """
    Get the current status of the task supervision system.
    
    Returns:
        Dict[str, Any]: The current supervision status
    """
    return get_supervision_status()

@router.post("/update_caps")
async def update_system_caps(request: Request):
    """
    Update the system caps configuration.
    
    Request body:
    - max_loops_per_task: Maximum number of loops allowed per task
    - max_delegation_depth: Maximum delegation depth allowed
    
    Returns:
        Dict[str, Any]: The updated system caps configuration
    """
    try:
        # Parse request body
        body = await request.json()
        
        # Validate required fields
        if "max_loops_per_task" not in body or "max_delegation_depth" not in body:
            raise HTTPException(status_code=400, content={
                "status": "error",
                "message": "Missing required fields: max_loops_per_task, max_delegation_depth"
            })
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(SYSTEM_CAPS_FILE), exist_ok=True)
        
        # Update system caps
        new_caps = {
            "max_loops_per_task": body["max_loops_per_task"],
            "max_delegation_depth": body["max_delegation_depth"]
        }
        
        # Write to file
        with open(SYSTEM_CAPS_FILE, 'w') as f:
            json.dump(new_caps, f, indent=2)
        
        # Reload system caps
        global system_caps
        system_caps = load_system_caps()
        
        logger.info(f"✅ System caps updated: max_loops_per_task={system_caps['max_loops_per_task']}, max_delegation_depth={system_caps['max_delegation_depth']}")
        
        return {
            "status": "success",
            "message": "System caps updated successfully",
            "system_caps": system_caps
        }
    except Exception as e:
        logger.error(f"❌ Error updating system caps: {str(e)}")
        raise HTTPException(status_code=500, content={
            "status": "error",
            "message": f"Error updating system caps: {str(e)}"
        })

def monitor_loop(task_id: str, loop_count: int) -> Dict[str, Any]:
    """
    Monitor loop count for a task and halt if it exceeds the maximum.
    
    Args:
        task_id (str): The ID of the task to monitor
        loop_count (int): The current loop count
        
    Returns:
        Dict[str, Any]: Monitoring result with status and reason
    """
    # Check global lockdown mode first
    if lockdown_mode:
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "lockdown_enforced",
            "task_id": task_id,
            "loop_count": loop_count,
            "risk_level": "critical",
            "reason": "Global lockdown mode active"
        }
        log_supervision_event(event)
        return {
            "status": "halted",
            "reason": "lockdown_mode_active",
            "event": event
        }
    
    # Check if loop count exceeds maximum
    if loop_count > system_caps["max_loops_per_task"]:
        # Create event
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "loop_exceeded",
            "task_id": task_id,
            "loop_count": loop_count,
            "max_loops": system_caps["max_loops_per_task"],
            "risk_level": "high",
            "reason": f"Loop count {loop_count} exceeds maximum {system_caps['max_loops_per_task']}"
        }
        
        # Log event
        log_supervision_event(event)
        
        # Halt task
        halt_task(task_id, "loop_exceeded")
        
        return {
            "status": "halted",
            "reason": "loop_exceeded",
            "event": event
        }
    
    # If within limits, log normal event
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "loop_monitored",
        "task_id": task_id,
        "loop_count": loop_count,
        "max_loops": system_caps["max_loops_per_task"],
        "risk_level": "low" if loop_count < system_caps["max_loops_per_task"] - 1 else "medium",
        "reason": f"Loop count {loop_count} within limits (max: {system_caps['max_loops_per_task']})"
    }
    
    log_supervision_event(event)
    
    return {
        "status": "ok",
        "reason": "within_limits",
        "event": event
    }

def monitor_delegation(agent_id: str, delegation_depth: int) -> Dict[str, Any]:
    """
    Monitor delegation depth for an agent and halt if it exceeds the maximum.
    
    Args:
        agent_id (str): The ID of the agent to monitor
        delegation_depth (int): The current delegation depth
        
    Returns:
        Dict[str, Any]: Monitoring result with status and reason
    """
    # Check global lockdown mode first
    if lockdown_mode:
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "lockdown_enforced",
            "agent_id": agent_id,
            "delegation_depth": delegation_depth,
            "risk_level": "critical",
            "reason": "Global lockdown mode active"
        }
        log_supervision_event(event)
        return {
            "status": "halted",
            "reason": "lockdown_mode_active",
            "event": event
        }
    
    # Check if delegation depth exceeds maximum
    if delegation_depth > system_caps["max_delegation_depth"]:
        # Create event
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "delegation_depth_exceeded",
            "agent_id": agent_id,
            "delegation_depth": delegation_depth,
            "max_depth": system_caps["max_delegation_depth"],
            "risk_level": "high",
            "reason": f"Delegation depth {delegation_depth} exceeds maximum {system_caps['max_delegation_depth']}"
        }
        
        # Log event
        log_supervision_event(event)
        
        # Halt task
        halt_task(agent_id, "delegation_depth_exceeded")
        
        return {
            "status": "halted",
            "reason": "delegation_depth_exceeded",
            "event": event
        }
    
    # If within limits, log normal event
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "delegation_monitored",
        "agent_id": agent_id,
        "delegation_depth": delegation_depth,
        "max_depth": system_caps["max_delegation_depth"],
        "risk_level": "low" if delegation_depth < system_caps["max_delegation_depth"] - 1 else "medium",
        "reason": f"Delegation depth {delegation_depth} within limits (max: {system_caps['max_delegation_depth']})"
    }
    
    log_supervision_event(event)
    
    return {
        "status": "ok",
        "reason": "within_limits",
        "event": event
    }

def monitor_reflection(agent_id: str, reflection_count: int) -> Dict[str, Any]:
    """
    Monitor reflection recursion for an agent and warn if it shows signs of recursion.
    
    Args:
        agent_id (str): The ID of the agent to monitor
        reflection_count (int): The current reflection count
        
    Returns:
        Dict[str, Any]: Monitoring result with status and reason
    """
    # Check global lockdown mode first
    if lockdown_mode:
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "lockdown_enforced",
            "agent_id": agent_id,
            "reflection_count": reflection_count,
            "risk_level": "critical",
            "reason": "Global lockdown mode active"
        }
        log_supervision_event(event)
        return {
            "status": "halted",
            "reason": "lockdown_mode_active",
            "event": event
        }
    
    # Check if reflection count is high (using same limit as loops for now)
    if reflection_count > system_caps["max_loops_per_task"]:
        # Create event
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "reflection_recursion",
            "agent_id": agent_id,
            "reflection_count": reflection_count,
            "max_reflections": system_caps["max_loops_per_task"],
            "risk_level": "high",
            "reason": f"Reflection count {reflection_count} indicates possible recursion"
        }
        
        # Log event
        log_supervision_event(event)
        
        # Halt task
        halt_task(agent_id, "reflection_recursion")
        
        return {
            "status": "warned",
            "reason": "reflection_recursion",
            "event": event
        }
    
    # If within limits, log normal event
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "reflection_monitored",
        "agent_id": agent_id,
        "reflection_count": reflection_count,
        "max_reflections": system_caps["max_loops_per_task"],
        "risk_level": "low" if reflection_count < system_caps["max_loops_per_task"] - 1 else "medium",
        "reason": f"Reflection count {reflection_count} within normal range"
    }
    
    log_supervision_event(event)
    
    return {
        "status": "ok",
        "reason": "within_limits",
        "event": event
    }

def halt_task(task_id_or_agent: str, reason: str) -> Dict[str, Any]:
    """
    Halt a task or agent due to a supervision violation.
    
    Args:
        task_id_or_agent (str): The ID of the task or agent to halt
        reason (str): The reason for halting the task
        
    Returns:
        Dict[str, Any]: Result of the halt operation
    """
    # Create halt event
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "task_halted",
        "task_id_or_agent": task_id_or_agent,
        "reason": reason,
        "risk_level": "high",
        "halt_id": str(uuid.uuid4())
    }
    
    # Log the halt event
    log_supervision_event(event)
    
        from app.api.modules.memory import write_memory
        
        memory = write_memory(
            agent_id="system",  # System is the agent recording this
            type="system_alert",
            content=f"Task or agent {task_id_or_agent} halted: {reason}",
            tags=["error", reason, "system_halt", "security"],
            status="error",
            task_id=task_id_or_agent if "task" in reason else None,
            target_agent_id=task_id_or_agent if "agent" in task_id_or_agent else None
        )
        
        event["memory_id"] = memory.get("memory_id")
    except Exception as e:
        logger.error(f"Failed to write halt event to memory: {str(e)}")
    
    logger.warning(f"🛑 TASK HALTED: {task_id_or_agent} - Reason: {reason}")
    
    return {
        "status": "halted",
        "task_id_or_agent": task_id_or_agent,
        "reason": reason,
        "timestamp": event["timestamp"],
        "halt_id": event["halt_id"]
    }

def log_supervision_event(event: Dict[str, Any]) -> None:
    """
    Log a supervision event to the task log file and console.
    
    Args:
        event (Dict[str, Any]): The event to log
    """
    # Ensure event has a timestamp
    if "timestamp" not in event:
        event["timestamp"] = datetime.utcnow().isoformat()
    
    # Add event ID if not present
    if "event_id" not in event:
        event["event_id"] = str(uuid.uuid4())
    
    # Log to console
    risk_emoji = "🟢"  # Low risk
    if event.get("risk_level") == "medium":
        risk_emoji = "🟡"  # Medium risk
    elif event.get("risk_level") == "high":
        risk_emoji = "🔴"  # High risk
    elif event.get("risk_level") == "critical":
        risk_emoji = "⚠️"  # Critical risk
    
    logger.info(f"{risk_emoji} {event.get('event_type', 'EVENT')}: {event.get('reason', 'No reason provided')}")
    
    # Log to file
    try:
        with open(TASK_LOG_FILE, 'a') as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to task log file: {str(e)}")
    
        from app.api.modules.memory import write_memory
            
            memory = write_memory(
                agent_id="system",  # System is the agent recording this
                type="system_alert",
                content=f"{event.get('event_type', 'Event')}: {event.get('reason', 'No reason provided')}",
                tags=["supervision", event.get("event_type", "event"), event.get("risk_level", "unknown")],
                status="active" if event.get("risk_level") != "critical" else "error"
            )
        except Exception as e:
            logger.error(f"Failed to write supervision event to memory: {str(e)}")

def get_supervision_status() -> Dict[str, Any]:
    """
    Get the current status of the task supervision system.
    
    Returns:
        Dict[str, Any]: The current supervision status
    """
    # Count events in log file
    event_counts = {
        "total": 0,
        "loop_exceeded": 0,
        "delegation_depth_exceeded": 0,
        "reflection_recursion": 0,
        "task_halted": 0,
        "lockdown_enforced": 0
    }
    
    try:
        if os.path.exists(TASK_LOG_FILE):
            with open(TASK_LOG_FILE, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        event_counts["total"] += 1
                        
                        event_type = event.get("event_type")
                        if event_type in event_counts:
                            event_counts[event_type] += 1
                    except:
                        pass
    except Exception as e:
        logger.error(f"Failed to read task log file: {str(e)}")
    
    # Get system caps
    caps = load_system_caps()
    
    return {
        "status": "active",
        "lockdown_mode": lockdown_mode,
        "system_caps": caps,
        "event_counts": event_counts,
        "log_file": TASK_LOG_FILE,
        "timestamp": datetime.utcnow().isoformat()
    }

# Initialize the module
logger.info("🔍 Task Supervisor initialized")
