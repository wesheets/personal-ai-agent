"""
Thread Summarizer Module

This module provides functionality for generating concise summaries of nested comment threads
in the Promethios system. It analyzes thread content and creates summaries that capture
key points, decisions, and actionable insights.

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
logger = logging.getLogger("orchestrator.thread_summarizer")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import nested_comments module
try:
    from orchestrator.modules.nested_comments import get_thread_messages, update_thread_status
    NESTED_COMMENTS_AVAILABLE = True
    logger.info("Successfully imported nested_comments module")
except ImportError:
    NESTED_COMMENTS_AVAILABLE = False
    logger.warning("Failed to import nested_comments module, will use direct memory access")

def generate_thread_summary(
    memory: Dict[str, Any],
    thread_id: str,
    max_length: int = 500
) -> Optional[str]:
    """
    Generate a concise summary of a thread.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        max_length: Maximum length of the summary
        
    Returns:
        The generated summary or None if failed
    """
    try:
        logger.info(f"Generating summary for thread {thread_id}")
        
        # Get thread messages
        if NESTED_COMMENTS_AVAILABLE:
            thread_messages = get_thread_messages(memory, thread_id)
        else:
            # Direct memory access if nested_comments module not available
            if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
                logger.error(f"Thread {thread_id} not found")
                return None
            
            thread_messages = memory["thread_messages"][thread_id]
        
        if not thread_messages:
            logger.error(f"No messages found in thread {thread_id}")
            return None
        
        # Get root message
        root_message = thread_messages[0]
        
        # Get loop ID from root message
        loop_id = root_message["loop_id"]
        
        # Extract key information
        thread_topic = root_message["message"]
        participants = list(set([msg["agent"] for msg in thread_messages]))
        reply_count = len(thread_messages) - 1
        
        # Identify key messages (excluding root message)
        key_messages = []
        for msg in thread_messages[1:]:
            # Consider messages with certain characteristics as key messages
            # For example, longer messages, messages from certain agents, etc.
            if len(msg["message"]) > 100 or msg["agent"] in ["orchestrator", "cto"]:
                key_messages.append(msg)
        
        # Sort key messages by depth (ascending)
        key_messages.sort(key=lambda x: x["depth"])
        
        # Limit to top 3 key messages if there are more
        if len(key_messages) > 3:
            key_messages = key_messages[:3]
        
        # Generate summary
        summary_parts = []
        
        # Add thread topic
        summary_parts.append(f"Thread topic: {thread_topic[:100]}{'...' if len(thread_topic) > 100 else ''}")
        
        # Add participants
        summary_parts.append(f"Participants: {', '.join(participants)}")
        
        # Add reply count
        summary_parts.append(f"Replies: {reply_count}")
        
        # Add key points from key messages
        if key_messages:
            summary_parts.append("Key points:")
            for i, msg in enumerate(key_messages):
                point = f"- {msg['agent']}: {msg['message'][:100]}{'...' if len(msg['message']) > 100 else ''}"
                summary_parts.append(point)
        
        # Check if thread is actionable
        if root_message.get("actionable", False):
            summary_parts.append("This thread contains actionable insights for plan revision.")
        
        # Join summary parts
        summary = "\n".join(summary_parts)
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length - 3] + "..."
        
        logger.info(f"Generated summary for thread {thread_id}")
        return summary
    
    except Exception as e:
        logger.error(f"Error generating thread summary: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def summarize_and_close_thread(
    memory: Dict[str, Any],
    thread_id: str,
    agent: str,
    max_length: int = 500
) -> bool:
    """
    Generate a summary for a thread and close it.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        agent: The agent closing the thread
        max_length: Maximum length of the summary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Summarizing and closing thread {thread_id}")
        
        # Generate summary
        summary = generate_thread_summary(memory, thread_id, max_length)
        
        if not summary:
            logger.error(f"Failed to generate summary for thread {thread_id}")
            return False
        
        # Update thread status to closed with summary
        if NESTED_COMMENTS_AVAILABLE:
            update_result = update_thread_status(
                memory=memory,
                thread_id=thread_id,
                status="closed",
                summary=summary,
                agent=agent
            )
            
            if not update_result:
                logger.error(f"Failed to update thread status to closed")
                return False
        else:
            # Direct memory access if nested_comments module not available
            if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
                logger.error(f"Thread {thread_id} not found")
                return False
            
            # Get thread messages
            thread_messages = memory["thread_messages"][thread_id]
            
            # Get root message
            root_message = thread_messages[0]
            
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
                    loop_threads[thread_id]["summary"] = summary
                    found = True
                    break
            
            if not found:
                logger.error(f"Thread {thread_id} not found in thread history")
                return False
            
            # Update root message status and summary
            root_message["status"] = "closed"
            root_message["summary"] = summary
            
            # Update thread metadata
            if "thread_metadata" in root_message and root_message["thread_metadata"]:
                root_message["thread_metadata"]["last_updated_at"] = timestamp
            
            # Add to loop trace if exists
            if "loop_trace" in memory and loop_id in memory["loop_trace"]:
                if "thread_activity" not in memory["loop_trace"][loop_id]:
                    memory["loop_trace"][loop_id]["thread_activity"] = []
                
                memory["loop_trace"][loop_id]["thread_activity"].append({
                    "action": "thread_closed",
                    "thread_id": thread_id,
                    "agent": agent,
                    "timestamp": timestamp,
                    "summary": summary
                })
            
            # Add to chat messages if requested
            if "chat_messages" in memory:
                memory["chat_messages"].append({
                    "role": "orchestrator",
                    "agent": agent,
                    "message": f"🔵 Thread closed: {root_message['message'][:100]}{'...' if len(root_message['message']) > 100 else ''}\n\nSummary: {summary}",
                    "loop": loop_id,
                    "timestamp": timestamp,
                    "thread_id": thread_id
                })
        
        logger.info(f"Summarized and closed thread {thread_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error summarizing and closing thread: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def get_thread_summaries_for_loop(
    memory: Dict[str, Any],
    loop_id: int
) -> List[Dict[str, Any]]:
    """
    Get summaries of all closed threads for a specific loop.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        
    Returns:
        List of thread summaries
    """
    try:
        logger.info(f"Getting thread summaries for loop {loop_id}")
        
        # Check if loop exists in thread history
        if "thread_history" not in memory or loop_id not in memory["thread_history"]:
            logger.info(f"No threads found for loop {loop_id}")
            return []
        
        # Get threads for loop
        loop_threads = memory["thread_history"][loop_id]
        
        # Initialize summaries list
        summaries = []
        
        # Iterate through threads
        for thread_id, thread_meta in loop_threads.items():
            # Only include closed, integrated, or discarded threads with summaries
            if thread_meta["status"] in ["closed", "integrated", "discarded"] and thread_meta.get("summary"):
                # Get thread messages
                if "thread_messages" in memory and thread_id in memory["thread_messages"]:
                    root_message = memory["thread_messages"][thread_id][0]
                    
                    # Create summary object
                    summary_obj = {
                        "thread_id": thread_id,
                        "status": thread_meta["status"],
                        "created_at": thread_meta["created_at"],
                        "closed_at": thread_meta["last_updated_at"],
                        "creator": thread_meta["creator"],
                        "participants": thread_meta["participants"],
                        "reply_count": thread_meta["reply_count"],
                        "summary": thread_meta["summary"],
                        "topic": root_message["message"][:100] + ("..." if len(root_message["message"]) > 100 else ""),
                        "actionable": thread_meta.get("actionable", False)
                    }
                    
                    # Add plan integration if available
                    if "plan_integration" in root_message and root_message["plan_integration"]:
                        summary_obj["plan_integration"] = root_message["plan_integration"]
                    
                    summaries.append(summary_obj)
        
        # Sort by closed_at (newest first)
        summaries.sort(key=lambda x: x["closed_at"], reverse=True)
        
        logger.info(f"Retrieved {len(summaries)} thread summaries for loop {loop_id}")
        return summaries
    
    except Exception as e:
        logger.error(f"Error getting thread summaries: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def get_actionable_threads(
    memory: Dict[str, Any],
    loop_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get all actionable threads that need plan revision.
    
    Args:
        memory: The memory dictionary
        loop_id: Optional loop ID to restrict search to
        
    Returns:
        List of actionable thread metadata
    """
    try:
        logger.info(f"Getting actionable threads{' for loop ' + str(loop_id) if loop_id is not None else ''}")
        
        # Check if thread history exists
        if "thread_history" not in memory:
            logger.info("No thread history found")
            return []
        
        # Initialize actionable threads list
        actionable_threads = []
        
        # Iterate through loops
        for thread_loop_id, loop_threads in memory["thread_history"].items():
            # Skip if loop ID is specified and doesn't match
            if loop_id is not None and thread_loop_id != loop_id:
                continue
            
            # Iterate through threads in loop
            for thread_id, thread_meta in loop_threads.items():
                # Check if thread is actionable and not yet integrated
                if thread_meta.get("actionable", False) and thread_meta["status"] != "integrated":
                    # Get thread messages
                    if "thread_messages" in memory and thread_id in memory["thread_messages"]:
                        root_message = memory["thread_messages"][thread_id][0]
                        
                        # Create actionable thread object
                        actionable_thread = {
                            "thread_id": thread_id,
                            "loop_id": thread_loop_id,
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
        
        # Sort by last_updated_at (newest first)
        actionable_threads.sort(key=lambda x: x["last_updated_at"], reverse=True)
        
        logger.info(f"Retrieved {len(actionable_threads)} actionable threads")
        return actionable_threads
    
    except Exception as e:
        logger.error(f"Error getting actionable threads: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def batch_summarize_threads(
    memory: Dict[str, Any],
    loop_id: int,
    agent: str = "orchestrator",
    max_threads: int = 10
) -> Dict[str, Any]:
    """
    Batch summarize all open threads for a loop.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        agent: The agent performing the summarization
        max_threads: Maximum number of threads to summarize
        
    Returns:
        Dictionary with results of the batch summarization
    """
    try:
        logger.info(f"Batch summarizing threads for loop {loop_id}")
        
        # Check if loop exists in thread history
        if "thread_history" not in memory or loop_id not in memory["thread_history"]:
            logger.info(f"No threads found for loop {loop_id}")
            return {"success": True, "summarized": 0, "failed": 0, "skipped": 0}
        
        # Get threads for loop
        loop_threads = memory["thread_history"][loop_id]
        
        # Initialize counters
        summarized = 0
        failed = 0
        skipped = 0
        
        # Iterate through threads
        for thread_id, thread_meta in loop_threads.items():
            # Only summarize open threads
            if thread_meta["status"] == "open":
                # Skip if max threads reached
                if summarized >= max_threads:
                    skipped += 1
                    continue
                
                # Summarize and close thread
                result = summarize_and_close_thread(
                    memory=memory,
                    thread_id=thread_id,
                    agent=agent
                )
                
                if result:
                    summarized += 1
                else:
                    failed += 1
            else:
                skipped += 1
        
        logger.info(f"Batch summarized {summarized} threads for loop {loop_id} (failed: {failed}, skipped: {skipped})")
        return {
            "success": True,
            "summarized": summarized,
            "failed": failed,
            "skipped": skipped
        }
    
    except Exception as e:
        logger.error(f"Error batch summarizing threads: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "summarized": 0,
            "failed": 0,
            "skipped": 0
        }
