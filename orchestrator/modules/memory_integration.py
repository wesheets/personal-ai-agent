"""
Memory Integration Module for Nested Comments

This module provides functionality for integrating nested comments with the memory system.
It ensures proper storage and retrieval of thread data, including thread history,
messages, and summaries.

Created for Phase 11.3.1 Nested Comments + Thread Logic implementation.
"""

import logging
import datetime
import json
import os
import sys
from typing import Dict, List, Any, Optional, Union
import traceback
import uuid

# Configure logging
logger = logging.getLogger("orchestrator.memory_integration")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import nested_comments and thread_summarizer modules
try:
    from orchestrator.modules.nested_comments import get_thread_messages, get_threads_for_loop
    from orchestrator.modules.thread_summarizer import get_thread_summaries_for_loop
    MODULES_AVAILABLE = True
    logger.info("Successfully imported nested_comments and thread_summarizer modules")
except ImportError:
    MODULES_AVAILABLE = False
    logger.warning("Failed to import required modules, will use direct memory access")

def initialize_thread_memory(memory: Dict[str, Any]) -> bool:
    """
    Initialize memory structures for thread storage.
    
    Args:
        memory: The memory dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Initializing thread memory structures")
        
        # Initialize thread history if not exists
        if "thread_history" not in memory:
            memory["thread_history"] = {}
            logger.info("Initialized thread_history in memory")
        
        # Initialize thread messages if not exists
        if "thread_messages" not in memory:
            memory["thread_messages"] = {}
            logger.info("Initialized thread_messages in memory")
        
        # Initialize thread summaries if not exists
        if "thread_summaries" not in memory:
            memory["thread_summaries"] = {}
            logger.info("Initialized thread_summaries in memory")
        
        return True
    
    except Exception as e:
        logger.error(f"Error initializing thread memory: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def store_thread_in_memory(
    memory: Dict[str, Any],
    thread_id: str,
    thread_data: Dict[str, Any]
) -> bool:
    """
    Store thread data in memory.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        thread_data: The thread data to store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Storing thread {thread_id} in memory")
        
        # Initialize memory structures if needed
        initialize_thread_memory(memory)
        
        # Get loop ID from thread data
        loop_id = thread_data.get("loop_id")
        
        if not loop_id:
            logger.error(f"Thread data missing loop_id: {thread_data}")
            return False
        
        # Initialize thread history for this loop if not exists
        if loop_id not in memory["thread_history"]:
            memory["thread_history"][loop_id] = {}
        
        # Store thread metadata in thread history
        memory["thread_history"][loop_id][thread_id] = {
            "created_at": thread_data.get("timestamp", datetime.datetime.now().isoformat()),
            "last_updated_at": thread_data.get("timestamp", datetime.datetime.now().isoformat()),
            "status": thread_data.get("status", "open"),
            "creator": thread_data.get("agent", "unknown"),
            "topic_hash": thread_data.get("topic_hash"),
            "reply_count": 0,
            "participants": [thread_data.get("agent", "unknown")],
            "summary": thread_data.get("summary"),
            "actionable": thread_data.get("actionable", False),
            "tags": thread_data.get("tags", [])
        }
        
        # Initialize thread messages for this thread if not exists
        if thread_id not in memory["thread_messages"]:
            memory["thread_messages"][thread_id] = []
        
        # Store thread message
        memory["thread_messages"][thread_id].append(thread_data)
        
        # Add to loop trace if exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"]:
            if "thread_activity" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_activity"] = []
            
            memory["loop_trace"][loop_id]["thread_activity"].append({
                "action": "thread_stored",
                "thread_id": thread_id,
                "agent": thread_data.get("agent", "unknown"),
                "timestamp": thread_data.get("timestamp", datetime.datetime.now().isoformat()),
                "message_preview": thread_data.get("message", "")[:100] + ("..." if len(thread_data.get("message", "")) > 100 else "")
            })
        
        logger.info(f"Stored thread {thread_id} in memory")
        return True
    
    except Exception as e:
        logger.error(f"Error storing thread in memory: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def store_reply_in_memory(
    memory: Dict[str, Any],
    thread_id: str,
    reply_data: Dict[str, Any]
) -> bool:
    """
    Store reply data in memory.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        reply_data: The reply data to store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Storing reply to thread {thread_id} in memory")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found in memory")
            return False
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Get root message
        root_message = thread_messages[0]
        
        # Get loop ID from root message
        loop_id = root_message["loop_id"]
        
        # Store reply message
        memory["thread_messages"][thread_id].append(reply_data)
        
        # Update thread metadata
        for loop_threads in memory["thread_history"].values():
            if thread_id in loop_threads:
                loop_threads[thread_id]["last_updated_at"] = reply_data.get("timestamp", datetime.datetime.now().isoformat())
                loop_threads[thread_id]["reply_count"] += 1
                
                if reply_data.get("agent") not in loop_threads[thread_id]["participants"]:
                    loop_threads[thread_id]["participants"].append(reply_data.get("agent"))
                break
        
        # Update root message metadata
        if "thread_metadata" in root_message and root_message["thread_metadata"]:
            root_message["thread_metadata"]["last_updated_at"] = reply_data.get("timestamp", datetime.datetime.now().isoformat())
            root_message["thread_metadata"]["reply_count"] += 1
            
            if reply_data.get("agent") not in root_message["thread_metadata"]["participants"]:
                root_message["thread_metadata"]["participants"].append(reply_data.get("agent"))
        
        # Add to loop trace if exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"]:
            if "thread_activity" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_activity"] = []
            
            memory["loop_trace"][loop_id]["thread_activity"].append({
                "action": "reply_stored",
                "thread_id": thread_id,
                "message_id": reply_data.get("message_id"),
                "parent_id": reply_data.get("parent_id"),
                "agent": reply_data.get("agent", "unknown"),
                "timestamp": reply_data.get("timestamp", datetime.datetime.now().isoformat()),
                "message_preview": reply_data.get("message", "")[:100] + ("..." if len(reply_data.get("message", "")) > 100 else ""),
                "depth": reply_data.get("depth", 0)
            })
        
        logger.info(f"Stored reply to thread {thread_id} in memory")
        return True
    
    except Exception as e:
        logger.error(f"Error storing reply in memory: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def store_thread_summary_in_memory(
    memory: Dict[str, Any],
    thread_id: str,
    summary: str,
    agent: str
) -> bool:
    """
    Store thread summary in memory.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        summary: The thread summary
        agent: The agent creating the summary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Storing summary for thread {thread_id} in memory")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found in memory")
            return False
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Get root message
        root_message = thread_messages[0]
        
        # Get loop ID from root message
        loop_id = root_message["loop_id"]
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Update thread summary in thread history
        found = False
        for loop_threads in memory["thread_history"].values():
            if thread_id in loop_threads:
                loop_threads[thread_id]["summary"] = summary
                loop_threads[thread_id]["last_updated_at"] = timestamp
                found = True
                break
        
        if not found:
            logger.error(f"Thread {thread_id} not found in thread history")
            return False
        
        # Update root message summary
        root_message["summary"] = summary
        
        # Initialize thread summaries for this loop if not exists
        if "thread_summaries" not in memory:
            memory["thread_summaries"] = {}
        
        if loop_id not in memory["thread_summaries"]:
            memory["thread_summaries"][loop_id] = {}
        
        # Store thread summary
        memory["thread_summaries"][loop_id][thread_id] = {
            "thread_id": thread_id,
            "summary": summary,
            "created_at": timestamp,
            "agent": agent,
            "status": root_message.get("status", "open")
        }
        
        # Add to loop trace if exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"]:
            if "thread_activity" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_activity"] = []
            
            memory["loop_trace"][loop_id]["thread_activity"].append({
                "action": "summary_stored",
                "thread_id": thread_id,
                "agent": agent,
                "timestamp": timestamp,
                "summary": summary
            })
            
            # Add to thread summaries if not exists
            if "thread_summaries" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_summaries"] = []
            
            memory["loop_trace"][loop_id]["thread_summaries"].append({
                "thread_id": thread_id,
                "created_at": timestamp,
                "agent": agent,
                "summary": summary,
                "status": root_message.get("status", "open")
            })
        
        logger.info(f"Stored summary for thread {thread_id} in memory")
        return True
    
    except Exception as e:
        logger.error(f"Error storing thread summary: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def retrieve_threads_from_memory(
    memory: Dict[str, Any],
    loop_id: Optional[int] = None,
    status: Optional[str] = None,
    agent: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Retrieve threads from memory with optional filtering.
    
    Args:
        memory: The memory dictionary
        loop_id: Optional loop ID to filter by
        status: Optional status to filter by
        agent: Optional agent to filter by
        limit: Maximum number of threads to return
        
    Returns:
        List of thread metadata
    """
    try:
        logger.info(f"Retrieving threads from memory (loop_id={loop_id}, status={status}, agent={agent})")
        
        # Check if thread history exists
        if "thread_history" not in memory:
            logger.info("No thread history found in memory")
            return []
        
        # Initialize result list
        threads = []
        
        # Iterate through loops
        for thread_loop_id, loop_threads in memory["thread_history"].items():
            # Skip if loop ID is specified and doesn't match
            if loop_id is not None and thread_loop_id != loop_id:
                continue
            
            # Iterate through threads in loop
            for thread_id, thread_meta in loop_threads.items():
                # Skip if status is specified and doesn't match
                if status is not None and thread_meta["status"] != status:
                    continue
                
                # Skip if agent is specified and not in participants
                if agent is not None and agent not in thread_meta["participants"]:
                    continue
                
                # Add thread to result list
                threads.append({
                    "thread_id": thread_id,
                    "loop_id": thread_loop_id,
                    **thread_meta
                })
        
        # Sort by last_updated_at (newest first)
        threads.sort(key=lambda x: x["last_updated_at"], reverse=True)
        
        # Limit results
        threads = threads[:limit]
        
        logger.info(f"Retrieved {len(threads)} threads from memory")
        return threads
    
    except Exception as e:
        logger.error(f"Error retrieving threads from memory: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def retrieve_thread_messages_from_memory(
    memory: Dict[str, Any],
    thread_id: str
) -> List[Dict[str, Any]]:
    """
    Retrieve all messages for a specific thread from memory.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        
    Returns:
        List of thread messages
    """
    try:
        logger.info(f"Retrieving messages for thread {thread_id} from memory")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found in memory")
            return []
        
        # Return thread messages
        return memory["thread_messages"][thread_id]
    
    except Exception as e:
        logger.error(f"Error retrieving thread messages: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def retrieve_thread_summaries_from_memory(
    memory: Dict[str, Any],
    loop_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Retrieve thread summaries from memory.
    
    Args:
        memory: The memory dictionary
        loop_id: Optional loop ID to filter by
        
    Returns:
        List of thread summaries
    """
    try:
        logger.info(f"Retrieving thread summaries from memory (loop_id={loop_id})")
        
        # Check if thread summaries exist
        if "thread_summaries" not in memory:
            logger.info("No thread summaries found in memory")
            return []
        
        # Initialize result list
        summaries = []
        
        # If loop ID is specified, return summaries for that loop
        if loop_id is not None:
            if loop_id not in memory["thread_summaries"]:
                logger.info(f"No thread summaries found for loop {loop_id}")
                return []
            
            # Iterate through thread summaries for loop
            for thread_id, summary in memory["thread_summaries"][loop_id].items():
                summaries.append(summary)
        else:
            # Iterate through all loops
            for loop_summaries in memory["thread_summaries"].values():
                # Iterate through thread summaries in loop
                for thread_id, summary in loop_summaries.items():
                    summaries.append(summary)
        
        # Sort by created_at (newest first)
        summaries.sort(key=lambda x: x["created_at"], reverse=True)
        
        logger.info(f"Retrieved {len(summaries)} thread summaries from memory")
        return summaries
    
    except Exception as e:
        logger.error(f"Error retrieving thread summaries: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def export_threads_to_chat_messages(
    memory: Dict[str, Any],
    loop_id: Optional[int] = None
) -> bool:
    """
    Export threads to chat messages for UI rendering.
    
    Args:
        memory: The memory dictionary
        loop_id: Optional loop ID to filter by
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Exporting threads to chat messages (loop_id={loop_id})")
        
        # Check if thread history exists
        if "thread_history" not in memory or "thread_messages" not in memory:
            logger.error("Thread history or messages not found in memory")
            return False
        
        # Check if chat messages exist
        if "chat_messages" not in memory:
            logger.warning("Chat messages not found in memory, initializing")
            memory["chat_messages"] = []
        
        # Get threads to export
        threads = []
        
        if loop_id is not None:
            # Get threads for specific loop
            if loop_id in memory["thread_history"]:
                for thread_id in memory["thread_history"][loop_id]:
                    if thread_id in memory["thread_messages"]:
                        threads.append(thread_id)
        else:
            # Get all threads
            for thread_id in memory["thread_messages"]:
                threads.append(thread_id)
        
        # Export each thread
        for thread_id in threads:
            thread_messages = memory["thread_messages"][thread_id]
            
            # Skip if no messages
            if not thread_messages:
                continue
            
            # Get root message
            root_message = thread_messages[0]
            
            # Create chat message for root message
            chat_message = {
                "role": root_message["role"],
                "agent": root_message["agent"],
                "message": root_message["message"],
                "loop": root_message["loop_id"],
                "timestamp": root_message["timestamp"],
                "thread_id": thread_id,
                "message_id": root_message["message_id"],
                "status": root_message["status"]
            }
            
            # Add summary if available
            if root_message.get("summary"):
                chat_message["summary"] = root_message["summary"]
            
            # Add file if available
            if root_message.get("file"):
                chat_message["file"] = root_message["file"]
            
            # Add to chat messages if not already exists
            message_exists = False
            for i, msg in enumerate(memory["chat_messages"]):
                if msg.get("message_id") == root_message["message_id"]:
                    # Update existing message
                    memory["chat_messages"][i] = chat_message
                    message_exists = True
                    break
            
            if not message_exists:
                memory["chat_messages"].append(chat_message)
            
            # Add replies as chat messages
            for reply in thread_messages[1:]:
                reply_chat_message = {
                    "role": reply["role"],
                    "agent": reply["agent"],
                    "message": reply["message"],
                    "loop": reply["loop_id"],
                    "timestamp": reply["timestamp"],
                    "thread_id": thread_id,
                    "message_id": reply["message_id"],
                    "parent_id": reply["parent_id"],
                    "depth": reply["depth"]
                }
                
                # Add file if available
                if reply.get("file"):
                    reply_chat_message["file"] = reply["file"]
                
                # Add to chat messages if not already exists
                message_exists = False
                for i, msg in enumerate(memory["chat_messages"]):
                    if msg.get("message_id") == reply["message_id"]:
                        # Update existing message
                        memory["chat_messages"][i] = reply_chat_message
                        message_exists = True
                        break
                
                if not message_exists:
                    memory["chat_messages"].append(reply_chat_message)
        
        # Sort chat messages by timestamp
        memory["chat_messages"].sort(key=lambda x: x.get("timestamp", ""))
        
        logger.info(f"Exported threads to chat messages")
        return True
    
    except Exception as e:
        logger.error(f"Error exporting threads to chat messages: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def import_chat_messages_to_threads(
    memory: Dict[str, Any],
    loop_id: Optional[int] = None
) -> bool:
    """
    Import chat messages to threads for storage.
    
    Args:
        memory: The memory dictionary
        loop_id: Optional loop ID to filter by
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Importing chat messages to threads (loop_id={loop_id})")
        
        # Check if chat messages exist
        if "chat_messages" not in memory:
            logger.error("Chat messages not found in memory")
            return False
        
        # Initialize memory structures if needed
        initialize_thread_memory(memory)
        
        # Get chat messages to import
        chat_messages = []
        
        if loop_id is not None:
            # Get messages for specific loop
            chat_messages = [msg for msg in memory["chat_messages"] if msg.get("loop") == loop_id]
        else:
            # Get all messages
            chat_messages = memory["chat_messages"]
        
        # Process root messages first (no parent_id)
        for msg in chat_messages:
            if not msg.get("parent_id") and msg.get("thread_id"):
                # Check if thread already exists
                thread_exists = False
                
                if msg["thread_id"] in memory["thread_messages"]:
                    thread_exists = True
                
                if not thread_exists:
                    # Create thread message
                    thread_message = {
                        "message_id": msg.get("message_id", str(uuid.uuid4())),
                        "loop_id": msg.get("loop"),
                        "thread_id": msg.get("thread_id"),
                        "parent_id": None,
                        "agent": msg.get("agent"),
                        "role": msg.get("role"),
                        "message": msg.get("message"),
                        "timestamp": msg.get("timestamp", datetime.datetime.now().isoformat()),
                        "depth": 0,
                        "status": msg.get("status", "open"),
                        "file": msg.get("file"),
                        "summary": msg.get("summary"),
                        "actionable": msg.get("actionable", False),
                        "tags": msg.get("tags", []),
                        "topic_hash": None,
                        "plan_integration": None,
                        "thread_metadata": {
                            "created_at": msg.get("timestamp", datetime.datetime.now().isoformat()),
                            "last_updated_at": msg.get("timestamp", datetime.datetime.now().isoformat()),
                            "reply_count": 0,
                            "participants": [msg.get("agent")]
                        }
                    }
                    
                    # Store thread in memory
                    store_thread_in_memory(memory, msg["thread_id"], thread_message)
        
        # Process replies (with parent_id)
        for msg in chat_messages:
            if msg.get("parent_id") and msg.get("thread_id"):
                # Check if thread exists
                if msg["thread_id"] in memory["thread_messages"]:
                    # Create reply message
                    reply_message = {
                        "message_id": msg.get("message_id", str(uuid.uuid4())),
                        "loop_id": msg.get("loop"),
                        "thread_id": msg.get("thread_id"),
                        "parent_id": msg.get("parent_id"),
                        "agent": msg.get("agent"),
                        "role": msg.get("role"),
                        "message": msg.get("message"),
                        "timestamp": msg.get("timestamp", datetime.datetime.now().isoformat()),
                        "depth": msg.get("depth", 1),
                        "status": "open",
                        "file": msg.get("file"),
                        "summary": None,
                        "actionable": False,
                        "tags": [],
                        "topic_hash": None,
                        "plan_integration": None,
                        "thread_metadata": None
                    }
                    
                    # Store reply in memory
                    store_reply_in_memory(memory, msg["thread_id"], reply_message)
        
        logger.info(f"Imported chat messages to threads")
        return True
    
    except Exception as e:
        logger.error(f"Error importing chat messages to threads: {str(e)}")
        logger.error(traceback.format_exc())
        return False
