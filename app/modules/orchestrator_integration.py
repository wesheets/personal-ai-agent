"""
Orchestrator Integration Module

This module integrates the loop validator, core beliefs, and depth controller
into the orchestrator to ensure loops meet minimum requirements.

The orchestrator integration serves as the central coordination point for the
cognitive control layer, ensuring all components work together seamlessly.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from app.modules.loop_validator import validate_loop, validate_and_enrich_loop
from app.modules.core_beliefs_integration import (
    inject_belief_references, 
    check_belief_conflicts,
    get_belief_description,
    get_belief_priority,
    get_violation_handling
)
from app.modules.depth_controller import enrich_loop_with_depth, preload_depth_for_rerun
from app.modules.agent_dispatch import create_dispatcher
from app.modules.agent_permission_validator import enforce_agent_permissions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorIntegration:
    """
    Class for integrating cognitive control components into the orchestrator.
    
    This class serves as the central coordination point for all cognitive control
    components, ensuring they work together seamlessly to enforce the system's
    core beliefs and operational thresholds.
    """
    
    def __init__(self, loop_id: str):
        """
        Initialize the orchestrator integration.
        
        Args:
            loop_id: The ID of the current loop
        """
        self.loop_id = loop_id
        self.agent_dispatcher = create_dispatcher(loop_id)
        self.validation_results = {}
        self.integration_metadata = {
            "initialized_at": datetime.utcnow().isoformat(),
            "loop_id": loop_id,
            "version": "1.0"
        }
        logger.info(f"Initialized OrchestratorIntegration for loop {loop_id}")
    
    def validate_and_prepare_loop(self, loop_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate and prepare a loop for execution, applying all cognitive controls.
        
        Args:
            loop_data: The loop data to validate and prepare
            
        Returns:
            Tuple containing:
            - Boolean indicating whether validation passed
            - Optional string with reason for failure
            - Dictionary with prepared loop data
        """
        logger.info(f"Validating and preparing loop {self.loop_id}")
        
        # Add validation timestamp
        loop_data["validation_timestamp"] = datetime.utcnow().isoformat()
        
        # Step 1: Validate loop against core requirements
        try:
            is_valid, reason, validation_result = validate_loop(loop_data)
            self.validation_results = validation_result
            
            if not is_valid:
                # Loop validation failed
                logger.warning(f"Loop {self.loop_id} validation failed: {reason}")
                loop_data["loop_validation"] = "failed"
                loop_data["validation_reason"] = reason
                loop_data["validation_status"] = {
                    "status": "failed",
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                    "checked_components": validation_result.get("checked_components", []),
                    "missing_components": validation_result.get("missing_components", [])
                }
                
                # Get handling instructions for missing components
                violation_type = "Missing Required Component"
                handling = get_violation_handling(violation_type)
                loop_data["violation_handling"] = handling
                
                return False, reason, loop_data
            
            logger.info(f"Loop {self.loop_id} passed basic validation")
            
            # Step 2: Enrich with depth information
            loop_data = enrich_loop_with_depth(loop_data)
            logger.debug(f"Loop {self.loop_id} enriched with depth: {loop_data.get('depth', 'standard')}")
            
            # Step 3: Inject belief references
            loop_data = inject_belief_references(loop_data)
            belief_count = len(loop_data.get("belief_reference", []))
            logger.debug(f"Loop {self.loop_id} injected with {belief_count} belief references")
            
            # Step 4: Add validation results
            loop_data["loop_validation"] = "passed"
            loop_data["validation_status"] = {
                "status": "passed",
                "timestamp": datetime.utcnow().isoformat(),
                "checked_components": validation_result.get("checked_components", []),
                "depth": loop_data.get("depth", "standard"),
                "belief_count": belief_count
            }
            
            # Step 5: Add orchestrator metadata
            loop_data["orchestrator_metadata"] = {
                "processed_by": "cognitive_control_layer",
                "processed_at": datetime.utcnow().isoformat(),
                "loop_id": self.loop_id,
                "validation_version": "1.0"
            }
            
            logger.info(f"Loop {self.loop_id} successfully prepared with cognitive controls")
            return True, None, loop_data
            
        except Exception as e:
            logger.error(f"Error during loop validation and preparation: {str(e)}")
            loop_data["loop_validation"] = "error"
            loop_data["validation_error"] = str(e)
            return False, f"Validation error: {str(e)}", loop_data
    
    def process_reflection_result(self, loop_data: Dict[str, Any], reflection_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process reflection results, checking for belief conflicts and updating loop data.
        
        Args:
            loop_data: The loop data
            reflection_result: The reflection result
            
        Returns:
            Updated loop data with belief conflict information
        """
        logger.info(f"Processing reflection results for loop {self.loop_id}")
        
        try:
            # Add processing timestamp
            loop_data["reflection_processed_at"] = datetime.utcnow().isoformat()
            
            # Check for belief conflicts
            conflicts, conflict_details = check_belief_conflicts(loop_data, reflection_result)
            
            # Update loop data with conflict information
            if conflicts:
                logger.warning(f"Found {len(conflicts)} belief conflicts in loop {self.loop_id}")
                loop_data["belief_conflict"] = True
                loop_data["belief_conflict_flags"] = conflicts
                loop_data["belief_conflict_details"] = conflict_details
                
                # Add descriptions for each conflicting belief
                loop_data["belief_conflict_descriptions"] = {}
                for belief in conflicts:
                    loop_data["belief_conflict_descriptions"][belief] = get_belief_description(belief)
                    priority = get_belief_priority(belief)
                    loop_data["belief_conflict_descriptions"][f"{belief}_priority"] = priority
                
                # Get handling instructions for belief conflicts
                violation_type = "Belief Conflict"
                handling = get_violation_handling(violation_type)
                loop_data["belief_conflict_handling"] = handling
            else:
                logger.info(f"No belief conflicts found in loop {self.loop_id}")
                loop_data["belief_conflict"] = False
            
            # Add agent violations from dispatcher
            violations = self.agent_dispatcher.get_violations()
            if violations:
                logger.warning(f"Found {len(violations)} agent permission violations in loop {self.loop_id}")
                loop_data["agent_violations"] = violations
                loop_data["permission_violation"] = True
                
                # Get handling instructions for permission violations
                violation_type = "Agent Permission Violation"
                handling = get_violation_handling(violation_type)
                loop_data["permission_violation_handling"] = handling
            else:
                loop_data["permission_violation"] = False
            
            # Add reflection metadata
            loop_data["reflection_metadata"] = {
                "processed_by": "cognitive_control_layer",
                "processed_at": datetime.utcnow().isoformat(),
                "loop_id": self.loop_id,
                "has_conflicts": bool(conflicts),
                "has_violations": bool(violations),
                "severity": conflict_details.get("severity", "none") if conflicts else "none"
            }
            
            logger.info(f"Reflection processing completed for loop {self.loop_id}")
            return loop_data
            
        except Exception as e:
            logger.error(f"Error during reflection processing: {str(e)}")
            loop_data["reflection_processing_error"] = str(e)
            return loop_data
    
    def determine_rerun_depth(self, loop_data: Dict[str, Any], rerun_reason: str) -> str:
        """
        Determine the appropriate depth for a loop rerun.
        
        Args:
            loop_data: The original loop data
            rerun_reason: The reason for the rerun
            
        Returns:
            Appropriate depth level for the rerun
        """
        logger.info(f"Determining rerun depth for loop {self.loop_id} with reason: {rerun_reason}")
        
        try:
            # Get the appropriate depth from the depth controller
            new_depth = preload_depth_for_rerun(loop_data, rerun_reason)
            
            # Log the depth change if applicable
            original_depth = loop_data.get("depth", "standard")
            if new_depth != original_depth:
                logger.info(f"Depth escalation for loop {self.loop_id}: {original_depth} -> {new_depth} due to {rerun_reason}")
            else:
                logger.debug(f"Maintaining depth {new_depth} for loop {self.loop_id} rerun")
            
            # Add rerun metadata
            if "rerun_metadata" not in loop_data:
                loop_data["rerun_metadata"] = []
            
            loop_data["rerun_metadata"].append({
                "rerun_reason": rerun_reason,
                "original_depth": original_depth,
                "new_depth": new_depth,
                "determined_at": datetime.utcnow().isoformat(),
                "escalated": new_depth != original_depth
            })
            
            return new_depth
            
        except Exception as e:
            logger.error(f"Error determining rerun depth: {str(e)}")
            # Default to deep depth on error to be safe
            return "deep"

def integrate_with_orchestrator(loop_id: str, loop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integrate cognitive control components with the orchestrator for a specific loop.
    
    Args:
        loop_id: The ID of the loop
        loop_data: The loop data
        
    Returns:
        Prepared loop data with all cognitive controls applied
    """
    logger.info(f"Integrating cognitive control layer with orchestrator for loop {loop_id}")
    
    try:
        integration = OrchestratorIntegration(loop_id)
        is_valid, reason, prepared_data = integration.validate_and_prepare_loop(loop_data)
        
        if not is_valid:
            logger.warning(f"Loop {loop_id} validation failed: {reason}")
            # Add integration metadata even for failed loops
            prepared_data["integration_status"] = {
                "status": "failed",
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.info(f"Loop {loop_id} successfully integrated with cognitive control layer")
            prepared_data["integration_status"] = {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return prepared_data
        
    except Exception as e:
        logger.error(f"Error integrating with orchestrator: {str(e)}")
        # Return original data with error information
        loop_data["integration_status"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        return loop_data

def process_reflection_with_controls(loop_id: str, loop_data: Dict[str, Any], reflection_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process reflection results with cognitive controls.
    
    Args:
        loop_id: The ID of the loop
        loop_data: The loop data
        reflection_result: The reflection result
        
    Returns:
        Updated loop data with belief conflict and permission violation information
    """
    logger.info(f"Processing reflection with cognitive controls for loop {loop_id}")
    
    try:
        integration = OrchestratorIntegration(loop_id)
        processed_data = integration.process_reflection_result(loop_data, reflection_result)
        
        # Add processing metadata
        processed_data["reflection_processing_status"] = {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "processor": "cognitive_control_layer"
        }
        
        return processed_data
        
    except Exception as e:
        logger.error(f"Error processing reflection with controls: {str(e)}")
        # Return original data with error information
        loop_data["reflection_processing_status"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        return loop_data

def determine_rerun_depth_with_controls(loop_id: str, loop_data: Dict[str, Any], rerun_reason: str) -> str:
    """
    Determine the appropriate depth for a loop rerun with cognitive controls.
    
    Args:
        loop_id: The ID of the loop
        loop_data: The original loop data
        rerun_reason: The reason for the rerun
        
    Returns:
        Appropriate depth level for the rerun
    """
    logger.info(f"Determining rerun depth with cognitive controls for loop {loop_id}")
    
    try:
        integration = OrchestratorIntegration(loop_id)
        depth = integration.determine_rerun_depth(loop_data, rerun_reason)
        
        # Log the determined depth
        logger.info(f"Determined rerun depth for loop {loop_id}: {depth}")
        
        # Add a timestamp to loop data for when depth was determined
        if "depth_determination_history" not in loop_data:
            loop_data["depth_determination_history"] = []
            
        loop_data["depth_determination_history"].append({
            "determined_at": datetime.utcnow().isoformat(),
            "depth": depth,
            "reason": rerun_reason,
            "determined_by": "cognitive_control_layer"
        })
        
        return depth
        
    except Exception as e:
        logger.error(f"Error determining rerun depth with controls: {str(e)}")
        # Default to deep depth on error to be safe
        return "deep"
