from app.memory import PROJECT_MEMORY
from app.agents.cto_agent import run_cto_agent
from app.utils.reflection_analyzer import ReflectionAnalyzer
from app.utils.system_flag_manager import SystemFlagManager
import pytest
import json
from datetime import datetime

# Mock project memory for testing
@pytest.fixture
def mock_project_memory():
    PROJECT_MEMORY.clear()
    PROJECT_MEMORY["test_project"] = {
        "loop_count": 3,
        "last_reflection": {
            "confidence": 0.8,
            "summary": "This is a test reflection summary"
        },
        "completed_steps": ["step1", "step2", "step3"],
        "planned_steps": ["step1", "step2", "step3", "step4"],
        "reflections_history": [
            {"summary": "Reflection 1"},
            {"summary": "Reflection 2"},
            {"summary": "Reflection 3"}
        ],
        "tool_history": [
            {"tool_name": "tool1", "success": True},
            {"tool_name": "tool2", "success": False},
            {"tool_name": "tool2", "success": False},
            {"tool_name": "tool2", "success": False}
        ]
    }
    return PROJECT_MEMORY

def test_cto_agent_run(mock_project_memory):
    # Run the CTO agent
    result = run_cto_agent("test_project")
    
    # Check that the result has the expected structure
    assert "loop" in result
    assert "timestamp" in result
    assert "issues_found" in result
    assert "issues" in result
    assert "summary" in result
    
    # Check that the result was added to cto_reflections
    assert "cto_reflections" in mock_project_memory["test_project"]
    assert len(mock_project_memory["test_project"]["cto_reflections"]) == 1
    
    # Check that issues were detected (agent_shortfall and repeated failed tools)
    assert result["issues_found"] == True
    assert "agent_shortfall" in result["issues"]
    
    # Check that a system flag was set
    assert "system_flags" in mock_project_memory["test_project"]
    assert len(mock_project_memory["test_project"]["system_flags"]) == 1
    assert mock_project_memory["test_project"]["system_flags"][0]["level"] == "warning"

def test_reflection_analyzer(mock_project_memory):
    # Create a reflection analyzer
    analyzer = ReflectionAnalyzer(mock_project_memory["test_project"])
    
    # Analyze the reflection
    issues = analyzer.analyze_reflection()
    
    # Check that skipped_steps issue was detected
    assert "skipped_steps" in issues
    assert "step4" in issues["skipped_steps"]["skipped"]
    
    # Modify the reflection confidence to test low confidence detection
    mock_project_memory["test_project"]["last_reflection"]["confidence"] = 0.3
    issues = analyzer.analyze_reflection()
    
    # Check that low_confidence issue was detected
    assert "low_confidence" in issues
    assert issues["low_confidence"]["value"] == 0.3

def test_system_flag_manager(mock_project_memory):
    # Create a system flag manager
    flag_manager = SystemFlagManager(mock_project_memory, "test_project")
    
    # Set a system flag
    flag = flag_manager.set_system_flag(
        level="error",
        origin="test",
        issues={"test_issue": "This is a test issue"}
    )
    
    # Check that the flag was set correctly
    assert flag["level"] == "error"
    assert flag["origin"] == "test"
    assert "test_issue" in flag["issues"]
    
    # Get active flags
    flags = flag_manager.get_active_flags()
    assert len(flags) == 2  # One from CTO agent run, one we just added
    
    # Get flags filtered by level
    error_flags = flag_manager.get_active_flags(level="error")
    assert len(error_flags) == 1
    assert error_flags[0]["level"] == "error"
    
    # Clear flags by origin
    flag_manager.clear_flags(origin="test")
    flags = flag_manager.get_active_flags()
    assert len(flags) == 1  # Only the CTO agent flag should remain
    
    # Clear all flags
    flag_manager.clear_flags()
    flags = flag_manager.get_active_flags()
    assert len(flags) == 0
