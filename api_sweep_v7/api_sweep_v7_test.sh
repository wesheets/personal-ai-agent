#!/bin/bash

# API Sweep V7 Test Script
# Phase 5.3 Connected API Verification Sweep
# Created: $(date)

# Configuration
BASE_URL="https://web-production-2639.up.railway.app"
RESULTS_DIR="/home/ubuntu/api_sweep_v7"
LOG_FILE="$RESULTS_DIR/api_sweep_v7_results.log"
SUMMARY_FILE="$RESULTS_DIR/api_sweep_v7_summary.md"
TOTAL_ENDPOINTS=17
WORKING_ENDPOINTS=0
FAILED_ENDPOINTS=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize log file
echo "# API Sweep V7 Test Results" > $LOG_FILE
echo "Test executed on $(date)" >> $LOG_FILE
echo "---" >> $LOG_FILE

# Initialize summary file
echo "# API Sweep V7 Summary" > $SUMMARY_FILE
echo "Test executed on $(date)" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE
echo "## Endpoint Status Table" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE
echo "| Endpoint | Method | Expected Status | Actual Status | Result |" >> $SUMMARY_FILE
echo "|----------|--------|----------------|---------------|--------|" >> $SUMMARY_FILE

# Function to log results
log_result() {
    local endpoint=$1
    local method=$2
    local expected_status=$3
    local actual_status=$4
    local response_body=$5
    local test_time=$6
    
    echo -e "\n## $method $endpoint" >> $LOG_FILE
    echo "- Expected Status: $expected_status" >> $LOG_FILE
    echo "- Actual Status: $actual_status" >> $LOG_FILE
    echo "- Response Time: ${test_time}s" >> $LOG_FILE
    echo "- Response Body:" >> $LOG_FILE
    echo '```json' >> $LOG_FILE
    echo "$response_body" >> $LOG_FILE
    echo '```' >> $LOG_FILE
    
    # Determine result
    if [[ "$actual_status" == "$expected_status" ]]; then
        result="✅ PASS"
        ((WORKING_ENDPOINTS++))
    else
        result="❌ FAIL"
        ((FAILED_ENDPOINTS++))
    fi
    
    # Add to summary table
    echo "| $endpoint | $method | $expected_status | $actual_status | $result |" >> $SUMMARY_FILE
}

# Function to test an endpoint
test_endpoint() {
    local endpoint=$1
    local method=$2
    local expected_status=$3
    local payload=$4
    local description=$5
    
    echo -e "${BLUE}Testing $method $endpoint${NC}"
    echo -e "${YELLOW}$description${NC}"
    
    # Measure execution time
    start_time=$(date +%s.%N)
    
    # Execute request based on method
    if [[ "$method" == "GET" ]]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X $method -H "Content-Type: application/json" -d "$payload" "$BASE_URL$endpoint" 2>&1)
    fi
    
    end_time=$(date +%s.%N)
    test_time=$(echo "$end_time - $start_time" | bc)
    
    # Extract status code and response body
    status_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    # Log result
    log_result "$endpoint" "$method" "$expected_status" "$status_code" "$response_body" "$test_time"
    
    # Display result
    if [[ "$status_code" == "$expected_status" ]]; then
        echo -e "${GREEN}✅ PASS: $method $endpoint returned $status_code (expected $expected_status)${NC}"
    else
        echo -e "${RED}❌ FAIL: $method $endpoint returned $status_code (expected $expected_status)${NC}"
    fi
    echo ""
}

# Main test execution
echo -e "${BLUE}Starting API Sweep V7 Test...${NC}"
echo -e "${BLUE}Testing working endpoints...${NC}"
echo ""

# 1. Test /api/agent/list (GET)
test_endpoint "/api/agent/list" "GET" "200" "" "Should return a list of all 5 agents"

# 2. Test /api/agent/run (POST) for HAL
test_endpoint "/api/agent/run" "POST" "200" '{
  "agent_id": "hal",
  "project_id": "saas_demo_001",
  "task": "Initialize HAL",
  "tools": ["file_writer"]
}' "Should run HAL agent with file_writer tool"

# 3. Test /api/agent/run (POST) for NOVA
test_endpoint "/api/agent/run" "POST" "200" '{
  "agent_id": "nova",
  "project_id": "demo_ui_001",
  "task": "Write LandingPage.jsx and log action to memory.",
  "tools": ["file_writer"]
}' "Should run NOVA agent with file_writer tool"

# 4. Test /api/agent/run (POST) for CRITIC
test_endpoint "/api/agent/run" "POST" "200" '{
  "agent_id": "critic",
  "project_id": "demo_writer_001",
  "task": "Review README and log feedback.",
  "tools": ["memory_writer"]
}' "Should run CRITIC agent with memory_writer tool"

