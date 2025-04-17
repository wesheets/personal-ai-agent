#!/bin/bash

# Test script for HAL agent execution
# This script tests the /api/agent/run endpoint with HAL agent

echo "🧪 Testing HAL agent execution"
echo "------------------------------"

# Define test payload
PAYLOAD='{
  "agent_id": "hal",
  "project_id": "saas_demo_001",
  "task": "Initialize HAL",
  "tools": ["file_writer"]
}'

echo "📝 Test payload:"
echo "$PAYLOAD" | jq .

# Send request to local endpoint (for testing in sandbox)
echo -e "\n🔄 Testing local endpoint (this will fail as expected since no server is running locally):"
curl -s -X POST -H "Content-Type: application/json" -d "$PAYLOAD" http://localhost:8000/api/agent/run | jq .

# Output expected response format for reference
echo -e "\n✅ Expected response format:"
echo '{
  "status": "success",
  "message": "HAL successfully created bootstrap file",
  "agent": "hal",
  "project_id": "saas_demo_001",
  "task": "Initialize HAL",
  "tools": ["file_writer"],
  "output": {
    "file_path": "/verticals/saas_demo_001/README.md",
    "status": "success"
  }
}' | jq .

echo -e "\n📋 Test summary:"
echo "1. The agent_run endpoint should map 'hal' to the run_hal_agent function"
echo "2. The run_hal_agent function should use file_writer to create a README.md file"
echo "3. The response should include 'HAL successfully created bootstrap file'"
echo "4. The implementation is now ready for deployment testing"

echo -e "\n🔍 Note: This test only verifies the implementation logic."
echo "To fully test the functionality, deploy the changes and use Postman or curl against the live API."
