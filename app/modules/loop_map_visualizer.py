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

# Configure logging
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

# Mode-specific visualization settings
MODE_VISUALIZATION_SETTINGS = {
    "fast": {
        "detail_level": "minimal",
        "node_types_to_show": [
            NodeType.AGENT, 
            NodeType.LOOP_START, 
            NodeType.LOOP_END, 
            NodeType.RERUN,
            NodeType.MODE_CHANGE
        ],
        "edge_types_to_show": [
            EdgeType.EXECUTION, 
            EdgeType.RERUN,
            EdgeType.MODE_TRANSITION
        ],
        "include_timestamps": False,
        "include_memory_details": False,
        "include_agent_details": False,
        "include_decision_details": False,
        "update_frequency": "end_only"
    },
    "balanced": {
        "detail_level": "standard",
        "node_types_to_show": [
            NodeType.AGENT, 
            NodeType.MEMORY, 
            NodeType.DECISION, 
            NodeType.REFLECTION, 
            NodeType.LOOP_START, 
            NodeType.LOOP_END, 
            NodeType.RERUN,
            NodeType.MODE_CHANGE,
            NodeType.DEPTH_CHANGE
        ],
        "edge_types_to_show": [
            EdgeType.EXECUTION, 
            EdgeType.MEMORY_ACCESS, 
            EdgeType.DECISION, 
            EdgeType.REFLECTION, 
            EdgeType.RERUN,
            EdgeType.MODE_TRANSITION,
            EdgeType.DEPTH_TRANSITION
        ],
        "include_timestamps": True,
        "include_memory_details": True,
        "include_agent_details": True,
        "include_decision_details": True,
        "update_frequency": "agent_completion"
    },
    "thorough": {
        "detail_level": "detailed",
        "node_types_to_show": [
            NodeType.AGENT, 
            NodeType.MEMORY, 
            NodeType.DECISION, 
            NodeType.REFLECTION, 
            NodeType.LOOP_START, 
            NodeType.LOOP_END, 
            NodeType.RERUN, 
            NodeType.OPERATOR,
            NodeType.MODE_CHANGE,
            NodeType.DEPTH_CHANGE
        ],
        "edge_types_to_show": [
            EdgeType.EXECUTION, 
            EdgeType.MEMORY_ACCESS, 
            EdgeType.DECISION, 
            EdgeType.REFLECTION, 
            EdgeType.RERUN, 
            EdgeType.OPERATOR,
            EdgeType.MODE_TRANSITION,
            EdgeType.DEPTH_TRANSITION
        ],
        "include_timestamps": True,
        "include_memory_details": True,
        "include_agent_details": True,
        "include_decision_details": True,
        "update_frequency": "real_time"
    },
    "research": {
        "detail_level": "comprehensive",
        "node_types_to_show": [
            NodeType.AGENT, 
            NodeType.MEMORY, 
            NodeType.DECISION, 
            NodeType.REFLECTION, 
            NodeType.LOOP_START, 
            NodeType.LOOP_END, 
            NodeType.RERUN, 
            NodeType.OPERATOR,
            NodeType.MODE_CHANGE,
            NodeType.DEPTH_CHANGE
        ],
        "edge_types_to_show": [
            EdgeType.EXECUTION, 
            EdgeType.MEMORY_ACCESS, 
            EdgeType.DECISION, 
            EdgeType.REFLECTION, 
            EdgeType.RERUN, 
            EdgeType.OPERATOR,
            EdgeType.MODE_TRANSITION,
            EdgeType.DEPTH_TRANSITION
        ],
        "include_timestamps": True,
        "include_memory_details": True,
        "include_agent_details": True,
        "include_decision_details": True,
        "include_uncertainty": True,
        "track_alternatives": True,
        "update_frequency": "real_time"
    }
}

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
        
        # Set visualization settings based on mode
        if self.mode in MODE_VISUALIZATION_SETTINGS:
            self.settings = MODE_VISUALIZATION_SETTINGS[self.mode]
        else:
            self.settings = MODE_VISUALIZATION_SETTINGS["balanced"]
        
        logger.info(f"Initialized LoopMapVisualizer for loop {loop_id} with {self.mode} mode and {color_scheme} color scheme")
    
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
                if self.mode in MODE_VISUALIZATION_SETTINGS:
                    self.settings = MODE_VISUALIZATION_SETTINGS[self.mode]
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
                    if NodeType.AGENT in self.settings["node_types_to_show"]:
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
                        if EdgeType.EXECUTION in self.settings["edge_types_to_show"]:
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
                    if "memory_access" in item and NodeType.MEMORY in self.settings["node_types_to_show"]:
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
                            
                            # Connect agent to memory
                            if EdgeType.MEMORY_ACCESS in self.settings["edge_types_to_show"]:
                                self.add_edge(
                                    source=agent_node_id,
                                    target=memory_node_id,
                                    edge_type=EdgeType.MEMORY_ACCESS,
                                    label=memory_item.get("operation", "Accesses"),
                                    data={"timestamp": timestamp}
                                )
                
                elif item_type == "decision":
                    # Add decision node
                    decision_id = f"decision_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if NodeType.DECISION in self.settings["node_types_to_show"]:
                        decision_data = {
                            "decision_type": item.get("decision_type"),
                            "timestamp": timestamp,
                            "outcome": item.get("outcome"),
                            "mode": item.get("mode", current_mode)
                        }
                        
                        # Add additional details if enabled for this mode
                        if self.settings["include_decision_details"]:
                            decision_data["confidence"] = item.get("confidence")
                            decision_data["alternatives"] = item.get("alternatives")
                        
                        self.add_node(
                            node_id=decision_id,
                            node_type=NodeType.DECISION,
                            label=f"Decision: {item.get('decision_type')}",
                            data=decision_data
                        )
                        
                        # Connect from last node
                        if EdgeType.DECISION in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=decision_id,
                                edge_type=EdgeType.DECISION,
                                label=item.get("outcome", "Decides"),
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = decision_id
                
                elif item_type == "reflection":
                    # Add reflection node
                    reflection_id = f"reflection_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if NodeType.REFLECTION in self.settings["node_types_to_show"]:
                        reflection_data = {
                            "reflection_type": item.get("reflection_type"),
                            "timestamp": timestamp,
                            "agent": item.get("agent"),
                            "mode": item.get("mode", current_mode)
                        }
                        
                        self.add_node(
                            node_id=reflection_id,
                            node_type=NodeType.REFLECTION,
                            label=f"Reflection: {item.get('reflection_type')}",
                            data=reflection_data
                        )
                        
                        # Connect from last node
                        if EdgeType.REFLECTION in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=reflection_id,
                                edge_type=EdgeType.REFLECTION,
                                label="Reflects",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = reflection_id
                
                elif item_type == "rerun":
                    # Add rerun node
                    rerun_id = f"rerun_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if NodeType.RERUN in self.settings["node_types_to_show"]:
                        rerun_data = {
                            "reason": item.get("reason"),
                            "timestamp": timestamp,
                            "loop_count": item.get("loop_count"),
                            "mode": item.get("mode", current_mode)
                        }
                        
                        self.add_node(
                            node_id=rerun_id,
                            node_type=NodeType.RERUN,
                            label=f"Rerun: {item.get('reason')}",
                            data=rerun_data
                        )
                        
                        # Connect from last node
                        if EdgeType.RERUN in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=rerun_id,
                                edge_type=EdgeType.RERUN,
                                label="Reruns",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = rerun_id
                
                elif item_type == "operator":
                    # Add operator node
                    operator_id = f"operator_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if NodeType.OPERATOR in self.settings["node_types_to_show"]:
                        operator_data = {
                            "operation": item.get("operation"),
                            "timestamp": timestamp,
                            "mode": item.get("mode", current_mode)
                        }
                        
                        self.add_node(
                            node_id=operator_id,
                            node_type=NodeType.OPERATOR,
                            label=f"Operator: {item.get('operation')}",
                            data=operator_data
                        )
                        
                        # Connect from last node
                        if EdgeType.OPERATOR in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=operator_id,
                                edge_type=EdgeType.OPERATOR,
                                label="Operates",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = operator_id
                
                elif item_type == "mode_change":
                    # Add mode change node
                    mode_change_id = f"mode_change_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if NodeType.MODE_CHANGE in self.settings["node_types_to_show"]:
                        mode_change_data = {
                            "old_mode": item.get("old_mode"),
                            "new_mode": item.get("new_mode"),
                            "reason": item.get("reason"),
                            "timestamp": timestamp
                        }
                        
                        self.add_node(
                            node_id=mode_change_id,
                            node_type=NodeType.MODE_CHANGE,
                            label=f"Mode Change: {item.get('old_mode')} -> {item.get('new_mode')}",
                            data=mode_change_data
                        )
                        
                        # Connect from last node
                        if EdgeType.MODE_TRANSITION in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=mode_change_id,
                                edge_type=EdgeType.MODE_TRANSITION,
                                label=f"Changes Mode: {item.get('reason')}",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = mode_change_id
                        
                        # Update current mode
                        current_mode = item.get("new_mode")
                
                elif item_type == "depth_change":
                    # Add depth change node
                    depth_change_id = f"depth_change_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if NodeType.DEPTH_CHANGE in self.settings["node_types_to_show"]:
                        depth_change_data = {
                            "old_depth": item.get("old_depth"),
                            "new_depth": item.get("new_depth"),
                            "reason": item.get("reason"),
                            "timestamp": timestamp,
                            "mode": current_mode
                        }
                        
                        self.add_node(
                            node_id=depth_change_id,
                            node_type=NodeType.DEPTH_CHANGE,
                            label=f"Depth Change: {item.get('old_depth')} -> {item.get('new_depth')}",
                            data=depth_change_data
                        )
                        
                        # Connect from last node
                        if EdgeType.DEPTH_TRANSITION in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=depth_change_id,
                                edge_type=EdgeType.DEPTH_TRANSITION,
                                label=f"Changes Depth: {item.get('reason')}",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = depth_change_id
            
            # Add loop end node
            end_node_id = f"loop_end_{self.loop_id}"
            self.add_node(
                node_id=end_node_id,
                node_type=NodeType.LOOP_END,
                label=f"Loop {self.loop_id} End",
                data={
                    "loop_id": self.loop_id,
                    "timestamp": loop_trace.get("end_time", datetime.utcnow().isoformat()),
                    "status": loop_trace.get("status", "completed"),
                    "loop_count": loop_count,
                    "mode": current_mode
                }
            )
            
            # Connect from last node to end node
            self.add_edge(
                source=last_node_id,
                target=end_node_id,
                edge_type=EdgeType.EXECUTION,
                label="Completes",
                data={"timestamp": loop_trace.get("end_time", datetime.utcnow().isoformat())}
            )
            
            # Build the final map
            loop_map = {
                "loop_id": self.loop_id,
                "mode": current_mode,
                "nodes": self.nodes,
                "edges": self.edges,
                "metadata": self.metadata
            }
            
            return loop_map
        except Exception as e:
            logger.error(f"Error generating loop map: {str(e)}")
            return {
                "loop_id": self.loop_id,
                "mode": self.mode,
                "error": str(e),
                "nodes": [],
                "edges": [],
                "metadata": self.metadata
            }
    
    def add_node(self, node_id: str, node_type: NodeType, label: str, data: Dict[str, Any]) -> None:
        """
        Add a node to the visualization.
        
        Args:
            node_id: Unique identifier for the node
            node_type: Type of node
            label: Label for the node
            data: Additional data for the node
        """
        # Get color for node type
        color = COLOR_SCHEMES[self.color_scheme].get(node_type, "#CCCCCC")
        
        # Create node
        node = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "color": color,
            "data": data
        }
        
        self.nodes.append(node)
    
    def add_edge(self, source: str, target: str, edge_type: EdgeType, label: str, data: Dict[str, Any]) -> None:
        """
        Add an edge to the visualization.
        
        Args:
            source: Source node ID
            target: Target node ID
            edge_type: Type of edge
            label: Label for the edge
            data: Additional data for the edge
        """
        # Get color for edge type
        color = COLOR_SCHEMES[self.color_scheme].get(edge_type, "#CCCCCC")
        
        # Create edge
        edge = {
            "source": source,
            "target": target,
            "type": edge_type,
            "label": label,
            "color": color,
            "data": data
        }
        
        self.edges.append(edge)
    
    def generate_html(self, loop_map: Dict[str, Any]) -> str:
        """
        Generate HTML visualization from loop map.
        
        Args:
            loop_map: The loop map data
            
        Returns:
            HTML string for visualization
        """
        # Convert loop map to JSON for embedding in HTML
        loop_map_json = json.dumps(loop_map)
        
        # Generate HTML with D3.js visualization
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loop Map Visualization - {loop_map['loop_id']}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        #visualization {{
            width: 100%;
            height: 800px;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }}
        
        .node {{
            cursor: pointer;
        }}
        
        .link {{
            stroke-opacity: 0.6;
        }}
        
        .node text {{
            font-size: 12px;
            fill: #333;
        }}
        
        .tooltip {{
            position: absolute;
            background-color: rgba(255, 255, 255, 0.9);
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            font-size: 12px;
            pointer-events: none;
            max-width: 300px;
            z-index: 1000;
        }}
        
        .controls {{
            margin-bottom: 20px;
        }}
        
        .controls button {{
            margin-right: 10px;
            padding: 5px 10px;
            background-color: #4285F4;
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }}
        
        .controls button:hover {{
            background-color: #3367D6;
        }}
        
        .metadata {{
            margin-top: 20px;
            padding: 10px;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <h1>Loop Map Visualization</h1>
    <div class="controls">
        <button id="zoom-in">Zoom In</button>
        <button id="zoom-out">Zoom Out</button>
        <button id="reset">Reset</button>
        <button id="toggle-labels">Toggle Labels</button>
        <button id="toggle-details">Toggle Details</button>
    </div>
    <div id="visualization"></div>
    <div class="metadata">
        <h2>Metadata</h2>
        <p><strong>Loop ID:</strong> {loop_map['loop_id']}</p>
        <p><strong>Mode:</strong> {loop_map['mode']}</p>
        <p><strong>Generated At:</strong> {loop_map['metadata']['generated_at']}</p>
        <p><strong>Node Count:</strong> {len(loop_map['nodes'])}</p>
        <p><strong>Edge Count:</strong> {len(loop_map['edges'])}</p>
    </div>
    
    <script>
        // Loop map data
        const loopMap = {loop_map_json};
        
        // Set up the visualization
        const width = document.getElementById('visualization').clientWidth;
        const height = document.getElementById('visualization').clientHeight;
        
        // Create SVG
        const svg = d3.select('#visualization')
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Create container for zoom
        const container = svg.append('g');
        
        // Set up zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {{
                container.attr('transform', event.transform);
            }});
        
        svg.call(zoom);
        
        // Create tooltip
        const tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);
        
        // Create force simulation
        const simulation = d3.forceSimulation(loopMap.nodes)
            .force('link', d3.forceLink(loopMap.edges).id(d => d.id).distance(150))
            .force('charge', d3.forceManyBody().strength(-500))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('x', d3.forceX(width / 2).strength(0.1))
            .force('y', d3.forceY(height / 2).strength(0.1));
        
        // Create links
        const link = container.append('g')
            .selectAll('line')
            .data(loopMap.edges)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke', d => d.color)
            .attr('stroke-width', 2);
        
        // Create link labels
        const linkLabel = container.append('g')
            .selectAll('text')
            .data(loopMap.edges)
            .enter()
            .append('text')
            .attr('class', 'link-label')
            .attr('text-anchor', 'middle')
            .attr('dy', -5)
            .text(d => d.label)
            .style('font-size', '10px')
            .style('fill', '#666')
            .style('pointer-events', 'none');
        
        // Create nodes
        const node = container.append('g')
            .selectAll('circle')
            .data(loopMap.nodes)
            .enter()
            .append('circle')
            .attr('class', 'node')
            .attr('r', d => d.type === 'loop_start' || d.type === 'loop_end' ? 15 : 10)
            .attr('fill', d => d.color)
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .on('mouseover', (event, d) => {{
                tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                
                // Build tooltip content
                let content = `<strong>${d.label}</strong><br/>`;
                content += `Type: ${d.type}<br/>`;
                
                // Add data properties
                for (const [key, value] of Object.entries(d.data)) {{
                    if (typeof value === 'object') {{
                        content += `${key}: ${JSON.stringify(value)}<br/>`;
                    }} else {{
                        content += `${key}: ${value}<br/>`;
                    }}
                }}
                
                tooltip.html(content)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            }})
            .on('mouseout', () => {{
                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            }})
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        // Create node labels
        const nodeLabel = container.append('g')
            .selectAll('text')
            .data(loopMap.nodes)
            .enter()
            .append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', 25)
            .text(d => d.label)
            .style('font-size', '10px')
            .style('pointer-events', 'none');
        
        // Update positions on tick
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            linkLabel
                .attr('x', d => (d.source.x + d.target.x) / 2)
                .attr('y', d => (d.source.y + d.target.y) / 2);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            nodeLabel
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});
        
        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Control buttons
        d3.select('#zoom-in').on('click', () => {{
            svg.transition().call(zoom.scaleBy, 1.5);
        }});
        
        d3.select('#zoom-out').on('click', () => {{
            svg.transition().call(zoom.scaleBy, 0.75);
        }});
        
        d3.select('#reset').on('click', () => {{
            svg.transition().call(zoom.transform, d3.zoomIdentity);
        }});
        
        let labelsVisible = true;
        d3.select('#toggle-labels').on('click', () => {{
            labelsVisible = !labelsVisible;
            nodeLabel.style('display', labelsVisible ? 'block' : 'none');
            linkLabel.style('display', labelsVisible ? 'block' : 'none');
        }});
        
        let detailsVisible = true;
        d3.select('#toggle-details').on('click', () => {{
            detailsVisible = !detailsVisible;
            d3.select('.metadata').style('display', detailsVisible ? 'block' : 'none');
        }});
    </script>
