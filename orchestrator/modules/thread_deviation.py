"""
Thread Deviation Memory Module

This module provides functionality for tracking historical deviations in threads
and analyzing patterns in thread discussions. It enables the system to learn from
past thread interactions and improve future thread management.

Created for Phase 11.3.1 Nested Comments + Thread Logic implementation.
"""

import logging
import datetime
import json
import os
import sys
from typing import Dict, List, Any, Optional, Union
import traceback
import hashlib

# Configure logging
logger = logging.getLogger("orchestrator.thread_deviation")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import required modules
try:
    from orchestrator.modules.nested_comments import get_thread_messages
    from orchestrator.modules.thread_summarizer import get_thread_summaries_for_loop
    MODULES_AVAILABLE = True
    logger.info("Successfully imported required modules")
except ImportError:
    MODULES_AVAILABLE = False
    logger.warning("Failed to import required modules, will use direct memory access")

def initialize_deviation_memory(memory: Dict[str, Any]) -> bool:
    """
    Initialize memory structures for thread deviation tracking.
    
    Args:
        memory: The memory dictionary
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Initializing thread deviation memory structures")
        
        # Initialize thread deviations if not exists
        if "thread_deviations" not in memory:
            memory["thread_deviations"] = {}
            logger.info("Initialized thread_deviations in memory")
        
        # Initialize deviation patterns if not exists
        if "deviation_patterns" not in memory:
            memory["deviation_patterns"] = {}
            logger.info("Initialized deviation_patterns in memory")
        
        return True
    
    except Exception as e:
        logger.error(f"Error initializing thread deviation memory: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def record_thread_deviation(
    memory: Dict[str, Any],
    thread_id: str,
    deviation_type: str,
    agent: str,
    description: str,
    severity: str = "medium",
    related_plan_step: Optional[int] = None
) -> bool:
    """
    Record a thread deviation event.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        deviation_type: Type of deviation (e.g., "off_topic", "plan_conflict", "scope_expansion")
        agent: The agent recording the deviation
        description: Description of the deviation
        severity: Severity level (low, medium, high)
        related_plan_step: Optional related plan step
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Recording thread deviation for thread {thread_id} by {agent}")
        
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
        
        # Initialize deviation memory if needed
        initialize_deviation_memory(memory)
        
        # Initialize thread deviations for this loop if not exists
        if loop_id not in memory["thread_deviations"]:
            memory["thread_deviations"][loop_id] = {}
        
        # Initialize thread deviations for this thread if not exists
        if thread_id not in memory["thread_deviations"][loop_id]:
            memory["thread_deviations"][loop_id][thread_id] = []
        
        # Create deviation event
        deviation_event = {
            "timestamp": timestamp,
            "agent": agent,
            "deviation_type": deviation_type,
            "description": description,
            "severity": severity,
            "related_plan_step": related_plan_step,
            "message_count": len(thread_messages),
            "participants": list(set([msg["agent"] for msg in thread_messages])),
            "resolved": False
        }
        
        # Add deviation event to thread deviations
        memory["thread_deviations"][loop_id][thread_id].append(deviation_event)
        
        # Add to loop trace if exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"]:
            if "thread_activity" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_activity"] = []
            
            trace_entry = {
                "action": "thread_deviation_recorded",
                "thread_id": thread_id,
                "agent": agent,
                "timestamp": timestamp,
                "deviation_type": deviation_type,
                "severity": severity,
                "description": description
            }
            
            if related_plan_step is not None:
                trace_entry["related_plan_step"] = related_plan_step
            
            memory["loop_trace"][loop_id]["thread_activity"].append(trace_entry)
            
            # Add to plan deviations if exists
            if "plan_deviations" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["plan_deviations"] = []
            
            deviation_entry = {
                "type": "thread_deviation",
                "thread_id": thread_id,
                "agent": agent,
                "timestamp": timestamp,
                "deviation_type": deviation_type,
                "severity": severity,
                "description": description
            }
            
            if related_plan_step is not None:
                deviation_entry["related_plan_step"] = related_plan_step
            
            memory["loop_trace"][loop_id]["plan_deviations"].append(deviation_entry)
        
        # Update deviation patterns
        update_deviation_patterns(memory, deviation_type, thread_messages)
        
        logger.info(f"Recorded thread deviation for thread {thread_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error recording thread deviation: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def resolve_thread_deviation(
    memory: Dict[str, Any],
    thread_id: str,
    deviation_index: int,
    agent: str,
    resolution_description: str
) -> bool:
    """
    Mark a thread deviation as resolved.
    
    Args:
        memory: The memory dictionary
        thread_id: The thread identifier
        deviation_index: Index of the deviation to resolve
        agent: The agent resolving the deviation
        resolution_description: Description of how the deviation was resolved
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Resolving thread deviation {deviation_index} for thread {thread_id} by {agent}")
        
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
        
        # Check if thread deviations exist
        if "thread_deviations" not in memory or loop_id not in memory["thread_deviations"] or thread_id not in memory["thread_deviations"][loop_id]:
            logger.error(f"No deviations found for thread {thread_id}")
            return False
        
        # Check if deviation index is valid
        if deviation_index >= len(memory["thread_deviations"][loop_id][thread_id]):
            logger.error(f"Deviation index {deviation_index} out of range")
            return False
        
        # Get deviation event
        deviation_event = memory["thread_deviations"][loop_id][thread_id][deviation_index]
        
        # Check if already resolved
        if deviation_event["resolved"]:
            logger.warning(f"Deviation already resolved")
            return True
        
        # Create timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Update deviation event
        deviation_event["resolved"] = True
        deviation_event["resolved_at"] = timestamp
        deviation_event["resolved_by"] = agent
        deviation_event["resolution_description"] = resolution_description
        
        # Add to loop trace if exists
        if "loop_trace" in memory and loop_id in memory["loop_trace"]:
            if "thread_activity" not in memory["loop_trace"][loop_id]:
                memory["loop_trace"][loop_id]["thread_activity"] = []
            
            memory["loop_trace"][loop_id]["thread_activity"].append({
                "action": "thread_deviation_resolved",
                "thread_id": thread_id,
                "agent": agent,
                "timestamp": timestamp,
                "deviation_type": deviation_event["deviation_type"],
                "resolution_description": resolution_description
            })
        
        logger.info(f"Resolved thread deviation {deviation_index} for thread {thread_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error resolving thread deviation: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def update_deviation_patterns(
    memory: Dict[str, Any],
    deviation_type: str,
    thread_messages: List[Dict[str, Any]]
) -> bool:
    """
    Update deviation patterns based on a new deviation event.
    
    Args:
        memory: The memory dictionary
        deviation_type: Type of deviation
        thread_messages: Messages in the thread
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Updating deviation patterns for type {deviation_type}")
        
        # Initialize deviation memory if needed
        initialize_deviation_memory(memory)
        
        # Initialize deviation pattern for this type if not exists
        if deviation_type not in memory["deviation_patterns"]:
            memory["deviation_patterns"][deviation_type] = {
                "count": 0,
                "common_agents": {},
                "common_words": {},
                "message_count_distribution": {},
                "participant_count_distribution": {}
            }
        
        # Update pattern
        pattern = memory["deviation_patterns"][deviation_type]
        
        # Increment count
        pattern["count"] += 1
        
        # Update common agents
        for msg in thread_messages:
            agent = msg["agent"]
            
            if agent not in pattern["common_agents"]:
                pattern["common_agents"][agent] = 0
            
            pattern["common_agents"][agent] += 1
        
        # Update common words
        all_text = " ".join([msg["message"] for msg in thread_messages])
        words = all_text.lower().split()
        
        for word in words:
            # Skip short words and common stop words
            if len(word) <= 2 or word in ["the", "and", "for", "that", "this", "with", "not", "are", "from"]:
                continue
            
            if word not in pattern["common_words"]:
                pattern["common_words"][word] = 0
            
            pattern["common_words"][word] += 1
        
        # Update message count distribution
        message_count = len(thread_messages)
        message_count_key = str(message_count)
        
        if message_count_key not in pattern["message_count_distribution"]:
            pattern["message_count_distribution"][message_count_key] = 0
        
        pattern["message_count_distribution"][message_count_key] += 1
        
        # Update participant count distribution
        participant_count = len(set([msg["agent"] for msg in thread_messages]))
        participant_count_key = str(participant_count)
        
        if participant_count_key not in pattern["participant_count_distribution"]:
            pattern["participant_count_distribution"][participant_count_key] = 0
        
        pattern["participant_count_distribution"][participant_count_key] += 1
        
        logger.info(f"Updated deviation patterns for type {deviation_type}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating deviation patterns: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def get_thread_deviations(
    memory: Dict[str, Any],
    thread_id: Optional[str] = None,
    loop_id: Optional[int] = None,
    deviation_type: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get thread deviations with optional filtering.
    
    Args:
        memory: The memory dictionary
        thread_id: Optional thread ID to filter by
        loop_id: Optional loop ID to filter by
        deviation_type: Optional deviation type to filter by
        resolved: Optional resolved status to filter by
        limit: Maximum number of deviations to return
        
    Returns:
        List of thread deviations
    """
    try:
        logger.info(f"Getting thread deviations (thread_id={thread_id}, loop_id={loop_id}, deviation_type={deviation_type}, resolved={resolved})")
        
        # Check if thread deviations exist
        if "thread_deviations" not in memory:
            logger.info("No thread deviations found in memory")
            return []
        
        # Initialize result list
        deviations = []
        
        # If thread ID is specified, get deviations for that thread
        if thread_id is not None:
            # Find thread in all loops
            for loop_deviations in memory["thread_deviations"].values():
                if thread_id in loop_deviations:
                    # Get thread deviations
                    thread_deviations = loop_deviations[thread_id]
                    
                    # Filter by deviation type if specified
                    if deviation_type is not None:
                        thread_deviations = [dev for dev in thread_deviations if dev["deviation_type"] == deviation_type]
                    
                    # Filter by resolved status if specified
                    if resolved is not None:
                        thread_deviations = [dev for dev in thread_deviations if dev["resolved"] == resolved]
                    
                    # Add thread ID to each deviation
                    for dev in thread_deviations:
                        dev_copy = dev.copy()
                        dev_copy["thread_id"] = thread_id
                        deviations.append(dev_copy)
                    
                    break
        
        # If loop ID is specified, get deviations for that loop
        elif loop_id is not None:
            if loop_id in memory["thread_deviations"]:
                # Iterate through threads in loop
                for thread_id, thread_deviations in memory["thread_deviations"][loop_id].items():
                    # Filter by deviation type if specified
                    filtered_deviations = thread_deviations
                    
                    if deviation_type is not None:
                        filtered_deviations = [dev for dev in filtered_deviations if dev["deviation_type"] == deviation_type]
                    
                    # Filter by resolved status if specified
                    if resolved is not None:
                        filtered_deviations = [dev for dev in filtered_deviations if dev["resolved"] == resolved]
                    
                    # Add thread ID to each deviation
                    for dev in filtered_deviations:
                        dev_copy = dev.copy()
                        dev_copy["thread_id"] = thread_id
                        deviations.append(dev_copy)
        
        # Otherwise, get all deviations
        else:
            # Iterate through all loops
            for loop_id, loop_deviations in memory["thread_deviations"].items():
                # Iterate through threads in loop
                for thread_id, thread_deviations in loop_deviations.items():
                    # Filter by deviation type if specified
                    filtered_deviations = thread_deviations
                    
                    if deviation_type is not None:
                        filtered_deviations = [dev for dev in filtered_deviations if dev["deviation_type"] == deviation_type]
                    
                    # Filter by resolved status if specified
                    if resolved is not None:
                        filtered_deviations = [dev for dev in filtered_deviations if dev["resolved"] == resolved]
                    
                    # Add thread ID and loop ID to each deviation
                    for dev in filtered_deviations:
                        dev_copy = dev.copy()
                        dev_copy["thread_id"] = thread_id
                        dev_copy["loop_id"] = loop_id
                        deviations.append(dev_copy)
        
        # Sort by timestamp (newest first)
        deviations.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit results
        deviations = deviations[:limit]
        
        logger.info(f"Retrieved {len(deviations)} thread deviations")
        return deviations
    
    except Exception as e:
        logger.error(f"Error getting thread deviations: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def get_deviation_patterns(
    memory: Dict[str, Any],
    deviation_type: Optional[str] = None,
    min_count: int = 1
) -> Dict[str, Any]:
    """
    Get deviation patterns with optional filtering.
    
    Args:
        memory: The memory dictionary
        deviation_type: Optional deviation type to filter by
        min_count: Minimum count to include a pattern
        
    Returns:
        Dictionary of deviation patterns
    """
    try:
        logger.info(f"Getting deviation patterns (deviation_type={deviation_type}, min_count={min_count})")
        
        # Check if deviation patterns exist
        if "deviation_patterns" not in memory:
            logger.info("No deviation patterns found in memory")
            return {}
        
        # Initialize result dictionary
        patterns = {}
        
        # If deviation type is specified, get pattern for that type
        if deviation_type is not None:
            if deviation_type in memory["deviation_patterns"]:
                pattern = memory["deviation_patterns"][deviation_type]
                
                # Check if count meets minimum
                if pattern["count"] >= min_count:
                    patterns[deviation_type] = pattern
        
        # Otherwise, get all patterns
        else:
            # Iterate through all patterns
            for dev_type, pattern in memory["deviation_patterns"].items():
                # Check if count meets minimum
                if pattern["count"] >= min_count:
                    patterns[dev_type] = pattern
        
        logger.info(f"Retrieved {len(patterns)} deviation patterns")
        return patterns
    
    except Exception as e:
        logger.error(f"Error getting deviation patterns: {str(e)}")
        logger.error(traceback.format_exc())
        return {}

def detect_potential_deviations(
    memory: Dict[str, Any],
    loop_id: int,
    threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Detect potential deviations in threads based on patterns.
    
    Args:
        memory: The memory dictionary
        loop_id: The loop identifier
        threshold: Similarity threshold for detection
        
    Returns:
        List of potential deviations
    """
    try:
        logger.info(f"Detecting potential deviations for loop {loop_id}")
        
        # Check if deviation patterns exist
        if "deviation_patterns" not in memory or not memory["deviation_patterns"]:
            logger.info("No deviation patterns found in memory")
            return []
        
        # Get all threads for loop
        threads = []
        
        if "thread_history" in memory and loop_id in memory["thread_history"]:
            for thread_id, thread_meta in memory["thread_history"][loop_id].items():
                # Only check open threads
                if thread_meta["status"] == "open":
                    # Check if thread already has deviations
                    has_deviations = False
                    
                    if "thread_deviations" in memory and loop_id in memory["thread_deviations"] and thread_id in memory["thread_deviations"][loop_id]:
                        has_deviations = len(memory["thread_deviations"][loop_id][thread_id]) > 0
                    
                    # Skip if thread already has deviations
                    if has_deviations:
                        continue
                    
                    # Get thread messages
                    if "thread_messages" in memory and thread_id in memory["thread_messages"]:
                        thread_messages = memory["thread_messages"][thread_id]
                        
                        # Create thread object
                        thread = {
                            "thread_id": thread_id,
                            "messages": thread_messages,
                            "message_count": len(thread_messages),
                            "participants": list(set([msg["agent"] for msg in thread_messages])),
                            "participant_count": len(set([msg["agent"] for msg in thread_messages])),
                            "all_text": " ".join([msg["message"] for msg in thread_messages])
                        }
                        
                        threads.append(thread)
        
        # Initialize potential deviations
        potential_deviations = []
        
        # Check each thread against patterns
        for thread in threads:
            # Check each pattern
            for deviation_type, pattern in memory["deviation_patterns"].items():
                # Skip patterns with low count
                if pattern["count"] < 3:
                    continue
                
                # Calculate similarity score
                similarity_score = 0.0
                
                # Check message count distribution
                message_count_key = str(thread["message_count"])
                if message_count_key in pattern["message_count_distribution"]:
                    message_count_similarity = pattern["message_count_distribution"][message_count_key] / pattern["count"]
                    similarity_score += message_count_similarity * 0.2
                
                # Check participant count distribution
                participant_count_key = str(thread["participant_count"])
                if participant_count_key in pattern["participant_count_distribution"]:
                    participant_count_similarity = pattern["participant_count_distribution"][participant_count_key] / pattern["count"]
                    similarity_score += participant_count_similarity * 0.2
                
                # Check common agents
                agent_similarity = 0.0
                for agent in thread["participants"]:
                    if agent in pattern["common_agents"]:
                        agent_similarity += pattern["common_agents"][agent] / pattern["count"]
                
                agent_similarity = agent_similarity / max(1, len(thread["participants"]))
                similarity_score += agent_similarity * 0.3
                
                # Check common words
                word_similarity = 0.0
                words = thread["all_text"].lower().split()
                word_count = 0
                
                for word in words:
                    # Skip short words and common stop words
                    if len(word) <= 2 or word in ["the", "and", "for", "that", "this", "with", "not", "are", "from"]:
                        continue
                    
                    if word in pattern["common_words"]:
                        word_similarity += pattern["common_words"][word] / pattern["count"]
                        word_count += 1
                
                if word_count > 0:
                    word_similarity = word_similarity / word_count
                    similarity_score += word_similarity * 0.3
                
                # Check if similarity score meets threshold
                if similarity_score >= threshold:
                    # Create potential deviation
                    potential_deviation = {
                        "thread_id": thread["thread_id"],
                        "deviation_type": deviation_type,
                        "similarity_score": similarity_score,
                        "message_count": thread["message_count"],
                        "participant_count": thread["participant_count"],
                        "participants": thread["participants"]
                    }
                    
                    potential_deviations.append(potential_deviation)
        
        # Sort by similarity score (highest first)
        potential_deviations.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        logger.info(f"Detected {len(potential_deviations)} potential deviations for loop {loop_id}")
        return potential_deviations
    
    except Exception as e:
        logger.error(f"Error detecting potential deviations: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def generate_deviation_report(
    memory: Dict[str, Any],
    loop_id: Optional[int] = None,
    include_patterns: bool = True,
    include_unresolved: bool = True,
    include_resolved: bool = False
) -> Dict[str, Any]:
    """
    Generate a comprehensive report of thread deviations.
    
    Args:
        memory: The memory dictionary
        loop_id: Optional loop ID to filter by
        include_patterns: Whether to include deviation patterns
        include_unresolved: Whether to include unresolved deviations
        include_resolved: Whether to include resolved deviations
        
    Returns:
        Dictionary containing the deviation report
    """
    try:
        logger.info(f"Generating deviation report (loop_id={loop_id}, include_patterns={include_patterns}, include_unresolved={include_unresolved}, include_resolved={include_resolved})")
        
        # Initialize report
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "summary": {
                "total_deviations": 0,
                "unresolved_deviations": 0,
                "resolved_deviations": 0,
                "deviation_types": {}
            },
            "deviations": [],
            "patterns": {}
        }
        
        # Get deviations
        all_deviations = []
        
        if include_unresolved:
            unresolved = get_thread_deviations(memory, loop_id=loop_id, resolved=False)
            all_deviations.extend(unresolved)
            report["summary"]["unresolved_deviations"] = len(unresolved)
        
        if include_resolved:
            resolved = get_thread_deviations(memory, loop_id=loop_id, resolved=True)
            all_deviations.extend(resolved)
            report["summary"]["resolved_deviations"] = len(resolved)
        
        # Update total count
        report["summary"]["total_deviations"] = len(all_deviations)
        
        # Count deviation types
        for dev in all_deviations:
            dev_type = dev["deviation_type"]
            
            if dev_type not in report["summary"]["deviation_types"]:
                report["summary"]["deviation_types"][dev_type] = 0
            
            report["summary"]["deviation_types"][dev_type] += 1
        
        # Add deviations to report
        report["deviations"] = all_deviations
        
        # Add patterns if requested
        if include_patterns:
            report["patterns"] = get_deviation_patterns(memory)
        
        logger.info(f"Generated deviation report with {report['summary']['total_deviations']} deviations")
        return report
    
    except Exception as e:
        logger.error(f"Error generating deviation report: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "error": str(e),
            "generated_at": datetime.datetime.now().isoformat(),
            "summary": {
                "total_deviations": 0,
                "unresolved_deviations": 0,
                "resolved_deviations": 0,
                "deviation_types": {}
            },
            "deviations": [],
            "patterns": {}
        }
