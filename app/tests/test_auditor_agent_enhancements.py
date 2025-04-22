"""
Tests for the enhanced Auditor Agent module.

This module tests the new features added to the Auditor Agent:
- Advanced anomaly detection
- Temporal pattern analysis
- Resource utilization monitoring
- Correlation analysis
- Risk scoring
"""

import os
import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from app.modules.auditor_agent import (
    AuditorAgent, 
    audit_loop, 
    get_audit_result, 
    get_audit_issues, 
    get_audit_warnings, 
    get_audit_recommendations,
    get_temporal_patterns
)

# Test data
TEST_LOOP_ID = "test_loop_123"
TEST_AGENT_ID = "test_agent_456"

# Mock loop data with execution anomalies for testing
MOCK_LOOP_DATA_WITH_ANOMALIES = {
    "loop_id": TEST_LOOP_ID,
    "agents": [
        {
            "id": "agent_1",
            "start_time": (datetime.utcnow() - timedelta(seconds=10)).isoformat(),
            "end_time": (datetime.utcnow() - timedelta(seconds=9)).isoformat(),
            "output": {"text": "This is agent 1 output mentioning belief_1 and belief_2"}
        },
        {
            "id": "agent_2",
            "start_time": (datetime.utcnow() - timedelta(seconds=8)).isoformat(),
            "end_time": (datetime.utcnow() - timedelta(seconds=5)).isoformat(),
            "output": {"text": "This is agent 2 output mentioning belief_1"}
        },
        {
            "id": "agent_3",
            "start_time": (datetime.utcnow() - timedelta(seconds=4)).isoformat(),
            "end_time": (datetime.utcnow() - timedelta(seconds=1)).isoformat(),
            "output": {"text": "This is agent 3 output with password=secret123 and API_KEY=abcdef"}
        }
    ],
    "beliefs_referenced": ["belief_1", "belief_2"],
    "memory_operations": [
        {
            "operation_type": "write",
            "key": "key_1",
            "agent_id": "agent_1",
            "success": True,
            "timestamp": (datetime.utcnow() - timedelta(seconds=9.5)).isoformat()
        },
        {
            "operation_type": "read",
            "key": "key_1",
            "agent_id": "agent_2",
            "success": True,
            "timestamp": (datetime.utcnow() - timedelta(seconds=7.5)).isoformat()
        },
        {
            "operation_type": "read",
            "key": "key_1",
            "agent_id": "agent_3",
            "success": True,
            "timestamp": (datetime.utcnow() - timedelta(seconds=3.5)).isoformat()
        },
        {
            "operation_type": "write",
            "key": "key_2",
            "agent_id": "agent_2",
            "success": True,
            "timestamp": (datetime.utcnow() - timedelta(seconds=6.5)).isoformat()
        }
    ],
    "memory_usage_kb": {
        "agent_1": 1024,
        "agent_2": 2048,
        "agent_3": 5120  # Anomalously high memory usage
    },
    "cpu_usage_percent": {
        "agent_1": 30,
        "agent_2": 45,
        "agent_3": 85  # Anomalously high CPU usage
    },
    "execution_time_ms": {
        "agent_1": 1000,
        "agent_2": 3000,
        "agent_3": 3000
    }
}

@pytest.fixture
def auditor_agent():
    """Create an auditor agent instance for testing."""
    with patch('app.modules.auditor_agent.read_from_memory') as mock_read, \
         patch('app.modules.auditor_agent.write_to_memory') as mock_write:
        
        # Mock read_from_memory to return historical audits
        async def mock_read_impl(key):
            if key == "loop_audits_history":
                return [
                    {
                        "loop_id": "previous_loop_1",
                        "audit_id": "audit_previous_loop_1",
                        "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                        "overall_score": 0.82,
                        "belief_consistency_score": 0.88,
                        "memory_integrity_score": 0.79,
                        "execution_score": 0.85,
                        "security_score": 0.90,
                        "resource_score": 0.75,
                        "issue_count": 2,
                        "warning_count": 1,
                        "recommendation_count": 2
                    },
                    {
                        "loop_id": "previous_loop_2",
                        "audit_id": "audit_previous_loop_2",
                        "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                        "overall_score": 0.79,
                        "belief_consistency_score": 0.85,
                        "memory_integrity_score": 0.76,
                        "execution_score": 0.82,
                        "security_score": 0.88,
                        "resource_score": 0.70,
                        "issue_count": 3,
                        "warning_count": 2,
                        "recommendation_count": 2
                    }
                ]
            return None
        
        mock_read.side_effect = mock_read_impl
        mock_write.return_value = True
        
        agent = AuditorAgent()
        yield agent

