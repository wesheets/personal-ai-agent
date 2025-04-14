#!/usr/bin/env python3
"""
Debug Sequence Test Script

This script runs a sequence of tests for critical routes in the system
and logs the results using the debug_logger utility.

Usage:
    python run_debug_sequence.py
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the debug logger
from src.utils.debug_logger import log_test_result

# Base URL for API requests
BASE_URL = "http://localhost:3000"

def test_delegate_route():
    """Test the delegation route"""
    print("Testing /api/delegate route...")
    
    try:
        url = f"{BASE_URL}/api/delegate"
        payload = {
            "agent_name": "TestAgent",
            "objective": "Build a pricing page",
            "required_capabilities": ["web_design"],
            "auto_execute": False
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            log_test_result("Delegation", "/api/delegate", "PASS", 
                           f"Agent {payload['agent_name']} assigned task", 
                           f"Task: {payload['objective']}")
            print(f"✅ Delegation test passed: {result}")
        else:
            log_test_result("Delegation", "/api/delegate", "FAIL", 
                           f"Status code: {response.status_code}", 
                           f"Response: {response.text}")
            print(f"❌ Delegation test failed: {response.text}")
    except Exception as e:
        log_test_result("Delegation", "/api/delegate", "FAIL", 
                       f"Exception: {str(e)}", 
                       "Connection error or server not running")
        print(f"❌ Delegation test error: {str(e)}")

def test_memory_read_route():
    """Test the memory read route"""
    print("Testing /api/memory/read route...")
    
    try:
        url = f"{BASE_URL}/api/memory/read"
        params = {
            "agent_id": "TestAgent",
            "limit": 5
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            memory_count = len(result.get("memories", []))
            log_test_result("Memory", "/api/memory/read", "PASS", 
                           f"Retrieved {memory_count} memories", 
                           f"Agent: {params['agent_id']}")
            print(f"✅ Memory read test passed: {memory_count} memories retrieved")
        else:
            log_test_result("Memory", "/api/memory/read", "FAIL", 
                           f"Status code: {response.status_code}", 
                           f"Response: {response.text}")
            print(f"❌ Memory read test failed: {response.text}")
    except Exception as e:
        log_test_result("Memory", "/api/memory/read", "FAIL", 
                       f"Exception: {str(e)}", 
                       "Connection error or server not running")
        print(f"❌ Memory read test error: {str(e)}")

def test_memory_write_route():
    """Test the memory write route"""
    print("Testing /api/memory/write route...")
    
    try:
        url = f"{BASE_URL}/api/memory/write"
        payload = {
            "agent_id": "TestAgent",
            "memory_type": "test_memory",
            "content": "This is a test memory created by the debug sequence",
            "tags": ["test", "debug"]
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            log_test_result("Memory", "/api/memory/write", "PASS", 
                           f"Memory created with ID: {result.get('memory_id', 'unknown')}", 
                           f"Agent: {payload['agent_id']}, Type: {payload['memory_type']}")
            print(f"✅ Memory write test passed: {result}")
        else:
            log_test_result("Memory", "/api/memory/write", "FAIL", 
                           f"Status code: {response.status_code}", 
                           f"Response: {response.text}")
            print(f"❌ Memory write test failed: {response.text}")
    except Exception as e:
        log_test_result("Memory", "/api/memory/write", "FAIL", 
                       f"Exception: {str(e)}", 
                       "Connection error or server not running")
        print(f"❌ Memory write test error: {str(e)}")

def test_memory_summarize_route():
    """Test the memory summarize route"""
    print("Testing /api/memory/summarize route...")
    
    try:
        url = f"{BASE_URL}/api/memory/summarize"
        payload = {
            "agent_id": "TestAgent",
            "limit": 10
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            log_test_result("Memory", "/api/memory/summarize", "PASS", 
                           f"Summarized {result.get('memory_count', 0)} memories", 
                           f"Agent: {payload['agent_id']}")
            print(f"✅ Memory summarize test passed: {result.get('summary', '')[:50]}...")
        else:
            log_test_result("Memory", "/api/memory/summarize", "FAIL", 
                           f"Status code: {response.status_code}", 
                           f"Response: {response.text}")
            print(f"❌ Memory summarize test failed: {response.text}")
    except Exception as e:
        log_test_result("Memory", "/api/memory/summarize", "FAIL", 
                       f"Exception: {str(e)}", 
                       "Connection error or server not running")
        print(f"❌ Memory summarize test error: {str(e)}")

def test_memory_thread_route():
    """Test the memory thread route"""
    print("Testing /api/memory/thread route...")
    
    try:
        # First create a memory with a goal_id
        goal_id = f"test_goal_{int(time.time())}"
        
        # Create memory with goal_id
        write_url = f"{BASE_URL}/api/memory/write"
        write_payload = {
            "agent_id": "TestAgent",
            "memory_type": "test_thread",
            "content": "This is a test memory for thread testing",
            "tags": ["test", "thread"],
            "goal_id": goal_id
        }
        
        write_response = requests.post(write_url, json=write_payload)
        
        if write_response.status_code != 200:
            log_test_result("Memory", "/api/memory/write", "FAIL", 
                           "Failed to create test memory for thread test", 
                           f"Response: {write_response.text}")
            print(f"❌ Memory thread test setup failed: {write_response.text}")
            return
        
        # Now test the thread route
        url = f"{BASE_URL}/api/memory/thread"
        params = {
            "goal_id": goal_id
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            thread_count = len(result.get("thread", []))
            log_test_result("Memory", "/api/memory/thread", "PASS", 
                           f"Retrieved thread with {thread_count} memories", 
                           f"Goal ID: {goal_id}")
            print(f"✅ Memory thread test passed: {thread_count} memories in thread")
        else:
            log_test_result("Memory", "/api/memory/thread", "FAIL", 
                           f"Status code: {response.status_code}", 
                           f"Response: {response.text}")
            print(f"❌ Memory thread test failed: {response.text}")
    except Exception as e:
        log_test_result("Memory", "/api/memory/thread", "FAIL", 
                       f"Exception: {str(e)}", 
                       "Connection error or server not running")
        print(f"❌ Memory thread test error: {str(e)}")

def test_agent_list_route():
    """Test the agent list route"""
    print("Testing /api/agent/list route...")
    
    try:
        url = f"{BASE_URL}/api/agent/list"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            agent_count = len(result.get("agents", []))
            log_test_result("Agent", "/api/agent/list", "PASS", 
                           f"Retrieved {agent_count} agents", 
                           "Agent registry accessible")
            print(f"✅ Agent list test passed: {agent_count} agents retrieved")
        else:
            log_test_result("Agent", "/api/agent/list", "FAIL", 
                           f"Status code: {response.status_code}", 
                           f"Response: {response.text}")
            print(f"❌ Agent list test failed: {response.text}")
    except Exception as e:
        log_test_result("Agent", "/api/agent/list", "FAIL", 
                       f"Exception: {str(e)}", 
                       "Connection error or server not running")
        print(f"❌ Agent list test error: {str(e)}")

def test_system_status_route():
    """Test the system status route"""
    print("Testing /api/system/status route...")
    
    try:
        url = f"{BASE_URL}/api/system/status"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            log_test_result("System", "/api/system/status", "PASS", 
                           f"System running for {result.get('uptime', 'unknown')}", 
                           f"Agents: {result.get('agent_count', 0)}, Memories: {result.get('memory_store_size', 0)}")
            print(f"✅ System status test passed: {result}")
        else:
            log_test_result("System", "/api/system/status", "FAIL", 
                           f"Status code: {response.status_code}", 
                           f"Response: {response.text}")
            print(f"❌ System status test failed: {response.text}")
    except Exception as e:
        log_test_result("System", "/api/system/status", "FAIL", 
                       f"Exception: {str(e)}", 
                       "Connection error or server not running")
        print(f"❌ System status test error: {str(e)}")

def run_all_tests():
    """Run all test sequences"""
    print("Starting debug sequence tests...")
    print("=" * 50)
    
    # Log test sequence start
    log_test_result("Debug", "/tests/run_debug_sequence", "INFO", 
                   "Starting debug sequence tests", 
                   f"Timestamp: {datetime.now().isoformat()}")
    
    # Run all tests
    test_delegate_route()
    test_memory_read_route()
    test_memory_write_route()
    test_memory_summarize_route()
    test_memory_thread_route()
    test_agent_list_route()
    test_system_status_route()
    
    # Log test sequence completion
    log_test_result("Debug", "/tests/run_debug_sequence", "INFO", 
                   "Completed debug sequence tests", 
                   f"Timestamp: {datetime.now().isoformat()}")
    
    print("=" * 50)
    print("Debug sequence tests completed.")
    print(f"Check logs/debug_tracker.md for detailed results.")

if __name__ == "__main__":
    run_all_tests()
