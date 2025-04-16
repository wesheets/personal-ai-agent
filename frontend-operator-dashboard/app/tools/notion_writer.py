"""
Notion Writer Tool for the Personal AI Agent System.

This module provides functionality to create, update, and manage content
in Notion workspaces.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("notion_writer")

def run(
    operation: str,
    content: Optional[Union[str, Dict[str, Any]]] = None,
    page_id: Optional[str] = None,
    database_id: Optional[str] = None,
    parent_page_id: Optional[str] = None,
    title: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    format: str = "markdown",
    include_children: bool = False,
    archive: bool = False,
    token: Optional[str] = None,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["notion", "document"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Create, update, or manage content in Notion.
    
    Args:
        operation: Operation to perform (create_page, update_page, get_page, etc.)
        content: Content to write (text or structured content)
        page_id: ID of the page to operate on (for update, get, delete operations)
        database_id: ID of the database to operate on (for database operations)
        parent_page_id: ID of the parent page (for create operations)
        title: Title of the page (for create operations)
        properties: Page properties (for create/update operations)
        format: Content format (markdown, html, etc.)
        include_children: Whether to include child blocks in get operations
        archive: Whether to archive instead of delete
        token: Notion API token
        store_memory: Whether to store the operation result in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing operation results and metadata
    """
    logger.info(f"Performing Notion {operation} operation")
    
    try:
        # Validate operation
        if operation not in SUPPORTED_OPERATIONS:
            raise ValueError(f"Unsupported operation: {operation}. Supported operations: {', '.join(SUPPORTED_OPERATIONS)}")
            
        # Validate required parameters for each operation
        _validate_parameters(operation, page_id, database_id, parent_page_id, title, content)
        
        # In a real implementation, this would use the Notion API
        # For now, we'll simulate the Notion operations
        
        # Simulate Notion API call
        result = _simulate_notion_operation(
            operation, content, page_id, database_id, parent_page_id,
            title, properties, format, include_children, archive
        )
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                memory_entry = {
                    "type": "notion_operation",
                    "operation": operation,
                    "timestamp": datetime.now().isoformat()
                }
                
                if operation == "create_page":
                    memory_entry["page_title"] = title
                    memory_entry["page_id"] = result.get("id")
                    if content:
                        content_summary = str(content)[:300] + "..." if len(str(content)) > 300 else str(content)
                        memory_entry["content_summary"] = content_summary
                
                elif operation == "update_page":
                    memory_entry["page_id"] = page_id
                    if content:
                        content_summary = str(content)[:300] + "..." if len(str(content)) > 300 else str(content)
                        memory_entry["content_summary"] = content_summary
                
                elif operation == "get_page":
                    memory_entry["page_id"] = page_id
                    memory_entry["page_title"] = result.get("title")
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags
                )
                
                logger.info(f"Stored Notion operation in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store Notion operation in memory: {str(e)}")
        
        return {
            "success": True,
            "operation": operation,
            "result": result
        }
    except Exception as e:
        error_msg = f"Error performing Notion operation: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "operation": operation
        }

def _validate_parameters(
    operation: str,
    page_id: Optional[str],
    database_id: Optional[str],
    parent_page_id: Optional[str],
    title: Optional[str],
    content: Optional[Any]
) -> None:
    """
    Validate required parameters for each operation.
    
    Args:
        operation: Operation to perform
        page_id: ID of the page to operate on
        database_id: ID of the database to operate on
        parent_page_id: ID of the parent page
        title: Title of the page
        content: Content to write
        
    Raises:
        ValueError: If required parameters are missing
    """
    if operation == "create_page":
        if not parent_page_id and not database_id:
            raise ValueError("Either parent_page_id or database_id is required for create_page operation")
        if not title:
            raise ValueError("Title is required for create_page operation")
    
    elif operation in ["update_page", "get_page", "delete_page"]:
        if not page_id:
            raise ValueError(f"page_id is required for {operation} operation")
    
    elif operation in ["create_database", "update_database", "get_database", "query_database"]:
        if operation == "create_database" and not parent_page_id:
            raise ValueError("parent_page_id is required for create_database operation")
        if operation != "create_database" and not database_id:
            raise ValueError(f"database_id is required for {operation} operation")

