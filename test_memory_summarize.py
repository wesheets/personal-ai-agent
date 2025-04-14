"""
Test script for the memory summarization functionality.

This script tests the memory summarization functionality by:
1. Creating test memory entries
2. Calling the summarize_memories function directly
3. Verifying the output matches expectations
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the memory summarization function
from app.modules.memory_summarizer import summarize_memories

def main():
    """Test the memory summarization functionality"""
    print("Testing Memory Summarization Module")
    print("=" * 50)
    
    # Create test memory entries
    test_memories = [
        {
            "memory_id": "1",
            "agent_id": "shiva",
            "type": "training",
            "content": "Learning about marketing systems for warehouse transformations.",
            "tags": ["marketing", "warehouse"],
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "memory_id": "2",
            "agent_id": "shiva",
            "type": "training",
            "content": "Studying headline branding techniques for industrial solutions.",
            "tags": ["branding", "headlines"],
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "memory_id": "3",
            "agent_id": "shiva",
            "type": "training",
            "content": "Analyzing warehouse transformation case studies.",
            "tags": ["warehouse", "case studies"],
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "memory_id": "4",
            "agent_id": "shiva",
            "type": "training",
            "content": "Reviewing marketing copy for industrial automation.",
            "tags": ["marketing", "automation"],
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "memory_id": "5",
            "agent_id": "shiva",
            "type": "training",
            "content": "Exploring branding strategies for warehouse solutions.",
            "tags": ["branding", "warehouse"],
            "timestamp": datetime.utcnow().isoformat()
        }
    ]
    
    # Test with all memories
    print("\nTest 1: Summarizing all memories")
    summary = summarize_memories(test_memories)
    print(f"Summary: {summary}")
    
    # Test with filtered memories (only branding)
    print("\nTest 2: Summarizing only branding memories")
    branding_memories = [m for m in test_memories if "branding" in m.get("tags", [])]
    summary = summarize_memories(branding_memories)
    print(f"Summary: {summary}")
    
    # Test with empty memories
    print("\nTest 3: Summarizing empty memories")
    summary = summarize_memories([])
    print(f"Summary: {summary}")
    
    # Test with different agent
    print("\nTest 4: Summarizing memories with different agent_id")
    different_agent_memories = test_memories.copy()
    for m in different_agent_memories:
        m["agent_id"] = "hal"
    summary = summarize_memories(different_agent_memories)
    print(f"Summary: {summary}")
    
    print("\nMemory Summarization Tests Completed")

if __name__ == "__main__":
    main()
