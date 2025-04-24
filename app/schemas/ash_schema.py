"""
ASH Agent Schema Definitions

This module defines the schemas for ASH agent requests and responses.
The ASH agent is responsible for risk analysis, anomaly detection, and
handling morally complex, high-risk operations.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AshAnalysisRequest(BaseModel):
    """
    Schema for ASH agent analysis request.
    """
    scenario_id: str = Field(..., description="Unique identifier for the scenario to analyze")
    context: Dict[str, Any] = Field(
        ..., 
        description="Context information for the analysis"
    )
    constraints: Optional[List[str]] = Field(
        default=[],
        description="List of constraints to consider in the analysis"
    )
    risk_tolerance: Optional[float] = Field(
        default=0.5,
        description="Risk tolerance level (0.0 to 1.0, with 1.0 being highest)",
        ge=0.0,
        le=1.0
    )
    tools: Optional[List[str]] = Field(
        default=["analyze", "detect", "test"],
        description="List of tools to use for the analysis"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "scenario_id": "scenario_123",
                "context": {
                    "domain": "cybersecurity",
                    "threat_level": "high",
                    "time_sensitivity": "critical"
                },
                "constraints": ["legal_compliance", "ethical_boundaries"],
                "risk_tolerance": 0.7,
                "tools": ["analyze", "detect"]
            }
        }


class RiskFactor(BaseModel):
    """
    Schema for risk factor details.
    """
    factor_id: str = Field(..., description="Unique identifier for the risk factor")
    name: str = Field(..., description="Name of the risk factor")
    probability: float = Field(
        ..., 
        description="Probability of the risk factor (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    impact: float = Field(
        ..., 
        description="Impact of the risk factor (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    description: str = Field(..., description="Description of the risk factor")
    mitigation_strategies: Optional[List[str]] = Field(
        default=[],
        description="List of mitigation strategies"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "factor_id": "risk_001",
                "name": "Data breach",
                "probability": 0.3,
                "impact": 0.9,
                "description": "Unauthorized access to sensitive data",
                "mitigation_strategies": [
                    "Implement encryption",
                    "Restrict access permissions",
                    "Regular security audits"
                ]
            }
        }


class AshAnalysisResult(BaseModel):
    """
    Schema for ASH agent analysis result.
    """
    status: str = Field(..., description="Status of the analysis (success, error)")
    scenario_id: str = Field(..., description="Scenario identifier")
    risk_assessment: Optional[str] = Field(
        None, 
        description="Overall risk assessment"
    )
    risk_factors: Optional[List[RiskFactor]] = Field(
        default=[],
        description="List of identified risk factors"
    )
    anomalies_detected: Optional[List[str]] = Field(
        default=[],
        description="List of detected anomalies"
    )
    recommended_actions: Optional[List[str]] = Field(
        default=[],
        description="List of recommended actions"
    )
    overall_risk_score: Optional[float] = Field(
        None,
        description="Overall risk score (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the analysis"
    )
    message: Optional[str] = Field(None, description="Error message if status is error")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "scenario_id": "scenario_123",
                "risk_assessment": "The scenario presents significant risks that require immediate attention.",
                "risk_factors": [
                    {
                        "factor_id": "risk_001",
                        "name": "Data breach",
                        "probability": 0.3,
                        "impact": 0.9,
                        "description": "Unauthorized access to sensitive data",
                        "mitigation_strategies": [
                            "Implement encryption",
                            "Restrict access permissions",
                            "Regular security audits"
                        ]
                    }
                ],
                "anomalies_detected": [
                    "Unusual access patterns",
                    "Unexpected system behavior"
                ],
                "recommended_actions": [
                    "Implement enhanced monitoring",
                    "Conduct security audit",
                    "Update access controls"
                ],
                "overall_risk_score": 0.65,
                "timestamp": "2025-04-24T19:11:34Z"
            }
        }


class AshTestRequest(BaseModel):
    """
    Schema for ASH agent test request.
    """
    scenario_id: str = Field(..., description="Unique identifier for the scenario to test")
    test_parameters: Dict[str, Any] = Field(
        ..., 
        description="Parameters for the test"
    )
    expected_outcomes: Optional[List[str]] = Field(
        default=[],
        description="List of expected outcomes"
    )
    tools: Optional[List[str]] = Field(
        default=["test"],
        description="List of tools to use for the test"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "scenario_id": "scenario_123",
                "test_parameters": {
                    "load_level": "high",
                    "duration": 3600,
                    "failure_points": ["network", "database"]
                },
                "expected_outcomes": [
                    "System remains operational",
                    "Data integrity maintained",
                    "Alerts triggered appropriately"
                ],
                "tools": ["test"]
            }
        }


class TestResult(BaseModel):
    """
    Schema for test result details.
    """
    test_id: str = Field(..., description="Unique identifier for the test")
    name: str = Field(..., description="Name of the test")
    status: str = Field(..., description="Status of the test (passed, failed, error)")
    description: str = Field(..., description="Description of the test")
    actual_outcome: str = Field(..., description="Actual outcome of the test")
    expected_outcome: Optional[str] = Field(None, description="Expected outcome of the test")
    
    class Config:
        schema_extra = {
            "example": {
                "test_id": "test_001",
                "name": "Network resilience test",
                "status": "passed",
                "description": "Test system resilience under network failure conditions",
                "actual_outcome": "System remained operational with 99.9% uptime",
                "expected_outcome": "System remains operational"
            }
        }


class AshTestResult(BaseModel):
    """
    Schema for ASH agent test result.
    """
    status: str = Field(..., description="Status of the test (success, error)")
    scenario_id: str = Field(..., description="Scenario identifier")
    test_summary: Optional[str] = Field(
        None, 
        description="Summary of the test results"
    )
    test_results: Optional[List[TestResult]] = Field(
        default=[],
        description="List of individual test results"
    )
    anomalies_detected: Optional[List[str]] = Field(
        default=[],
        description="List of detected anomalies during testing"
    )
    recommendations: Optional[List[str]] = Field(
        default=[],
        description="List of recommendations based on test results"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the test"
    )
    message: Optional[str] = Field(None, description="Error message if status is error")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "scenario_id": "scenario_123",
                "test_summary": "All tests completed successfully with minor anomalies detected.",
                "test_results": [
                    {
                        "test_id": "test_001",
                        "name": "Network resilience test",
                        "status": "passed",
                        "description": "Test system resilience under network failure conditions",
                        "actual_outcome": "System remained operational with 99.9% uptime",
                        "expected_outcome": "System remains operational"
                    }
                ],
                "anomalies_detected": [
                    "Slight performance degradation under extreme load"
                ],
                "recommendations": [
                    "Optimize database queries",
                    "Increase cache size",
                    "Implement load balancing"
                ],
                "timestamp": "2025-04-24T19:11:34Z"
            }
        }


# Fallback schema for handling errors
class AshErrorResult(BaseModel):
    """
    Schema for ASH agent error result.
    """
    status: str = Field("error", description="Status of the operation")
    message: str = Field(..., description="Error message")
    scenario_id: Optional[str] = Field(None, description="Scenario identifier if applicable")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO timestamp of the error"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "message": "Failed to analyze scenario: insufficient data",
                "scenario_id": "scenario_123",
                "timestamp": "2025-04-24T19:11:34Z"
            }
        }
