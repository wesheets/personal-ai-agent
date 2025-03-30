"""
Planner Orchestrator Module for the Autonomous Goal Decomposer + Planner Agent

This module serves as the execution core that receives a main goal, breaks it into subtasks,
assigns subtasks to agents, sequences execution based on dependencies, stores progress in
vector memory, and escalates issues when necessary.
"""

import os
import json
import uuid
import time
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime

# Import required modules
from app.tools.agent_router import get_agent_router, find_agent
from app.core.vector_memory import VectorMemory, get_vector_memory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlannerOrchestrator:
    """
    Execution core for the Planner Agent that handles goal decomposition,
    subtask assignment, execution sequencing, and progress tracking.
    """
    
    def __init__(self):
        """Initialize the planner orchestrator."""
        self.agent_router = get_agent_router()
        self.vector_memory = get_vector_memory()
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname("/app/logs/planner_execution_log.json"), exist_ok=True)
        
        # Load planner configuration
        try:
            with open("/app/prompts/planner.json", "r") as f:
                self.planner_config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading planner configuration: {str(e)}")
            self.planner_config = {}
        
        # Initialize active goals tracking
        self.active_goals = {}
    
    def process_goal(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a high-level goal by decomposing it into subtasks and orchestrating execution.
        
        Args:
            goal: High-level goal details
            
        Returns:
            Goal execution results
        """
        # Generate a unique goal ID if not provided
        goal_id = goal.get("id", str(uuid.uuid4()))
        goal["id"] = goal_id
        
        # Log the start of goal processing
        self._log_execution_event(goal_id, "goal_start", "Started processing goal", goal)
        
        # Store the goal in memory
        self._store_in_memory(goal_id, "goal", goal, "goal_start")
        
        # Track the goal as active
        self.active_goals[goal_id] = {
            "goal": goal,
            "status": "in_progress",
            "subtasks": [],
            "start_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            # Decompose the goal into subtasks
            subtasks = self._decompose_goal(goal)
            
            # Assign agents to subtasks
            assigned_subtasks = self._assign_agents(subtasks, goal_id)
            
            # Sequence subtasks based on dependencies
            sequenced_subtasks = self._sequence_subtasks(assigned_subtasks)
            
            # Update active goal tracking
            self.active_goals[goal_id]["subtasks"] = sequenced_subtasks
            self.active_goals[goal_id]["last_updated"] = datetime.now().isoformat()
            
            # Execute the subtasks
            results = self._execute_subtasks(sequenced_subtasks, goal_id)
            
            # Compile the final results
            final_result = self._compile_results(goal, results)
            
            # Update goal status to completed
            self.active_goals[goal_id]["status"] = "completed"
            self.active_goals[goal_id]["completion_time"] = datetime.now().isoformat()
            self.active_goals[goal_id]["last_updated"] = datetime.now().isoformat()
            
            # Log the completion of goal processing
            self._log_execution_event(goal_id, "goal_complete", "Completed processing goal", final_result)
            
            # Store the final result in memory
            self._store_in_memory(goal_id, "goal_result", final_result, "goal_complete")
            
            return final_result
        
        except Exception as e:
            error_msg = f"Error processing goal: {str(e)}"
            logger.error(error_msg)
            
            # Update goal status to failed
            self.active_goals[goal_id]["status"] = "failed"
            self.active_goals[goal_id]["error"] = error_msg
            self.active_goals[goal_id]["last_updated"] = datetime.now().isoformat()
            
            # Log the failure
            self._log_execution_event(goal_id, "goal_failed", error_msg, {"error": str(e)})
            
            # Escalate the issue
            self._escalate_issue(goal_id, "goal_processing_failed", error_msg, goal)
            
            return {
                "status": "failed",
                "goal_id": goal_id,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def _decompose_goal(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decompose a high-level goal into atomic subtasks.
        
        Args:
            goal: High-level goal details
            
        Returns:
            List of subtasks
        """
        goal_id = goal["id"]
        goal_description = goal.get("description", "")
        goal_context = goal.get("context", {})
        
        logger.info(f"Decomposing goal: {goal_description}")
        
        # Log the decomposition start
        self._log_execution_event(goal_id, "decomposition_start", "Started goal decomposition", goal)
        
        # TODO: Implement integration with autonomous_research_chain for more complex decomposition
        # For now, use a rule-based approach to decompose the goal
        
        # Extract decomposition strategy from goal or use default
        strategy = goal.get("decomposition_strategy", "sequential_breakdown")
        
        # Get available strategies from planner config
        available_strategies = self.planner_config.get("decomposition_strategies", [])
        if strategy not in available_strategies and available_strategies:
            strategy = available_strategies[0]
        
        subtasks = []
        
        if strategy == "sequential_breakdown":
            # Simple sequential breakdown based on goal type
            goal_type = goal.get("type", "general")
            
            if "research" in goal_type.lower():
                # Research-oriented goal
                subtasks = [
                    {
                        "id": f"{goal_id}_subtask_1",
                        "description": f"Research background information for: {goal_description}",
                        "type": "research",
                        "dependencies": []
                    },
                    {
                        "id": f"{goal_id}_subtask_2",
                        "description": f"Analyze key findings from research on: {goal_description}",
                        "type": "analysis",
                        "dependencies": [f"{goal_id}_subtask_1"]
                    },
                    {
                        "id": f"{goal_id}_subtask_3",
                        "description": f"Synthesize conclusions and recommendations for: {goal_description}",
                        "type": "synthesis",
                        "dependencies": [f"{goal_id}_subtask_2"]
                    }
                ]
            
            elif "development" in goal_type.lower() or "code" in goal_type.lower():
                # Development-oriented goal
                subtasks = [
                    {
                        "id": f"{goal_id}_subtask_1",
                        "description": f"Design architecture for: {goal_description}",
                        "type": "architecture",
                        "dependencies": []
                    },
                    {
                        "id": f"{goal_id}_subtask_2",
                        "description": f"Implement core functionality for: {goal_description}",
                        "type": "code",
                        "dependencies": [f"{goal_id}_subtask_1"]
                    },
                    {
                        "id": f"{goal_id}_subtask_3",
                        "description": f"Test and validate implementation of: {goal_description}",
                        "type": "testing",
                        "dependencies": [f"{goal_id}_subtask_2"]
                    },
                    {
                        "id": f"{goal_id}_subtask_4",
                        "description": f"Document implementation of: {goal_description}",
                        "type": "documentation",
                        "dependencies": [f"{goal_id}_subtask_2"]
                    }
                ]
            
            elif "deployment" in goal_type.lower() or "infrastructure" in goal_type.lower():
                # Operations-oriented goal
                subtasks = [
                    {
                        "id": f"{goal_id}_subtask_1",
                        "description": f"Plan deployment strategy for: {goal_description}",
                        "type": "planning",
                        "dependencies": []
                    },
                    {
                        "id": f"{goal_id}_subtask_2",
                        "description": f"Prepare infrastructure for: {goal_description}",
                        "type": "infrastructure",
                        "dependencies": [f"{goal_id}_subtask_1"]
                    },
                    {
                        "id": f"{goal_id}_subtask_3",
                        "description": f"Execute deployment of: {goal_description}",
                        "type": "deployment",
                        "dependencies": [f"{goal_id}_subtask_2"]
                    },
                    {
                        "id": f"{goal_id}_subtask_4",
                        "description": f"Verify and monitor deployment of: {goal_description}",
                        "type": "monitoring",
                        "dependencies": [f"{goal_id}_subtask_3"]
                    }
                ]
            
            else:
                # General goal
                subtasks = [
                    {
                        "id": f"{goal_id}_subtask_1",
                        "description": f"Gather information for: {goal_description}",
                        "type": "research",
                        "dependencies": []
                    },
                    {
                        "id": f"{goal_id}_subtask_2",
                        "description": f"Analyze requirements for: {goal_description}",
                        "type": "analysis",
                        "dependencies": [f"{goal_id}_subtask_1"]
                    },
                    {
                        "id": f"{goal_id}_subtask_3",
                        "description": f"Develop solution for: {goal_description}",
                        "type": "development",
                        "dependencies": [f"{goal_id}_subtask_2"]
                    },
                    {
                        "id": f"{goal_id}_subtask_4",
                        "description": f"Validate solution for: {goal_description}",
                        "type": "validation",
                        "dependencies": [f"{goal_id}_subtask_3"]
                    }
                ]
        
        elif strategy == "parallel_tasks":
            # Parallel tasks with minimal dependencies
            subtasks = [
                {
                    "id": f"{goal_id}_subtask_1",
                    "description": f"Research component for: {goal_description}",
                    "type": "research",
                    "dependencies": []
                },
                {
                    "id": f"{goal_id}_subtask_2",
                    "description": f"Development component for: {goal_description}",
                    "type": "code",
                    "dependencies": []
                },
                {
                    "id": f"{goal_id}_subtask_3",
                    "description": f"Documentation component for: {goal_description}",
                    "type": "documentation",
                    "dependencies": []
                },
                {
                    "id": f"{goal_id}_subtask_4",
                    "description": f"Integration of all components for: {goal_description}",
                    "type": "integration",
                    "dependencies": [f"{goal_id}_subtask_1", f"{goal_id}_subtask_2", f"{goal_id}_subtask_3"]
                }
            ]
        
        elif strategy == "research_first":
            # Research-heavy approach
            subtasks = [
                {
                    "id": f"{goal_id}_subtask_1",
                    "description": f"Conduct comprehensive research on: {goal_description}",
                    "type": "research",
                    "dependencies": []
                },
                {
                    "id": f"{goal_id}_subtask_2",
                    "description": f"Analyze research findings for: {goal_description}",
                    "type": "analysis",
                    "dependencies": [f"{goal_id}_subtask_1"]
                },
                {
                    "id": f"{goal_id}_subtask_3",
                    "description": f"Develop preliminary solution for: {goal_description}",
                    "type": "development",
                    "dependencies": [f"{goal_id}_subtask_2"]
                },
                {
                    "id": f"{goal_id}_subtask_4",
                    "description": f"Gather feedback on preliminary solution for: {goal_description}",
                    "type": "feedback",
                    "dependencies": [f"{goal_id}_subtask_3"]
                },
                {
                    "id": f"{goal_id}_subtask_5",
                    "description": f"Refine solution based on feedback for: {goal_description}",
                    "type": "refinement",
                    "dependencies": [f"{goal_id}_subtask_4"]
                }
            ]
        
        # Add goal context to each subtask
        for subtask in subtasks:
            subtask["goal_id"] = goal_id
            subtask["goal_description"] = goal_description
            subtask["context"] = goal_context
            subtask["created_at"] = datetime.now().isoformat()
        
        # Log the decomposition completion
        self._log_execution_event(goal_id, "decomposition_complete", "Completed goal decomposition", {"subtasks": subtasks})
        
        # Store subtasks in memory
        for subtask in subtasks:
            self._store_in_memory(goal_id, "subtask", subtask, "subtask_created")
        
        return subtasks
    
    def _assign_agents(self, subtasks: List[Dict[str, Any]], goal_id: str) -> List[Dict[str, Any]]:
        """
        Assign agents to subtasks based on their capabilities.
        
        Args:
            subtasks: List of subtasks
            goal_id: ID of the parent goal
            
        Returns:
            List of subtasks with assigned agents
        """
        logger.info(f"Assigning agents to subtasks for goal {goal_id}")
        
        # Log the assignment start
        self._log_execution_event(goal_id, "assignment_start", "Started agent assignment", {"subtasks": subtasks})
        
        assigned_subtasks = []
        
        for subtask in subtasks:
            subtask_id = subtask["id"]
            subtask_description = subtask["description"]
            subtask_type = subtask.get("type", "")
            
            # Find the best agent for this subtask
            agent_name = find_agent(subtask_description, subtask_type)
            
            # Add agent assignment to the subtask
            assigned_subtask = subtask.copy()
            assigned_subtask["assigned_agent"] = agent_name
            assigned_subtask["assignment_time"] = datetime.now().isoformat()
            
            assigned_subtasks.append(assigned_subtask)
            
            # Log the assignment
            self._log_execution_event(
                goal_id, 
                "subtask_assigned", 
                f"Assigned subtask {subtask_id} to agent {agent_name}", 
                {"subtask_id": subtask_id, "agent": agent_name}
            )
            
            # Store the assignment in memory
            self._store_in_memory(
                goal_id, 
                "subtask_assignment", 
                assigned_subtask, 
                "subtask_assigned"
            )
        
        # Log the assignment completion
        self._log_execution_event(
            goal_id, 
            "assignment_complete", 
            "Completed agent assignment", 
            {"assigned_subtasks": assigned_subtasks}
        )
        
        return assigned_subtasks
    
    def _sequence_subtasks(self, subtasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sequence subtasks based on dependencies.
        
        Args:
            subtasks: List of subtasks with assigned agents
            
        Returns:
            List of sequenced subtasks
        """
        # Create a dependency graph
        dependency_graph = {}
        for subtask in subtasks:
            subtask_id = subtask["id"]
            dependencies = subtask.get("dependencies", [])
            dependency_graph[subtask_id] = dependencies
        
        # Perform topological sort to sequence subtasks
        sequenced_ids = self._topological_sort(dependency_graph)
        
        # Create a map of subtask ID to subtask
        subtask_map = {subtask["id"]: subtask for subtask in subtasks}
        
        # Create the sequenced list of subtasks
        sequenced_subtasks = [subtask_map[subtask_id] for subtask_id in sequenced_ids]
        
        # Add sequence numbers to subtasks
        for i, subtask in enumerate(sequenced_subtasks):
            subtask["sequence_number"] = i + 1
        
        return sequenced_subtasks
    
    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """
        Perform topological sort on a dependency graph.
        
        Args:
            graph: Dependency graph where keys are nodes and values are dependencies
            
        Returns:
            Topologically sorted list of nodes
        """
        # Initialize variables
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(node):
            if node in temp_visited:
                # Cyclic dependency detected
                raise ValueError(f"Cyclic dependency detected involving node {node}")
            
            if node not in visited:
                temp_visited.add(node)
                
                # Visit dependencies
                for dependency in graph.get(node, []):
                    visit(dependency)
                
                temp_visited.remove(node)
                visited.add(node)
                result.append(node)
        
        # Visit all nodes
        for node in graph:
            if node not in visited:
                visit(node)
        
        # Reverse the result to get the correct order
        return result[::-1]
    
    def _execute_subtasks(self, subtasks: List[Dict[str, Any]], goal_id: str) -> List[Dict[str, Any]]:
        """
        Execute subtasks in sequence.
        
        Args:
            subtasks: List of sequenced subtasks
            goal_id: ID of the parent goal
            
        Returns:
            List of execution results
        """
        logger.info(f"Executing subtasks for goal {goal_id}")
        
        # Log the execution start
        self._log_execution_event(goal_id, "execution_start", "Started subtask execution", {"subtasks": subtasks})
        
        results = []
        
        for subtask in subtasks:
            subtask_id = subtask["id"]
            agent_name = subtask["assigned_agent"]
            
            # Log the subtask execution start
            self._log_execution_event(
                goal_id, 
                "subtask_execution_start", 
                f"Started execution of subtask {subtask_id} by agent {agent_name}", 
                {"subtask_id": subtask_id, "agent": agent_name}
            )
            
            # Update subtask status in memory
            subtask["status"] = "in_progress"
            subtask["execution_start_time"] = datetime.now().isoformat()
            self._store_in_memory(goal_id, "subtask_status", subtask, "subtask_in_progress")
            
            try:
                # Route the subtask to the assigned agent
                result = self.agent_router.route_task(subtask, agent_name, goal_id)
                
                # Update subtask with result
                subtask["status"] = result.get("status", "unknown")
                subtask["result"] = result
                subtask["execution_end_time"] = datetime.now().isoformat()
                
                # Store the result in memory
                self._store_in_memory(
                    goal_id, 
                    "subtask_result", 
                    {"subtask_id": subtask_id, "result": result}, 
                    "subtask_completed"
                )
                
                # Log the subtask execution completion
                self._log_execution_event(
                    goal_id, 
                    "subtask_execution_complete", 
                    f"Completed execution of subtask {subtask_id} by agent {agent_name}", 
                    {"subtask_id": subtask_id, "agent": agent_name, "result": result}
                )
                
                # Check for failure
                if result.get("status") != "success":
                    # Log the failure
                    error_msg = result.get("error", "Unknown error")
                    self._log_execution_event(
                        goal_id, 
                        "subtask_execution_failed", 
                        f"Failed execution of subtask {subtask_id}: {error_msg}", 
                        {"subtask_id": subtask_id, "error": error_msg}
                    )
                    
                    # Decide whether to escalate or continue
                    if self._should_escalate(subtask, result):
                        # Escalate the issue
                        self._escalate_issue(
                            goal_id, 
                            "subtask_execution_failed", 
                            f"Failed execution of subtask {subtask_id}: {error_msg}", 
                            {"subtask": subtask, "result": result}
                        )
                        
                        # Depending on the escalation policy, we might want to abort execution
                        escalation_policy = self.planner_config.get("escalation_policy", {})
                        if escalation_policy.get("abort_on_failure", False):
                            logger.warning(f"Aborting execution of goal {goal_id} due to subtask failure")
                            break
            
            except Exception as e:
                error_msg = f"Error executing subtask {subtask_id}: {str(e)}"
                logger.error(error_msg)
                
                # Update subtask status
                subtask["status"] = "failed"
                subtask["error"] = error_msg
                subtask["execution_end_time"] = datetime.now().isoformat()
                
                # Store the error in memory
                self._store_in_memory(
                    goal_id, 
                    "subtask_error", 
                    {"subtask_id": subtask_id, "error": error_msg}, 
                    "subtask_failed"
                )
                
                # Log the failure
                self._log_execution_event(
                    goal_id, 
                    "subtask_execution_error", 
                    error_msg, 
                    {"subtask_id": subtask_id, "error": str(e)}
                )
                
                # Escalate the issue
                self._escalate_issue(
                    goal_id, 
                    "subtask_execution_error", 
                    error_msg, 
                    {"subtask": subtask, "error": str(e)}
                )
                
                # Depending on the escalation policy, we might want to abort execution
                escalation_policy = self.planner_config.get("escalation_policy", {})
                if escalation_policy.get("abort_on_failure", False):
                    logger.warning(f"Aborting execution of goal {goal_id} due to subtask error")
                    break
            
            # Add the result to the list
            results.append({
                "subtask_id": subtask_id,
                "agent": agent_name,
                "status": subtask.get("status", "unknown"),
                "result": subtask.get("result", {}),
                "error": subtask.get("error", None),
                "execution_start_time": subtask.get("execution_start_time", ""),
                "execution_end_time": subtask.get("execution_end_time", "")
            })
        
        # Log the execution completion
        self._log_execution_event(goal_id, "execution_complete", "Completed subtask execution", {"results": results})
        
        return results
    
    def _compile_results(self, goal: Dict[str, Any], results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compile the final results of goal execution.
        
        Args:
            goal: Original goal
            results: List of subtask execution results
            
        Returns:
            Compiled results
        """
        goal_id = goal["id"]
        
        # Count successes and failures
        success_count = sum(1 for r in results if r.get("status") == "success")
        failure_count = sum(1 for r in results if r.get("status") not in ["success", "unknown"])
        
        # Determine overall status
        if failure_count == 0:
            overall_status = "success"
        elif success_count > 0:
            overall_status = "partial_success"
        else:
            overall_status = "failed"
        
        # Compile the results
        compiled_results = {
            "goal_id": goal_id,
            "goal_description": goal.get("description", ""),
            "status": overall_status,
            "subtask_count": len(results),
            "success_count": success_count,
            "failure_count": failure_count,
            "start_time": self.active_goals[goal_id].get("start_time", ""),
            "completion_time": datetime.now().isoformat(),
            "subtask_results": results,
            "summary": self._generate_summary(goal, results)
        }
        
        return compiled_results
    
    def _generate_summary(self, goal: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of the goal execution.
        
        Args:
            goal: Original goal
            results: List of subtask execution results
            
        Returns:
            Summary text
        """
        goal_description = goal.get("description", "")
        success_count = sum(1 for r in results if r.get("status") == "success")
        failure_count = sum(1 for r in results if r.get("status") not in ["success", "unknown"])
        
        if failure_count == 0:
            status_text = "successfully completed"
        elif success_count > 0:
            status_text = "partially completed"
        else:
            status_text = "failed to complete"
        
        summary = f"Goal '{goal_description}' was {status_text} with {success_count} successful subtasks and {failure_count} failed subtasks."
        
        # Add details about successful subtasks
        if success_count > 0:
            successful_subtasks = [r for r in results if r.get("status") == "success"]
            summary += f" Successfully completed subtasks include: {', '.join(r.get('subtask_id', '') for r in successful_subtasks[:3])}"
            if success_count > 3:
                summary += f" and {success_count - 3} more."
        
        # Add details about failed subtasks
        if failure_count > 0:
            failed_subtasks = [r for r in results if r.get("status") not in ["success", "unknown"]]
            summary += f" Failed subtasks include: {', '.join(r.get('subtask_id', '') for r in failed_subtasks[:3])}"
            if failure_count > 3:
                summary += f" and {failure_count - 3} more."
        
        return summary
    
    def _should_escalate(self, subtask: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """
        Determine whether an issue should be escalated.
        
        Args:
            subtask: Subtask details
            result: Execution result
            
        Returns:
            True if the issue should be escalated, False otherwise
        """
        # Get escalation policy from planner config
        escalation_policy = self.planner_config.get("escalation_policy", {})
        
        # Check confidence threshold
        confidence = result.get("confidence", 1.0)
        confidence_threshold = escalation_policy.get("confidence_threshold", 0.6)
        if confidence < confidence_threshold:
            return True
        
        # Check retry attempts
        retry_attempts = result.get("retry_attempts", 0)
        max_retry_attempts = escalation_policy.get("max_retry_attempts", 3)
        if retry_attempts >= max_retry_attempts:
            return True
        
        # Check for critical errors
        error = result.get("error", "")
        if "critical" in error.lower() or "fatal" in error.lower():
            return True
        
        return False
    
    def _escalate_issue(self, goal_id: str, issue_type: str, message: str, details: Dict[str, Any]) -> None:
        """
        Escalate an issue to the Guardian Agent or human.
        
        Args:
            goal_id: ID of the goal
            issue_type: Type of issue
            message: Issue message
            details: Issue details
        """
        # Get escalation policy from planner config
        escalation_policy = self.planner_config.get("escalation_policy", {})
        escalate_to = escalation_policy.get("escalate_to", ["guardian", "human"])
        
        # Log the escalation
        self._log_execution_event(goal_id, "issue_escalated", message, {
            "issue_type": issue_type,
            "escalate_to": escalate_to,
            "details": details
        })
        
        # Store the escalation in memory
        self._store_in_memory(goal_id, "escalation", {
            "issue_type": issue_type,
            "message": message,
            "escalate_to": escalate_to,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }, "issue_escalated")
        
        # Escalate to Guardian Agent if specified
        if "guardian" in escalate_to:
            try:
                # Route the escalation to the Guardian Agent
                escalation_task = {
                    "id": f"{goal_id}_escalation_{int(time.time())}",
                    "description": f"Escalated issue: {message}",
                    "type": "escalation",
                    "issue_type": issue_type,
                    "goal_id": goal_id,
                    "details": details,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.agent_router.route_task(escalation_task, "guardian", goal_id)
                
                logger.info(f"Escalated issue to Guardian Agent: {message}")
            
            except Exception as e:
                logger.error(f"Error escalating to Guardian Agent: {str(e)}")
        
        # TODO: Implement human escalation if specified
        if "human" in escalate_to:
            logger.info(f"Human escalation not yet implemented for issue: {message}")
    
    def _log_execution_event(self, goal_id: str, event_type: str, message: str, details: Dict[str, Any]) -> None:
        """
        Log an execution event to the planner_execution_log.json file.
        
        Args:
            goal_id: ID of the goal
            event_type: Type of event
            message: Event message
            details: Event details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "goal_id": goal_id,
            "event_type": event_type,
            "message": message,
            "details": details
        }
        
        try:
            # Read existing logs
            logs = []
            log_file = "/app/logs/planner_execution_log.json"
            
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    try:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = []
                    except json.JSONDecodeError:
                        logs = []
            
            # Append new log entry
            logs.append(log_entry)
            
            # Write back to file
            with open(log_file, "w") as f:
                json.dump(logs, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error logging execution event: {str(e)}")
    
    def _store_in_memory(self, goal_id: str, entry_type: str, data: Dict[str, Any], status: str) -> None:
        """
        Store data in vector memory.
        
        Args:
            goal_id: ID of the goal
            entry_type: Type of memory entry
            data: Data to store
            status: Status of the entry
        """
        try:
            # Prepare memory entry
            memory_entry = {
                "goal_id": goal_id,
                "entry_type": entry_type,
                "data": data,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in vector memory
            self.vector_memory.add_memory(
                text=json.dumps(memory_entry),
                metadata={
                    "goal_id": goal_id,
                    "entry_type": entry_type,
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        except Exception as e:
            logger.error(f"Error storing in memory: {str(e)}")
    
    def get_goal_status(self, goal_id: str) -> Dict[str, Any]:
        """
        Get the status of a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Goal status information
        """
        if goal_id not in self.active_goals:
            # Try to retrieve from memory
            try:
                memories = self.vector_memory.search(
                    query=f"goal_id:{goal_id}",
                    metadata_filter={"entry_type": "goal"},
                    limit=1
                )
                
                if memories:
                    memory_data = json.loads(memories[0]["text"])
                    return {
                        "goal_id": goal_id,
                        "status": "retrieved_from_memory",
                        "data": memory_data,
                        "timestamp": datetime.now().isoformat()
                    }
                
                return {
                    "goal_id": goal_id,
                    "status": "not_found",
                    "timestamp": datetime.now().isoformat()
                }
            
            except Exception as e:
                logger.error(f"Error retrieving goal from memory: {str(e)}")
                return {
                    "goal_id": goal_id,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return self.active_goals[goal_id]
    
    def resume_goal(self, goal_id: str) -> Dict[str, Any]:
        """
        Resume a partially completed goal.
        
        Args:
            goal_id: ID of the goal to resume
            
        Returns:
            Result of resuming the goal
        """
        # Check if the goal is already active
        if goal_id in self.active_goals:
            return {
                "status": "already_active",
                "goal_id": goal_id,
                "message": "Goal is already active",
                "timestamp": datetime.now().isoformat()
            }
        
        # Try to retrieve the goal from memory
        try:
            # Get the goal
            goal_memories = self.vector_memory.search(
                query=f"goal_id:{goal_id}",
                metadata_filter={"entry_type": "goal"},
                limit=1
            )
            
            if not goal_memories:
                return {
                    "status": "not_found",
                    "goal_id": goal_id,
                    "message": "Goal not found in memory",
                    "timestamp": datetime.now().isoformat()
                }
            
            goal_data = json.loads(goal_memories[0]["text"])
            goal = goal_data.get("data", {})
            
            # Get completed subtasks
            completed_memories = self.vector_memory.search(
                query=f"goal_id:{goal_id}",
                metadata_filter={"entry_type": "subtask_result", "status": "subtask_completed"},
                limit=100
            )
            
            completed_subtask_ids = set()
            for memory in completed_memories:
                memory_data = json.loads(memory["text"])
                subtask_data = memory_data.get("data", {})
                subtask_id = subtask_data.get("subtask_id", "")
                if subtask_id:
                    completed_subtask_ids.add(subtask_id)
            
            # Get all subtasks
            subtask_memories = self.vector_memory.search(
                query=f"goal_id:{goal_id}",
                metadata_filter={"entry_type": "subtask"},
                limit=100
            )
            
            subtasks = []
            for memory in subtask_memories:
                memory_data = json.loads(memory["text"])
                subtask = memory_data.get("data", {})
                subtasks.append(subtask)
            
            # Filter out completed subtasks
            remaining_subtasks = [s for s in subtasks if s["id"] not in completed_subtask_ids]
            
            if not remaining_subtasks:
                return {
                    "status": "already_completed",
                    "goal_id": goal_id,
                    "message": "Goal has already been completed",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Log the resumption
            self._log_execution_event(
                goal_id, 
                "goal_resumed", 
                f"Resuming goal {goal_id}", 
                {"completed_subtasks": len(completed_subtask_ids), "remaining_subtasks": len(remaining_subtasks)}
            )
            
            # Process the remaining subtasks
            # First, assign agents to the remaining subtasks
            assigned_subtasks = self._assign_agents(remaining_subtasks, goal_id)
            
            # Sequence the remaining subtasks
            sequenced_subtasks = self._sequence_subtasks(assigned_subtasks)
            
            # Execute the remaining subtasks
            results = self._execute_subtasks(sequenced_subtasks, goal_id)
            
            # Compile the final results
            final_result = self._compile_results(goal, results)
            
            # Log the completion of the resumed goal
            self._log_execution_event(
                goal_id, 
                "resumed_goal_complete", 
                f"Completed resumed goal {goal_id}", 
                final_result
            )
            
            # Store the final result in memory
            self._store_in_memory(goal_id, "goal_result", final_result, "goal_complete")
            
            return {
                "status": "success",
                "goal_id": goal_id,
                "message": "Goal resumed and completed",
                "result": final_result,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            error_msg = f"Error resuming goal {goal_id}: {str(e)}"
            logger.error(error_msg)
            
            # Log the failure
            self._log_execution_event(
                goal_id, 
                "goal_resume_failed", 
                error_msg, 
                {"error": str(e)}
            )
            
            return {
                "status": "error",
                "goal_id": goal_id,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def replay_goal_history(self, goal_id: str) -> Dict[str, Any]:
        """
        Replay the history of a goal from memory.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Goal history
        """
        try:
            # Get all memories related to the goal
            memories = self.vector_memory.search(
                query=f"goal_id:{goal_id}",
                limit=1000
            )
            
            if not memories:
                return {
                    "status": "not_found",
                    "goal_id": goal_id,
                    "message": "Goal not found in memory",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Sort memories by timestamp
            sorted_memories = sorted(
                memories,
                key=lambda m: json.loads(m["text"]).get("timestamp", "")
            )
            
            # Extract events from memories
            events = []
            for memory in sorted_memories:
                memory_data = json.loads(memory["text"])
                events.append({
                    "entry_type": memory_data.get("entry_type", "unknown"),
                    "status": memory_data.get("status", "unknown"),
                    "timestamp": memory_data.get("timestamp", ""),
                    "data": memory_data.get("data", {})
                })
            
            return {
                "status": "success",
                "goal_id": goal_id,
                "event_count": len(events),
                "events": events,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            error_msg = f"Error replaying goal history for {goal_id}: {str(e)}"
            logger.error(error_msg)
            
            return {
                "status": "error",
                "goal_id": goal_id,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }

# Create a singleton instance
_planner_orchestrator = None

def get_planner_orchestrator() -> PlannerOrchestrator:
    """
    Get the singleton instance of the planner orchestrator.
    
    Returns:
        PlannerOrchestrator instance
    """
    global _planner_orchestrator
    if _planner_orchestrator is None:
        _planner_orchestrator = PlannerOrchestrator()
    return _planner_orchestrator

# For API integration
def process_goal(goal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a high-level goal.
    
    Args:
        goal: High-level goal details
        
    Returns:
        Goal execution results
    """
    orchestrator = get_planner_orchestrator()
    return orchestrator.process_goal(goal)

def get_goal_status(goal_id: str) -> Dict[str, Any]:
    """
    Get the status of a goal.
    
    Args:
        goal_id: ID of the goal
        
    Returns:
        Goal status information
    """
    orchestrator = get_planner_orchestrator()
    return orchestrator.get_goal_status(goal_id)

def resume_goal(goal_id: str) -> Dict[str, Any]:
    """
    Resume a partially completed goal.
    
    Args:
        goal_id: ID of the goal to resume
        
    Returns:
        Result of resuming the goal
    """
    orchestrator = get_planner_orchestrator()
    return orchestrator.resume_goal(goal_id)

def replay_goal_history(goal_id: str) -> Dict[str, Any]:
    """
    Replay the history of a goal from memory.
    
    Args:
        goal_id: ID of the goal
        
    Returns:
        Goal history
    """
    orchestrator = get_planner_orchestrator()
    return orchestrator.replay_goal_history(goal_id)
