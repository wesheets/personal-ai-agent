"""
Nested Comments Module

This module provides functionality for creating and managing nested comment threads
in the Promethios system. It enables structured conversations with parent-child
relationships, thread lifecycle management, and integration with the memory system.

Created for Phase 11.3.1 Nested Comments + Thread Logic implementation.
"""

import logging
import uuid
import datetime
import json
import hashlib
from typing import Dict, List, Any, Optional, Union
import traceback
import os
import sys

# Configure logging
logger = logging.getLogger("orchestrator.nested_comments")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import schema validator
try:
    from orchestrator.modules.schema_validator import validate_against_schema
    VALIDATOR_AVAILABLE = True
    logger.info("Successfully imported schema validator")
except ImportError:
    VALIDATOR_AVAILABLE = False
    logger.warning("Failed to import schema validator, validation will be skipped")

def create_thread(
    memory: Dict[str, Any],
    loop_id: int,
    agent: str,
    role: str,
    message: str,
    file: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new thread with a root message.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        agent: The agent creating the thread
        role: The role of the message creator
        message: The content of the message
        file: Optional file attachment
        tags: Optional tags for categorizing the thread
        
    Returns:
        The created thread message object
    """
    try:
        logger.info(f"Creating new thread for loop {loop_id} by {agent}")
        
        # Generate UUIDs for message and thread
        message_id = str(uuid.uuid4())
        thread_id = str(uuid.uuid4())
        
        # Generate topic hash for future reference
        topic_hash = hashlib.md5(message.encode()).hexdigest()
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Initialize thread message
        thread_message = {
            "message_id": message_id,
            "loop_id": loop_id,
            "thread_id": thread_id,
            "parent_id": None,  # Root message has no parent
            "agent": agent,
            "role": role,
            "message": message,
            "timestamp": timestamp,
            "depth": 0,  # Root message has depth 0
            "status": "open",
            "file": file,
            "summary": None,
            "actionable": False,
            "tags": tags or [],
            "topic_hash": topic_hash,
            "plan_integration": None,
            "thread_metadata": {
                "created_at": timestamp,
                "last_updated_at": timestamp,
                "reply_count": 0,
                "participants": [agent]
            }
        }
        
        # Validate against schema if validator is available
        if VALIDATOR_AVAILABLE:
            schema_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "schemas", "orchestrator", "nested_message.schema.json"
            )
            validation_result = validate_against_schema(thread_message, schema_path)
            if not validation_result["valid"]:
                logger.error(f"Thread message validation failed: {validation_result['errors']}")
                return None
        
        # Initialize thread history in memory if not exists
        if "thread_history" not in memory:
            memory["thread_history"] = {}
        
        # Initialize thread messages in memory if not exists
        if "thread_messages" not in memory:
            memory["thread_messages"] = {}
        
        # Initialize thread for this loop if not exists
        if loop_id not in memory["thread_history"]:
            memory["thread_history"][loop_id] = {}
        
        # Add thread to memory
        memory["thread_history"][loop_id][thread_id] = {
            "created_at": timestamp,
            "last_updated_at": timestamp,
            "status": "open",
            "creator": agent,
            "topic_hash": topic_hash,
            "reply_count": 0,
            "participants": [agent],
            "summary": None,
            "actionable": False,
            "tags": tags or []
        }
        
        # Add message to thread messages
        if thread_id not in memory["thread_messages"]:
            memory["thread_messages"][thread_id] = []
        
        memory["thread_messages"][thread_id].append(thread_message)
        
        # Add to loop trace if exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"]:
            if "thread_activity" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_activity"] = []
            
            memory["loop_trace"][loop_id]["thread_activity"].append({
                "action": "thread_created",
                "thread_id": thread_id,
                "agent": agent,
                "timestamp": timestamp,
                "message_preview": message[:100] + ("..." if len(message) > 100 else "")
            })
        
        # Add to chat messages if requested
        if "chat_messages" in memory:
            memory["chat_messages"].append({
                "role": role,
                "agent": agent,
                "message": f"🧵 Started a new thread: {message[:100]}{'...' if len(message) > 100 else ''}",
                "loop": loop_id,
                "timestamp": timestamp,
                "thread_id": thread_id
            })
        
        logger.info(f"Created new thread {thread_id} for loop {loop_id}")
        return thread_message
    
    except Exception as e:
        logger.error(f"Error creating thread: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def reply_to_thread(
    memory: Dict[str, Any],
    thread_id: str,
    agent: str,
    role: str,
    message: str,
    parent_id: Optional[str] = None,
    file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Reply to an existing thread.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        agent: The agent creating the reply
        role: The role of the message creator
        message: The content of the message
        parent_id: Optional parent message ID (defaults to latest message if None)
        file: Optional file attachment
        
    Returns:
        The created reply message object
    """
    try:
        logger.info(f"Creating reply to thread {thread_id} by {agent}")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found")
            return None
        
        # Get thread messages
        thread_messages = memory["thread_messages"][thread_id]
        
        # Find parent message
        parent_message = None
        if parent_id:
            for msg in thread_messages:
                if msg["message_id"] == parent_id:
                    parent_message = msg
                    break
            
            if not parent_message:
                logger.error(f"Parent message {parent_id} not found in thread {thread_id}")
                return None
        else:
            # Default to latest message as parent
            parent_message = thread_messages[-1]
            parent_id = parent_message["message_id"]
        
        # Get loop ID from parent message
        loop_id = parent_message["loop_id"]
        
        # Generate UUID for message
        message_id = str(uuid.uuid4())
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Calculate depth (parent depth + 1)
        depth = parent_message["depth"] + 1
        
        # Initialize reply message
        reply_message = {
            "message_id": message_id,
            "loop_id": loop_id,
            "thread_id": thread_id,
            "parent_id": parent_id,
            "agent": agent,
            "role": role,
            "message": message,
            "timestamp": timestamp,
            "depth": depth,
            "status": "open",
            "file": file,
            "summary": None,
            "actionable": False,
            "tags": [],
            "topic_hash": parent_message["topic_hash"],
            "plan_integration": None,
            "thread_metadata": None  # Only root message has metadata
        }
        
        # Validate against schema if validator is available
        if VALIDATOR_AVAILABLE:
            schema_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "schemas", "orchestrator", "nested_message.schema.json"
            )
            validation_result = validate_against_schema(reply_message, schema_path)
            if not validation_result["valid"]:
                logger.error(f"Reply message validation failed: {validation_result['errors']}")
                return None
        
        # Add message to thread messages
        memory["thread_messages"][thread_id].append(reply_message)
        
        # Update thread metadata
        for loop_threads in memory["thread_history"].values():
            if thread_id in loop_threads:
                loop_threads[thread_id]["last_updated_at"] = timestamp
                loop_threads[thread_id]["reply_count"] += 1
                
                if agent not in loop_threads[thread_id]["participants"]:
                    loop_threads[thread_id]["participants"].append(agent)
                break
        
        # Update root message metadata
        root_message = thread_messages[0]
        if "thread_metadata" in root_message and root_message["thread_metadata"]:
            root_message["thread_metadata"]["last_updated_at"] = timestamp
            root_message["thread_metadata"]["reply_count"] += 1
            
            if agent not in root_message["thread_metadata"]["participants"]:
                root_message["thread_metadata"]["participants"].append(agent)
        
        # Add to loop trace if exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"]:
            if "thread_activity" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_activity"] = []
            
            memory["loop_trace"][loop_id]["thread_activity"].append({
                "action": "thread_reply",
                "thread_id": thread_id,
                "message_id": message_id,
                "parent_id": parent_id,
                "agent": agent,
                "timestamp": timestamp,
                "message_preview": message[:100] + ("..." if len(message) > 100 else ""),
                "depth": depth
            })
        
        # Add to chat messages if requested
        if "chat_messages" in memory:
            memory["chat_messages"].append({
                "role": role,
                "agent": agent,
                "message": f"↪️ Replied to thread: {message[:100]}{'...' if len(message) > 100 else ''}",
                "loop": loop_id,
                "timestamp": timestamp,
                "thread_id": thread_id,
                "parent_id": parent_id,
                "depth": depth
            })
        
        logger.info(f"Created reply {message_id} to thread {thread_id}")
        return reply_message
    
    except Exception as e:
        logger.error(f"Error replying to thread: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def get_thread_messages(
    memory: Dict[str, Any],
    thread_id: str
) -> List[Dict[str, Any]]:
    """
    Get all messages in a thread.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        
    Returns:
        List of messages in the thread
    """
    try:
        logger.info(f"Getting messages for thread {thread_id}")
        
        # Check if thread exists
        if "thread_messages" not in memory or thread_id not in memory["thread_messages"]:
            logger.error(f"Thread {thread_id} not found")
            return []
        
        # Return thread messages
        return memory["thread_messages"][thread_id]
    
    except Exception as e:
        logger.error(f"Error getting thread messages: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def get_threads_for_loop(
    memory: Dict[str, Any],
    loop_id: int
) -> Dict[str, Dict[str, Any]]:
    """
    Get all threads for a specific loop.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        
    Returns:
        Dictionary of thread IDs to thread metadata
    """
    try:
        logger.info(f"Getting threads for loop {loop_id}")
        
        # Check if loop exists in thread history
        if "thread_history" not in memory or loop_id not in memory["thread_history"]:
            logger.info(f"No threads found for loop {loop_id}")
            return {}
        
        # Return threads for loop
        return memory["thread_history"][loop_id]
    
    except Exception as e:
        logger.error(f"Error getting threads for loop: {str(e)}")
        logger.error(traceback.format_exc())
        return {}

