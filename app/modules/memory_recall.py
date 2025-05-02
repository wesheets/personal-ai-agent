"""
Memory Recall Module

This module implements the functionality for memory recall operations.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import re

# Configure logging
logger = logging.getLogger("memory_recall")

# Mock memory database for demonstration
# In a production environment, this would be a database or vector store
_memory_entries = [
    {
        "memory_id": "mem_12345",
        "content": {
            "plan_id": "plan_456",
            "steps": [
                "Analyze requirements",
                "Design solution",
                "Implement code",
                "Test implementation",
                "Deploy to production"
            ],
            "goal": "Implement new feature"
        },
        "tags": ["plan_generated", "orchestrator_output"],
        "agent_id": "ORCHESTRATOR",
        "loop_id": "loop_12345",
        "timestamp": "2025-04-24T20:40:00Z"
    },
    {
        "memory_id": "mem_12346",
        "content": {
            "review_id": "rev_789",
            "issues": [
                "Missing error handling",
                "Inefficient algorithm"
            ],
            "recommendations": [
                "Add try-catch blocks",
                "Optimize the sorting algorithm"
            ]
        },
        "tags": ["review_completed", "critic_output"],
        "agent_id": "CRITIC",
        "loop_id": "loop_12345",
        "timestamp": "2025-04-24T20:35:00Z"
    },
    {
        "memory_id": "mem_12347",
        "content": {
            "analysis_id": "ana_123",
            "insights": [
                "User engagement increased by 15%",
                "Performance improved by 30%",
                "Error rate decreased by 25%"
            ],
            "summary": "The changes have had a positive impact on the system."
        },
        "tags": ["analysis_completed", "sage_output"],
        "agent_id": "SAGE",
        "loop_id": "loop_12345",
        "timestamp": "2025-04-24T20:30:00Z"
    },
    {
        "memory_id": "mem_12348",
        "content": {
            "conversation_id": "conv_456",
            "messages": [
                {"role": "user", "content": "How can I improve the system?"},
                {"role": "assistant", "content": "You can optimize the algorithms and add more error handling."}
            ]
        },
        "tags": ["conversation", "user_interaction"],
        "agent_id": "ORCHESTRATOR",
        "loop_id": "loop_12345",
        "timestamp": "2025-04-24T20:25:00Z"
    },
    {
        "memory_id": "mem_12349",
        "content": {
            "plan_id": "plan_457",
            "steps": [
                "Analyze performance bottlenecks",
                "Identify optimization opportunities",
                "Implement optimizations",
                "Test performance improvements",
                "Deploy optimized version"
            ],
            "goal": "Improve system performance"
        },
        "tags": ["plan_generated", "orchestrator_output"],
        "agent_id": "ORCHESTRATOR",
        "loop_id": "loop_67890",
        "timestamp": "2025-04-24T19:40:00Z"
    }
]

def recall_memory(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recall memory entries based on the provided criteria.
    
    Args:
        request_data: Request data containing method, query, limit, offset, etc.
        
    Returns:
        Dictionary containing the memory recall results
    """
    try:
        method = request_data.get("method", "tag")
        query = request_data.get("query", "")
        limit = min(request_data.get("limit", 10), 100)  # Cap at 100 for performance
        offset = request_data.get("offset", 0)
        sort_order = request_data.get("sort_order", "newest_first")
        start_date = request_data.get("start_date")
        end_date = request_data.get("end_date")
        agent_filter = request_data.get("agent_filter")
        loop_filter = request_data.get("loop_filter")
        
        # Validate query
        if not query.strip():
            return {
                "message": "Query must not be empty",
                "query": query,
                "method": method,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Filter entries based on criteria
        filtered_entries = _filter_entries(
            method, query, start_date, end_date, agent_filter, loop_filter
        )
        
        # Sort entries
        sorted_entries = _sort_entries(filtered_entries, sort_order)
        
        # Apply pagination
        paginated_entries = sorted_entries[offset:offset + limit]
        
        # Log the memory recall to memory
        _log_memory_recall(method, query, len(filtered_entries))
        
        # Return the results
        return {
            "query": query,
            "method": method,
            "total_results": len(filtered_entries),
            "returned_results": len(paginated_entries),
            "results": paginated_entries,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error recalling memory: {str(e)}")
        return {
            "message": f"Failed to recall memory: {str(e)}",
            "query": request_data.get("query"),
            "method": request_data.get("method"),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def _filter_entries(
    method: str,
    query: str,
    start_date: Optional[str],
    end_date: Optional[str],
    agent_filter: Optional[str],
    loop_filter: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Filter memory entries based on the provided criteria.
    
    Args:
        method: Method to use for filtering (tag, keyword, semantic, temporal, agent)
        query: Query string
        start_date: Start date filter (ISO timestamp)
        end_date: End date filter (ISO timestamp)
        agent_filter: Agent ID filter
        loop_filter: Loop ID filter
        
    Returns:
        List of filtered memory entries
    """
    # Start with all entries
    filtered_entries = _memory_entries.copy()
    
    # Apply method-specific filtering
    if method == "tag":
        filtered_entries = [
            entry for entry in filtered_entries
            if query.lower() in [tag.lower() for tag in entry.get("tags", [])]
        ]
    elif method == "keyword":
        filtered_entries = [
            entry for entry in filtered_entries
            if _contains_keyword(entry, query)
        ]
    elif method == "semantic":
        # In a real implementation, this would use vector similarity search
        # For this implementation, we'll use a simple keyword search
        filtered_entries = [
            entry for entry in filtered_entries
            if _contains_keyword(entry, query)
        ]
    elif method == "temporal":
        # For temporal search, query is expected to be a time range like "1h", "1d", "1w"
        filtered_entries = [
            entry for entry in filtered_entries
            if _is_within_time_range(entry, query)
        ]
    elif method == "agent":
        filtered_entries = [
            entry for entry in filtered_entries
            if entry.get("agent_id", "").lower() == query.lower()
        ]
    
    # Apply date filters
    if start_date:
        filtered_entries = [
            entry for entry in filtered_entries
            if entry.get("timestamp", "") >= start_date
        ]
    
    if end_date:
        filtered_entries = [
            entry for entry in filtered_entries
            if entry.get("timestamp", "") <= end_date
        ]
    
    # Apply agent filter
    if agent_filter:
        filtered_entries = [
            entry for entry in filtered_entries
            if entry.get("agent_id", "").lower() == agent_filter.lower()
        ]
    
    # Apply loop filter
    if loop_filter:
        filtered_entries = [
            entry for entry in filtered_entries
            if entry.get("loop_id", "").lower() == loop_filter.lower()
        ]
    
    return filtered_entries

def _sort_entries(entries: List[Dict[str, Any]], sort_order: str) -> List[Dict[str, Any]]:
    """
    Sort memory entries based on the provided sort order.
    
    Args:
        entries: Memory entries to sort
        sort_order: Sort order (newest_first, oldest_first, relevance)
        
    Returns:
        Sorted list of memory entries
    """
    if sort_order == "newest_first":
        return sorted(entries, key=lambda x: x.get("timestamp", ""), reverse=True)
    elif sort_order == "oldest_first":
        return sorted(entries, key=lambda x: x.get("timestamp", ""))
    elif sort_order == "relevance":
        # In a real implementation, this would use relevance scoring
        # For this implementation, we'll return as is
        return entries
    else:
        return entries

def _contains_keyword(entry: Dict[str, Any], keyword: str) -> bool:
    """
    Check if a memory entry contains the specified keyword.
    
    Args:
        entry: Memory entry to check
        keyword: Keyword to search for
        
    Returns:
        True if the entry contains the keyword, False otherwise
    """
    # Convert entry to string for simple keyword search
    entry_str = json.dumps(entry).lower()
    return keyword.lower() in entry_str

def _is_within_time_range(entry: Dict[str, Any], time_range: str) -> bool:
    """
    Check if a memory entry is within the specified time range.
    
    Args:
        entry: Memory entry to check
        time_range: Time range string (e.g., "1h", "1d", "1w")
        
    Returns:
        True if the entry is within the time range, False otherwise
    """
    try:
        # Parse time range
        match = re.match(r"(\d+)([hdwmy])", time_range.lower())
        if not match:
            return False
        
        value = int(match.group(1))
        unit = match.group(2)
        
        # Calculate time delta
        if unit == "h":
            delta = timedelta(hours=value)
        elif unit == "d":
            delta = timedelta(days=value)
        elif unit == "w":
            delta = timedelta(weeks=value)
        elif unit == "m":
            delta = timedelta(days=value * 30)  # Approximate
        elif unit == "y":
            delta = timedelta(days=value * 365)  # Approximate
        else:
            return False
        
        # Calculate cutoff time
        cutoff_time = datetime.utcnow() - delta
        cutoff_str = cutoff_time.isoformat()
        
        # Check if entry is after cutoff time
        return entry.get("timestamp", "") >= cutoff_str
    
    except Exception as e:
        logger.error(f"Error parsing time range: {str(e)}")
        return False

def _log_memory_recall(method: str, query: str, result_count: int) -> None:
    """
    Log memory recall to memory.
    
    Args:
        method: Method used for recall
        query: Query string
        result_count: Number of results found
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "operation": "memory_recall",
            "method": method,
            "query": query,
            "result_count": result_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to console for demonstration
        logger.info(f"Memory recall logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: memory_recall_{method}_{query}")
    
    except Exception as e:
        logger.error(f"Error logging memory recall: {str(e)}")
