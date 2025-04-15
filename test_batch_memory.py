import json
import uuid
from datetime import datetime

# Test script for the orchestrator memory integration
# This script simulates a request to the /api/orchestrator/start-project endpoint
# and verifies that the batch memory writing functionality works as expected

from app.schemas.memory import StepType
from app.modules.memory_thread import thread_memory

async def test_batch_memory_writing():
    """Test the batch memory writing functionality"""
    print("🧪 Testing batch memory writing functionality...")
    
    # Generate test IDs
    project_id = f"test-project-{str(uuid.uuid4())[:8]}"
    chain_id = f"test-chain-{str(uuid.uuid4())[:8]}"
    
    # Create a direct request dictionary matching the expected structure
    request = {
        "project_id": project_id,
        "chain_id": chain_id,
        "agent_id": "orchestrator",
        "memories": [
            {
                "agent": "hal",
                "role": "agent",
                "content": "This is a test output from HAL",
                "step_type": StepType.plan
            },
            {
                "agent": "ash",
                "role": "agent",
                "content": "This is a test output from ASH",
                "step_type": StepType.docs
            },
            {
                "agent": "nova",
                "role": "agent",
                "content": "This is a test output from NOVA",
                "step_type": StepType.ui
            },
            {
                "agent": "critic",
                "role": "agent",
                "content": "This is a test output from CRITIC",
                "step_type": StepType.reflection
            }
        ]
    }
    
    # Call thread_memory with the request
    try:
        result = await thread_memory(request)
        print(f"✅ Successfully wrote batch memory: {result}")
        
        # Verify the result
        if result.get("status") == "added" and result.get("thread_length") == 4:
            print(f"✅ All 4 memories were successfully written")
            print(f"📝 Thread length: {result.get('thread_length')}")
            return True
        else:
            print(f"❌ Failed to write all memories: {result}")
            return False
    except Exception as e:
        print(f"❌ Error writing batch memory: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_batch_memory_writing())