def update_thread_status(
    memory: Dict[str, Any],
    thread_id: str,
    status: str,
    summary: Optional[str] = None,
    agent: Optional[str] = None
) -> bool:
    """
    Update the status of a thread.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        status: The new status (open, closed, integrated, discarded)
        summary: Optional summary for closed threads
        agent: The agent updating the status
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Updating status of thread {thread_id} to {status}")
        
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
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Update thread status in thread history
        found = False
        for loop_threads in memory["thread_history"].values():
            if thread_id in loop_threads:
                loop_threads[thread_id]["status"] = status
                loop_threads[thread_id]["last_updated_at"] = timestamp
                
                if summary:
                    loop_threads[thread_id]["summary"] = summary
                
                found = True
                break
        
        if not found:
            logger.error(f"Thread {thread_id} not found in thread history")
            return False
        
        # Update root message status
        root_message["status"] = status
        
        # Update root message summary if provided
        if summary:
            root_message["summary"] = summary
        
        # Update thread metadata
        if "thread_metadata" in root_message and root_message["thread_metadata"]:
            root_message["thread_metadata"]["last_updated_at"] = timestamp
        
        # Add to loop trace if exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"]:
            if "thread_activity" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_activity"] = []
            
            trace_entry = {
                "action": f"thread_{status}",
                "thread_id": thread_id,
                "timestamp": timestamp
            }
            
            if agent:
                trace_entry["agent"] = agent
            
            if summary:
                trace_entry["summary"] = summary
            
            memory["loop_trace"][loop_id]["thread_activity"].append(trace_entry)
        
        # Add to chat messages if requested
        if "chat_messages" in memory:
            status_emoji = {
                "open": "🟢",
                "closed": "🔵",
                "integrated": "✅",
                "discarded": "❌"
            }.get(status, "🔄")
            
            chat_message = {
                "role": "orchestrator",
                "agent": agent or "orchestrator",
                "message": f"{status_emoji} Thread {status}: {root_message['message'][:100]}{'...' if len(root_message['message']) > 100 else ''}",
                "loop": loop_id,
                "timestamp": timestamp,
                "thread_id": thread_id
            }
            
            if summary:
                chat_message["message"] += f"\n\nSummary: {summary}"
            
            memory["chat_messages"].append(chat_message)
        
        logger.info(f"Updated status of thread {thread_id} to {status}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating thread status: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def mark_thread_for_plan_revision(
    memory: Dict[str, Any],
    thread_id: str,
    agent: str
) -> bool:
    """
    Mark a thread as containing actionable insights for plan revision.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        agent: The agent marking the thread
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Marking thread {thread_id} for plan revision by {agent}")
        
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
            
            memory["loop_trace"][loop_id]["thread_activity"].append({
                "action": "thread_marked_actionable",
                "thread_id": thread_id,
                "agent": agent,
                "timestamp": timestamp
            })
            
            # Add to plan deviations if exists
            if "plan_deviations" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["plan_deviations"] = []
            
            memory["loop_trace"][loop_id]["plan_deviations"].append({
                "type": "thread_insight",
                "thread_id": thread_id,
                "agent": agent,
                "timestamp": timestamp,
                "message": f"Thread contains actionable insights for plan revision: {root_message['message'][:100]}{'...' if len(root_message['message']) > 100 else ''}"
            })
        
        # Add to chat messages if requested
        if "chat_messages" in memory:
            memory["chat_messages"].append({
                "role": "orchestrator",
                "agent": agent,
                "message": f"🔍 Thread marked for plan revision: {root_message['message'][:100]}{'...' if len(root_message['message']) > 100 else ''}",
                "loop": loop_id,
                "timestamp": timestamp,
                "thread_id": thread_id
            })
        
        logger.info(f"Marked thread {thread_id} for plan revision")
        return True
    
    except Exception as e:
        logger.error(f"Error marking thread for plan revision: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def find_similar_threads(
    memory: Dict[str, Any],
    message: str,
    loop_id: Optional[int] = None,
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Find threads with similar topics to the given message.
    
    Args:
        memory: The memory dictionary
        message: The message to find similar threads for
        loop_id: Optional loop ID to restrict search to
        limit: Maximum number of similar threads to return
        
    Returns:
        List of similar thread metadata
    """
    try:
        logger.info(f"Finding similar threads for message: {message[:50]}...")
        
        # Generate topic hash for message
        topic_hash = hashlib.md5(message.encode()).hexdigest()
        
        # Initialize result list
        similar_threads = []
        
        # Check if thread history exists
        if "thread_history" not in memory:
            logger.info("No thread history found")
            return []
        
        # Iterate through loops
        for thread_loop_id, loop_threads in memory["thread_history"].items():
            # Skip if loop ID is specified and doesn't match
            if loop_id is not None and thread_loop_id != loop_id:
                continue
            
            # Iterate through threads in loop
            for thread_id, thread_meta in loop_threads.items():
                # Check if topic hash matches
                if thread_meta["topic_hash"] == topic_hash:
                    # Add thread to result list
                    similar_threads.append({
                        "thread_id": thread_id,
                        "loop_id": thread_loop_id,
                        "created_at": thread_meta["created_at"],
                        "status": thread_meta["status"],
                        "creator": thread_meta["creator"],
                        "reply_count": thread_meta["reply_count"],
                        "participants": thread_meta["participants"],
                        "summary": thread_meta["summary"],
                        "similarity": 1.0  # Exact match
                    })
                else:
                    # TODO: Implement fuzzy matching for topic similarity
                    # For now, just check if message contains similar words
                    message_words = set(message.lower().split())
                    
                    # Get root message for this thread
                    if "thread_messages" in memory and thread_id in memory["thread_messages"]:
                        root_message = memory["thread_messages"][thread_id][0]["message"]
                        root_words = set(root_message.lower().split())
                        
                        # Calculate word overlap
                        if message_words and root_words:
                            overlap = len(message_words.intersection(root_words))
                            similarity = overlap / max(len(message_words), len(root_words))
                            
                            # Add thread if similarity is above threshold
                            if similarity > 0.3:
                                similar_threads.append({
                                    "thread_id": thread_id,
                                    "loop_id": thread_loop_id,
                                    "created_at": thread_meta["created_at"],
                                    "status": thread_meta["status"],
                                    "creator": thread_meta["creator"],
                                    "reply_count": thread_meta["reply_count"],
                                    "participants": thread_meta["participants"],
                                    "summary": thread_meta["summary"],
                                    "similarity": similarity
                                })
        
        # Sort by similarity (highest first)
        similar_threads.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Return top N results
        return similar_threads[:limit]
    
    except Exception as e:
        logger.error(f"Error finding similar threads: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def integrate_thread_with_plan(
    memory: Dict[str, Any],
    thread_id: str,
    plan_step: Optional[int] = None,
    integration_type: str = "modification",
    integration_summary: str = "",
    agent: Optional[str] = None
) -> bool:
    """
    Integrate a thread into the plan.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        plan_step: Optional plan step that was affected
        integration_type: How the thread was integrated (addition, modification, removal, clarification)
        integration_summary: Summary of how the thread was integrated
        agent: The agent performing the integration
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Integrating thread {thread_id} into plan")
        
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
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Create plan integration object
        plan_integration = {
            "integrated_at": timestamp,
            "plan_step": plan_step,
            "integration_type": integration_type,
            "integration_summary": integration_summary
        }
        
        # Update thread status to integrated
        update_result = update_thread_status(
            memory=memory,
            thread_id=thread_id,
            status="integrated",
            summary=integration_summary,
            agent=agent
        )
        
        if not update_result:
            logger.error(f"Failed to update thread status to integrated")
            return False
        
        # Update root message plan integration
        root_message["plan_integration"] = plan_integration
        
        # Add to loop trace if exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"]:
            if "thread_activity" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_activity"] = []
            
            trace_entry = {
                "action": "thread_integrated",
                "thread_id": thread_id,
                "timestamp": timestamp,
                "plan_step": plan_step,
                "integration_type": integration_type,
                "integration_summary": integration_summary
            }
            
            if agent:
                trace_entry["agent"] = agent
            
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
                "agent": agent or "orchestrator"
            })
        
        # Add to chat messages if requested
        if "chat_messages" in memory:
            step_text = f" (step {plan_step})" if plan_step is not None else ""
            
            memory["chat_messages"].append({
                "role": "orchestrator",
                "agent": agent or "orchestrator",
                "message": f"🔄 Thread integrated into plan{step_text}: {integration_summary}",
                "loop": loop_id,
                "timestamp": timestamp,
                "thread_id": thread_id
            })
        
        logger.info(f"Integrated thread {thread_id} into plan")
        return True
    
    except Exception as e:
        logger.error(f"Error integrating thread with plan: {str(e)}")
        logger.error(traceback.format_exc())
        return False
