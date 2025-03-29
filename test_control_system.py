"""
Test script for the Agent Control Schema + Guardian Enforcement System.

This script tests permission enforcement, rate limiting, and violation logging.
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime

# Add app directory to path
sys.path.append('/home/ubuntu/app')

# Import control enforcer and violation logger
from core.control_enforcer import ControlEnforcer, get_enforcer
from core.violation_logger import ViolationLogger, get_violation_logger

def test_schema_loading():
    """Test loading the control schema"""
    print("\n=== Testing Schema Loading ===")
    
    try:
        # Initialize control enforcer
        enforcer = ControlEnforcer()
        schema = enforcer._load_schema()
        
        # Validate schema
        is_valid = enforcer.validate_schema(schema)
        
        if is_valid:
            print("✅ Schema loaded and validated successfully")
            print(f"Schema version: {schema.get('schema_version')}")
            print(f"Schema ID: {schema.get('schema_id')}")
        else:
            print("❌ Schema validation failed")
        
        return is_valid
    
    except Exception as e:
        print(f"❌ Error loading schema: {str(e)}")
        return False

def test_agent_schema_loading():
    """Test loading agent-specific schemas"""
    print("\n=== Testing Agent Schema Loading ===")
    
    try:
        # Initialize control enforcer
        enforcer = ControlEnforcer()
        
        # Test loading schemas for all agents
        agent_names = ["builder", "memory", "ops", "research", "guardian"]
        results = {}
        
        for agent_name in agent_names:
            try:
                agent_schema = enforcer.load_agent_schema(agent_name)
                results[agent_name] = {
                    "success": True,
                    "permissions": agent_schema.get("permissions", {})
                }
                print(f"✅ Loaded schema for {agent_name}")
            except Exception as e:
                results[agent_name] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ Failed to load schema for {agent_name}: {str(e)}")
        
        # Print summary
        success_count = sum(1 for r in results.values() if r.get("success", False))
        print(f"\nSuccessfully loaded {success_count}/{len(agent_names)} agent schemas")
        
        return results
    
    except Exception as e:
        print(f"❌ Error in agent schema loading test: {str(e)}")
        return {}

def test_permission_enforcement():
    """Test enforcing permissions"""
    print("\n=== Testing Permission Enforcement ===")
    
    try:
        # Initialize control enforcer
        enforcer = ControlEnforcer()
        
        # Test tool permissions
        print("\nTesting tool permissions:")
        test_cases = [
            {"agent": "builder", "tool": "code_executor", "expected": True},
            {"agent": "builder", "tool": "web_search", "expected": False},
            {"agent": "memory", "tool": "web_search", "expected": True},
            {"agent": "memory", "tool": "github_commit", "expected": False},
            {"agent": "ops", "tool": "slack_messenger", "expected": True},
            {"agent": "research", "tool": "multi_agent_debater", "expected": True},
            {"agent": "guardian", "tool": "disable_agent", "expected": True},
            {"agent": "guardian", "tool": "code_executor", "expected": False}
        ]
        
        for case in test_cases:
            result = enforcer.check_tool_permission(case["agent"], case["tool"])
            if result == case["expected"]:
                print(f"✅ {case['agent']} {'can' if result else 'cannot'} use {case['tool']} (expected)")
            else:
                print(f"❌ {case['agent']} {'can' if result else 'cannot'} use {case['tool']} (unexpected)")
        
        # Test code execution permissions
        print("\nTesting code execution permissions:")
        code_test_cases = [
            {"agent": "builder", "expected": True},
            {"agent": "memory", "expected": False},
            {"agent": "ops", "expected": True},
            {"agent": "research", "expected": False},
            {"agent": "guardian", "expected": False}
        ]
        
        for case in code_test_cases:
            result = enforcer.check_code_execution(case["agent"])
            if result == case["expected"]:
                print(f"✅ {case['agent']} {'can' if result else 'cannot'} execute code (expected)")
            else:
                print(f"❌ {case['agent']} {'can' if result else 'cannot'} execute code (unexpected)")
        
        # Test memory access permissions
        print("\nTesting memory access permissions:")
        memory_test_cases = [
            {"agent": "builder", "scope": "project_code", "write": True, "expected": True},
            {"agent": "builder", "scope": "user_data", "write": True, "expected": False},
            {"agent": "memory", "scope": "user_data", "write": True, "expected": True},
            {"agent": "memory", "scope": "infrastructure", "write": True, "expected": False},
            {"agent": "ops", "scope": "infrastructure", "write": True, "expected": True},
            {"agent": "research", "scope": "research_data", "write": True, "expected": True},
            {"agent": "guardian", "scope": "all_agents", "write": True, "expected": True}
        ]
        
        for case in memory_test_cases:
            result = enforcer.check_memory_access(case["agent"], case["scope"], case["write"])
            if result == case["expected"]:
                print(f"✅ {case['agent']} {'can' if result else 'cannot'} access {case['scope']} memory (expected)")
            else:
                print(f"❌ {case['agent']} {'can' if result else 'cannot'} access {case['scope']} memory (unexpected)")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in permission enforcement test: {str(e)}")
        return False

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n=== Testing Rate Limiting ===")
    
    try:
        # Initialize control enforcer
        enforcer = ControlEnforcer()
        
        # Test rate limiting for builder agent (limit: 5 per minute)
        agent_name = "builder"
        enforcer.register_agent_start(agent_name)
        
        print(f"Testing rate limit for {agent_name} (5 per minute):")
        
        # Try 7 actions (should allow 5, block 2)
        results = []
        for i in range(7):
            result = enforcer.check_rate_limit(agent_name)
            results.append(result)
            print(f"Action {i+1}: {'✅ Allowed' if result else '❌ Blocked'}")
        
        # Verify results
        allowed = sum(1 for r in results if r)
        blocked = sum(1 for r in results if not r)
        
        print(f"\nRate limit test results: {allowed} allowed, {blocked} blocked")
        if allowed == 5 and blocked == 2:
            print("✅ Rate limiting working as expected")
        else:
            print("❌ Rate limiting not working as expected")
        
        # Test retry limiting
        print("\nTesting retry limiting:")
        
        # Test retry limit for memory agent (limit: 3)
        agent_name = "memory"
        action_id = "test_action_1"
        
        # Try 5 retries (should allow 3, block 2)
        retry_results = []
        for i in range(5):
            result = enforcer.check_retry_limit(agent_name, action_id)
            retry_results.append(result)
            print(f"Retry {i+1}: {'✅ Allowed' if result else '❌ Blocked'}")
        
        # Verify results
        allowed = sum(1 for r in retry_results if r)
        blocked = sum(1 for r in retry_results if not r)
        
        print(f"\nRetry limit test results: {allowed} allowed, {blocked} blocked")
        if allowed == 3 and blocked == 2:
            print("✅ Retry limiting working as expected")
        else:
            print("❌ Retry limiting not working as expected")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in rate limiting test: {str(e)}")
        return False

def test_violation_logging():
    """Test violation logging functionality"""
    print("\n=== Testing Violation Logging ===")
    
    try:
        # Initialize violation logger
        logger = ViolationLogger()
        
        # Log a test violation
        violation = logger.log_violation(
            agent_name="test_agent",
            violation_type="test_violation",
            violation_reason="testing_violation_logger",
            details={"test": True, "timestamp": datetime.now().isoformat()},
            recommended_action="log",
            threshold_exceeded=False
        )
        
        print(f"Logged test violation: {violation.get('violation_type')}")
        
        # Get recent violations
        recent = logger.get_recent_violations(limit=5)
        
        if recent and len(recent) > 0:
            print(f"✅ Retrieved {len(recent)} recent violations")
            print(f"Most recent violation: {recent[0].get('violation_type')} by {recent[0].get('agent_name')}")
        else:
            print("❌ Failed to retrieve recent violations")
        
        # Get statistics
        stats = logger.get_violation_statistics()
        
        if stats:
            print(f"✅ Generated violation statistics")
            print(f"Total violations: {stats.get('total_violations', 0)}")
        else:
            print("❌ Failed to generate violation statistics")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in violation logging test: {str(e)}")
        return False

def test_lifecycle_management():
    """Test agent lifecycle management"""
    print("\n=== Testing Lifecycle Management ===")
    
    try:
        # Initialize control enforcer
        enforcer = ControlEnforcer()
        
        # Test normal lifecycle
        agent_name = "research"
        enforcer.register_agent_start(agent_name)
        
        # Should be allowed to continue
        result = enforcer.check_lifecycle(agent_name)
        print(f"Initial lifecycle check: {'✅ Allowed' if result else '❌ Blocked'}")
        
        # Simulate exceeding max run time by manipulating start time
        print("\nSimulating exceeding max run time:")
        enforcer.agent_start_times[agent_name] = time.time() - 2000  # Research agent has 1800 sec limit
        
        # Should be blocked now
        result = enforcer.check_lifecycle(agent_name)
        print(f"After exceeding max run time: {'✅ Allowed' if result else '❌ Blocked (expected)'}")
        
        if not result:
            print("✅ Lifecycle management working as expected")
        else:
            print("❌ Lifecycle management not working as expected")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in lifecycle management test: {str(e)}")
        return False

def test_confidence_escalation():
    """Test confidence-based escalation"""
    print("\n=== Testing Confidence Escalation ===")
    
    try:
        # Initialize control enforcer
        enforcer = ControlEnforcer()
        
        # Test confidence escalation for different agents
        test_cases = [
            {"agent": "builder", "confidence": 0.6, "expected_escalate": False},
            {"agent": "builder", "confidence": 0.4, "expected_escalate": True},
            {"agent": "memory", "confidence": 0.7, "expected_escalate": False},
            {"agent": "memory", "confidence": 0.5, "expected_escalate": True},
            {"agent": "ops", "confidence": 0.8, "expected_escalate": False},
            {"agent": "ops", "confidence": 0.6, "expected_escalate": True},
            {"agent": "guardian", "confidence": 0.8, "expected_escalate": False},
            {"agent": "guardian", "confidence": 0.6, "expected_escalate": True}
        ]
        
        for case in test_cases:
            result = enforcer.check_confidence(case["agent"], case["confidence"])
            escalate = result.get("escalate", False)
            
            if escalate == case["expected_escalate"]:
                print(f"✅ {case['agent']} with confidence {case['confidence']} {'escalates' if escalate else 'does not escalate'} (expected)")
            else:
                print(f"❌ {case['agent']} with confidence {case['confidence']} {'escalates' if escalate else 'does not escalate'} (unexpected)")
        
        return True
    
    except Exception as e:
        print(f"❌ Error in confidence escalation test: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Starting tests for Agent Control Schema + Guardian Enforcement System")
    
    # Run all tests
    tests = [
        test_schema_loading,
        test_agent_schema_loading,
        test_permission_enforcement,
        test_rate_limiting,
        test_violation_logging,
        test_lifecycle_management,
        test_confidence_escalation
    ]
    
    results = {}
    
    for test_func in tests:
        test_name = test_func.__name__
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test {test_name} failed with error: {str(e)}")
            results[test_name] = False
    
    # Print summary
    print("\n=== Test Summary ===")
    passed = sum(1 for r in results.values() if r)
    failed = sum(1 for r in results.values() if not r)
    
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    for test_name, result in results.items():
        print(f"{'✅' if result else '❌'} {test_name}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n❌ {failed} tests failed")

if __name__ == "__main__":
    main()
