"""
Drift Monitor Module

This module provides functionality for detecting and monitoring drift
in loop outputs, agent behaviors, or schema versions.
"""

import logging
import hashlib
import json
import difflib
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Import memory operations
try:
    from app.modules.memory_writer import write_memory, read_memory
    memory_available = True
except ImportError:
    memory_available = False
    logging.warning("⚠️ Could not import memory operations, using mock implementations")
    # Mock implementations for testing
    async def write_memory(project_id, tag, value):
        return {"status": "success", "message": "Mock write successful"}
    
    async def read_memory(project_id, tag):
        return None

# Import schema integrity utilities if available
try:
    from app.utils.schema_integrity import get_schema_checksum
    schema_validation_available = True
except ImportError:
    schema_validation_available = False
    logging.warning("⚠️ Schema validation not available, using basic validation")
    
    def get_schema_checksum(obj):
        """Simple fallback checksum function"""
        if isinstance(obj, dict):
            obj_str = json.dumps(obj, sort_keys=True)
        else:
            obj_str = str(obj)
        return hashlib.sha256(obj_str.encode()).hexdigest()

# Configure logging
logger = logging.getLogger("app.modules.drift_monitor")

async def detect_loop_drift(
    previous_output: Any, 
    current_output: Any
) -> Tuple[float, str, str, str]:
    """
    Detect drift between previous and current outputs.
    
    Args:
        previous_output: The previous output to compare against
        current_output: The current output to check for drift
        
    Returns:
        Tuple containing:
        - drift_score: A float between 0 and 1 indicating the amount of drift
        - explanation: A string explaining the drift detection
        - previous_checksum: Checksum of the previous output
        - current_checksum: Checksum of the current output
    """
    try:
        # Generate checksums
        if isinstance(previous_output, dict) and isinstance(current_output, dict):
            # Convert to JSON strings for comparison
            previous_json = json.dumps(previous_output, sort_keys=True, indent=2)
            current_json = json.dumps(current_output, sort_keys=True, indent=2)
            
            # Generate checksums
            previous_checksum = hashlib.sha256(previous_json.encode()).hexdigest()
            current_checksum = hashlib.sha256(current_json.encode()).hexdigest()
            
            # If checksums match exactly, no drift
            if previous_checksum == current_checksum:
                return 0.0, "Outputs are identical", previous_checksum, current_checksum
            
            # Calculate similarity using difflib
            similarity = difflib.SequenceMatcher(None, previous_json, current_json).ratio()
            drift_score = 1.0 - similarity
            
            # Generate explanation
            if drift_score < 0.1:
                explanation = "Minor differences detected, likely formatting or non-essential fields"
            elif drift_score < 0.3:
                explanation = "Moderate changes detected in output content"
            elif drift_score < 0.6:
                explanation = "Significant changes detected in output structure and content"
            else:
                explanation = "Major divergence detected, outputs are substantially different"
            
            # Add diff details for significant drift
            if drift_score > 0.2:
                diff = difflib.unified_diff(
                    previous_json.splitlines(),
                    current_json.splitlines(),
                    lineterm='',
                    n=3
                )
                diff_text = '\n'.join(list(diff)[:20])  # Limit diff size
                explanation += f"\n\nKey differences:\n{diff_text}"
            
            return drift_score, explanation, previous_checksum, current_checksum
        
        else:
            # Handle non-dict objects
            previous_str = str(previous_output)
            current_str = str(current_output)
            
            # Generate checksums
            previous_checksum = hashlib.sha256(previous_str.encode()).hexdigest()
            current_checksum = hashlib.sha256(current_str.encode()).hexdigest()
            
            # If checksums match exactly, no drift
            if previous_checksum == current_checksum:
                return 0.0, "Outputs are identical", previous_checksum, current_checksum
            
            # Calculate similarity using difflib
            similarity = difflib.SequenceMatcher(None, previous_str, current_str).ratio()
            drift_score = 1.0 - similarity
            
            # Generate explanation
            if drift_score < 0.1:
                explanation = "Minor differences detected in text output"
            elif drift_score < 0.3:
                explanation = "Moderate changes detected in text output"
            elif drift_score < 0.6:
                explanation = "Significant changes detected in text output"
            else:
                explanation = "Major divergence detected in text output"
            
            return drift_score, explanation, previous_checksum, current_checksum
    
    except Exception as e:
        logger.error(f"❌ Error detecting drift: {str(e)}")
        # Generate fallback checksums
        previous_checksum = hashlib.sha256(str(previous_output).encode()).hexdigest()
        current_checksum = hashlib.sha256(str(current_output).encode()).hexdigest()
        return 1.0, f"Error detecting drift: {str(e)}", previous_checksum, current_checksum