def _simulate_notion_operation(
    operation: str,
    content: Optional[Any],
    page_id: Optional[str],
    database_id: Optional[str],
    parent_page_id: Optional[str],
    title: Optional[str],
    properties: Optional[Dict[str, Any]],
    format: str,
    include_children: bool,
    archive: bool
) -> Dict[str, Any]:
    """
    Simulate Notion API operations for development purposes.
    
    Args:
        operation: Operation to perform
        content: Content to write
        page_id: ID of the page to operate on
        database_id: ID of the database to operate on
        parent_page_id: ID of the parent page
        title: Title of the page
        properties: Page properties
        format: Content format
        include_children: Whether to include child blocks
        archive: Whether to archive instead of delete
        
    Returns:
        Dictionary with simulated operation results
    """
    # Generate IDs for new resources
    def generate_id(prefix: str) -> str:
        return f"{prefix}_{int(time.time())}_{hash(str(content) + str(title)) % 10000:04d}"
    
    # Simulate different operations
    if operation == "create_page":
        page_id = generate_id("page")
        
        result = {
            "id": page_id,
            "created_time": datetime.now().isoformat(),
            "last_edited_time": datetime.now().isoformat(),
            "title": title,
            "url": f"https://notion.so/{page_id.replace('_', '-')}",
            "parent": {
                "type": "page_id" if parent_page_id else "database_id",
                "id": parent_page_id or database_id
            }
        }
        
        if properties:
            result["properties"] = properties
        
        return result
    
    elif operation == "update_page":
        return {
            "id": page_id,
            "last_edited_time": datetime.now().isoformat(),
            "url": f"https://notion.so/{page_id.replace('_', '-')}",
            "updated": True
        }
    
    elif operation == "get_page":
        return {
            "id": page_id,
            "created_time": "2025-01-15T12:30:00.000Z",
            "last_edited_time": "2025-03-20T15:45:00.000Z",
            "title": f"Page {page_id[-4:]}",
            "url": f"https://notion.so/{page_id.replace('_', '-')}",
            "content": _generate_sample_page_content() if include_children else None,
            "properties": {
                "Title": {"title": [{"text": {"content": f"Page {page_id[-4:]}"}}]},
                "Tags": {"multi_select": [{"name": "Sample"}, {"name": "Demo"}]},
                "Status": {"select": {"name": "Active"}}
            }
        }
    
    elif operation == "delete_page":
        return {
            "id": page_id,
            "deleted": True,
            "archived": archive
        }
    
    elif operation == "create_database":
        db_id = generate_id("db")
        
        return {
            "id": db_id,
            "created_time": datetime.now().isoformat(),
            "title": title,
            "url": f"https://notion.so/{db_id.replace('_', '-')}",
            "parent": {
                "type": "page_id",
                "id": parent_page_id
            },
            "properties": properties or {
                "Name": {"title": {}},
                "Status": {"select": {"options": [
                    {"name": "Active", "color": "green"},
                    {"name": "Pending", "color": "yellow"},
                    {"name": "Completed", "color": "blue"}
                ]}},
                "Priority": {"select": {"options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "green"}
                ]}}
            }
        }
    
    elif operation == "update_database":
        return {
            "id": database_id,
            "last_edited_time": datetime.now().isoformat(),
            "updated": True
        }
    
    elif operation == "get_database":
        return {
            "id": database_id,
            "created_time": "2025-01-10T09:15:00.000Z",
            "last_edited_time": "2025-03-18T14:20:00.000Z",
            "title": f"Database {database_id[-4:]}",
            "url": f"https://notion.so/{database_id.replace('_', '-')}",
            "properties": {
                "Name": {"title": {}},
                "Status": {"select": {"options": [
                    {"name": "Active", "color": "green"},
                    {"name": "Pending", "color": "yellow"},
                    {"name": "Completed", "color": "blue"}
                ]}},
                "Priority": {"select": {"options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "green"}
                ]}}
            }
        }
    
    elif operation == "query_database":
        return {
            "results": _generate_sample_database_results(database_id),
            "has_more": False,
            "next_cursor": None
        }
    
    elif operation == "search":
        query = content if isinstance(content, str) else ""
        return {
            "results": _generate_sample_search_results(query),
            "has_more": False,
            "next_cursor": None
        }
    
    # Default fallback
    return {
        "operation": operation,
        "simulated": True,
        "timestamp": datetime.now().isoformat()
    }

