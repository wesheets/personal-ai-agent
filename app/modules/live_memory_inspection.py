"""
Live Memory Inspection Module

This module implements the Live Memory Inspection functionality, which provides
real-time access to the memory state of running loops, allowing for inspection,
debugging, and analysis of memory contents during execution.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

class MemoryAccessLevel(str, Enum):
    """Enum for memory access levels"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"

class MemoryFormat(str, Enum):
    """Enum for memory output formats"""
    JSON = "json"
    TREE = "tree"
    TABLE = "table"
    GRAPH = "graph"

class MemoryFilter(BaseModel):
    """Model for memory filtering options"""
    keys: Optional[List[str]] = Field(default=None, description="List of specific memory keys to include")
    prefix: Optional[str] = Field(default=None, description="Prefix filter for memory keys")
    types: Optional[List[str]] = Field(default=None, description="Filter by value types")
    modified_after: Optional[datetime] = Field(default=None, description="Filter for keys modified after timestamp")
    modified_before: Optional[datetime] = Field(default=None, description="Filter for keys modified before timestamp")
    created_by: Optional[List[str]] = Field(default=None, description="Filter by creator agent")
    accessed_by: Optional[List[str]] = Field(default=None, description="Filter by accessing agent")
    min_size: Optional[int] = Field(default=None, description="Minimum value size in bytes")
    max_size: Optional[int] = Field(default=None, description="Maximum value size in bytes")
    
    def apply(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the filter to memory data
        
        Args:
            memory_data: The memory data to filter
            
        Returns:
            Filtered memory data
        """
        filtered_data = {}
        
        for key, value in memory_data.items():
            # Skip if key doesn't match specific keys filter
            if self.keys is not None and key not in self.keys:
                continue
                
            # Skip if key doesn't match prefix filter
            if self.prefix is not None and not key.startswith(self.prefix):
                continue
                
            # Skip if value type doesn't match types filter
            if self.types is not None:
                value_type = type(value.get("value")).__name__
                if value_type not in self.types:
                    continue
            
            # Skip if modified timestamp doesn't match filters
            if self.modified_after is not None and value.get("last_modified"):
                modified_time = datetime.fromisoformat(value.get("last_modified"))
                if modified_time < self.modified_after:
                    continue
                    
            if self.modified_before is not None and value.get("last_modified"):
                modified_time = datetime.fromisoformat(value.get("last_modified"))
                if modified_time > self.modified_before:
                    continue
            
            # Skip if creator doesn't match filter
            if self.created_by is not None and value.get("created_by") not in self.created_by:
                continue
                
            # Skip if accessed_by doesn't match filter
            if self.accessed_by is not None:
                # Check if any of the access history matches the filter
                access_history = value.get("access_history", [])
                if not any(access.get("agent") in self.accessed_by for access in access_history):
                    continue
            
            # Skip if size doesn't match filters
            if self.min_size is not None or self.max_size is not None:
                # Estimate size by converting to JSON
                size = len(json.dumps(value.get("value")))
                
                if self.min_size is not None and size < self.min_size:
                    continue
                    
                if self.max_size is not None and size > self.max_size:
                    continue
            
            # If we got here, the key/value passed all filters
            filtered_data[key] = value
            
        return filtered_data

class MemoryDiff(BaseModel):
    """Model for memory diff results"""
    added: Dict[str, Any] = Field(default_factory=dict, description="Keys added since baseline")
    removed: Dict[str, Any] = Field(default_factory=dict, description="Keys removed since baseline")
    modified: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Keys modified since baseline with before/after values")
    unchanged: Dict[str, Any] = Field(default_factory=dict, description="Keys unchanged since baseline")

# Mode-specific memory inspection settings
MODE_MEMORY_SETTINGS = {
    "fast": {
        "access_level": MemoryAccessLevel.READ_ONLY,
        "snapshot_frequency": "end_only",
        "max_snapshots": 1,
        "detail_level": "minimal",
        "track_changes": False,
        "enable_time_travel": False,
        "enable_filtering": True,
        "enable_export": True,
        "default_format": MemoryFormat.JSON
    },
    "balanced": {
        "access_level": MemoryAccessLevel.READ_ONLY,
        "snapshot_frequency": "agent_completion",
        "max_snapshots": 5,
        "detail_level": "standard",
        "track_changes": True,
        "enable_time_travel": False,
        "enable_filtering": True,
        "enable_export": True,
        "default_format": MemoryFormat.JSON
    },
    "thorough": {
        "access_level": MemoryAccessLevel.READ_WRITE,
        "snapshot_frequency": "real_time",
        "max_snapshots": 20,
        "detail_level": "detailed",
        "track_changes": True,
        "enable_time_travel": True,
        "enable_filtering": True,
        "enable_export": True,
        "default_format": MemoryFormat.JSON
    },
    "research": {
        "access_level": MemoryAccessLevel.ADMIN,
        "snapshot_frequency": "real_time",
        "max_snapshots": 50,
        "detail_level": "comprehensive",
        "track_changes": True,
        "enable_time_travel": True,
        "enable_filtering": True,
        "enable_export": True,
        "default_format": MemoryFormat.JSON,
        "research_specific": {
            "track_uncertainty": True,
            "track_alternatives": True,
            "enable_memory_exploration": True,
            "enable_counterfactual_analysis": True
        }
    }
}

class MemoryInspector:
    """
    Class for inspecting and analyzing memory state of running loops.
    """
    
    def __init__(self, loop_id: str, mode: str = "balanced"):
        """
        Initialize the memory inspector.
        
        Args:
            loop_id: The ID of the loop to inspect
            mode: The orchestrator mode (fast, balanced, thorough, research)
        """
        self.loop_id = loop_id
        self.mode = mode.lower() if mode else "balanced"
        
        # Set access level and other settings based on mode
        if self.mode in MODE_MEMORY_SETTINGS:
            self.settings = MODE_MEMORY_SETTINGS[self.mode]
        else:
            self.settings = MODE_MEMORY_SETTINGS["balanced"]
            
        self.access_level = self.settings["access_level"]
        
        self.snapshots = {}  # Dictionary to store memory snapshots
        self.watchers = {}   # Dictionary to store memory watchers
        self.last_snapshot_time = None
        self.snapshot_count = 0
        self.max_snapshots = self.settings["max_snapshots"]
        
        logger.info(f"Initialized MemoryInspector for loop {loop_id} with {self.mode} mode and {self.access_level} access")
    
    async def get_memory_state(self, filter_options: Optional[MemoryFilter] = None) -> Dict[str, Any]:
        """
        Get the current memory state for the loop.
        
        Args:
            filter_options: Optional filter to apply to the memory data
            
        Returns:
            Dictionary containing the memory state
        """
        logger.info(f"Getting memory state for loop {self.loop_id} in {self.mode} mode")
        
        try:
            # In a real implementation, this would fetch from a database or memory service
            # For this implementation, we'll simulate fetching memory
            memory_data = await self._fetch_memory_data()
            
            # Apply filter if provided and filtering is enabled
            if filter_options and self.settings["enable_filtering"]:
                memory_data = filter_options.apply(memory_data)
            
            # Record access for auditing
            await self._record_memory_access("get_memory_state", list(memory_data.keys()))
            
            # Update last snapshot time
            self.last_snapshot_time = datetime.utcnow()
            
            # Create snapshot if tracking changes
            if self.settings["track_changes"]:
                await self._create_snapshot(memory_data)
            
            # Determine detail level based on mode
            detail_level = self.settings["detail_level"]
            
            # Prepare response with appropriate detail level
            response = {
                "loop_id": self.loop_id,
                "timestamp": self.last_snapshot_time.isoformat(),
                "mode": self.mode,
                "memory": memory_data,
                "metadata": {
                    "key_count": len(memory_data),
                    "access_level": self.access_level,
                    "filtered": filter_options is not None,
                    "detail_level": detail_level
                }
            }
            
            # Add additional metadata for higher detail levels
            if detail_level in ["detailed", "comprehensive"]:
                response["metadata"]["snapshot_count"] = self.snapshot_count
                response["metadata"]["last_snapshot_time"] = self.last_snapshot_time.isoformat()
                
                if self.settings["track_changes"] and self.snapshot_count > 1:
                    # Add change statistics
                    latest_snapshot = self.snapshots.get(self.last_snapshot_time.isoformat(), {})
                    previous_snapshots = [s for t, s in self.snapshots.items() if t != self.last_snapshot_time.isoformat()]
                    
                    if previous_snapshots:
                        previous_snapshot = previous_snapshots[-1]
                        diff = self._compute_diff(previous_snapshot, latest_snapshot)
                        
                        response["metadata"]["changes"] = {
                            "added": len(diff.added),
                            "removed": len(diff.removed),
                            "modified": len(diff.modified),
                            "unchanged": len(diff.unchanged)
                        }
            
            # Add research-specific data if applicable
            if self.mode == "research" and detail_level == "comprehensive":
                response["metadata"]["research"] = {
                    "uncertainty_tracking": self.settings["research_specific"]["track_uncertainty"],
                    "alternatives_tracking": self.settings["research_specific"]["track_alternatives"],
                    "exploration_enabled": self.settings["research_specific"]["enable_memory_exploration"],
                    "counterfactual_analysis": self.settings["research_specific"]["enable_counterfactual_analysis"]
                }
            
            return response
        except Exception as e:
            logger.error(f"Error getting memory state: {str(e)}")
            return {
                "loop_id": self.loop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "memory": {},
                "metadata": {
                    "error": str(e),
                    "key_count": 0,
                    "access_level": self.access_level
                }
            }
    
    async def get_memory_value(self, key: str) -> Dict[str, Any]:
        """
        Get a specific memory value by key.
        
        Args:
            key: The memory key to retrieve
            
        Returns:
            Dictionary containing the memory value and metadata
        """
        logger.info(f"Getting memory value for key {key} in loop {self.loop_id}")
        
        try:
            # In a real implementation, this would fetch from a database or memory service
            # For this implementation, we'll simulate fetching memory
            memory_data = await self._fetch_memory_data()
            
            if key not in memory_data:
                return {
                    "loop_id": self.loop_id,
                    "key": key,
                    "found": False,
                    "timestamp": datetime.utcnow().isoformat(),
                    "mode": self.mode,
                    "error": "Key not found"
                }
            
            # Record access for auditing
            await self._record_memory_access("get_memory_value", [key])
            
            # Determine detail level based on mode
            detail_level = self.settings["detail_level"]
            
            # Prepare response with appropriate detail level
            response = {
                "loop_id": self.loop_id,
                "key": key,
                "found": True,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "value": memory_data[key].get("value")
            }
            
            # Add metadata based on detail level
            if detail_level == "minimal":
                response["metadata"] = {
                    "value_type": type(memory_data[key].get("value")).__name__
                }
            elif detail_level == "standard":
                response["metadata"] = {
                    "created_at": memory_data[key].get("created_at"),
                    "created_by": memory_data[key].get("created_by"),
                    "last_modified": memory_data[key].get("last_modified"),
                    "value_type": type(memory_data[key].get("value")).__name__
                }
            else:  # detailed or comprehensive
                response["metadata"] = {
                    "created_at": memory_data[key].get("created_at"),
                    "created_by": memory_data[key].get("created_by"),
                    "last_modified": memory_data[key].get("last_modified"),
                    "last_modified_by": memory_data[key].get("last_modified_by"),
                    "access_count": memory_data[key].get("access_count", 0),
                    "value_type": type(memory_data[key].get("value")).__name__
                }
                
                # Add history if available and in comprehensive mode
                if detail_level == "comprehensive" and "access_history" in memory_data[key]:
                    response["metadata"]["access_history"] = memory_data[key]["access_history"]
            
            # Add research-specific data if applicable
            if self.mode == "research" and detail_level == "comprehensive":
                if "uncertainty" in memory_data[key]:
                    response["metadata"]["uncertainty"] = memory_data[key]["uncertainty"]
                if "alternatives" in memory_data[key]:
                    response["metadata"]["alternatives"] = memory_data[key]["alternatives"]
            
            return response
        except Exception as e:
            logger.error(f"Error getting memory value: {str(e)}")
            return {
                "loop_id": self.loop_id,
                "key": key,
                "found": False,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": str(e)
            }
    
    async def set_memory_value(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Set a memory value (requires READ_WRITE or ADMIN access level).
        
        Args:
            key: The memory key to set
            value: The value to set
            metadata: Optional metadata to set
            
        Returns:
            Dictionary containing the result of the operation
        """
        logger.info(f"Setting memory value for key {key} in loop {self.loop_id}")
        
        # Check access level
        if self.access_level == MemoryAccessLevel.READ_ONLY:
            logger.warning(f"Cannot set memory value with READ_ONLY access level in {self.mode} mode")
            return {
                "loop_id": self.loop_id,
                "key": key,
                "success": False,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": "Insufficient access level (READ_ONLY)"
            }
        
        try:
            # In a real implementation, this would update a database or memory service
            # For this implementation, we'll simulate updating memory
            memory_data = await self._fetch_memory_data()
            
            # Create or update memory entry
            now = datetime.utcnow()
            
            if key in memory_data:
                # Update existing entry
                memory_data[key]["value"] = value
                memory_data[key]["last_modified"] = now.isoformat()
                memory_data[key]["last_modified_by"] = "memory_inspector"
                memory_data[key]["access_count"] = memory_data[key].get("access_count", 0) + 1
                
                # Update metadata if provided
                if metadata:
                    for meta_key, meta_value in metadata.items():
                        memory_data[key][meta_key] = meta_value
            else:
                # Create new entry
                memory_data[key] = {
                    "value": value,
                    "created_at": now.isoformat(),
                    "created_by": "memory_inspector",
                    "last_modified": now.isoformat(),
                    "last_modified_by": "memory_inspector",
                    "access_count": 1,
                    "value_type": type(value).__name__
                }
                
                # Add metadata if provided
                if metadata:
                    for meta_key, meta_value in metadata.items():
                        memory_data[key][meta_key] = meta_value
            
            # Record access for auditing
            await self._record_memory_access("set_memory_value", [key])
            
            # Update last snapshot time
            self.last_snapshot_time = now
            
            # Create snapshot if tracking changes
            if self.settings["track_changes"]:
                await self._create_snapshot(memory_data)
            
            # Notify watchers if any
            if key in self.watchers:
                for watcher in self.watchers[key]:
                    await watcher(key, value, "set")
            
            return {
                "loop_id": self.loop_id,
                "key": key,
                "success": True,
                "timestamp": now.isoformat(),
                "mode": self.mode,
                "metadata": {
                    "operation": "set",
                    "previous_value_exists": key in memory_data,
                    "value_type": type(value).__name__
                }
            }
        except Exception as e:
            logger.error(f"Error setting memory value: {str(e)}")
            return {
                "loop_id": self.loop_id,
                "key": key,
                "success": False,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": str(e)
            }
    
    async def delete_memory_value(self, key: str) -> Dict[str, Any]:
        """
        Delete a memory value (requires ADMIN access level).
        
        Args:
            key: The memory key to delete
            
        Returns:
            Dictionary containing the result of the operation
        """
        logger.info(f"Deleting memory value for key {key} in loop {self.loop_id}")
        
        # Check access level
        if self.access_level != MemoryAccessLevel.ADMIN:
            logger.warning(f"Cannot delete memory value without ADMIN access level in {self.mode} mode")
            return {
                "loop_id": self.loop_id,
                "key": key,
                "success": False,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": "Insufficient access level (requires ADMIN)"
            }
        
        try:
            # In a real implementation, this would update a database or memory service
            # For this implementation, we'll simulate updating memory
            memory_data = await self._fetch_memory_data()
            
            if key not in memory_data:
                return {
                    "loop_id": self.loop_id,
                    "key": key,
                    "success": False,
                    "timestamp": datetime.utcnow().isoformat(),
                    "mode": self.mode,
                    "error": "Key not found"
                }
            
            # Store value for response
            old_value = memory_data[key].get("value")
            
            # Delete the key
            del memory_data[key]
            
            # Record access for auditing
            await self._record_memory_access("delete_memory_value", [key])
            
            # Update last snapshot time
            self.last_snapshot_time = datetime.utcnow()
            
            # Create snapshot if tracking changes
            if self.settings["track_changes"]:
                await self._create_snapshot(memory_data)
            
            # Notify watchers if any
            if key in self.watchers:
                for watcher in self.watchers[key]:
                    await watcher(key, None, "delete")
                
                # Remove watchers for this key
                del self.watchers[key]
            
            return {
                "loop_id": self.loop_id,
                "key": key,
                "success": True,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "metadata": {
                    "operation": "delete",
                    "previous_value_type": type(old_value).__name__
                }
            }
        except Exception as e:
            logger.error(f"Error deleting memory value: {str(e)}")
            return {
                "loop_id": self.loop_id,
                "key": key,
                "success": False,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": str(e)
            }
    
    async def get_memory_snapshot(self, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a memory snapshot at a specific time (requires time travel to be enabled).
        
        Args:
            timestamp: Optional timestamp to get snapshot for (defaults to latest)
            
        Returns:
            Dictionary containing the memory snapshot
        """
        logger.info(f"Getting memory snapshot for loop {self.loop_id} at {timestamp or 'latest'}")
        
        # Check if time travel is enabled
        if not self.settings["enable_time_travel"] and timestamp is not None:
            logger.warning(f"Time travel not enabled in {self.mode} mode")
            return {
                "loop_id": self.loop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": "Time travel not enabled in this mode",
                "available_snapshots": self.snapshot_count
            }
        
        try:
            # If no timestamp provided, use latest
            if timestamp is None:
                if not self.snapshots:
                    # No snapshots available, fetch current state
                    memory_data = await self._fetch_memory_data()
                    snapshot_time = datetime.utcnow().isoformat()
                else:
                    # Use latest snapshot
                    snapshot_times = sorted(self.snapshots.keys())
                    snapshot_time = snapshot_times[-1]
                    memory_data = self.snapshots[snapshot_time]
            else:
                # Find closest snapshot to requested timestamp
                if not self.snapshots:
                    return {
                        "loop_id": self.loop_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "mode": self.mode,
                        "error": "No snapshots available",
                        "available_snapshots": 0
                    }
                
                # Find exact match or closest earlier snapshot
                snapshot_times = sorted(self.snapshots.keys())
                
                if timestamp in snapshot_times:
                    # Exact match
                    snapshot_time = timestamp
                    memory_data = self.snapshots[snapshot_time]
                else:
                    # Find closest earlier snapshot
                    earlier_snapshots = [t for t in snapshot_times if t < timestamp]
                    
                    if not earlier_snapshots:
                        return {
                            "loop_id": self.loop_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            "mode": self.mode,
                            "error": f"No snapshots available before {timestamp}",
                            "available_snapshots": self.snapshot_count,
                            "earliest_snapshot": snapshot_times[0] if snapshot_times else None
                        }
                    
                    snapshot_time = earlier_snapshots[-1]
                    memory_data = self.snapshots[snapshot_time]
            
            # Record access for auditing
            await self._record_memory_access("get_memory_snapshot", list(memory_data.keys()))
            
            return {
                "loop_id": self.loop_id,
                "timestamp": snapshot_time,
                "requested_timestamp": timestamp,
                "mode": self.mode,
                "memory": memory_data,
                "metadata": {
                    "key_count": len(memory_data),
                    "snapshot_count": self.snapshot_count,
                    "available_snapshots": list(self.snapshots.keys())
                }
            }
        except Exception as e:
            logger.error(f"Error getting memory snapshot: {str(e)}")
            return {
                "loop_id": self.loop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": str(e),
                "available_snapshots": self.snapshot_count
            }
    
    async def compare_memory_snapshots(self, timestamp1: str, timestamp2: str) -> Dict[str, Any]:
        """
        Compare two memory snapshots (requires time travel to be enabled).
        
        Args:
            timestamp1: First timestamp to compare
            timestamp2: Second timestamp to compare
            
        Returns:
            Dictionary containing the diff between snapshots
        """
        logger.info(f"Comparing memory snapshots for loop {self.loop_id} at {timestamp1} and {timestamp2}")
        
        # Check if time travel is enabled
        if not self.settings["enable_time_travel"]:
            logger.warning(f"Time travel not enabled in {self.mode} mode")
            return {
                "loop_id": self.loop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": "Time travel not enabled in this mode",
                "available_snapshots": self.snapshot_count
            }
        
        try:
            # Check if snapshots exist
            if not self.snapshots:
                return {
                    "loop_id": self.loop_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "mode": self.mode,
                    "error": "No snapshots available",
                    "available_snapshots": 0
                }
            
            # Find snapshots
            snapshot_times = sorted(self.snapshots.keys())
            
            # Find exact or closest matches for timestamp1
            if timestamp1 in snapshot_times:
                snapshot1_time = timestamp1
            else:
                earlier_snapshots = [t for t in snapshot_times if t < timestamp1]
                if not earlier_snapshots:
                    return {
                        "loop_id": self.loop_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "mode": self.mode,
                        "error": f"No snapshots available before {timestamp1}",
                        "available_snapshots": self.snapshot_count,
                        "earliest_snapshot": snapshot_times[0] if snapshot_times else None
                    }
                snapshot1_time = earlier_snapshots[-1]
            
            # Find exact or closest matches for timestamp2
            if timestamp2 in snapshot_times:
                snapshot2_time = timestamp2
            else:
                earlier_snapshots = [t for t in snapshot_times if t < timestamp2]
                if not earlier_snapshots:
                    return {
                        "loop_id": self.loop_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "mode": self.mode,
                        "error": f"No snapshots available before {timestamp2}",
                        "available_snapshots": self.snapshot_count,
                        "earliest_snapshot": snapshot_times[0] if snapshot_times else None
                    }
                snapshot2_time = earlier_snapshots[-1]
            
            # Get snapshots
            snapshot1 = self.snapshots[snapshot1_time]
            snapshot2 = self.snapshots[snapshot2_time]
            
            # Compute diff
            diff = self._compute_diff(snapshot1, snapshot2)
            
            # Record access for auditing
            keys_accessed = list(diff.added.keys()) + list(diff.removed.keys()) + list(diff.modified.keys()) + list(diff.unchanged.keys())
            await self._record_memory_access("compare_memory_snapshots", keys_accessed)
            
            return {
                "loop_id": self.loop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "snapshot1": {
                    "timestamp": snapshot1_time,
                    "requested_timestamp": timestamp1,
                    "key_count": len(snapshot1)
                },
                "snapshot2": {
                    "timestamp": snapshot2_time,
                    "requested_timestamp": timestamp2,
                    "key_count": len(snapshot2)
                },
                "diff": {
                    "added": diff.added,
                    "removed": diff.removed,
                    "modified": diff.modified,
                    "unchanged": len(diff.unchanged)
                },
                "metadata": {
                    "total_changes": len(diff.added) + len(diff.removed) + len(diff.modified),
                    "unchanged_count": len(diff.unchanged),
                    "available_snapshots": self.snapshot_count
                }
            }
        except Exception as e:
            logger.error(f"Error comparing memory snapshots: {str(e)}")
            return {
                "loop_id": self.loop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": str(e),
                "available_snapshots": self.snapshot_count
            }
    
    async def export_memory(self, format: MemoryFormat = MemoryFormat.JSON) -> Dict[str, Any]:
        """
        Export memory data in the specified format.
        
        Args:
            format: The format to export in
            
        Returns:
            Dictionary containing the exported memory data
        """
        logger.info(f"Exporting memory for loop {self.loop_id} in {format} format")
        
        try:
            # Get current memory state
            memory_data = await self._fetch_memory_data()
            
            # Record access for auditing
            await self._record_memory_access("export_memory", list(memory_data.keys()))
            
            # Export in the specified format
            if format == MemoryFormat.JSON:
                export_data = json.dumps(memory_data, indent=2)
            elif format == MemoryFormat.TREE:
                # Simple tree format (would be more sophisticated in a real implementation)
                export_data = self._format_as_tree(memory_data)
            elif format == MemoryFormat.TABLE:
                # Simple table format (would be more sophisticated in a real implementation)
                export_data = self._format_as_table(memory_data)
            elif format == MemoryFormat.GRAPH:
                # Simple graph format (would be more sophisticated in a real implementation)
                export_data = self._format_as_graph(memory_data)
            else:
                export_data = json.dumps(memory_data, indent=2)
            
            return {
                "loop_id": self.loop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "format": format,
                "data": export_data,
                "metadata": {
                    "key_count": len(memory_data),
                    "export_size": len(export_data)
                }
            }
        except Exception as e:
            logger.error(f"Error exporting memory: {str(e)}")
            return {
                "loop_id": self.loop_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mode": self.mode,
                "error": str(e)
            }
    
    def change_mode(self, new_mode: str) -> None:
        """
        Change the inspector mode.
        
        Args:
            new_mode: The new mode to use
        """
        logger.info(f"Changing mode from {self.mode} to {new_mode} for loop {self.loop_id}")
        
        self.mode = new_mode.lower() if new_mode else "balanced"
        
        # Update settings based on new mode
        if self.mode in MODE_MEMORY_SETTINGS:
            self.settings = MODE_MEMORY_SETTINGS[self.mode]
        else:
            self.settings = MODE_MEMORY_SETTINGS["balanced"]
            
        self.access_level = self.settings["access_level"]
        self.max_snapshots = self.settings["max_snapshots"]
    
    async def _fetch_memory_data(self) -> Dict[str, Any]:
        """
        Fetch memory data from the memory service.
        
        Returns:
            Dictionary containing memory data
        """
        # In a real implementation, this would fetch from a database or memory service
        # For this implementation, we'll return a simulated memory state
        return {
            "task_description": {
                "value": f"Sample task for loop {self.loop_id}",
                "created_at": "2025-04-21T10:00:00.000Z",
                "created_by": "user",
                "last_modified": "2025-04-21T10:00:00.000Z",
                "value_type": "str"
            },
            "loop_count": {
                "value": 1,
                "created_at": "2025-04-21T10:00:00.000Z",
                "created_by": "orchestrator",
                "last_modified": "2025-04-21T10:00:00.000Z",
                "value_type": "int"
            },
            "agent_results": {
                "value": {
                    "HAL": "Completed analysis",
                    "NOVA": "Generated solution"
                },
                "created_at": "2025-04-21T10:05:00.000Z",
                "created_by": "orchestrator",
                "last_modified": "2025-04-21T10:05:00.000Z",
                "value_type": "dict"
            }
        }
    
    async def _record_memory_access(self, operation: str, keys: List[str]) -> None:
        """
        Record memory access for auditing.
        
        Args:
            operation: The operation performed
            keys: The keys accessed
        """
        # In a real implementation, this would record to a database or audit log
        logger.debug(f"Memory access: {operation} on keys {keys} in loop {self.loop_id}")
    
    async def _create_snapshot(self, memory_data: Dict[str, Any]) -> None:
        """
        Create a memory snapshot.
        
        Args:
            memory_data: The memory data to snapshot
        """
        # Create a deep copy of the memory data
        snapshot = json.loads(json.dumps(memory_data))
        
        # Store snapshot with current timestamp
        timestamp = datetime.utcnow().isoformat()
        self.snapshots[timestamp] = snapshot
        self.snapshot_count += 1
        
        # Limit number of snapshots based on mode
        if len(self.snapshots) > self.max_snapshots:
            # Remove oldest snapshot
            oldest_timestamp = min(self.snapshots.keys())
            del self.snapshots[oldest_timestamp]
    
    def _compute_diff(self, snapshot1: Dict[str, Any], snapshot2: Dict[str, Any]) -> MemoryDiff:
        """
        Compute the difference between two memory snapshots.
        
        Args:
            snapshot1: First snapshot
            snapshot2: Second snapshot
            
        Returns:
            MemoryDiff object containing the differences
        """
        diff = MemoryDiff()
        
        # Find keys in snapshot2 but not in snapshot1 (added)
        for key in snapshot2:
            if key not in snapshot1:
                diff.added[key] = snapshot2[key]
        
        # Find keys in snapshot1 but not in snapshot2 (removed)
        for key in snapshot1:
            if key not in snapshot2:
                diff.removed[key] = snapshot1[key]
        
        # Find keys in both but with different values (modified)
        for key in snapshot1:
            if key in snapshot2:
                # Compare values
                if snapshot1[key].get("value") != snapshot2[key].get("value"):
                    diff.modified[key] = {
                        "before": snapshot1[key],
                        "after": snapshot2[key]
                    }
                else:
                    diff.unchanged[key] = snapshot2[key]
        
        return diff
    
    def _format_as_tree(self, memory_data: Dict[str, Any]) -> str:
        """
        Format memory data as a tree.
        
        Args:
            memory_data: The memory data to format
            
        Returns:
            String containing the formatted tree
        """
        result = []
        
        for key, value in memory_data.items():
            result.append(f"- {key}")
            result.append(f"  - Value: {value.get('value')}")
            result.append(f"  - Type: {type(value.get('value')).__name__}")
            result.append(f"  - Created: {value.get('created_at')} by {value.get('created_by')}")
            result.append(f"  - Modified: {value.get('last_modified')}")
        
        return "\n".join(result)
    
    def _format_as_table(self, memory_data: Dict[str, Any]) -> str:
        """
        Format memory data as a table.
        
        Args:
            memory_data: The memory data to format
            
        Returns:
            String containing the formatted table
        """
        result = []
        
        # Header
        result.append("| Key | Value | Type | Created | Modified |")
        result.append("|-----|-------|------|---------|----------|")
        
        # Rows
        for key, value in memory_data.items():
            value_str = str(value.get("value"))
            if len(value_str) > 30:
                value_str = value_str[:27] + "..."
            
            result.append(f"| {key} | {value_str} | {type(value.get('value')).__name__} | {value.get('created_at')} | {value.get('last_modified')} |")
        
        return "\n".join(result)
    
    def _format_as_graph(self, memory_data: Dict[str, Any]) -> str:
        """
        Format memory data as a graph.
        
        Args:
            memory_data: The memory data to format
            
        Returns:
            String containing the formatted graph (DOT format)
        """
        result = ["digraph Memory {"]
        result.append("  node [shape=box];")
        
        # Add nodes for each memory key
        for key, value in memory_data.items():
            value_str = str(value.get("value"))
            if len(value_str) > 30:
                value_str = value_str[:27] + "..."
            
            result.append(f'  "{key}" [label="{key}\\nValue: {value_str}\\nType: {type(value.get("value")).__name__}"];')
        
        # Add edges based on creation relationships
        creators = {}
        for key, value in memory_data.items():
            creator = value.get("created_by")
            if creator not in creators:
                creators[creator] = []
            creators[creator].append(key)
        
        for creator, keys in creators.items():
            result.append(f'  "{creator}" [shape=ellipse];')
            for key in keys:
                result.append(f'  "{creator}" -> "{key}" [label="created"];')
        
        result.append("}")
        return "\n".join(result)

def create_memory_inspector(loop_id: str, mode: str = "balanced") -> MemoryInspector:
    """
    Create a memory inspector for a loop.
    
    Args:
        loop_id: The ID of the loop to inspect
        mode: The orchestrator mode (fast, balanced, thorough, research)
        
    Returns:
        MemoryInspector instance
    """
    return MemoryInspector(loop_id, mode)

def inspect_memory(loop_id: str, mode: str = "balanced", filter_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Inspect memory for a loop (synchronous wrapper).
    
    Args:
        loop_id: The ID of the loop to inspect
        mode: The orchestrator mode (fast, balanced, thorough, research)
        filter_options: Optional filter to apply to the memory data
        
    Returns:
        Dictionary containing the memory state
    """
    inspector = create_memory_inspector(loop_id, mode)
    
    # Convert filter options to MemoryFilter if provided
    memory_filter = None
    if filter_options:
        memory_filter = MemoryFilter(**filter_options)
    
    # Create event loop if needed
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run the async method
    return loop.run_until_complete(inspector.get_memory_state(memory_filter))

def should_snapshot_memory(mode: str, event_type: str) -> bool:
    """
    Determine if memory should be snapshotted for a given mode and event type.
    
    Args:
        mode: The orchestrator mode (fast, balanced, thorough, research)
        event_type: The event type (agent_completion, reflection, decision, loop_end)
        
    Returns:
        True if memory should be snapshotted, False otherwise
    """
    mode = mode.lower() if mode else "balanced"
    
    # Get snapshot frequency for the mode
    if mode in MODE_MEMORY_SETTINGS:
        snapshot_frequency = MODE_MEMORY_SETTINGS[mode]["snapshot_frequency"]
    else:
        snapshot_frequency = MODE_MEMORY_SETTINGS["balanced"]["snapshot_frequency"]
    
    # Determine if snapshot should be taken based on frequency and event type
    if snapshot_frequency == "end_only":
        return event_type == "loop_end"
    elif snapshot_frequency == "agent_completion":
        return event_type in ["agent_completion", "loop_end"]
    elif snapshot_frequency == "real_time":
        return True  # Snapshot for all events
    else:
        return False
