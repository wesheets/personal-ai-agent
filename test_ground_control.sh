#!/bin/bash

# Test script for Phase 6.2.1 Ground Control system status endpoints
# This script tests the new endpoints added to system_routes.py

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API base URL - use localhost for local testing
API_URL="http://localhost:8000"

# Create directory for response data
mkdir -p test_responses

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local payload=$3
    local description=$4
    
    echo -e "${BLUE}Testing ${method} ${endpoint}${NC} - ${description}"
    
    # Create the response file path
    response_file="test_responses/$(echo ${endpoint} | tr '/' '_').json"
    
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
    
    # Check if the request was successful
    if [ -f "${response_file}" ] && [ -s "${response_file}" ]; then
        # Check if the response contains an error message
        error_count=$(grep -c "error" "${response_file}")
        if [ $error_count -eq 0 ]; then
            echo -e "${GREEN}✅ ${method} ${endpoint} - Success${NC}"
            echo -e "${YELLOW}Response:${NC}"
            cat "${response_file}" | python3 -m json.tool
            echo ""
            return 0
        else
            echo -e "${RED}❌ ${method} ${endpoint} - Failed (Error in response)${NC}"
            echo -e "${YELLOW}Response:${NC}"
            cat "${response_file}" | python3 -m json.tool
            echo ""
            return 1
        fi
    else
        echo -e "${RED}❌ ${method} ${endpoint} - Failed (Empty or missing response)${NC}"
        return 1
    fi
}

# Print header
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 6.2.1 Ground Control Endpoint Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Testing system status endpoints..."
echo ""

# Initialize counters
total_endpoints=3
working_endpoints=0

# Test system status endpoint
echo -e "${BLUE}Testing System Status Endpoint${NC}"
echo -e "${BLUE}---------------------------${NC}"

if test_endpoint "GET" "/api/system/status" "project_id=test_project" "Get system status for a project"; then
    working_endpoints=$((working_endpoints + 1))
fi

# Test system pulse endpoint
echo -e "${BLUE}Testing System Pulse Endpoint${NC}"
echo -e "${BLUE}---------------------------${NC}"

if test_endpoint "GET" "/api/system/pulse" "" "Get system pulse status"; then
    working_endpoints=$((working_endpoints + 1))
fi

# Test system log endpoint
echo -e "${BLUE}Testing System Log Endpoint${NC}"
echo -e "${BLUE}-------------------------${NC}"

if test_endpoint "GET" "/api/system/log" "limit=5" "Get system log entries"; then
    working_endpoints=$((working_endpoints + 1))
fi

# Calculate success percentage
success_percentage=$(( (working_endpoints * 100) / total_endpoints ))

# Print summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total Endpoints: ${total_endpoints}"
echo -e "Working Endpoints: ${working_endpoints}"
echo -e "Success Rate: ${success_percentage}%"

# Check if all endpoints are working
if [ $success_percentage -eq 100 ]; then
    echo -e "${GREEN}✅ All endpoints are working properly!${NC}"
    echo -e "${GREEN}✅ Phase 6.2.1 Ground Control implementation is successful!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some endpoints are not working properly.${NC}"
    echo -e "${RED}❌ Phase 6.2.1 Ground Control implementation is incomplete.${NC}"
    exit 1
fi
