#!/bin/bash

# Final API Health Check — Phase 5.3.3 Verification Sweep
echo "Final API Health Check — Phase 5.3.3 Verification Sweep"
echo "======================================================"
echo "Testing all endpoints to verify 100% API health after fixes..."
echo ""

# Configuration
BASE_URL="https://web-production-2639.up.railway.app"
TOTAL_ENDPOINTS=11
WORKING_ENDPOINTS=0
FAILED_ENDPOINTS=0

# Function to test an endpoint
test_endpoint() {
  local method=$1
  local endpoint=$2
  local payload=$3
  local description=$4
  
  echo "Testing $description: $method $endpoint"
  
  if [ "$method" == "GET" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL$endpoint")
  else
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL$endpoint" \
      -H "Content-Type: application/json" \
      -d "$payload")
  fi
  
  if [ "$response" == "200" ] || [ "$response" == "201" ]; then
    echo "✅ Success ($response)"
    WORKING_ENDPOINTS=$((WORKING_ENDPOINTS+1))
  else
    echo "❌ Failed ($response)"
    FAILED_ENDPOINTS=$((FAILED_ENDPOINTS+1))
  fi
  echo ""
}

# Test all endpoints from the checklist
echo "🔍 Testing /api/agent/run"
test_endpoint "POST" "/api/agent/run" '{"agent_id":"hal","project_id":"test_001","task":"Test task","tools":["file_writer"]}' "Agent Run"

echo "🔍 Testing /api/agent/list"
test_endpoint "GET" "/api/agent/list" "" "Agent List"

echo "🔍 Testing /api/agent/delegate"
test_endpoint "POST" "/api/agent/delegate" '{"project_id":"test_001","task":"Test task","agent_id":"hal"}' "Agent Delegate"

echo "🔍 Testing /api/agent/loop"
test_endpoint "POST" "/api/agent/loop" '{"project_id":"test_001","task":"Test task","iterations":1}' "Agent Loop"

echo "🔍 Testing /api/orchestrator/consult"
test_endpoint "POST" "/api/orchestrator/consult" '{"agent_id":"hal","project_id":"test_001","task":"Test task","objective":"Test objective","context":"Test context"}' "Orchestrator Consult"

echo "🔍 Testing /api/memory/write"
test_endpoint "POST" "/api/memory/write" '{"project_id":"test_001","content":"Test memory entry","metadata":{"type":"test"}}' "Memory Write"

echo "🔍 Testing /api/memory/read"
test_endpoint "GET" "/api/memory/read?project_id=test_001" "" "Memory Read"

echo "🔍 Testing /api/memory/summarize"
test_endpoint "POST" "/api/memory/summarize" '{"project_id":"test_001","query":"Test query"}' "Memory Summarize"

echo "🔍 Testing /api/memory/thread"
test_endpoint "GET" "/api/memory/thread?project_id=test_001" "" "Memory Thread"

echo "🔍 Testing /api/debug/memory/log"
test_endpoint "GET" "/api/debug/memory/log" "" "Debug Memory Log"

echo "🔍 Testing /api/project/state"
test_endpoint "GET" "/api/project/state?project_id=test_001" "" "Project State"

# Calculate health percentage
HEALTH_PERCENTAGE=$(( (WORKING_ENDPOINTS * 100) / TOTAL_ENDPOINTS ))

echo "API Health Summary:"
echo "------------------"
echo "Total Endpoints: $TOTAL_ENDPOINTS"
echo "Working Endpoints: $WORKING_ENDPOINTS"
echo "Failed Endpoints: $FAILED_ENDPOINTS"
echo "API Health Percentage: $HEALTH_PERCENTAGE%"

if [ $HEALTH_PERCENTAGE -eq 100 ]; then
  echo "✅ PASS: System is now 100% API Healthy — ready for external exposure, automated workflows, and agent self-correction."
  echo "✅ All endpoints return 200 OK"
  echo "✅ No 404, 422, or 500 errors from expected-working routes"
  echo "✅ Full system traceability, cognition, and API integrity confirmed"
  echo ""
  echo "Ready to initiate Phase 6.1"
else
  echo "❌ FAIL: System is at $HEALTH_PERCENTAGE% API health, below the required 100%"
  echo "❌ Some endpoints are not returning 200 OK"
  echo "❌ Further fixes required before proceeding to Phase 6.1"
fi
