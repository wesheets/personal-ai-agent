"""
Delegate Stream Module

This module implements the functionality for creating and managing delegate streams.
"""

import logging
import json
import uuid
import random
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio
import websockets

# Configure logging
logger = logging.getLogger("delegate_stream")

# In-memory storage for streams and stream status
# In a production environment, this would be a database
_streams: Dict[str, Dict[str, Any]] = {}
_stream_status: Dict[str, Dict[str, Any]] = {}
_stream_events: Dict[str, List[Dict[str, Any]]] = {}
_active_connections: Dict[str, List[Any]] = {}

def create_stream(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a delegate stream based on the provided parameters.
    
    Args:
        request_data: Request data containing stream_type, target_id, description, etc.
        
    Returns:
        Dictionary containing the stream result or status
    """
    try:
        stream_type = request_data.get("stream_type")
        target_id = request_data.get("target_id")
        description = request_data.get("description")
        priority = request_data.get("priority", "medium")
        filters = request_data.get("filters", {})
        max_events = request_data.get("max_events")
        timeout_seconds = request_data.get("timeout_seconds")
        agent_id = request_data.get("agent_id")
        loop_id = request_data.get("loop_id")
        
        # Validate target ID
        if not target_id or not target_id.strip():
            return {
                "message": "Target ID must not be empty",
                "stream_type": stream_type,
                "target_id": target_id,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Validate description
        if not description or not description.strip():
            return {
                "message": "Description must not be empty",
                "stream_type": stream_type,
                "target_id": target_id,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Generate stream ID
        stream_id = f"stream_{uuid.uuid4().hex[:8]}"
        
        # Generate token
        token = f"token_{uuid.uuid4().hex}"
        
        # Calculate expiration time (default: 24 hours)
        expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        
        # Generate connection URL
        connection_url = f"wss://api.promethios.ai/streams/{stream_id}"
        
        # Create stream entry
        _streams[stream_id] = {
            "stream_id": stream_id,
            "stream_type": stream_type,
            "target_id": target_id,
            "description": description,
            "priority": priority,
            "filters": filters,
            "max_events": max_events,
            "timeout_seconds": timeout_seconds,
            "status": "active",
            "connection_url": connection_url,
            "token": token,
            "expires_at": expires_at,
            "agent_id": agent_id,
            "loop_id": loop_id,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Create stream status entry
        _stream_status[stream_id] = {
            "stream_id": stream_id,
            "stream_type": stream_type,
            "target_id": target_id,
            "status": "active",
            "events_streamed": 0,
            "connected_clients": 0,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at,
            "agent_id": agent_id,
            "loop_id": loop_id
        }
        
        # Initialize events list
        _stream_events[stream_id] = []
        
        # Initialize connections list
        _active_connections[stream_id] = []
        
        # Log the stream creation to memory
        _log_stream_creation(stream_id, stream_type, target_id)
        
        # Return the stream result
        return {
            "stream_id": stream_id,
            "stream_type": stream_type,
            "target_id": target_id,
            "status": "active",
            "connection_url": connection_url,
            "token": token,
            "expires_at": expires_at,
            "agent_id": agent_id,
            "loop_id": loop_id,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error creating stream: {str(e)}")
        return {
            "message": f"Failed to create stream: {str(e)}",
            "stream_type": request_data.get("stream_type"),
            "target_id": request_data.get("target_id"),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def get_stream_status(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the status of a stream.
    
    Args:
        request_data: Request data containing stream_id
        
    Returns:
        Dictionary containing the stream status
    """
    try:
        stream_id = request_data.get("stream_id")
        
        # Validate stream ID
        if not stream_id:
            return {
                "message": "Stream ID must not be empty",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Check if stream exists in stream status
        if stream_id not in _stream_status:
            return {
                "message": f"Stream with ID {stream_id} not found",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Get stream status
        status = _stream_status[stream_id]
        
        # Log the status check to memory
        _log_status_check(stream_id, status["status"])
        
        # Return the status
        return {
            "stream_id": status["stream_id"],
            "stream_type": status["stream_type"],
            "target_id": status["target_id"],
            "status": status["status"],
            "events_streamed": status["events_streamed"],
            "connected_clients": status["connected_clients"],
            "created_at": status["created_at"],
            "expires_at": status["expires_at"],
            "agent_id": status["agent_id"],
            "loop_id": status["loop_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error getting stream status: {str(e)}")
        return {
            "message": f"Failed to get stream status: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

def close_stream(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Close a stream.
    
    Args:
        request_data: Request data containing stream_id and reason
        
    Returns:
        Dictionary containing the closure result
    """
    try:
        stream_id = request_data.get("stream_id")
        reason = request_data.get("reason")
        
        # Validate stream ID
        if not stream_id:
            return {
                "message": "Stream ID must not be empty",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Check if stream exists
        if stream_id not in _streams:
            return {
                "message": f"Stream with ID {stream_id} not found",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Get stream
        stream = _streams[stream_id]
        status = _stream_status[stream_id]
        
        # Check if already closed
        if status["status"] == "closed":
            return {
                "stream_id": stream_id,
                "status": "already_closed",
                "events_streamed": status["events_streamed"],
                "duration_seconds": _calculate_duration_seconds(status["created_at"]),
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        
        # Update stream status
        _stream_status[stream_id]["status"] = "closed"
        
        # Close all active connections
        # In a real implementation, this would notify all connected clients
        _active_connections[stream_id] = []
        _stream_status[stream_id]["connected_clients"] = 0
        
        # Calculate duration
        duration_seconds = _calculate_duration_seconds(status["created_at"])
        
        # Log the closure to memory
        _log_stream_closure(stream_id, reason, status["events_streamed"], duration_seconds)
        
        # Return the closure result
        return {
            "stream_id": stream_id,
            "status": "success",
            "events_streamed": status["events_streamed"],
            "duration_seconds": duration_seconds,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    except Exception as e:
        logger.error(f"Error closing stream: {str(e)}")
        return {
            "message": f"Failed to close stream: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

async def handle_stream_connection(websocket, path):
    """
    Handle a WebSocket connection to a stream.
    
    Args:
        websocket: WebSocket connection
        path: Connection path
    """
    # Extract stream ID from path
    stream_id = path.split("/")[-1]
    
    # Check if stream exists
    if stream_id not in _streams:
        await websocket.send(json.dumps({
            "error": f"Stream with ID {stream_id} not found"
        }))
        return
    
    # Check if stream is active
    if _stream_status[stream_id]["status"] != "active":
        await websocket.send(json.dumps({
            "error": f"Stream with ID {stream_id} is not active"
        }))
        return
    
    # Add connection to active connections
    _active_connections[stream_id].append(websocket)
    _stream_status[stream_id]["connected_clients"] += 1
    
    try:
        # Send welcome message
        await websocket.send(json.dumps({
            "type": "welcome",
            "stream_id": stream_id,
            "message": f"Connected to stream {stream_id}"
        }))
        
        # Send existing events
        for event in _stream_events[stream_id]:
            await websocket.send(json.dumps(event))
        
        # Keep connection open and handle incoming messages
        async for message in websocket:
            # Process incoming messages if needed
            pass
    
    except websockets.exceptions.ConnectionClosed:
        # Connection closed
        pass
    
    finally:
        # Remove connection from active connections
        if websocket in _active_connections[stream_id]:
            _active_connections[stream_id].remove(websocket)
            _stream_status[stream_id]["connected_clients"] -= 1

def add_event_to_stream(stream_id: str, event_type: str, source: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add an event to a stream.
    
    Args:
        stream_id: Stream ID
        event_type: Event type
        source: Event source
        data: Event data
        
    Returns:
        Dictionary containing the event
    """
    try:
        # Check if stream exists
        if stream_id not in _streams:
            return {
                "error": f"Stream with ID {stream_id} not found"
            }
        
        # Check if stream is active
        if _stream_status[stream_id]["status"] != "active":
            return {
                "error": f"Stream with ID {stream_id} is not active"
            }
        
        # Generate event ID
        event_id = f"event_{uuid.uuid4().hex[:8]}"
        
        # Create event
        event = {
            "event_id": event_id,
            "stream_id": stream_id,
            "event_type": event_type,
            "source": source,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add event to stream events
        _stream_events[stream_id].append(event)
        
        # Update events streamed count
        _stream_status[stream_id]["events_streamed"] += 1
        
        # Check if max events reached
        max_events = _streams[stream_id].get("max_events")
        if max_events and _stream_status[stream_id]["events_streamed"] >= max_events:
            # Close stream
            close_stream({"stream_id": stream_id, "reason": "Max events reached"})
        
        # Send event to all connected clients
        # In a real implementation, this would be done asynchronously
        for connection in _active_connections[stream_id]:
            asyncio.create_task(connection.send(json.dumps(event)))
        
        return event
    
    except Exception as e:
        logger.error(f"Error adding event to stream: {str(e)}")
        return {
            "error": f"Failed to add event to stream: {str(e)}"
        }

def _calculate_duration_seconds(created_at: str) -> int:
    """
    Calculate the duration in seconds between created_at and now.
    
    Args:
        created_at: ISO timestamp of creation
        
    Returns:
        Duration in seconds
    """
    try:
        created_datetime = datetime.fromisoformat(created_at)
        now = datetime.utcnow()
        return int((now - created_datetime).total_seconds())
    except Exception:
        return 0

def _log_stream_creation(
    stream_id: str,
    stream_type: str,
    target_id: str
) -> None:
    """
    Log stream creation to memory.
    
    Args:
        stream_id: Stream ID
        stream_type: Type of stream
        target_id: Target ID
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "operation": "stream_creation",
            "stream_id": stream_id,
            "stream_type": stream_type,
            "target_id": target_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to console for demonstration
        logger.info(f"Stream creation logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: stream_creation_{stream_id}")
    
    except Exception as e:
        logger.error(f"Error logging stream creation: {str(e)}")

def _log_status_check(stream_id: str, status: str) -> None:
    """
    Log status check to memory.
    
    Args:
        stream_id: Stream ID
        status: Stream status
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "operation": "stream_status_check",
            "stream_id": stream_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to console for demonstration
        logger.info(f"Status check logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: stream_status_check_{stream_id}")
    
    except Exception as e:
        logger.error(f"Error logging status check: {str(e)}")

def _log_stream_closure(
    stream_id: str,
    reason: Optional[str],
    events_streamed: int,
    duration_seconds: int
) -> None:
    """
    Log stream closure to memory.
    
    Args:
        stream_id: Stream ID
        reason: Reason for closure
        events_streamed: Number of events streamed
        duration_seconds: Duration in seconds
    """
    try:
        # In a real implementation, this would write to a memory service
        log_entry = {
            "operation": "stream_closure",
            "stream_id": stream_id,
            "reason": reason,
            "events_streamed": events_streamed,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log to console for demonstration
        logger.info(f"Stream closure logged: {json.dumps(log_entry)}")
        print(f"Logged to memory: stream_closure_{stream_id}")
    
    except Exception as e:
        logger.error(f"Error logging stream closure: {str(e)}")
