"""
Schema Validation Test Module

This module provides test cases for validating the schema validation implementation
for Phase 2 of the Schema Compliance initiative.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import schema validation modules
from modules.schema_validation import validate_schema
from implementation.visual_settings_validator import validate_visual_settings, get_validated_settings_for_mode
from implementation.md_export_validator import validate_md_export, create_md_export
from implementation.html_export_validator import validate_html_export, create_html_export
from implementation.rerun_decision import RerunDecision

# Configure logging
logging.basicConfig(
    filename='/debug/schema_trace.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('schema_validation_test')

def run_all_tests():
    """Run all schema validation tests and return results"""
    results = {
        "test_run_timestamp": datetime.utcnow().isoformat(),
        "tests": {},
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    # Test visual settings validation
    results["tests"]["visual_settings"] = test_visual_settings_validation()
    
    # Test RerunDecision validation
    results["tests"]["rerun_decision"] = test_rerun_decision_validation()
    
    # Test MD export validation
    results["tests"]["md_export"] = test_md_export_validation()
    
    # Test HTML export validation
    results["tests"]["html_export"] = test_html_export_validation()
    
    # Test loop map visualization validation
    results["tests"]["loop_map_visualization"] = test_loop_map_visualization()
    
    # Test loop lineage export validation
    results["tests"]["loop_lineage_export"] = test_loop_lineage_export()
    
    # Calculate summary
    for test_name, test_result in results["tests"].items():
        results["summary"]["total"] += 1
        if test_result["status"] == "passed":
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    
    # Save results to file
    output_dir = "/home/ubuntu/schema_compliance_phase2/test_results"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, "validation_test_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    return results

def test_visual_settings_validation():
    """Test visual settings validation"""
    logger.info("Testing visual settings validation")
    
    # Test case 1: Valid settings for balanced mode
    balanced_settings = get_validated_settings_for_mode("balanced")
    is_valid_balanced, validated_balanced, _ = validate_visual_settings(balanced_settings, "balanced")
    
    # Test case 2: Valid settings for thorough mode
    thorough_settings = get_validated_settings_for_mode("thorough")
    is_valid_thorough, validated_thorough, _ = validate_visual_settings(thorough_settings, "thorough")
    
    # Test case 3: Invalid settings (missing required field)
    invalid_settings = {
        "detail_level": "minimal",
        # Missing node_types_to_show
        "edge_types_to_show": ["execution", "rerun"],
        "include_timestamps": False,
        "include_memory_details": False,
        "include_agent_details": False,
        "include_decision_details": False,
        "update_frequency": "end_only"
    }
    is_valid_invalid, validated_invalid, error_invalid = validate_visual_settings(invalid_settings)
    
    # Check results
    all_passed = is_valid_balanced and is_valid_thorough and not is_valid_invalid
    
    return {
        "status": "passed" if all_passed else "failed",
        "details": {
            "balanced_mode": {
                "is_valid": is_valid_balanced,
                "has_validation_metadata": "schema_validated" in validated_balanced
            },
            "thorough_mode": {
                "is_valid": is_valid_thorough,
                "has_validation_metadata": "schema_validated" in validated_thorough
            },
            "invalid_settings": {
                "is_valid": is_valid_invalid,
                "error": error_invalid
            }
        }
    }

def test_rerun_decision_validation():
    """Test RerunDecision validation"""
    logger.info("Testing RerunDecision validation")
    
    # Test case 1: Valid rerun decision
    valid_decision_data = {
        "decision": "rerun",
        "loop_id": "loop-123",
        "original_loop_id": "loop-122",
        "new_loop_id": "loop-124",
        "rerun_reason": "alignment_score_low",
        "rerun_number": 1,
        "reason": "The alignment score was below threshold",
        "orchestrator_persona": "SAGE",
        "rerun_limit_reached": False,
        "bias_echo_detected": False,
        "fatigue_threshold_exceeded": False,
        "force_finalized": False,
        "rerun_trigger": ["alignment_monitor"],
        "alignment_score": 0.65,
        "drift_score": 0.2,
        "depth": "standard"
    }
    
    try:
        valid_decision = RerunDecision(**valid_decision_data)
        valid_decision_dict = valid_decision.dict()
        valid_decision_json = valid_decision.json()
        valid_decision_validated = RerunDecision.validate_decision_data(valid_decision_data)
        
        valid_test_passed = (
            valid_decision_dict["schema_validated"] and
            "validation_timestamp" in valid_decision_dict and
            "schema_validated" in valid_decision_validated
        )
    except Exception as e:
        logger.error(f"Error in valid RerunDecision test: {str(e)}")
        valid_test_passed = False
    
    # Test case 2: Invalid rerun decision (missing required field)
    invalid_decision_data = {
        "decision": "rerun",
        # Missing loop_id
        "original_loop_id": "loop-122",
        "new_loop_id": "loop-124",
        "rerun_reason": "alignment_score_low",
        "rerun_number": 1
    }
    
    try:
        invalid_test_passed = False
        RerunDecision(**invalid_decision_data)
    except Exception:
        # Should raise an exception
        invalid_test_passed = True
    
    # Test case 3: Invalid decision value
    invalid_value_data = {
        "decision": "retry",  # Invalid value, should be 'rerun' or 'finalize'
        "loop_id": "loop-123",
        "original_loop_id": "loop-122",
        "new_loop_id": "loop-124"
    }
    
    try:
        invalid_value_test_passed = False
        RerunDecision(**invalid_value_data)
    except Exception:
        # Should raise an exception
        invalid_value_test_passed = True
    
    # Check results
    all_passed = valid_test_passed and invalid_test_passed and invalid_value_test_passed
    
    return {
        "status": "passed" if all_passed else "failed",
        "details": {
            "valid_decision": {
                "passed": valid_test_passed,
                "has_validation_metadata": valid_test_passed and "schema_validated" in valid_decision_dict
            },
            "invalid_decision": {
                "passed": invalid_test_passed
            },
            "invalid_value": {
                "passed": invalid_value_test_passed
            }
        }
    }

def test_md_export_validation():
    """Test MD export validation"""
    logger.info("Testing MD export validation")
    
    # Test case 1: Valid MD export
    valid_md_content = """# Loop Summary

