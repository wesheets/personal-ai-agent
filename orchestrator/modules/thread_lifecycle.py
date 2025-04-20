"""
Thread Lifecycle Management Module

This module provides functionality for managing the lifecycle of nested comment threads
in the Promethios system. It handles status transitions between open, closed, integrated,
and discarded states, and ensures proper logging of lifecycle events.

Created for Phase 11.3.1 Nested Comments + Thread Logic implementation.
"""

import logging
import datetime
import json
import os
import sys
from typing import Dict, List, Any, Optional, Union
import traceback

# Configure logging
logger = logging.getLogger("orchestrator.thread_lifecycle")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import required modules
try:
    from orchestrator.modules.nested_comments import get_thread_messages, update_thread_status
    from orchestrator.modules.thread_summarizer import generate_thread_summary
    MODULES_AVAILABLE = True
    logger.info("Successfully imported required modules")
except ImportError:
    MODULES_AVAILABLE = False
    logger.warning("Failed to import required modules, will use direct memory access")

def close_thread(
    memory: Dict[str, Any],
    thread_id: str,
    agent: str,
    auto_summarize: bool = True,
    summary: Optional[str] = None,
    max_summary_length: int = 500
) -> bool:
    """
    Close a thread and optionally generate a summary.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        agent: The agent closing the thread
        auto_summarize: Whether to automatically generate a summary
        summary: Optional manual summary (overrides auto-summary)
        max_summary_length: Maximum length of auto-generated summary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Closing thread {thread_id} by {agent}")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found")
            return False
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Get root message
        root_message = thread_messages[0]
        
        # Check if thread is already closed
        if root_message.get("status") in ["closed", "integrated", "discarded"]:
            logger.warning(f"Thread {thread_id} is already in {root_message.get('status')} state")
            return False
        
        # Generate summary if needed
        thread_summary = summary
        
        if auto_summarize and not thread_summary:
            if MODULES_AVAILABLE:
                thread_summary = generate_thread_summary(memory, thread_id, max_summary_length)
            else:
                # Simple summary generation if module not available
                thread_summary = f"Thread closed by {agent} with {len(thread_messages)} messages."
        
        # Update thread status
        if MODULES_AVAILABLE:
            update_result = update_thread_status(
                memory=memory,
                thread_id=thread_id,
                status="closed",
                summary=thread_summary,
                agent=agent
            )
            
            if not update_result:
                logger.error(f"Failed to update thread status to closed")
                return False
        else:
            # Direct memory access if module not available
            # Get loop ID from root message
            loop_id = root_message["loop_id"]
            
            # Create timestamp
            timestamp = datetime.datetime.now().isoformat()
            
            # Update thread status in thread history
            found = False
            for loop_threads in memory["thread_history"].values():
                if thread_id in loop_threads:
                    loop_threads[thread_id]["status"] = "closed"
                    loop_threads[thread_id]["last_updated_at"] = timestamp
                    
                    if thread_summary:
                        loop_threads[thread_id]["summary"] = thread_summary
                    
                    found = True
                    break
            
            if not found:
                logger.error(f"Thread {thread_id} not found in thread history")
                return False
            
            # Update root message status and summary
            root_message["status"] = "closed"
            
            if thread_summary:
                root_message["summary"] = thread_summary
            
            # Update thread metadata
            if "thread_metadata" in root_message and root_message["thread_metadata"]:
                root_message["thread_metadata"]["last_updated_at"] = timestamp
            
            # Add to loop trace if exists
            if "loop_trace" in memory and loop_id in memory["loop_trace"]:
                if "thread_activity" not in memory["loop_trace"][loop_id]:
                    memory["loop_trace"][loop_id]["thread_activity"] = []
                
                trace_entry = {
                    "action": "thread_closed",
                    "thread_id": thread_id,
                    "agent": agent,
                    "timestamp": timestamp
                }
                
                if thread_summary:
                    trace_entry["summary"] = thread_summary
                
                memory["loop_trace"][loop_id]["thread_activity"].append(trace_entry)
            
            # Add to chat messages if requested
            if "chat_messages" in memory:
                chat_message = {
                    "role": "orchestrator",
                    "agent": agent,
                    "message": f"🔵 Thread closed: {root_message['message'][:100]}{'...' if len(root_message['message']) > 100 else ''}",
                    "loop": loop_id,
                    "timestamp": timestamp,
                    "thread_id": thread_id
                }
                
                if thread_summary:
                    chat_message["message"] += f"\n\nSummary: {thread_summary}"
                
                memory["chat_messages"].append(chat_message)
        
        logger.info(f"Closed thread {thread_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error closing thread: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def integrate_thread(
    memory: Dict[str, Any],
    thread_id: str,
    agent: str,
    plan_step: Optional[int] = None,
    integration_type: str = "modification",
    integration_summary: Optional[str] = None
) -> bool:
    """
    Integrate a thread into the plan.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        agent: The agent integrating the thread
        plan_step: Optional plan step that was affected
        integration_type: How the thread was integrated (addition, modification, removal, clarification)
        integration_summary: Optional summary of how the thread was integrated
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Integrating thread {thread_id} by {agent}")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found")
            return False
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Get root message
        root_message = thread_messages[0]
        
        # Check if thread is already integrated
        if root_message.get("status") == "integrated":
            logger.warning(f"Thread {thread_id} is already integrated")
            return False
        
        # Get loop ID from root message
        loop_id = root_message["loop_id"]
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Create integration summary if not provided
        if not integration_summary:
            integration_summary = f"Thread integrated by {agent}"
            
            if plan_step is not None:
                integration_summary += f" into plan step {plan_step}"
            
            integration_summary += f" as {integration_type}."
        
        # Create plan integration object
        plan_integration = {
            "integrated_at": timestamp,
            "plan_step": plan_step,
            "integration_type": integration_type,
            "integration_summary": integration_summary
        }
        
        # Update thread status to integrated
        if MODULES_AVAILABLE:
            from orchestrator.modules.nested_comments import integrate_thread_with_plan
            
            integration_result = integrate_thread_with_plan(
                memory=memory,
                thread_id=thread_id,
                plan_step=plan_step,
                integration_type=integration_type,
                integration_summary=integration_summary,
                agent=agent
            )
            
            if not integration_result:
                logger.error(f"Failed to integrate thread")
                return False
        else:
            # Direct memory access if module not available
            # Update thread status in thread history
            found = False
            for loop_threads in memory["thread_history"].values():
                if thread_id in loop_threads:
                    loop_threads[thread_id]["status"] = "integrated"
                    loop_threads[thread_id]["last_updated_at"] = timestamp
                    loop_threads[thread_id]["summary"] = integration_summary
                    found = True
                    break
            
            if not found:
                logger.error(f"Thread {thread_id} not found in thread history")
                return False
            
            # Update root message status, summary, and plan integration
            root_message["status"] = "integrated"
            root_message["summary"] = integration_summary
            root_message["plan_integration"] = plan_integration
            
            # Update thread metadata
            if "thread_metadata" in root_message and root_message["thread_metadata"]:
                root_message["thread_metadata"]["last_updated_at"] = timestamp
            
            # Add to loop trace if exists
            if "loop_trace" in memory and loop_id in memory["loop_trace"]:
                if "thread_activity" not in memory["loop_trace"][loop_id]:
                    memory["loop_trace"][loop_id]["thread_activity"] = []
                
                trace_entry = {
                    "action": "thread_integrated",
                    "thread_id": thread_id,
                    "agent": agent,
                    "timestamp": timestamp,
                    "plan_step": plan_step,
                    "integration_type": integration_type,
                    "integration_summary": integration_summary
                }
                
                memory["loop_trace"][loop_id]["thread_activity"].append(trace_entry)
                
                # Add to thread summaries if not exists
                if "thread_summaries" not in memory["loop_trace"][loop_id]:
                    memory["loop_trace"][loop_id]["thread_summaries"] = []
                
                memory["loop_trace"][loop_id]["thread_summaries"].append({
                    "thread_id": thread_id,
                    "integrated_at": timestamp,
                    "plan_step": plan_step,
                    "integration_type": integration_type,
                    "summary": integration_summary,
                    "agent": agent
                })
            
            # Add to chat messages if requested
            if "chat_messages" in memory:
                step_text = f" (step {plan_step})" if plan_step is not None else ""
                
                memory["chat_messages"].append({
                    "role": "orchestrator",
                    "agent": agent,
                    "message": f"✅ Thread integrated into plan{step_text}: {integration_summary}",
                    "loop": loop_id,
                    "timestamp": timestamp,
                    "thread_id": thread_id
                })
        
        logger.info(f"Integrated thread {thread_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error integrating thread: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def discard_thread(
    memory: Dict[str, Any],
    thread_id: str,
    agent: str,
    reason: Optional[str] = None
) -> bool:
    """
    Discard a thread.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        agent: The agent discarding the thread
        reason: Optional reason for discarding
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Discarding thread {thread_id} by {agent}")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found")
            return False
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Get root message
        root_message = thread_messages[0]
        
        # Check if thread is already discarded
        if root_message.get("status") == "discarded":
            logger.warning(f"Thread {thread_id} is already discarded")
            return False
        
        # Create discard summary
        discard_summary = f"Thread discarded by {agent}"
        
        if reason:
            discard_summary += f": {reason}"
        else:
            discard_summary += "."
        
        # Update thread status to discarded
        if MODULES_AVAILABLE:
            update_result = update_thread_status(
                memory=memory,
                thread_id=thread_id,
                status="discarded",
                summary=discard_summary,
                agent=agent
            )
            
            if not update_result:
                logger.error(f"Failed to update thread status to discarded")
                return False
        else:
            # Direct memory access if module not available
            # Get loop ID from root message
            loop_id = root_message["loop_id"]
            
            # Create timestamp
            timestamp = datetime.datetime.now().isoformat()
            
            # Update thread status in thread history
            found = False
            for loop_threads in memory["thread_history"].values():
                if thread_id in loop_threads:
                    loop_threads[thread_id]["status"] = "discarded"
                    loop_threads[thread_id]["last_updated_at"] = timestamp
                    loop_threads[thread_id]["summary"] = discard_summary
                    found = True
                    break
            
            if not found:
                logger.error(f"Thread {thread_id} not found in thread history")
                return False
            
            # Update root message status and summary
            root_message["status"] = "discarded"
            root_message["summary"] = discard_summary
            
            # Update thread metadata
            if "thread_metadata" in root_message and root_message["thread_metadata"]:
                root_message["thread_metadata"]["last_updated_at"] = timestamp
            
            # Add to loop trace if exists
            if "loop_trace" in memory and loop_id in memory["loop_trace"]:
                if "thread_activity" not in memory["loop_trace"][loop_id]:
                    memory["loop_trace"][loop_id]["thread_activity"] = []
                
                trace_entry = {
                    "action": "thread_discarded",
                    "thread_id": thread_id,
                    "agent": agent,
                    "timestamp": timestamp,
                    "reason": reason
                }
                
                memory["loop_trace"][loop_id]["thread_activity"].append(trace_entry)
            
            # Add to chat messages if requested
            if "chat_messages" in memory:
                chat_message = {
                    "role": "orchestrator",
                    "agent": agent,
                    "message": f"❌ Thread discarded: {root_message['message'][:100]}{'...' if len(root_message['message']) > 100 else ''}",
                    "loop": loop_id,
                    "timestamp": timestamp,
                    "thread_id": thread_id
                }
                
                if reason:
                    chat_message["message"] += f"\n\nReason: {reason}"
                
                memory["chat_messages"].append(chat_message)
        
        logger.info(f"Discarded thread {thread_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error discarding thread: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def reopen_thread(
    memory: Dict[str, Any],
    thread_id: str,
    agent: str,
    reason: Optional[str] = None
) -> bool:
    """
    Reopen a closed, integrated, or discarded thread.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        agent: The agent reopening the thread
        reason: Optional reason for reopening
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Reopening thread {thread_id} by {agent}")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found")
            return False
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Get root message
        root_message = thread_messages[0]
        
        # Check if thread is already open
        if root_message.get("status") == "open":
            logger.warning(f"Thread {thread_id} is already open")
            return False
        
        # Get previous status for logging
        previous_status = root_message.get("status", "unknown")
        
        # Update thread status to open
        if MODULES_AVAILABLE:
            update_result = update_thread_status(
                memory=memory,
                thread_id=thread_id,
                status="open",
                summary=None,  # Clear summary when reopening
                agent=agent
            )
            
            if not update_result:
                logger.error(f"Failed to update thread status to open")
                return False
        else:
            # Direct memory access if module not available
            # Get loop ID from root message
            loop_id = root_message["loop_id"]
            
            # Create timestamp
            timestamp = datetime.datetime.now().isoformat()
            
            # Update thread status in thread history
            found = False
            for loop_threads in memory["thread_history"].values():
                if thread_id in loop_threads:
                    loop_threads[thread_id]["status"] = "open"
                    loop_threads[thread_id]["last_updated_at"] = timestamp
                    loop_threads[thread_id]["summary"] = None  # Clear summary when reopening
                    found = True
                    break
            
            if not found:
                logger.error(f"Thread {thread_id} not found in thread history")
                return False
            
            # Update root message status and clear summary
            root_message["status"] = "open"
            root_message["summary"] = None
            
            # Clear plan integration if exists
            if "plan_integration" in root_message:
                root_message["plan_integration"] = None
            
            # Update thread metadata
            if "thread_metadata" in root_message and root_message["thread_metadata"]:
                root_message["thread_metadata"]["last_updated_at"] = timestamp
            
            # Add to loop trace if exists
            if "loop_trace" in memory and loop_id in memory["loop_trace"]:
                if "thread_activity" not in memory["loop_trace"][loop_id]:
                    memory["loop_trace"][loop_id]["thread_activity"] = []
                
                trace_entry = {
                    "action": "thread_reopened",
                    "thread_id": thread_id,
                    "agent": agent,
                    "timestamp": timestamp,
                    "previous_status": previous_status
                }
                
                if reason:
                    trace_entry["reason"] = reason
                
                memory["loop_trace"][loop_id]["thread_activity"].append(trace_entry)
            
            # Add to chat messages if requested
            if "chat_messages" in memory:
                chat_message = {
                    "role": "orchestrator",
                    "agent": agent,
                    "message": f"🟢 Thread reopened (was {previous_status}): {root_message['message'][:100]}{'...' if len(root_message['message']) > 100 else ''}",
                    "loop": loop_id,
                    "timestamp": timestamp,
                    "thread_id": thread_id
                }
                
                if reason:
                    chat_message["message"] += f"\n\nReason: {reason}"
                
                memory["chat_messages"].append(chat_message)
        
        logger.info(f"Reopened thread {thread_id} (was {previous_status})")
        return True
    
    except Exception as e:
        logger.error(f"Error reopening thread: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def batch_close_inactive_threads(
    memory: Dict[str, Any],
    loop_id: int,
    agent: str = "orchestrator",
    inactivity_threshold_minutes: int = 30,
    max_threads: int = 10
) -> Dict[str, Any]:
    """
    Batch close inactive threads for a loop.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        agent: The agent performing the batch close
        inactivity_threshold_minutes: Threshold in minutes to consider a thread inactive
        max_threads: Maximum number of threads to close
        
    Returns:
        Dictionary with results of the batch close
    """
    try:
        logger.info(f"Batch closing inactive threads for loop {loop_id}")
        
        # Check if loop exists in thread history
        if "thread_history" not in memory or loop_id not in memory["thread_history"]:
            logger.info(f"No threads found for loop {loop_id}")
            return {"success": True, "closed": 0, "failed": 0, "skipped": 0}
        
        # Get threads for loop
        loop_threads = memory["thread_history"][loop_id]
        
        # Initialize counters
        closed = 0
        failed = 0
        skipped = 0
        
        # Get current time
        current_time = datetime.datetime.now()
        
        # Iterate through threads
        for thread_id, thread_meta in loop_threads.items():
            # Only close open threads
            if thread_meta["status"] == "open":
                # Skip if max threads reached
                if closed >= max_threads:
                    skipped += 1
                    continue
                
                # Check if thread is inactive
                last_updated = datetime.datetime.fromisoformat(thread_meta["last_updated_at"])
                inactive_minutes = (current_time - last_updated).total_seconds() / 60
                
                if inactive_minutes >= inactivity_threshold_minutes:
                    # Close thread
                    close_result = close_thread(
                        memory=memory,
                        thread_id=thread_id,
                        agent=agent,
                        auto_summarize=True
                    )
                    
                    if close_result:
                        closed += 1
                    else:
                        failed += 1
                else:
                    skipped += 1
            else:
                skipped += 1
        
        logger.info(f"Batch closed {closed} inactive threads for loop {loop_id} (failed: {failed}, skipped: {skipped})")
        return {
            "success": True,
            "closed": closed,
            "failed": failed,
            "skipped": skipped
        }
    
    except Exception as e:
        logger.error(f"Error batch closing inactive threads: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "closed": 0,
            "failed": 0,
            "skipped": 0
        }

