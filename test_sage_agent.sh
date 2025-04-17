#!/bin/bash

# Test script for SAGE Meta-Summary Agent and System Summary Endpoints
# This script tests the functionality of the SAGE agent and system summary endpoints

echo "🧪 Starting SAGE Meta-Summary Agent Test Script"
echo "================================================"

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Define test project ID
PROJECT_ID="test_project_$(date +%s)"
echo -e "${BLUE}Using test project ID: ${PROJECT_ID}${NC}"

# Create some test data for the project
echo -e "\n${YELLOW}Step 1: Creating test data for the project${NC}"

# Create project state
echo "Creating project state..."
mkdir -p app/modules/project_states
cat > app/modules/project_states/${PROJECT_ID}.json << EOF
{
  "project_id": "${PROJECT_ID}",
  "status": "in_progress",
  "files_created": [
    "README.md",
    "main.py",
    "utils.py"
  ],
  "agents_involved": [
    "hal",
    "nova",
    "critic"
  ],
  "latest_agent_action": {
    "agent": "critic",
    "action": "reviewed code quality",
    "timestamp": "$(date -Iseconds)"
  },
  "next_recommended_step": "Implement additional features",
  "tool_usage": {
    "file_writer": 5,
    "memory_writer": 3,
    "code_analyzer": 2
  },
  "timestamp": "$(date -Iseconds)"
}
EOF

# Create memory thread entries
echo "Creating memory thread entries..."
mkdir -p memory/summaries

# Create memory thread database if it doesn't exist
if [ ! -f app/modules/memory_thread.py ]; then
  mkdir -p app/modules
  cat > app/modules/memory_thread.py << EOF
"""
Memory Thread Module (Mock for testing)
"""
import json
import datetime
from typing import Dict, List, Any

# In-memory database to store memory threads
THREAD_DB = {}

def get_current_timestamp():
    return datetime.datetime.now().isoformat() + "Z"
EOF
fi

# Add test memory entries to the THREAD_DB
cat > test_memory_setup.py << EOF
import sys
import os
import json
import datetime

# Add the current directory to the path so we can import the modules
sys.path.append(os.getcwd())

try:
    # Try to import the memory_thread module
    from app.modules.memory_thread import THREAD_DB
    
    # Create thread key
    thread_key = "${PROJECT_ID}::main"
    
    # Initialize thread if it doesn't exist
    if thread_key not in THREAD_DB:
        THREAD_DB[thread_key] = []
    
    # Add test memory entries
    THREAD_DB[thread_key].extend([
        {
            "memory_id": "mem-1",
            "agent": "hal",
            "role": "assistant",
            "content": "Created initial project structure",
            "step_type": "thinking",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
            "project_id": "${PROJECT_ID}",
            "chain_id": "main"
        },
        {
            "memory_id": "mem-2",
            "agent": "hal",
            "role": "assistant",
            "content": "Implemented core functionality in main.py",
            "step_type": "action",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat(),
            "project_id": "${PROJECT_ID}",
            "chain_id": "main"
        },
        {
            "memory_id": "mem-3",
            "agent": "nova",
            "role": "assistant",
            "content": "Added utility functions in utils.py",
            "step_type": "action",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=30)).isoformat(),
            "project_id": "${PROJECT_ID}",
            "chain_id": "main"
        },
        {
            "memory_id": "mem-4",
            "agent": "critic",
            "role": "assistant",
            "content": "Reviewed code quality and suggested improvements",
            "step_type": "thinking",
            "timestamp": datetime.datetime.now().isoformat(),
            "project_id": "${PROJECT_ID}",
            "chain_id": "main"
        }
    ])
    
    print(f"Added {len(THREAD_DB[thread_key])} memory entries to thread {thread_key}")
    
except Exception as e:
    print(f"Error setting up test memory: {str(e)}")
EOF

# Run the test memory setup script
echo "Running test memory setup script..."
python3 test_memory_setup.py

echo -e "\n${YELLOW}Step 2: Testing SAGE agent directly${NC}"
# Create a test script to run the SAGE agent directly
cat > test_sage_agent.py << EOF
import sys
import os
import json

# Add the current directory to the path so we can import the modules
sys.path.append(os.getcwd())

try:
    # Try to import the SAGE agent
    from agents.sage_agent import run_sage_agent
    
    # Run the SAGE agent
    result = run_sage_agent("${PROJECT_ID}", tools=["memory_writer"])
    
    # Print the result
    print(json.dumps(result, indent=2))
    
except Exception as e:
    print(f"Error running SAGE agent: {str(e)}")
EOF

# Run the test script
echo "Running SAGE agent test script..."
python3 test_sage_agent.py

echo -e "\n${YELLOW}Step 3: Testing GET /system/summary endpoint${NC}"
# Test the GET endpoint using curl
echo "Testing GET /system/summary endpoint..."
curl -s -X GET "http://localhost:8000/api/system/summary?project_id=${PROJECT_ID}" | python3 -m json.tool

echo -e "\n${YELLOW}Step 4: Testing POST /system/summary endpoint (auto-summary trigger)${NC}"
# Test the POST endpoint using curl
echo "Testing POST /system/summary endpoint..."
curl -s -X POST "http://localhost:8000/api/system/summary?project_id=${PROJECT_ID}" | python3 -m json.tool

echo -e "\n${YELLOW}Step 5: Verifying system summary memory storage${NC}"
# Create a test script to check if the summary was stored in memory
cat > test_summary_storage.py << EOF
import sys
import os
import json

# Add the current directory to the path so we can import the modules
sys.path.append(os.getcwd())

try:
    # Try to import the system_summary module
    from memory.system_summary import get_all_summaries
    
    # Get all summaries for the project
    summaries = get_all_summaries("${PROJECT_ID}")
    
    # Print the summaries
    print(f"Found {len(summaries)} summaries for project ${PROJECT_ID}")
    for i, summary in enumerate(summaries):
        print(f"\nSummary {i+1}:")
        print(f"ID: {summary.get('summary_id', 'unknown')}")
        print(f"Timestamp: {summary.get('timestamp', 'unknown')}")
        print(f"Content: {summary.get('content', 'unknown')}")
    
except Exception as e:
    print(f"Error checking summary storage: {str(e)}")
EOF

# Run the test script
echo "Running summary storage test script..."
python3 test_summary_storage.py

echo -e "\n${GREEN}✅ SAGE Meta-Summary Agent Test Complete${NC}"
echo "================================================"
