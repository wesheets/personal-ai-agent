#!/usr/bin/env python3
"""
Test script for CRITIC agent with project state awareness.
This script tests if CRITIC agent correctly checks for NOVA's work before proceeding.
"""

import os
import sys
import json
from app.modules.agent_runner import run_critic_agent

# Create project_states directory if it doesn't exist
os.makedirs("project_states", exist_ok=True)

# Test 1: Project state without NOVA
print("🧪 Test 1: Testing CRITIC agent without NOVA in agents_involved...")
project_state = {
    "project_id": "test_project_critic1",
    "status": "in_progress",
    "files_created": ["/verticals/test_project_critic1/README.md"],
    "agents_involved": ["hal"],  # NOVA not in list
    "latest_agent_action": {"agent": "hal", "action": "Created initial files"},
    "next_recommended_step": "Run NOVA",
    "tool_usage": {"file_writer": 1}
}

# Save to project_states directory
with open(f"project_states/test_project_critic1.json", "w") as f:
    json.dump(project_state, f, indent=2)

result1 = run_critic_agent("Review UI", "test_project_critic1", ["code_reviewer"])

print("\n📊 Test 1 Results:")
print(f"Status: {result1.get('status')}")
print(f"Notes: {result1.get('notes')}")

# Test 2: Project state with NOVA
print("\n🧪 Test 2: Testing CRITIC agent with NOVA in agents_involved...")
project_state = {
    "project_id": "test_project_critic2",
    "status": "in_progress",
    "files_created": [
        "/verticals/test_project_critic2/README.md",
        "/verticals/test_project_critic2/frontend/LandingPage.jsx"
    ],
    "agents_involved": ["hal", "nova"],  # NOVA in list
    "latest_agent_action": {"agent": "nova", "action": "Designed UI"},
    "next_recommended_step": "Run CRITIC",
    "tool_usage": {"file_writer": 2}
}

# Save to project_states directory
with open(f"project_states/test_project_critic2.json", "w") as f:
    json.dump(project_state, f, indent=2)

result2 = run_critic_agent("Review UI", "test_project_critic2", ["code_reviewer"])

print("\n📊 Test 2 Results:")
print(f"Status: {result2.get('status', 'unknown')}")
print(f"Project State included: {'project_state' in result2}")

# Verify tests passed
if result1.get('status') == 'blocked' and 'NOVA has not' in result1.get('notes', ''):
    print("\n✅ TEST 1 PASSED: CRITIC agent correctly blocked when NOVA hasn't run")
else:
    print("\n❌ TEST 1 FAILED: CRITIC agent did not block when NOVA hasn't run")

if result2.get('status') != 'blocked' and 'project_state' in result2:
    print("✅ TEST 2 PASSED: CRITIC agent proceeded when NOVA has run and included project_state")
else:
    print("❌ TEST 2 FAILED: CRITIC agent did not proceed correctly when NOVA has run")
