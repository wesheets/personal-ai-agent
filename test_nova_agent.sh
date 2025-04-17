#!/bin/bash

# Test script for NOVA agent run endpoint with file_writer tool
# This script tests the Phase 5.1 NOVA Agent Memory Logging + Output Fix

echo "Testing NOVA agent run endpoint with file_writer tool..."

# Create test payload
cat > nova_test_payload.json << EOF
{
  "agent_id": "nova",
  "project_id": "demo_ui_001",
  "task": "Write LandingPage.jsx and log action to memory.",
  "tools": ["file_writer"]
}
EOF

# Create test directory for NOVA
mkdir -p /home/ubuntu/promethios/personal-ai-agent/verticals/demo_ui_001/frontend

# Run test using direct function call to avoid FastAPI dependency
python3 -c "
import sys
sys.path.append('/home/ubuntu/promethios/personal-ai-agent')
from app.modules.agent_runner import run_nova_agent
import json

# Load test payload
with open('nova_test_payload.json', 'r') as f:
    payload = json.load(f)

# Call run_nova_agent function directly
result = run_nova_agent(
    task=payload['task'],
    project_id=payload['project_id'],
    tools=payload['tools']
)

# Print result
print('NOVA Test Result:')
print(json.dumps(result, indent=2))

# Check if result contains standardized fields
print('\\nOutput fields check:')
print(f'- files_created: {\"✅ Present\" if \"files_created\" in result else \"❌ Missing\"}')
print(f'- actions_taken: {\"✅ Present\" if \"actions_taken\" in result else \"❌ Missing\"}')
print(f'- notes: {\"✅ Present\" if \"notes\" in result else \"❌ Missing\"}')
print(f'- status: {\"✅ Present\" if \"status\" in result else \"❌ Missing\"}')

if all(field in result for field in ['files_created', 'actions_taken', 'notes', 'status']):
    print('\\n✅ TEST PASSED: All required fields present in output')
else:
    print('\\n❌ TEST FAILED: Some required fields missing in output')
"

# Check if file was actually created
if [ -f "/home/ubuntu/promethios/personal-ai-agent/verticals/demo_ui_001/frontend/LandingPage.jsx" ]; then
  echo "✅ File verification PASSED: LandingPage.jsx was created"
  echo "File content:"
  cat /home/ubuntu/promethios/personal-ai-agent/verticals/demo_ui_001/frontend/LandingPage.jsx
else
  echo "❌ File verification FAILED: LandingPage.jsx was not created"
fi

# Clean up
rm nova_test_payload.json
