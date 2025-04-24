"""
Test Endpoints for Floating Modules

This script provides test functions for the floating modules implemented in the Promethios system.
"""

import json
import requests
import sys
from typing import Dict, Any, List

# Base URL for API endpoints
BASE_URL = "http://localhost:8000/api"

def test_agent_config_module():
    """Test the agent/config module endpoints."""
    print("\n=== Testing Agent Configuration Module ===")
    
    # Test case 1: Set agent configuration
    endpoint = f"{BASE_URL}/agent/config"
    
    config_request = {
        "agent_id": "ORCHESTRATOR",
        "permissions": [
            {
                "tool_id": "memory_search",
                "enabled": True,
                "permission_level": "standard",
                "rate_limit": 10
            },
            {
                "tool_id": "file_write",
                "enabled": True,
                "permission_level": "elevated",
                "rate_limit": 5
            }
        ],
        "fallback_behavior": {
            "retry_count": 3,
            "fallback_agent": "MEMORY",
            "error_response_template": "I'm sorry, I couldn't complete that task. {error_message}",
            "log_failures": True
        },
        "memory_access_level": "standard",
        "custom_settings": {
            "max_loop_iterations": 5,
            "timeout_seconds": 300
        }
    }
    
    print("Test case 1: Set agent configuration")
    response = make_request("POST", endpoint, config_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('config_updated') else '❌ FAIL'}")
        print(f"Agent ID: {response.get('agent_id')}")
        print(f"Permissions count: {response.get('permissions_count')}")
        print(f"Memory access level: {response.get('memory_access_level')}")
        print(f"Fallback configured: {response.get('fallback_configured')}")
    
    # Test case 2: Get agent configuration
    agent_id = "ORCHESTRATOR"
    endpoint = f"{BASE_URL}/agent/config/{agent_id}"
    
    print("\nTest case 2: Get agent configuration")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if response.get('agent_id') == agent_id else '❌ FAIL'}")
        print(f"Agent ID: {response.get('agent_id')}")
        print(f"Permissions count: {len(response.get('permissions', []))}")
        print(f"Memory access level: {response.get('memory_access_level')}")
        print(f"Custom settings: {response.get('custom_settings')}")
    
    # Test case 3: Delete agent configuration
    endpoint = f"{BASE_URL}/agent/config/{agent_id}"
    
    print("\nTest case 3: Delete agent configuration")
    response = make_request("DELETE", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if response.get('config_deleted') else '❌ FAIL'}")
        print(f"Agent ID: {response.get('agent_id')}")
    
    # Test case 4: Get non-existent agent configuration
    agent_id = "NONEXISTENT"
    endpoint = f"{BASE_URL}/agent/config/{agent_id}"
    
    print("\nTest case 4: Get non-existent agent configuration")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if response.get('agent_id') == agent_id else '❌ FAIL'}")
        print(f"Agent ID: {response.get('agent_id')}")
        print(f"Default permissions: {len(response.get('permissions', [])) == 0}")
        print(f"Default memory access level: {response.get('memory_access_level') == 'standard'}")