def get_thread_lifecycle_history(
    memory: Dict[str, Any],
    thread_id: str
) -> List[Dict[str, Any]]:
    """
    Get the lifecycle history of a thread.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        
    Returns:
        List of lifecycle events for the thread
    """
    try:
        logger.info(f"Getting lifecycle history for thread {thread_id}")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found")
            return []
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Get root message
        root_message = thread_messages[0]
        
        # Get loop ID from root message
        loop_id = root_message["loop_id"]
        
        # Initialize lifecycle events
        lifecycle_events = []
        
        # Add thread creation event
        lifecycle_events.append({
            "action": "thread_created",
            "thread_id": thread_id,
            "agent": root_message["agent"],
            "timestamp": root_message["timestamp"],
            "status": "open"
        })
        
        # Check if loop trace exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"] and "thread_activity" in memory["loop_trace"][loop_id]:
            # Get thread activity from loop trace
            thread_activity = memory["loop_trace"][loop_id]["thread_activity"]
            
            # Filter activity for this thread
            thread_activity = [event for event in thread_activity if event.get("thread_id") == thread_id]
            
            # Add to lifecycle events
            lifecycle_events.extend(thread_activity)
        
        # Sort by timestamp
        lifecycle_events.sort(key=lambda x: x.get("timestamp", ""))
        
        logger.info(f"Retrieved {len(lifecycle_events)} lifecycle events for thread {thread_id}")
        return lifecycle_events
    
    except Exception as e:
        logger.error(f"Error getting thread lifecycle history: {str(e)}")
        logger.error(traceback.format_exc())
        return []
