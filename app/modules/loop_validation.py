"""
Loop Sanity Validator Implementation

This module implements the Loop Sanity Validator functionality for validating loop configurations
before execution, ensuring structural integrity and preventing invalid loop plans.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from app.schemas.loop_validation_schema import (
    LoopValidationRequest,
    ValidationIssue,
    ValidationRecommendation,
    LoopValidationResult,
    LoopValidationError
)

# Configure logging
logger = logging.getLogger("loop_validator")

class LoopSanityValidator:
    """
    Loop Sanity Validator for validating loop configurations.
    
    This validator ensures that:
    - All planned agents exist and are properly registered
    - The expected schema is valid and complete
    - The max loops value is reasonable
    - The overall loop structure is sound
    """
    
    def __init__(self):
        """Initialize the Loop Sanity Validator with required configuration."""
        self.version = "1.0.0"
        self.registered_agents = self._load_registered_agents()
        self.schema_templates = self._load_schema_templates()
        self.max_recommended_loops = 10
        self.min_validation_score_threshold = 0.7
        
        logger.info("Loop Sanity Validator initialized (version: %s)", self.version)
    
    def _load_registered_agents(self) -> List[str]:
        """
        Load the list of registered agents from the system.
        
        In a real implementation, this would query the agent registry.
        For now, we'll use a hardcoded list of common agents.
        
        Returns:
            List of registered agent identifiers
        """
        # This would normally query the agent registry
        return [
            "ORCHESTRATOR", "CRITIC", "SAGE", "NOVA", "PESSIMIST", 
            "HISTORIAN", "DEBUGGER", "CTO", "OBSERVER", "GUARDIAN",
            "ASH", "SITEGEN", "TRAINER", "CORE-FORGE", "HAL"
        ]
    
    def _load_schema_templates(self) -> Dict[str, Any]:
        """
        Load schema templates for validation.
        
        In a real implementation, this would load from a schema repository.
        For now, we'll use hardcoded templates.
        
        Returns:
            Dictionary of schema templates
        """
        # This would normally load from a schema repository
        return {
            "basic_loop": {
                "input": {
                    "query": "string",
                    "parameters": "object"
                },
                "output": {
                    "result": "string",
                    "status": "string",
                    "metadata": "object"
                }
            },
            "advanced_loop": {
                "input": {
                    "query": "string",
                    "parameters": "object",
                    "context": "object",
                    "history": "array"
                },
                "output": {
                    "result": "string",
                    "status": "string",
                    "metadata": "object",
                    "debug_info": "object",
                    "next_steps": "array"
                }
            }
        }
    
    def validate_loop(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a loop configuration.
        
        Args:
            request_data: Dictionary containing the validation request data
            
        Returns:
            Dictionary containing the validation result
        """
        try:
            # Validate request against schema
            request = LoopValidationRequest(**request_data)
            
            # Perform validation checks
            agent_issues, agent_recommendations = self._validate_agents(request.planned_agents)
            schema_issues, schema_recommendations = self._validate_schema(request.expected_schema)
            loop_issues, loop_recommendations = self._validate_max_loops(request.max_loops)
            
            # Combine all issues and recommendations
            all_issues = agent_issues + schema_issues + loop_issues
            all_recommendations = agent_recommendations + schema_recommendations + loop_recommendations
            
            # Calculate validation score
            validation_score = self._calculate_validation_score(all_issues)
            
            # Determine if the loop is valid
            valid = validation_score >= self.min_validation_score_threshold and not any(
                issue.severity == "critical" for issue in all_issues
            )
            
            # Log validation result
            self._log_validation_result(
                request.project_id,
                request.loop_id,
                valid,
                validation_score,
                all_issues,
                all_recommendations
            )
            
            # Create response
            response = LoopValidationResult(
                valid=valid,
                project_id=request.project_id,
                loop_id=request.loop_id,
                issues=all_issues,
                recommendations=all_recommendations,
                validation_score=validation_score,
                version=self.version
            )
            
            return response.dict()
        
        except Exception as e:
            logger.error("Error validating loop: %s", str(e))
            error_response = LoopValidationError(
                message=f"Error validating loop: {str(e)}",
                project_id=request_data.get("project_id"),
                loop_id=request_data.get("loop_id"),
                version=self.version
            )
            return error_response.dict()
    
    def _validate_agents(self, planned_agents: List[str]) -> Tuple[List[ValidationIssue], List[ValidationRecommendation]]:
        """
        Validate the planned agents for a loop.
        
        Args:
            planned_agents: List of agent identifiers planned for the loop
            
        Returns:
            Tuple of (issues, recommendations)
        """
        issues = []
        recommendations = []
        
        # Check if all planned agents are registered
        for agent in planned_agents:
            if agent not in self.registered_agents:
                issues.append(ValidationIssue(
                    issue_type="agent",
                    severity="error",
                    description=f"Agent '{agent}' is not registered in the system",
                    affected_component="planned_agents"
                ))
                
                # Suggest similar agents as recommendations
                similar_agents = self._find_similar_agents(agent)
                if similar_agents:
                    recommendations.append(ValidationRecommendation(
                        recommendation_type="agent",
                        description=f"Replace '{agent}' with one of these registered agents: {', '.join(similar_agents)}",
                        priority=4
                    ))
        
        # Check for required agents
        required_agents = ["ORCHESTRATOR", "CRITIC"]
        for agent in required_agents:
            if agent not in planned_agents:
                issues.append(ValidationIssue(
                    issue_type="agent",
                    severity="warning",
                    description=f"Recommended agent '{agent}' is not included in the planned agents",
                    affected_component="planned_agents"
                ))
                
                recommendations.append(ValidationRecommendation(
                    recommendation_type="agent",
                    description=f"Consider adding '{agent}' to the planned agents for better loop performance",
                    priority=3
                ))
        
        # Check for agent conflicts
        if "PESSIMIST" in planned_agents and "OPTIMIST" in planned_agents:
            issues.append(ValidationIssue(
                issue_type="agent",
                severity="warning",
                description="Potential conflict between PESSIMIST and OPTIMIST agents",
                affected_component="planned_agents"
            ))
            
            recommendations.append(ValidationRecommendation(
                recommendation_type="agent",
                description="Consider using either PESSIMIST or OPTIMIST, but not both in the same loop",
                priority=2
            ))
        
        return issues, recommendations
    
    def _find_similar_agents(self, agent: str) -> List[str]:
        """
        Find similar registered agents based on string similarity.
        
        Args:
            agent: Agent identifier to find similar agents for
            
        Returns:
            List of similar agent identifiers
        """
        # Simple string similarity check
        return [
            registered_agent for registered_agent in self.registered_agents
            if self._string_similarity(agent.lower(), registered_agent.lower()) > 0.6
        ]
    
    def _string_similarity(self, a: str, b: str) -> float:
        """
        Calculate string similarity between two strings.
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Simple implementation using character overlap
        if not a or not b:
            return 0.0
        
        a_set = set(a)
        b_set = set(b)
        
        intersection = len(a_set.intersection(b_set))
        union = len(a_set.union(b_set))
        
        return intersection / union if union > 0 else 0.0
    
    def _validate_schema(self, expected_schema: Dict[str, Any]) -> Tuple[List[ValidationIssue], List[ValidationRecommendation]]:
        """
        Validate the expected schema for a loop.
        
        Args:
            expected_schema: Expected schema structure for loop inputs and outputs
            
        Returns:
            Tuple of (issues, recommendations)
        """
        issues = []
        recommendations = []
        
        # Check if schema has required sections
        required_sections = ["input", "output"]
        for section in required_sections:
            if section not in expected_schema:
                issues.append(ValidationIssue(
                    issue_type="schema",
                    severity="error",
                    description=f"Required schema section '{section}' is missing",
                    affected_component="expected_schema"
                ))
                
                recommendations.append(ValidationRecommendation(
                    recommendation_type="schema",
                    description=f"Add '{section}' section to the expected schema",
                    priority=5
                ))
        
        # Check if schema matches any templates
        best_match = None
        best_match_score = 0.0
        
        for template_name, template in self.schema_templates.items():
            match_score = self._calculate_schema_match_score(expected_schema, template)
            if match_score > best_match_score:
                best_match = template_name
                best_match_score = match_score
        
        if best_match and best_match_score < 0.8:
            recommendations.append(ValidationRecommendation(
                recommendation_type="schema",
                description=f"Consider using the '{best_match}' schema template for better compatibility",
                priority=3
            ))
        
        # Check for common schema issues
        if "input" in expected_schema and "query" not in expected_schema["input"]:
            issues.append(ValidationIssue(
                issue_type="schema",
                severity="warning",
                description="Common field 'query' is missing from input schema",
                affected_component="expected_schema.input"
            ))
        
        if "output" in expected_schema and "status" not in expected_schema["output"]:
            issues.append(ValidationIssue(
                issue_type="schema",
                severity="warning",
                description="Common field 'status' is missing from output schema",
                affected_component="expected_schema.output"
            ))
        
        return issues, recommendations
    
    def _calculate_schema_match_score(self, schema: Dict[str, Any], template: Dict[str, Any]) -> float:
        """
        Calculate how well a schema matches a template.
        
        Args:
            schema: Schema to check
            template: Template to match against
            
        Returns:
            Match score between 0.0 and 1.0
        """
        # Simple implementation checking section and field overlap
        score = 0.0
        total_sections = len(template)
        matched_sections = 0
        
        for section_name, section_template in template.items():
            if section_name in schema:
                matched_sections += 1
                
                section_schema = schema[section_name]
                total_fields = len(section_template)
                matched_fields = sum(1 for field in section_template if field in section_schema)
                
                score += matched_fields / total_fields if total_fields > 0 else 0.0
        
        return (score / total_sections) if total_sections > 0 else 0.0
    
    def _validate_max_loops(self, max_loops: int) -> Tuple[List[ValidationIssue], List[ValidationRecommendation]]:
        """
        Validate the maximum number of loops.
        
        Args:
            max_loops: Maximum number of loop iterations allowed
            
        Returns:
            Tuple of (issues, recommendations)
        """
        issues = []
        recommendations = []
        
        # Check if max_loops is reasonable
        if max_loops > self.max_recommended_loops:
            issues.append(ValidationIssue(
                issue_type="loops",
                severity="warning",
                description=f"Maximum loops ({max_loops}) exceeds recommended limit ({self.max_recommended_loops})",
                affected_component="max_loops"
            ))
            
            recommendations.append(ValidationRecommendation(
                recommendation_type="loops",
                description=f"Consider reducing max_loops from {max_loops} to {self.max_recommended_loops} for better performance",
                priority=3
            ))
        
        if max_loops < 2:
            recommendations.append(ValidationRecommendation(
                recommendation_type="loops",
                description="Consider increasing max_loops to at least 2 to allow for iteration",
                priority=2
            ))
        
        return issues, recommendations
    
    def _calculate_validation_score(self, issues: List[ValidationIssue]) -> float:
        """
        Calculate the overall validation score based on issues.
        
        Args:
            issues: List of validation issues
            
        Returns:
            Validation score between 0.0 and 1.0
        """
        if not issues:
            return 1.0
        
        # Calculate score based on issue severity
        severity_weights = {
            "critical": 1.0,
            "error": 0.5,
            "warning": 0.2
        }
        
        total_weight = sum(severity_weights[issue.severity] for issue in issues)
        max_weight = len(issues)  # If all issues were critical
        
        # Score is inversely proportional to the weighted sum of issues
        return max(0.0, 1.0 - (total_weight / max_weight if max_weight > 0 else 0.0))
    
    def _log_validation_result(
        self,
        project_id: str,
        loop_id: str,
        valid: bool,
        validation_score: float,
        issues: List[ValidationIssue],
        recommendations: List[ValidationRecommendation]
    ) -> None:
        """
        Log the validation result to the system.
        
        Args:
            project_id: Project identifier
            loop_id: Loop identifier
            valid: Whether the loop configuration is valid
            validation_score: Overall validation score
            issues: List of validation issues
            recommendations: List of validation recommendations
        """
        log_tag = f"loop_sanity_check_{loop_id}"
        
        log_data = {
            "project_id": project_id,
            "loop_id": loop_id,
            "valid": valid,
            "validation_score": validation_score,
            "issues": [issue.dict() for issue in issues],
            "recommendations": [rec.dict() for rec in recommendations],
            "timestamp": datetime.utcnow().isoformat(),
            "version": self.version
        }
        
        # In a real implementation, this would write to a persistent store
        logger.info("Validation result for loop %s: valid=%s, score=%.2f, issues=%d", 
                   loop_id, valid, validation_score, len(issues))
        
        # Log to console for demonstration
        print(f"Logged validation result to {log_tag}: {json.dumps(log_data, indent=2)}")


# Create singleton instance
loop_validator = LoopSanityValidator()

def validate_loop(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a loop configuration using the Loop Sanity Validator.
    
    Args:
        request_data: Dictionary containing the validation request data
        
    Returns:
        Dictionary containing the validation result
    """
    return loop_validator.validate_loop(request_data)
