#!/bin/bash

# Test script for orchestrator consult endpoint
echo "Testing Orchestrator Consult Endpoint..."
echo "========================================"

# Configuration
BASE_URL="https://web-production-2639.up.railway.app"
ENDPOINT="/api/orchestrator/consult"

# Test POST request
echo "POST $BASE_URL$ENDPOINT"
curl -s -X POST "$BASE_URL$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test_project_001",
    "task": "Test orchestrator consult endpoint",
    "context": "This is a test of the orchestrator consult endpoint with the updated validation."
  }' | jq .

echo ""
echo "Test completed."
