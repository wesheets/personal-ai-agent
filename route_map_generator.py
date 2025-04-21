"""
Route Map Generator

This script generates a comprehensive map of all API routes in the application.
It creates three output files:
1. route_map.json - Structured JSON with route metadata
2. route_map.md - Human-readable markdown documentation
3. route_map_persona_view.json - Persona-specific capabilities
"""

import os
import json
import inspect
import importlib
import pkgutil
from typing import Dict, List, Any, Optional, Set
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

# Import the FastAPI app
from app.main import app

def get_all_routes() -> List[Dict[str, Any]]:
    """
    Extract all routes from the FastAPI application.
    
    Returns:
        List of dictionaries containing route information
    """
    routes = []
    
    for route in app.routes:
        route_info = {
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, "methods") else [],
            "endpoint": str(route.endpoint.__name__) if hasattr(route, "endpoint") else None,
            "tags": getattr(route, "tags", []),
            "description": inspect.getdoc(route.endpoint) if hasattr(route, "endpoint") else None,
            "response_model": None,
            "status_code": getattr(route, "status_code", 200),
            "deprecated": getattr(route, "deprecated", False),
            "operation_id": getattr(route, "operation_id", None),
            "include_in_schema": getattr(route, "include_in_schema", True),
        }
        
        # Extract response model if available
        if hasattr(route, "response_model"):
            response_model = route.response_model
            if response_model:
                if hasattr(response_model, "__name__"):
                    route_info["response_model"] = response_model.__name__
                else:
                    route_info["response_model"] = str(response_model)
        
        # Extract parameters if available
        if hasattr(route, "endpoint") and hasattr(route.endpoint, "__annotations__"):
            params = []
            for param_name, param_type in route.endpoint.__annotations__.items():
                if param_name != "return":
                    param_info = {
                        "name": param_name,
                        "type": str(param_type),
                        "required": True,  # Default to required
                    }
                    params.append(param_info)
            route_info["parameters"] = params
        
        routes.append(route_info)
    
    return routes

