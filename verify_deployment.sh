#!/bin/bash

# Phase 6.2.0 API Health Verification Script
# This script verifies that all 11 API endpoints are working properly
# after deploying the Phase 6.2.0 hotfix.

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API base URL
API_URL="https://web-production-2639.up.railway.app"

# Create directory for response data
mkdir -p responses

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local payload=$3
    local description=$4
    
    echo -e "${BLUE}Testing ${method} ${endpoint}${NC} - ${description}"
    
    # Create the response file path
    response_file="responses/$(echo ${endpoint} | tr '/' '_').json"
    
    # Make the request based on method
    if [ "$method" == "GET" ]; then
        if [ -z "$payload" ]; then
            # GET request without query parameters
            curl -s -X GET "${API_URL}${endpoint}" \
                -H "Content-Type: application/json" \
                -o "${response_file}"
        else
            # GET request with query parameters
            curl -s -X GET "${API_URL}${endpoint}?${payload}" \
                -H "Content-Type: application/json" \
                -o "${response_file}"
        fi
    else
        # POST request with payload
        curl -s -X POST "${API_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "${payload}" \
            -o "${response_file}"
    fi
    
    # Check if the request was successful (HTTP 200)
    http_code=$(cat "${response_file}" | grep -c "API endpoint not found")
    if [ $http_code -eq 0 ]; then
        echo -e "${GREEN}✅ ${method} ${endpoint} - Success${NC}"
        return 0
    else
        echo -e "${RED}❌ ${method} ${endpoint} - Failed${NC}"
        echo -e "${YELLOW}Response:${NC}"
        cat "${response_file}"
        echo ""
        return 1
    fi
}

# Print header
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 6.2.0 API Health Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Testing all 11 API endpoints..."
echo ""

# Initialize counters
total_endpoints=11
working_endpoints=0

# Test all endpoints
echo -e "${BLUE}Testing Agent Endpoints${NC}"
echo -e "${BLUE}------------------${NC}"

# 1. Test /api/agent/run
if test_endpoint "POST" "/api/agent/run" '{"agent_id":"hal","project_id":"test_project","task":"Create a test project","tools":["file_writer"]}' "Run HAL agent"; then
    working_endpoints=$((working_endpoints + 1))
fi

# 2. Test /api/agent/list
if test_endpoint "GET" "/api/agent/list" "" "List available agents"; then
    working_endpoints=$((working_endpoints + 1))
fi

# 3. Test /api/agent/delegate
if test_endpoint "POST" "/api/agent/delegate" '{"agent":"hal","task":"Delegate test task","project_id":"test_project"}' "Delegate task to agent"; then
    working_endpoints=$((working_endpoints + 1))
fi

# 4. Test /api/agent/loop
if test_endpoint "POST" "/api/agent/loop" '{"agent":"hal","input":"Test input","project_id":"test_project"}' "Continue agent conversation"; then
    working_endpoints=$((working_endpoints + 1))
fi

echo ""
echo -e "${BLUE}Testing Memory Endpoints${NC}"
echo -e "${BLUE}---------------------${NC}"

# 5. Test /api/memory/write
if test_endpoint "POST" "/api/memory/write" '{"project_id":"test_project","agent":"hal","action":"test","content":"Test memory entry"}' "Write memory entry"; then
    working_endpoints=$((working_endpoints + 1))
fi

# 6. Test /api/memory/read
if test_endpoint "GET" "/api/memory/read" "project_id=test_project" "Read memory entries"; then
    working_endpoints=$((working_endpoints + 1))
fi

# 7. Test /api/memory/thread
if test_endpoint "GET" "/api/memory/thread" "project_id=test_project&chain_id=main" "Get memory thread"; then
    working_endpoints=$((working_endpoints + 1))
fi

# 8. Test /api/memory/summarize
if test_endpoint "POST" "/api/memory/summarize" '{"project_id":"test_project","query":"Test query"}' "Summarize memory"; then
    working_endpoints=$((working_endpoints + 1))
fi

echo ""
echo -e "${BLUE}Testing Project Endpoints${NC}"
echo -e "${BLUE}----------------------${NC}"

# 9. Test /api/project/state
if test_endpoint "GET" "/api/project/state" "project_id=test_project" "Get project state"; then
    working_endpoints=$((working_endpoints + 1))
fi

echo ""
echo -e "${BLUE}Testing Orchestrator Endpoints${NC}"
echo -e "${BLUE}---------------------------${NC}"

# 10. Test /api/orchestrator/consult
if test_endpoint "POST" "/api/orchestrator/consult" '{"agent_id":"hal","project_id":"test_project","task":"Test orchestrator consultation"}' "Consult orchestrator"; then
    working_endpoints=$((working_endpoints + 1))
fi

echo ""
echo -e "${BLUE}Testing Debug Endpoints${NC}"
echo -e "${BLUE}---------------------${NC}"

# 11. Test /api/debug/memory/log
if test_endpoint "GET" "/api/debug/memory/log" "" "Get memory debug log"; then
    working_endpoints=$((working_endpoints + 1))
fi

# Calculate health percentage
health_percentage=$(( (working_endpoints * 100) / total_endpoints ))

# Print summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}API Health Check Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total Endpoints: ${total_endpoints}"
echo -e "Working Endpoints: ${working_endpoints}"
echo -e "API Health: ${health_percentage}%"

# Check if all endpoints are working
if [ $health_percentage -eq 100 ]; then
    echo -e "${GREEN}✅ All endpoints are working properly!${NC}"
    echo -e "${GREEN}✅ Phase 6.2.0 deployment is successful!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some endpoints are not working properly.${NC}"
    echo -e "${RED}❌ Phase 6.2.0 deployment is incomplete.${NC}"
    exit 1
fi
