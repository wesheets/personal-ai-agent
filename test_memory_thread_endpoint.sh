#!/bin/bash

# Test script for memory thread endpoint
echo "Testing Memory Thread Endpoint..."
echo "=================================="

# Configuration
BASE_URL="https://web-production-2639.up.railway.app"
PROJECT_ID="test_project_001"
CHAIN_ID="test_chain_001"
ENDPOINT="/api/memory/thread"

# Test GET request
echo "GET $BASE_URL$ENDPOINT?project_id=$PROJECT_ID&chain_id=$CHAIN_ID"
curl -s -X GET "$BASE_URL$ENDPOINT?project_id=$PROJECT_ID&chain_id=$CHAIN_ID" | jq .

echo ""
echo "Test completed."
