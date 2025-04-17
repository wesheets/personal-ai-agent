#!/usr/bin/env python3
"""
Test script for HAL agent with project state awareness.
This script tests if HAL agent correctly skips work when README.md already exists.
"""

import os
import sys
import json
from app.modules.agent_runner import run_hal_agent

# Create project_states directory if it doesn't exist
os.makedirs("project_states", exist_ok=True)

# Copy test project state to project_states directory
with open("test_project_state.json", "r") as f:
    project_state = json.load(f)

# Save to project_states directory
with open(f"project_states/test_project.json", "w") as f:
    json.dump(project_state, f, indent=2)

print("🧪 Testing HAL agent with existing README.md...")
result = run_hal_agent("Create initial files", "test_project", ["file_writer"])

print("\n📊 Test Results:")
print(f"Status: {result.get('status')}")
print(f"Notes: {result.get('notes')}")
print(f"Project State: {json.dumps(result.get('project_state'), indent=2)}")

# Verify test passed
if result.get('status') == 'skipped' and 'README.md already exists' in result.get('notes', ''):
    print("\n✅ TEST PASSED: HAL agent correctly skipped duplicate work")
else:
    print("\n❌ TEST FAILED: HAL agent did not skip duplicate work")
