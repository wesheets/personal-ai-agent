"""
System overview diagnostic route for monitoring agent health and system status.
"""
from fastapi import APIRouter, Request
import logging
import os
import json
import datetime
import platform
from pathlib import Path
from typing import Dict, List, Any
from app.agents.memory_agent import handle_memory_task
from app.core.run import AGENT_HANDLERS

# Configure logging
logger = logging.getLogger("api")

# Create router
router = APIRouter(prefix="/system", tags=["System"])

@router.get("/overview")
async def get_system_overview():
    """
    Returns a comprehensive overview of the system health and status.
    
    This endpoint provides:
    - Active agents list
    - Last 5 memory entries
    - Current system mode
    - Boot time and uptime
    """
    try:
        # Get active agents
        active_agents = []
        for agent_id in AGENT_HANDLERS:
            active_agents.append({
                "id": agent_id,
                "handler": AGENT_HANDLERS[agent_id].__name__,
                "status": "active"
            })
        
        # Get last 5 memory entries
        memory_entries = handle_memory_task("SHOW")
        last_entries = []
        if memory_entries and memory_entries != "🧠 No recent memory.":
            entries = memory_entries.split("\n")
            # Filter out empty entries and take the last 5
            valid_entries = [entry for entry in entries if entry.strip()]
            last_entries = valid_entries[-5:] if len(valid_entries) > 5 else valid_entries
        
        # Determine current system mode
        system_mode = os.environ.get("SYSTEM_MODE", "production")
        debug_enabled = os.environ.get("DEBUG", "false").lower() == "true"
        
        # Get boot time
        boot_time = "Unknown"
        uptime = "Unknown"
        
        try:
            # Try to get system boot time
            import psutil
            boot_timestamp = psutil.boot_time()
            boot_time = datetime.datetime.fromtimestamp(boot_timestamp).isoformat()
            uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_timestamp)).total_seconds()
            
            # Format uptime
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
        except (ImportError, Exception) as e:
            logger.warning(f"Could not determine boot time: {str(e)}")
            # Fallback to process start time
            import time
            process_start = time.time() - process_start_time
            hours, remainder = divmod(process_start, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{int(hours)}h {int(minutes)}m {int(seconds)}s (process uptime)"
        
        # Get system information
        system_info = {
            "os": platform.system(),
            "version": platform.version(),
            "python": platform.python_version(),
            "hostname": platform.node()
        }
        
        # Return the overview
        return {
            "active_agents": active_agents,
            "agent_count": len(active_agents),
            "last_memory_entries": last_entries,
            "system_mode": system_mode,
            "debug_enabled": debug_enabled,
            "boot_time": boot_time,
            "uptime": uptime,
            "system_info": system_info,
            "status": "healthy"
        }
        
    except Exception as e:
        logger.error(f"Error generating system overview: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate system overview: {str(e)}"
        }

# Store process start time for uptime calculation fallback
process_start_time = datetime.datetime.now().timestamp()
