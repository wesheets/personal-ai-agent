#!/bin/bash

# Test script for project state endpoint
echo "Testing Project State Endpoint..."
echo "=================================="

# Configuration
BASE_URL="https://web-production-2639.up.railway.app"
PROJECT_ID="test_project_001"
ENDPOINT="/api/project/state"

# Test GET request
echo "GET $BASE_URL$ENDPOINT?project_id=$PROJECT_ID"
curl -s -X GET "$BASE_URL$ENDPOINT?project_id=$PROJECT_ID" | jq .

echo ""
echo "Test completed."
