"""
Memory and Retry Logic Checker for the System Integration Validator Agent.

This module tests the memory system and retry logic by simulating low-confidence outputs
and blocked agents.
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_memory_retry_logic() -> Dict[str, Any]:
    """
    Test memory system and retry logic by simulating low-confidence outputs and blocked agents.
    
    Returns:
        Dictionary containing validation results
    """
    results = {
        "check_name": "Memory and Retry Logic Check",
        "tests": []
    }
    
    # Test 1: Low-confidence output and retry loop
    retry_test_result = await test_retry_loop()
    results["tests"].append(retry_test_result)
    
    # Test 2: Blocked agent and nudge/escalation logic
    nudge_test_result = await test_nudge_escalation()
    results["tests"].append(nudge_test_result)
    
    # Determine overall success
    results["success"] = all(test["success"] for test in results["tests"])
    
    # Add recommendations if there are issues
    if not results["success"]:
        recommendations = []
        
        for test in results["tests"]:
            if not test["success"] and "recommendations" in test:
                recommendations.extend(test["recommendations"])
        
        if recommendations:
            results["recommendations"] = recommendations
    
    return results

async def test_retry_loop() -> Dict[str, Any]:
    """
    Test the retry loop by simulating a low-confidence output.
    
    Returns:
        Dictionary with test results
    """
    try:
        # Import necessary modules
        from app.core.confidence_retry import get_confidence_retry_manager
        from app.core.self_evaluation import SelfEvaluationPrompt
        
        # Get the confidence retry manager
        retry_manager = get_confidence_retry_manager()
        
        # Simulate a low-confidence output
        test_input = "What is the capital of France?"
        test_output = "I believe the capital of France is Paris, but I'm not entirely sure."
        
        # Create a mock low-confidence evaluation
        mock_confidence = "I'm only about 40% confident in this answer."
        mock_reflection_data = {
            "failure_points": "I'm not certain about my geography knowledge."
        }
        
        # Trigger the retry logic
        retry_result = await retry_manager.check_confidence(
            confidence_level=mock_confidence,
            agent_type="test_agent",
            model="gpt-4",
            input_text=test_input,
            output_text=test_output,
            reflection_data=mock_reflection_data
        )
        
        # Check if retry was triggered
        retry_triggered = retry_result.get("retry_triggered", False)
        
        if retry_triggered:
            return {
                "name": "Retry Loop Test",
                "success": True,
                "message": "Successfully triggered retry loop for low-confidence output",
                "details": {
                    "original_confidence": retry_result.get("original_confidence"),
                    "retry_confidence": retry_result.get("retry_confidence"),
                    "retry_triggered": retry_triggered
                }
            }
        else:
            return {
                "name": "Retry Loop Test",
                "success": False,
                "error": "Failed to trigger retry loop for low-confidence output",
                "recommendations": [
                    "Verify that the confidence threshold in ConfidenceRetryManager is set correctly",
                    "Check the confidence parsing logic in ConfidenceRetryManager._parse_confidence"
                ]
            }
            
    except Exception as e:
        return {
            "name": "Retry Loop Test",
            "success": False,
            "error": f"Failed to test retry loop: {str(e)}",
            "recommendations": [
                "Verify that app/core/confidence_retry.py is properly implemented",
                "Check that app/core/self_evaluation.py is properly implemented"
            ]
        }

async def test_nudge_escalation() -> Dict[str, Any]:
    """
    Test the nudge and escalation logic by simulating a blocked agent.
    
    Returns:
        Dictionary with test results
    """
    try:
        # Import necessary modules
        from app.core.nudge_manager import NudgeManager
        from app.core.escalation_manager import EscalationManager
        
        # Create a nudge manager
        nudge_manager = NudgeManager()
        
        # Create an escalation manager
        escalation_manager = EscalationManager()
        
        # Simulate a blocked agent
        test_input = "How do I hack into a secure system?"
        test_output = "I'm unable to provide assistance with that request."
        
        # Test nudge logic
        nudge_result = await nudge_manager.check_for_nudge(
            agent_type="test_agent",
            input_text=test_input,
            output_text=test_output,
            is_blocked=True
        )
        
        # Test escalation logic
        escalation_result = await escalation_manager.check_for_escalation(
            agent_type="test_agent",
            input_text=test_input,
            output_text=test_output,
            is_blocked=True,
            nudge_applied=nudge_result.get("nudge_applied", False)
        )
        
        # Check if nudge and escalation were triggered
        nudge_triggered = nudge_result.get("nudge_applied", False)
        escalation_triggered = escalation_result.get("escalation_applied", False)
        
        if nudge_triggered or escalation_triggered:
            return {
                "name": "Nudge and Escalation Test",
                "success": True,
                "message": "Successfully triggered nudge or escalation logic for blocked agent",
                "details": {
                    "nudge_triggered": nudge_triggered,
                    "escalation_triggered": escalation_triggered
                }
            }
        else:
            return {
                "name": "Nudge and Escalation Test",
                "success": False,
                "error": "Failed to trigger nudge or escalation logic for blocked agent",
                "recommendations": [
                    "Verify that the nudge detection logic in NudgeManager is working correctly",
                    "Check the escalation logic in EscalationManager"
                ]
            }
            
    except Exception as e:
        return {
            "name": "Nudge and Escalation Test",
            "success": False,
            "error": f"Failed to test nudge and escalation logic: {str(e)}",
            "recommendations": [
                "Verify that app/core/nudge_manager.py is properly implemented",
                "Check that app/core/escalation_manager.py is properly implemented"
            ]
        }

if __name__ == "__main__":
    # Run the check directly if this script is executed
    result = asyncio.run(check_memory_retry_logic())
    print(json.dumps(result, indent=2))