def categorize_routes(routes: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize routes by their prefix or tags.
    
    Args:
        routes: List of route information dictionaries
        
    Returns:
        Dictionary mapping categories to lists of routes
    """
    categories = {
        "core": [],
        "loop": [],
        "agent": [],
        "persona": [],
        "debug": [],
        "other": []
    }
    
    for route in routes:
        path = route["path"]
        tags = route["tags"]
        
        if any(tag.lower() == "debug" for tag in tags) or "/debug/" in path:
            categories["debug"].append(route)
        elif "/core/" in path or any(tag.lower() == "core" for tag in tags):
            categories["core"].append(route)
        elif "/loop/" in path or any(tag.lower() == "loop" for tag in tags):
            categories["loop"].append(route)
        elif "/agent/" in path or any(tag.lower() == "agent" for tag in tags):
            categories["agent"].append(route)
        elif "/persona/" in path or any(tag.lower() == "persona" for tag in tags):
            categories["persona"].append(route)
        else:
            categories["other"].append(route)
    
    return categories

def generate_route_map_json(routes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a structured route map in JSON format.
    
    Args:
        routes: List of route information dictionaries
        
    Returns:
        Dictionary containing the structured route map
    """
    categorized_routes = categorize_routes(routes)
    
    route_map = {
        "metadata": {
            "total_routes": len(routes),
            "generated_at": import_time,
            "version": "1.0.0"
        },
        "categories": {}
    }
    
    for category, category_routes in categorized_routes.items():
        route_map["categories"][category] = {
            "count": len(category_routes),
            "routes": category_routes
        }
    
    return route_map

def generate_route_map_md(route_map: Dict[str, Any]) -> str:
    """
    Generate a human-readable markdown documentation of the route map.
    
    Args:
        route_map: Dictionary containing the structured route map
        
    Returns:
        Markdown string
    """
    md = "# Promethios API Route Map\n\n"
    
    # Add metadata
    metadata = route_map["metadata"]
    md += f"**Total Routes:** {metadata['total_routes']}  \n"
    md += f"**Generated At:** {metadata['generated_at']}  \n"
    md += f"**Version:** {metadata['version']}  \n\n"
    
    # Add table of contents
    md += "## Table of Contents\n\n"
    for category in route_map["categories"]:
        category_count = route_map["categories"][category]["count"]
        if category_count > 0:
            md += f"- [{category.capitalize()} Routes ({category_count})](#{category}-routes)\n"
    md += "\n"
    
    # Add routes by category
    for category, category_data in route_map["categories"].items():
        if category_data["count"] > 0:
            md += f"## {category.capitalize()} Routes\n\n"
            
            for route in category_data["routes"]:
                path = route["path"]
                methods = ", ".join(route["methods"])
                description = route["description"] or "No description available"
                
                md += f"### `{methods} {path}`\n\n"
                md += f"{description}\n\n"
                
                # Add parameters if available
                if "parameters" in route and route["parameters"]:
                    md += "**Parameters:**\n\n"
                    md += "| Name | Type | Required |\n"
                    md += "|------|------|----------|\n"
                    
                    for param in route["parameters"]:
                        required = "Yes" if param["required"] else "No"
                        md += f"| {param['name']} | {param['type']} | {required} |\n"
                    
                    md += "\n"
                
                # Add response model if available
                if route["response_model"]:
                    md += f"**Response Model:** {route['response_model']}\n\n"
                
                # Add status code
                md += f"**Status Code:** {route['status_code']}\n\n"
                
                # Add tags if available
                if route["tags"]:
                    tags = ", ".join(route["tags"])
                    md += f"**Tags:** {tags}\n\n"
                
                # Add separator
                md += "---\n\n"
    
    return md

def generate_persona_view_json(route_map: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a persona-specific view of the route map.
    
    Args:
        route_map: Dictionary containing the structured route map
        
    Returns:
        Dictionary containing the persona-specific route map
    """
    personas = {
        "SAGE": {
            "description": "Default mode focused on balanced execution",
            "capabilities": [],
            "routes": []
        },
        "ARCHITECT": {
            "description": "Focused on system design and structure",
            "capabilities": [],
            "routes": []
        },
        "RESEARCHER": {
            "description": "Focused on information gathering and analysis",
            "capabilities": [],
            "routes": []
        },
        "RITUALIST": {
            "description": "Focused on precise, methodical execution",
            "capabilities": [],
            "routes": []
        },
        "INVENTOR": {
            "description": "Focused on creative problem-solving",
            "capabilities": [],
            "routes": []
        }
    }
    
    # Map routes to personas based on categories and tags
    for category, category_data in route_map["categories"].items():
        for route in category_data["routes"]:
            # Core routes are available to all personas
            if category == "core":
                for persona in personas:
                    personas[persona]["routes"].append(route)
            
            # Loop routes are available to SAGE and RITUALIST
            elif category == "loop":
                personas["SAGE"]["routes"].append(route)
                personas["RITUALIST"]["routes"].append(route)
            
            # Agent routes are available to SAGE, RESEARCHER, and INVENTOR
            elif category == "agent":
                personas["SAGE"]["routes"].append(route)
                personas["RESEARCHER"]["routes"].append(route)
                personas["INVENTOR"]["routes"].append(route)
            
            # Persona routes are available to all personas
            elif category == "persona":
                for persona in personas:
                    personas[persona]["routes"].append(route)
            
            # Debug routes are available to ARCHITECT
            elif category == "debug":
                personas["ARCHITECT"]["routes"].append(route)
    
    # Generate capabilities based on available routes
    for persona, persona_data in personas.items():
        capabilities = set()
        
        for route in persona_data["routes"]:
            path = route["path"]
            
            if "/health" in path:
                capabilities.add("System health monitoring")
            elif "/memory" in path:
                capabilities.add("Memory management")
            elif "/loop" in path:
                capabilities.add("Loop execution control")
            elif "/agent" in path:
                capabilities.add("Agent interaction")
            elif "/persona" in path:
                capabilities.add("Persona management")
            elif "/debug" in path:
                capabilities.add("System debugging")
        
        persona_data["capabilities"] = list(capabilities)
        persona_data["route_count"] = len(persona_data["routes"])
    
    # Create the final persona view
    persona_view = {
        "metadata": route_map["metadata"],
        "personas": personas
    }
    
    return persona_view

# Get current time for metadata
import datetime
import_time = datetime.datetime.now().isoformat()

# Generate route maps
routes = get_all_routes()
route_map = generate_route_map_json(routes)
route_map_md = generate_route_map_md(route_map)
persona_view = generate_persona_view_json(route_map)

# Write to files
with open("route_map.json", "w") as f:
    json.dump(route_map, f, indent=2)

with open("route_map.md", "w") as f:
    f.write(route_map_md)

with open("route_map_persona_view.json", "w") as f:
    json.dump(persona_view, f, indent=2)

print(f"Generated route maps with {len(routes)} total routes")
print("Files created:")
print("- route_map.json")
print("- route_map.md")
print("- route_map_persona_view.json")
