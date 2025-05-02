"""
Planning Logic Integration Module

This module integrates the depth controller into the planning logic
to adjust reflection based on depth level.

The planning logic integration ensures that the reflection process is
appropriately tailored to the depth level of each loop, optimizing the
balance between thoroughness and efficiency.
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime

from app.modules.depth_controller import (
    get_agents_for_depth,
    get_reflection_config,
    adjust_agent_plan,
    enrich_loop_with_depth,
    get_required_beliefs_for_depth
)
from app.modules.core_beliefs_integration import get_belief_description

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlanningLogicIntegration:
    """
    Class for integrating depth controller into planning logic.
    
    This class ensures that reflection plans are appropriately tailored to the
    depth level of each loop, optimizing the balance between thoroughness and efficiency.
    """
    
    def __init__(self, loop_id: str):
        """
        Initialize the planning logic integration.
        
        Args:
            loop_id: The ID of the current loop
        """
        self.loop_id = loop_id
        self.integration_metadata = {
            "initialized_at": datetime.utcnow().isoformat(),
            "loop_id": loop_id,
            "version": "1.0"
        }
        logger.info(f"Initialized PlanningLogicIntegration for loop {loop_id}")
    
    def generate_reflection_plan(self, loop_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a reflection plan based on the loop depth.
        
        Args:
            loop_data: The loop data
            
        Returns:
            List of reflection steps to execute
        """
        logger.info(f"Generating reflection plan for loop {self.loop_id}")
        
        try:
            # Get depth from loop data or default to standard
            depth = loop_data.get("depth", "standard")
            logger.debug(f"Using depth '{depth}' for reflection plan generation")
            
            # Get reflection configuration for this depth
            reflection_config = get_reflection_config(depth)
            
            # Generate base reflection plan
            base_plan = self._generate_base_reflection_plan()
            logger.debug(f"Generated base reflection plan with {len(base_plan)} steps")
            
            # Adjust plan based on depth
            adjusted_plan = adjust_agent_plan(base_plan, depth)
            logger.info(f"Adjusted reflection plan to {len(adjusted_plan)} steps for depth '{depth}'")
            
            # Get required beliefs for this depth
            required_beliefs = get_required_beliefs_for_depth(depth)
            
            # Add depth-specific configuration to each step
            for step in adjusted_plan:
                agent = step.get("agent")
                step["depth"] = depth
                step["loop_id"] = self.loop_id
                step["generated_at"] = datetime.utcnow().isoformat()
                
                # Add belief references based on agent and depth
                if agent == "CRITIC":
                    step["belief_reference"] = ["alignment_over_speed"]
                elif agent == "PESSIMIST":
                    step["belief_reference"] = ["bias_awareness_required", "minimize_hallucination"]
                elif agent == "CEO":
                    step["belief_reference"] = ["transparency_to_operator"]
                elif agent == "SAGE":
                    step["belief_reference"] = required_beliefs
                else:
                    # Default to depth-required beliefs
                    step["belief_reference"] = required_beliefs
                
                # Add belief descriptions for reference
                step["belief_descriptions"] = {}
                for belief in step.get("belief_reference", []):
                    step["belief_descriptions"][belief] = get_belief_description(belief)
                
                logger.debug(f"Configured step for agent {agent} with {len(step.get('belief_reference', []))} beliefs")
            
            # Add plan metadata
            plan_metadata = {
                "generated_at": datetime.utcnow().isoformat(),
                "depth": depth,
                "step_count": len(adjusted_plan),
                "agents": [step.get("agent") for step in adjusted_plan],
                "loop_id": self.loop_id
            }
            
            # Return plan with metadata
            return {
                "plan": adjusted_plan,
                "metadata": plan_metadata
            }
            
        except Exception as e:
            logger.error(f"Error generating reflection plan: {str(e)}")
            # Return a minimal plan as fallback
            return {
                "plan": [
                    {
                        "agent": "CRITIC",
                        "action": "score_summary",
                        "order": 1,
                        "depth": "standard",
                        "loop_id": self.loop_id,
                        "belief_reference": ["reflection_before_execution"],
                        "error": str(e)
                    }
                ],
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "depth": "standard",
                    "step_count": 1,
                    "agents": ["CRITIC"],
                    "loop_id": self.loop_id,
                    "error": str(e),
                    "is_fallback": True
                }
            }
    
    def _generate_base_reflection_plan(self) -> List[Dict[str, Any]]:
        """
        Generate the base reflection plan with all possible agents.
        
        Returns:
            List of all possible reflection steps
        """
        logger.debug(f"Generating base reflection plan for loop {self.loop_id}")
        
        # Define the complete set of reflection steps with all possible agents
        return [
            {
                "agent": "HAL",
                "action": "analyze_technical_requirements",
                "order": 1,
                "description": "Analyze technical aspects and implementation details",
                "purpose": "Ensure technical feasibility and correctness"
            },
            {
                "agent": "NOVA",
                "action": "execute_task",
                "order": 2,
                "description": "Execute the primary task with focus on efficiency",
                "purpose": "Complete the core task requirements"
            },
            {
                "agent": "CRITIC",
                "action": "score_summary",
                "order": 3,
                "description": "Evaluate quality and completeness of the solution",
                "purpose": "Ensure solution meets quality standards"
            },
            {
                "agent": "CEO",
                "action": "evaluate_alignment",
                "order": 4,
                "description": "Assess alignment with user intent and business goals",
                "purpose": "Ensure solution aligns with strategic objectives"
            },
            {
                "agent": "PESSIMIST",
                "action": "identify_bias",
                "order": 5,
                "description": "Identify potential biases and failure modes",
                "purpose": "Mitigate risks and ensure ethical considerations"
            },
            {
                "agent": "SAGE",
                "action": "evaluate_alignment",
                "order": 6,
                "description": "Perform comprehensive evaluation of solution quality",
                "purpose": "Ensure holistic alignment with all requirements"
            }
        ]
    
    def adjust_execution_plan(self, loop_data: Dict[str, Any], execution_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Adjust an execution plan based on the loop depth.
        
        Args:
            loop_data: The loop data
            execution_plan: The original execution plan
            
        Returns:
            Dictionary containing adjusted execution plan and metadata
        """
        logger.info(f"Adjusting execution plan for loop {self.loop_id}")
        
        try:
            # Get depth from loop data or default to standard
            depth = loop_data.get("depth", "standard")
            logger.debug(f"Using depth '{depth}' for execution plan adjustment")
            
            # Get required beliefs for this depth
            required_beliefs = get_required_beliefs_for_depth(depth)
            
            # Add depth information to each step
            for step in execution_plan:
                step["depth"] = depth
                step["loop_id"] = self.loop_id
                step["adjusted_at"] = datetime.utcnow().isoformat()
                
                # Add belief references based on step type
                if "belief_reference" not in step:
                    step["belief_reference"] = required_beliefs
                
                # Add belief descriptions for reference
                step["belief_descriptions"] = {}
                for belief in step.get("belief_reference", []):
                    step["belief_descriptions"][belief] = get_belief_description(belief)
                
                logger.debug(f"Configured execution step {step.get('order', 0)} with {len(step.get('belief_reference', []))} beliefs")
            
            # Add plan metadata
            plan_metadata = {
                "adjusted_at": datetime.utcnow().isoformat(),
                "depth": depth,
                "step_count": len(execution_plan),
                "loop_id": self.loop_id,
                "belief_count": len(required_beliefs)
            }
            
            logger.info(f"Successfully adjusted execution plan with {len(execution_plan)} steps for depth '{depth}'")
            
            # Return plan with metadata
            return {
                "plan": execution_plan,
                "metadata": plan_metadata
            }
            
        except Exception as e:
            logger.error(f"Error adjusting execution plan: {str(e)}")
            # Return original plan with error information
            return {
                "plan": execution_plan,
                "metadata": {
                    "adjusted_at": datetime.utcnow().isoformat(),
                    "depth": loop_data.get("depth", "standard"),
                    "step_count": len(execution_plan),
                    "loop_id": self.loop_id,
                    "error": str(e),
                    "is_fallback": True
                }
            }

def generate_reflection_plan_with_depth(loop_id: str, loop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a reflection plan with depth-based adjustments.
    
    Args:
        loop_id: The ID of the loop
        loop_data: The loop data
        
    Returns:
        Dictionary containing reflection plan and metadata adjusted for the specified depth
    """
    logger.info(f"Generating reflection plan with depth for loop {loop_id}")
    
    try:
        integration = PlanningLogicIntegration(loop_id)
        result = integration.generate_reflection_plan(loop_data)
        logger.info(f"Successfully generated reflection plan for loop {loop_id}")
        return result
    except Exception as e:
        logger.error(f"Error in generate_reflection_plan_with_depth: {str(e)}")
        # Return a minimal fallback plan
        return {
            "plan": [
                {
                    "agent": "CRITIC",
                    "action": "score_summary",
                    "order": 1,
                    "depth": "standard",
                    "loop_id": loop_id,
                    "belief_reference": ["reflection_before_execution"],
                    "error": str(e)
                }
            ],
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "depth": "standard",
                "step_count": 1,
                "agents": ["CRITIC"],
                "loop_id": loop_id,
                "error": str(e),
                "is_fallback": True
            }
        }

def adjust_execution_plan_with_depth(loop_id: str, loop_data: Dict[str, Any], execution_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Adjust an execution plan with depth-based considerations.
    
    Args:
        loop_id: The ID of the loop
        loop_data: The loop data
        execution_plan: The original execution plan
        
    Returns:
        Dictionary containing adjusted execution plan and metadata
    """
    logger.info(f"Adjusting execution plan with depth for loop {loop_id}")
    
    try:
        integration = PlanningLogicIntegration(loop_id)
        result = integration.adjust_execution_plan(loop_data, execution_plan)
        logger.info(f"Successfully adjusted execution plan for loop {loop_id}")
        return result
    except Exception as e:
        logger.error(f"Error in adjust_execution_plan_with_depth: {str(e)}")
        # Return original plan with error information
        return {
            "plan": execution_plan,
            "metadata": {
                "adjusted_at": datetime.utcnow().isoformat(),
                "depth": loop_data.get("depth", "standard"),
                "step_count": len(execution_plan),
                "loop_id": loop_id,
                "error": str(e),
                "is_fallback": True
            }
        }
