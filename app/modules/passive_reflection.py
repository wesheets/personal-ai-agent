"""
Passive Reflection Engine

This module provides functionality for passive reflection on agent tasks,
allowing agents to re-evaluate tasks after being blocked.
"""
import logging
import json
import os
import time
import threading
from typing import Dict, Any, List, Optional, Callable

# Configure logging
logger = logging.getLogger("app.modules.passive_reflection")

# Import project_state for tracking project status
try:
    from app.modules.project_state import read_project_state, update_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    print("❌ project_state import failed")

# Import agent_retry for retry and recovery flow
try:
    from app.modules.agent_retry import check_for_unblocked_agents, get_retry_status, mark_agent_retry_attempted
    AGENT_RETRY_AVAILABLE = True
except ImportError:
    AGENT_RETRY_AVAILABLE = False
    print("❌ agent_retry import failed")

# Import memory_block_writer for logging block information
try:
    from app.modules.memory_block_writer import write_block_memory, write_unblock_memory
    MEMORY_BLOCK_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_BLOCK_WRITER_AVAILABLE = False
    print("❌ memory_block_writer import failed")

class PassiveReflectionEngine:
    """
    Engine for passive reflection on agent tasks, allowing agents to re-evaluate
    tasks after being blocked.
    """
    def __init__(self):
        self.reflection_threads = {}
        self.running = True
    
    def start_reflection(self, project_id: str, interval: int = 60) -> Dict[str, Any]:
        """
        Start passive reflection for a project.
        
        Args:
            project_id: The project identifier
            interval: Reflection interval in seconds
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            if not PROJECT_STATE_AVAILABLE or not AGENT_RETRY_AVAILABLE:
                error_msg = "Project state or agent retry not available, cannot start reflection"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id
                }
            
            # Start reflection thread if not already running
            if project_id not in self.reflection_threads or not self.reflection_threads[project_id].is_alive():
                self._start_reflection_thread(project_id, interval)
            
            logger.info(f"Started passive reflection for project {project_id} with interval {interval}s")
            print(f"🧠 Started passive reflection for project {project_id} with interval {interval}s")
            
            return {
                "status": "success",
                "message": f"Started passive reflection for project {project_id}",
                "project_id": project_id,
                "interval": interval
            }
            
        except Exception as e:
            error_msg = f"Error starting passive reflection for {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "error": str(e)
            }
    
    def stop_reflection(self, project_id: str) -> Dict[str, Any]:
        """
        Stop passive reflection for a project.
        
        Args:
            project_id: The project identifier
            
        Returns:
            Dict containing the result of the operation
        """
        try:
            if project_id not in self.reflection_threads:
                return {
                    "status": "success",
                    "message": f"No reflection thread found for project {project_id}",
                    "project_id": project_id
                }
            
            # Stop reflection thread
            self.running = False
            if self.reflection_threads[project_id].is_alive():
                self.reflection_threads[project_id].join(1)  # Wait for thread to terminate
                del self.reflection_threads[project_id]
            
            logger.info(f"Stopped passive reflection for project {project_id}")
            print(f"👋 Stopped passive reflection for project {project_id}")
            
            return {
                "status": "success",
                "message": f"Stopped passive reflection for project {project_id}",
                "project_id": project_id
            }
            
        except Exception as e:
            error_msg = f"Error stopping passive reflection for {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "error": str(e)
            }
    
    def _start_reflection_thread(self, project_id: str, interval: int = 60) -> None:
        """
        Start reflection thread for a project.
        
        Args:
            project_id: The project identifier
            interval: Reflection interval in seconds
        """
        def reflect_on_project():
            while self.running:
                try:
                    # Check for unblocked agents
                    unblocked_agents = check_for_unblocked_agents(project_id)
                    
                    if unblocked_agents:
                        logger.info(f"Found {len(unblocked_agents)} unblocked agents for project {project_id}")
                        print(f"🔓 Found {len(unblocked_agents)} unblocked agents for project {project_id}")
                        
                        # Process each unblocked agent
                        for agent_info in unblocked_agents:
                            agent_id = agent_info.get("agent_id")
                            blocked_due_to = agent_info.get("blocked_due_to")
                            unblock_condition = agent_info.get("unblock_condition")
                            
                            # Log unblock memory
                            if MEMORY_BLOCK_WRITER_AVAILABLE:
                                write_unblock_memory({
                                    "project_id": project_id,
                                    "agent": agent_id,
                                    "action": "unblocked",
                                    "content": f"{agent_id.upper()} agent unblocked - {unblock_condition} condition met",
                                    "previously_blocked_due_to": blocked_due_to,
                                    "unblock_reason": f"{unblock_condition} condition met"
                                })
                                print(f"📝 Unblock memory logged for {agent_id.upper()} agent")
                            
                            # Mark agent as retry attempted
                            mark_agent_retry_attempted(project_id, agent_id)
                            
                            # Update project state
                            if PROJECT_STATE_AVAILABLE:
                                project_state_data = {
                                    "latest_agent_action": {
                                        "agent": agent_id,
                                        "action": f"Unblocked - {unblock_condition} condition met"
                                    },
                                    "unblocked_agents": [agent_id]
                                }
                                
                                update_project_state(project_id, project_state_data)
                                print(f"✅ Project state updated for unblocked agent {agent_id}")
                    
                    # Sleep for interval
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in reflection thread for project {project_id}: {str(e)}")
                    time.sleep(interval)  # Sleep even on error to avoid tight loop
        
        # Start reflection thread
        thread = threading.Thread(target=reflect_on_project, daemon=True)
        thread.start()
        self.reflection_threads[project_id] = thread
        
        logger.info(f"Started reflection thread for project {project_id} with interval {interval}s")
        print(f"🧠 Started reflection thread for project {project_id} with interval {interval}s")

    def re_evaluate_task(self, project_id: str, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Re-evaluate a task for an agent after being unblocked.
        
        Args:
            project_id: The project identifier
            agent_id: The agent identifier
            task: The original task data
            
        Returns:
            Dict containing the result of the operation and updated task
        """
        try:
            if not PROJECT_STATE_AVAILABLE:
                error_msg = "Project state not available, cannot re-evaluate task"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "message": error_msg,
                    "project_id": project_id,
                    "agent_id": agent_id
                }
            
            # Read current project state
            project_state = read_project_state(project_id)
            
            # Check if agent was previously blocked
            retry_status = get_retry_status(project_id, agent_id)
            
            if not retry_status or retry_status.get("status") != "unblocked":
                return {
                    "status": "not_applicable",
                    "message": f"Agent {agent_id} was not previously blocked or has not been unblocked",
                    "project_id": project_id,
                    "agent_id": agent_id,
                    "task": task
                }
            
            # Update task with current project state
            updated_task = task.copy()
            updated_task["project_state"] = project_state
            updated_task["retry_info"] = {
                "previously_blocked_due_to": retry_status.get("blocked_due_to"),
                "unblock_condition": retry_status.get("unblock_condition"),
                "unblocked_at": retry_status.get("unblocked_at")
            }
            
            logger.info(f"Re-evaluated task for agent {agent_id} in project {project_id}")
            print(f"🔄 Re-evaluated task for agent {agent_id} in project {project_id}")
            
            return {
                "status": "success",
                "message": f"Re-evaluated task for agent {agent_id}",
                "project_id": project_id,
                "agent_id": agent_id,
                "task": updated_task
            }
            
        except Exception as e:
            error_msg = f"Error re-evaluating task for agent {agent_id} in project {project_id}: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                "status": "error",
                "message": error_msg,
                "project_id": project_id,
                "agent_id": agent_id,
                "error": str(e)
            }

# Create a singleton instance
reflection_engine = PassiveReflectionEngine()

def start_reflection(project_id: str, interval: int = 60) -> Dict[str, Any]:
    """
    Start passive reflection for a project.
    
    Args:
        project_id: The project identifier
        interval: Reflection interval in seconds
        
    Returns:
        Dict containing the result of the operation
    """
    return reflection_engine.start_reflection(project_id, interval)

def stop_reflection(project_id: str) -> Dict[str, Any]:
    """
    Stop passive reflection for a project.
    
    Args:
        project_id: The project identifier
        
    Returns:
        Dict containing the result of the operation
    """
    return reflection_engine.stop_reflection(project_id)

def re_evaluate_task(project_id: str, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Re-evaluate a task for an agent after being unblocked.
    
    Args:
        project_id: The project identifier
        agent_id: The agent identifier
        task: The original task data
        
    Returns:
        Dict containing the result of the operation and updated task
    """
    return reflection_engine.re_evaluate_task(project_id, agent_id, task)
