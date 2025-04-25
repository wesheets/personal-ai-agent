"""
Dashboard Routes Module

This module defines the API routes for the loop summary dashboard,
which visualizes SAGE belief maps and loop summaries.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import json
import importlib.util
import sys
import os

# Configure logging
logger = logging.getLogger("app.routes.dashboard_routes")

# Import memory functions with flexible import paths
memory_available = False

# Try multiple import paths for orchestrator_memory
import_paths = [
    "app.modules.orchestrator_memory",
    "modules.orchestrator_memory",
    ".orchestrator_memory"
]

for import_path in import_paths:
    try:
        module = importlib.import_module(import_path)
        if hasattr(module, 'read_memory') and hasattr(module, 'list_memories'):
            read_memory = module.read_memory
            list_memories = module.list_memories
            memory_available = True
            logger.info(f"✅ Successfully imported memory functions from {import_path}")
            break
    except ImportError:
        logger.warning(f"⚠️ Could not import memory functions from {import_path}")
        continue

# If no import succeeded, check if we can load the module from file
if not memory_available:
    # List of possible file paths to check
    file_paths = [
        os.path.join("app", "modules", "orchestrator_memory.py"),
        os.path.join("/app", "modules", "orchestrator_memory.py"),
        os.path.join("/home", "ubuntu", "personal-ai-agent", "app", "modules", "orchestrator_memory.py")
    ]
    
    for file_path in file_paths:
        if os.path.exists(file_path):
            try:
                spec = importlib.util.spec_from_file_location("orchestrator_memory", file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules["orchestrator_memory"] = module
                spec.loader.exec_module(module)
                
                if hasattr(module, 'read_memory') and hasattr(module, 'list_memories'):
                    read_memory = module.read_memory
                    list_memories = module.list_memories
                    memory_available = True
                    logger.info(f"✅ Successfully loaded memory functions from file: {file_path}")
                    break
            except Exception as e:
                logger.warning(f"⚠️ Error loading memory functions from file {file_path}: {str(e)}")
                continue

# If still not available, try to use memory_writer directly
if not memory_available:
    try:
        from app.modules.memory_writer import read_memory, list_memories
        memory_available = True
        logger.info("✅ Using memory_writer functions directly")
    except ImportError:
        logger.warning("⚠️ Could not import memory_writer")

# If still not available, create mock implementation
if not memory_available:
    logger.warning("⚠️ Memory module not available, dashboard will use mock data")
    
    # Mock implementation for testing
    async def read_memory(agent_id, memory_type, tag, project_id=None):
        logger.info(f"Mock memory read: {agent_id}, {memory_type}, {tag}")
        return {"status": "success", "value": "Mock memory value"}
    
    async def list_memories(agent_id, memory_type, tag_prefix=None, project_id=None):
        logger.info(f"Mock list memories: {agent_id}, {memory_type}, {tag_prefix}")
        return {"status": "success", "memories": []}

# Create router
router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)

@router.get("/sage/beliefs")
async def get_sage_beliefs(loop_id: Optional[str] = None):
    """
    Get SAGE belief maps for visualization.
    
    If loop_id is provided, returns beliefs for that specific loop.
    Otherwise, returns beliefs for all loops.
    
    Args:
        loop_id: Optional loop identifier
        
    Returns:
        Dict containing belief data for visualization
    """
    if not memory_available:
        raise HTTPException(
            status_code=503,
            detail="Memory module is not available"
        )
    
    try:
        if loop_id:
            # Get beliefs for specific loop
            memory_tag = f"sage_summary_{loop_id}"
            memory_result = await read_memory(
                agent_id="sage",
                memory_type="loop",
                tag=memory_tag
            )
            
            if memory_result.get("status") != "success":
                raise HTTPException(
                    status_code=404,
                    detail=f"No belief data found for loop {loop_id}"
                )
            
            try:
                belief_data = json.loads(memory_result.get("value", "{}"))
            except json.JSONDecodeError:
                belief_data = {"error": "Invalid JSON data in memory"}
            
            return {
                "loop_id": loop_id,
                "belief_data": belief_data
            }
        else:
            # Get beliefs for all loops
            memory_results = await list_memories(
                agent_id="sage",
                memory_type="loop",
                tag_prefix="sage_summary_"
            )
            
            if memory_results.get("status") != "success":
                raise HTTPException(
                    status_code=500,
                    detail="Failed to list memory entries"
                )
            
            memories = memory_results.get("memories", [])
            
            # Process each memory entry
            belief_data_list = []
            for memory in memories:
                tag = memory.get("tag", "")
                if not tag.startswith("sage_summary_"):
                    continue
                
                # Extract loop_id from tag
                loop_id = tag.replace("sage_summary_", "")
                
                # Get memory value
                memory_result = await read_memory(
                    agent_id="sage",
                    memory_type="loop",
                    tag=tag
                )
                
                if memory_result.get("status") != "success":
                    continue
                
                try:
                    belief_data = json.loads(memory_result.get("value", "{}"))
                except json.JSONDecodeError:
                    continue
                
                belief_data_list.append({
                    "loop_id": loop_id,
                    "belief_data": belief_data
                })
            
            return {
                "belief_data_list": belief_data_list
            }
    
    except Exception as e:
        logger.error(f"Error retrieving SAGE beliefs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving SAGE beliefs: {str(e)}"
        )

@router.get("/loops")
async def get_loop_summaries():
    """
    Get summaries for all loops.
    
    Returns:
        Dict containing loop summaries for dashboard display
    """
    if not memory_available:
        raise HTTPException(
            status_code=503,
            detail="Memory module is not available"
        )
    
    try:
        # Get all loop summaries
        memory_results = await list_memories(
            agent_id="orchestrator",
            memory_type="loop",
            tag_prefix="loop_summary_"
        )
        
        if memory_results.get("status") != "success":
            raise HTTPException(
                status_code=500,
                detail="Failed to list memory entries"
            )
        
        memories = memory_results.get("memories", [])
        
        # Process each memory entry
        loop_summaries = []
        for memory in memories:
            tag = memory.get("tag", "")
            if not tag.startswith("loop_summary_"):
                continue
            
            # Extract loop_id from tag
            loop_id = tag.replace("loop_summary_", "")
            
            # Get memory value
            memory_result = await read_memory(
                agent_id="orchestrator",
                memory_type="loop",
                tag=tag
            )
            
            if memory_result.get("status") != "success":
                continue
            
            summary_text = memory_result.get("value", "")
            
            loop_summaries.append({
                "loop_id": loop_id,
                "summary": summary_text
            })
        
        return {
            "loop_summaries": loop_summaries
        }
    
    except Exception as e:
        logger.error(f"Error retrieving loop summaries: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving loop summaries: {str(e)}"
        )

@router.get("/")
async def get_dashboard_index():
    """
    Get dashboard index information.
    
    Returns:
        Dict containing dashboard metadata
    """
    return {
        "name": "Loop Summary Dashboard",
        "description": "Visualizes SAGE belief maps and loop summaries",
        "version": "1.0.0",
        "memory_available": memory_available,
        "endpoints": [
            {
                "path": "/dashboard/sage/beliefs",
                "description": "Get SAGE belief maps for visualization"
            },
            {
                "path": "/dashboard/loops",
                "description": "Get summaries for all loops"
            }
        ]
    }
