import json
import uuid
from datetime import datetime

# Test script for verifying memory thread storage and summarization
# This script tests both the thread storage and the memory summarization functionality

from app.schemas.memory import StepType
from app.modules.memory_thread import thread_memory, get_memory_thread, clear_all_threads

async def test_memory_thread_storage_and_summarization():
    """Test memory thread storage and summarization"""
    print("🧪 Testing memory thread storage and summarization...")
    
    # Clear all threads to start with a clean state
    clear_all_threads()
    
    # Generate test IDs
    project_id = f"test-project-{str(uuid.uuid4())[:8]}"
    chain_id = f"test-chain-{str(uuid.uuid4())[:8]}"
    
    # Step 1: Create a sample ThreadRequest and store memories
    print("\n📝 Step 1: Storing batch memories...")
    request = {
        "project_id": project_id,
        "chain_id": chain_id,
        "agent_id": "orchestrator",
        "memories": [
            {
                "agent": "hal",
                "role": "agent",
                "content": "This is a test output from HAL with planning information",
                "step_type": StepType.plan
            },
            {
                "agent": "ash",
                "role": "agent",
                "content": "This is a test output from ASH with documentation",
                "step_type": StepType.docs
            },
            {
                "agent": "nova",
                "role": "agent",
                "content": "This is a test output from NOVA with UI design",
                "step_type": StepType.ui
            },
            {
                "agent": "critic",
                "role": "agent",
                "content": "This is a test output from CRITIC with reflection",
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
            print(f"📝 Memory IDs: {result.get('memory_ids')}")
        else:
            print(f"❌ Failed to write all memories: {result}")
            return False
    except Exception as e:
        print(f"❌ Error writing batch memory: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False
    
    # Step 2: Retrieve the memory thread
    print("\n📝 Step 2: Retrieving memory thread...")
    try:
        thread = await get_memory_thread(project_id, chain_id)
        
        # Verify the thread
        if len(thread) == 4:
            print(f"✅ Successfully retrieved memory thread with {len(thread)} entries")
            
            # Print thread contents
            for i, entry in enumerate(thread):
                print(f"  Memory {i+1}: Agent={entry.get('agent')}, Type={entry.get('step_type')}")
        else:
            print(f"❌ Failed to retrieve all memories: {thread}")
            return False
    except Exception as e:
        print(f"❌ Error retrieving memory thread: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False
    
    # Step 3: Test memory summarization
    print("\n📝 Step 3: Testing memory summarization...")
    try:
        # Import memory_summarize module
        from app.modules.memory_summarize import summarize_memory_thread
        from app.schemas.memory import SummarizationRequest
        
        # Test with explicit agent_id
        print("  Testing with explicit agent_id='hal'...")
        summary_request = SummarizationRequest(
            project_id=project_id,
            chain_id=chain_id,
            agent_id="hal"
        )
        
        hal_summary = await summarize_memory_thread(summary_request)
        print(f"  ✅ HAL summary: {hal_summary.get('summary')}")
        
        # Test with fallback agent_id
        print("  Testing with fallback agent_id (omitted)...")
        fallback_request = SummarizationRequest(
            project_id=project_id,
            chain_id=chain_id
        )
        
        fallback_summary = await summarize_memory_thread(fallback_request)
        print(f"  ✅ Fallback summary: {fallback_summary.get('summary')}")
        
        # Verify that agent_id defaults to "orchestrator" if missing
        if fallback_summary.get("agent_id") == "orchestrator":
            print("  ✅ agent_id correctly defaulted to 'orchestrator'")
        else:
            print(f"  ❌ agent_id did not default correctly: {fallback_summary.get('agent_id')}")
            
        return True
    except Exception as e:
        print(f"❌ Error testing memory summarization: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_memory_thread_storage_and_summarization())
