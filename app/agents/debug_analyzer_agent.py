"""
Debug Analyzer Agent Module

This module implements the Debug Analyzer agent, which acts as a diagnostic tool
for analyzing failed or incomplete loop executions within the Promethios architecture.
"""

import os
import json
import logging
import traceback
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import Agent SDK
from agent_sdk.agent_sdk import Agent, validate_schema

# Configure logging
logger = logging.getLogger("app.agents.debug_analyzer")

# Import memory operations
try:
    from app.modules.memory_writer import write_memory, read_memory
    MEMORY_WRITER_AVAILABLE = True
except ImportError:
    MEMORY_WRITER_AVAILABLE = False
    logger.warning("⚠️ memory_writer import failed")
    
    # Mock implementations for testing
    async def write_memory(project_id, tag, value):
        logger.info(f"Mock memory write: {project_id}, {tag}, {len(str(value))} chars")
        return {"status": "success", "message": "Mock memory write successful"}
    
    async def read_memory(project_id, tag):
        logger.info(f"Mock memory read: {project_id}, {tag}")
        return {"status": "success", "data": {}}

# Import orchestrator memory operations
try:
    from app.modules.orchestrator_memory_enhanced import log_loop_event
    ORCHESTRATOR_MEMORY_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_MEMORY_AVAILABLE = False
    logger.warning("⚠️ orchestrator_memory_enhanced import failed")
    
    # Mock implementation for testing
    async def log_loop_event(loop_id, project_id, agent, task, result_tag, status, additional_data=None):
        logger.info(f"Mock log_loop_event: {loop_id}, {project_id}, {agent}, {task}, {result_tag}, {status}")
        return {"status": "success"}

# Import project state operations
try:
    from app.modules.project_state import read_project_state
    PROJECT_STATE_AVAILABLE = True
except ImportError:
    PROJECT_STATE_AVAILABLE = False
    logger.warning("⚠️ project_state import failed")
    
    # Mock implementation for testing
    def read_project_state(project_id):
        logger.info(f"Mock read_project_state: {project_id}")
        return {"loop_count": 0, "agents_involved": ["hal"], "files_created": []}

# Import snapshot operations
try:
    from app.utils.snapshot_manager import get_loop_snapshot
    SNAPSHOT_MANAGER_AVAILABLE = True
except ImportError:
    SNAPSHOT_MANAGER_AVAILABLE = False
    logger.warning("⚠️ snapshot_manager import failed")
    
    # Mock implementation for testing
    async def get_loop_snapshot(loop_id):
        logger.info(f"Mock get_loop_snapshot: {loop_id}")
        return None

class LoopIssue:
    """Class representing an issue identified in a loop execution."""
    
    def __init__(self, issue_type, description, severity, affected_agent=None, affected_memory_tags=None, timestamp=None):
        self.issue_type = issue_type
        self.description = description
        self.severity = severity
        self.affected_agent = affected_agent
        self.affected_memory_tags = affected_memory_tags or []
        self.timestamp = timestamp
    
    def dict(self):
        """Convert to dictionary representation."""
        return {
            "issue_type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
            "affected_agent": self.affected_agent,
            "affected_memory_tags": self.affected_memory_tags,
            "timestamp": self.timestamp
        }

class RepairSuggestion:
    """Class representing a repair suggestion for an identified issue."""
    
    def __init__(self, suggestion_type, description, priority, target_agent=None, required_changes=None, expected_outcome=None):
        self.suggestion_type = suggestion_type
        self.description = description
        self.priority = priority
        self.target_agent = target_agent
        self.required_changes = required_changes or []
        self.expected_outcome = expected_outcome or ""
    
    def dict(self):
        """Convert to dictionary representation."""
        return {
            "suggestion_type": self.suggestion_type,
            "description": self.description,
            "priority": self.priority,
            "target_agent": self.target_agent,
            "required_changes": self.required_changes,
            "expected_outcome": self.expected_outcome
        }

