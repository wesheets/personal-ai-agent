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
from app.modules.depth_controller import (
    enrich_loop_with_depth, 
    preload_depth_for_rerun,
    enrich_loop_with_mode,
    preload_mode_for_rerun,
    get_depth_for_mode
)
from app.modules.tiered_orchestrator import (
    TieredOrchestrator,
    determine_optimal_mode,
    get_mode_config
)
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
    
    def __init__(self, loop_id: str, mode: Optional[str] = None):
        """
        Initialize the orchestrator integration.
        
        Args:
            loop_id: The ID of the current loop
            mode: Optional orchestrator mode (fast, balanced, thorough, research)
        """
        self.loop_id = loop_id
        self.agent_dispatcher = create_dispatcher(loop_id)
        self.validation_results = {}
        
        # Initialize tiered orchestrator with specified or default mode
        self.mode = mode if mode else "balanced"
        self.tiered_orchestrator = TieredOrchestrator(loop_id, self.mode)
        
        self.integration_metadata = {
            "initialized_at": datetime.utcnow().isoformat(),
            "loop_id": loop_id,
            "mode": self.mode,
            "version": "1.0"
        }
        logger.info(f"Initialized OrchestratorIntegration for loop {loop_id} with mode {self.mode}")
    
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
        logger.info(f"Validating and preparing loop {self.loop_id} with mode {self.mode}")
        
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
            
            # Step 2: Determine optimal mode if not explicitly set
            if "mode" not in loop_data:
                task_description = loop_data.get("task_description", "")
                complexity = loop_data.get("complexity_score")
                sensitivity = loop_data.get("sensitivity_score")
                time_constraint = loop_data.get("time_constraint_score")
                user_preference = loop_data.get("user_mode_preference")
                
                optimal_mode = determine_optimal_mode(
                    task_description, 
                    complexity, 
                    sensitivity, 
                    time_constraint,
                    user_preference
                )
                
                # Update the tiered orchestrator with the optimal mode
                if optimal_mode != self.mode:
                    self.tiered_orchestrator.change_mode(optimal_mode)
                    self.mode = optimal_mode
                    logger.info(f"Automatically selected optimal mode {optimal_mode} for loop {self.loop_id}")
            else:
                # Use the mode specified in loop_data
                specified_mode = loop_data["mode"]
                if specified_mode != self.mode:
                    self.tiered_orchestrator.change_mode(specified_mode)
                    self.mode = specified_mode
                    logger.info(f"Using specified mode {specified_mode} for loop {self.loop_id}")
            
            # Step 3: Prepare loop with tiered orchestrator
            loop_data = self.tiered_orchestrator.prepare_loop(loop_data)
            logger.debug(f"Loop {self.loop_id} prepared with mode: {self.mode}")
            
            # Step 4: Inject belief references
            loop_data = inject_belief_references(loop_data)
            belief_count = len(loop_data.get("belief_reference", []))
            logger.debug(f"Loop {self.loop_id} injected with {belief_count} belief references")
            
            # Step 5: Add validation results
            loop_data["loop_validation"] = "passed"
            loop_data["validation_status"] = {
                "status": "passed",
                "timestamp": datetime.utcnow().isoformat(),
                "checked_components": validation_result.get("checked_components", []),
                "mode": self.mode,
                "depth": get_depth_for_mode(self.mode),
                "belief_count": belief_count
            }
            
            # Step 6: Add orchestrator metadata
            loop_data["orchestrator_metadata"] = {
                "processed_by": "cognitive_control_layer",
                "processed_at": datetime.utcnow().isoformat(),
                "loop_id": self.loop_id,
                "mode": self.mode,
                "validation_version": "1.0"
            }
            
            logger.info(f"Loop {self.loop_id} successfully prepared with cognitive controls in {self.mode} mode")
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
        logger.info(f"Processing reflection results for loop {self.loop_id} in {self.mode} mode")
        
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
                "mode": self.mode,
                "has_conflicts": bool(conflicts),
                "has_violations": bool(violations),
                "severity": conflict_details.get("severity", "none") if conflicts else "none"
            }
            
            # Update visualization if needed based on mode
            if self.tiered_orchestrator.should_visualize_step("reflection"):
                loop_data["visualization_update_required"] = True
                loop_data["visualization_trigger"] = "reflection_processed"
            
            # Update memory snapshot if needed based on mode
            if self.tiered_orchestrator.should_snapshot_memory("reflection"):
                loop_data["memory_snapshot_required"] = True
                loop_data["memory_snapshot_trigger"] = "reflection_processed"
            
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
    
    def determine_rerun_mode(self, loop_data: Dict[str, Any], rerun_reason: str) -> str:
        """
        Determine the appropriate mode for a loop rerun.
        
        Args:
            loop_data: The original loop data
            rerun_reason: The reason for the rerun
            
        Returns:
            Appropriate orchestrator mode for the rerun
        """
        logger.info(f"Determining rerun mode for loop {self.loop_id} with reason: {rerun_reason}")
        
        try:
            # Get the appropriate mode from the depth controller
            new_mode = preload_mode_for_rerun(loop_data, rerun_reason)
            
            # Log the mode change if applicable
            original_mode = loop_data.get("mode", "balanced")
            if new_mode != original_mode:
                logger.info(f"Mode escalation for loop {self.loop_id}: {original_mode} -> {new_mode} due to {rerun_reason}")
                
                # Update the tiered orchestrator with the new mode
                self.tiered_orchestrator.change_mode(new_mode)
                self.mode = new_mode
            else:
                logger.debug(f"Maintaining mode {new_mode} for loop {self.loop_id} rerun")
            
            # Add rerun metadata
            if "rerun_mode_metadata" not in loop_data:
                loop_data["rerun_mode_metadata"] = []
            
            loop_data["rerun_mode_metadata"].append({
                "rerun_reason": rerun_reason,
                "original_mode": original_mode,
                "new_mode": new_mode,
                "determined_at": datetime.utcnow().isoformat(),
                "escalated": new_mode != original_mode
            })
            
            return new_mode
            
        except Exception as e:
            logger.error(f"Error determining rerun mode: {str(e)}")
            # Default to thorough mode on error to be safe
            return "thorough"

