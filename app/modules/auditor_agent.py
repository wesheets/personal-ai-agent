"""
Auditor Agent Module

This module provides comprehensive auditing capabilities for loop execution.
It analyzes loop execution traces to identify:
- Belief consistency issues
- Memory integrity problems
- Execution anomalies
- Potential security concerns
- Compliance violations
- Performance bottlenecks

The auditor agent runs automatically after loop completion and generates
detailed reports with issues, warnings, and recommendations for improving
loop execution quality and reliability.
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import uuid
import re
import statistics
import math
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    
    # Mock data for testing
    if key.startswith("loop_audit["):
        loop_id = key[11:-1]  # Extract loop_id from "loop_audit[loop_id]"
        return {
            "loop_id": loop_id,
            "audit_id": f"audit_{loop_id}_{int(time.time())}",
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": 0.85,
            "belief_consistency_score": 0.9,
            "memory_integrity_score": 0.8,
            "issues": [
                {
                    "type": "belief_inconsistency",
                    "severity": "warning",
                    "description": "Belief 'user_privacy' referenced inconsistently",
                    "location": "agent_3.output"
                }
            ],
            "warnings": [
                {
                    "type": "memory_access",
                    "description": "Redundant memory reads detected",
                    "count": 3
                }
            ],
            "recommendations": [
                {
                    "type": "performance",
                    "description": "Consider optimizing agent_2 execution",
                    "potential_improvement": "15% reduction in execution time"
                }
            ]
        }
    elif key.startswith("loop_audits_history["):
        # Return a list of previous audits for temporal analysis
        return [
            {
                "loop_id": "previous_loop_1",
                "audit_id": "audit_previous_loop_1",
                "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "overall_score": 0.82,
                "belief_consistency_score": 0.88,
                "memory_integrity_score": 0.79,
                "execution_score": 0.85,
                "security_score": 0.90,
                "issue_count": 2,
                "warning_count": 1,
                "recommendation_count": 2
            },
            {
                "loop_id": "previous_loop_2",
                "audit_id": "audit_previous_loop_2",
                "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "overall_score": 0.79,
                "belief_consistency_score": 0.85,
                "memory_integrity_score": 0.76,
                "execution_score": 0.82,
                "security_score": 0.88,
                "issue_count": 3,
                "warning_count": 2,
                "recommendation_count": 2
            }
        ]
    
    return None

# Mock function for writing to memory
# In a real implementation, this would write to a database or storage system
async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    # Simulate memory write
    await asyncio.sleep(0.1)
    logger.debug(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

class AuditorAgent:
    """
    Class for auditing loop execution and identifying issues.
    """
    
    def __init__(self):
        """Initialize a new AuditorAgent."""
        self.audits = {}  # loop_id -> audit results
        self.historical_audits = []  # List of previous audits for temporal analysis
        logger.info("Initialized auditor agent")
    
    async def audit_loop(self, loop_id: str, loop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit a loop execution.
        
        Args:
            loop_id: The ID of the loop to audit
            loop_data: The loop execution data
            
        Returns:
            Dictionary with audit results
        """
        logger.info(f"Auditing loop {loop_id}")
        
        # Load historical audits for temporal analysis
        await self._load_historical_audits()
        
        # Generate audit ID
        audit_id = str(uuid.uuid4())
        
        # Perform belief consistency check
        belief_consistency_score, belief_issues = self._check_belief_consistency(loop_data)
        
        # Perform memory integrity check
        memory_integrity_score, memory_issues = self._check_memory_integrity(loop_data)
        
        # Perform execution anomaly check with enhanced anomaly detection
        execution_score, execution_issues = self._check_execution_anomalies(loop_data)
        
        # Perform security check
        security_score, security_issues = self._check_security_concerns(loop_data)
        
        # Perform resource utilization check (new)
        resource_score, resource_issues = self._check_resource_utilization(loop_data)
        
        # Calculate overall score with weighted components
        overall_score = (
            belief_consistency_score * 0.25 +
            memory_integrity_score * 0.25 +
            execution_score * 0.20 +
            security_score * 0.20 +
            resource_score * 0.10
        )
        
        # Combine all issues
        all_issues = belief_issues + memory_issues + execution_issues + security_issues + resource_issues
        
        # Perform correlation analysis on issues (new)
        correlated_issues = self._perform_correlation_analysis(all_issues, loop_data)
        all_issues.extend(correlated_issues)
        
        # Generate warnings
        warnings = self._generate_warnings(loop_data, all_issues)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(loop_data, all_issues, warnings)
        
        # Perform temporal pattern analysis (new)
        temporal_patterns = self._analyze_temporal_patterns(loop_id, loop_data)
        if temporal_patterns:
            for pattern in temporal_patterns:
                if pattern["type"] == "issue_trend":
                    warnings.append({
                        "type": "recurring_issue_pattern",
                        "description": pattern["description"],
                        "trend": pattern["trend"],
                        "affected_components": pattern["affected_components"]
                    })
                elif pattern["type"] == "performance_trend":
                    recommendations.append({
                        "type": "performance_trend",
                        "description": pattern["description"],
                        "trend": pattern["trend"],
                        "potential_improvement": pattern["potential_improvement"]
                    })
        
        # Calculate risk scores for issues (new)
        risk_scored_issues = self._calculate_risk_scores(all_issues, loop_data)
        
        # Create audit result
        audit_result = {
            "audit_id": audit_id,
            "loop_id": loop_id,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": round(overall_score, 2),
            "belief_consistency_score": round(belief_consistency_score, 2),
            "memory_integrity_score": round(memory_integrity_score, 2),
            "execution_score": round(execution_score, 2),
            "security_score": round(security_score, 2),
            "resource_score": round(resource_score, 2),  # New score
            "issue_count": len(all_issues),
            "warning_count": len(warnings),
            "recommendation_count": len(recommendations),
            "issues": risk_scored_issues,  # Using risk-scored issues
            "warnings": warnings,
            "recommendations": recommendations,
            "temporal_patterns": temporal_patterns,  # New field
            "correlation_analysis": {  # New field
                "correlated_issue_count": len(correlated_issues),
                "correlation_strength": self._calculate_correlation_strength(all_issues)
            }
        }
        
        # Store audit result
        self.audits[loop_id] = audit_result
        
        # Add to historical audits for future temporal analysis
        self.historical_audits.append({
            "loop_id": loop_id,
            "audit_id": audit_id,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_score": round(overall_score, 2),
            "belief_consistency_score": round(belief_consistency_score, 2),
            "memory_integrity_score": round(memory_integrity_score, 2),
            "execution_score": round(execution_score, 2),
            "security_score": round(security_score, 2),
            "resource_score": round(resource_score, 2),
            "issue_count": len(all_issues),
            "warning_count": len(warnings),
            "recommendation_count": len(recommendations)
        })
        
        # Save to memory
        await write_to_memory(f"loop_audit[{loop_id}]", audit_result)
        await write_to_memory(f"loop_audits_history", self.historical_audits)
        
        logger.info(f"Completed audit for loop {loop_id}: score={overall_score:.2f}")
        return audit_result
    
    async def _load_historical_audits(self):
        """Load historical audits for temporal analysis."""
        if not self.historical_audits:
            history = await read_from_memory("loop_audits_history")
            if history:
                self.historical_audits = history
    
    async def get_audit_result(self, loop_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audit result for a loop.
        
        Args:
            loop_id: The ID of the loop
            
        Returns:
            Dictionary with audit result if found, None otherwise
        """
        # Check if audit result is in memory
        if loop_id in self.audits:
            return self.audits[loop_id]
        
        # Try to load from storage
        audit_result = await read_from_memory(f"loop_audit[{loop_id}]")
        if audit_result:
            self.audits[loop_id] = audit_result
            return audit_result
        
        logger.warning(f"Audit result not found for loop {loop_id}")
        return None
    
    async def get_audit_issues(self, loop_id: str) -> List[Dict[str, Any]]:
        """
        Get audit issues for a loop.
        
        Args:
            loop_id: The ID of the loop
            
        Returns:
            List of dictionaries with issue information
        """
        audit_result = await self.get_audit_result(loop_id)
        if audit_result:
            return audit_result.get("issues", [])
        
        return []
    
    async def get_audit_warnings(self, loop_id: str) -> List[Dict[str, Any]]:
        """
        Get audit warnings for a loop.
        
        Args:
            loop_id: The ID of the loop
            
        Returns:
            List of dictionaries with warning information
        """
        audit_result = await self.get_audit_result(loop_id)
        if audit_result:
            return audit_result.get("warnings", [])
        
        return []
    
    async def get_audit_recommendations(self, loop_id: str) -> List[Dict[str, Any]]:
        """
        Get audit recommendations for a loop.
        
        Args:
            loop_id: The ID of the loop
            
        Returns:
            List of dictionaries with recommendation information
        """
        audit_result = await self.get_audit_result(loop_id)
        if audit_result:
            return audit_result.get("recommendations", [])
        
        return []
    
    async def get_temporal_patterns(self, loop_id: str) -> List[Dict[str, Any]]:
        """
        Get temporal patterns for a loop.
        
        Args:
            loop_id: The ID of the loop
            
        Returns:
            List of dictionaries with temporal pattern information
        """
        audit_result = await self.get_audit_result(loop_id)
        if audit_result:
            return audit_result.get("temporal_patterns", [])
        
        return []
    
    def _check_belief_consistency(self, loop_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Check belief consistency in loop execution.
        
        Args:
            loop_data: The loop execution data
            
        Returns:
            Tuple of (score, issues)
        """
        issues = []
        
        # Extract beliefs referenced
        beliefs_referenced = loop_data.get("beliefs_referenced", [])
        
        # Check for belief references in agent outputs
        agents = loop_data.get("agents", [])
        
        for agent in agents:
            agent_id = agent.get("id", "unknown")
            agent_output = agent.get("output", {}).get("text", "")
            
            # Check if agent output references beliefs not in beliefs_referenced
            for belief in beliefs_referenced:
                # Simple check: belief should be mentioned in output if referenced
                if belief in beliefs_referenced and belief.lower() not in agent_output.lower():
                    issues.append({
                        "type": "belief_inconsistency",
                        "severity": "warning",
                        "description": f"Belief '{belief}' referenced but not used in output",
                        "location": f"{agent_id}.output"
                    })
            
            # Enhanced: Check for belief interpretation consistency across agents
            for belief in beliefs_referenced:
                belief_interpretations = {}
                for a in agents:
                    a_id = a.get("id", "unknown")
                    a_output = a.get("output", {}).get("text", "")
                    
                    # Extract sentences containing the belief
                    if isinstance(belief, str) and belief.lower() in a_output.lower():
                        sentences = re.split(r'[.!?]+', a_output)
                        for sentence in sentences:
                            if belief.lower() in sentence.lower():
                                if a_id not in belief_interpretations:
                                    belief_interpretations[a_id] = []
                                belief_interpretations[a_id].append(sentence.strip())
                
                # Check for inconsistencies in interpretation
                if len(belief_interpretations) >= 2:
                    # Simple heuristic: if the sentences mentioning the belief are very different in length,
                    # they might represent different interpretations
                    lengths = [len(interp[0]) for interp in belief_interpretations.values() if interp]
                    if lengths and max(lengths) > 2 * min(lengths):
                        issues.append({
                            "type": "belief_interpretation_inconsistency",
                            "severity": "warning",
                            "description": f"Belief '{belief}' may be interpreted inconsistently across agents",
                            "location": f"multiple_agents",
                            "agents_involved": list(belief_interpretations.keys())
                        })
        
        # Calculate score based on issues
        base_score = 1.0
        penalty_per_issue = 0.1
        score = max(0.0, base_score - len(issues) * penalty_per_issue)
        
        return score, issues
    
    def _check_memory_integrity(self, loop_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Check memory integrity in loop execution.
        
        Args:
            loop_data: The loop execution data
            
        Returns:
            Tuple of (score, issues)
        """
        issues = []
        
        # Extract memory operations
        memory_operations = loop_data.get("memory_operations", [])
        
        # Check for read-after-write consistency
        memory_state = {}  # key -> last operation
        memory_access_patterns = defaultdict(list)  # key -> list of operations
        
        for op in memory_operations:
            op_type = op.get("operation_type", "")
            key = op.get("key", "")
            agent_id = op.get("agent_id", "unknown")
            success = op.get("success", True)
            timestamp = op.get("timestamp", "")
            
            if not key:
                continue
            
            # Track access patterns for each key
            memory_access_patterns[key].append({
                "operation_type": op_type,
                "agent_id": agent_id,
                "timestamp": timestamp,
                "success": success
            })
            
            if not success:
                issues.append({
                    "type": "memory_operation_failure",
                    "severity": "error",
                    "description": f"Memory operation {op_type} failed",
                    "location": f"{agent_id}.memory_operation"
                })
                continue
            
            if op_type == "read":
                if key not in memory_state:
                    issues.append({
                        "type": "read_before_write",
                        "severity": "warning",
                        "description": f"Reading key '{key}' before it was written",
                        "location": f"{agent_id}.memory_operation"
                    })
            
            memory_state[key] = op_type
        
        # Check for unused writes
        for key, last_op in memory_state.items():
            if last_op == "write":
                # Check if the write was ever read
                was_read = any(op.get("operation_type") == "read" and op.get("key") == key 
                              for op in memory_operations)
                
                if not was_read:
                    issues.append({
                        "type": "unused_write",
                        "severity": "info",
                        "description": f"Key '{key}' was written but never read",
                        "location": "memory_operations"
                    })
        
        # Enhanced: Check for inefficient memory access patterns
        for key, operations in memory_access_patterns.items():
            # Check for repeated reads without writes in between
            consecutive_reads = 0
            max_consecutive_reads = 0
            last_agent = None
            
            for op in operations:
                if op["operation_type"] == "read":
                    if last_agent != op["agent_id"]:
                        consecutive_reads += 1
                        last_agent = op["agent_id"]
                    else:
                        consecutive_reads = 1
                    max_consecutive_reads = max(max_consecutive_reads, consecutive_reads)
                else:
                    consecutive_reads = 0
            
            if max_consecutive_reads > 3:
                issues.append({
                    "type": "inefficient_memory_access",
                    "severity": "info",
                    "description": f"Key '{key}' was read {max_consecutive_reads} times consecutively by different agents without writes in between",
                    "location": "memory_operations",
                    "optimization_potential": "Consider caching or sharing read results between agents"
                })
            
            # Check for write-write patterns (overwriting without reading)
            write_indices = [i for i, op in enumerate(operations) if op["operation_type"] == "write"]
            for i in range(len(write_indices) - 1):
                current_write = write_indices[i]
                next_write = write_indices[i + 1]
                
                # Check if there's a read between these writes
                has_read_between = any(operations[j]["operation_type"] == "read" 
                                      for j in range(current_write + 1, next_write))
                
                if not has_read_between:
                    issues.append({
                        "type": "overwritten_data",
                        "severity": "warning",
                        "description": f"Key '{key}' was overwritten without being read first",
                        "location": "memory_operations",
                        "agents_involved": [operations[current_write]["agent_id"], operations[next_write]["agent_id"]]
                    })
        
        # Calculate score based on issues
        base_score = 1.0
        error_penalty = 0.2
        warning_penalty = 0.1
        info_penalty = 0.05
        
        error_count = sum(1 for issue in issues if issue.get("severity") == "error")
        warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
        info_count = sum(1 for issue in issues if issue.get("severity") == "info")
        
        score = max(0.0, base_score - 
                   error_count * error_penalty - 
                   warning_count * warning_penalty - 
                   info_count * info_penalty)
        
        return score, issues
    
    def _check_execution_anomalies(self, loop_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Check for execution anomalies in loop execution with enhanced anomaly detection.
        
        Args:
            loop_data: The loop execution data
            
        Returns:
            Tuple of (score, issues)
        """
        issues = []
        
        # Extract execution times
        agents = loop_data.get("agents", [])
        
        # Check for agents with unusually long execution times
        execution_times = []
        for agent in agents:
            agent_id = agent.get("id", "unknown")
            start_time = agent.get("start_time")
            end_time = agent.get("end_time")
            
            if start_time and end_time:
                try:
                    start = datetime.fromisoformat(start_time)
                    end = datetime.fromisoformat(end_time)
                    duration = (end - start).total_seconds() * 1000  # ms
                    execution_times.append((agent_id, duration))
                except (ValueError, TypeError):
                    issues.append({
                        "type": "invalid_timestamp",
                        "severity": "warning",
                        "description": f"Invalid timestamp format for agent {agent_id}",
                        "location": f"{agent_id}.start_time or {agent_id}.end_time"
                    })
        
        if execution_times:
            # Enhanced: Use Z-score for anomaly detection instead of simple threshold
            times = [time for _, time in execution_times]
            
            if len(times) > 1:
                try:
                    mean_time = statistics.mean(times)
                    stdev_time = statistics.stdev(times)
                    
                    for agent_id, time in execution_times:
                        if stdev_time > 0:  # Avoid division by zero
                            z_score = (time - mean_time) / stdev_time
                            
                            if z_score > 2.0:  # More than 2 standard deviations
                                severity = "warning" if z_score < 3.0 else "error"
                                issues.append({
                                    "type": "execution_anomaly",
                                    "severity": severity,
                                    "description": f"Agent {agent_id} execution time ({time:.0f}ms) is significantly higher than average (Z-score: {z_score:.2f})",
                                    "location": f"{agent_id}",
                                    "z_score": round(z_score, 2),
                                    "mean_time": round(mean_time, 2),
                                    "stdev_time": round(stdev_time, 2)
                                })
                except statistics.StatisticsError:
                    # Fall back to simpler method if statistics calculation fails
                    avg_time = sum(times) / len(times)
                    for agent_id, time in execution_times:
                        if time > 2 * avg_time:
                            issues.append({
                                "type": "execution_anomaly",
                                "severity": "warning",
                                "description": f"Agent {agent_id} execution time ({time:.0f}ms) is significantly higher than average ({avg_time:.0f}ms)",
                                "location": f"{agent_id}"
                            })
            else:
                # Only one execution time, can't do statistical analysis
                pass
            
            # Enhanced: Check for execution sequence anomalies
            agent_sequence = []
            for agent in agents:
                if agent.get("start_time") and agent.get("end_time"):
                    try:
                        start = datetime.fromisoformat(agent.get("start_time"))
                        end = datetime.fromisoformat(agent.get("end_time"))
                        agent_sequence.append({
                            "id": agent.get("id", "unknown"),
                            "start": start,
                            "end": end
                        })
                    except (ValueError, TypeError):
                        pass
            
            # Sort by start time
            agent_sequence.sort(key=lambda x: x["start"])
            
            # Check for overlapping executions that shouldn't overlap
            for i in range(len(agent_sequence) - 1):
                current = agent_sequence[i]
                next_agent = agent_sequence[i + 1]
                
                # If current agent ends after next agent starts, they overlap
                if current["end"] > next_agent["start"]:
                    overlap_duration = (current["end"] - next_agent["start"]).total_seconds() * 1000
                    
                    # Only flag if overlap is significant (more than 100ms)
                    if overlap_duration > 100:
                        issues.append({
                            "type": "execution_overlap",
                            "severity": "info",
                            "description": f"Agents {current['id']} and {next_agent['id']} have overlapping execution times ({overlap_duration:.0f}ms)",
                            "location": f"{current['id']},{next_agent['id']}",
                            "overlap_duration_ms": round(overlap_duration, 2)
                        })
        
        # Calculate score based on issues
        base_score = 1.0
        error_penalty = 0.2
        warning_penalty = 0.1
        info_penalty = 0.05
        
        error_count = sum(1 for issue in issues if issue.get("severity") == "error")
        warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
        info_count = sum(1 for issue in issues if issue.get("severity") == "info")
        
        score = max(0.0, base_score - 
                   error_count * error_penalty - 
                   warning_count * warning_penalty - 
                   info_count * info_penalty)
        
        return score, issues
    
    def _check_security_concerns(self, loop_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Check for security concerns in loop execution.
        
        Args:
            loop_data: The loop execution data
            
        Returns:
            Tuple of (score, issues)
        """
        issues = []
        
        # Extract agent outputs
        agents = loop_data.get("agents", [])
        
        # Enhanced: More comprehensive security patterns
        security_patterns = [
            (r"password", "Potential password exposure"),
            (r"token", "Potential token exposure"),
            (r"api[_\s]?key", "Potential API key exposure"),
            (r"secret", "Potential secret exposure"),
            (r"credential", "Potential credential exposure"),
            (r"auth[_\s]?token", "Potential authentication token exposure"),
            (r"private[_\s]?key", "Potential private key exposure"),
            (r"access[_\s]?key", "Potential access key exposure"),
            (r"jwt", "Potential JWT token exposure"),
            (r"oauth", "Potential OAuth token exposure")
        ]
        
        # Enhanced: Check for patterns that look like actual secrets (e.g., hex strings, base64)
        secret_format_patterns = [
            (r"[a-f0-9]{32,}", "Potential MD5 hash or hex-encoded secret"),
            (r"[A-Za-z0-9+/]{40,}={0,2}", "Potential Base64-encoded secret"),
            (r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "Potential JWT token")
        ]
        
        for agent in agents:
            agent_id = agent.get("id", "unknown")
            agent_output = agent.get("output", {}).get("text", "")
            
            # Check for security keyword patterns
            for pattern, description in security_patterns:
                if re.search(pattern, agent_output, re.IGNORECASE):
                    # Look for actual secrets near the pattern
                    matches = re.finditer(pattern, agent_output, re.IGNORECASE)
                    for match in matches:
                        # Get context around the match
                        start = max(0, match.start() - 20)
                        end = min(len(agent_output), match.end() + 20)
                        context = agent_output[start:end]
                        
                        # Check if there's something that looks like a value assignment
                        if re.search(r"[=:]\s*['\"]?[\w+/=]+['\"]?", context):
                            issues.append({
                                "type": "security_concern",
                                "severity": "error",
                                "description": description,
                                "location": f"{agent_id}.output",
                                "context": context
                            })
                            break
                        else:
                            # Just mentioning the term without apparent value
                            issues.append({
                                "type": "security_keyword",
                                "severity": "warning",
                                "description": f"Mention of security-sensitive term: {description}",
                                "location": f"{agent_id}.output"
                            })
                            break
            
            # Check for secret format patterns
            for pattern, description in secret_format_patterns:
                matches = re.finditer(pattern, agent_output)
                for match in matches:
                    # Get context around the match
                    start = max(0, match.start() - 10)
                    end = min(len(agent_output), match.end() + 10)
                    context = agent_output[start:end]
                    
                    issues.append({
                        "type": "security_concern",
                        "severity": "error",
                        "description": description,
                        "location": f"{agent_id}.output",
                        "context": context
                    })
        
        # Calculate score based on issues
        base_score = 1.0
        error_penalty = 0.25  # Higher penalty for security issues
        warning_penalty = 0.15
        
        error_count = sum(1 for issue in issues if issue.get("severity") == "error")
        warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
        
        score = max(0.0, base_score - 
                   error_count * error_penalty - 
                   warning_count * warning_penalty)
        
        return score, issues
    
    def _check_resource_utilization(self, loop_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Check resource utilization in loop execution.
        
        Args:
            loop_data: The loop execution data
            
        Returns:
            Tuple of (score, issues)
        """
        issues = []
        
        # Extract memory usage data
        memory_usage = loop_data.get("memory_usage_kb", {})
        if not isinstance(memory_usage, dict):
            memory_usage = {}
        
        # Extract CPU usage data (if available)
        cpu_usage = loop_data.get("cpu_usage_percent", {})
        if not isinstance(cpu_usage, dict):
            cpu_usage = {}
        
        # Check for high memory usage
        if memory_usage:
            total_memory = sum(memory_usage.values())
            avg_memory = total_memory / len(memory_usage) if memory_usage else 0
            
            for agent_id, usage in memory_usage.items():
                if usage > 2 * avg_memory and usage > 1024:  # More than 2x average and more than 1MB
                    issues.append({
                        "type": "high_memory_usage",
                        "severity": "warning",
                        "description": f"Agent {agent_id} used {usage} KB of memory (average: {avg_memory:.0f} KB)",
                        "location": f"{agent_id}",
                        "usage": usage,
                        "average": round(avg_memory, 2)
                    })
            
            # Check for total memory usage
            if total_memory > 10240:  # More than 10MB
                issues.append({
                    "type": "high_total_memory",
                    "severity": "warning",
                    "description": f"Total memory usage is high: {total_memory} KB",
                    "location": "all_agents",
                    "usage": total_memory
                })
        
        # Check for high CPU usage
        if cpu_usage:
            avg_cpu = sum(cpu_usage.values()) / len(cpu_usage) if cpu_usage else 0
            
            for agent_id, usage in cpu_usage.items():
                if usage > 80:  # More than 80% CPU
                    issues.append({
                        "type": "high_cpu_usage",
                        "severity": "warning",
                        "description": f"Agent {agent_id} used {usage}% CPU",
                        "location": f"{agent_id}",
                        "usage": usage
                    })
        
        # Check for resource efficiency
        agents = loop_data.get("agents", [])
        execution_times = {}
        
        for agent in agents:
            agent_id = agent.get("id", "unknown")
            start_time = agent.get("start_time")
            end_time = agent.get("end_time")
            
            if start_time and end_time:
                try:
                    start = datetime.fromisoformat(start_time)
                    end = datetime.fromisoformat(end_time)
                    duration = (end - start).total_seconds() * 1000  # ms
                    execution_times[agent_id] = duration
                except (ValueError, TypeError):
                    pass
        
        # Calculate resource efficiency (time vs memory)
        for agent_id, exec_time in execution_times.items():
            mem_usage = memory_usage.get(agent_id, 0)
            
            if mem_usage > 0 and exec_time > 0:
                efficiency = mem_usage / exec_time  # KB per ms
                
                if efficiency > 5:  # More than 5KB per ms is inefficient
                    issues.append({
                        "type": "resource_inefficiency",
                        "severity": "info",
                        "description": f"Agent {agent_id} has low resource efficiency ({efficiency:.2f} KB/ms)",
                        "location": f"{agent_id}",
                        "efficiency": round(efficiency, 2),
                        "memory_usage_kb": mem_usage,
                        "execution_time_ms": round(exec_time, 2)
                    })
        
        # Calculate score based on issues
        base_score = 1.0
        warning_penalty = 0.15
        info_penalty = 0.05
        
        warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
        info_count = sum(1 for issue in issues if issue.get("severity") == "info")
        
        score = max(0.0, base_score - 
                   warning_count * warning_penalty - 
                   info_count * info_penalty)
        
        return score, issues
    
    def _perform_correlation_analysis(self, issues: List[Dict[str, Any]], loop_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform correlation analysis on issues to identify related problems.
        
        Args:
            issues: List of identified issues
            loop_data: The loop execution data
            
        Returns:
            List of correlated issues
        """
        correlated_issues = []
        
        # Group issues by location
        location_issues = defaultdict(list)
        for issue in issues:
            location = issue.get("location", "unknown")
            location_issues[location].append(issue)
        
        # Check for multiple issues in the same location
        for location, loc_issues in location_issues.items():
            if len(loc_issues) > 2:
                # Multiple issues in same location might indicate a systemic problem
                issue_types = [issue.get("type", "unknown") for issue in loc_issues]
                
                correlated_issues.append({
                    "type": "correlated_issues",
                    "severity": "warning",
                    "description": f"Multiple issues ({len(loc_issues)}) detected in {location}",
                    "location": location,
                    "issue_count": len(loc_issues),
                    "issue_types": issue_types,
                    "correlation_type": "location"
                })
        
        # Check for correlations between execution time and memory usage
        execution_anomalies = [issue for issue in issues if issue.get("type") == "execution_anomaly"]
        memory_issues = [issue for issue in issues if issue.get("type") in ["high_memory_usage", "resource_inefficiency"]]
        
        # If both execution and memory issues exist, check for correlation
        if execution_anomalies and memory_issues:
            # Extract agent IDs with both types of issues
            exec_agents = set(issue.get("location", "").split(".")[0] for issue in execution_anomalies)
            mem_agents = set(issue.get("location", "").split(".")[0] for issue in memory_issues)
            
            common_agents = exec_agents.intersection(mem_agents)
            
            if common_agents:
                for agent in common_agents:
                    correlated_issues.append({
                        "type": "performance_correlation",
                        "severity": "warning",
                        "description": f"Agent {agent} has both execution time and memory usage issues",
                        "location": agent,
                        "correlation_type": "performance",
                        "correlated_metrics": ["execution_time", "memory_usage"]
                    })
        
        # Check for correlations between belief inconsistency and execution anomalies
        belief_issues = [issue for issue in issues if issue.get("type") in ["belief_inconsistency", "belief_interpretation_inconsistency"]]
        
        if belief_issues and execution_anomalies:
            # This could indicate that belief processing is causing performance issues
            correlated_issues.append({
                "type": "belief_performance_correlation",
                "severity": "info",
                "description": "Belief inconsistencies may be related to execution performance issues",
                "location": "multiple",
                "correlation_type": "belief_performance",
                "belief_issue_count": len(belief_issues),
                "execution_issue_count": len(execution_anomalies)
            })
        
        return correlated_issues
    
    def _calculate_correlation_strength(self, issues: List[Dict[str, Any]]) -> float:
        """
        Calculate the overall correlation strength among issues.
        
        Args:
            issues: List of identified issues
            
        Returns:
            Correlation strength score between 0 and 1
        """
        if not issues:
            return 0.0
        
        # Count issues by type
        issue_types = defaultdict(int)
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            issue_types[issue_type] += 1
        
        # Count issues by location
        issue_locations = defaultdict(int)
        for issue in issues:
            location = issue.get("location", "unknown")
            issue_locations[location] += 1
        
        # Calculate type concentration (higher means issues are concentrated in fewer types)
        type_concentration = sum(count * count for count in issue_types.values()) / (len(issues) * len(issues))
        
        # Calculate location concentration (higher means issues are concentrated in fewer locations)
        location_concentration = sum(count * count for count in issue_locations.values()) / (len(issues) * len(issues))
        
        # Combine the two measures
        correlation_strength = (type_concentration + location_concentration) / 2
        
        return min(1.0, correlation_strength)
    
    def _analyze_temporal_patterns(self, loop_id: str, loop_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze temporal patterns across multiple loop executions.
        
        Args:
            loop_id: The ID of the current loop
            loop_data: The loop execution data
            
        Returns:
            List of temporal patterns
        """
        patterns = []
        
        # Need at least 2 historical audits for temporal analysis
        if len(self.historical_audits) < 2:
            return patterns
        
        # Sort historical audits by timestamp
        sorted_audits = sorted(self.historical_audits, 
                              key=lambda x: datetime.fromisoformat(x["timestamp"]))
        
        # Analyze score trends
        score_metrics = ["overall_score", "belief_consistency_score", 
                        "memory_integrity_score", "execution_score", "security_score"]
        
        for metric in score_metrics:
            scores = [audit.get(metric, 0) for audit in sorted_audits]
            
            if len(scores) >= 3:  # Need at least 3 points for trend analysis
                # Simple trend detection: consistently increasing or decreasing
                is_increasing = all(scores[i] <= scores[i+1] for i in range(len(scores)-1))
                is_decreasing = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
                
                if is_decreasing and scores[0] - scores[-1] > 0.1:  # Significant decrease
                    patterns.append({
                        "type": "score_trend",
                        "trend": "decreasing",
                        "metric": metric,
                        "description": f"{metric.replace('_', ' ').title()} has been consistently decreasing",
                        "start_value": scores[0],
                        "current_value": scores[-1],
                        "change": round(scores[-1] - scores[0], 2)
                    })
                elif is_increasing and scores[-1] - scores[0] > 0.1:  # Significant increase
                    patterns.append({
                        "type": "score_trend",
                        "trend": "increasing",
                        "metric": metric,
                        "description": f"{metric.replace('_', ' ').title()} has been consistently improving",
                        "start_value": scores[0],
                        "current_value": scores[-1],
                        "change": round(scores[-1] - scores[0], 2)
                    })
        
        # Analyze issue count trends
        issue_counts = [audit.get("issue_count", 0) for audit in sorted_audits]
        
        if len(issue_counts) >= 3:
            is_increasing = all(issue_counts[i] <= issue_counts[i+1] for i in range(len(issue_counts)-1))
            is_decreasing = all(issue_counts[i] >= issue_counts[i+1] for i in range(len(issue_counts)-1))
            
            if is_increasing and issue_counts[-1] - issue_counts[0] >= 2:
                patterns.append({
                    "type": "issue_trend",
                    "trend": "increasing",
                    "description": "Number of issues has been consistently increasing",
                    "start_value": issue_counts[0],
                    "current_value": issue_counts[-1],
                    "change": issue_counts[-1] - issue_counts[0],
                    "affected_components": "multiple"
                })
            elif is_decreasing and issue_counts[0] - issue_counts[-1] >= 2:
                patterns.append({
                    "type": "issue_trend",
                    "trend": "decreasing",
                    "description": "Number of issues has been consistently decreasing",
                    "start_value": issue_counts[0],
                    "current_value": issue_counts[-1],
                    "change": issue_counts[0] - issue_counts[-1],
                    "affected_components": "multiple"
                })
        
        # Analyze performance trends if we have execution times
        if "execution_time_ms" in loop_data:
            # Current execution times
            current_times = loop_data.get("execution_time_ms", {})
            
            # Check if we have historical execution times
            has_historical_times = any("execution_time_ms" in audit for audit in sorted_audits)
            
            if has_historical_times and current_times:
                for agent_id, current_time in current_times.items():
                    # Get historical times for this agent
                    historical_times = []
                    for audit in sorted_audits:
                        if "execution_time_ms" in audit and agent_id in audit["execution_time_ms"]:
                            historical_times.append(audit["execution_time_ms"][agent_id])
                    
                    if len(historical_times) >= 2:
                        # Calculate average historical time
                        avg_historical = sum(historical_times) / len(historical_times)
                        
                        # Check if current time is significantly different
                        if current_time > avg_historical * 1.5:
                            patterns.append({
                                "type": "performance_trend",
                                "trend": "degrading",
                                "description": f"Agent {agent_id} execution time has increased significantly",
                                "historical_avg": round(avg_historical, 2),
                                "current_value": round(current_time, 2),
                                "change_percent": round((current_time - avg_historical) / avg_historical * 100, 2),
                                "affected_components": agent_id,
                                "potential_improvement": f"Investigate {agent_id} for performance regression"
                            })
                        elif current_time < avg_historical * 0.7:
                            patterns.append({
                                "type": "performance_trend",
                                "trend": "improving",
                                "description": f"Agent {agent_id} execution time has decreased significantly",
                                "historical_avg": round(avg_historical, 2),
                                "current_value": round(current_time, 2),
                                "change_percent": round((avg_historical - current_time) / avg_historical * 100, 2),
                                "affected_components": agent_id,
                                "potential_improvement": "Continue with recent optimizations"
                            })
        
        return patterns
    
    def _calculate_risk_scores(self, issues: List[Dict[str, Any]], loop_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate risk scores for issues based on impact and likelihood.
        
        Args:
            issues: List of identified issues
            loop_data: The loop execution data
            
        Returns:
            List of issues with risk scores
        """
        risk_scored_issues = []
        
        # Severity to impact mapping
        severity_impact = {
            "error": 0.9,
            "warning": 0.6,
            "info": 0.3
        }
        
        # Issue type to likelihood mapping
        type_likelihood = {
            "security_concern": 0.9,
            "memory_operation_failure": 0.8,
            "execution_anomaly": 0.7,
            "belief_inconsistency": 0.6,
            "read_before_write": 0.5,
            "unused_write": 0.4,
            "high_memory_usage": 0.6,
            "high_cpu_usage": 0.6,
            "resource_inefficiency": 0.5,
            "correlated_issues": 0.7,
            "performance_correlation": 0.6
        }
        
        # Default likelihood for unknown types
        default_likelihood = 0.5
        
        for issue in issues:
            # Copy the issue
            risk_issue = issue.copy()
            
            # Get impact from severity
            severity = issue.get("severity", "info")
            impact = severity_impact.get(severity, 0.3)
            
            # Get likelihood from issue type
            issue_type = issue.get("type", "unknown")
            likelihood = type_likelihood.get(issue_type, default_likelihood)
            
            # Adjust likelihood based on context
            if "context" in issue:
                # Security issues with actual values are more likely to be exploited
                if issue_type == "security_concern" and re.search(r"[=:]\s*['\"]?[\w+/=]+['\"]?", issue["context"]):
                    likelihood = min(1.0, likelihood + 0.1)
            
            # Calculate risk score (impact * likelihood)
            risk_score = impact * likelihood
            
            # Add risk information to the issue
            risk_issue["risk"] = {
                "impact": round(impact, 2),
                "likelihood": round(likelihood, 2),
                "risk_score": round(risk_score, 2),
                "risk_level": self._get_risk_level(risk_score)
            }
            
            risk_scored_issues.append(risk_issue)
        
        # Sort issues by risk score (highest first)
        risk_scored_issues.sort(key=lambda x: x["risk"]["risk_score"], reverse=True)
        
        return risk_scored_issues
    
    def _get_risk_level(self, risk_score: float) -> str:
        """
        Get risk level from risk score.
        
        Args:
            risk_score: Risk score between 0 and 1
            
        Returns:
            Risk level string
        """
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _generate_warnings(self, loop_data: Dict[str, Any], 
                         issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate warnings based on issues and loop data.
        
        Args:
            loop_data: The loop execution data
            issues: List of identified issues
            
        Returns:
            List of warnings
        """
        warnings = []
        
        # Group issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        # Generate warnings for issue groups
        for issue_type, type_issues in issue_types.items():
            if len(type_issues) > 1:
                warnings.append({
                    "type": issue_type,
                    "description": f"Multiple {issue_type} issues detected",
                    "count": len(type_issues)
                })
        
        # Check for other warning conditions
        
        # Check for high agent count
        agents = loop_data.get("agents", [])
        if len(agents) > 5:
            warnings.append({
                "type": "high_agent_count",
                "description": f"Loop uses a high number of agents ({len(agents)})",
                "count": len(agents)
            })
        
        # Check for high memory operation count
        memory_operations = loop_data.get("memory_operations", [])
        if len(memory_operations) > 20:
            warnings.append({
                "type": "high_memory_operations",
                "description": f"Loop uses a high number of memory operations ({len(memory_operations)})",
                "count": len(memory_operations)
            })
        
        # Enhanced: Check for high-risk issues
        high_risk_issues = [issue for issue in issues 
                           if "risk" in issue and issue["risk"]["risk_level"] == "high"]
        
        if high_risk_issues:
            warnings.append({
                "type": "high_risk_issues",
                "description": f"Loop has {len(high_risk_issues)} high-risk issues that require immediate attention",
                "count": len(high_risk_issues),
                "issue_types": list(set(issue.get("type", "unknown") for issue in high_risk_issues))
            })
        
        # Enhanced: Check for resource utilization warnings
        resource_issues = [issue for issue in issues 
                          if issue.get("type") in ["high_memory_usage", "high_cpu_usage", "resource_inefficiency"]]
        
        if len(resource_issues) >= 2:
            warnings.append({
                "type": "resource_utilization",
                "description": f"Loop has {len(resource_issues)} resource utilization issues",
                "count": len(resource_issues),
                "affected_resources": list(set(issue.get("type", "").replace("high_", "").replace("_usage", "") 
                                             for issue in resource_issues))
            })
        
        return warnings
    
    def _generate_recommendations(self, loop_data: Dict[str, Any],
                                issues: List[Dict[str, Any]],
                                warnings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on issues, warnings, and loop data.
        
        Args:
            loop_data: The loop execution data
            issues: List of identified issues
            warnings: List of generated warnings
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Generate recommendations based on issues
        security_issues = [i for i in issues if i.get("type") == "security_concern"]
        if security_issues:
            recommendations.append({
                "type": "security",
                "description": "Review agent outputs for potential security concerns",
                "potential_improvement": "Reduced security risk",
                "priority": "high",
                "issue_count": len(security_issues)
            })
        
        memory_issues = [i for i in issues if i.get("type") in ["read_before_write", "unused_write", "inefficient_memory_access"]]
        if memory_issues:
            recommendations.append({
                "type": "memory_usage",
                "description": "Optimize memory access patterns",
                "potential_improvement": "Improved memory efficiency",
                "priority": "medium",
                "issue_count": len(memory_issues),
                "specific_actions": [
                    "Ensure keys are written before being read",
                    "Avoid unused writes",
                    "Consider caching frequently accessed data"
                ]
            })
        
        execution_issues = [i for i in issues if i.get("type") == "execution_anomaly"]
        if execution_issues:
            # Extract agent IDs with execution issues
            agent_ids = list(set(i.get("location", "").split(".")[0] for i in execution_issues))
            
            recommendations.append({
                "type": "performance",
                "description": "Investigate slow agent executions",
                "potential_improvement": "Reduced execution time",
                "priority": "medium",
                "issue_count": len(execution_issues),
                "affected_agents": agent_ids,
                "specific_actions": [
                    f"Profile agent {agent_id} execution" for agent_id in agent_ids
                ]
            })
        
        # Enhanced: Recommendations for resource utilization issues
        resource_issues = [i for i in issues if i.get("type") in ["high_memory_usage", "high_cpu_usage", "resource_inefficiency"]]
        if resource_issues:
            # Group by resource type
            memory_issues = [i for i in resource_issues if "memory" in i.get("type", "")]
            cpu_issues = [i for i in resource_issues if "cpu" in i.get("type", "")]
            
            if memory_issues:
                recommendations.append({
                    "type": "memory_optimization",
                    "description": "Optimize memory usage in identified agents",
                    "potential_improvement": "Reduced memory footprint",
                    "priority": "medium",
                    "issue_count": len(memory_issues),
                    "affected_agents": list(set(i.get("location", "unknown") for i in memory_issues)),
                    "specific_actions": [
                        "Implement memory-efficient data structures",
                        "Release unused resources promptly",
                        "Consider streaming for large data processing"
                    ]
                })
            
            if cpu_issues:
                recommendations.append({
                    "type": "cpu_optimization",
                    "description": "Optimize CPU usage in identified agents",
                    "potential_improvement": "Reduced CPU utilization",
                    "priority": "medium",
                    "issue_count": len(cpu_issues),
                    "affected_agents": list(set(i.get("location", "unknown") for i in cpu_issues)),
                    "specific_actions": [
                        "Optimize algorithms for efficiency",
                        "Consider parallel processing where appropriate",
                        "Reduce unnecessary computation"
                    ]
                })
        
        # Enhanced: Recommendations for correlated issues
        correlated_issues = [i for i in issues if i.get("type") in ["correlated_issues", "performance_correlation", "belief_performance_correlation"]]
        if correlated_issues:
            recommendations.append({
                "type": "systemic_improvement",
                "description": "Address systemic issues affecting multiple components",
                "potential_improvement": "Improved system stability and performance",
                "priority": "high",
                "issue_count": len(correlated_issues),
                "correlation_types": list(set(i.get("correlation_type", "unknown") for i in correlated_issues)),
                "specific_actions": [
                    "Review system architecture for component interactions",
                    "Implement cross-component monitoring",
                    "Standardize resource management across agents"
                ]
            })
        
        # Generate recommendations based on warnings
        high_agent_warning = next((w for w in warnings if w.get("type") == "high_agent_count"), None)
        if high_agent_warning:
            recommendations.append({
                "type": "architecture",
                "description": "Consider reducing the number of agents",
                "potential_improvement": "Simplified loop execution",
                "priority": "low",
                "specific_actions": [
                    "Consolidate agents with similar responsibilities",
                    "Review agent division of labor",
                    "Consider hierarchical agent organization"
                ]
            })
        
        high_memory_ops_warning = next((w for w in warnings if w.get("type") == "high_memory_operations"), None)
        if high_memory_ops_warning:
            recommendations.append({
                "type": "memory_access",
                "description": "Reduce number of memory operations",
                "potential_improvement": "Improved performance and reliability",
                "priority": "medium",
                "specific_actions": [
                    "Batch related memory operations",
                    "Cache frequently accessed data",
                    "Review data sharing between agents"
                ]
            })
        
        # Generate general recommendations
        if not issues and not warnings:
            recommendations.append({
                "type": "general",
                "description": "No significant issues found",
                "potential_improvement": "Continue monitoring for changes",
                "priority": "low"
            })
        
        # Sort recommendations by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
        
        return recommendations

# Global auditor agent instance
_auditor_agent = None

def get_auditor_agent() -> AuditorAgent:
    """
    Get the global auditor agent instance.
    
    Returns:
        AuditorAgent instance
    """
    global _auditor_agent
    if _auditor_agent is None:
        _auditor_agent = AuditorAgent()
    
    return _auditor_agent

async def audit_loop(loop_id: str, loop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audit a loop execution.
    
    Args:
        loop_id: The ID of the loop to audit
        loop_data: The loop execution data
        
    Returns:
        Dictionary with audit results
    """
    auditor = get_auditor_agent()
    return await auditor.audit_loop(loop_id, loop_data)

async def get_audit_result(loop_id: str) -> Optional[Dict[str, Any]]:
    """
    Get audit result for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dictionary with audit result if found, None otherwise
    """
    auditor = get_auditor_agent()
    return await auditor.get_audit_result(loop_id)

async def get_audit_issues(loop_id: str) -> List[Dict[str, Any]]:
    """
    Get audit issues for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        List of dictionaries with issue information
    """
    auditor = get_auditor_agent()
    return await auditor.get_audit_issues(loop_id)

async def get_audit_warnings(loop_id: str) -> List[Dict[str, Any]]:
    """
    Get audit warnings for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        List of dictionaries with warning information
    """
    auditor = get_auditor_agent()
    return await auditor.get_audit_warnings(loop_id)

async def get_audit_recommendations(loop_id: str) -> List[Dict[str, Any]]:
    """
    Get audit recommendations for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        List of dictionaries with recommendation information
    """
    auditor = get_auditor_agent()
    return await auditor.get_audit_recommendations(loop_id)

async def get_temporal_patterns(loop_id: str) -> List[Dict[str, Any]]:
    """
    Get temporal patterns for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        List of dictionaries with temporal pattern information
    """
    auditor = get_auditor_agent()
    return await auditor.get_temporal_patterns(loop_id)
