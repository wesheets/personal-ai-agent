import pytest
from datetime import datetime, timedelta
from app.memory import PROJECT_MEMORY, initialize_project_memory, add_reflection_score, log_schema_drift, snapshot_loop
from app.agents.cto_agent import run_cto_agent, analyze_system_trends

# Mock project memory for testing
@pytest.fixture
def mock_project_memory():
    PROJECT_MEMORY.clear()
    initialize_project_memory("test_project")
    
    # Add some reflection scores
    add_reflection_score("test_project", 0.8, "Good reflection")
    add_reflection_score("test_project", 0.7, "Decent reflection")
    add_reflection_score("test_project", 0.6, "Average reflection")
    add_reflection_score("test_project", 0.5, "Mediocre reflection")
    add_reflection_score("test_project", 0.4, "Poor reflection")
    
    # Add some drift logs
    log_schema_drift("test_project", "missing_field", {"field": "confidence", "object": "reflection"})
    log_schema_drift("test_project", "type_mismatch", {"field": "loop_count", "expected": "integer", "found": "string"})
    log_schema_drift("test_project", "unknown_field", {"field": "unknown_field", "object": "memory"})
    log_schema_drift("test_project", "missing_field", {"field": "summary", "object": "reflection"})
    
    # Add some loop snapshots
    PROJECT_MEMORY["test_project"]["loop_count"] = 1
    PROJECT_MEMORY["test_project"]["completed_steps"] = ["step1", "step2"]
    PROJECT_MEMORY["test_project"]["planned_steps"] = ["step1", "step2", "step3"]
    snapshot_loop("test_project")
    
    PROJECT_MEMORY["test_project"]["loop_count"] = 2
    PROJECT_MEMORY["test_project"]["completed_steps"] = ["step1"]
    PROJECT_MEMORY["test_project"]["planned_steps"] = ["step1", "step2", "step3"]
    snapshot_loop("test_project")
    
    PROJECT_MEMORY["test_project"]["loop_count"] = 3
    PROJECT_MEMORY["test_project"]["completed_steps"] = ["step1", "step2"]
    PROJECT_MEMORY["test_project"]["planned_steps"] = ["step1", "step2", "step3"]
    snapshot_loop("test_project")
    
    PROJECT_MEMORY["test_project"]["loop_count"] = 4
    PROJECT_MEMORY["test_project"]["completed_steps"] = ["step1"]
    PROJECT_MEMORY["test_project"]["planned_steps"] = ["step1", "step2", "step3"]
    snapshot_loop("test_project")
    
    PROJECT_MEMORY["test_project"]["loop_count"] = 5
    PROJECT_MEMORY["test_project"]["completed_steps"] = ["step1"]
    PROJECT_MEMORY["test_project"]["planned_steps"] = ["step1", "step2", "step3"]
    snapshot_loop("test_project")
    
    return PROJECT_MEMORY

def test_analyze_system_trends(mock_project_memory):
    # Run the system trends analysis
    result = analyze_system_trends("test_project")
    
    # Check that the result has the expected structure
    assert "timestamp" in result
    assert "project_id" in result
    assert "system_health_score" in result
    assert "issues" in result
    assert "loop_count" in result
    
    # Check that the system health score is calculated correctly
    # With declining reflection quality and frequent agent skips, score should be reduced
    assert result["system_health_score"] < 1.0
    
    # Check that the issues list contains the expected issues
    assert "Reflection quality declining" in result["issues"]
    assert "Schema drift frequent" in result["issues"]
    assert "Agents being skipped frequently" in result["issues"]
    
    # Check that the result was added to cto_audit_history
    assert "cto_audit_history" in mock_project_memory["test_project"]
    assert len(mock_project_memory["test_project"]["cto_audit_history"]) == 1
    
    # Check that the system_health_score was updated in project memory
    assert "system_health_score" in mock_project_memory["test_project"]
    assert mock_project_memory["test_project"]["system_health_score"] == result["system_health_score"]
    
    # Check that a warning was added to cto_warnings (since health score is low)
    assert "cto_warnings" in mock_project_memory["test_project"]
    assert len(mock_project_memory["test_project"]["cto_warnings"]) == 1
    assert mock_project_memory["test_project"]["cto_warnings"][0]["warning"] == "System trending unhealthy"

def test_run_cto_agent_with_trends(mock_project_memory):
    # Run the CTO agent
    result = run_cto_agent("test_project")
    
    # Check that the single-loop audit was performed
    assert "loop" in result
    assert "timestamp" in result
    assert "issues_found" in result
    assert "issues" in result
    assert "summary" in result
    
    # Check that the result was added to cto_reflections
    assert "cto_reflections" in mock_project_memory["test_project"]
    assert len(mock_project_memory["test_project"]["cto_reflections"]) == 1
    
    # Check that the system trends analysis was also performed
    assert "cto_audit_history" in mock_project_memory["test_project"]
    assert len(mock_project_memory["test_project"]["cto_audit_history"]) == 1
    
    # Run the CTO agent again to test multiple runs
    result = run_cto_agent("test_project")
    
    # Check that another reflection was added
    assert len(mock_project_memory["test_project"]["cto_reflections"]) == 2
    
    # Check that another audit history entry was added
    assert len(mock_project_memory["test_project"]["cto_audit_history"]) == 2

def test_memory_helper_functions():
    PROJECT_MEMORY.clear()
    
    # Test initialize_project_memory
    memory = initialize_project_memory("new_project")
    assert "loop_count" in memory
    assert "cto_reflections" in memory
    assert "system_flags" in memory
    assert "reflection_scores" in memory
    assert "drift_logs" in memory
    assert "loop_snapshots" in memory
    assert "cto_audit_history" in memory
    assert "cto_warnings" in memory
    assert "system_health_score" in memory
    
    # Test add_reflection_score
    score = add_reflection_score("new_project", 0.9, "Excellent reflection")
    assert "timestamp" in score
    assert score["score"] == 0.9
    assert score["summary"] == "Excellent reflection"
    assert len(PROJECT_MEMORY["new_project"]["reflection_scores"]) == 1
    
    # Test log_schema_drift
    drift = log_schema_drift("new_project", "missing_field", {"field": "test"})
    assert "timestamp" in drift
    assert drift["type"] == "missing_field"
    assert drift["details"]["field"] == "test"
    assert len(PROJECT_MEMORY["new_project"]["drift_logs"]) == 1
    
    # Test snapshot_loop
    PROJECT_MEMORY["new_project"]["loop_count"] = 1
    PROJECT_MEMORY["new_project"]["completed_steps"] = ["step1"]
    snapshot = snapshot_loop("new_project")
    assert "timestamp" in snapshot
    assert snapshot["loop_count"] == 1
    assert snapshot["snapshot"]["completed_steps"] == ["step1"]
    assert len(PROJECT_MEMORY["new_project"]["loop_snapshots"]) == 1
