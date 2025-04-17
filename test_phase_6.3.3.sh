#!/bin/bash

# Test script for Phase 6.3.3 - Restart Promethios Core
# Tests both the AGENT_RUNNERS fix and the POST /system/summary endpoint

echo -e "\n\033[1;36m===== Phase 6.3.3 Hotfix Test Script =====\033[0m\n"

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test project ID
PROJECT_ID="test_project_$(date +%s)"
echo -e "${BLUE}Using test project ID: ${PROJECT_ID}${NC}\n"

# Function to check if server is running
check_server() {
  echo -e "${BLUE}Checking if server is running...${NC}"
  curl -s http://localhost:8000/health > /dev/null
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Server is running${NC}"
    return 0
  else
    echo -e "${RED}❌ Server is not running${NC}"
    return 1
  fi
}

# Function to start the server
start_server() {
  echo -e "${BLUE}Starting server...${NC}"
  cd /home/ubuntu/promethios/personal-ai-agent
  python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > server_output.log 2>&1 &
  SERVER_PID=$!
  echo -e "${BLUE}Server started with PID: ${SERVER_PID}${NC}"
  
  # Wait for server to start
  echo -e "${BLUE}Waiting for server to start...${NC}"
  for i in {1..10}; do
    sleep 2
    if check_server; then
      echo -e "${GREEN}✅ Server started successfully${NC}"
      return 0
    fi
    echo -e "${YELLOW}Still waiting for server to start (attempt $i/10)...${NC}"
  done
  
  echo -e "${RED}❌ Server failed to start within the timeout period${NC}"
  return 1
}

# Function to stop the server
stop_server() {
  if [ -n "$SERVER_PID" ]; then
    echo -e "${BLUE}Stopping server with PID: ${SERVER_PID}${NC}"
    kill $SERVER_PID
    wait $SERVER_PID 2>/dev/null
    echo -e "${GREEN}✅ Server stopped${NC}"
  fi
}

# Function to test the /api/agent/list endpoint (depends on AGENT_RUNNERS)
test_agent_list() {
  echo -e "\n${BLUE}Testing /api/agent/list endpoint...${NC}"
  RESPONSE=$(curl -s http://localhost:8000/api/agent/list)
  echo -e "${BLUE}Response: ${RESPONSE}${NC}"
  
  # Check if response contains "sage"
  if echo $RESPONSE | grep -q "sage"; then
    echo -e "${GREEN}✅ AGENT_RUNNERS fix verified - 'sage' agent is in the list${NC}"
    return 0
  else
    echo -e "${RED}❌ AGENT_RUNNERS fix failed - 'sage' agent is not in the list${NC}"
    return 1
  fi
}

# Function to test the POST /api/system/summary endpoint
test_post_system_summary() {
  echo -e "\n${BLUE}Testing POST /api/system/summary endpoint...${NC}"
  RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"project_id\":\"$PROJECT_ID\"}" http://localhost:8000/api/system/summary)
  echo -e "${BLUE}Response: ${RESPONSE}${NC}"
  
  # Check if response contains success status
  if echo $RESPONSE | grep -q "success"; then
    echo -e "${GREEN}✅ POST /api/system/summary endpoint works correctly${NC}"
    return 0
  else
    echo -e "${RED}❌ POST /api/system/summary endpoint failed${NC}"
    return 1
  fi
}

# Function to test the POST /api/system/summary endpoint with query parameter
test_post_system_summary_query() {
  echo -e "\n${BLUE}Testing POST /api/system/summary?project_id=${PROJECT_ID} endpoint...${NC}"
  RESPONSE=$(curl -s -X POST "http://localhost:8000/api/system/summary?project_id=${PROJECT_ID}")
  echo -e "${BLUE}Response: ${RESPONSE}${NC}"
  
  # Check if response contains success status
  if echo $RESPONSE | grep -q "success"; then
    echo -e "${GREEN}✅ POST /api/system/summary with query parameter works correctly${NC}"
    return 0
  else
    echo -e "${RED}❌ POST /api/system/summary with query parameter failed${NC}"
    return 1
  fi
}

# Function to test the GET /api/system/summary endpoint
test_get_system_summary() {
  echo -e "\n${BLUE}Testing GET /api/system/summary?project_id=${PROJECT_ID} endpoint...${NC}"
  RESPONSE=$(curl -s "http://localhost:8000/api/system/summary?project_id=${PROJECT_ID}")
  echo -e "${BLUE}Response: ${RESPONSE}${NC}"
  
  # Check if response contains success status
  if echo $RESPONSE | grep -q "success" || echo $RESPONSE | grep -q "summary"; then
    echo -e "${GREEN}✅ GET /api/system/summary endpoint works correctly${NC}"
    return 0
  else
    echo -e "${RED}❌ GET /api/system/summary endpoint failed${NC}"
    return 1
  fi
}

# Function to check server logs for route registration
check_server_logs() {
  echo -e "\n${BLUE}Checking server logs for route registration...${NC}"
  if grep -q "ROUTE LOADED:.*summary" server_output.log; then
    echo -e "${GREEN}✅ Summary routes are properly registered${NC}"
    grep "ROUTE LOADED:.*summary" server_output.log | sed "s/^/${GREEN}✅ /"
    echo -e "${NC}"
    return 0
  else
    echo -e "${RED}❌ No summary routes found in server logs${NC}"
    return 1
  fi
}

# Main test execution
echo -e "${BLUE}Starting tests...${NC}"

# Start the server
start_server

# Run tests if server started successfully
if [ $? -eq 0 ]; then
  # Check server logs for route registration
  check_server_logs
  
  # Test AGENT_RUNNERS fix
  test_agent_list
  AGENT_LIST_RESULT=$?
  
  # Test POST /api/system/summary endpoint
  test_post_system_summary
  POST_SUMMARY_RESULT=$?
  
  # Test POST /api/system/summary endpoint with query parameter
  test_post_system_summary_query
  POST_SUMMARY_QUERY_RESULT=$?
  
  # Test GET /api/system/summary endpoint
  test_get_system_summary
  GET_SUMMARY_RESULT=$?
  
  # Stop the server
  stop_server
  
  # Print test summary
  echo -e "\n${BLUE}===== Test Summary =====${NC}"
  if [ $AGENT_LIST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ AGENT_RUNNERS fix: PASSED${NC}"
  else
    echo -e "${RED}❌ AGENT_RUNNERS fix: FAILED${NC}"
  fi
  
  if [ $POST_SUMMARY_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ POST /api/system/summary endpoint: PASSED${NC}"
  else
    echo -e "${RED}❌ POST /api/system/summary endpoint: FAILED${NC}"
  fi
  
  if [ $POST_SUMMARY_QUERY_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ POST /api/system/summary with query parameter: PASSED${NC}"
  else
    echo -e "${RED}❌ POST /api/system/summary with query parameter: FAILED${NC}"
  fi
  
  if [ $GET_SUMMARY_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ GET /api/system/summary endpoint: PASSED${NC}"
  else
    echo -e "${RED}❌ GET /api/system/summary endpoint: FAILED${NC}"
  fi
  
  # Overall result
  if [ $AGENT_LIST_RESULT -eq 0 ] && [ $POST_SUMMARY_RESULT -eq 0 ] && [ $POST_SUMMARY_QUERY_RESULT -eq 0 ] && [ $GET_SUMMARY_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests PASSED${NC}"
    exit 0
  else
    echo -e "\n${RED}❌ Some tests FAILED${NC}"
    exit 1
  fi
else
  echo -e "${RED}❌ Cannot run tests because server failed to start${NC}"
  exit 1
fi
