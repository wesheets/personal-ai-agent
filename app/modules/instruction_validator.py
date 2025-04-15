"""
Instruction validator module for validating agent outputs against expected outputs.

This module provides functionality to validate whether an agent's memory includes
all expected outputs and checkpoints specified in an instruction.
"""

from src.utils.debug_logger import log_test_result
from typing import List, Dict, Any, Optional
import json

# This would be replaced with actual implementation
# For now, we'll simulate memory extraction
def extract_outputs_from_memory(agent_id: str) -> List[Dict[str, Any]]:
    """
    Extract outputs from agent memory.
    
    Args:
        agent_id: The ID of the agent
        
    Returns:
        List of memory entries containing outputs
    """
    # Simulate memory extraction - this would be replaced with actual implementation
    # that queries the memory store for the agent's outputs
    
    # For HAL agent, return outputs including task.output
    if agent_id.lower() == "hal":
        return [
            {
                "type": "output",
                "content": "login.route implementation",
                "tags": ["output", "login.route"]
            },
            {
                "type": "output",
                "content": "login.handler implementation",
                "tags": ["output", "login.handler"]
            },
            {
                "type": "output",
                "content": "def capitalize_words(s): return ' '.join(word.capitalize() for word in s.split())",
                "tags": ["output", "task.output"]
            },
            {
                "type": "reflection",
                "content": "I've implemented the login route and handler according to best practices",
                "tags": ["reflection"]
            }
        ]
    
    # For ASH agent, return outputs including summary.task.output and reflection
    elif agent_id.lower() == "ash":
        return [
            {
                "type": "output",
                "content": "This function capitalizes each word by splitting the string and applying capitalize() to each word.",
                "tags": ["output", "summary.task.output"]
            },
            {
                "type": "reflection",
                "content": "HAL's implementation is correct.",
                "tags": ["reflection"]
            }
        ]
    
    # For NOVA agent, return outputs including ui.preview and reflection
    elif agent_id.lower() == "nova":
        return [
            {
                "type": "output",
                "content": "<div class='result'>\n  <h3>Reversed Words</h3>\n  <ul>\n    <li>world (5)</li>\n    <li>hello (5)</li>\n  </ul>\n</div>",
                "tags": ["output", "ui.preview"]
            },
            {
                "type": "reflection",
                "content": "Generated a UI preview that matches HAL's result.",
                "tags": ["reflection"]
            }
        ]
    
    # For other agents, return empty list
    return []

def validate_instruction_outputs(
    agent_id: str,
    expected_outputs: List[str],
    checkpoints: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Validate whether agent memory includes all expected outputs and checkpoints.
    
    Args:
        agent_id: The ID of the agent
        expected_outputs: List of expected output identifiers
        checkpoints: Optional list of checkpoint identifiers
        
    Returns:
        Dict with validation status and details
    """
    if checkpoints is None:
        checkpoints = []
    
    # Extract outputs from agent memory
    memory_entries = extract_outputs_from_memory(agent_id)
    
    # Track which outputs and checkpoints are found
    found_outputs = []
    missing_outputs = []
    found_checkpoints = []
    missing_checkpoints = []
    
    # Check for expected outputs
    for output in expected_outputs:
        output_found = False
        for entry in memory_entries:
            if output in entry.get("tags", []) or output in entry.get("content", ""):
                output_found = True
                found_outputs.append(output)
                break
        
        if not output_found:
            missing_outputs.append(output)
    
    # Check for checkpoints
    for checkpoint in checkpoints:
        checkpoint_found = False
        for entry in memory_entries:
            if checkpoint in entry.get("tags", []) or checkpoint in entry.get("content", ""):
                checkpoint_found = True
                found_checkpoints.append(checkpoint)
                break
        
        if not checkpoint_found:
            missing_checkpoints.append(checkpoint)
    
    # Determine overall status
    if not missing_outputs and not missing_checkpoints:
        status = "complete"
        details = f"All {len(expected_outputs)} outputs and {len(checkpoints)} checkpoints found"
        
        log_test_result(
            "Validator", 
            "/api/modules/instruction_validator", 
            "PASS", 
            f"Validation complete for agent {agent_id}", 
            details
        )
    else:
        status = "failed"
        details = f"Missing outputs: {missing_outputs}, Missing checkpoints: {missing_checkpoints}"
        
        log_test_result(
            "Validator", 
            "/api/modules/instruction_validator", 
            "FAIL", 
            f"Validation failed for agent {agent_id}", 
            details
        )
    
    # Return validation result
    return {
        "status": status,
        "details": details,
        "found_outputs": found_outputs,
        "missing_outputs": missing_outputs,
        "found_checkpoints": found_checkpoints,
        "missing_checkpoints": missing_checkpoints
    }
