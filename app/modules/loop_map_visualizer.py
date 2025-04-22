"""
Loop Map Visualizer Module

This module implements the Loop Map Visualizer functionality, which provides
a visual representation of loop execution paths, agent interactions, and
memory state transitions. It generates both JSON data structures for API
consumption and HTML/SVG visualizations for human viewing.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import base64
from enum import Enum
import sys

# Import schema validation module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from app.modules.schema_validation import validate_schema, validate_before_export
except ImportError:
    # Fallback if direct import fails
    try:
        from schema_validation import validate_schema, validate_before_export
    except ImportError:
        # Final fallback with stub functions
        def validate_schema(*args, **kwargs): return True, None
        def validate_before_export(*args, **kwargs): return True, None

# Configure logging
try:
    log_dir = '/tmp'
    logging.basicConfig(
        filename=f'{log_dir}/schema_trace.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
except Exception:
    # Fallback to console logging if file logging fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

class VisualizationFormat(str, Enum):
    """Enum for visualization output formats"""
    JSON = "json"
    HTML = "html"
    SVG = "svg"
    PNG = "png"
    DOT = "dot"  # GraphViz dot format

class NodeType(str, Enum):
    """Enum for node types in the visualization"""
    AGENT = "agent"
    MEMORY = "memory"
    DECISION = "decision"
    REFLECTION = "reflection"
    LOOP_START = "loop_start"
    LOOP_END = "loop_end"
    RERUN = "rerun"
    OPERATOR = "operator"
    MODE_CHANGE = "mode_change"
    DEPTH_CHANGE = "depth_change"

class EdgeType(str, Enum):
    """Enum for edge types in the visualization"""
    EXECUTION = "execution"
    MEMORY_ACCESS = "memory_access"
    DECISION = "decision"
    REFLECTION = "reflection"
    RERUN = "rerun"
    OPERATOR = "operator"
    MODE_TRANSITION = "mode_transition"
    DEPTH_TRANSITION = "depth_transition"

# Color schemes for different visualization elements
COLOR_SCHEMES = {
    "default": {
        NodeType.AGENT: "#4285F4",  # Google Blue
        NodeType.MEMORY: "#34A853",  # Google Green
        NodeType.DECISION: "#FBBC05",  # Google Yellow
        NodeType.REFLECTION: "#EA4335",  # Google Red
        NodeType.LOOP_START: "#9C27B0",  # Purple
        NodeType.LOOP_END: "#9C27B0",  # Purple
        NodeType.RERUN: "#FF9800",  # Orange
        NodeType.OPERATOR: "#607D8B",  # Blue Grey
        NodeType.MODE_CHANGE: "#00BCD4",  # Cyan
        NodeType.DEPTH_CHANGE: "#3F51B5",  # Indigo
        
        EdgeType.EXECUTION: "#4285F4",  # Google Blue
        EdgeType.MEMORY_ACCESS: "#34A853",  # Google Green
        EdgeType.DECISION: "#FBBC05",  # Google Yellow
        EdgeType.REFLECTION: "#EA4335",  # Google Red
        EdgeType.RERUN: "#FF9800",  # Orange
        EdgeType.OPERATOR: "#607D8B",  # Blue Grey
        EdgeType.MODE_TRANSITION: "#00BCD4",  # Cyan
        EdgeType.DEPTH_TRANSITION: "#3F51B5",  # Indigo
    },
    "dark": {
        NodeType.AGENT: "#8AB4F8",  # Light Blue
        NodeType.MEMORY: "#81C995",  # Light Green
        NodeType.DECISION: "#FDD663",  # Light Yellow
        NodeType.REFLECTION: "#F28B82",  # Light Red
        NodeType.LOOP_START: "#D1A7F1",  # Light Purple
        NodeType.LOOP_END: "#D1A7F1",  # Light Purple
        NodeType.RERUN: "#FFBD45",  # Light Orange
        NodeType.OPERATOR: "#9AA0A6",  # Light Grey
        NodeType.MODE_CHANGE: "#80DEEA",  # Light Cyan
        NodeType.DEPTH_CHANGE: "#9FA8DA",  # Light Indigo
        
        EdgeType.EXECUTION: "#8AB4F8",  # Light Blue
        EdgeType.MEMORY_ACCESS: "#81C995",  # Light Green
        EdgeType.DECISION: "#FDD663",  # Light Yellow
        EdgeType.REFLECTION: "#F28B82",  # Light Red
        EdgeType.RERUN: "#FFBD45",  # Light Orange
        EdgeType.OPERATOR: "#9AA0A6",  # Light Grey
        EdgeType.MODE_TRANSITION: "#80DEEA",  # Light Cyan
        EdgeType.DEPTH_TRANSITION: "#9FA8DA",  # Light Indigo
    },
    "accessibility": {
        NodeType.AGENT: "#1A73E8",  # Accessible Blue
        NodeType.MEMORY: "#188038",  # Accessible Green
        NodeType.DECISION: "#E37400",  # Accessible Yellow
        NodeType.REFLECTION: "#D93025",  # Accessible Red
        NodeType.LOOP_START: "#7B1FA2",  # Accessible Purple
        NodeType.LOOP_END: "#7B1FA2",  # Accessible Purple
        NodeType.RERUN: "#E65100",  # Accessible Orange
        NodeType.OPERATOR: "#455A64",  # Accessible Blue Grey
        NodeType.MODE_CHANGE: "#0097A7",  # Accessible Cyan
        NodeType.DEPTH_CHANGE: "#303F9F",  # Accessible Indigo
        
        EdgeType.EXECUTION: "#1A73E8",  # Accessible Blue
        EdgeType.MEMORY_ACCESS: "#188038",  # Accessible Green
        EdgeType.DECISION: "#E37400",  # Accessible Yellow
        EdgeType.REFLECTION: "#D93025",  # Accessible Red
        EdgeType.RERUN: "#E65100",  # Accessible Orange
        EdgeType.OPERATOR: "#455A64",  # Accessible Blue Grey
        EdgeType.MODE_TRANSITION: "#0097A7",  # Accessible Cyan
        EdgeType.DEPTH_TRANSITION: "#303F9F",  # Accessible Indigo
    }
}

def create_visualizer(*args, **kwargs):
    """
    Stub function for creating a visualizer instance.
    This function is required for backend boot but is not fully implemented.
    
    Returns:
        Dictionary with status message indicating stub implementation
    """
    logger.info("create_visualizer stub function called")
    return {"status": "Visualizer not implemented. Stub function active."}

def visualize_loop(*args, **kwargs):
    """
    Stub function for visualizing a loop trace.
    This function is required for backend boot but is not fully implemented.
    
    Returns:
        Dictionary with status message indicating stub implementation
    """
    logger.info("visualize_loop stub function called")
    return {"status": "Loop visualization not implemented. Stub function active."}

# Load visual settings schema
def load_visual_settings(mode: str) -> Dict[str, Any]:
    """
    Load visual settings for the specified mode from schema.
    
    Args:
        mode: The orchestrator mode (fast, balanced, thorough, research)
        
    Returns:
        Dictionary containing the visual settings
    """
    # Default settings if schema validation fails
    default_settings = {
        "detail_level": "standard",
        "node_types_to_show": [
            "agent", "memory", "decision", "reflection", 
            "loop_start", "loop_end", "rerun", "mode_change", "depth_change"
        ],
        "edge_types_to_show": [
            "execution", "memory_access", "decision", "reflection", 
            "rerun", "mode_transition", "depth_transition"
        ],
        "include_timestamps": True,
        "include_memory_details": True,
        "include_agent_details": True,
        "include_decision_details": True,
        "update_frequency": "agent_completion"
    }
    
    # Define settings based on mode
    if mode == "fast":
        settings = {
            "detail_level": "minimal",
            "node_types_to_show": [
                "agent", "loop_start", "loop_end", "rerun", "mode_change"
            ],
            "edge_types_to_show": [
                "execution", "rerun", "mode_transition"
            ],
            "include_timestamps": False,
            "include_memory_details": False,
            "include_agent_details": False,
            "include_decision_details": False,
            "update_frequency": "end_only"
        }
    elif mode == "balanced":
        settings = default_settings
    elif mode == "thorough":
        settings = {
            "detail_level": "detailed",
            "node_types_to_show": [
                "agent", "memory", "decision", "reflection", 
                "loop_start", "loop_end", "rerun", "operator",
                "mode_change", "depth_change"
            ],
            "edge_types_to_show": [
                "execution", "memory_access", "decision", "reflection", 
                "rerun", "operator", "mode_transition", "depth_transition"
            ],
            "include_timestamps": True,
            "include_memory_details": True,
            "include_agent_details": True,
            "include_decision_details": True,
            "update_frequency": "real_time"
        }
    elif mode == "research":
        settings = {
            "detail_level": "comprehensive",
            "node_types_to_show": [
                "agent", "memory", "decision", "reflection", 
                "loop_start", "loop_end", "rerun", "operator",
                "mode_change", "depth_change"
            ],
            "edge_types_to_show": [
                "execution", "memory_access", "decision", "reflection", 
                "rerun", "operator", "mode_transition", "depth_transition"
            ],
            "include_timestamps": True,
            "include_memory_details": True,
            "include_agent_details": True,
            "include_decision_details": True,
            "include_uncertainty": True,
            "track_alternatives": True,
            "update_frequency": "real_time"
        }
    else:
        settings = default_settings
    
    # Validate settings against schema
    is_valid, error = validate_schema(settings, 'visual_settings')
    if not is_valid:
        logger.error(f"Invalid visual settings for mode {mode}: {error}")
        logger.warning(f"Using default visual settings for mode {mode}")
        return default_settings
    
    logger.info(f"Visual settings for mode {mode} validated successfully")
    return settings

class LoopMapVisualizer:
    """
    Class for generating visualizations of loop execution paths.
    """
    
    def __init__(self, loop_id: str, mode: str = "balanced", color_scheme: str = "default"):
        """
        Initialize the loop map visualizer.
        
        Args:
            loop_id: The ID of the loop to visualize
            mode: The orchestrator mode (fast, balanced, thorough, research)
            color_scheme: The color scheme to use for visualization (default, dark, accessibility)
        """
        self.loop_id = loop_id
        self.mode = mode.lower() if mode else "balanced"
        self.color_scheme = color_scheme if color_scheme in COLOR_SCHEMES else "default"
        self.nodes = []
        self.edges = []
        self.metadata = {
            "loop_id": loop_id,
            "mode": self.mode,
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        }
        
        # Load visualization settings based on mode from schema
        self.settings = load_visual_settings(self.mode)
        
        logger.info(f"Initialized LoopMapVisualizer for loop {loop_id} with {self.mode} mode and {color_scheme} color scheme")
    
    def add_node(self, node_id: str, node_type: NodeType, label: str, data: Dict[str, Any]) -> None:
        """
        Add a node to the visualization.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of the node
            label: Display label for the node
            data: Node-specific data
        """
        self.nodes.append({
            "id": node_id,
            "type": node_type,
            "label": label,
            "data": data
        })
    
    def add_edge(self, source: str, target: str, edge_type: EdgeType, label: str, data: Dict[str, Any]) -> None:
        """
        Add an edge to the visualization.
        
        Args:
            source: ID of the source node
            target: ID of the target node
            edge_type: Type of the edge
            label: Display label for the edge
            data: Edge-specific data
        """
        self.edges.append({
            "source": source,
            "target": target,
            "type": edge_type,
            "label": label,
            "data": data
        })
    
    def generate_map_from_trace(self, loop_trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a loop map from a loop trace.
        
        Args:
            loop_trace: The loop trace data
            
        Returns:
            Dictionary containing the loop map data
        """
        logger.info(f"Generating loop map for loop {self.loop_id} in {self.mode} mode")
        
        try:
            # Reset nodes and edges
            self.nodes = []
            self.edges = []
            
            # Extract loop data
            loop_count = loop_trace.get("loop_count", 1)
            trace_items = loop_trace.get("trace", [])
            current_mode = loop_trace.get("mode", self.mode)
            
            # Update mode if different from initialization
            if current_mode != self.mode:
                self.mode = current_mode
                self.settings = load_visual_settings(self.mode)
                self.metadata["mode"] = self.mode
            
            # Add loop start node
            start_node_id = f"loop_start_{self.loop_id}"
            self.add_node(
                node_id=start_node_id,
                node_type=NodeType.LOOP_START,
                label=f"Loop {self.loop_id} Start",
                data={
                    "loop_id": self.loop_id,
                    "timestamp": loop_trace.get("start_time", datetime.utcnow().isoformat()),
                    "loop_count": loop_count,
                    "mode": current_mode
                }
            )
            
            # Track the last node ID for connecting edges
            last_node_id = start_node_id
            
            # Process trace items
            for item in trace_items:
                item_type = item.get("type")
                timestamp = item.get("timestamp", datetime.utcnow().isoformat())
                
                if item_type == "agent_execution":
                    # Add agent node
                    agent_name = item.get("agent_name")
                    agent_node_id = f"agent_{agent_name}_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "agent" in self.settings["node_types_to_show"]:
                        agent_data = {
                            "agent_name": agent_name,
                            "timestamp": timestamp,
                            "status": item.get("status"),
                            "mode": item.get("mode", current_mode)
                        }
                        
                        # Add additional details if enabled for this mode
                        if self.settings["include_agent_details"]:
                            agent_data["duration"] = item.get("duration")
                            agent_data["depth"] = item.get("depth")
                            agent_data["reflection_intensity"] = item.get("reflection_intensity")
                        
                        self.add_node(
                            node_id=agent_node_id,
                            node_type=NodeType.AGENT,
                            label=f"Agent: {agent_name}",
                            data=agent_data
                        )
                        
                        # Connect from last node
                        if "execution" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=agent_node_id,
                                edge_type=EdgeType.EXECUTION,
                                label="Executes",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = agent_node_id
                    
                    # If agent accessed memory, add memory node and edge
                    if "memory_access" in item and "memory" in self.settings["node_types_to_show"]:
                        memory_access = item.get("memory_access", [])
                        for memory_item in memory_access:
                            memory_key = memory_item.get("key")
                            memory_node_id = f"memory_{memory_key}_{timestamp}"
                            
                            memory_data = {
                                "memory_key": memory_key,
                                "timestamp": timestamp,
                                "operation": memory_item.get("operation")
                            }
                            
                            # Add additional details if enabled for this mode
                            if self.settings["include_memory_details"]:
                                memory_data["value_type"] = memory_item.get("value_type")
                                memory_data["access_count"] = memory_item.get("access_count")
                            
                            self.add_node(
                                node_id=memory_node_id,
                                node_type=NodeType.MEMORY,
                                label=f"Memory: {memory_key}",
                                data=memory_data
                            )
                            
                            # Connect from agent node
                            if "memory_access" in self.settings["edge_types_to_show"]:
                                self.add_edge(
                                    source=agent_node_id,
                                    target=memory_node_id,
                                    edge_type=EdgeType.MEMORY_ACCESS,
                                    label=memory_item.get("operation"),
                                    data={"timestamp": timestamp}
                                )
                
                elif item_type == "decision":
                    # Add decision node
                    decision_id = item.get("decision_id")
                    decision_node_id = f"decision_{decision_id}_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "decision" in self.settings["node_types_to_show"]:
                        decision_data = {
                            "decision_id": decision_id,
                            "timestamp": timestamp,
                            "decision_type": item.get("decision_type"),
                            "outcome": item.get("outcome")
                        }
                        
                        # Add additional details if enabled for this mode
                        if self.settings["include_decision_details"]:
                            decision_data["confidence"] = item.get("confidence")
                            decision_data["alternatives"] = item.get("alternatives")
                        
                        self.add_node(
                            node_id=decision_node_id,
                            node_type=NodeType.DECISION,
                            label=f"Decision: {item.get('decision_type')}",
                            data=decision_data
                        )
                        
                        # Connect from last node
                        if "decision" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=decision_node_id,
                                edge_type=EdgeType.DECISION,
                                label="Decides",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = decision_node_id
                
                elif item_type == "reflection":
                    # Add reflection node
                    reflection_id = item.get("reflection_id")
                    reflection_node_id = f"reflection_{reflection_id}_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "reflection" in self.settings["node_types_to_show"]:
                        reflection_data = {
                            "reflection_id": reflection_id,
                            "timestamp": timestamp,
                            "reflection_type": item.get("reflection_type"),
                            "depth": item.get("depth", 0)
                        }
                        
                        self.add_node(
                            node_id=reflection_node_id,
                            node_type=NodeType.REFLECTION,
                            label=f"Reflection: {item.get('reflection_type')}",
                            data=reflection_data
                        )
                        
                        # Connect from last node
                        if "reflection" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=reflection_node_id,
                                edge_type=EdgeType.REFLECTION,
                                label="Reflects",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = reflection_node_id
                
                elif item_type == "rerun":
                    # Add rerun node
                    rerun_id = item.get("rerun_id")
                    rerun_node_id = f"rerun_{rerun_id}_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "rerun" in self.settings["node_types_to_show"]:
                        rerun_data = {
                            "rerun_id": rerun_id,
                            "timestamp": timestamp,
                            "reason": item.get("reason"),
                            "agent": item.get("agent")
                        }
                        
                        self.add_node(
                            node_id=rerun_node_id,
                            node_type=NodeType.RERUN,
                            label=f"Rerun: {item.get('agent')}",
                            data=rerun_data
                        )
                        
                        # Connect from last node
                        if "rerun" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=rerun_node_id,
                                edge_type=EdgeType.RERUN,
                                label="Reruns",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = rerun_node_id
                
                elif item_type == "operator_intervention":
                    # Add operator node
                    intervention_id = item.get("intervention_id")
                    operator_node_id = f"operator_{intervention_id}_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "operator" in self.settings["node_types_to_show"]:
                        operator_data = {
                            "intervention_id": intervention_id,
                            "timestamp": timestamp,
                            "action": item.get("action"),
                            "target": item.get("target")
                        }
                        
                        self.add_node(
                            node_id=operator_node_id,
                            node_type=NodeType.OPERATOR,
                            label=f"Operator: {item.get('action')}",
                            data=operator_data
                        )
                        
                        # Connect from last node
                        if "operator" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=operator_node_id,
                                edge_type=EdgeType.OPERATOR,
                                label="Intervenes",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = operator_node_id
                
                elif item_type == "mode_change":
                    # Add mode change node
                    mode_change_id = f"mode_change_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "mode_change" in self.settings["node_types_to_show"]:
                        mode_data = {
                            "timestamp": timestamp,
                            "old_mode": item.get("old_mode"),
                            "new_mode": item.get("new_mode"),
                            "reason": item.get("reason")
                        }
                        
                        self.add_node(
                            node_id=mode_change_id,
                            node_type=NodeType.MODE_CHANGE,
                            label=f"Mode Change: {item.get('old_mode')} → {item.get('new_mode')}",
                            data=mode_data
                        )
                        
                        # Connect from last node
                        if "mode_transition" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=mode_change_id,
                                edge_type=EdgeType.MODE_TRANSITION,
                                label="Changes Mode",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = mode_change_id
                        
                        # Update current mode
                        current_mode = item.get("new_mode")
                        self.mode = current_mode
                        self.settings = load_visual_settings(self.mode)
                        self.metadata["mode"] = self.mode
                
                elif item_type == "depth_change":
                    # Add depth change node
                    depth_change_id = f"depth_change_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "depth_change" in self.settings["node_types_to_show"]:
                        depth_data = {
                            "timestamp": timestamp,
                            "old_depth": item.get("old_depth"),
                            "new_depth": item.get("new_depth"),
                            "reason": item.get("reason")
                        }
                        
                        self.add_node(
                            node_id=depth_change_id,
                            node_type=NodeType.DEPTH_CHANGE,
                            label=f"Depth Change: {item.get('old_depth')} → {item.get('new_depth')}",
                            data=depth_data
                        )
                        
                        # Connect from last node
                        if "depth_transition" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=depth_change_id,
                                edge_type=EdgeType.DEPTH_TRANSITION,
                                label="Changes Depth",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = depth_change_id
            
            # Add loop end node if loop is complete
            if loop_trace.get("status") == "complete":
                end_node_id = f"loop_end_{self.loop_id}"
                self.add_node(
                    node_id=end_node_id,
                    node_type=NodeType.LOOP_END,
                    label=f"Loop {self.loop_id} End",
                    data={
                        "loop_id": self.loop_id,
                        "timestamp": loop_trace.get("end_time", datetime.utcnow().isoformat()),
                        "duration": loop_trace.get("duration"),
                        "status": "complete"
                    }
                )
                
                # Connect from last node
                if "execution" in self.settings["edge_types_to_show"]:
                    self.add_edge(
                        source=last_node_id,
                        target=end_node_id,
                        edge_type=EdgeType.EXECUTION,
                        label="Completes",
                        data={"timestamp": loop_trace.get("end_time", datetime.utcnow().isoformat())}
                    )
            
            # Prepare result
            result = {
                "loop_id": self.loop_id,
                "mode": self.mode,
                "generated_at": datetime.utcnow().isoformat(),
                "version": "1.0",
                "nodes": self.nodes,
                "edges": self.edges,
                "metadata": self.metadata
            }
            
            # Validate result before returning
            is_valid, error = validate_before_export(result)
            if not is_valid:
                logger.error(f"Invalid loop map for loop {self.loop_id}: {error}")
                return {"error": f"Failed to generate valid loop map: {error}"}
            
            logger.info(f"Successfully generated loop map for loop {self.loop_id} with {len(self.nodes)} nodes and {len(self.edges)} edges")
            return result
            
        except Exception as e:
            logger.error(f"Error generating loop map for loop {self.loop_id}: {str(e)}")
            return {"error": f"Failed to generate loop map: {str(e)}"}