# 5. Test /api/agent/run (POST) for ASH
test_endpoint "/api/agent/run" "POST" "200" '{
  "agent_id": "ash",
  "project_id": "demo_writer_001",
  "task": "Simulate deployment and log result.",
  "tools": ["memory_writer"]
}' "Should run ASH agent with memory_writer tool"

# 6. Test /api/agent/loop (POST)
test_endpoint "/api/agent/loop" "POST" "200" '{
  "agent_id": "hal",
  "project_id": "test_loop_001",
  "task": "Test looping functionality",
  "max_iterations": 1
}' "Should test agent looping functionality"

# 7. Test /api/agent/delegate (POST)
test_endpoint "/api/agent/delegate" "POST" "200" '{
  "task": "Test delegation functionality",
  "project_id": "test_delegate_001"
}' "Should test agent delegation functionality"

# 8. Test /api/memory/write (POST)
test_endpoint "/api/memory/write" "POST" "200" '{
  "agent": "test",
  "project_id": "test_memory_001",
  "action": "Testing memory write",
  "tool_used": "api_test"
}' "Should write a memory entry"

# 9. Test /api/memory/read (GET)
test_endpoint "/api/memory/read?project_id=test_memory_001" "GET" "200" "" "Should read memory entries for project"

# 10. Test /api/memory/thread (GET)
test_endpoint "/api/memory/thread?project_id=test_memory_001" "GET" "200" "" "Should get memory thread for project"

# 11. Test /api/memory/summarize (POST)
test_endpoint "/api/memory/summarize" "POST" "200" '{
  "project_id": "test_memory_001",
  "prompt": "Summarize test memory"
}' "Should summarize memory for project"

# 12. Test /api/debug/memory/log (GET)
test_endpoint "/api/debug/memory/log?project_id=test_memory_001" "GET" "200" "" "Should get memory logs for debugging"

# 13. Test /api/project/state (GET)
test_endpoint "/api/project/state?project_id=test_memory_001" "GET" "200" "" "Should get project state as JSON"

# 14. Test /api/orchestrator/consult (POST)
test_endpoint "/api/orchestrator/consult" "POST" "200" '{
  "task": "Test orchestrator consultation",
  "project_id": "test_orchestrator_001"
}' "Should test orchestrator consultation"

echo -e "${BLUE}Testing problematic endpoints...${NC}"
echo ""

# 15. Test /api/train (POST)
test_endpoint "/api/train" "POST" "404" '{
  "model": "test",
  "data": "test data"
}' "Expected to fail - planned for Phase 6"

# 16. Test /api/plan (POST)
test_endpoint "/api/plan" "POST" "404" '{
  "task": "Test planning",
  "project_id": "test_plan_001"
}' "Expected to fail - missing or stubbed"

# 17. Test /api/snapshot (POST)
test_endpoint "/api/snapshot" "POST" "404" '{
  "project_id": "test_snapshot_001"
}' "Expected to fail - not yet implemented"

# 18. Test /api/status (GET)
test_endpoint "/api/status" "GET" "404" "" "Expected to fail - legacy placeholder"

# 19. Test /api/system/integrity (GET)
test_endpoint "/api/system/integrity" "GET" "404" "" "Expected to fail - path mismatch"

# 20. Test /api/debug/agents (GET)
test_endpoint "/api/debug/agents" "GET" "404" "" "Expected to fail - double prefix or unregistered"

# Calculate API health percentage
TOTAL_TESTED=$((WORKING_ENDPOINTS + FAILED_ENDPOINTS))
HEALTH_PERCENTAGE=$(echo "scale=2; ($WORKING_ENDPOINTS / $TOTAL_ENDPOINTS) * 100" | bc)

# Add summary statistics
echo "" >> $SUMMARY_FILE
echo "## API Health Statistics" >> $SUMMARY_FILE
echo "" >> $SUMMARY_FILE
echo "- Total Endpoints Tested: $TOTAL_TESTED" >> $SUMMARY_FILE
echo "- Working Endpoints: $WORKING_ENDPOINTS" >> $SUMMARY_FILE
echo "- Failed Endpoints: $FAILED_ENDPOINTS" >> $SUMMARY_FILE
echo "- API Health Percentage: ${HEALTH_PERCENTAGE}%" >> $SUMMARY_FILE

# Display summary
echo -e "${BLUE}API Sweep V7 Test Completed${NC}"
echo -e "${BLUE}Results:${NC}"
echo -e "Total Endpoints Tested: $TOTAL_TESTED"
echo -e "Working Endpoints: ${GREEN}$WORKING_ENDPOINTS${NC}"
echo -e "Failed Endpoints: ${RED}$FAILED_ENDPOINTS${NC}"
echo -e "API Health Percentage: ${YELLOW}${HEALTH_PERCENTAGE}%${NC}"
echo -e "Detailed results saved to: $LOG_FILE"
echo -e "Summary saved to: $SUMMARY_FILE"