This is a summary of loop execution.

## Agents Involved
- Agent 1
- Agent 2

## Decisions
1. Decision 1
2. Decision 2
"""
    
    valid_md_metadata = {
        "export_timestamp": datetime.utcnow().isoformat(),
        "format_version": "1.0",
        "export_type": "loop_summary"
    }
    
    is_valid_md, validated_md, _ = create_md_export("loop-123", valid_md_content, valid_md_metadata)
    
    # Test case 2: Invalid MD export (wrong format)
    invalid_md_export = {
        "format": "text",  # Should be 'markdown'
        "loop_id": "loop-123",
        "content": valid_md_content,
        "metadata": valid_md_metadata
    }
    
    is_valid_invalid_md, _, error_invalid_md = validate_md_export(invalid_md_export)
    
    # Check results
    all_passed = is_valid_md and not is_valid_invalid_md
    
    return {
        "status": "passed" if all_passed else "failed",
        "details": {
            "valid_md_export": {
                "is_valid": is_valid_md,
                "has_validation_metadata": "schema_validated" in validated_md
            },
            "invalid_md_export": {
                "is_valid": is_valid_invalid_md,
                "error": error_invalid_md
            }
        }
    }

def test_html_export_validation():
    """Test HTML export validation"""
    logger.info("Testing HTML export validation")
    
    # Test case 1: Valid HTML export
    valid_html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Loop Summary</title>
</head>
<body>
    <h1>Loop Summary</h1>
    <p>This is a summary of loop execution.</p>
    
    <h2>Agents Involved</h2>
    <ul>
        <li>Agent 1</li>
        <li>Agent 2</li>
    </ul>
    
    <h2>Decisions</h2>
    <ol>
        <li>Decision 1</li>
        <li>Decision 2</li>
    </ol>
</body>
</html>
"""
    
    valid_html_metadata = {
        "export_timestamp": datetime.utcnow().isoformat(),
        "format_version": "1.0",
        "export_type": "loop_summary"
    }
    
    is_valid_html, validated_html, _ = create_html_export("loop-123", valid_html_content, valid_html_metadata, "loop_summary")
    
    # Test case 2: Invalid HTML export (wrong format)
    invalid_html_export = {
        "format": "xml",  # Should be 'html'
        "loop_id": "loop-123",
        "content": valid_html_content,
        "metadata": valid_html_metadata
    }
    
    is_valid_invalid_html, _, error_invalid_html = validate_html_export(invalid_html_export)
    
    # Check results
    all_passed = is_valid_html and not is_valid_invalid_html
    
    return {
        "status": "passed" if all_passed else "failed",
        "details": {
            "valid_html_export": {
                "is_valid": is_valid_html,
                "has_validation_metadata": "schema_validated" in validated_html
            },
            "invalid_html_export": {
                "is_valid": is_valid_invalid_html,
                "error": error_invalid_html
            }
        }
    }

