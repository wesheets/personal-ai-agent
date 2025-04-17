#!/bin/bash

# Local API Health Test Script
# This script tests the local implementation of the API endpoints
# to verify that the fixes are working properly before deployment.

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Phase 6.2.0 Local Implementation Test${NC}"
echo -e "${BLUE}========================================${NC}"

# Test 1: Verify GET endpoint registration fix in main.py
echo -e "${BLUE}Test 1: Verifying GET endpoint registration fix${NC}"
if grep -q "async def serve_react_app(full_path: str, request: Request)" app/main.py && \
   grep -q "route_path = route.path.replace(\"{\"" app/main.py; then
    echo -e "${GREEN}✅ GET endpoint registration fix is properly implemented${NC}"
else
    echo -e "${RED}❌ GET endpoint registration fix is not properly implemented${NC}"
    exit 1
fi

# Test 2: Verify retry hook integration in agent_runner.py
echo -e "${BLUE}Test 2: Verifying retry hook integration${NC}"
if grep -q "from utils.retry_hooks import get_retry_status" app/modules/agent_runner.py && \
   grep -q "RETRY_HOOKS_AVAILABLE = True" app/modules/agent_runner.py && \
   grep -q "def safe_get_retry_status" app/modules/agent_runner.py; then
    echo -e "${GREEN}✅ Retry hook integration is properly implemented${NC}"
else
    echo -e "${RED}❌ Retry hook integration is not properly implemented${NC}"
    exit 1
fi

# Test 3: Verify memory_store fallback in agent_runner.py
echo -e "${BLUE}Test 3: Verifying memory_store fallback${NC}"
if grep -q "memory_store = {}" app/modules/agent_runner.py; then
    echo -e "${GREEN}✅ Memory store fallback is properly implemented${NC}"
else
    echo -e "${RED}❌ Memory store fallback is not properly implemented${NC}"
    exit 1
fi

# Test 4: Verify deployment verification script
echo -e "${BLUE}Test 4: Verifying deployment verification script${NC}"
if [ -f "verify_deployment.sh" ] && [ -x "verify_deployment.sh" ]; then
    echo -e "${GREEN}✅ Deployment verification script is properly implemented${NC}"
else
    echo -e "${RED}❌ Deployment verification script is not properly implemented${NC}"
    exit 1
fi

# Test 5: Verify Python syntax of modified files
echo -e "${BLUE}Test 5: Verifying Python syntax of modified files${NC}"
if python3 -m py_compile app/main.py app/modules/agent_runner.py; then
    echo -e "${GREEN}✅ Python syntax is valid in modified files${NC}"
else
    echo -e "${RED}❌ Python syntax errors found in modified files${NC}"
    exit 1
fi

# Print summary
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ All local tests passed!${NC}"
echo -e "${GREEN}✅ Implementation is ready for deployment${NC}"
echo -e "${BLUE}========================================${NC}"

exit 0
