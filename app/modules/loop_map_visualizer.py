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
from modules.schema_validation import validate_schema, validate_before_export

# Configure logging
logging.basicConfig(
    filename='/debug/schema_trace.log',
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
                            
                            # Connect agent to memory
                            if "memory_access" in self.settings["edge_types_to_show"]:
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
                    if "decision" in self.settings["node_types_to_show"]:
                        decision_data = {
                            "decision_type": item.get("decision_type"),
                            "timestamp": timestamp,
                            "outcome": item.get("outcome")
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
                        if "decision" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=decision_id,
                                edge_type=EdgeType.DECISION,
                                label="Decides",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = decision_id
                
                elif item_type == "reflection":
                    # Add reflection node
                    reflection_id = f"reflection_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "reflection" in self.settings["node_types_to_show"]:
                        self.add_node(
                            node_id=reflection_id,
                            node_type=NodeType.REFLECTION,
                            label=f"Reflection: {item.get('reflection_type')}",
                            data={
                                "reflection_type": item.get("reflection_type"),
                                "timestamp": timestamp,
                                "agent": item.get("agent")
                            }
                        )
                        
                        # Connect from last node
                        if "reflection" in self.settings["edge_types_to_show"]:
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
                    if "rerun" in self.settings["node_types_to_show"]:
                        self.add_node(
                            node_id=rerun_id,
                            node_type=NodeType.RERUN,
                            label=f"Rerun: {item.get('reason')}",
                            data={
                                "reason": item.get("reason"),
                                "timestamp": timestamp,
                                "loop_count": item.get("loop_count", loop_count + 1)
                            }
                        )
                        
                        # Connect from last node
                        if "rerun" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=rerun_id,
                                edge_type=EdgeType.RERUN,
                                label="Reruns",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = rerun_id
                
                elif item_type == "operator_action":
                    # Add operator node
                    operator_id = f"operator_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "operator" in self.settings["node_types_to_show"]:
                        self.add_node(
                            node_id=operator_id,
                            node_type=NodeType.OPERATOR,
                            label=f"Operator: {item.get('operation')}",
                            data={
                                "operation": item.get("operation"),
                                "timestamp": timestamp
                            }
                        )
                        
                        # Connect from last node
                        if "operator" in self.settings["edge_types_to_show"]:
                            self.add_edge(
                                source=last_node_id,
                                target=operator_id,
                                edge_type=EdgeType.OPERATOR,
                                label="Intervenes",
                                data={"timestamp": timestamp}
                            )
                        
                        # Update last node
                        last_node_id = operator_id
                
                elif item_type == "mode_change":
                    # Add mode change node
                    mode_change_id = f"mode_change_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "mode_change" in self.settings["node_types_to_show"]:
                        old_mode = item.get("old_mode", "unknown")
                        new_mode = item.get("new_mode", "unknown")
                        
                        self.add_node(
                            node_id=mode_change_id,
                            node_type=NodeType.MODE_CHANGE,
                            label=f"Mode Change: {old_mode} → {new_mode}",
                            data={
                                "old_mode": old_mode,
                                "new_mode": new_mode,
                                "reason": item.get("reason"),
                                "timestamp": timestamp
                            }
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
                        
                        # Update mode and settings
                        if new_mode != self.mode:
                            self.mode = new_mode
                            self.settings = load_visual_settings(self.mode)
                            self.metadata["mode"] = self.mode
                
                elif item_type == "depth_change":
                    # Add depth change node
                    depth_change_id = f"depth_change_{timestamp}"
                    
                    # Only add if this node type should be shown in current mode
                    if "depth_change" in self.settings["node_types_to_show"]:
                        old_depth = item.get("old_depth", 0)
                        new_depth = item.get("new_depth", 0)
                        
                        self.add_node(
                            node_id=depth_change_id,
                            node_type=NodeType.DEPTH_CHANGE,
                            label=f"Depth Change: {old_depth} → {new_depth}",
                            data={
                                "old_depth": old_depth,
                                "new_depth": new_depth,
                                "reason": item.get("reason"),
                                "timestamp": timestamp
                            }
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
            
            # Add loop end node
            end_node_id = f"loop_end_{self.loop_id}"
            self.add_node(
                node_id=end_node_id,
                node_type=NodeType.LOOP_END,
                label=f"Loop {self.loop_id} End",
                data={
                    "loop_id": self.loop_id,
                    "timestamp": loop_trace.get("end_time", datetime.utcnow().isoformat()),
                    "loop_count": loop_count,
                    "mode": self.mode
                }
            )
            
            # Connect from last node to end node
            if "execution" in self.settings["edge_types_to_show"]:
                self.add_edge(
                    source=last_node_id,
                    target=end_node_id,
                    edge_type=EdgeType.EXECUTION,
                    label="Completes",
                    data={"timestamp": datetime.utcnow().isoformat()}
                )
            
            # Create the loop map
            loop_map = {
                "metadata": self.metadata,
                "nodes": self.nodes,
                "edges": self.edges,
                "settings": self.settings
            }
            
            # Validate loop map against schema
            is_valid, error = validate_schema(loop_map, 'loop_map_visualization')
            if not is_valid:
                logger.error(f"Invalid loop map for loop {self.loop_id}: {error}")
                loop_map["validation_error"] = error
            else:
                logger.info(f"Loop map for loop {self.loop_id} validated successfully")
                loop_map["schema_validated"] = True
                loop_map["validation_timestamp"] = datetime.utcnow().isoformat()
            
            return loop_map
        
        except Exception as e:
            logger.error(f"Error generating loop map: {str(e)}")
            return {
                "error": f"Failed to generate loop map: {str(e)}",
                "loop_id": self.loop_id
            }
    
    def export_map(self, loop_trace: Dict[str, Any], format_type: str = "json", output_dir: str = "/tmp") -> Dict[str, Any]:
        """
        Export a loop map to a file.
        
        Args:
            loop_trace: The loop trace data
            format_type: The format to export as ("json", "html", "svg", "png", "dot")
            output_dir: Directory to save the file
            
        Returns:
            Dict with export result
        """
        # Generate the loop map
        loop_map = self.generate_map_from_trace(loop_trace)
        
        # Check for errors
        if "error" in loop_map:
            return {
                "success": False,
                "error": loop_map["error"],
                "loop_id": self.loop_id
            }
        
        # Check for validation errors
        if "validation_error" in loop_map:
            return {
                "success": False,
                "error": f"Schema validation failed: {loop_map['validation_error']}",
                "loop_id": self.loop_id
            }
        
        # Create a timestamp for the filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create the filename
        filename = f"loop_map_{self.loop_id}_{timestamp}.{format_type.lower()}"
        
        # Create the full file path
        file_path = os.path.join(output_dir, filename)
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            if format_type.lower() == "json":
                # Export as JSON
                with open(file_path, "w") as f:
                    json.dump(loop_map, f, indent=2)
            
            elif format_type.lower() == "html":
                # Export as HTML
                html_content = self._generate_html(loop_map)
                
                # Validate HTML export format
                html_export = {
                    "format": "html",
                    "loop_id": self.loop_id,
                    "content": html_content,
                    "metadata": {
                        "export_timestamp": datetime.utcnow().isoformat(),
                        "format_version": "1.0",
                        "export_type": "loop_map"
                    }
                }
                
                # Validate against HTML export schema
                is_valid = validate_before_export(html_export, 'html')
                if not is_valid:
                    return {
                        "success": False,
                        "error": "HTML export format validation failed",
                        "loop_id": self.loop_id
                    }
                
                with open(file_path, "w") as f:
                    f.write(html_content)
            
            elif format_type.lower() == "svg":
                # Export as SVG
                svg_content = self._generate_svg(loop_map)
                with open(file_path, "w") as f:
                    f.write(svg_content)
            
            elif format_type.lower() == "png":
                # Export as PNG
                # This would typically use a library like Pillow or cairosvg to convert SVG to PNG
                # For this example, we'll just create a placeholder
                with open(file_path, "w") as f:
                    f.write("PNG export not implemented in this example")
            
            elif format_type.lower() == "dot":
                # Export as GraphViz DOT format
                dot_content = self._generate_dot(loop_map)
                with open(file_path, "w") as f:
                    f.write(dot_content)
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format_type}",
                    "loop_id": self.loop_id
                }
            
            return {
                "success": True,
                "loop_id": self.loop_id,
                "format": format_type,
                "file_path": file_path,
                "schema_validated": True,
                "validation_timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error exporting loop map: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to export loop map: {str(e)}",
                "loop_id": self.loop_id
            }
    
    def _generate_html(self, loop_map: Dict[str, Any]) -> str:
        """
        Generate HTML representation of the loop map.
        
        Args:
            loop_map: The loop map data
            
        Returns:
            HTML string
        """
        # This is a simplified example - a real implementation would use a proper visualization library
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loop Map: {self.loop_id}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .metadata {{
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .visualization {{
            margin-top: 30px;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
            overflow: auto;
        }}
        .node {{
            display: inline-block;
            margin: 10px;
            padding: 10px;
            border-radius: 5px;
            background-color: #f0f0f0;
            border: 1px solid #ddd;
        }}
        .edge {{
            margin: 5px 0;
            padding: 5px;
            border-bottom: 1px solid #eee;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-align: right;
        }}
    </style>
</head>
<body>
    <h1>Loop Map: {self.loop_id}</h1>
    
    <div class="metadata">
        <h2>Metadata</h2>
        <p><strong>Loop ID:</strong> {loop_map["metadata"]["loop_id"]}</p>
        <p><strong>Mode:</strong> {loop_map["metadata"]["mode"]}</p>
        <p><strong>Generated At:</strong> {loop_map["metadata"]["generated_at"]}</p>
        <p><strong>Version:</strong> {loop_map["metadata"]["version"]}</p>
    </div>
    
    <div class="visualization">
        <h2>Nodes</h2>
        <div class="nodes">
"""
        
        # Add nodes
        for node in loop_map["nodes"]:
            node_type = node["type"]
            color = COLOR_SCHEMES[self.color_scheme].get(node_type, "#cccccc")
            
            html += f"""
            <div class="node" style="background-color: {color}">
                <h3>{node["label"]}</h3>
                <p><strong>ID:</strong> {node["id"]}</p>
                <p><strong>Type:</strong> {node["type"]}</p>
"""
            
            # Add node data
            for key, value in node["data"].items():
                html += f"                <p><strong>{key}:</strong> {value}</p>\n"
            
            html += "            </div>\n"
        
        html += """
        </div>
        
        <h2>Edges</h2>
        <div class="edges">
"""
        
        # Add edges
        for edge in loop_map["edges"]:
            edge_type = edge["type"]
            color = COLOR_SCHEMES[self.color_scheme].get(edge_type, "#cccccc")
            
            html += f"""
            <div class="edge" style="border-left: 5px solid {color}; padding-left: 10px;">
                <p><strong>From:</strong> {edge["source"]} <strong>To:</strong> {edge["target"]}</p>
                <p><strong>Type:</strong> {edge["type"]}</p>
                <p><strong>Label:</strong> {edge["label"]}</p>
"""
            
            # Add edge data
            for key, value in edge["data"].items():
                html += f"                <p><strong>{key}:</strong> {value}</p>\n"
            
            html += "            </div>\n"
        
        html += f"""
        </div>
    </div>
    
    <div class="timestamp">
        Generated on {datetime.utcnow().isoformat()}
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_svg(self, loop_map: Dict[str, Any]) -> str:
        """
        Generate SVG representation of the loop map.
        
        Args:
            loop_map: The loop map data
            
        Returns:
            SVG string
        """
        # This is a placeholder - a real implementation would use a proper visualization library
        svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
    <rect width="800" height="600" fill="#ffffff" />
    <text x="400" y="50" font-family="Arial" font-size="24" text-anchor="middle">Loop Map: {self.loop_id}</text>
    <text x="400" y="80" font-family="Arial" font-size="16" text-anchor="middle">Mode: {loop_map["metadata"]["mode"]}</text>
    <text x="400" y="110" font-family="Arial" font-size="16" text-anchor="middle">Generated At: {loop_map["metadata"]["generated_at"]}</text>
    <text x="400" y="300" font-family="Arial" font-size="18" text-anchor="middle">SVG visualization would be generated here</text>
    <text x="400" y="330" font-family="Arial" font-size="18" text-anchor="middle">with {len(loop_map["nodes"])} nodes and {len(loop_map["edges"])} edges</text>
</svg>
"""
        
        return svg
    
    def _generate_dot(self, loop_map: Dict[str, Any]) -> str:
        """
        Generate GraphViz DOT representation of the loop map.
        
        Args:
            loop_map: The loop map data
            
        Returns:
            DOT string
        """
        # This is a simplified example - a real implementation would use a proper GraphViz library
        dot = f"""digraph LoopMap_{self.loop_id} {{
    label="Loop Map: {self.loop_id}\\nMode: {loop_map["metadata"]["mode"]}\\nGenerated At: {loop_map["metadata"]["generated_at"]}";
    labelloc="t";
    fontsize=16;
    fontname="Arial";
    node [fontname="Arial", fontsize=12, shape=box, style=filled];
    edge [fontname="Arial", fontsize=10];
    
"""
        
        # Add nodes
        for node in loop_map["nodes"]:
            node_type = node["type"]
            color = COLOR_SCHEMES[self.color_scheme].get(node_type, "#cccccc")
            color = color.replace("#", "")  # Remove # for DOT format
            
            dot += f'    "{node["id"]}" [label="{node["label"]}", fillcolor="#{color}"];\n'
        
        # Add edges
        for edge in loop_map["edges"]:
            edge_type = edge["type"]
            color = COLOR_SCHEMES[self.color_scheme].get(edge_type, "#cccccc")
            color = color.replace("#", "")  # Remove # for DOT format
            
            dot += f'    "{edge["source"]}" -> "{edge["target"]}" [label="{edge["label"]}", color="#{color}"];\n'
        
        dot += "}\n"
        
        return dot