class TestAuditorAgentEnhancements:
    """Tests for the enhanced Auditor Agent module."""
    
    @pytest.mark.asyncio
    async def test_advanced_anomaly_detection(self, auditor_agent):
        """Test advanced anomaly detection using Z-score analysis."""
        # Audit a loop with execution anomalies
        result = await auditor_agent.audit_loop(
            loop_id=TEST_LOOP_ID,
            loop_data=MOCK_LOOP_DATA_WITH_ANOMALIES
        )
        
        # Check if execution anomalies were detected
        execution_issues = [issue for issue in result["issues"] 
                           if issue.get("type") == "execution_anomaly"]
        
        # Should detect at least one anomaly
        assert len(execution_issues) > 0
        
        # Check if Z-score is included in the anomaly detection
        assert any("z_score" in issue for issue in execution_issues)
        
        # Check if mean and standard deviation are included
        assert any("mean_time" in issue for issue in execution_issues)
        assert any("stdev_time" in issue for issue in execution_issues)
    
    @pytest.mark.asyncio
    async def test_resource_utilization_monitoring(self, auditor_agent):
        """Test resource utilization monitoring."""
        # Audit a loop with resource utilization anomalies
        result = await auditor_agent.audit_loop(
            loop_id=TEST_LOOP_ID,
            loop_data=MOCK_LOOP_DATA_WITH_ANOMALIES
        )
        
        # Check if resource score is included
        assert "resource_score" in result
        
        # Check if resource issues were detected
        resource_issues = [issue for issue in result["issues"] 
                          if issue.get("type") in ["high_memory_usage", "high_cpu_usage", "resource_inefficiency"]]
        
        # Should detect at least one resource issue
        assert len(resource_issues) > 0
        
        # Check for memory usage issues
        memory_issues = [issue for issue in resource_issues 
                        if issue.get("type") == "high_memory_usage"]
        assert len(memory_issues) > 0
        
        # Check for CPU usage issues
        cpu_issues = [issue for issue in resource_issues 
                     if issue.get("type") == "high_cpu_usage"]
        assert len(cpu_issues) > 0
    
    @pytest.mark.asyncio
    async def test_correlation_analysis(self, auditor_agent):
        """Test correlation analysis between different types of issues."""
        # Audit a loop with multiple types of issues
        result = await auditor_agent.audit_loop(
            loop_id=TEST_LOOP_ID,
            loop_data=MOCK_LOOP_DATA_WITH_ANOMALIES
        )
        
        # Check if correlation analysis is included
        assert "correlation_analysis" in result
        
        # Check if correlation strength is calculated
        assert "correlation_strength" in result["correlation_analysis"]
        
        # Check if correlated issues were detected
        correlated_issues = [issue for issue in result["issues"] 
                            if issue.get("type") in ["correlated_issues", "performance_correlation", "belief_performance_correlation"]]
        
        # The test data should generate at least one correlated issue
        assert len(correlated_issues) > 0
    
    @pytest.mark.asyncio
    async def test_temporal_pattern_analysis(self, auditor_agent):
        """Test temporal pattern analysis across multiple loop executions."""
        # Audit a loop
        result = await auditor_agent.audit_loop(
            loop_id=TEST_LOOP_ID,
            loop_data=MOCK_LOOP_DATA_WITH_ANOMALIES
        )
        
        # Check if temporal patterns are included
        assert "temporal_patterns" in result
        
        # Get temporal patterns
        patterns = await auditor_agent.get_temporal_patterns(TEST_LOOP_ID)
        
        # Should have at least one pattern
        assert len(patterns) > 0
        
        # Check pattern structure
        for pattern in patterns:
            assert "type" in pattern
            assert "description" in pattern
            assert "trend" in pattern
    
    @pytest.mark.asyncio
    async def test_risk_scoring(self, auditor_agent):
        """Test risk scoring for issues."""
        # Audit a loop with security issues
        result = await auditor_agent.audit_loop(
            loop_id=TEST_LOOP_ID,
            loop_data=MOCK_LOOP_DATA_WITH_ANOMALIES
        )
        
        # Check if issues have risk scores
        for issue in result["issues"]:
            assert "risk" in issue
            assert "impact" in issue["risk"]
            assert "likelihood" in issue["risk"]
            assert "risk_score" in issue["risk"]
            assert "risk_level" in issue["risk"]
            
            # Risk score should be between 0 and 1
            assert 0 <= issue["risk"]["risk_score"] <= 1
            
            # Risk level should be one of: low, medium, high
            assert issue["risk"]["risk_level"] in ["low", "medium", "high"]
        
        # Security issues should have high risk
        security_issues = [issue for issue in result["issues"] 
                          if issue.get("type") == "security_concern"]
        
        if security_issues:
            assert security_issues[0]["risk"]["risk_level"] == "high"
    
    @pytest.mark.asyncio
    async def test_enhanced_recommendations(self, auditor_agent):
        """Test enhanced recommendations with specific actions."""
        # Audit a loop
        result = await auditor_agent.audit_loop(
            loop_id=TEST_LOOP_ID,
            loop_data=MOCK_LOOP_DATA_WITH_ANOMALIES
        )
        
        # Get recommendations
        recommendations = result["recommendations"]
        
        # Should have at least one recommendation
        assert len(recommendations) > 0
        
        # Check if recommendations have priorities
        for recommendation in recommendations:
            assert "priority" in recommendation
            assert recommendation["priority"] in ["high", "medium", "low"]
        
        # Check if some recommendations have specific actions
        specific_actions_count = sum(1 for r in recommendations if "specific_actions" in r)
        assert specific_actions_count > 0
    
    @pytest.mark.asyncio
    async def test_get_temporal_patterns_function(self, auditor_agent):
        """Test the get_temporal_patterns function."""
        # Audit a loop first
        await auditor_agent.audit_loop(
            loop_id=TEST_LOOP_ID,
            loop_data=MOCK_LOOP_DATA_WITH_ANOMALIES
        )
        
        # Get temporal patterns
        patterns = await get_temporal_patterns(TEST_LOOP_ID)
        
        # Should have at least one pattern
        assert len(patterns) > 0
        
        # Check pattern structure
        for pattern in patterns:
            assert "type" in pattern
            assert "description" in pattern
            assert "trend" in pattern

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
