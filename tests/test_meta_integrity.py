import pytest
from app.memory import PROJECT_MEMORY

# Mock memory and utility functions for testing
@pytest.fixture
def mock_project_memory():
    """
    Create a mock project memory for testing the integrity tests themselves.
    """
    PROJECT_MEMORY.clear()
    
    # Create a test project with good health
    PROJECT_MEMORY["test_healthy"] = {
        "loop_count": 5,
        "last_snapshot": {"timestamp": "2025-04-20T12:00:00Z", "state": "healthy"},
        "reflection_scores": [
            {"timestamp": "2025-04-20T11:00:00Z", "score": 0.8, "summary": "Good reflection"}
        ],
        "orchestrator_decisions": [
            {"timestamp": "2025-04-20T11:30:00Z", "action": "run_agent", "reasoning": "Agent needed"}
        ],
        "system_health_score": 0.9,
        "drift_logs": [],
        "agent_executions": [
            {"agent": "orchestrator", "timestamp": "2025-04-20T11:00:00Z"},
            {"agent": "planner", "timestamp": "2025-04-20T11:05:00Z"}
        ],
        "loop_snapshots": [
            {"loop_count": 1, "timestamp": "2025-04-20T10:00:00Z"},
            {"loop_count": 2, "timestamp": "2025-04-20T10:30:00Z"},
            {"loop_count": 3, "timestamp": "2025-04-20T11:00:00Z"},
            {"loop_count": 4, "timestamp": "2025-04-20T11:30:00Z"},
            {"loop_count": 5, "timestamp": "2025-04-20T12:00:00Z"}
        ]
    }
    
    # Create a test project with issues
    PROJECT_MEMORY["test_unhealthy"] = {
        "loop_count": 5,
        "last_snapshot": {"timestamp": "2025-04-20T12:00:00Z", "state": "degraded"},
        "reflection_scores": [
            {"timestamp": "2025-04-20T11:00:00Z", "score": 0.4, "summary": "Poor reflection"}
        ],
        "orchestrator_decisions": [],
        "system_health_score": 0.3,
        "drift_logs": [
            {"timestamp": "2025-04-20T11:30:00Z", "type": "schema_drift", "severity": "critical"}
        ],
        "agent_executions": [
            {"agent": "planner", "timestamp": "2025-04-20T11:00:00Z"},
            {"agent": "orchestrator", "timestamp": "2025-04-20T11:05:00Z"}
        ],
        "loop_snapshots": [
            {"loop_count": 1, "timestamp": "2025-04-20T10:00:00Z"},
            {"loop_count": 3, "timestamp": "2025-04-20T10:30:00Z"},
            {"loop_count": 5, "timestamp": "2025-04-20T11:00:00Z"}
        ]
    }
    
    return PROJECT_MEMORY

def test_the_tests(mock_project_memory):
    """
    Meta-test to verify that our integrity tests correctly identify issues.
    """
    from tests.test_system_integrity import (
        test_reflection_confidence,
        test_system_health_score,
        test_drift_logs_status,
        test_loop_snapshot_consistency
    )
    
    # Test with healthy project - should pass
    PROJECT_MEMORY.clear()
    PROJECT_MEMORY["test_project"] = mock_project_memory["test_healthy"]
    
    # These should not raise exceptions
    test_reflection_confidence()
    test_system_health_score()
    test_drift_logs_status()
    
    # Test with unhealthy project - should fail
    PROJECT_MEMORY.clear()
    PROJECT_MEMORY["test_project"] = mock_project_memory["test_unhealthy"]
    
    # These should raise exceptions
    with pytest.raises(AssertionError):
        test_reflection_confidence()
    
    with pytest.raises(AssertionError):
        test_system_health_score()
    
    with pytest.raises(AssertionError):
        test_drift_logs_status()
    
    with pytest.raises(AssertionError):
        test_loop_snapshot_consistency()
