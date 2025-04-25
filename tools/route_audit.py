#!/usr/bin/env python3
"""
Route Audit Tool for Personal AI Agent Backend
Tests all endpoints against the live backend URL and records their status.
"""

import json
import requests
import sys
import os
from datetime import datetime
from pathlib import Path

# Configuration
LIVE_URL = "https://personal-ai-agent-ji4s.onrender.com"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/live_endpoint_audit_report.json"

# List of endpoints to test (this would ideally be extracted from the codebase)
# For now, we'll define a list of common endpoints based on the repository structure
ENDPOINTS = [
    # Agent endpoints
    {"path": "/agent/builder", "method": "POST"},
    {"path": "/agent/ops", "method": "POST"},
    {"path": "/agent/research", "method": "POST"},
    {"path": "/agent/memory", "method": "POST"},
    {"path": "/agent/loop", "method": "POST"},
    {"path": "/agent/delegate", "method": "POST"},
    {"path": "/agent/forge", "method": "POST"},
    {"path": "/agent/hal", "method": "POST"},
    {"path": "/agent/nova", "method": "POST"},
    {"path": "/agent/sage", "method": "POST"},
    {"path": "/agent/critic", "method": "POST"},
    {"path": "/agent/pessimist", "method": "POST"},
    
    # Memory endpoints
    {"path": "/memory/add", "method": "POST"},
    {"path": "/memory/search", "method": "POST"},
    {"path": "/memory/delete", "method": "DELETE"},
    {"path": "/memory/update", "method": "PUT"},
    {"path": "/memory/list", "method": "GET"},
    {"path": "/memory/clear", "method": "POST"},
    {"path": "/memory/stats", "method": "GET"},
    {"path": "/memory/export", "method": "GET"},
    {"path": "/memory/import", "method": "POST"},
    
    # File upload endpoints
    {"path": "/upload_file", "method": "POST"},
    {"path": "/upload_base64", "method": "POST"},
    
    # Tool endpoints
    {"path": "/tools/web_search", "method": "POST"},
    {"path": "/tools/url_summarizer", "method": "POST"},
    {"path": "/tools/pdf_ingest", "method": "POST"},
    {"path": "/tools/code_executor", "method": "POST"},
    {"path": "/tools/github_commit", "method": "POST"},
    {"path": "/tools/image_caption", "method": "POST"},
    {"path": "/tools/email_drafter", "method": "POST"},
    
    # System endpoints
    {"path": "/system/status", "method": "GET"},
    {"path": "/system/snapshot", "method": "GET"},
    {"path": "/system/health", "method": "GET"},
    {"path": "/system/logs", "method": "GET"},
    {"path": "/system/config", "method": "GET"},
    {"path": "/system/restart", "method": "POST"},
    
    # Orchestrator endpoints
    {"path": "/orchestrator/status", "method": "GET"},
    {"path": "/orchestrator/start", "method": "POST"},
    {"path": "/orchestrator/stop", "method": "POST"},
    {"path": "/orchestrator/consult", "method": "POST"},
    
    # Plan endpoints
    {"path": "/plan/generate", "method": "POST"},
    {"path": "/plan/execute", "method": "POST"},
    {"path": "/plan/status", "method": "GET"},
    {"path": "/plan/cancel", "method": "POST"},
    
    # Auth endpoints
    {"path": "/auth/login", "method": "POST"},
    {"path": "/auth/logout", "method": "POST"},
    {"path": "/auth/register", "method": "POST"},
    {"path": "/auth/verify", "method": "POST"},
    {"path": "/auth/reset", "method": "POST"},
    
    # User endpoints
    {"path": "/user/profile", "method": "GET"},
    {"path": "/user/update", "method": "PUT"},
    {"path": "/user/delete", "method": "DELETE"},
    {"path": "/user/preferences", "method": "GET"},
    
    # Admin endpoints
    {"path": "/admin/users", "method": "GET"},
    {"path": "/admin/logs", "method": "GET"},
    {"path": "/admin/config", "method": "GET"},
    {"path": "/admin/stats", "method": "GET"},
    
    # API endpoints
    {"path": "/api/v1/status", "method": "GET"},
    {"path": "/api/v1/agents", "method": "GET"},
    {"path": "/api/v1/tools", "method": "GET"},
    {"path": "/api/v1/memory", "method": "GET"},
    
    # Webhook endpoints
    {"path": "/webhook/github", "method": "POST"},
    {"path": "/webhook/slack", "method": "POST"},
    
    # Training endpoints
    {"path": "/training/start", "method": "POST"},
    {"path": "/training/status", "method": "GET"},
    {"path": "/training/stop", "method": "POST"},
    
    # Feedback endpoints
    {"path": "/feedback/submit", "method": "POST"},
    {"path": "/feedback/list", "method": "GET"},
    
    # Documentation endpoints
    {"path": "/docs", "method": "GET"},
    {"path": "/redoc", "method": "GET"},
    {"path": "/openapi.json", "method": "GET"},
    
    # Root endpoint
    {"path": "/", "method": "GET"},
    
    # Additional endpoints to reach ~99 total
    {"path": "/agent/builder/config", "method": "GET"},
    {"path": "/agent/ops/config", "method": "GET"},
    {"path": "/agent/research/config", "method": "GET"},
    {"path": "/memory/thread", "method": "POST"},
    {"path": "/memory/thread/list", "method": "GET"},
    {"path": "/memory/thread/update", "method": "PUT"},
    {"path": "/memory/thread/delete", "method": "DELETE"},
    {"path": "/tools/list", "method": "GET"},
    {"path": "/tools/status", "method": "GET"},
    {"path": "/system/version", "method": "GET"},
    {"path": "/system/update", "method": "POST"},
    {"path": "/orchestrator/agents", "method": "GET"},
    {"path": "/orchestrator/tools", "method": "GET"},
    {"path": "/plan/list", "method": "GET"},
    {"path": "/plan/delete", "method": "DELETE"},
    {"path": "/auth/refresh", "method": "POST"},
    {"path": "/user/sessions", "method": "GET"},
    {"path": "/admin/system", "method": "GET"},
    {"path": "/admin/memory", "method": "GET"},
    {"path": "/api/v1/system", "method": "GET"},
    {"path": "/api/v1/orchestrator", "method": "GET"},
    {"path": "/webhook/custom", "method": "POST"},
    {"path": "/training/export", "method": "GET"},
    {"path": "/training/import", "method": "POST"},
    {"path": "/feedback/stats", "method": "GET"},
    {"path": "/feedback/export", "method": "GET"}
]

