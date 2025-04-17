import pytest
import json
from fastapi.testclient import TestClient
from memory.system_log import log_event, get_system_log, clear_system_log
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_logs():
    """Clear logs before each test"""
    clear_system_log()
    yield

def test_log_event_function():
    """Test the log_event function directly"""
    # Log a test event
    event = log_event("HAL", "Test event", "test-project", {"test_key": "test_value"})
    
    # Verify event structure
    assert event["agent"] == "HAL"
    assert event["event"] == "Test event"
    assert event["project_id"] == "test-project"
    assert event["metadata"]["test_key"] == "test_value"
    assert "timestamp" in event
    assert "formatted_time" in event
    
    # Verify it was added to the log
    logs = get_system_log()
    assert len(logs) == 1
    assert logs[0]["agent"] == "HAL"

def test_get_system_log_function():
    """Test the get_system_log function directly"""
    # Add multiple events
    log_event("HAL", "Event 1", "project-1")
    log_event("NOVA", "Event 2", "project-1")
    log_event("CRITIC", "Event 3", "project-2")
    
    # Test filtering by project
    project1_logs = get_system_log(project_id="project-1")
    assert len(project1_logs) == 2
    
    # Test filtering by agent
    hal_logs = get_system_log(agent_filter="HAL")
    assert len(hal_logs) == 1
    assert hal_logs[0]["agent"] == "HAL"
    
    # Test limit
    limited_logs = get_system_log(limit=1)
    assert len(limited_logs) == 1

def test_get_logs_endpoint():
    """Test the GET /api/system/log endpoint"""
    # Add test logs
    log_event("HAL", "API Test Event", "api-test")
    
    # Test API endpoint
    response = client.get("/api/system/log")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["logs"]) >= 1
    
    # Test with project_id filter
    response = client.get("/api/system/log?project_id=api-test")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["logs"]) == 1
    assert data["logs"][0]["agent"] == "HAL"
    assert data["logs"][0]["event"] == "API Test Event"

def test_add_log_endpoint():
    """Test the POST /api/system/log endpoint"""
    # Test adding a log via API
    response = client.post(
        "/api/system/log?agent_name=NOVA&event=API+Created+Event&project_id=api-post-test"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify it was added
    logs = get_system_log(project_id="api-post-test")
    assert len(logs) == 1
    assert logs[0]["agent"] == "NOVA"
    assert logs[0]["event"] == "API Created Event"

def test_clear_logs_endpoint():
    """Test the DELETE /api/system/log endpoint"""
    # Add some logs
    log_event("ASH", "Clear Test", "clear-test")
    
    # Verify logs exist
    assert len(get_system_log(project_id="clear-test")) == 1
    
    # Clear logs via API
    response = client.delete("/api/system/log")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify logs were cleared
    assert len(get_system_log()) == 0

def test_agent_hooks_integration():
    """
    Test that agent hooks correctly log events
    Note: This is a simplified test that doesn't actually run the agents
    """
    # Simulate what would happen in the agent runner
    log_event("HAL", "Starting execution", "hook-test")
    log_event("HAL", "Completed task", "hook-test")
    log_event("NOVA", "Starting execution", "hook-test")
    log_event("NOVA", "Blocked: waiting for HAL", "hook-test", {"blocked_by": "HAL"})
    
    # Get logs for the test project
    logs = get_system_log(project_id="hook-test")
    
    # Verify correct number of logs
    assert len(logs) == 4
    
    # Verify agent names are present
    agents = [log["agent"] for log in logs]
    assert "HAL" in agents
    assert "NOVA" in agents
    
    # Verify blocked status is logged with metadata
    blocked_logs = [log for log in logs if "Blocked" in log["event"]]
    assert len(blocked_logs) == 1
    assert blocked_logs[0]["metadata"]["blocked_by"] == "HAL"
