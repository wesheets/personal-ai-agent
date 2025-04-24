"""
PESSIMIST Pre-Run Evaluation Implementation

This module implements the PESSIMIST Pre-Run Evaluation functionality for evaluating loop plans
before execution, identifying potential risks, and providing confidence scores.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from app.schemas.pessimist_evaluation_schema import (
    PessimistCheckRequest,
    Risk,
    RecommendedChange,
    PessimistCheckResult,
    PessimistCheckError
)

# Configure logging
logger = logging.getLogger("pessimist_evaluator")

class PessimistEvaluator:
    """
    PESSIMIST Pre-Run Evaluator for evaluating loop plans.
    
    This evaluator ensures that:
    - Loop plans are structurally sound
    - Agents are properly mapped to roles
    - Components are properly configured
    - Risks are identified and mitigated
    """
    
    def __init__(self):
        """Initialize the PESSIMIST Pre-Run Evaluator with required configuration."""
        self.version = "1.0.0"
        self.confidence_threshold = 0.6
        self.risk_weights = {
            "critical": 1.0,
            "high": 0.7,
            "medium": 0.4,
            "low": 0.2
        }
        
        logger.info("PESSIMIST Pre-Run Evaluator initialized (version: %s)", self.version)
    
    def evaluate_loop_plan(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a loop plan.
        
        Args:
            request_data: Dictionary containing the evaluation request data
            
        Returns:
            Dictionary containing the evaluation result
        """
        try:
            # Validate request against schema
            request = PessimistCheckRequest(**request_data)
            
            # Perform evaluation checks
            plan_risks, plan_changes = self._evaluate_loop_plan(request.loop_plan)
            component_risks, component_changes = self._evaluate_components(request.component_list)
            agent_risks, agent_changes = self._evaluate_agent_map(request.agent_map)
            
            # Combine all risks and recommended changes
            all_risks = plan_risks + component_risks + agent_risks
            all_changes = plan_changes + component_changes + agent_changes
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(all_risks)
            
            # Determine if the loop plan is approved
            approved = confidence_score >= self.confidence_threshold
            
            # Generate evaluation summary
            evaluation_summary = self._generate_evaluation_summary(
                confidence_score, 
                approved, 
                all_risks, 
                all_changes
            )
            
            # Log evaluation result
            self._log_evaluation_result(
                request.project_id,
                request.loop_id,
                confidence_score,
                approved,
                all_risks,
                all_changes,
                evaluation_summary
            )
            
            # Create response
            response = PessimistCheckResult(
                project_id=request.project_id,
                loop_id=request.loop_id,
                confidence_score=confidence_score,
                approved=approved,
                risks=all_risks,
                recommended_changes=all_changes,
                evaluation_summary=evaluation_summary,
                version=self.version
            )
            
            return response.dict()
        
        except Exception as e:
            logger.error("Error evaluating loop plan: %s", str(e))
            error_response = PessimistCheckError(
                message=f"Error evaluating loop plan: {str(e)}",
                project_id=request_data.get("project_id"),
                loop_id=request_data.get("loop_id"),
                version=self.version
            )
            return error_response.dict()
    
    def _evaluate_loop_plan(self, loop_plan: Dict[str, Any]) -> Tuple[List[Risk], List[RecommendedChange]]:
        """
        Evaluate the loop plan structure.
        
        Args:
            loop_plan: Detailed plan for the loop execution
            
        Returns:
            Tuple of (risks, recommended_changes)
        """
        risks = []
        recommended_changes = []
        
        # Check if loop plan has steps
        if "steps" not in loop_plan or not loop_plan["steps"]:
            risks.append(Risk(
                risk_id=f"risk_plan_{len(risks) + 1:03d}",
                risk_type="plan",
                severity="critical",
                description="Loop plan has no steps defined",
                affected_elements=["loop_plan"],
                mitigation_suggestions=["Define at least one step in the loop plan"]
            ))
            
            recommended_changes.append(RecommendedChange(
                change_id=f"change_plan_{len(recommended_changes) + 1:03d}",
                change_type="plan",
                priority=10,
                description="Add steps to the loop plan",
                affected_elements=["loop_plan"],
                expected_impact="Enable loop execution"
            ))
        
        # Check step sequence
        if "steps" in loop_plan and loop_plan["steps"]:
            steps = loop_plan["steps"]
            
            # Check for step ID sequence
            step_ids = [step.get("step_id") for step in steps if "step_id" in step]
            if step_ids and (sorted(step_ids) != list(range(min(step_ids), max(step_ids) + 1))):
                risks.append(Risk(
                    risk_id=f"risk_plan_{len(risks) + 1:03d}",
                    risk_type="plan",
                    severity="medium",
                    description="Step IDs are not sequential",
                    affected_elements=["loop_plan.steps"],
                    mitigation_suggestions=["Reorder steps to have sequential IDs"]
                ))
                
                recommended_changes.append(RecommendedChange(
                    change_id=f"change_plan_{len(recommended_changes) + 1:03d}",
                    change_type="plan",
                    priority=5,
                    description="Reorder steps to have sequential IDs",
                    affected_elements=["loop_plan.steps"],
                    expected_impact="Improved clarity and execution order"
                ))
            
            # Check for missing agent or action in steps
            for i, step in enumerate(steps):
                if "agent" not in step:
                    risks.append(Risk(
                        risk_id=f"risk_plan_{len(risks) + 1:03d}",
                        risk_type="plan",
                        severity="high",
                        description=f"Step {i+1} is missing agent assignment",
                        affected_elements=[f"loop_plan.steps[{i}]"],
                        mitigation_suggestions=["Assign an agent to each step"]
                    ))
                
                if "action" not in step:
                    risks.append(Risk(
                        risk_id=f"risk_plan_{len(risks) + 1:03d}",
                        risk_type="plan",
                        severity="high",
                        description=f"Step {i+1} is missing action definition",
                        affected_elements=[f"loop_plan.steps[{i}]"],
                        mitigation_suggestions=["Define an action for each step"]
                    ))
        
        # Check for max iterations
        if "max_iterations" not in loop_plan:
            risks.append(Risk(
                risk_id=f"risk_plan_{len(risks) + 1:03d}",
                risk_type="plan",
                severity="medium",
                description="Loop plan has no maximum iterations defined",
                affected_elements=["loop_plan"],
                mitigation_suggestions=["Define max_iterations to prevent infinite loops"]
            ))
            
            recommended_changes.append(RecommendedChange(
                change_id=f"change_plan_{len(recommended_changes) + 1:03d}",
                change_type="plan",
                priority=7,
                description="Add max_iterations to the loop plan",
                affected_elements=["loop_plan"],
                expected_impact="Prevent potential infinite loops"
            ))
        elif loop_plan["max_iterations"] > 10:
            risks.append(Risk(
                risk_id=f"risk_plan_{len(risks) + 1:03d}",
                risk_type="plan",
                severity="low",
                description=f"Maximum iterations ({loop_plan['max_iterations']}) is unusually high",
                affected_elements=["loop_plan.max_iterations"],
                mitigation_suggestions=["Consider reducing max_iterations to a more reasonable value"]
            ))
        
        # Check for timeout
        if "timeout_seconds" not in loop_plan:
            risks.append(Risk(
                risk_id=f"risk_plan_{len(risks) + 1:03d}",
                risk_type="plan",
                severity="medium",
                description="Loop plan has no timeout defined",
                affected_elements=["loop_plan"],
                mitigation_suggestions=["Define timeout_seconds to prevent long-running loops"]
            ))
            
            recommended_changes.append(RecommendedChange(
                change_id=f"change_plan_{len(recommended_changes) + 1:03d}",
                change_type="plan",
                priority=6,
                description="Add timeout_seconds to the loop plan",
                affected_elements=["loop_plan"],
                expected_impact="Prevent excessively long-running loops"
            ))
        elif loop_plan.get("timeout_seconds", 0) > 600:
            risks.append(Risk(
                risk_id=f"risk_plan_{len(risks) + 1:03d}",
                risk_type="plan",
                severity="low",
                description=f"Timeout ({loop_plan['timeout_seconds']} seconds) is unusually high",
                affected_elements=["loop_plan.timeout_seconds"],
                mitigation_suggestions=["Consider reducing timeout to a more reasonable value"]
            ))
        
        return risks, recommended_changes
    
    def _evaluate_components(self, components: List[Dict[str, Any]]) -> Tuple[List[Risk], List[RecommendedChange]]:
        """
        Evaluate the components involved in the loop.
        
        Args:
            components: List of components involved in the loop
            
        Returns:
            Tuple of (risks, recommended_changes)
        """
        risks = []
        recommended_changes = []
        
        # Check for high-risk components
        high_risk_components = [
            comp for comp in components 
            if comp.risk_level == "high"
        ]
        
        if high_risk_components:
            for comp in high_risk_components:
                risks.append(Risk(
                    risk_id=f"risk_comp_{len(risks) + 1:03d}",
                    risk_type="component",
                    severity="high",
                    description=f"High-risk component: {comp.component_id}",
                    affected_elements=[comp.component_id],
                    mitigation_suggestions=[
                        "Add additional validation for this component",
                        "Implement fallback mechanisms",
                        "Consider replacing with lower-risk alternative"
                    ]
                ))
                
                recommended_changes.append(RecommendedChange(
                    change_id=f"change_comp_{len(recommended_changes) + 1:03d}",
                    change_type="component",
                    priority=8,
                    description=f"Add fallback mechanism for {comp.component_id}",
                    affected_elements=[comp.component_id],
                    expected_impact="Reduced risk of component failure"
                ))
        
        # Check for duplicate component IDs
        component_ids = [comp.component_id for comp in components]
        duplicate_ids = set([cid for cid in component_ids if component_ids.count(cid) > 1])
        
        if duplicate_ids:
            risks.append(Risk(
                risk_id=f"risk_comp_{len(risks) + 1:03d}",
                risk_type="component",
                severity="medium",
                description=f"Duplicate component IDs: {', '.join(duplicate_ids)}",
                affected_elements=list(duplicate_ids),
                mitigation_suggestions=["Ensure each component has a unique ID"]
            ))
            
            recommended_changes.append(RecommendedChange(
                change_id=f"change_comp_{len(recommended_changes) + 1:03d}",
                change_type="component",
                priority=7,
                description="Resolve duplicate component IDs",
                affected_elements=list(duplicate_ids),
                expected_impact="Prevent confusion and potential conflicts"
            ))
        
        # Check for missing descriptions
        components_without_description = [
            comp.component_id for comp in components 
            if not comp.description or comp.description.strip() == ""
        ]
        
        if components_without_description:
            risks.append(Risk(
                risk_id=f"risk_comp_{len(risks) + 1:03d}",
                risk_type="component",
                severity="low",
                description=f"Components missing descriptions: {', '.join(components_without_description)}",
                affected_elements=components_without_description,
                mitigation_suggestions=["Add descriptive information to all components"]
            ))
        
        return risks, recommended_changes
    
    def _evaluate_agent_map(self, agent_map: List[Dict[str, Any]]) -> Tuple[List[Risk], List[RecommendedChange]]:
        """
        Evaluate the agent mapping.
        
        Args:
            agent_map: Mapping of agents to roles in the loop
            
        Returns:
            Tuple of (risks, recommended_changes)
        """
        risks = []
        recommended_changes = []
        
        # Check for critical agents
        critical_agents = ["ORCHESTRATOR", "CRITIC"]
        missing_critical_agents = [
            agent for agent in critical_agents
            if agent not in [mapping.agent_id for mapping in agent_map]
        ]
        
        if missing_critical_agents:
            risks.append(Risk(
                risk_id=f"risk_agent_{len(risks) + 1:03d}",
                risk_type="agent",
                severity="high",
                description=f"Missing critical agents: {', '.join(missing_critical_agents)}",
                affected_elements=["agent_map"],
                mitigation_suggestions=[f"Add {', '.join(missing_critical_agents)} to the agent map"]
            ))
            
            for agent in missing_critical_agents:
                recommended_changes.append(RecommendedChange(
                    change_id=f"change_agent_{len(recommended_changes) + 1:03d}",
                    change_type="agent",
                    priority=9,
                    description=f"Add {agent} agent to the loop",
                    affected_elements=["agent_map"],
                    expected_impact=f"Ensure critical {agent} functionality is available"
                ))
        
        # Check for circular dependencies
        circular_deps = self._find_circular_dependencies(agent_map)
        if circular_deps:
            for cycle in circular_deps:
                cycle_str = " -> ".join(cycle) + f" -> {cycle[0]}"
                risks.append(Risk(
                    risk_id=f"risk_agent_{len(risks) + 1:03d}",
                    risk_type="agent",
                    severity="critical",
                    description=f"Circular dependency detected: {cycle_str}",
                    affected_elements=cycle,
                    mitigation_suggestions=["Resolve circular dependencies in agent map"]
                ))
                
                recommended_changes.append(RecommendedChange(
                    change_id=f"change_agent_{len(recommended_changes) + 1:03d}",
                    change_type="agent",
                    priority=10,
                    description=f"Break circular dependency: {cycle_str}",
                    affected_elements=cycle,
                    expected_impact="Prevent deadlocks and ensure proper execution flow"
                ))
        
        # Check for duplicate roles
        roles = [mapping.role for mapping in agent_map]
        duplicate_roles = set([role for role in roles if roles.count(role) > 1])
        
        if duplicate_roles:
            risks.append(Risk(
                risk_id=f"risk_agent_{len(risks) + 1:03d}",
                risk_type="agent",
                severity="medium",
                description=f"Duplicate roles assigned: {', '.join(duplicate_roles)}",
                affected_elements=["agent_map"],
                mitigation_suggestions=["Ensure each role is assigned to only one agent"]
            ))
            
            recommended_changes.append(RecommendedChange(
                change_id=f"change_agent_{len(recommended_changes) + 1:03d}",
                change_type="agent",
                priority=6,
                description="Resolve duplicate role assignments",
                affected_elements=["agent_map"],
                expected_impact="Prevent confusion and role conflicts"
            ))
        
        # Check for missing priorities
        agents_without_priority = [
            mapping.agent_id for mapping in agent_map 
            if mapping.priority is None
        ]
        
        if agents_without_priority:
            risks.append(Risk(
                risk_id=f"risk_agent_{len(risks) + 1:03d}",
                risk_type="agent",
                severity="low",
                description=f"Agents missing priority: {', '.join(agents_without_priority)}",
                affected_elements=agents_without_priority,
                mitigation_suggestions=["Assign priority levels to all agents"]
            ))
        
        # Check for GUARDIAN agent (recommended for safety)
        if "GUARDIAN" not in [mapping.agent_id for mapping in agent_map]:
            recommended_changes.append(RecommendedChange(
                change_id=f"change_agent_{len(recommended_changes) + 1:03d}",
                change_type="agent",
                priority=5,
                description="Consider adding GUARDIAN agent for safety monitoring",
                affected_elements=["agent_map"],
                expected_impact="Improved safety and error handling"
            ))
        
        return risks, recommended_changes
    
    def _find_circular_dependencies(self, agent_map: List[Dict[str, Any]]) -> List[List[str]]:
        """
        Find circular dependencies in the agent map.
        
        Args:
            agent_map: Mapping of agents to roles in the loop
            
        Returns:
            List of circular dependency chains
        """
        # Build dependency graph
        graph = {}
        for mapping in agent_map:
            agent_id = mapping.agent_id
            dependencies = mapping.dependencies or []
            graph[agent_id] = dependencies
        
        # Find cycles using DFS
        cycles = []
        visited = set()
        path = []
        
        def dfs(node):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                dfs(neighbor)
            
            path.pop()
        
        for node in graph:
            dfs(node)
        
        return cycles
    
    def _calculate_confidence_score(self, risks: List[Risk]) -> float:
        """
        Calculate the confidence score based on identified risks.
        
        Args:
            risks: List of identified risks
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not risks:
            return 1.0
        
        # Calculate weighted risk score
        total_risk_weight = sum(
            self.risk_weights.get(risk.severity, 0.5) for risk in risks
        )
        
        # Normalize to 0.0-1.0 range, with higher values being worse
        normalized_risk = min(1.0, total_risk_weight / 5.0)  # Cap at 1.0
        
        # Confidence is inverse of risk
        return 1.0 - normalized_risk
    
    def _generate_evaluation_summary(
        self,
        confidence_score: float,
        approved: bool,
        risks: List[Risk],
        changes: List[RecommendedChange]
    ) -> str:
        """
        Generate a summary of the evaluation results.
        
        Args:
            confidence_score: Confidence score for the loop plan
            approved: Whether the loop plan is approved
            risks: List of identified risks
            changes: List of recommended changes
            
        Returns:
            Summary string
        """
        # Determine confidence level
        confidence_level = "high" if confidence_score >= 0.8 else "medium" if confidence_score >= 0.6 else "low"
        
        # Count risks by severity
        risk_counts = {}
        for risk in risks:
            risk_counts[risk.severity] = risk_counts.get(risk.severity, 0) + 1
        
        # Generate summary
        if approved:
            summary = f"Loop plan is approved with {confidence_level} confidence ({confidence_score:.2f})."
        else:
            summary = f"Loop plan is rejected due to low confidence ({confidence_score:.2f})."
        
        if risks:
            risk_summary = ", ".join(f"{count} {severity}" for severity, count in risk_counts.items())
            summary += f" {len(risks)} risks identified ({risk_summary})."
        else:
            summary += " No risks identified."
        
        if changes:
            summary += f" {len(changes)} recommended changes provided."
        
        return summary
    
    def _log_evaluation_result(
        self,
        project_id: str,
        loop_id: str,
        confidence_score: float,
        approved: bool,
        risks: List[Risk],
        changes: List[RecommendedChange],
        summary: str
    ) -> None:
        """
        Log the evaluation result to the system.
        
        Args:
            project_id: Project identifier
            loop_id: Loop identifier
            confidence_score: Confidence score for the loop plan
            approved: Whether the loop plan is approved
            risks: List of identified risks
            changes: List of recommended changes
            summary: Evaluation summary
        """
        log_tag = f"pessimist_reject_log_{loop_id}" if not approved else f"pessimist_eval_log_{loop_id}"
        
        log_data = {
            "project_id": project_id,
            "loop_id": loop_id,
            "confidence_score": confidence_score,
            "approved": approved,
            "risks": [risk.dict() for risk in risks],
            "recommended_changes": [change.dict() for change in changes],
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
            "version": self.version
        }
        
        # In a real implementation, this would write to a persistent store
        logger.info("Evaluation result for loop %s: approved=%s, confidence=%.2f, risks=%d", 
                   loop_id, approved, confidence_score, len(risks))
        
        # Log to console for demonstration
        print(f"Logged evaluation result to {log_tag}: {json.dumps(log_data, indent=2)}")


# Create singleton instance
pessimist_evaluator = PessimistEvaluator()

def evaluate_loop_plan(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a loop plan using the PESSIMIST Pre-Run Evaluator.
    
    Args:
        request_data: Dictionary containing the evaluation request data
        
    Returns:
        Dictionary containing the evaluation result
    """
    return pessimist_evaluator.evaluate_loop_plan(request_data)