def _generate_sample_page_content() -> List[Dict[str, Any]]:
    """
    Generate sample page content for simulation purposes.
    
    Returns:
        List of content blocks
    """
    return [
        {
            "type": "paragraph",
            "paragraph": {
                "text": [{"type": "text", "text": {"content": "This is a sample paragraph."}}]
            }
        },
        {
            "type": "heading_1",
            "heading_1": {
                "text": [{"type": "text", "text": {"content": "Sample Heading"}}]
            }
        },
        {
            "type": "paragraph",
            "paragraph": {
                "text": [{"type": "text", "text": {"content": "Another paragraph with more content."}}]
            }
        },
        {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "text": [{"type": "text", "text": {"content": "List item 1"}}]
            }
        },
        {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "text": [{"type": "text", "text": {"content": "List item 2"}}]
            }
        },
        {
            "type": "to_do",
            "to_do": {
                "text": [{"type": "text", "text": {"content": "Task to complete"}}],
                "checked": False
            }
        }
    ]

def _generate_sample_database_results(database_id: str) -> List[Dict[str, Any]]:
    """
    Generate sample database query results for simulation purposes.
    
    Args:
        database_id: Database ID
        
    Returns:
        List of database items
    """
    return [
        {
            "id": f"page_{int(time.time())}_{1:04d}",
            "properties": {
                "Name": {"title": [{"text": {"content": "Sample Item 1"}}]},
                "Status": {"select": {"name": "Active", "color": "green"}},
                "Priority": {"select": {"name": "High", "color": "red"}}
            },
            "url": f"https://notion.so/{database_id.replace('_', '-')}-item-1"
        },
        {
            "id": f"page_{int(time.time())}_{2:04d}",
            "properties": {
                "Name": {"title": [{"text": {"content": "Sample Item 2"}}]},
                "Status": {"select": {"name": "Pending", "color": "yellow"}},
                "Priority": {"select": {"name": "Medium", "color": "yellow"}}
            },
            "url": f"https://notion.so/{database_id.replace('_', '-')}-item-2"
        },
        {
            "id": f"page_{int(time.time())}_{3:04d}",
            "properties": {
                "Name": {"title": [{"text": {"content": "Sample Item 3"}}]},
                "Status": {"select": {"name": "Completed", "color": "blue"}},
                "Priority": {"select": {"name": "Low", "color": "green"}}
            },
            "url": f"https://notion.so/{database_id.replace('_', '-')}-item-3"
        }
    ]

def _generate_sample_search_results(query: str) -> List[Dict[str, Any]]:
    """
    Generate sample search results for simulation purposes.
    
    Args:
        query: Search query
        
    Returns:
        List of search results
    """
    return [
        {
            "id": f"page_{int(time.time())}_{1:04d}",
            "title": f"Result 1 for '{query}'",
            "object": "page",
            "url": f"https://notion.so/result-1-{query.replace(' ', '-')}"
        },
        {
            "id": f"page_{int(time.time())}_{2:04d}",
            "title": f"Result 2 for '{query}'",
            "object": "page",
            "url": f"https://notion.so/result-2-{query.replace(' ', '-')}"
        },
        {
            "id": f"db_{int(time.time())}_{1:04d}",
            "title": f"Database related to '{query}'",
            "object": "database",
            "url": f"https://notion.so/db-{query.replace(' ', '-')}"
        }
    ]

# Define supported operations
SUPPORTED_OPERATIONS = [
    "create_page",
    "update_page",
    "get_page",
    "delete_page",
    "create_database",
    "update_database",
    "get_database",
    "query_database",
    "search"
]