</body>
</html>
"""
        
        return html
    
    def generate_svg(self, loop_map: Dict[str, Any]) -> str:
        """
        Generate SVG visualization from loop map.
        
        Args:
            loop_map: The loop map data
            
        Returns:
            SVG string for visualization
        """
        # This would be a more complex implementation in a real system
        # For this implementation, we'll return a simple SVG
        
        # Calculate dimensions based on node count
        width = max(800, len(loop_map["nodes"]) * 100)
        height = max(600, len(loop_map["nodes"]) * 75)
        
        # Start SVG
        svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#f5f5f5"/>
    <text x="10" y="30" font-family="Arial" font-size="20" fill="#333">Loop Map: {loop_map['loop_id']}</text>
    <text x="10" y="50" font-family="Arial" font-size="14" fill="#666">Mode: {loop_map['mode']}</text>
"""
        
        # Add nodes
        for i, node in enumerate(loop_map["nodes"]):
            x = 100 + (i % 5) * 150
            y = 100 + (i // 5) * 100
            
            svg += f"""    <circle cx="{x}" cy="{y}" r="10" fill="{node['color']}"/>
    <text x="{x}" y="{y + 25}" font-family="Arial" font-size="12" text-anchor="middle" fill="#333">{node['label']}</text>
"""
        
        # Add edges (simplified)
        for edge in loop_map["edges"]:
            # Find source and target nodes
            source_index = next((i for i, node in enumerate(loop_map["nodes"]) if node["id"] == edge["source"]), 0)
            target_index = next((i for i, node in enumerate(loop_map["nodes"]) if node["id"] == edge["target"]), 0)
            
            source_x = 100 + (source_index % 5) * 150
            source_y = 100 + (source_index // 5) * 100
            target_x = 100 + (target_index % 5) * 150
            target_y = 100 + (target_index // 5) * 100
            
            svg += f"""    <line x1="{source_x}" y1="{source_y}" x2="{target_x}" y2="{target_y}" stroke="{edge['color']}" stroke-width="2"/>
"""
        
        # End SVG
        svg += "</svg>"
        
        return svg
    
    def change_mode(self, new_mode: str) -> None:
        """
        Change the visualizer mode.
        
        Args:
            new_mode: The new mode to use
        """
        logger.info(f"Changing mode from {self.mode} to {new_mode} for loop {self.loop_id}")
        
        self.mode = new_mode.lower() if new_mode else "balanced"
        
        # Update settings based on new mode
        if self.mode in MODE_VISUALIZATION_SETTINGS:
            self.settings = MODE_VISUALIZATION_SETTINGS[self.mode]
        else:
            self.settings = MODE_VISUALIZATION_SETTINGS["balanced"]
        
        # Update metadata
        self.metadata["mode"] = self.mode
    
    def should_update_visualization(self, event_type: str) -> bool:
        """
        Determine if visualization should be updated for a given event type.
        
        Args:
            event_type: The event type (agent_completion, reflection, decision, loop_end)
            
        Returns:
            True if visualization should be updated, False otherwise
        """
        # Get update frequency for the mode
        update_frequency = self.settings["update_frequency"]
        
        # Determine if visualization should be updated based on frequency and event type
        if update_frequency == "end_only":
            return event_type == "loop_end"
        elif update_frequency == "agent_completion":
            return event_type in ["agent_completion", "loop_end"]
        elif update_frequency == "real_time":
            return True  # Update for all events
        else:
            return False

def create_visualizer(loop_id: str, mode: str = "balanced", color_scheme: str = "default") -> LoopMapVisualizer:
    """
    Create a loop map visualizer for a loop.
    
    Args:
        loop_id: The ID of the loop to visualize
        mode: The orchestrator mode (fast, balanced, thorough, research)
        color_scheme: The color scheme to use for visualization (default, dark, accessibility)
        
    Returns:
        LoopMapVisualizer instance
    """
    return LoopMapVisualizer(loop_id, mode, color_scheme)

def visualize_loop(loop_id: str, loop_trace: Dict[str, Any], mode: str = "balanced", format: VisualizationFormat = VisualizationFormat.HTML, color_scheme: str = "default") -> Dict[str, Any]:
    """
    Visualize a loop trace.
    
    Args:
        loop_id: The ID of the loop to visualize
        loop_trace: The loop trace data
        mode: The orchestrator mode (fast, balanced, thorough, research)
        format: The output format (json, html, svg, png, dot)
        color_scheme: The color scheme to use for visualization (default, dark, accessibility)
        
    Returns:
        Dictionary containing the visualization data
    """
    logger.info(f"Visualizing loop {loop_id} in {mode} mode with {format} format")
    
    try:
        # Create visualizer
        visualizer = create_visualizer(loop_id, mode, color_scheme)
        
        # Generate loop map
        loop_map = visualizer.generate_map_from_trace(loop_trace)
        
        # Generate visualization in requested format
        if format == VisualizationFormat.JSON:
            visualization = json.dumps(loop_map, indent=2)
            content_type = "application/json"
        elif format == VisualizationFormat.HTML:
            visualization = visualizer.generate_html(loop_map)
            content_type = "text/html"
        elif format == VisualizationFormat.SVG:
            visualization = visualizer.generate_svg(loop_map)
            content_type = "image/svg+xml"
        elif format == VisualizationFormat.PNG:
            # This would be a more complex implementation in a real system
            # For this implementation, we'll return a placeholder
            visualization = "PNG visualization not implemented"
            content_type = "text/plain"
        elif format == VisualizationFormat.DOT:
            # This would be a more complex implementation in a real system
            # For this implementation, we'll return a placeholder
            visualization = "DOT visualization not implemented"
            content_type = "text/plain"
        else:
            visualization = json.dumps(loop_map, indent=2)
            content_type = "application/json"
        
        return {
            "loop_id": loop_id,
            "mode": mode,
            "format": format,
            "content_type": content_type,
            "visualization": visualization,
            "metadata": {
                "node_count": len(loop_map["nodes"]),
                "edge_count": len(loop_map["edges"]),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error visualizing loop: {str(e)}")
        return {
            "loop_id": loop_id,
            "mode": mode,
            "format": format,
            "error": str(e)
        }
