"""
Thread-to-Plan Integration Module

This module provides functionality for integrating insights from nested comment threads
into plans in the Promethios system. It enables actionable thread content to be
incorporated into plan revisions, ensuring valuable discussions lead to concrete actions.

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
logger = logging.getLogger("orchestrator.thread_plan_integration")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import required modules
try:
    from orchestrator.modules.nested_comments import get_thread_messages, mark_thread_for_plan_revision
    from orchestrator.modules.thread_summarizer import get_actionable_threads
    from orchestrator.modules.thread_lifecycle import integrate_thread
    MODULES_AVAILABLE = True
    logger.info("Successfully imported required modules")
except ImportError:
    MODULES_AVAILABLE = False
    logger.warning("Failed to import required modules, will use direct memory access")

def mark_thread_actionable(
    memory: Dict[str, Any],
    thread_id: str,
    agent: str,
    reason: Optional[str] = None
) -> bool:
    """
    Mark a thread as containing actionable insights for plan revision.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        agent: The agent marking the thread
        reason: Optional reason for marking as actionable
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Marking thread {thread_id} as actionable by {agent}")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found")
            return False
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Get root message
        root_message = thread_messages[0]
        
        # Check if thread is already marked as actionable
        if root_message.get("actionable", False):
            logger.warning(f"Thread {thread_id} is already marked as actionable")
            return True
        
        # Mark thread as actionable
        if MODULES_AVAILABLE:
            mark_result = mark_thread_for_plan_revision(
                memory=memory,
                thread_id=thread_id,
                agent=agent
            )
            
            if not mark_result:
                logger.error(f"Failed to mark thread as actionable")
                return False
        else:
            # Direct memory access if module not available
            # Get loop ID from root message
            loop_id = root_message["loop_id"]
            
            # Create timestamp
            timestamp = datetime.datetime.now().isoformat()
            
            # Update thread actionable flag in thread history
            found = False
            for loop_threads in memory["thread_history"].values():
                if thread_id in loop_threads:
                    loop_threads[thread_id]["actionable"] = True
                    loop_threads[thread_id]["last_updated_at"] = timestamp
                    found = True
                    break
            
            if not found:
                logger.error(f"Thread {thread_id} not found in thread history")
                return False
            
            # Update root message actionable flag
            root_message["actionable"] = True
            
            # Update thread metadata
            if "thread_metadata" in root_message and root_message["thread_metadata"]:
                root_message["thread_metadata"]["last_updated_at"] = timestamp
            
            # Add to loop trace if exists
            if "loop_trace" in memory and loop_id in memory["loop_trace"]:
                if "thread_activity" not in memory["loop_trace"][loop_id]:
                    memory["loop_trace"][loop_id]["thread_activity"] = []
                
                trace_entry = {
                    "action": "thread_marked_actionable",
                    "thread_id": thread_id,
                    "agent": agent,
                    "timestamp": timestamp
                }
                
                if reason:
                    trace_entry["reason"] = reason
                
                memory["loop_trace"][loop_id]["thread_activity"].append(trace_entry)
                
                # Add to plan deviations if exists
                if "plan_deviations" not in memory["loop_trace"][loop_id]:
                    memory["loop_trace"][loop_id]["plan_deviations"] = []
                
                deviation_entry = {
                    "type": "thread_insight",
                    "thread_id": thread_id,
                    "agent": agent,
                    "timestamp": timestamp,
                    "message": f"Thread contains actionable insights for plan revision: {root_message['message'][:100]}{'...' if len(root_message['message']) > 100 else ''}"
                }
                
                if reason:
                    deviation_entry["reason"] = reason
                
                memory["loop_trace"][loop_id]["plan_deviations"].append(deviation_entry)
            
            # Add to chat messages if requested
            if "chat_messages" in memory:
                chat_message = {
                    "role": "orchestrator",
                    "agent": agent,
                    "message": f"🔍 Thread marked for plan revision: {root_message['message'][:100]}{'...' if len(root_message['message']) > 100 else ''}",
                    "loop": loop_id,
                    "timestamp": timestamp,
                    "thread_id": thread_id
                }
                
                if reason:
                    chat_message["message"] += f"\n\nReason: {reason}"
                
                memory["chat_messages"].append(chat_message)
        
        logger.info(f"Marked thread {thread_id} as actionable")
        return True
    
    except Exception as e:
        logger.error(f"Error marking thread as actionable: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def get_plan_for_loop(
    memory: Dict[str, Any],
    loop_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get the current plan for a loop.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        
    Returns:
        The current plan or None if not found
    """
    try:
        logger.info(f"Getting plan for loop {loop_id}")
        
        # Check if loop trace exists
        if "loop_trace" not in memory or loop_id not in memory["loop_trace"]:
            logger.error(f"Loop trace not found for loop {loop_id}")
            return None
        
        # Check if plan exists
        if "plan" not in memory["loop_trace"][loop_id]:
            logger.error(f"Plan not found in loop trace for loop {loop_id}")
            return None
        
        # Return plan
        return memory["loop_trace"][loop_id]["plan"]
    
    except Exception as e:
        logger.error(f"Error getting plan for loop: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def update_plan_with_thread_insight(
    memory: Dict[str, Any],
    thread_id: str,
    plan_step: int,
    agent: str,
    modification_type: str = "addition",
    modification_content: Optional[str] = None
) -> bool:
    """
    Update a plan with insights from a thread.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        plan_step: The plan step to modify
        agent: The agent updating the plan
        modification_type: Type of modification (addition, modification, removal, clarification)
        modification_content: Optional content for the modification
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Updating plan with insights from thread {thread_id} by {agent}")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found")
            return False
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Get root message
        root_message = thread_messages[0]
        
        # Get loop ID from root message
        loop_id = root_message["loop_id"]
        
        # Get current plan
        plan = get_plan_for_loop(memory, loop_id)
        
        if not plan:
            logger.error(f"Failed to get plan for loop {loop_id}")
            return False
        
        # Check if plan step exists
        if "steps" not in plan or plan_step >= len(plan["steps"]):
            logger.error(f"Plan step {plan_step} not found in plan")
            return False
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Generate modification content if not provided
        if not modification_content:
            # Get thread summary if available
            summary = root_message.get("summary")
            
            if summary:
                modification_content = f"Based on thread discussion: {summary}"
            else:
                # Use root message content
                modification_content = f"Based on thread discussion: {root_message['message'][:200]}{'...' if len(root_message['message']) > 200 else ''}"
        
        # Store original step content
        original_step = plan["steps"][plan_step]
        
        # Update plan step based on modification type
        if modification_type == "addition":
            # Add content to step
            plan["steps"][plan_step] += f"\n\n{modification_content}"
        elif modification_type == "modification":
            # Replace step content
            plan["steps"][plan_step] = modification_content
        elif modification_type == "removal":
            # Remove step (replace with removal notice)
            plan["steps"][plan_step] = f"[Removed based on thread insight] {original_step[:50]}..."
        elif modification_type == "clarification":
            # Add clarification to step
            plan["steps"][plan_step] += f"\n\nClarification: {modification_content}"
        else:
            logger.error(f"Unknown modification type: {modification_type}")
            return False
        
        # Update plan in memory
        memory["loop_trace"][loop_id]["plan"] = plan
        
        # Add to plan revisions if exists
        if "plan_revisions" not in memory["loop_trace"][loop_id]:
            memory["loop_trace"][loop_id]["plan_revisions"] = []
        
        memory["loop_trace"][loop_id]["plan_revisions"].append({
            "timestamp": timestamp,
            "agent": agent,
            "step": plan_step,
            "modification_type": modification_type,
            "original_content": original_step,
            "new_content": plan["steps"][plan_step],
            "thread_id": thread_id
        })
        
        # Integrate thread with plan
        integration_summary = f"Thread insights integrated into plan step {plan_step} as {modification_type}."
        
        if MODULES_AVAILABLE:
            integrate_result = integrate_thread(
                memory=memory,
                thread_id=thread_id,
                agent=agent,
                plan_step=plan_step,
                integration_type=modification_type,
                integration_summary=integration_summary
            )
            
            if not integrate_result:
                logger.error(f"Failed to integrate thread with plan")
                return False
        
        logger.info(f"Updated plan with insights from thread {thread_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating plan with thread insight: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def process_actionable_threads(
    memory: Dict[str, Any],
    loop_id: int,
    agent: str = "orchestrator",
    max_threads: int = 5
) -> Dict[str, Any]:
    """
    Process actionable threads for a loop and update the plan.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        agent: The agent processing the threads
        max_threads: Maximum number of threads to process
        
    Returns:
        Dictionary with results of the processing
    """
    try:
        logger.info(f"Processing actionable threads for loop {loop_id}")
        
        # Get actionable threads
        if MODULES_AVAILABLE:
            actionable_threads = get_actionable_threads(memory, loop_id)
        else:
            # Direct memory access if module not available
            actionable_threads = []
            
            # Check if thread history exists
            if "thread_history" in memory and loop_id in memory["thread_history"]:
                # Iterate through threads in loop
                for thread_id, thread_meta in memory["thread_history"][loop_id].items():
                    # Check if thread is actionable and not yet integrated
                    if thread_meta.get("actionable", False) and thread_meta["status"] != "integrated":
                        # Get thread messages
                        if "thread_messages" in memory and thread_id in memory["thread_messages"]:
                            root_message = memory["thread_messages"][thread_id][0]
                            
                            # Create actionable thread object
                            actionable_thread = {
                                "thread_id": thread_id,
                                "loop_id": loop_id,
                                "status": thread_meta["status"],
                                "created_at": thread_meta["created_at"],
                                "last_updated_at": thread_meta["last_updated_at"],
                                "creator": thread_meta["creator"],
                                "participants": thread_meta["participants"],
                                "reply_count": thread_meta["reply_count"],
                                "topic": root_message["message"][:100] + ("..." if len(root_message["message"]) > 100 else ""),
                                "summary": thread_meta.get("summary")
                            }
                            
                            actionable_threads.append(actionable_thread)
        
        # Check if any actionable threads found
        if not actionable_threads:
            logger.info(f"No actionable threads found for loop {loop_id}")
            return {
                "success": True,
                "processed": 0,
                "failed": 0,
                "skipped": 0,
                "message": "No actionable threads found"
            }
        
        # Get current plan
        plan = get_plan_for_loop(memory, loop_id)
        
        if not plan:
            logger.error(f"Failed to get plan for loop {loop_id}")
            return {
                "success": False,
                "processed": 0,
                "failed": 0,
                "skipped": 0,
                "message": "Failed to get plan for loop"
            }
        
        # Initialize counters
        processed = 0
        failed = 0
        skipped = 0
        
        # Process threads
        for thread in actionable_threads:
            # Skip if max threads reached
            if processed >= max_threads:
                skipped += 1
                continue
            
            # Determine best plan step to update
            # For simplicity, use the first step that mentions a keyword from the thread topic
            thread_topic = thread.get("topic", "")
            topic_words = set(thread_topic.lower().split())
            
            best_step = 0
            best_match = 0
            
            for i, step in enumerate(plan.get("steps", [])):
                step_words = set(step.lower().split())
                match_count = len(topic_words.intersection(step_words))
                
                if match_count > best_match:
                    best_match = match_count
                    best_step = i
            
            # Update plan with thread insight
            update_result = update_plan_with_thread_insight(
                memory=memory,
                thread_id=thread["thread_id"],
                plan_step=best_step,
                agent=agent,
                modification_type="addition"  # Default to addition
            )
            
            if update_result:
                processed += 1
            else:
                failed += 1
        
        logger.info(f"Processed {processed} actionable threads for loop {loop_id} (failed: {failed}, skipped: {skipped})")
        return {
            "success": True,
            "processed": processed,
            "failed": failed,
            "skipped": skipped,
            "message": f"Processed {processed} actionable threads"
        }
    
    except Exception as e:
        logger.error(f"Error processing actionable threads: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "processed": 0,
            "failed": 0,
            "skipped": 0,
            "message": f"Error: {str(e)}"
        }