def integrate_with_orchestrator(loop_id: str, loop_data: Dict[str, Any], mode: Optional[str] = None) -> Dict[str, Any]:
    """
    Integrate cognitive control components with the orchestrator for a specific loop.
    
    Args:
        loop_id: The ID of the loop
        loop_data: The loop data
        mode: Optional orchestrator mode (fast, balanced, thorough, research)
        
    Returns:
        Prepared loop data with all cognitive controls applied
    """
    logger.info(f"Integrating cognitive control layer with orchestrator for loop {loop_id}")
    
    try:
        integration = OrchestratorIntegration(loop_id, mode)
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
        # Use the mode from loop_data if available
        mode = loop_data.get("mode", "balanced")
        integration = OrchestratorIntegration(loop_id, mode)
        processed_data = integration.process_reflection_result(loop_data, reflection_result)
        
        # Add processing metadata
        processed_data["reflection_processing_status"] = {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "processor": "cognitive_control_layer",
            "mode": mode
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
        # Use the mode from loop_data if available
        mode = loop_data.get("mode", "balanced")
        integration = OrchestratorIntegration(loop_id, mode)
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

def determine_rerun_mode_with_controls(loop_id: str, loop_data: Dict[str, Any], rerun_reason: str) -> str:
    """
    Determine the appropriate mode for a loop rerun with cognitive controls.
    
    Args:
        loop_id: The ID of the loop
        loop_data: The original loop data
        rerun_reason: The reason for the rerun
        
    Returns:
        Appropriate orchestrator mode for the rerun
    """
    logger.info(f"Determining rerun mode with cognitive controls for loop {loop_id}")
    
    try:
        # Use the mode from loop_data if available
        current_mode = loop_data.get("mode", "balanced")
        integration = OrchestratorIntegration(loop_id, current_mode)
        mode = integration.determine_rerun_mode(loop_data, rerun_reason)
        
        # Log the determined mode
        logger.info(f"Determined rerun mode for loop {loop_id}: {mode}")
        
        # Add a timestamp to loop data for when mode was determined
        if "mode_determination_history" not in loop_data:
            loop_data["mode_determination_history"] = []
            
        loop_data["mode_determination_history"].append({
            "determined_at": datetime.utcnow().isoformat(),
            "mode": mode,
            "reason": rerun_reason,
            "determined_by": "cognitive_control_layer"
        })
        
        return mode
        
    except Exception as e:
        logger.error(f"Error determining rerun mode with controls: {str(e)}")
        # Default to thorough mode on error to be safe
        return "thorough"