class DebugAnalyzerAgent(Agent):
    """
    Debug Analyzer Agent implementation.
    
    This agent acts as a diagnostic tool for analyzing failed or incomplete loop executions,
    identifying issues, and suggesting repairs.
    """
    
    def __init__(self, tools: List[str] = None):
        """Initialize the Debug Analyzer Agent with SDK compliance."""
        # Define agent properties
        name = "Debug Analyzer"
        role = "Loop Diagnostic Tool"
        tools_list = tools or ["analyze_memory", "diagnose_loop", "recommend_fix"]
        permissions = ["read_memory", "write_memory", "read_logs"]
        description = "Diagnostic agent for analyzing failed or incomplete loop executions, identifying issues, and suggesting repairs."
        tone_profile = {
            "analytical": "high",
            "technical": "high",
            "precise": "high",
            "neutral": "medium",
            "helpful": "medium"
        }
        
        # Define schema paths
        input_schema_path = "app/schemas/debug_analyzer/input_schema.json"
        output_schema_path = "app/schemas/debug_analyzer/output_schema.json"
        
        # Initialize the Agent base class
        super().__init__(
            name=name,
            role=role,
            tools=tools_list,
            permissions=permissions,
            description=description,
            tone_profile=tone_profile,
            schema_path=output_schema_path,
            version="1.0.0",
            status="active",
            trust_score=0.90,
            contract_version="1.0.0"
        )
        
        self.input_schema_path = input_schema_path
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against the input schema.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if validation succeeds, False otherwise
        """
        return validate_schema(data, self.input_schema_path)
    
    async def execute(self, loop_id: str, project_id: str, version: str = "1.0.0", 
                     agent_filter: List[str] = None, raw_log_text: str = None, 
                     task: str = None, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            loop_id: Unique identifier for the loop being analyzed
            project_id: Unique identifier for the project
            version: Version of the analysis request (optional)
            agent_filter: Optional list of agents to filter analysis by
            raw_log_text: Optional raw log text to analyze
            task: Task to be performed by the Debug Analyzer agent (optional)
            **kwargs: Additional arguments
            
        Returns:
            Dict containing the result of the execution
        """
        try:
            logger.info(f"DebugAnalyzerAgent.execute called with loop_id: {loop_id}, project_id: {project_id}")
            
            # Prepare input data for validation
            input_data = {
                "loop_id": loop_id,
                "project_id": project_id,
                "version": version
            }
            
            if agent_filter:
                input_data["agent_filter"] = agent_filter
            
            if raw_log_text:
                input_data["raw_log_text"] = raw_log_text
            
            if task:
                input_data["task"] = task
            
            # Add any additional kwargs to input data
            input_data.update(kwargs)
            
            # Validate input
            if not self.validate_input(input_data):
                logger.warning(f"Input validation failed for loop_id: {loop_id}")
            
            # Log the start of the analysis
            if ORCHESTRATOR_MEMORY_AVAILABLE:
                await log_loop_event(
                    loop_id=loop_id,
                    project_id=project_id,
                    agent="debug_analyzer",
                    task="analyze_loop_execution",
                    result_tag=f"loop_diagnosis_{loop_id}_v{version}",
                    status="in_progress",
                    additional_data={"version": version}
                )
            
            # Read project state
            project_state = {}
            if PROJECT_STATE_AVAILABLE:
                project_state = read_project_state(project_id)
            
            # Initialize analysis variables
            issues = []
            memory_tags_checked = []
            agents_involved = []
            failed_agents = []
            
            # Get loop snapshot if available
            loop_snapshot = None
            if SNAPSHOT_MANAGER_AVAILABLE:
                try:
                    loop_snapshot = await get_loop_snapshot(loop_id)
                    if loop_snapshot:
                        memory_tags_checked.append(f"loop_snapshot_{loop_id}")
                        # Extract agents involved from snapshot
                        if "agents_involved" in loop_snapshot:
                            agents_involved.extend(loop_snapshot["agents_involved"])
                        # Check for failed steps in snapshot
                        if "steps" in loop_snapshot:
                            for step in loop_snapshot["steps"]:
                                if step.get("status") == "failed":
                                    agent = step.get("agent")
                                    if agent and agent not in failed_agents:
                                        failed_agents.append(agent)
                                    issues.append(LoopIssue(
                                        issue_type="step_failure",
                                        description=f"Step '{step.get('name', 'unknown')}' failed during execution",
                                        severity="high",
                                        affected_agent=agent,
                                        affected_memory_tags=[],
                                        timestamp=step.get("timestamp")
                                    ))
                except Exception as e:
                    logger.warning(f"⚠️ Could not get loop snapshot: {str(e)}")
                    issues.append(LoopIssue(
                        issue_type="missing_snapshot",
                        description=f"Could not retrieve loop snapshot: {str(e)}",
                        severity="medium",
                        affected_agent=None,
                        affected_memory_tags=[f"loop_snapshot_{loop_id}"]
                    ))
            
            # Check memory tags for specific agents
            memory_tags_to_check = [
                f"forge_build_log_{loop_id}",
                f"critic_review_{loop_id}",
                f"pessimist_reject_log_{loop_id}",
                f"sage_summary_{loop_id}"
            ]
            
            # Filter memory tags if agent_filter is provided
            if agent_filter:
                filtered_tags = []
                for tag in memory_tags_to_check:
                    for agent in agent_filter:
                        if agent.lower() in tag.lower():
                            filtered_tags.append(tag)
                            break
                memory_tags_to_check = filtered_tags
            
            # Check each memory tag
            if MEMORY_WRITER_AVAILABLE:
                for tag in memory_tags_to_check:
                    try:
                        memory_data = await read_memory(
                            project_id=project_id,
                            tag=tag
                        )
                        memory_tags_checked.append(tag)
                        
                        # Extract agent from tag
                        agent = None
                        if "forge" in tag:
                            agent = "forge"
                        elif "critic" in tag:
                            agent = "critic"
                        elif "pessimist" in tag:
                            agent = "pessimist"
                        elif "sage" in tag:
                            agent = "sage"
                        
                        if agent and agent not in agents_involved:
                            agents_involved.append(agent)
                        
                        # Check for errors or failures in memory data
                        if isinstance(memory_data, dict):
                            if memory_data.get("status") == "failed" or memory_data.get("error"):
                                if agent and agent not in failed_agents:
                                    failed_agents.append(agent)
                                issues.append(LoopIssue(
                                    issue_type="agent_failure",
                                    description=f"{agent.upper() if agent else 'Unknown agent'} failed: {memory_data.get('error', 'Unknown error')}",
                                    severity="high",
                                    affected_agent=agent,
                                    affected_memory_tags=[tag],
                                    timestamp=memory_data.get("timestamp")
                                ))
                    except Exception as e:
                        logger.warning(f"⚠️ Could not read memory tag {tag}: {str(e)}")
                        issues.append(LoopIssue(
                            issue_type="missing_memory",
                            description=f"Memory tag {tag} is missing or inaccessible",
                            severity="medium",
                            affected_agent=None,
                            affected_memory_tags=[tag]
                        ))
            
            # Process raw log text if provided
            if raw_log_text:
                # Simple analysis of raw log text
                log_lines = raw_log_text.split("\n")
                for line in log_lines:
                    if "error" in line.lower() or "exception" in line.lower() or "failed" in line.lower():
                        # Extract agent name if present
                        agent = None
                        for potential_agent in ["hal", "critic", "forge", "orchestrator", "sage", "pessimist"]:
                            if potential_agent in line.lower():
                                agent = potential_agent
                                if agent not in agents_involved:
                                    agents_involved.append(agent)
                                if "failed" in line.lower() and agent not in failed_agents:
                                    failed_agents.append(agent)
                                break
                        
                        issues.append(LoopIssue(
                            issue_type="log_error",
                            description=f"Error detected in logs: {line.strip()}",
                            severity="medium",
                            affected_agent=agent,
                            affected_memory_tags=[]
                        ))
            
            # Generate repair suggestions based on identified issues
            recommendations = self._generate_repair_suggestions(issues, failed_agents, agents_involved)
            
            # Calculate confidence score based on available data
            confidence_score = self._calculate_confidence_score(
                issues=issues,
                memory_tags_checked=memory_tags_checked,
                memory_tags_to_check=memory_tags_to_check,
                loop_snapshot_available=loop_snapshot is not None
            )
            
            # Create debug result
            debug_result = {
                "loop_id": loop_id,
                "project_id": project_id,
                "issues": [issue.dict() for issue in issues],
                "agents": agents_involved,
                "failed_agents": failed_agents,
                "memory_tags_checked": memory_tags_checked,
                "recommendations": [rec.dict() for rec in recommendations],
                "confidence_score": confidence_score,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "version": version,
                "status": "success",
                "message": f"Analysis completed with {len(issues)} issues identified"
            }
            
            # Validate output
            if not self.validate_schema(debug_result):
                logger.warning(f"Output validation failed for debug result")
            
            # Log the debug result
            if MEMORY_WRITER_AVAILABLE:
                await write_memory(
                    project_id=project_id,
                    tag=f"loop_diagnosis_{loop_id}_v{version}",
                    value=debug_result
                )
            
            # Log the completion of the analysis
            if ORCHESTRATOR_MEMORY_AVAILABLE:
                await log_loop_event(
                    loop_id=loop_id,
                    project_id=project_id,
                    agent="debug_analyzer",
                    task="analyze_loop_execution",
                    result_tag=f"loop_diagnosis_{loop_id}_v{version}",
                    status="completed",
                    additional_data={
                        "version": version,
                        "issues_count": len(issues),
                        "failed_agents": failed_agents,
                        "confidence_score": confidence_score
                    }
                )
            
            logger.info(f"✅ Debug Analyzer completed analysis with confidence score {confidence_score}")
            return debug_result
            
        except Exception as e:
            error_msg = f"Error in DebugAnalyzerAgent.execute: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Try to log the error
            if ORCHESTRATOR_MEMORY_AVAILABLE:
                try:
                    await log_loop_event(
                        loop_id=loop_id,
                        project_id=project_id,
                        agent="debug_analyzer",
                        task="analyze_loop_execution",
                        result_tag=f"loop_diagnosis_{loop_id}_v{version}",
                        status="failed",
                        additional_data={"error": error_msg}
                    )
                except Exception as log_error:
                    logger.error(f"❌ Error logging failure: {str(log_error)}")
            
            # Return error response that will pass schema validation
            error_result = {
                "loop_id": loop_id,
                "project_id": project_id,
                "issues": [
                    {
                        "issue_type": "analyzer_failure",
                        "description": f"Debug Analyzer failed: {error_msg}",
                        "severity": "critical",
                        "affected_agent": "debug_analyzer",
                        "affected_memory_tags": []
                    }
                ],
                "agents": [],
                "failed_agents": ["debug_analyzer"],
                "memory_tags_checked": [],
                "recommendations": [
                    {
                        "suggestion_type": "retry",
                        "description": "Retry Debug Analyzer with more detailed logs",
                        "priority": 1,
                        "target_agent": "debug_analyzer",
                        "required_changes": ["Provide raw_log_text", "Check system logs"],
                        "expected_outcome": "Debug Analyzer should complete with more information"
                    }
                ],
                "confidence_score": 0.0,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "version": version,
                "status": "error",
                "message": error_msg
            }
            
            # Validate output
            if not self.validate_schema(error_result):
                logger.warning(f"Output validation failed for error result")
            
            return error_result
    
    def _generate_repair_suggestions(self, 
                              issues: List[LoopIssue],
                              failed_agents: List[str],
                              agents_involved: List[str]) -> List[RepairSuggestion]:
        """
        Generate repair suggestions based on identified issues.
        
        Args:
            issues: List of identified issues
            failed_agents: List of agents that failed during execution
            agents_involved: List of agents involved in the loop execution
            
        Returns:
            List of repair suggestions
        """
        recommendations = []
        
        # Group issues by agent
        agent_issues = {}
        for issue in issues:
            agent = issue.affected_agent
            if agent:
                if agent not in agent_issues:
                    agent_issues[agent] = []
                agent_issues[agent].append(issue)
        
        # Generate suggestions for each failed agent
        for agent in failed_agents:
            agent_specific_issues = agent_issues.get(agent, [])
            
            # Check for missing memory issues
            missing_memory_issues = [i for i in agent_specific_issues if i.issue_type == "missing_memory"]
            if missing_memory_issues:
                affected_tags = []
                for issue in missing_memory_issues:
                    if issue.affected_memory_tags:
                        affected_tags.extend(issue.affected_memory_tags)
                
                recommendations.append(RepairSuggestion(
                    suggestion_type="provide_memory",
                    description=f"Provide missing memory data for {agent}",
                    priority=1,
                    target_agent=agent,
                    required_changes=[f"Create or restore {tag}" for tag in affected_tags],
                    expected_outcome=f"Agent {agent} should be able to access required memory data"
                ))
            
            # Check for agent failure issues
            agent_failure_issues = [i for i in agent_specific_issues if i.issue_type == "agent_failure"]
            if agent_failure_issues:
                recommendations.append(RepairSuggestion(
                    suggestion_type="fix_agent",
                    description=f"Fix {agent} agent implementation",
                    priority=2,
                    target_agent=agent,
                    required_changes=["Check agent code for errors", "Verify agent dependencies"],
                    expected_outcome=f"Agent {agent} should execute without errors"
                ))
            
            # Check for step failure issues
            step_failure_issues = [i for i in agent_specific_issues if i.issue_type == "step_failure"]
            if step_failure_issues:
                recommendations.append(RepairSuggestion(
                    suggestion_type="retry_step",
                    description=f"Retry failed step for {agent}",
                    priority=3,
                    target_agent=agent,
                    required_changes=["Ensure prerequisites are met", "Check for transient errors"],
                    expected_outcome=f"Step should complete successfully on retry"
                ))
        
        # Add general recommendations if no specific ones were generated
        if not recommendations:
            if issues:
                recommendations.append(RepairSuggestion(
                    suggestion_type="general_fix",
                    description="Address identified issues and retry execution",
                    priority=1,
                    target_agent=None,
                    required_changes=["Fix identified issues", "Retry execution"],
                    expected_outcome="Loop should execute successfully"
                ))
            else:
                recommendations.append(RepairSuggestion(
                    suggestion_type="gather_more_info",
                    description="Gather more information about the loop execution",
                    priority=1,
                    target_agent=None,
                    required_changes=["Enable detailed logging", "Check system logs"],
                    expected_outcome="More information should be available for diagnosis"
                ))
        
        return recommendations
    
    def _calculate_confidence_score(self,
                             issues: List[LoopIssue],
                             memory_tags_checked: List[str],
                             memory_tags_to_check: List[str],
                             loop_snapshot_available: bool) -> float:
        """
        Calculate confidence score based on available data.
        
        Args:
            issues: List of identified issues
            memory_tags_checked: List of memory tags checked during analysis
            memory_tags_to_check: List of memory tags that should be checked
            loop_snapshot_available: Whether loop snapshot is available
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Base confidence
        confidence = 0.5
        
        # Adjust based on memory tags coverage
        if memory_tags_to_check:
            coverage = len(memory_tags_checked) / len(memory_tags_to_check)
            confidence += coverage * 0.2
        
        # Adjust based on loop snapshot availability
        if loop_snapshot_available:
            confidence += 0.1
        
        # Adjust based on issues found
        if issues:
            # More issues generally means more confidence in the analysis
            confidence += min(len(issues) * 0.05, 0.2)
        else:
            # No issues could mean either everything is fine or we missed something
            confidence -= 0.1
        
        # Ensure confidence is within bounds
        confidence = max(0.0, min(confidence, 1.0))
        
        return confidence

# Create an instance of the agent
debug_analyzer_agent = DebugAnalyzerAgent()

async def run_debug_analyzer_agent(loop_id: str, project_id: str, version: str = "1.0.0", 
                                  agent_filter: List[str] = None, raw_log_text: str = None,
                                  task: str = None) -> Dict[str, Any]:
    """
    Run the Debug Analyzer agent with the given parameters.
    
    This function provides backward compatibility with the legacy implementation
    while using the new Agent SDK pattern.
    
    Args:
        loop_id: Unique identifier for the loop being analyzed
        project_id: Unique identifier for the project
        version: Version of the analysis request (optional)
        agent_filter: Optional list of agents to filter analysis by
        raw_log_text: Optional raw log text to analyze
        task: Task to be performed by the Debug Analyzer agent (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    # Execute the agent
    return await debug_analyzer_agent.execute(
        loop_id=loop_id,
        project_id=project_id,
        version=version,
        agent_filter=agent_filter,
        raw_log_text=raw_log_text,
        task=task
    )

# memory_tag: healed_phase3.3
