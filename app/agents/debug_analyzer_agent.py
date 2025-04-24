"""
Debug Analyzer Agent Module

This module implements the Debug Analyzer agent, which acts as a diagnostic tool
for analyzing failed or incomplete loop executions within the Promethios architecture.
"""

import os
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import schemas
from app.schemas.debug_schema import LoopDebugRequest, LoopDebugResult, LoopIssue, RepairSuggestion

# Import memory operations
from app.modules.memory_writer import write_memory, read_memory
from app.modules.orchestrator_memory_enhanced import log_loop_event

# Import project state operations
from app.modules.project_state import read_project_state

# Import snapshot operations
from app.utils.snapshot_manager import get_loop_snapshot

# Configure logging
logger = logging.getLogger("app.agents.debug_analyzer")

class DebugAnalyzerAgent:
    """
    Debug Analyzer Agent implementation.
    
    This agent acts as a diagnostic tool for analyzing failed or incomplete loop executions,
    identifying issues, and suggesting repairs.
    """
    
    def __init__(self):
        """Initialize the Debug Analyzer Agent with required configuration."""
        self.name = "debug-analyzer-agent"
        self.role = "Loop Diagnostic Tool"
        self.tools = ["analyze_memory", "diagnose_loop", "recommend_fix"]
        self.permissions = ["read_memory", "write_memory"]
        self.description = "Diagnostic agent for analyzing failed or incomplete loop executions"
        self.version = "1.0.0"
        self.status = "active"
        self.tone_profile = {
            "style": "technical",
            "emotion": "neutral",
            "vibe": "analytical",
            "persona": "Precise diagnostician with a focus on root cause analysis"
        }
        self.schema_path = "schemas/debug_schema.py"
        self.trust_score = 0.90
        self.contract_version = "1.0.0"
    
    async def analyze_loop(self, 
                request: LoopDebugRequest) -> LoopDebugResult:
        """
        Analyze a failed or incomplete loop execution.
        
        Args:
            request: The debug request containing loop_id, project_id, and optional filters
            
        Returns:
            LoopDebugResult containing the diagnosis of the loop execution
        """
        try:
            logger.info(f"Running Debug Analyzer agent for loop: {request.loop_id}, project: {request.project_id}")
            print(f"🔍 Debug Analyzer analyzing loop '{request.loop_id}' for project '{request.project_id}'")
            
            # Log the start of the analysis
            await log_loop_event(
                loop_id=request.loop_id,
                project_id=request.project_id,
                agent="debug_analyzer",
                task="analyze_loop_execution",
                result_tag=f"loop_diagnosis_{request.loop_id}_v{request.version}",
                status="in_progress",
                additional_data={"version": request.version}
            )
            
            # Read project state
            project_state = read_project_state(request.project_id)
            
            # Initialize analysis variables
            issues = []
            memory_tags_checked = []
            agents_involved = []
            failed_agents = []
            
            # Get loop snapshot if available
            loop_snapshot = None
            try:
                loop_snapshot = await get_loop_snapshot(request.loop_id)
                if loop_snapshot:
                    memory_tags_checked.append(f"loop_snapshot_{request.loop_id}")
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
                    affected_memory_tags=[f"loop_snapshot_{request.loop_id}"]
                ))
            
            # Check memory tags for specific agents
            memory_tags_to_check = [
                f"forge_build_log_{request.loop_id}",
                f"critic_review_{request.loop_id}",
                f"pessimist_reject_log_{request.loop_id}",
                f"sage_summary_{request.loop_id}"
            ]
            
            # Filter memory tags if agent_filter is provided
            if request.agent_filter:
                filtered_tags = []
                for tag in memory_tags_to_check:
                    for agent in request.agent_filter:
                        if agent.lower() in tag.lower():
                            filtered_tags.append(tag)
                            break
                memory_tags_to_check = filtered_tags
            
            # Check each memory tag
            for tag in memory_tags_to_check:
                try:
                    memory_data = await read_memory(
                        project_id=request.project_id,
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
            if request.raw_log_text:
                # Simple analysis of raw log text
                log_lines = request.raw_log_text.split("\n")
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
            debug_result = LoopDebugResult(
                loop_id=request.loop_id,
                project_id=request.project_id,
                issues=issues,
                agents=agents_involved,
                failed_agents=failed_agents,
                memory_tags_checked=memory_tags_checked,
                recommendations=recommendations,
                confidence_score=confidence_score,
                analysis_timestamp=datetime.utcnow().isoformat(),
                version=request.version
            )
            
            # Log the debug result
            await write_memory(
                project_id=request.project_id,
                tag=f"loop_diagnosis_{request.loop_id}_v{request.version}",
                value=debug_result.dict()
            )
            
            # Log the completion of the analysis
            await log_loop_event(
                loop_id=request.loop_id,
                project_id=request.project_id,
                agent="debug_analyzer",
                task="analyze_loop_execution",
                result_tag=f"loop_diagnosis_{request.loop_id}_v{request.version}",
                status="completed",
                additional_data={
                    "version": request.version,
                    "issues_count": len(issues),
                    "failed_agents": failed_agents,
                    "confidence_score": confidence_score
                }
            )
            
            logger.info(f"✅ Debug Analyzer completed analysis with confidence score {confidence_score}")
            return debug_result
            
        except Exception as e:
            error_msg = f"Error running Debug Analyzer agent: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            
            # Try to log the error
            try:
                await log_loop_event(
                    loop_id=request.loop_id,
                    project_id=request.project_id,
                    agent="debug_analyzer",
                    task="analyze_loop_execution",
                    result_tag=f"loop_diagnosis_{request.loop_id}_v{request.version}",
                    status="failed",
                    additional_data={"error": error_msg}
                )
            except Exception as log_error:
                logger.error(f"❌ Error logging failure: {str(log_error)}")
            
            # Return error response that will pass schema validation
            return LoopDebugResult(
                loop_id=request.loop_id,
                project_id=request.project_id,
                issues=[
                    LoopIssue(
                        issue_type="analyzer_failure",
                        description=f"Debug Analyzer failed: {error_msg}",
                        severity="critical",
                        affected_agent="debug_analyzer",
                        affected_memory_tags=[]
                    )
                ],
                agents=[],
                failed_agents=["debug_analyzer"],
                memory_tags_checked=[],
                recommendations=[
                    RepairSuggestion(
                        suggestion_type="retry",
                        description="Retry Debug Analyzer with more detailed logs",
                        priority=1,
                        target_agent="debug_analyzer",
                        required_changes=["Provide raw_log_text", "Check system logs"],
                        expected_outcome="Debug Analyzer should complete with more information"
                    )
                ],
                confidence_score=0.0,
                analysis_timestamp=datetime.utcnow().isoformat(),
                version=request.version
            )
    
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
                    expected_outcome=f"{agent.upper()} should complete with the required memory data"
                ))
            
            # Check for agent failures
            agent_failure_issues = [i for i in agent_specific_issues if i.issue_type == "agent_failure"]
            if agent_failure_issues:
                recommendations.append(RepairSuggestion(
                    suggestion_type="retry",
                    description=f"Retry {agent} with modified parameters",
                    priority=2,
                    target_agent=agent,
                    required_changes=["Increase timeout", "Provide fallback data"],
                    expected_outcome=f"{agent.upper()} should complete with modified parameters"
                ))
            
            # Check for step failures
            step_failure_issues = [i for i in agent_specific_issues if i.issue_type == "step_failure"]
            if step_failure_issues:
                recommendations.append(RepairSuggestion(
                    suggestion_type="skip_step",
                    description=f"Skip failed steps in {agent} or provide alternative implementation",
                    priority=3,
                    target_agent=agent,
                    required_changes=["Mark steps as optional", "Provide alternative implementation"],
                    expected_outcome=f"{agent.upper()} should complete by skipping problematic steps"
                ))
        
        # Add general recommendations if no specific ones were generated
        if not recommendations:
            # Check for missing snapshot
            if any(i.issue_type == "missing_snapshot" for i in issues):
                recommendations.append(RepairSuggestion(
                    suggestion_type="create_snapshot",
                    description="Create a new loop snapshot",
                    priority=1,
                    target_agent="orchestrator",
                    required_changes=["Trigger snapshot creation"],
                    expected_outcome="Loop snapshot should be available for analysis"
                ))
            
            # Add fallback recommendation
            recommendations.append(RepairSuggestion(
                suggestion_type="restart_loop",
                description="Restart the loop with additional logging",
                priority=4,
                target_agent="orchestrator",
                required_changes=["Enable verbose logging", "Set longer timeouts"],
                expected_outcome="Loop should complete with more diagnostic information"
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
            memory_tags_checked: List of memory tags successfully checked
            memory_tags_to_check: List of memory tags that should be checked
            loop_snapshot_available: Whether a loop snapshot was available
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Base confidence
        confidence = 0.5
        
        # Adjust based on memory tag coverage
        if memory_tags_to_check:
            memory_coverage = len(memory_tags_checked) / len(memory_tags_to_check)
            confidence += memory_coverage * 0.3
        
        # Adjust based on snapshot availability
        if loop_snapshot_available:
            confidence += 0.1
        
        # Adjust based on issues found
        if issues:
            # More issues generally means more confidence in the diagnosis
            issue_factor = min(len(issues) * 0.05, 0.2)
            confidence += issue_factor
            
            # But if we have analyzer failures, reduce confidence
            analyzer_failures = [i for i in issues if i.issue_type == "analyzer_failure"]
            if analyzer_failures:
                confidence -= 0.3
        else:
            # No issues found might mean we missed something
            confidence -= 0.1
        
        # Ensure confidence is between 0.0 and 1.0
        return max(0.0, min(1.0, confidence))
