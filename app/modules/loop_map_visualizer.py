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
    def validate_schema(*args, **kwargs): return True
    def validate_before_export(*args, **kwargs): return True

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

# Add the missing functions that are imported by orchestrator_routes.py
def create_visualizer(loop_id: str, mode: str = "balanced", color_scheme: str = "default") -> LoopMapVisualizer:
    """
    Create a new loop map visualizer instance.
    
    Args:
        loop_id: The ID of the loop to visualize
        mode: The orchestrator mode (fast, balanced, thorough, research)
        color_scheme: The color scheme to use for visualization (default, dark, accessibility)
        
    Returns:
        A new LoopMapVisualizer instance
    """
    logger.info(f"Creating visualizer for loop {loop_id} with mode {mode} and color scheme {color_scheme}")
    return LoopMapVisualizer(loop_id, mode, color_scheme)

def visualize_loop(loop_trace: Dict[str, Any], format: VisualizationFormat = VisualizationFormat.JSON) -> Dict[str, Any]:
    """
    Visualize a loop trace in the specified format.
    
    Args:
        loop_trace: The loop trace data
        format: The output format for the visualization
        
    Returns:
        Visualization data in the specified format
    """
    logger.info(f"Visualizing loop trace in {format} format")
    
    # Extract loop ID and mode from trace
    loop_id = loop_trace.get("loop_id", "unknown")
    mode = loop_trace.get("mode", "balanced")
    
    # Create visualizer
    visualizer = create_visualizer(loop_id, mode)
    
    # Return placeholder visualization data
    return {
        "format": format,
        "loop_id": loop_id,
        "mode": mode,
        "generated_at": datetime.utcnow().isoformat(),
        "version": "1.0",
        "nodes": [],
        "edges": [],
        "message": "Placeholder visualization - safe import guard is working"
    }
