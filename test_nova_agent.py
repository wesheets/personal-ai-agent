#!/usr/bin/env python3
"""
Test script for NOVA agent with project state awareness.
This script tests if NOVA agent correctly checks for HAL's work before proceeding.
"""

import os
import sys
import json
from app.modules.agent_runner import run_nova_agent

# Create project_states directory if it doesn't exist
os.makedirs("project_states", exist_ok=True)

# Test 1: Project state without HAL
print("🧪 Test 1: Testing NOVA agent without HAL in agents_involved...")
project_state = {
    "project_id": "test_project_nova1",
    "status": "in_progress",
    "files_created": ["/verticals/test_project_nova1/README.md"],
    "agents_involved": [],  # HAL not in list
    "latest_agent_action": {"agent": "system", "action": "Project initialized"},
    "next_recommended_step": "Run HAL",
    "tool_usage": {}
}

# Save to project_states directory
with open(f"project_states/test_project_nova1.json", "w") as f:
    json.dump(project_state, f, indent=2)

result1 = run_nova_agent("Design UI", "test_project_nova1", ["ui_designer"])

print("\n📊 Test 1 Results:")
print(f"Status: {result1.get('status')}")
print(f"Notes: {result1.get('notes')}")

# Test 2: Project state with HAL
print("\n🧪 Test 2: Testing NOVA agent with HAL in agents_involved...")
project_state = {
    "project_id": "test_project_nova2",
    "status": "in_progress",
    "files_created": ["/verticals/test_project_nova2/README.md"],
    "agents_involved": ["hal"],  # HAL in list
    "latest_agent_action": {"agent": "hal", "action": "Created initial files"},
    "next_recommended_step": "Run NOVA",
    "tool_usage": {"file_writer": 1}
}

# Save to project_states directory
with open(f"project_states/test_project_nova2.json", "w") as f:
    json.dump(project_state, f, indent=2)

result2 = run_nova_agent("Design UI", "test_project_nova2", ["ui_designer"])

print("\n📊 Test 2 Results:")
print(f"Status: {result2.get('status', 'unknown')}")
print(f"Project State included: {'project_state' in result2}")

# Verify tests passed
if result1.get('status') == 'blocked' and 'HAL has not' in result1.get('notes', ''):
    print("\n✅ TEST 1 PASSED: NOVA agent correctly blocked when HAL hasn't run")
else:
    print("\n❌ TEST 1 FAILED: NOVA agent did not block when HAL hasn't run")

if result2.get('status') != 'blocked' and 'project_state' in result2:
    print("✅ TEST 2 PASSED: NOVA agent proceeded when HAL has run and included project_state")
else:
    print("❌ TEST 2 FAILED: NOVA agent did not proceed correctly when HAL has run")