async def log_drift(
    loop_id: str,
    agent: str,
    previous_checksum: str,
    current_checksum: str,
    drift_score: float,
    drift_detected: bool,
    explanation: str,
    snapshot_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Log drift detection results to memory.
    
    Args:
        loop_id: Unique identifier for the loop
        agent: Agent that produced the output
        previous_checksum: Checksum of the previous output
        current_checksum: Checksum of the current output
        drift_score: Quantified measure of drift
        drift_detected: Whether drift was detected
        explanation: Explanation of the drift detection
        snapshot_id: Reference snapshot ID for comparison
        
    Returns:
        Dictionary containing the result of the memory write operation
    """
    try:
        # Create drift log
        drift_log = {
            "loop_id": loop_id,
            "agent": agent,
            "snapshot_id": snapshot_id,
            "previous_checksum": previous_checksum,
            "current_checksum": current_checksum,
            "drift_detected": drift_detected,
            "drift_score": drift_score,
            "explanation": explanation,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Write to memory
        memory_tag = f"loop_drift_log_{loop_id}_{agent}"
        result = await write_memory(loop_id, memory_tag, drift_log)
        
        # Log the operation
        if result and result.get("status") == "success":
            logger.info(f"✅ Drift log written for loop {loop_id}, agent {agent}")
            return {"status": "success", "drift_log": drift_log}
        else:
            logger.error(f"❌ Failed to write drift log for loop {loop_id}: {result}")
            return {"status": "error", "message": f"Failed to write drift log: {result}"}
    
    except Exception as e:
        logger.error(f"❌ Error logging drift: {str(e)}")
        return {"status": "error", "message": f"Error logging drift: {str(e)}"}

async def get_previous_output(
    loop_id: str,
    current_output_tag: str,
    previous_output_tag: Optional[str] = None,
    snapshot_id: Optional[str] = None
) -> Tuple[Any, str]:
    """
    Get the previous output for comparison.
    
    Args:
        loop_id: Unique identifier for the loop
        current_output_tag: Memory tag where the current output is stored
        previous_output_tag: Memory tag where the previous output is stored
        snapshot_id: Reference snapshot ID for comparison
        
    Returns:
        Tuple containing:
        - previous_output: The previous output to compare against
        - source: The source of the previous output (tag or snapshot)
    """
    try:
        # Try to get from previous output tag if provided
        if previous_output_tag:
            previous_output = await read_memory(loop_id, previous_output_tag)
            if previous_output:
                return previous_output, f"tag:{previous_output_tag}"
        
        # Try to get from snapshot if provided
        if snapshot_id:
            try:
                from app.utils.snapshot_manager import load_snapshot
                snapshot = await load_snapshot(loop_id)
                if snapshot and snapshot.memory_state:
                    # Look for the same tag in the snapshot
                    previous_output = snapshot.memory_state.get(current_output_tag)
                    if previous_output:
                        return previous_output, f"snapshot:{snapshot_id}"
            except ImportError:
                logger.warning("⚠️ Snapshot manager not available, cannot load from snapshot")
        
        # Try to get from historical logs
        historical_tag = f"{current_output_tag}_history"
        history = await read_memory(loop_id, historical_tag)
        if history and isinstance(history, list) and len(history) > 0:
            return history[-1], f"history:{historical_tag}"
        
        # No previous output found
        return None, "none"
    
    except Exception as e:
        logger.error(f"❌ Error getting previous output: {str(e)}")
        return None, f"error:{str(e)}"

async def determine_recommended_action(
    drift_score: float,
    threshold: float,
    agent: str
) -> str:
    """
    Determine the recommended action based on drift score.
    
    Args:
        drift_score: Quantified measure of drift
        threshold: Threshold for drift detection
        agent: Agent that produced the output
        
    Returns:
        String containing the recommended action
    """
    if drift_score <= threshold:
        return "continue"
    
    if drift_score <= threshold * 1.5:
        return "log_warning"
    
    if drift_score <= threshold * 2.5:
        return "trigger_critic_review"
    
    return "rewind_and_retry"
