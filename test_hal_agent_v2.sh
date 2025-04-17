#!/bin/bash

# Test script for HAL agent run endpoint with file_writer tool
# This script tests the Phase 5.1 HAL Agent Memory Logging + Output Fix

echo "Testing HAL agent run endpoint with file_writer tool..."

# Create test payload
cat > hal_test_payload.json << EOF
{
  "agent_id": "hal",
  "project_id": "demo_writer_001",
  "task": "Create README.md and log action to memory.",
  "tools": ["file_writer"]
}
EOF

# Create test directory for HAL
mkdir -p /home/ubuntu/promethios/personal-ai-agent/verticals/demo_writer_001

# Run test using Python to simulate API call
python3 -c "
import sys
sys.path.append('/home/ubuntu/promethios/personal-ai-agent')
from routes.agent_routes import agent_run
import json
import asyncio

async def test_hal():
    # Load test payload
    with open('hal_test_payload.json', 'r') as f:
        payload = json.load(f)
    
    # Call agent_run function
    result = await agent_run(payload)
    
    # Print result
    print('HAL Test Result:')
    print(json.dumps(result, indent=2))
    
    # Check if output contains standardized fields
    if 'output' in result:
        output = result['output']
        print('\\nOutput fields check:')
        print(f'- files_created: {\"✅ Present\" if \"files_created\" in output else \"❌ Missing\"}')
        print(f'- actions_taken: {\"✅ Present\" if \"actions_taken\" in output else \"❌ Missing\"}')
        print(f'- notes: {\"✅ Present\" if \"notes\" in output else \"❌ Missing\"}')
        print(f'- status: {\"✅ Present\" if \"status\" in output else \"❌ Missing\"}')
        
        if all(field in output for field in ['files_created', 'actions_taken', 'notes', 'status']):
            print('\\n✅ TEST PASSED: All required fields present in output')
        else:
            print('\\n❌ TEST FAILED: Some required fields missing in output')
    else:
        print('\\n❌ TEST FAILED: No output field in response')

# Run the test
asyncio.run(test_hal())
"

# Check if file was actually created
if [ -f "/home/ubuntu/promethios/personal-ai-agent/verticals/demo_writer_001/README.md" ]; then
  echo "✅ File verification PASSED: README.md was created"
  echo "File content:"
  cat /home/ubuntu/promethios/personal-ai-agent/verticals/demo_writer_001/README.md
else
  echo "❌ File verification FAILED: README.md was not created"
fi

# Clean up
rm hal_test_payload.json
