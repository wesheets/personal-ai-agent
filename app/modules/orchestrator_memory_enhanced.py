"""
Orchestrator Memory Module
This module provides memory operations specifically for the orchestrator component,
allowing it to log loop events, store beliefs, and maintain a history of system interactions.

Enhanced with retry handler and error classification for improved resilience.
"""
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Import memory utilities
from app.memory.project_memory import PROJECT_MEMORY
from app.modules.memory_writer import write_memory, read_memory

# Import retry handler and error classifier
try:
    from app.utils.retry_handler import async_retry_decorator, retry_async_with_backoff
    from app.utils.error_classification import classify_error, log_error_to_memory
    hardening_available = True
    logging.info("✅ Hardening utilities loaded successfully in orchestrator_memory")
except ImportError as e:
    hardening_available = False
    logging.warning(f"⚠️ Hardening utilities not available in orchestrator_memory, falling back to basic error handling: {str(e)}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Apply retry decorator if hardening is available
if hardening_available:
    @async_retry_decorator(retries=3, backoff=1.5)
    async def log_loop_event(
        loop_id: str,
        project_id: str,
        agent: str,
        task: str,
        result_tag: Optional[str] = None,
        status: str = "completed",
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a loop event to orchestrator memory with retry capability.
        
        Args:
            loop_id: Unique identifier for the loop
            project_id: Project identifier
            agent: Agent that performed the action
            task: Description of the task
            result_tag: Optional memory tag where result is stored
            status: Status of the event (e.g., "completed", "failed", "in_progress")
            additional_data: Any additional data to include in the log
            
        Returns:
            Dict containing the status of the memory write operation
        """
        try:
            # Create the log entry
            log_data = {
                "loop_id": loop_id,
                "project_id": project_id,
                "agent": agent,
                "task": task,
                "result_tag": result_tag,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "additional_data": additional_data or {}
            }
            
            # Get the existing log or create a new one
            memory_key = f"orchestrator_loop_log_{project_id}"
            existing_log = await read_memory(project_id, memory_key)
            
            if existing_log and "entries" in existing_log:
                # Append to existing log
                existing_log["entries"].append(log_data)
                existing_log["last_updated"] = datetime.utcnow().isoformat()
                result = await write_memory(project_id, memory_key, existing_log)
            else:
                # Create new log
                new_log = {
                    "entries": [log_data],
                    "last_updated": datetime.utcnow().isoformat()
                }
                result = await write_memory(project_id, memory_key, new_log)
            
            logger.info(f"✅ Logged loop event: {agent} - {task} ({status})")
            return result
        except Exception as e:
            error_category = classify_error(e)
            logger.error(f"❌ {error_category} logging loop event: {str(e)}")
            
            # Log error to memory
            try:
                await log_error_to_memory(
                    memory_writer=write_memory,
                    project_id=project_id,
                    agent_id="orchestrator",
                    e=e,
                    operation="log_loop_event"
                )
            except Exception as log_error:
                logger.error(f"❌ Failed to log error to memory: {str(log_error)}")
            
            # Re-raise the exception to trigger retry
            raise e
else:
    # Original implementation without retry
    async def log_loop_event(
        loop_id: str,
        project_id: str,
        agent: str,
        task: str,
        result_tag: Optional[str] = None,
        status: str = "completed",
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a loop event to orchestrator memory.
        
        Args:
            loop_id: Unique identifier for the loop
            project_id: Project identifier
            agent: Agent that performed the action
            task: Description of the task
            result_tag: Optional memory tag where result is stored
            status: Status of the event (e.g., "completed", "failed", "in_progress")
            additional_data: Any additional data to include in the log
            
        Returns:
            Dict containing the status of the memory write operation
        """
        try:
            # Create the log entry
            log_data = {
                "loop_id": loop_id,
                "project_id": project_id,
                "agent": agent,
                "task": task,
                "result_tag": result_tag,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "additional_data": additional_data or {}
            }
            
            # Get the existing log or create a new one
            memory_key = f"orchestrator_loop_log_{project_id}"
            existing_log = await read_memory(project_id, memory_key)
            
            if existing_log and "entries" in existing_log:
                # Append to existing log
                existing_log["entries"].append(log_data)
                existing_log["last_updated"] = datetime.utcnow().isoformat()
                result = await write_memory(project_id, memory_key, existing_log)
            else:
                # Create new log
                new_log = {
                    "entries": [log_data],
                    "last_updated": datetime.utcnow().isoformat()
                }
                result = await write_memory(project_id, memory_key, new_log)
            
            logger.info(f"✅ Logged loop event: {agent} - {task} ({status})")
            return result
        except Exception as e:
            logger.error(f"Error logging loop event: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to log loop event: {str(e)}",
                "error": str(e)
            }

# Apply retry decorator to get_loop_log if hardening is available
if hardening_available:
    @async_retry_decorator(retries=3, backoff=1.5)
    async def get_loop_log(project_id: str) -> Dict[str, Any]:
        """
        Retrieve the loop event log for a specific project with retry capability.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dict containing the loop event log
        """
        try:
            # Read the log from memory
            result = await read_memory(
                project_id=project_id,
                tag=f"orchestrator_loop_log_{project_id}"
            )
            
            # If no log exists, return empty log
            if not result:
                return {
                    "entries": [],
                    "last_updated": datetime.utcnow().isoformat()
                }
            
            return result
        except Exception as e:
            error_category = classify_error(e)
            logger.error(f"❌ {error_category} retrieving loop log: {str(e)}")
            
            # Log error to memory
            try:
                await log_error_to_memory(
                    memory_writer=write_memory,
                    project_id=project_id,
                    agent_id="orchestrator",
                    e=e,
                    operation="get_loop_log"
                )
            except Exception as log_error:
                logger.error(f"❌ Failed to log error to memory: {str(log_error)}")
            
            # Re-raise the exception to trigger retry
            raise e
else:
    # Original implementation without retry
    async def get_loop_log(project_id: str) -> Dict[str, Any]:
        """
        Retrieve the loop event log for a specific project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dict containing the loop event log
        """
        try:
            # Read the log from memory
            result = await read_memory(
                project_id=project_id,
                tag=f"orchestrator_loop_log_{project_id}"
            )
            
            # If no log exists, return empty log
            if not result:
                return {
                    "entries": [],
                    "last_updated": datetime.utcnow().isoformat()
                }
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving loop log: {str(e)}")
            # Return empty log on error
            return {
                "entries": [],
                "last_updated": datetime.utcnow().isoformat(),
                "error": str(e)
            }

# Apply retry decorator to store_belief if hardening is available
if hardening_available:
    @async_retry_decorator(retries=3, backoff=1.5)
    async def store_belief(
        project_id: str,
        belief: str,
        confidence: float = 0.8,
        evidence: Optional[List[str]] = None,
        category: str = "agent_performance"
    ) -> Dict[str, Any]:
        """
        Store an orchestrator belief in memory with retry capability.
        
        Args:
            project_id: Project identifier
            belief: The belief statement
            confidence: Confidence level (0.0 to 1.0)
            evidence: List of evidence supporting the belief
            category: Category of the belief
            
        Returns:
            Dict containing the status of the memory write operation
        """
        try:
            # Create the belief entry
            belief_data = {
                "belief": belief,
                "confidence": confidence,
                "evidence": evidence or [],
                "category": category,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Get existing beliefs or create new list
            memory_key = f"orchestrator_beliefs_{project_id}"
            existing_beliefs = await read_memory(project_id, memory_key)
            
            if existing_beliefs and isinstance(existing_beliefs, list):
                # Append to existing beliefs
                existing_beliefs.append(belief_data)
                result = await write_memory(project_id, memory_key, existing_beliefs)
            else:
                # Create new beliefs list
                result = await write_memory(project_id, memory_key, [belief_data])
            
            logger.info(f"✅ Stored belief: {belief[:50]}... ({category}, {confidence:.2f})")
            return result
        except Exception as e:
            error_category = classify_error(e)
            logger.error(f"❌ {error_category} storing belief: {str(e)}")
            
            # Log error to memory
            try:
                await log_error_to_memory(
                    memory_writer=write_memory,
                    project_id=project_id,
                    agent_id="orchestrator",
                    e=e,
                    operation="store_belief"
                )
            except Exception as log_error:
                logger.error(f"❌ Failed to log error to memory: {str(log_error)}")
            
            # Re-raise the exception to trigger retry
            raise e
else:
    # Original implementation without retry
    async def store_belief(
        project_id: str,
        belief: str,
        confidence: float = 0.8,
        evidence: Optional[List[str]] = None,
        category: str = "agent_performance"
    ) -> Dict[str, Any]:
        """
        Store an orchestrator belief in memory.
        
        Args:
            project_id: Project identifier
            belief: The belief statement
            confidence: Confidence level (0.0 to 1.0)
            evidence: List of evidence supporting the belief
            category: Category of the belief
            
        Returns:
            Dict containing the status of the memory write operation
        """
        try:
            # Create the belief entry
            belief_data = {
                "belief": belief,
                "confidence": confidence,
                "evidence": evidence or [],
                "category": category,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Get existing beliefs or create new list
            memory_key = f"orchestrator_beliefs_{project_id}"
            existing_beliefs = await read_memory(project_id, memory_key)
            
            if existing_beliefs and isinstance(existing_beliefs, list):
                # Append to existing beliefs
                existing_beliefs.append(belief_data)
                result = await write_memory(project_id, memory_key, existing_beliefs)
            else:
                # Create new beliefs list
                result = await write_memory(project_id, memory_key, [belief_data])
            
            logger.info(f"✅ Stored belief: {belief[:50]}... ({category}, {confidence:.2f})")
            return result
        except Exception as e:
            logger.error(f"Error storing belief: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to store belief: {str(e)}",
                "error": str(e)
            }

# Apply retry decorator to get_beliefs if hardening is available
if hardening_available:
    @async_retry_decorator(retries=3, backoff=1.5)
    async def get_beliefs(project_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve orchestrator beliefs from memory with retry capability.
        
        Args:
            project_id: Project identifier
            category: Optional category filter
            
        Returns:
            List of belief entries
        """
        try:
            # Read beliefs from memory
            memory_key = f"orchestrator_beliefs_{project_id}"
            beliefs = await read_memory(project_id, memory_key)
            
            # If no beliefs exist, return empty list
            if not beliefs:
                return []
            
            # Filter by category if specified
            if category:
                beliefs = [b for b in beliefs if b.get("category") == category]
            
            return beliefs
        except Exception as e:
            error_category = classify_error(e)
            logger.error(f"❌ {error_category} retrieving beliefs: {str(e)}")
            
            # Log error to memory
            try:
                await log_error_to_memory(
                    memory_writer=write_memory,
                    project_id=project_id,
                    agent_id="orchestrator",
                    e=e,
                    operation="get_beliefs"
                )
            except Exception as log_error:
                logger.error(f"❌ Failed to log error to memory: {str(log_error)}")
            
            # Re-raise the exception to trigger retry
            raise e
else:
    # Original implementation without retry
    async def get_beliefs(project_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve orchestrator beliefs from memory.
        
        Args:
            project_id: Project identifier
            category: Optional category filter
            
        Returns:
            List of belief entries
        """
        try:
            # Read beliefs from memory
            memory_key = f"orchestrator_beliefs_{project_id}"
            beliefs = await read_memory(project_id, memory_key)
            
            # If no beliefs exist, return empty list
            if not beliefs:
                return []
            
            # Filter by category if specified
            if category:
                beliefs = [b for b in beliefs if b.get("category") == category]
            
            return beliefs
        except Exception as e:
            logger.error(f"Error retrieving beliefs: {str(e)}")
            # Return empty list on error
            return []

# Apply retry decorator to get_latest_loop_events if hardening is available
if hardening_available:
    @async_retry_decorator(retries=3, backoff=1.5)
    async def get_latest_loop_events(project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent loop events for a project with retry capability.
        
        Args:
            project_id: Project identifier
            limit: Maximum number of events to return
            
        Returns:
            List of recent loop events
        """
        try:
            # Get the full loop log
            log = await get_loop_log(project_id)
            
            # Extract entries
            entries = log.get("entries", [])
            
            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Return limited number of entries
            return entries[:limit]
        except Exception as e:
            error_category = classify_error(e)
            logger.error(f"❌ {error_category} retrieving latest loop events: {str(e)}")
            
            # Log error to memory
            try:
                await log_error_to_memory(
                    memory_writer=write_memory,
                    project_id=project_id,
                    agent_id="orchestrator",
                    e=e,
                    operation="get_latest_loop_events"
                )
            except Exception as log_error:
                logger.error(f"❌ Failed to log error to memory: {str(log_error)}")
            
            # Re-raise the exception to trigger retry
            raise e
else:
    # Original implementation without retry
    async def get_latest_loop_events(project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent loop events for a project.
        
        Args:
            project_id: Project identifier
            limit: Maximum number of events to return
            
        Returns:
            List of recent loop events
        """
        try:
            # Get the full loop log
            log = await get_loop_log(project_id)
            
            # Extract entries
            entries = log.get("entries", [])
            
            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Return limited number of entries
            return entries[:limit]
        except Exception as e:
            logger.error(f"Error retrieving latest loop events: {str(e)}")
            return []

# Apply retry decorator to get_agent_activity_summary if hardening is available
if hardening_available:
    @async_retry_decorator(retries=3, backoff=1.5)
    async def get_agent_activity_summary(project_id: str) -> Dict[str, Any]:
        """
        Generate a summary of agent activities for a project with retry capability.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dict containing agent activity summary
        """
        try:
            # Get the full loop log
            log = await get_loop_log(project_id)
            
            # Extract entries
            entries = log.get("entries", [])
            
            # Initialize summary
            summary = {
                "total_events": len(entries),
                "agents": {},
                "latest_event": None,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Process entries
            for entry in entries:
                agent = entry.get("agent")
                if agent:
                    # Update agent stats
                    if agent not in summary["agents"]:
                        summary["agents"][agent] = {
                            "total_actions": 0,
                            "completed": 0,
                            "failed": 0,
                            "in_progress": 0,
                            "latest_action": None
                        }
                    
                    # Increment counters
                    summary["agents"][agent]["total_actions"] += 1
                    status = entry.get("status", "unknown")
                    if status in ["completed", "failed", "in_progress"]:
                        summary["agents"][agent][status] += 1
                    
                    # Update latest action
                    if not summary["agents"][agent]["latest_action"] or \
                       entry.get("timestamp", "") > summary["agents"][agent]["latest_action"].get("timestamp", ""):
                        summary["agents"][agent]["latest_action"] = entry
            
            # Find latest event overall
            if entries:
                entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                summary["latest_event"] = entries[0]
            
            return summary
        except Exception as e:
            error_category = classify_error(e)
            logger.error(f"❌ {error_category} generating agent activity summary: {str(e)}")
            
            # Log error to memory
            try:
                await log_error_to_memory(
                    memory_writer=write_memory,
                    project_id=project_id,
                    agent_id="orchestrator",
                    e=e,
                    operation="get_agent_activity_summary"
                )
            except Exception as log_error:
                logger.error(f"❌ Failed to log error to memory: {str(log_error)}")
            
            # Re-raise the exception to trigger retry
            raise e
else:
    # Original implementation without retry
    async def get_agent_activity_summary(project_id: str) -> Dict[str, Any]:
        """
        Generate a summary of agent activities for a project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dict containing agent activity summary
        """
        try:
            # Get the full loop log
            log = await get_loop_log(project_id)
            
            # Extract entries
            entries = log.get("entries", [])
            
            # Initialize summary
            summary = {
                "total_events": len(entries),
                "agents": {},
                "latest_event": None,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Process entries
            for entry in entries:
                agent = entry.get("agent")
                if agent:
                    # Update agent stats
                    if agent not in summary["agents"]:
                        summary["agents"][agent] = {
                            "total_actions": 0,
                            "completed": 0,
                            "failed": 0,
                            "in_progress": 0,
                            "latest_action": None
                        }
                    
                    # Increment counters
                    summary["agents"][agent]["total_actions"] += 1
                    status = entry.get("status", "unknown")
                    if status in ["completed", "failed", "in_progress"]:
                        summary["agents"][agent][status] += 1
                    
                    # Update latest action
                    if not summary["agents"][agent]["latest_action"] or \
                       entry.get("timestamp", "") > summary["agents"][agent]["latest_action"].get("timestamp", ""):
                        summary["agents"][agent]["latest_action"] = entry
            
            # Find latest event overall
            if entries:
                entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                summary["latest_event"] = entries[0]
            
            return summary
        except Exception as e:
            logger.error(f"Error generating agent activity summary: {str(e)}")
            return {
                "total_events": 0,
                "agents": {},
                "latest_event": None,
                "generated_at": datetime.utcnow().isoformat(),
                "error": str(e)
            }
