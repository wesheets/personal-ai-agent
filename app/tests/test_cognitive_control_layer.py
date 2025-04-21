"""
Cognitive Control Layer Test Module

This module provides tests for the Claude-inspired cognitive control layer.
It tests all components and their integration to ensure they work together correctly.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all cognitive control layer components
from app.modules.loop_validator import validate_loop, validate_and_enrich_loop
from app.modules.core_beliefs_integration import (
    inject_belief_references, 
    check_belief_conflicts,
    get_belief_description,
    get_belief_priority,
    get_violation_handling
)
from app.modules.depth_controller import (
    enrich_loop_with_depth, 
    preload_depth_for_rerun,
    get_agents_for_depth,
    get_reflection_config,
    get_required_beliefs_for_depth
)
from app.modules.agent_dispatch import create_dispatcher, dispatch_agent
from app.modules.orchestrator_integration import (
    integrate_with_orchestrator, 
    process_reflection_with_controls,
    determine_rerun_depth_with_controls
)
from app.modules.planning_logic_integration import (
    generate_reflection_plan_with_depth, 
    adjust_execution_plan_with_depth
)
from app.modules.agent_permission_validator import (
    enforce_agent_permissions,
    check_permission,
    log_violation,
    get_substitute_action
)

def test_loop_validator():
    """Test the loop validator component."""
    logger.info("Testing Loop Validator...")
    
    # Test valid loop
    valid_loop = {
        "loop_id": "test_loop_001",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE",
        "plan": [
            {"step": 1, "description": "Analyze requirements"},
            {"step": 2, "description": "Design architecture"},
            {"step": 3, "description": "Implement solution"}
        ],
        "reflection_agent": ["CRITIC", "CEO"]
    }
    
    is_valid, reason, validation_result = validate_loop(valid_loop)
    assert is_valid, f"Valid loop failed validation: {reason}"
    assert "checked_components" in validation_result, "Validation result missing checked_components"
    assert len(validation_result["checked_components"]) >= 4, "Not all components were checked"
    logger.info("✓ Valid loop passed validation")
    
    # Test invalid loop (missing prompt)
    invalid_loop = {
        "loop_id": "test_loop_002",
        "orchestrator_persona": "SAGE",
        "plan": [
            {"step": 1, "description": "Analyze requirements"}
        ],
        "reflection_agent": ["CRITIC"]
    }
    
    is_valid, reason, validation_result = validate_loop(invalid_loop)
    assert not is_valid, "Invalid loop passed validation"
    assert "missing prompt" in reason.lower(), f"Unexpected validation failure reason: {reason}"
    assert "missing_components" in validation_result, "Validation result missing missing_components"
    assert "prompt" in validation_result["missing_components"], "Missing prompt not reported in missing_components"
    logger.info("✓ Invalid loop (missing prompt) correctly rejected")
    
    # Test invalid loop (invalid persona)
    invalid_persona_loop = {
        "loop_id": "test_loop_003",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "INVALID_PERSONA",
        "plan": [
            {"step": 1, "description": "Analyze requirements"},
            {"step": 2, "description": "Design architecture"},
            {"step": 3, "description": "Implement solution"}
        ],
        "reflection_agent": ["CRITIC", "CEO"]
    }
    
    is_valid, reason, validation_result = validate_loop(invalid_persona_loop)
    assert not is_valid, "Invalid persona loop passed validation"
    assert "invalid persona" in reason.lower(), f"Unexpected validation failure reason: {reason}"
    assert "invalid_components" in validation_result, "Validation result missing invalid_components"
    assert "orchestrator_persona" in validation_result["invalid_components"], "Invalid persona not reported in invalid_components"
    logger.info("✓ Invalid loop (invalid persona) correctly rejected")
    
    # Test invalid loop (insufficient plan steps)
    insufficient_plan_loop = {
        "loop_id": "test_loop_004",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE",
        "plan": [
            {"step": 1, "description": "Implement solution"}
        ],
        "reflection_agent": ["CRITIC", "CEO"]
    }
    
    is_valid, reason, validation_result = validate_loop(insufficient_plan_loop)
    assert not is_valid, "Insufficient plan loop passed validation"
    assert "plan has fewer than" in reason.lower(), f"Unexpected validation failure reason: {reason}"
    assert "invalid_components" in validation_result, "Validation result missing invalid_components"
    assert "plan" in validation_result["invalid_components"], "Invalid plan not reported in invalid_components"
    logger.info("✓ Invalid loop (insufficient plan steps) correctly rejected")
    
    # Test invalid loop (missing required agent for depth)
    missing_agent_loop = {
        "loop_id": "test_loop_005",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE",
        "plan": [
            {"step": 1, "description": "Analyze requirements"},
            {"step": 2, "description": "Design architecture"},
            {"step": 3, "description": "Implement solution"}
        ],
        "reflection_agent": ["HAL"],
        "depth": "deep"
    }
    
    is_valid, reason, validation_result = validate_loop(missing_agent_loop)
    assert not is_valid, "Missing agent loop passed validation"
    assert "missing required agent" in reason.lower(), f"Unexpected validation failure reason: {reason}"
    assert "missing_components" in validation_result, "Validation result missing missing_components"
    logger.info("✓ Invalid loop (missing required agent for depth) correctly rejected")
    
    # Test validate_and_enrich_loop function
    enriched_loop = validate_and_enrich_loop(valid_loop)
    assert enriched_loop["validation_status"] == "passed", "Enriched loop validation failed"
    assert "depth" in enriched_loop, "Depth not added to enriched loop"
    assert "belief_reference" in enriched_loop, "Belief references not added to enriched loop"
    assert "validation_timestamp" in enriched_loop, "Validation timestamp not added to enriched loop"
    logger.info("✓ Loop correctly validated and enriched")
    
    logger.info("Loop Validator tests passed!\n")

def test_core_beliefs_integration():
    """Test the core beliefs integration component."""
    logger.info("Testing Core Beliefs Integration...")
    
    # Test belief reference injection
    loop_data = {
        "loop_id": "test_loop_001",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE",
        "depth": "standard"
    }
    
    enriched_loop = inject_belief_references(loop_data)
    assert "belief_reference" in enriched_loop, "Belief references not injected"
    assert "reflection_before_execution" in enriched_loop["belief_reference"], "Missing core belief: reflection_before_execution"
    assert any("alignment_threshold" in ref for ref in enriched_loop["belief_reference"]), "Missing core belief: alignment_threshold"
    logger.info("✓ Belief references correctly injected")
    
    # Test belief conflict detection
    reflection_result = {
        "alignment_score": 0.6,  # Below threshold
        "drift_score": 0.3,      # Above threshold
        "bias_echo": True
    }
    
    conflicts, conflict_details = check_belief_conflicts(loop_data, reflection_result)
    assert "alignment_threshold" in conflicts, "Alignment threshold conflict not detected"
    assert "drift_threshold" in conflicts, "Drift threshold conflict not detected"
    assert "bias_awareness_required" in conflicts, "Bias awareness conflict not detected"
    assert "severity" in conflict_details, "Conflict details missing severity"
    assert "conflict_count" in conflict_details, "Conflict details missing conflict_count"
    logger.info("✓ Belief conflicts correctly detected with details")
    
    # Test belief description retrieval
    belief_desc = get_belief_description("reflection_before_execution")
    assert belief_desc is not None, "Belief description not found"
    assert len(belief_desc) > 0, "Empty belief description"
    logger.info("✓ Belief description correctly retrieved")
    
    # Test belief priority retrieval
    belief_priority = get_belief_priority("alignment_over_speed")
    assert belief_priority is not None, "Belief priority not found"
    assert isinstance(belief_priority, (int, float)), "Belief priority not a number"
    logger.info("✓ Belief priority correctly retrieved")
    
    # Test violation handling retrieval
    violation_handling = get_violation_handling("Belief Conflict")
    assert violation_handling is not None, "Violation handling not found"
    assert "action" in violation_handling, "Violation handling missing action"
    assert "severity" in violation_handling, "Violation handling missing severity"
    logger.info("✓ Violation handling correctly retrieved")
    
    logger.info("Core Beliefs Integration tests passed!\n")

def test_depth_controller():
    """Test the depth controller component."""
    logger.info("Testing Depth Controller...")
    
    # Test depth enrichment
    loop_data = {
        "loop_id": "test_loop_001",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE"
    }
    
    # Test standard depth (default)
    enriched_loop = enrich_loop_with_depth(loop_data)
    assert enriched_loop["depth"] == "standard", f"Unexpected depth: {enriched_loop['depth']}"
    assert "reflection_agents" in enriched_loop, "Missing reflection_agents in enriched loop"
    assert "CRITIC" in enriched_loop["reflection_agents"], "Missing CRITIC agent for standard depth"
    assert "CEO" in enriched_loop["reflection_agents"], "Missing CEO agent for standard depth"
    logger.info("✓ Standard depth correctly applied")
    
    # Test shallow depth
    shallow_loop = enrich_loop_with_depth(loop_data, "shallow")
    assert shallow_loop["depth"] == "shallow", f"Unexpected depth: {shallow_loop['depth']}"
    assert "HAL" in shallow_loop["reflection_agents"], "Missing HAL agent for shallow depth"
    assert "NOVA" in shallow_loop["reflection_agents"], "Missing NOVA agent for shallow depth"
    logger.info("✓ Shallow depth correctly applied")
    
    # Test deep depth
    deep_loop = enrich_loop_with_depth(loop_data, "deep")
    assert deep_loop["depth"] == "deep", f"Unexpected depth: {deep_loop['depth']}"
    assert "SAGE" in deep_loop["reflection_agents"], "Missing SAGE agent for deep depth"
    assert "PESSIMIST" in deep_loop["reflection_agents"], "Missing PESSIMIST agent for deep depth"
    logger.info("✓ Deep depth correctly applied")
    
    # Test depth preloading for rerun
    original_loop = {
        "loop_id": "test_loop_001",
        "depth": "standard"
    }
    
    # Test escalation to deep for alignment issues
    rerun_depth = preload_depth_for_rerun(original_loop, "alignment_threshold_not_met")
    assert rerun_depth == "deep", f"Unexpected rerun depth: {rerun_depth}"
    logger.info("✓ Depth correctly escalated for alignment issues")
    
    # Test maintaining deep depth
    deep_loop = {
        "loop_id": "test_loop_002",
        "depth": "deep"
    }
    rerun_depth = preload_depth_for_rerun(deep_loop, "any_reason")
    assert rerun_depth == "deep", f"Unexpected rerun depth: {rerun_depth}"
    logger.info("✓ Deep depth correctly maintained for reruns")
    
    # Test get_agents_for_depth function
    shallow_agents = get_agents_for_depth("shallow")
    assert "HAL" in shallow_agents, "Missing HAL agent for shallow depth"
    assert "NOVA" in shallow_agents, "Missing NOVA agent for shallow depth"
    
    standard_agents = get_agents_for_depth("standard")
    assert "CRITIC" in standard_agents, "Missing CRITIC agent for standard depth"
    assert "CEO" in standard_agents, "Missing CEO agent for standard depth"
    
    deep_agents = get_agents_for_depth("deep")
    assert "SAGE" in deep_agents, "Missing SAGE agent for deep depth"
    assert "PESSIMIST" in deep_agents, "Missing PESSIMIST agent for deep depth"
    logger.info("✓ Agents correctly retrieved for each depth")
    
    # Test get_reflection_config function
    shallow_config = get_reflection_config("shallow")
    assert "max_reflection_time" in shallow_config, "Missing max_reflection_time in shallow config"
    
    standard_config = get_reflection_config("standard")
    assert "max_reflection_time" in standard_config, "Missing max_reflection_time in standard config"
    
    deep_config = get_reflection_config("deep")
    assert "max_reflection_time" in deep_config, "Missing max_reflection_time in deep config"
    logger.info("✓ Reflection config correctly retrieved for each depth")
    
    # Test get_required_beliefs_for_depth function
    shallow_beliefs = get_required_beliefs_for_depth("shallow")
    assert len(shallow_beliefs) > 0, "No beliefs returned for shallow depth"
    
    standard_beliefs = get_required_beliefs_for_depth("standard")
    assert len(standard_beliefs) > 0, "No beliefs returned for standard depth"
    assert len(standard_beliefs) >= len(shallow_beliefs), "Standard depth should have at least as many beliefs as shallow"
    
    deep_beliefs = get_required_beliefs_for_depth("deep")
    assert len(deep_beliefs) > 0, "No beliefs returned for deep depth"
    assert len(deep_beliefs) >= len(standard_beliefs), "Deep depth should have at least as many beliefs as standard"
    logger.info("✓ Required beliefs correctly retrieved for each depth")
    
    logger.info("Depth Controller tests passed!\n")

def test_agent_permission_validator():
    """Test the agent permission validator component."""
    logger.info("Testing Agent Permission Validator...")
    
    # Test allowed action
    is_allowed, violation, substitute = enforce_agent_permissions("SAGE", "reflect", "test_loop_001")
    assert is_allowed, "SAGE should be allowed to reflect"
    assert violation is None, "No violation should be reported for allowed action"
    logger.info("✓ Allowed action correctly validated")
    
    # Test disallowed action
    is_allowed, violation, substitute = enforce_agent_permissions("NOVA", "identify_bias", "test_loop_001")
    assert not is_allowed, "NOVA should not be allowed to identify_bias"
    assert violation is not None, "Violation should be reported for disallowed action"
    assert violation["agent"] == "NOVA", f"Unexpected agent in violation: {violation['agent']}"
    assert violation["attempted_action"] == "identify_bias", f"Unexpected action in violation: {violation['attempted_action']}"
    assert violation["loop_id"] == "test_loop_001", f"Unexpected loop_id in violation: {violation['loop_id']}"
    assert "timestamp" in violation, "Violation missing timestamp"
    assert "severity" in violation, "Violation missing severity"
    logger.info("✓ Disallowed action correctly rejected with detailed violation")
    
    # Test substitute action
    assert substitute is not None, "Substitute action should be provided"
    assert "action" in substitute, "Substitute missing action"
    assert "reason" in substitute, "Substitute missing reason"
    logger.info("✓ Substitute action correctly provided with reason")
    
    # Test check_permission function directly
    is_allowed = check_permission("CRITIC", "score_summary")
    assert is_allowed, "CRITIC should be allowed to score_summary"
    
    is_allowed = check_permission("HAL", "evaluate_alignment")
    assert not is_allowed, "HAL should not be allowed to evaluate_alignment"
    logger.info("✓ Permission checking function works correctly")
    
    # Test get_substitute_action function directly
    substitute = get_substitute_action("NOVA", "identify_bias")
    assert substitute is not None, "Substitute action should be provided"
    assert "action" in substitute, "Substitute missing action"
    logger.info("✓ Substitute action function works correctly")
    
    logger.info("Agent Permission Validator tests passed!\n")

def test_orchestrator_integration():
    """Test the orchestrator integration component."""
    logger.info("Testing Orchestrator Integration...")
    
    # Test loop validation and preparation
    loop_data = {
        "loop_id": "test_loop_001",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE",
        "plan": [
            {"step": 1, "description": "Analyze requirements"},
            {"step": 2, "description": "Design architecture"},
            {"step": 3, "description": "Implement solution"}
        ],
        "reflection_agent": ["CRITIC", "CEO"]
    }
    
    prepared_loop = integrate_with_orchestrator("test_loop_001", loop_data)
    assert prepared_loop["loop_validation"] == "passed", f"Loop validation failed: {prepared_loop.get('validation_reason')}"
    assert "belief_reference" in prepared_loop, "Belief references not injected"
    assert "depth" in prepared_loop, "Depth not set"
    assert "reflection_agents" in prepared_loop, "Reflection agents not set"
    assert "validation_status" in prepared_loop, "Validation status not set"
    assert "orchestrator_metadata" in prepared_loop, "Orchestrator metadata not set"
    assert "integration_status" in prepared_loop, "Integration status not set"
    logger.info("✓ Loop correctly validated and prepared with metadata")
    
    # Test reflection result processing
    reflection_result = {
        "alignment_score": 0.6,  # Below threshold
        "drift_score": 0.3,      # Above threshold
        "bias_echo": True
    }
    
    processed_loop = process_reflection_with_controls("test_loop_001", loop_data, reflection_result)
    assert processed_loop["belief_conflict"], "Belief conflict not detected"
    assert "belief_conflict_flags" in processed_loop, "Belief conflict flags not set"
    assert "alignment_threshold" in processed_loop["belief_conflict_flags"], "Alignment threshold conflict not detected"
    assert "belief_conflict_details" in processed_loop, "Belief conflict details not set"
    assert "belief_conflict_descriptions" in processed_loop, "Belief conflict descriptions not set"
    assert "belief_conflict_handling" in processed_loop, "Belief conflict handling not set"
    assert "reflection_metadata" in processed_loop, "Reflection metadata not set"
    assert "reflection_processing_status" in processed_loop, "Reflection processing status not set"
    logger.info("✓ Reflection results correctly processed with detailed metadata")
    
    # Test rerun depth determination
    rerun_depth = determine_rerun_depth_with_controls("test_loop_001", loop_data, "alignment_threshold_not_met")
    assert rerun_depth == "deep", f"Unexpected rerun depth: {rerun_depth}"
    assert "depth_determination_history" in loop_data, "Depth determination history not added to loop data"
    assert len(loop_data["depth_determination_history"]) > 0, "Empty depth determination history"
    assert "determined_at" in loop_data["depth_determination_history"][0], "Depth determination missing timestamp"
    assert "reason" in loop_data["depth_determination_history"][0], "Depth determination missing reason"
    logger.info("✓ Rerun depth correctly determined with history tracking")
    
    logger.info("Orchestrator Integration tests passed!\n")

def test_planning_logic_integration():
    """Test the planning logic integration component."""
    logger.info("Testing Planning Logic Integration...")
    
    # Test reflection plan generation
    loop_data = {
        "loop_id": "test_loop_001",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE",
        "depth": "standard"
    }
    
    reflection_plan_result = generate_reflection_plan_with_depth("test_loop_001", loop_data)
    assert "plan" in reflection_plan_result, "Reflection plan result missing plan"
    assert "metadata" in reflection_plan_result, "Reflection plan result missing metadata"
    
    reflection_plan = reflection_plan_result["plan"]
    assert any(step["agent"] == "CRITIC" for step in reflection_plan), "CRITIC missing from reflection plan"
    assert any(step["agent"] == "CEO" for step in reflection_plan), "CEO missing from reflection plan"
    assert not any(step["agent"] == "PESSIMIST" for step in reflection_plan), "PESSIMIST should not be in standard reflection plan"
    
    # Check for enhanced step metadata
    for step in reflection_plan:
        assert "depth" in step, "Step missing depth"
        assert "loop_id" in step, "Step missing loop_id"
        assert "generated_at" in step, "Step missing generated_at timestamp"
        assert "belief_reference" in step, "Step missing belief_reference"
        assert "belief_descriptions" in step, "Step missing belief_descriptions"
    
    # Check plan metadata
    metadata = reflection_plan_result["metadata"]
    assert "generated_at" in metadata, "Metadata missing generated_at"
    assert "depth" in metadata, "Metadata missing depth"
    assert "step_count" in metadata, "Metadata missing step_count"
    assert "agents" in metadata, "Metadata missing agents list"
    logger.info("✓ Standard reflection plan correctly generated with metadata")
    
    # Test deep reflection plan
    deep_loop = {
        "loop_id": "test_loop_002",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE",
        "depth": "deep"
    }
    
    deep_reflection_result = generate_reflection_plan_with_depth("test_loop_002", deep_loop)
    deep_reflection_plan = deep_reflection_result["plan"]
    assert any(step["agent"] == "SAGE" for step in deep_reflection_plan), "SAGE missing from deep reflection plan"
    assert any(step["agent"] == "PESSIMIST" for step in deep_reflection_plan), "PESSIMIST missing from deep reflection plan"
    logger.info("✓ Deep reflection plan correctly generated")
    
    # Test execution plan adjustment
    execution_plan = [
        {"step": 1, "description": "Analyze requirements", "agent": "SAGE"},
        {"step": 2, "description": "Design architecture", "agent": "ARCHITECT"},
        {"step": 3, "description": "Implement solution", "agent": "HAL"}
    ]
    
    adjusted_result = adjust_execution_plan_with_depth("test_loop_001", loop_data, execution_plan)
    assert "plan" in adjusted_result, "Adjusted result missing plan"
    assert "metadata" in adjusted_result, "Adjusted result missing metadata"
    
    adjusted_plan = adjusted_result["plan"]
    assert all("depth" in step for step in adjusted_plan), "Depth not added to execution plan steps"
    assert all(step["depth"] == "standard" for step in adjusted_plan), "Incorrect depth in execution plan steps"
    assert all("loop_id" in step for step in adjusted_plan), "Loop ID not added to execution plan steps"
    assert all("adjusted_at" in step for step in adjusted_plan), "Adjusted timestamp not added to execution plan steps"
    assert all("belief_reference" in step for step in adjusted_plan), "Belief references not added to execution plan steps"
    assert all("belief_descriptions" in step for step in adjusted_plan), "Belief descriptions not added to execution plan steps"
    
    # Check plan metadata
    metadata = adjusted_result["metadata"]
    assert "adjusted_at" in metadata, "Metadata missing adjusted_at"
    assert "depth" in metadata, "Metadata missing depth"
    assert "step_count" in metadata, "Metadata missing step_count"
    assert "belief_count" in metadata, "Metadata missing belief_count"
    logger.info("✓ Execution plan correctly adjusted with metadata")
    
    logger.info("Planning Logic Integration tests passed!\n")

def test_end_to_end_flow():
    """Test the end-to-end flow of the cognitive control layer."""
    logger.info("Testing End-to-End Flow...")
    
    # Create a test loop
    loop_data = {
        "loop_id": "test_loop_001",
        "prompt": "Create a simple todo app",
        "orchestrator_persona": "SAGE",
        "plan": [
            {"step": 1, "description": "Analyze requirements"},
            {"step": 2, "description": "Design architecture"},
            {"step": 3, "description": "Implement solution"}
        ],
        "reflection_agent": ["CRITIC", "CEO"]
    }
    
    # Step 1: Validate and prepare the loop
    prepared_loop = integrate_with_orchestrator("test_loop_001", loop_data)
    assert prepared_loop["loop_validation"] == "passed", f"Loop validation failed: {prepared_loop.get('validation_reason')}"
    assert "orchestrator_metadata" in prepared_loop, "Orchestrator metadata not added"
    logger.info("✓ Step 1: Loop validated and prepared with metadata")
    
    # Step 2: Generate a reflection plan
    reflection_plan_result = generate_reflection_plan_with_depth("test_loop_001", prepared_loop)
    assert "plan" in reflection_plan_result, "Reflection plan result missing plan"
    assert "metadata" in reflection_plan_result, "Reflection plan result missing metadata"
    reflection_plan = reflection_plan_result["plan"]
    assert len(reflection_plan) > 0, "Empty reflection plan generated"
    logger.info("✓ Step 2: Reflection plan generated with metadata")
    
    # Step 3: Dispatch agents according to the plan
    agent_results = []
    violations = []
    
    for step in reflection_plan:
        agent = step["agent"]
        action = step["action"]
        result, step_violations = dispatch_agent("test_loop_001", agent, action)
        agent_results.append(result)
        violations.extend(step_violations)
    
    assert len(agent_results) == len(reflection_plan), "Not all agents were dispatched"
    logger.info("✓ Step 3: Agents dispatched according to plan")
    
    # Step 4: Process reflection results
    reflection_result = {
        "alignment_score": 0.8,
        "drift_score": 0.1,
        "summary_valid": True,
        "agent_results": agent_results
    }
    
    processed_loop = process_reflection_with_controls("test_loop_001", prepared_loop, reflection_result)
    assert not processed_loop.get("belief_conflict", False), "Unexpected belief conflict detected"
    assert "reflection_metadata" in processed_loop, "Reflection metadata not added"
    assert "reflection_processing_status" in processed_loop, "Reflection processing status not added"
    logger.info("✓ Step 4: Reflection results processed with metadata")
    
    # Step 5: Test with a validation failure
    invalid_loop = {
        "loop_id": "test_loop_002",
        "prompt": "",  # Empty prompt
        "orchestrator_persona": "SAGE",
        "plan": [
            {"step": 1, "description": "Analyze requirements"},
            {"step": 2, "description": "Design architecture"},
            {"step": 3, "description": "Implement solution"}
        ],
        "reflection_agent": ["CRITIC", "CEO"]
    }
    
    prepared_invalid_loop = integrate_with_orchestrator("test_loop_002", invalid_loop)
    assert prepared_invalid_loop["loop_validation"] == "failed", "Invalid loop passed validation"
    assert "validation_reason" in prepared_invalid_loop, "Validation reason not provided"
    assert "validation_status" in prepared_invalid_loop, "Validation status not provided"
    assert "missing_components" in prepared_invalid_loop["validation_status"], "Missing components not listed in validation status"
    assert "violation_handling" in prepared_invalid_loop, "Violation handling not provided"
    logger.info("✓ Step 5: Invalid loop correctly rejected with detailed validation status")
    
    # Step 6: Test with a permission violation
    result, step_violations = dispatch_agent("test_loop_001", "NOVA", "identify_bias")
    assert len(step_violations) > 0, "Permission violation not detected"
    assert "timestamp" in step_violations[0], "Violation missing timestamp"
    assert "severity" in step_violations[0], "Violation missing severity"
    logger.info("✓ Step 6: Permission violation correctly detected with detailed violation info")
    
    # Step 7: Test with a belief conflict
    conflict_reflection_result = {
        "alignment_score": 0.6,  # Below threshold
        "drift_score": 0.3,      # Above threshold
        "bias_echo": True
    }
    
    conflict_processed_loop = process_reflection_with_controls("test_loop_001", prepared_loop, conflict_reflection_result)
    assert conflict_processed_loop["belief_conflict"], "Belief conflict not detected"
    assert "belief_conflict_flags" in conflict_processed_loop, "Belief conflict flags not set"
    assert "belief_conflict_details" in conflict_processed_loop, "Belief conflict details not set"
    assert "belief_conflict_descriptions" in conflict_processed_loop, "Belief conflict descriptions not set"
    assert "belief_conflict_handling" in conflict_processed_loop, "Belief conflict handling not set"
    logger.info("✓ Step 7: Belief conflicts correctly detected and handled")
    
    # Step 8: Test rerun depth determination
    rerun_depth = determine_rerun_depth_with_controls("test_loop_001", prepared_loop, "alignment_threshold_not_met")
    assert rerun_depth == "deep", f"Unexpected rerun depth: {rerun_depth}"
    assert "depth_determination_history" in prepared_loop, "Depth determination history not added"
    logger.info("✓ Step 8: Rerun depth correctly determined with history tracking")
    
    logger.info("End-to-End Flow tests passed!\n")

def run_all_tests():
    """Run all tests for the cognitive control layer."""
    logger.info("Running Cognitive Control Layer Tests...\n")
    
    test_loop_validator()
    test_core_beliefs_integration()
    test_depth_controller()
    test_agent_permission_validator()
    test_orchestrator_integration()
    test_planning_logic_integration()
    test_end_to_end_flow()
    
    logger.info("\nAll Cognitive Control Layer tests passed!")

if __name__ == "__main__":
    run_all_tests()

if __name__ == "__main__":
    run_all_tests()
