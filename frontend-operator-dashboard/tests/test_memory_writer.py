import pytest
import uuid
from datetime import datetime
from app.modules.memory_writer import write_memory, memory_store

@pytest.fixture(autouse=True)
def clear_memory_store():
    """Clear the memory store before each test."""
    memory_store.clear()
    yield

@pytest.mark.memory
def test_memory_format_validation():
    """Test that the memory format includes all required fields."""
    payload = {
        "agent_id": "test-agent",
        "type": "observation",
        "content": "This is a test observation",
        "tags": ["test", "observation"]
    }
    
    # Write the memory directly using the function
    memory = write_memory(
        agent_id=payload["agent_id"],
        type=payload["type"],
        content=payload["content"],
        tags=payload["tags"]
    )
    
    # Verify all required fields are present
    assert "memory_id" in memory
    assert "agent_id" in memory
    assert "type" in memory
    assert "content" in memory
    assert "tags" in memory
    assert "timestamp" in memory
    
    # Verify field values
    assert memory["agent_id"] == payload["agent_id"]
    assert memory["type"] == payload["type"]
    assert memory["content"] == payload["content"]
    assert memory["tags"] == payload["tags"]
    
    # Verify timestamp format (ISO format)
    assert "T" in memory["timestamp"]  # Simple check for ISO format with T separator

@pytest.mark.memory
def test_valid_memory_write():
    """Test that a valid memory write returns a memory with correct structure."""
    # Test data
    agent_id = "hal"
    memory_type = "reflection"
    content = "HAL resolved the delegate route bug."
    tags = ["bugfix", "delegate"]
    
    # Call the function directly
    memory = write_memory(agent_id, memory_type, content, tags)
    
    # Verify the result
    assert memory["memory_id"] is not None
    assert len(memory["memory_id"]) > 0
    assert memory["agent_id"] == agent_id
    assert memory["type"] == memory_type
    assert memory["content"] == content
    assert memory["tags"] == tags
    assert "timestamp" in memory

@pytest.mark.memory
def test_rapid_fire_write():
    """Test that multiple rapid memory writes all succeed with unique memory_ids."""
    memory_ids = set()
    
    for i in range(10):
        # Call the function directly
        memory = write_memory(
            agent_id=f"agent-{i}",
            type="thought",
            content=f"This is thought number {i}",
            tags=["test", f"thought-{i}"]
        )
        
        # Verify memory_id is unique
        memory_id = memory["memory_id"]
        assert memory_id not in memory_ids
        memory_ids.add(memory_id)
    
    # Verify we have 10 unique memory_ids
    assert len(memory_ids) == 10
    # Verify we have 10 items in the memory store
    assert len(memory_store) == 10

@pytest.mark.memory
def test_duplicate_memory_id_check():
    """Test that identical memory content still generates unique memory_ids."""
    # Write the same memory twice
    memory1 = write_memory(
        agent_id="hal",
        type="reflection",
        content="This is identical content",
        tags=["test", "duplicate"]
    )
    
    memory2 = write_memory(
        agent_id="hal",
        type="reflection",
        content="This is identical content",
        tags=["test", "duplicate"]
    )
    
    # Verify both have memory_ids
    assert "memory_id" in memory1
    assert "memory_id" in memory2
    
    # Verify memory_ids are different
    assert memory1["memory_id"] != memory2["memory_id"]

@pytest.mark.memory
def test_memory_store_persistence():
    """Test that memories are stored in the memory_store."""
    # Clear the memory store first
    memory_store.clear()
    
    # Write a memory
    memory = write_memory(
        agent_id="test-agent",
        type="observation",
        content="Testing memory store persistence",
        tags=["test", "persistence"]
    )
    
    # Verify the memory is in the memory_store
    assert len(memory_store) == 1
    assert memory_store[0]["memory_id"] == memory["memory_id"]
    assert memory_store[0]["agent_id"] == "test-agent"
    assert memory_store[0]["type"] == "observation"
    assert memory_store[0]["content"] == "Testing memory store persistence"
    assert memory_store[0]["tags"] == ["test", "persistence"]

@pytest.mark.memory
def test_uuid_generation():
    """Test that UUIDs are properly generated for each memory."""
    # Write a memory
    memory = write_memory(
        agent_id="test-agent",
        type="thought",
        content="Testing UUID generation",
        tags=["test", "uuid"]
    )
    
    # Verify the memory_id is a valid UUID
    try:
        uuid_obj = uuid.UUID(memory["memory_id"])
        assert str(uuid_obj) == memory["memory_id"]
    except ValueError:
        pytest.fail(f"memory_id {memory['memory_id']} is not a valid UUID")