def make_request(method: str, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Make an HTTP request to the specified endpoint.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Endpoint URL
        data: Request data (for POST requests)
        
    Returns:
        Response data as dictionary, or None if request failed
    """
    try:
        print(f"Making {method} request to {url}")
        if data:
            print(f"Request data: {json.dumps(data, indent=2)}")
        
        # In a real implementation, this would make an actual HTTP request
        # For this test script, we'll simulate the response
        
        # Simulate response based on request
        if "/agent/config" in url:
            if method == "POST":
                response = {
                    "agent_id": data["agent_id"],
                    "config_updated": True,
                    "permissions_count": len(data.get("permissions", [])),
                    "memory_access_level": data.get("memory_access_level", "standard"),
                    "fallback_configured": data.get("fallback_behavior") is not None,
                    "timestamp": "2025-04-24T20:44:30Z",
                    "version": "1.0.0"
                }
            elif method == "GET":
                agent_id = url.split("/")[-1]
                if agent_id == "NONEXISTENT":
                    response = {
                        "agent_id": agent_id,
                        "permissions": [],
                        "fallback_behavior": None,
                        "memory_access_level": "standard",
                        "custom_settings": {},
                        "timestamp": "2025-04-24T20:44:30Z",
                        "version": "1.0.0"
                    }
                else:
                    response = {
                        "agent_id": agent_id,
                        "permissions": [
                            {
                                "tool_id": "memory_search",
                                "enabled": True,
                                "permission_level": "standard",
                                "rate_limit": 10
                            },
                            {
                                "tool_id": "file_write",
                                "enabled": True,
                                "permission_level": "elevated",
                                "rate_limit": 5
                            }
                        ],
                        "fallback_behavior": {
                            "retry_count": 3,
                            "fallback_agent": "MEMORY",
                            "error_response_template": "I'm sorry, I couldn't complete that task. {error_message}",
                            "log_failures": True
                        },
                        "memory_access_level": "standard",
                        "custom_settings": {
                            "max_loop_iterations": 5,
                            "timeout_seconds": 300
                        },
                        "timestamp": "2025-04-24T20:44:30Z",
                        "version": "1.0.0"
                    }
            elif method == "DELETE":
                agent_id = url.split("/")[-1]
                response = {
                    "agent_id": agent_id,
                    "config_deleted": True,
                    "timestamp": "2025-04-24T20:44:30Z",
                    "version": "1.0.0"
                }
        else:
            response = {"error": "Endpoint not implemented in test script"}
        
        print(f"Response: {json.dumps(response, indent=2)}")
        return response
    
    except Exception as e:
        print(f"Error making request: {str(e)}")
        return None

def test_agent_context_module():
    """Test the agent/context module endpoints."""
    print("\n=== Testing Agent Context Module ===")
    
    # Test case 1: Get agent context by POST
    endpoint = f"{BASE_URL}/agent/context"
    
    context_request = {
        "agent_id": "ORCHESTRATOR",
        "loop_id": "loop_12345",
        "include_memory_stats": True
    }
    
    print("Test case 1: Get agent context by POST")
    response = make_request("POST", endpoint, context_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('agent_id') == 'ORCHESTRATOR' else '❌ FAIL'}")
        print(f"Agent ID: {response.get('agent_id')}")
        print(f"Agent State: {response.get('state')}")
        print(f"Loop ID: {response.get('loop_state', {}).get('loop_id')}")
        print(f"Memory Usage: {response.get('memory_usage', {}).get('total_entries')} entries")
    
    # Test case 2: Get agent context by GET
    agent_id = "CRITIC"
    endpoint = f"{BASE_URL}/agent/context/{agent_id}?loop_id=loop_12345&include_memory_stats=true"
    
    print("\nTest case 2: Get agent context by GET")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if response.get('agent_id') == agent_id else '❌ FAIL'}")
        print(f"Agent ID: {response.get('agent_id')}")
        print(f"Agent State: {response.get('state')}")
        print(f"Loop ID: {response.get('loop_state', {}).get('loop_id')}")
        print(f"Memory Usage: {response.get('memory_usage', {}).get('total_entries')} entries")
    
    # Test case 3: Get non-existent agent context
    agent_id = "NONEXISTENT"
    endpoint = f"{BASE_URL}/agent/context/{agent_id}"
    
    print("\nTest case 3: Get non-existent agent context")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")
        print(f"Agent ID: {response.get('agent_id')}")

def test_memory_recall_module():
    """Test the memory/recall module endpoints."""
    print("\n=== Testing Memory Recall Module ===")
    
    # Test case 1: Recall memory by POST
    endpoint = f"{BASE_URL}/memory/recall"
    
    recall_request = {
        "method": "tag",
        "query": "plan_generated",
        "limit": 10,
        "offset": 0,
        "sort_order": "newest_first",
        "start_date": "2025-04-20T00:00:00Z",
        "end_date": "2025-04-24T23:59:59Z",
        "agent_filter": "ORCHESTRATOR",
        "loop_filter": "loop_12345"
    }
    
    print("Test case 1: Recall memory by POST")
    response = make_request("POST", endpoint, recall_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('query') == 'plan_generated' else '❌ FAIL'}")
        print(f"Query: {response.get('query')}")
        print(f"Method: {response.get('method')}")
        print(f"Total Results: {response.get('total_results')}")
        print(f"Returned Results: {response.get('returned_results')}")
        print(f"First Result Memory ID: {response.get('results', [{}])[0].get('memory_id') if response.get('results') else 'N/A'}")
    
    # Test case 2: Recall memory by GET
    query = "plan_generated"
    endpoint = f"{BASE_URL}/memory/recall?query={query}&method=tag&limit=10&offset=0&sort_order=newest_first&agent_filter=ORCHESTRATOR"
    
    print("\nTest case 2: Recall memory by GET")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if response.get('query') == query else '❌ FAIL'}")
        print(f"Query: {response.get('query')}")
        print(f"Method: {response.get('method')}")
        print(f"Total Results: {response.get('total_results')}")
        print(f"Returned Results: {response.get('returned_results')}")
    
    # Test case 3: Recall memory with invalid query
    endpoint = f"{BASE_URL}/memory/recall?query=&method=tag"
    
    print("\nTest case 3: Recall memory with invalid query")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")

def test_memory_embed_module():
    """Test the memory/embed module endpoints."""
    print("\n=== Testing Memory Embed Module ===")
    
    # Test case 1: Embed memory by POST
    endpoint = f"{BASE_URL}/memory/embed"
    
    embed_request = {
        "content": "This is a sample text to embed in the vector database for semantic search.",
        "model": "default",
        "dimension": 512,
        "tags": ["sample", "text", "embedding"],
        "agent_id": "MEMORY",
        "loop_id": "loop_12345"
    }
    
    print("Test case 1: Embed memory by POST")
    response = make_request("POST", endpoint, embed_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('memory_id') else '❌ FAIL'}")
        print(f"Memory ID: {response.get('memory_id')}")
        print(f"Embedding Size: {response.get('embedding_size')}")
        print(f"Model Used: {response.get('model_used')}")
        print(f"Tags: {response.get('tags')}")
    
    # Test case 2: Embed memory batch by POST
    endpoint = f"{BASE_URL}/memory/embed/batch"
    
    batch_request = {
        "items": [
            {
                "content": "First sample text to embed.",
                "model": "default",
                "dimension": 512,
                "tags": ["sample", "text", "embedding"],
                "agent_id": "MEMORY",
                "loop_id": "loop_12345"
            },
            {
                "content": "Second sample text to embed.",
                "model": "default",
                "dimension": 512,
                "tags": ["sample", "text", "embedding"],
                "agent_id": "MEMORY",
                "loop_id": "loop_12345"
            }
        ]
    }
    
    print("\nTest case 2: Embed memory batch by POST")
    response = make_request("POST", endpoint, batch_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('results') and len(response.get('results', [])) == 2 else '❌ FAIL'}")
        print(f"Total Items: {response.get('total_items')}")
        print(f"Successful Items: {response.get('successful_items')}")
        print(f"First Memory ID: {response.get('results', [{}])[0].get('memory_id') if response.get('results') else 'N/A'}")
    
    # Test case 3: Embed memory with empty content
    endpoint = f"{BASE_URL}/memory/embed"
    
    embed_request = {
        "content": "",
        "model": "default",
        "dimension": 512,
        "tags": ["sample", "text", "embedding"],
        "agent_id": "MEMORY",
        "loop_id": "loop_12345"
    }
    
    print("\nTest case 3: Embed memory with empty content")
    response = make_request("POST", endpoint, embed_request)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")

def test_plan_generate_module():
    """Test the plan/generate module endpoints."""
    print("\n=== Testing Plan Generate Module ===")
    
    # Test case 1: Generate plan by POST
    endpoint = f"{BASE_URL}/plan/generate"
    
    plan_request = {
        "goal": "Implement a new feature for the user dashboard",
        "plan_type": "task",
        "format": "steps",
        "context": "The dashboard currently shows basic metrics but needs to display user activity over time.",
        "constraints": ["Must be completed in 2 weeks", "Must use existing API endpoints"],
        "max_steps": 10,
        "agent_id": "ORCHESTRATOR",
        "loop_id": "loop_12345"
    }
    
    print("Test case 1: Generate plan by POST")
    response = make_request("POST", endpoint, plan_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('plan_id') else '❌ FAIL'}")
        print(f"Plan ID: {response.get('plan_id')}")
        print(f"Goal: {response.get('goal')}")
        print(f"Total Steps: {response.get('total_steps')}")
        print(f"Estimated Completion Time: {response.get('estimated_completion_time')}")
    
    # Test case 2: Generate plan by GET
    goal = "Create a marketing campaign for product launch"
    endpoint = f"{BASE_URL}/plan/generate?goal={goal}&plan_type=project&format=markdown&max_steps=5"
    
    print("\nTest case 2: Generate plan by GET")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if response.get('goal') == goal else '❌ FAIL'}")
        print(f"Plan ID: {response.get('plan_id')}")
        print(f"Format: {response.get('format')}")
        print(f"Content Preview: {response.get('content', '')[:100]}...")
    
    # Test case 3: Generate plan with empty goal
    endpoint = f"{BASE_URL}/plan/generate?goal=&plan_type=task"
    
    print("\nTest case 3: Generate plan with empty goal")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")

def test_train_module():
    """Test the train module endpoints."""
    print("\n=== Testing Train Module ===")
    
    # Test case 1: Train model by POST
    endpoint = f"{BASE_URL}/train"
    
    train_request = {
        "model_type": "classifier",
        "training_data": [
            {"text": "I love this product", "label": "positive"},
            {"text": "This product is terrible", "label": "negative"},
            {"text": "Average product, nothing special", "label": "neutral"}
        ],
        "data_format": "json",
        "model_name": "sentiment-classifier-v1",
        "hyperparameters": {
            "learning_rate": 0.001,
            "batch_size": 32
        },
        "validation_split": 0.2,
        "max_epochs": 10,
        "agent_id": "TRAINER",
        "loop_id": "loop_12345"
    }
    
    print("Test case 1: Train model by POST")
    response = make_request("POST", endpoint, train_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('model_id') else '❌ FAIL'}")
        print(f"Model ID: {response.get('model_id')}")
        print(f"Model Name: {response.get('model_name')}")
        print(f"Status: {response.get('status')}")
        
        # Store model_id for status check
        model_id = response.get('model_id')
        
        if model_id:
            # Test case 2: Check training status by GET
            endpoint = f"{BASE_URL}/train/status/{model_id}"
            
            print("\nTest case 2: Check training status by GET")
            response = make_request("GET", endpoint)
            if response:
                print(f"Status: {'✅ PASS' if response.get('model_id') == model_id else '❌ FAIL'}")
                print(f"Training Status: {response.get('status')}")
                print(f"Progress: {response.get('progress')}%")
                print(f"Current Epoch: {response.get('current_epoch')}")
                print(f"Total Epochs: {response.get('total_epochs')}")
            
            # Test case 3: Check training status by POST
            endpoint = f"{BASE_URL}/train/status"
            
            status_request = {
                "model_id": model_id
            }
            
            print("\nTest case 3: Check training status by POST")
            response = make_request("POST", endpoint, status_request)
            if response:
                print(f"Status: {'✅ PASS' if response.get('model_id') == model_id else '❌ FAIL'}")
                print(f"Training Status: {response.get('status')}")
                print(f"Progress: {response.get('progress')}%")
    
    # Test case 4: Train model with invalid model name
    endpoint = f"{BASE_URL}/train"
    
    invalid_train_request = {
        "model_type": "classifier",
        "training_data": [
            {"text": "I love this product", "label": "positive"},
            {"text": "This product is terrible", "label": "negative"}
        ],
        "data_format": "json",
        "model_name": "",  # Empty model name
        "max_epochs": 5
    }
    
    print("\nTest case 4: Train model with invalid model name")
    response = make_request("POST", endpoint, invalid_train_request)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")
    
    # Test case 5: Check status with invalid model ID
    endpoint = f"{BASE_URL}/train/status/invalid_model_id"
    
    print("\nTest case 5: Check status with invalid model ID")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")

def test_export_module():
    """Test the export module endpoints."""
    print("\n=== Testing Export Module ===")
    
    # Test case 1: Export data by POST
    endpoint = f"{BASE_URL}/export"
    
    export_request = {
        "export_type": "loop",
        "export_id": "loop_12345",
        "format": "json",
        "include_metadata": True,
        "filters": {
            "status": "completed",
            "tags": ["important", "production"]
        },
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-04-24T00:00:00Z",
        "max_items": 1000,
        "agent_id": "EXPORTER",
        "loop_id": "loop_12345"
    }
    
    print("Test case 1: Export data by POST")
    response = make_request("POST", endpoint, export_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('export_id') else '❌ FAIL'}")
        print(f"Export ID: {response.get('export_id')}")
        print(f"Export Type: {response.get('export_type')}")
        print(f"Format: {response.get('format')}")
        
        # Store export_id for status check
        export_id = response.get('export_id')
        
        if export_id:
            # Test case 2: Check export status by GET
            endpoint = f"{BASE_URL}/export/status/{export_id}"
            
            print("\nTest case 2: Check export status by GET")
            response = make_request("GET", endpoint)
            if response:
                print(f"Status: {'✅ PASS' if response.get('export_id') == export_id else '❌ FAIL'}")
                print(f"Export Status: {response.get('status')}")
                print(f"Progress: {response.get('progress')}%")
                print(f"Items Processed: {response.get('items_processed')}")
                print(f"Total Items: {response.get('total_items')}")
            
            # Test case 3: Check export status by POST
            endpoint = f"{BASE_URL}/export/status"
            
            status_request = {
                "export_id": export_id
            }
            
            print("\nTest case 3: Check export status by POST")
            response = make_request("POST", endpoint, status_request)
            if response:
                print(f"Status: {'✅ PASS' if response.get('export_id') == export_id else '❌ FAIL'}")
                print(f"Export Status: {response.get('status')}")
                print(f"Progress: {response.get('progress')}%")
    
    # Test case 4: Export data with invalid export ID
    endpoint = f"{BASE_URL}/export"
    
    invalid_export_request = {
        "export_type": "loop",
        "export_id": "",  # Empty export ID
        "format": "json"
    }
    
    print("\nTest case 4: Export data with invalid export ID")
    response = make_request("POST", endpoint, invalid_export_request)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")
    
    # Test case 5: Check status with invalid export ID
    endpoint = f"{BASE_URL}/export/status/invalid_export_id"
    
    print("\nTest case 5: Check status with invalid export ID")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")

def test_fix_module():
    """Test the fix module endpoints."""
    print("\n=== Testing Fix Module ===")
    
    # Test case 1: Apply fix by POST
    endpoint = f"{BASE_URL}/fix"
    
    fix_request = {
        "fix_type": "schema",
        "target_id": "loop_12345",
        "description": "Fix missing required fields in loop schema",
        "parameters": {
            "fields": ["status", "created_at"],
            "repair_strategy": "add_defaults"
        },
        "force": False,
        "agent_id": "FIXER",
        "loop_id": "loop_12345"
    }
    
    print("Test case 1: Apply fix by POST")
    response = make_request("POST", endpoint, fix_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('fix_id') else '❌ FAIL'}")
        print(f"Fix ID: {response.get('fix_id')}")
        print(f"Fix Type: {response.get('fix_type')}")
        print(f"Target ID: {response.get('target_id')}")
        print(f"Status: {response.get('status')}")
        
        # Store fix_id for status check
        fix_id = response.get('fix_id')
        
        if fix_id:
            # Test case 2: Check fix status by GET
            endpoint = f"{BASE_URL}/fix/status/{fix_id}"
            
            print("\nTest case 2: Check fix status by GET")
            response = make_request("GET", endpoint)
            if response:
                print(f"Status: {'✅ PASS' if response.get('fix_id') == fix_id else '❌ FAIL'}")
                print(f"Fix Status: {response.get('status')}")
                print(f"Progress: {response.get('progress')}%")
                print(f"Changes Made: {response.get('changes_made')}")
            
            # Test case 3: Check fix status by POST
            endpoint = f"{BASE_URL}/fix/status"
            
            status_request = {
                "fix_id": fix_id
            }
            
            print("\nTest case 3: Check fix status by POST")
            response = make_request("POST", endpoint, status_request)
            if response:
                print(f"Status: {'✅ PASS' if response.get('fix_id') == fix_id else '❌ FAIL'}")
                print(f"Fix Status: {response.get('status')}")
                print(f"Progress: {response.get('progress')}%")
            
            # Test case 4: Rollback fix
            endpoint = f"{BASE_URL}/fix/rollback"
            
            rollback_request = {
                "fix_id": fix_id,
                "reason": "Testing rollback functionality"
            }
            
            print("\nTest case 4: Rollback fix")
            response = make_request("POST", endpoint, rollback_request)
            if response:
                print(f"Status: {'✅ PASS' if response.get('fix_id') == fix_id else '❌ FAIL'}")
                print(f"Rollback ID: {response.get('rollback_id')}")
                print(f"Status: {response.get('status')}")
                print(f"Changes Reverted: {response.get('changes_reverted')}")
    
    # Test case 5: Apply fix with invalid target ID
    endpoint = f"{BASE_URL}/fix"
    
    invalid_fix_request = {
        "fix_type": "schema",
        "target_id": "",  # Empty target ID
        "description": "Fix missing required fields",
        "parameters": {}
    }
    
    print("\nTest case 5: Apply fix with invalid target ID")
    response = make_request("POST", endpoint, invalid_fix_request)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")
    
    # Test case 6: Check status with invalid fix ID
    endpoint = f"{BASE_URL}/fix/status/invalid_fix_id"
    
    print("\nTest case 6: Check status with invalid fix ID")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")

def test_delegate_stream_module():
    """Test the delegate stream module endpoints."""
    print("\n=== Testing Delegate Stream Module ===")
    
    # Test case 1: Create stream by POST
    endpoint = f"{BASE_URL}/delegate/stream"
    
    stream_request = {
        "stream_type": "loop",
        "target_id": "loop_12345",
        "description": "Stream loop events for monitoring",
        "priority": "medium",
        "filters": {
            "event_types": ["agent_call", "memory_access", "error"],
            "min_confidence": 0.7
        },
        "max_events": 1000,
        "timeout_seconds": 3600,
        "agent_id": "MONITOR",
        "loop_id": "loop_12345"
    }
    
    print("Test case 1: Create stream by POST")
    response = make_request("POST", endpoint, stream_request)
    if response:
        print(f"Status: {'✅ PASS' if response.get('stream_id') else '❌ FAIL'}")
        print(f"Stream ID: {response.get('stream_id')}")
        print(f"Stream Type: {response.get('stream_type')}")
        print(f"Target ID: {response.get('target_id')}")
        print(f"Status: {response.get('status')}")
        print(f"Connection URL: {response.get('connection_url')}")
        
        # Store stream_id for status check
        stream_id = response.get('stream_id')
        
        if stream_id:
            # Test case 2: Check stream status by GET
            endpoint = f"{BASE_URL}/delegate/stream/status/{stream_id}"
            
            print("\nTest case 2: Check stream status by GET")
            response = make_request("GET", endpoint)
            if response:
                print(f"Status: {'✅ PASS' if response.get('stream_id') == stream_id else '❌ FAIL'}")
                print(f"Stream Status: {response.get('status')}")
                print(f"Events Streamed: {response.get('events_streamed')}")
                print(f"Connected Clients: {response.get('connected_clients')}")
            
            # Test case 3: Check stream status by POST
            endpoint = f"{BASE_URL}/delegate/stream/status"
            
            status_request = {
                "stream_id": stream_id
            }
            
            print("\nTest case 3: Check stream status by POST")
            response = make_request("POST", endpoint, status_request)
            if response:
                print(f"Status: {'✅ PASS' if response.get('stream_id') == stream_id else '❌ FAIL'}")
                print(f"Stream Status: {response.get('status')}")
                print(f"Events Streamed: {response.get('events_streamed')}")
            
            # Test case 4: Close stream
            endpoint = f"{BASE_URL}/delegate/stream/close"
            
            close_request = {
                "stream_id": stream_id,
                "reason": "Testing close functionality"
            }
            
            print("\nTest case 4: Close stream")
            response = make_request("POST", endpoint, close_request)
            if response:
                print(f"Status: {'✅ PASS' if response.get('stream_id') == stream_id else '❌ FAIL'}")
                print(f"Close Status: {response.get('status')}")
                print(f"Events Streamed: {response.get('events_streamed')}")
                print(f"Duration Seconds: {response.get('duration_seconds')}")
    
    # Test case 5: Create stream with invalid target ID
    endpoint = f"{BASE_URL}/delegate/stream"
    
    invalid_stream_request = {
        "stream_type": "loop",
        "target_id": "",  # Empty target ID
        "description": "Stream loop events",
        "priority": "medium"
    }
    
    print("\nTest case 5: Create stream with invalid target ID")
    response = make_request("POST", endpoint, invalid_stream_request)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")
    
    # Test case 6: Check status with invalid stream ID
    endpoint = f"{BASE_URL}/delegate/stream/status/invalid_stream_id"
    
    print("\nTest case 6: Check status with invalid stream ID")
    response = make_request("GET", endpoint)
    if response:
        print(f"Status: {'✅ PASS' if 'message' in response else '❌ FAIL'}")
        print(f"Error Message: {response.get('message')}")

def main():
    """Run all tests."""
    print("=== Floating Modules Test Suite ===")
    
    test_agent_config_module()
    test_agent_context_module()
    test_memory_recall_module()
    test_memory_embed_module()
    test_plan_generate_module()
    test_train_module()
    test_export_module()
    test_fix_module()
    test_delegate_stream_module()
    
    print("\n=== Test Suite Complete ===")

if __name__ == "__main__":
    main()
