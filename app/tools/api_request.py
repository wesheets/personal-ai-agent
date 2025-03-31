"""
API Request Tool for the Personal AI Agent System.

This module provides functionality to make HTTP requests to external APIs
and process the responses.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("api_request")

def run(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
    verify_ssl: bool = True,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["api_request", "external_data"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Make an HTTP request to an external API and process the response.
    
    Args:
        url: The API endpoint URL
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        headers: Optional HTTP headers
        params: Optional URL parameters
        data: Optional request body (form data or string)
        json_data: Optional JSON request body
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        store_memory: Whether to store the API response in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing the API response and metadata
    """
    logger.info(f"Making {method} request to API: {url}")
    
    try:
        # In a real implementation, this would make actual API requests
        # For now, we'll simulate the API response
        
        # Validate method
        method = method.upper()
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            raise ValueError(f"Invalid HTTP method: {method}")
            
        # Simulate API request and response
        response_data, status_code, response_headers = _simulate_api_response(
            url, method, headers, params, data, json_data
        )
        
        result = {
            "success": True,
            "url": url,
            "method": method,
            "status_code": status_code,
            "headers": response_headers,
            "data": response_data,
            "request_metadata": {
                "headers_sent": headers,
                "params_sent": params,
                "data_sent": data,
                "json_sent": json_data,
                "timeout": timeout,
                "verify_ssl": verify_ssl
            }
        }
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a summary of the response for memory storage
                response_summary = str(response_data)
                if len(response_summary) > 500:
                    response_summary = response_summary[:500] + "..."
                
                memory_entry = {
                    "type": "api_request",
                    "url": url,
                    "method": method,
                    "status_code": status_code,
                    "timestamp": datetime.now().isoformat(),
                    "response_summary": response_summary
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags
                )
                
                logger.info(f"Stored API response in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store API response in memory: {str(e)}")
        
        return result
    except Exception as e:
        error_msg = f"Error making API request: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "url": url,
            "method": method
        }

def _simulate_api_response(
    url: str,
    method: str,
    headers: Optional[Dict[str, str]],
    params: Optional[Dict[str, Any]],
    data: Optional[Union[Dict[str, Any], str]],
    json_data: Optional[Dict[str, Any]]
) -> tuple:
    """
    Simulate an API response for development purposes.
    
    Args:
        url: The API endpoint URL
        method: HTTP method
        headers: HTTP headers
        params: URL parameters
        data: Request body
        json_data: JSON request body
        
    Returns:
        Tuple of (response_data, status_code, response_headers)
    """
    # Extract API endpoint for simulation purposes
    endpoint = url.split("/")[-1] if "/" in url else url
    
    # Default response headers
    response_headers = {
        "Content-Type": "application/json",
        "Server": "SimulatedAPI/1.0",
        "Date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "Cache-Control": "no-cache",
        "X-Request-ID": f"req-{hash(url) % 10000:04d}"
    }
    
    # Simulate different responses based on endpoint and method
    if "weather" in endpoint.lower():
        response_data = {
            "location": params.get("location", "Unknown") if params else "Unknown",
            "temperature": 22.5,
            "conditions": "Partly Cloudy",
            "humidity": 65,
            "wind_speed": 10,
            "forecast": [
                {"day": "Today", "high": 24, "low": 18, "conditions": "Partly Cloudy"},
                {"day": "Tomorrow", "high": 26, "low": 19, "conditions": "Sunny"},
                {"day": "Day 3", "high": 23, "low": 17, "conditions": "Rain"}
            ]
        }
        status_code = 200
        
    elif "user" in endpoint.lower():
        if method == "GET":
            user_id = params.get("id", "123") if params else "123"
            response_data = {
                "id": user_id,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "created_at": "2024-10-15T14:30:00Z",
                "status": "active"
            }
            status_code = 200
        elif method == "POST":
            # Simulate user creation
            user_data = json_data or data or {}
            response_data = {
                "id": "456",
                "name": user_data.get("name", "New User"),
                "email": user_data.get("email", "new.user@example.com"),
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
            status_code = 201
        else:
            response_data = {"message": "Method not allowed"}
            status_code = 405
            
    elif "product" in endpoint.lower():
        if method == "GET":
            product_id = params.get("id", "789") if params else "789"
            response_data = {
                "id": product_id,
                "name": "Smart Widget Pro",
                "price": 99.99,
                "category": "Electronics",
                "in_stock": True,
                "features": ["Wireless", "Smart Home Integration", "Voice Control"]
            }
            status_code = 200
        else:
            response_data = {"message": "Method not allowed"}
            status_code = 405
            
    elif "search" in endpoint.lower():
        query = params.get("q", "") if params else ""
        response_data = {
            "query": query,
            "results_count": 42,
            "results": [
                {"id": "1", "title": f"Result 1 for {query}", "relevance": 0.95},
                {"id": "2", "title": f"Result 2 for {query}", "relevance": 0.87},
                {"id": "3", "title": f"Result 3 for {query}", "relevance": 0.82}
            ],
            "pagination": {
                "page": params.get("page", 1) if params else 1,
                "total_pages": 5,
                "next_page": 2
            }
        }
        status_code = 200
        
    else:
        # Generic response
        response_data = {
            "message": "API request received",
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }
        status_code = 200
    
    # Add request echo for debugging
    response_data["request_echo"] = {
        "url": url,
        "method": method,
        "headers": headers,
        "params": params,
        "has_data": data is not None,
        "has_json": json_data is not None
    }
    
    return response_data, status_code, response_headers
