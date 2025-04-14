"""
Test script for agent tone memory functionality.

This script tests the functionality of agent tone profiles in memory operations,
including writing memories with agent tone and reading memories with agent tone.
"""

import pytest
import json
import os
from app.modules.memory_writer import write_memory, memory_store, get_agent_tone_profile, _load_agent_manifest
from pathlib import Path

# Test agent IDs
TEST_AGENT_ID = "hal-agent"
NON_EXISTENT_AGENT_ID = "non-existent-agent"

def setup_module():
    """Set up test environment before running tests."""
    # Clear memory store
    memory_store.clear()
    
    # Ensure agent manifest is loaded
    _load_agent_manifest()

def test_get_agent_tone_profile():
    """Test retrieving agent tone profile from manifest."""
    # Test retrieving tone profile for existing agent
    tone_profile = get_agent_tone_profile(TEST_AGENT_ID)
    assert tone_profile is not None
    assert "style" in tone_profile
    assert "emotion" in tone_profile
    assert "vibe" in tone_profile
    assert "persona" in tone_profile
    
    # Test retrieving tone profile for non-existent agent
    tone_profile = get_agent_tone_profile(NON_EXISTENT_AGENT_ID)
    assert tone_profile is None

def test_write_memory_with_agent_tone():
    """Test writing memory with agent tone profile."""
    # Write memory for agent with tone profile
    memory = write_memory(
        agent_id=TEST_AGENT_ID,
        type="observation",
        content="This is a test observation with agent tone.",
        tags=["test", "agent_tone"]
    )
    
    # Verify memory has agent_tone field
    assert "agent_tone" in memory
    assert memory["agent_tone"]["style"] == "formal"
    assert memory["agent_tone"]["emotion"] == "neutral"
    assert memory["agent_tone"]["vibe"] == "guardian"
    
    # Write memory for non-existent agent
    memory = write_memory(
        agent_id=NON_EXISTENT_AGENT_ID,
        type="observation",
        content="This is a test observation without agent tone.",
        tags=["test", "no_agent_tone"]
    )
    
    # Verify memory does not have agent_tone field
    assert "agent_tone" not in memory

def test_memory_store_contains_agent_tone():
    """Test that memory store contains memories with agent tone."""
    # Filter memories for test agent
    test_agent_memories = [m for m in memory_store if m["agent_id"] == TEST_AGENT_ID]
    
    # Verify at least one memory exists
    assert len(test_agent_memories) > 0
    
    # Verify memory has agent_tone field
    assert "agent_tone" in test_agent_memories[0]
    assert test_agent_memories[0]["agent_tone"]["style"] == "formal"
    assert test_agent_memories[0]["agent_tone"]["emotion"] == "neutral"
    assert test_agent_memories[0]["agent_tone"]["vibe"] == "guardian"
    
    # Filter memories for non-existent agent
    non_existent_agent_memories = [m for m in memory_store if m["agent_id"] == NON_EXISTENT_AGENT_ID]
    
    # Verify at least one memory exists
    assert len(non_existent_agent_memories) > 0
    
    # Verify memory does not have agent_tone field
    assert "agent_tone" not in non_existent_agent_memories[0]

def test_different_agent_tone_profiles():
    """Test that different agents have different tone profiles."""
    # Write memories for different agents
    memory1 = write_memory(
        agent_id="hal-agent",
        type="observation",
        content="This is a test observation from HAL.",
        tags=["test", "hal"]
    )
    
    memory2 = write_memory(
        agent_id="lifetree-agent",
        type="observation",
        content="This is a test observation from Lifetree.",
        tags=["test", "lifetree"]
    )
    
    # Verify both memories have agent_tone field
    assert "agent_tone" in memory1
    assert "agent_tone" in memory2
    
    # Verify tone profiles are different
    assert memory1["agent_tone"]["style"] != memory2["agent_tone"]["style"]
    assert memory1["agent_tone"]["emotion"] != memory2["agent_tone"]["emotion"]
    assert memory1["agent_tone"]["vibe"] != memory2["agent_tone"]["vibe"]
    
    # Verify specific tone profiles
    assert memory1["agent_tone"]["style"] == "formal"
    assert memory1["agent_tone"]["vibe"] == "guardian"
    
    assert memory2["agent_tone"]["style"] == "conversational"
    assert memory2["agent_tone"]["emotion"] == "warm"
    assert memory2["agent_tone"]["vibe"] == "coach"

def test_agent_tone_in_shared_memory():
    """
    Test that agent tone is included in shared memory metadata.
    
    Note: This test is a placeholder and would need to be implemented
    with proper mocking of the shared memory layer.
    """
    # This would require mocking the shared memory layer
    # For now, we'll just note that the implementation includes
    # agent_tone in the metadata passed to shared_memory.store_memory()
    pass