def suggest_plan_modifications_from_threads(
    memory: Dict[str, Any],
    loop_id: int,
    max_suggestions: int = 3
) -> List[Dict[str, Any]]:
    """
    Suggest plan modifications based on thread discussions.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        max_suggestions: Maximum number of suggestions to return
        
    Returns:
        List of suggested plan modifications
    """
    try:
        logger.info(f"Suggesting plan modifications from threads for loop {loop_id}")
        
        # Get all threads for loop
        threads = []
        
        if "thread_history" in memory and loop_id in memory["thread_history"]:
            for thread_id, thread_meta in memory["thread_history"][loop_id].items():
                # Include all threads that are not discarded
                if thread_meta["status"] != "discarded":
                    # Get thread messages
                    if "thread_messages" in memory and thread_id in memory["thread_messages"]:
                        root_message = memory["thread_messages"][thread_id][0]
                        
                        # Create thread object
                        thread = {
                            "thread_id": thread_id,
                            "status": thread_meta["status"],
                            "created_at": thread_meta["created_at"],
                            "last_updated_at": thread_meta["last_updated_at"],
                            "creator": thread_meta["creator"],
                            "participants": thread_meta["participants"],
                            "reply_count": thread_meta["reply_count"],
                            "topic": root_message["message"],
                            "summary": thread_meta.get("summary"),
                            "actionable": thread_meta.get("actionable", False)
                        }
                        
                        threads.append(thread)
        
        # Get current plan
        plan = get_plan_for_loop(memory, loop_id)
        
        if not plan:
            logger.error(f"Failed to get plan for loop {loop_id}")
            return []
        
        # Initialize suggestions
        suggestions = []
        
        # Process threads
        for thread in threads:
            # Skip if already actionable
            if thread.get("actionable", False):
                continue
            
            # Skip if already integrated
            if thread.get("status") == "integrated":
                continue
            
            # Get thread topic and summary
            topic = thread.get("topic", "")
            summary = thread.get("summary")
            
            # Use summary if available, otherwise use topic
            content = summary if summary else topic
            
            # Determine best plan step to update
            # For simplicity, use the first step that mentions a keyword from the thread topic
            topic_words = set(topic.lower().split())
            
            best_step = 0
            best_match = 0
            
            for i, step in enumerate(plan.get("steps", [])):
                step_words = set(step.lower().split())
                match_count = len(topic_words.intersection(step_words))
                
                if match_count > best_match:
                    best_match = match_count
                    best_step = i
            
            # Create suggestion
            suggestion = {
                "thread_id": thread["thread_id"],
                "plan_step": best_step,
                "modification_type": "addition",  # Default to addition
                "content": content[:200] + ("..." if len(content) > 200 else ""),
                "confidence": best_match / max(1, len(topic_words)),  # Simple confidence score
                "thread_status": thread["status"],
                "participants": thread["participants"]
            }
            
            suggestions.append(suggestion)
        
        # Sort by confidence (highest first)
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Return top N suggestions
        return suggestions[:max_suggestions]
    
    except Exception as e:
        logger.error(f"Error suggesting plan modifications: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def get_plan_integration_history(
    memory: Dict[str, Any],
    loop_id: int
) -> List[Dict[str, Any]]:
    """
    Get the history of thread integrations into the plan.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        
    Returns:
        List of thread integration events
    """
    try:
        logger.info(f"Getting plan integration history for loop {loop_id}")
        
        # Initialize integration history
        integration_history = []
        
        # Check if loop trace exists
        if "loop_trace" not in memory or loop_id not in memory["loop_trace"]:
            logger.error(f"Loop trace not found for loop {loop_id}")
            return []
        
        # Check if plan revisions exist
        if "plan_revisions" in memory["loop_trace"][loop_id]:
            # Get plan revisions
            plan_revisions = memory["loop_trace"][loop_id]["plan_revisions"]
            
            # Filter revisions with thread_id
            thread_revisions = [rev for rev in plan_revisions if "thread_id" in rev]
            
            # Add to integration history
            integration_history.extend(thread_revisions)
        
        # Check if thread summaries exist
        if "thread_summaries" in memory["loop_trace"][loop_id]:
            # Get thread summaries
            thread_summaries = memory["loop_trace"][loop_id]["thread_summaries"]
            
            # Add to integration history
            for summary in thread_summaries:
                if "integrated_at" in summary:
                    integration_history.append({
                        "timestamp": summary["integrated_at"],
                        "agent": summary.get("agent", "unknown"),
                        "thread_id": summary["thread_id"],
                        "plan_step": summary.get("plan_step"),
                        "integration_type": summary.get("integration_type", "unknown"),
                        "summary": summary.get("summary", "")
                    })
        
        # Sort by timestamp
        integration_history.sort(key=lambda x: x.get("timestamp", ""))
        
        logger.info(f"Retrieved {len(integration_history)} integration events for loop {loop_id}")
        return integration_history
    
    except Exception as e:
        logger.error(f"Error getting plan integration history: {str(e)}")
        logger.error(traceback.format_exc())
        return []