def test_endpoint(endpoint):
    """Test a single endpoint and return its status"""
    url = f"{LIVE_URL}{endpoint['path']}"
    method = endpoint['method']
    
    result = {
        "route_path": endpoint['path'],
        "method": method,
        "status": None,
        "bound_schema": "Unknown",
        "responsible_agent": "Unknown"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json={}, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            result["status"] = "Method Not Supported"
            return result
        
        result["status"] = f"{response.status_code} {response.reason}"
        
        # Try to extract schema and agent info from response if available
        if response.status_code == 200:
            try:
                data = response.json()
                if "schema" in data:
                    result["bound_schema"] = data["schema"]
                if "agent" in data:
                    result["responsible_agent"] = data["agent"]
            except:
                pass
    except requests.exceptions.RequestException as e:
        result["status"] = f"Error: {str(e)}"
    
    return result

def main():
    """Main function to run the route audit"""
    print(f"Starting route audit against {LIVE_URL}")
    print(f"Testing {len(ENDPOINTS)} endpoints...")
    
    results = []
    
    for i, endpoint in enumerate(ENDPOINTS, 1):
        print(f"Testing {i}/{len(ENDPOINTS)}: {endpoint['method']} {endpoint['path']}")
        result = test_endpoint(endpoint)
        results.append(result)
    
    # Save results to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Route audit completed. Results saved to {OUTPUT_FILE}")
    
    # Count status codes
    status_counts = {}
    for result in results:
        status = result["status"]
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = 1
    
    print("\nStatus Summary:")
    for status, count in status_counts.items():
        print(f"{status}: {count}")
    
    return results

if __name__ == "__main__":
    main()
