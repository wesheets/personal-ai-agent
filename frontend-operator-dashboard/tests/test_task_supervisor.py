"""
Test file for the task_supervisor module.

This module contains tests for the task_supervisor.py module, which provides
centralized monitoring for all agent activities, preventing runaway execution,
detecting agents exceeding system caps, logging structured audit events, and
enforcing emergency halts.
"""

import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# Import the task_supervisor module
from app.modules.task_supervisor import (
    monitor_loop,
    monitor_delegation,
    monitor_reflection,
    halt_task,
    log_supervision_event,
    get_supervision_status,
    system_caps
)

# Create a temporary log file for testing
@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    fd, path = tempfile.mkstemp()
    yield path
    os.close(fd)
    os.unlink(path)

# Test monitor_loop function
def test_monitor_loop_within_limits():
    """Test that monitor_loop allows tasks within loop limits."""
    # Test with loop count below the limit
    result = monitor_loop("test-task-1", 1)
    assert result["status"] == "ok"
    assert result["reason"] == "within_limits"
    assert result["event"]["risk_level"] == "low"

    # Test with loop count at the limit
    result = monitor_loop("test-task-2", system_caps["max_loops_per_task"])
    assert result["status"] == "ok"
    assert result["reason"] == "within_limits"
    assert result["event"]["risk_level"] == "medium"

def test_monitor_loop_exceeds_limits():
    """Test that monitor_loop halts tasks exceeding loop limits."""
    # Test with loop count above the limit
    result = monitor_loop("test-task-3", system_caps["max_loops_per_task"] + 1)
    assert result["status"] == "halted"
    assert result["reason"] == "loop_exceeded"
    assert result["event"]["risk_level"] == "high"
    assert result["event"]["event_type"] == "loop_exceeded"

# Test monitor_delegation function
def test_monitor_delegation_within_limits():
    """Test that monitor_delegation allows tasks within delegation limits."""
    # Test with delegation depth below the limit
    result = monitor_delegation("test-agent-1", 1)
    assert result["status"] == "ok"
    assert result["reason"] == "within_limits"
    assert result["event"]["risk_level"] == "low"

    # Test with delegation depth at the limit
    result = monitor_delegation("test-agent-2", system_caps["max_delegation_depth"])
    assert result["status"] == "ok"
    assert result["reason"] == "within_limits"
    assert result["event"]["risk_level"] == "medium"

def test_monitor_delegation_exceeds_limits():
    """Test that monitor_delegation halts tasks exceeding delegation limits."""
    # Test with delegation depth above the limit
    result = monitor_delegation("test-agent-3", system_caps["max_delegation_depth"] + 1)
    assert result["status"] == "halted"
    assert result["reason"] == "delegation_depth_exceeded"
    assert result["event"]["risk_level"] == "high"
    assert result["event"]["event_type"] == "delegation_depth_exceeded"

# Test monitor_reflection function
def test_monitor_reflection_within_limits():
    """Test that monitor_reflection allows tasks within reflection limits."""
    # Test with reflection count below the limit
    result = monitor_reflection("test-agent-1", 1)
    assert result["status"] == "ok"
    assert result["reason"] == "within_limits"
    assert result["event"]["risk_level"] == "low"

    # Test with reflection count at the limit
    result = monitor_reflection("test-agent-2", system_caps["max_loops_per_task"])
    assert result["status"] == "ok"
    assert result["reason"] == "within_limits"
    assert result["event"]["risk_level"] == "medium"

def test_monitor_reflection_exceeds_limits():
    """Test that monitor_reflection warns about tasks exceeding reflection limits."""
    # Test with reflection count above the limit
    result = monitor_reflection("test-agent-3", system_caps["max_loops_per_task"] + 1)
    assert result["status"] == "warned"
    assert result["reason"] == "reflection_recursion"
    assert result["event"]["risk_level"] == "high"
    assert result["event"]["event_type"] == "reflection_recursion"

# Test halt_task function
def test_halt_task():
    """Test that halt_task properly halts a task."""
    result = halt_task("test-task-4", "test_reason")
    assert result["status"] == "halted"
    assert result["task_id_or_agent"] == "test-task-4"
    assert result["reason"] == "test_reason"
    assert "timestamp" in result
    assert "halt_id" in result

# Test log_supervision_event function
def test_log_supervision_event(temp_log_file):
    """Test that log_supervision_event properly logs events."""
    # Patch the TASK_LOG_FILE path
    with patch('app.modules.task_supervisor.TASK_LOG_FILE', temp_log_file):
        # Create a test event
        event = {
            "event_type": "test_event",
            "risk_level": "medium",
            "reason": "Test event for unit testing"
        }
        
        # Log the event
        log_supervision_event(event)
        
        # Read the log file
        with open(temp_log_file, 'r') as f:
            log_content = f.read()
        
        # Check that the event was logged
        assert "test_event" in log_content
        assert "medium" in log_content
        assert "Test event for unit testing" in log_content

# Test lockdown mode
def test_lockdown_mode():
    """Test that lockdown mode halts all activities."""
    # Patch the lockdown_mode variable
    with patch('app.modules.task_supervisor.lockdown_mode', True):
        # Test monitor_loop
        result = monitor_loop("test-task-5", 1)
        assert result["status"] == "halted"
        assert result["reason"] == "lockdown_mode_active"
        assert result["event"]["event_type"] == "lockdown_enforced"
        
        # Test monitor_delegation
        result = monitor_delegation("test-agent-5", 1)
        assert result["status"] == "halted"
        assert result["reason"] == "lockdown_mode_active"
        assert result["event"]["event_type"] == "lockdown_enforced"
        
        # Test monitor_reflection
        result = monitor_reflection("test-agent-5", 1)
        assert result["status"] == "halted"
        assert result["reason"] == "lockdown_mode_active"
        assert result["event"]["event_type"] == "lockdown_enforced"

# Test get_supervision_status function
def test_get_supervision_status(temp_log_file):
    """Test that get_supervision_status returns the correct status."""
    # Patch the TASK_LOG_FILE path
    with patch('app.modules.task_supervisor.TASK_LOG_FILE', temp_log_file):
        # Create some test events
        events = [
            {"event_type": "loop_exceeded", "risk_level": "high"},
            {"event_type": "delegation_depth_exceeded", "risk_level": "high"},
            {"event_type": "reflection_recursion", "risk_level": "high"}
        ]
        
        # Write events to the log file
        with open(temp_log_file, 'w') as f:
            for event in events:
                f.write(json.dumps(event) + "\n")
        
        # Get the supervision status
        status = get_supervision_status()
        
        # Check the status
        assert status["status"] == "active"
        assert status["event_counts"]["total"] == 3
        assert status["event_counts"]["loop_exceeded"] == 1
        assert status["event_counts"]["delegation_depth_exceeded"] == 1
        assert status["event_counts"]["reflection_recursion"] == 1
        assert "system_caps" in status
        assert "timestamp" in status

# Test integration with memory_writer
def test_integration_with_memory_writer():
    """Test integration with memory_writer module."""
    # Mock the write_memory function
    with patch('app.modules.task_supervisor.write_memory') as mock_write_memory:
        # Set up the mock
        mock_memory = {"memory_id": "test-memory-id"}
        mock_write_memory.return_value = mock_memory
        
        # Call halt_task
        result = halt_task("test-task-6", "test_reason")
        
        # Check that write_memory was called
        mock_write_memory.assert_called_once()
        
        # Check that the memory_id was added to the result
        assert "memory_id" in mock_write_memory.call_args[1]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
