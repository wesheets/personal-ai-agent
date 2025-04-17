#!/usr/bin/env python3
"""
Test script for ASH agent with project state awareness.
This script tests if ASH agent correctly checks project status before proceeding.
"""

import os
import sys
import json
from app.modules.agent_runner import run_ash_agent

# Create project_states directory if it doesn't exist
os.makedirs("project_states", exist_ok=True)

# Test 1: Project state not ready for deployment
print("🧪 Test 1: Testing ASH agent with status not ready for deployment...")
project_state = {
    "project_id": "test_project_ash1",
    "status": "in_progress",  # Not ready for deployment
    "files_created": [
        "/verticals/test_project_ash1/README.md",
        "/verticals/test_project_ash1/frontend/LandingPage.jsx"
    ],
    "agents_involved": ["hal", "nova", "critic"],
    "latest_agent_action": {"agent": "critic", "action": "Reviewed UI"},
    "next_recommended_step": "Run ASH",
    "tool_usage": {"file_writer": 2}
}

# Save to project_states directory
with open(f"project_states/test_project_ash1.json", "w") as f:
    json.dump(project_state, f, indent=2)

result1 = run_ash_agent("Create documentation", "test_project_ash1", ["doc_generator"])

print("\n📊 Test 1 Results:")
print(f"Status: {result1.get('status')}")
print(f"Notes: {result1.get('notes')}")

# Test 2: Project state ready for deployment
print("\n🧪 Test 2: Testing ASH agent with status ready for deployment...")
project_state = {
    "project_id": "test_project_ash2",
    "status": "ready_for_deploy",  # Ready for deployment
    "files_created": [
        "/verticals/test_project_ash2/README.md",
        "/verticals/test_project_ash2/frontend/LandingPage.jsx"
    ],
    "agents_involved": ["hal", "nova", "critic"],
    "latest_agent_action": {"agent": "critic", "action": "Reviewed UI"},
    "next_recommended_step": "Run ASH",
    "tool_usage": {"file_writer": 2}
}

# Save to project_states directory
with open(f"project_states/test_project_ash2.json", "w") as f:
    json.dump(project_state, f, indent=2)

result2 = run_ash_agent("Create documentation", "test_project_ash2", ["doc_generator"])

print("\n📊 Test 2 Results:")
print(f"Status: {result2.get('status', 'unknown')}")
print(f"Project State included: {'project_state' in result2}")

# Verify tests passed
if result1.get('status') == 'on_hold' and 'not ready for deployment' in result1.get('notes', ''):
    print("\n✅ TEST 1 PASSED: ASH agent correctly on hold when project not ready for deployment")
else:
    print("\n❌ TEST 1 FAILED: ASH agent did not go on hold when project not ready for deployment")

if result2.get('status') != 'on_hold' and 'project_state' in result2:
    print("✅ TEST 2 PASSED: ASH agent proceeded when project ready for deployment and included project_state")
else:
    print("❌ TEST 2 FAILED: ASH agent did not proceed correctly when project ready for deployment")
