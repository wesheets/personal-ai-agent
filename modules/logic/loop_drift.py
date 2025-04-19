"""
Loop Drift Detection Module
This function detects potential loop regression or stagnation patterns
as part of the Cognitive Paradox Protocol.
"""

import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger("modules.logic.loop_drift")

def detect_loop_drift(project_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect potential loop regression or stagnation patterns.
    
    Args:
        project_state: The current project state
            
    Returns:
        Dict containing the detection results, including:
        - reflection_recommended: Boolean indicating if reflection is recommended
        - reason: String with the reason for the recommendation
    """
    try:
        # Extract relevant metrics from project state
        loop_count = project_state.get("loop_count", 0)
        last_agent = project_state.get("last_completed_agent", "")
        completed_steps = project_state.get("completed_steps", [])
        
        # Check for potential loop regression or stagnation
        if loop_count > 6 or (last_agent and completed_steps.count(last_agent) > 2):
            logger.warning(f"Loop drift detected: loop_count={loop_count}, repeated_agent={last_agent} ({completed_steps.count(last_agent)} times)")
            print(f"⚠️ Loop drift detected: loop_count={loop_count}, repeated_agent={last_agent} ({completed_steps.count(last_agent)} times)")
            
            return {
                "reflection_recommended": True,
                "reason": "Agent has re-run multiple times or loop count is unusually high."
            }
        
        # No drift detected
        logger.info(f"No loop drift detected: loop_count={loop_count}, last_agent={last_agent}")
        print(f"✅ No loop drift detected: loop_count={loop_count}, last_agent={last_agent}")
        
        return {
            "reflection_recommended": False
        }
        
    except Exception as e:
        error_msg = f"Error detecting loop drift: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        # Return a safe default result
        return {
            "reflection_recommended": False,
            "error": str(e)
        }