def test_loop_map_visualization():
    """Test loop map visualization validation"""
    logger.info("Testing loop map visualization validation")
    
    # Test case: Valid loop map visualization
    valid_loop_map = {
        "metadata": {
            "loop_id": "loop-123",
            "mode": "balanced",
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0"
        },
        "nodes": [
            {
                "id": "loop_start_loop-123",
                "type": "loop_start",
                "label": "Loop loop-123 Start",
                "data": {
                    "loop_id": "loop-123",
                    "timestamp": datetime.utcnow().isoformat(),
                    "loop_count": 1,
                    "mode": "balanced"
                }
            },
            {
                "id": "agent_memory-agent_2025-04-22T02:50:00Z",
                "type": "agent",
                "label": "Agent: memory-agent",
                "data": {
                    "agent_name": "memory-agent",
                    "timestamp": "2025-04-22T02:50:00Z",
                    "status": "completed",
                    "mode": "balanced"
                }
            }
        ],
        "edges": [
            {
                "source": "loop_start_loop-123",
                "target": "agent_memory-agent_2025-04-22T02:50:00Z",
                "type": "execution",
                "label": "Executes",
                "data": {
                    "timestamp": "2025-04-22T02:50:00Z"
                }
            }
        ],
        "settings": {
            "detail_level": "standard",
            "node_types_to_show": [
                "agent", "memory", "decision", "reflection", 
                "loop_start", "loop_end", "rerun", "mode_change", "depth_change"
            ],
            "edge_types_to_show": [
                "execution", "memory_access", "decision", "reflection", 
                "rerun", "mode_transition", "depth_transition"
            ],
            "include_timestamps": True,
            "include_memory_details": True,
            "include_agent_details": True,
            "include_decision_details": True,
            "update_frequency": "agent_completion"
        }
    }
    
    is_valid_loop_map, error_loop_map = validate_schema(valid_loop_map, 'loop_map_visualization')
    
    return {
        "status": "passed" if is_valid_loop_map else "failed",
        "details": {
            "is_valid": is_valid_loop_map,
            "error": error_loop_map
        }
    }

def test_loop_lineage_export():
    """Test loop lineage export validation"""
    logger.info("Testing loop lineage export validation")
    
    # Test case: Valid loop lineage export
    valid_lineage_export = {
        "loop_id": "loop-123",
        "export_format": "json",
        "timestamp": datetime.utcnow().isoformat(),
        "lineage": {
            "original_loop_id": "loop-120",
            "rerun_chain": ["loop-120", "loop-121", "loop-122", "loop-123"],
            "rerun_reasons": [
                "alignment_score_low",
                "drift_score_high",
                "belief_conflict"
            ],
            "total_reruns": 3
        },
        "summary": {
            "initial_goal": "Analyze data",
            "final_outcome": "Data analyzed successfully",
            "improvement_metrics": {
                "alignment_score": [0.65, 0.75, 0.85, 0.95],
                "drift_score": [0.35, 0.25, 0.15, 0.05]
            }
        },
        "metadata": {
            "export_version": "1.0",
            "generated_by": "loop_lineage_export_system"
        }
    }
    
    is_valid_lineage, error_lineage = validate_schema(valid_lineage_export, 'loop_lineage_export')
    
    return {
        "status": "passed" if is_valid_lineage else "failed",
        "details": {
            "is_valid": is_valid_lineage,
            "error": error_lineage
        }
    }

if __name__ == "__main__":
    results = run_all_tests()
    
    # Print summary
    print(f"Tests completed: {results['summary']['passed']}/{results['summary']['total']} passed")
    
    for test_name, test_result in results["tests"].items():
        status = "✅" if test_result["status"] == "passed" else "❌"
        print(f"{status} {test_name}")
    
    # Exit with appropriate code
    sys.exit(0 if results["summary"]["failed"] == 0 else 1)
