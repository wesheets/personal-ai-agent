"""
Belief Drift Monitor (v2) Implementation

This module implements the Belief Drift Monitor functionality for comparing recent loop
SAGE summaries, CRITIC logs, and project goal beliefs to detect belief alignment drift.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

# Configure logging
logger = logging.getLogger("drift_monitor")

async def detect_loop_drift(loop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect drift in loop execution data.
    
    Args:
        loop_data: Dictionary containing loop execution data
            
    Returns:
        Dictionary containing drift detection result
    """
    try:
        logger.info("Detecting loop drift")
        
        # Create monitor instance
        monitor = BeliefDriftMonitor()
        
        # Extract data from loop_data
        project_id = loop_data.get("project_id", "unknown")
        sage_summaries = loop_data.get("sage_summaries", [])
        critic_logs = loop_data.get("critic_logs", [])
        project_goals = loop_data.get("project_goals", {})
        
        # Monitor belief drift
        result = monitor.monitor_belief_drift(
            project_id=project_id,
            sage_summaries=sage_summaries,
            critic_logs=critic_logs,
            project_goals=project_goals
        )
        
        return result
    except Exception as e:
        logger.error(f"Error detecting loop drift: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to detect loop drift: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

async def log_drift(drift_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log drift detection results to the system.
    
    Args:
        drift_data: Dictionary containing drift detection data
            
    Returns:
        Dictionary containing log result
    """
    try:
        logger.info("Logging drift detection results")
        
        # Extract data
        project_id = drift_data.get("project_id", "unknown")
        drift_detected = drift_data.get("drift_detected", False)
        overall_alignment = drift_data.get("overall_alignment", 0.0)
        
        # Generate log tag
        log_tag = f"drift_log_{project_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Create log entry
        log_entry = {
            "project_id": project_id,
            "drift_detected": drift_detected,
            "overall_alignment": overall_alignment,
            "drift_data": drift_data,
            "timestamp": datetime.utcnow().isoformat(),
            "log_tag": log_tag
        }
        
        # In a real implementation, this would write to a persistent store
        logger.info(f"Drift log created for project {project_id}: drift={drift_detected}, alignment={overall_alignment:.2f}")
        
        return {
            "status": "success",
            "message": "Drift log created successfully",
            "log_tag": log_tag,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error logging drift: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to log drift: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

async def get_previous_output(project_id: str, output_type: str = "drift") -> Dict[str, Any]:
    """
    Get previous output for a specific project and type.
    
    Args:
        project_id: The project identifier
        output_type: The type of output to retrieve
            
    Returns:
        Dictionary containing previous output data
    """
    try:
        logger.info(f"Getting previous {output_type} output for project: {project_id}")
        
        # In a real implementation, this would query a database
        # For now, return mock data
        
        if output_type == "drift":
            return {
                "project_id": project_id,
                "drift_detected": False,
                "overall_alignment": 0.85,
                "timestamp": (datetime.utcnow() - datetime.timedelta(days=1)).isoformat(),
                "recommendations": [
                    {
                        "type": "info",
                        "priority": "low",
                        "description": "Previous alignment was within acceptable range."
                    }
                ]
            }
        else:
            return {
                "project_id": project_id,
                "output_type": output_type,
                "content": f"Previous {output_type} output for project {project_id}",
                "timestamp": (datetime.utcnow() - datetime.timedelta(days=1)).isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting previous output: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to get previous output: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

async def determine_recommended_action(drift_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determine recommended action based on drift data.
    
    Args:
        drift_data: Dictionary containing drift detection data
            
    Returns:
        Dictionary containing recommended action
    """
    try:
        logger.info("Determining recommended action based on drift data")
        
        # Extract data
        project_id = drift_data.get("project_id", "unknown")
        drift_detected = drift_data.get("drift_detected", False)
        overall_alignment = drift_data.get("overall_alignment", 0.0)
        
        # Determine action based on alignment score
        if not drift_detected or overall_alignment >= 0.8:
            action = {
                "type": "continue",
                "priority": "low",
                "description": "Continue with current approach. Alignment is good."
            }
        elif overall_alignment >= 0.6:
            action = {
                "type": "review",
                "priority": "medium",
                "description": "Review recent changes and consider minor adjustments to improve alignment."
            }
        elif overall_alignment >= 0.4:
            action = {
                "type": "adjust",
                "priority": "high",
                "description": "Significant drift detected. Adjust approach to better align with project goals."
            }
        else:
            action = {
                "type": "reset",
                "priority": "critical",
                "description": "Critical drift detected. Consider resetting approach or reviewing project goals."
            }
        
        return {
            "status": "success",
            "project_id": project_id,
            "recommended_action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error determining recommended action: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to determine recommended action: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

class BeliefDriftMonitor:
    """
    Belief Drift Monitor for detecting drift in belief alignment.
    
    This monitor compares:
    - Recent loop SAGE summaries
    - CRITIC logs
    - Project goal beliefs
    
    It flags drift when belief alignment drops below 70%.
    """
    
    def __init__(self):
        """Initialize the Belief Drift Monitor with required configuration."""
        self.version = "2.0.0"
        self.alignment_threshold = 0.7  # 70% alignment threshold
        self.max_history_items = 10  # Maximum number of historical items to compare
        
        logger.info("Belief Drift Monitor (v2) initialized (version: %s)", self.version)
    
    def monitor_belief_drift(
        self, 
        project_id: str,
        sage_summaries: List[Dict[str, Any]],
        critic_logs: List[Dict[str, Any]],
        project_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Monitor belief drift by comparing SAGE summaries, CRITIC logs, and project goals.
        
        Args:
            project_id: Project identifier
            sage_summaries: List of recent SAGE summaries
            critic_logs: List of recent CRITIC logs
            project_goals: Project goal beliefs
            
        Returns:
            Dictionary containing the monitoring result
        """
        try:
            # Extract beliefs from each source
            sage_beliefs = self._extract_sage_beliefs(sage_summaries)
            critic_beliefs = self._extract_critic_beliefs(critic_logs)
            goal_beliefs = self._extract_goal_beliefs(project_goals)
            
            # Calculate alignment scores
            sage_goal_alignment = self._calculate_alignment(sage_beliefs, goal_beliefs)
            critic_goal_alignment = self._calculate_alignment(critic_beliefs, goal_beliefs)
            sage_critic_alignment = self._calculate_alignment(sage_beliefs, critic_beliefs)
            
            # Calculate overall alignment
            overall_alignment = (sage_goal_alignment + critic_goal_alignment + sage_critic_alignment) / 3
            
            # Determine if drift is detected
            drift_detected = overall_alignment < self.alignment_threshold
            
            # Generate drift analysis
            drift_analysis = self._generate_drift_analysis(
                overall_alignment,
                sage_goal_alignment,
                critic_goal_alignment,
                sage_critic_alignment,
                drift_detected
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                drift_detected,
                overall_alignment,
                sage_goal_alignment,
                critic_goal_alignment,
                sage_critic_alignment
            )
            
            # Log monitoring result
            result = self._log_monitoring_result(
                project_id,
                overall_alignment,
                drift_detected,
                drift_analysis,
                recommendations
            )
            
            return result
        
        except Exception as e:
            logger.error("Error monitoring belief drift: %s", str(e))
            return {
                "status": "error",
                "message": f"Error monitoring belief drift: {str(e)}",
                "project_id": project_id,
                "timestamp": datetime.utcnow().isoformat(),
                "version": self.version
            }
    
    def _extract_sage_beliefs(self, sage_summaries: List[Dict[str, Any]]) -> List[str]:
        """
        Extract beliefs from SAGE summaries.
        
        Args:
            sage_summaries: List of recent SAGE summaries
            
        Returns:
            List of extracted beliefs
        """
        beliefs = []
        
        for summary in sage_summaries[-self.max_history_items:]:
            # Extract beliefs from summary content
            if "analysis" in summary:
                analysis = summary["analysis"]
                if isinstance(analysis, str):
                    # Extract sentences that likely contain beliefs
                    sentences = re.split(r'[.!?]', analysis)
                    belief_sentences = [
                        s.strip() for s in sentences
                        if any(kw in s.lower() for kw in [
                            "believe", "conclusion", "determine", "assess", "evaluate",
                            "find", "indicate", "suggest", "imply", "infer"
                        ])
                    ]
                    beliefs.extend(belief_sentences)
            
            # Extract beliefs from key findings
            if "key_findings" in summary and isinstance(summary["key_findings"], list):
                beliefs.extend(summary["key_findings"])
        
        return beliefs
    
    def _extract_critic_beliefs(self, critic_logs: List[Dict[str, Any]]) -> List[str]:
        """
        Extract beliefs from CRITIC logs.
        
        Args:
            critic_logs: List of recent CRITIC logs
            
        Returns:
            List of extracted beliefs
        """
        beliefs = []
        
        for log in critic_logs[-self.max_history_items:]:
            # Extract beliefs from review content
            if "review" in log:
                review = log["review"]
                if isinstance(review, str):
                    # Extract sentences that likely contain beliefs
                    sentences = re.split(r'[.!?]', review)
                    belief_sentences = [
                        s.strip() for s in sentences
                        if any(kw in s.lower() for kw in [
                            "believe", "conclusion", "determine", "assess", "evaluate",
                            "find", "indicate", "suggest", "imply", "infer", "critique"
                        ])
                    ]
                    beliefs.extend(belief_sentences)
            
            # Extract beliefs from issues
            if "issues" in log and isinstance(log["issues"], list):
                for issue in log["issues"]:
                    if isinstance(issue, dict) and "description" in issue:
                        beliefs.append(issue["description"])
        
        return beliefs
    
    def _extract_goal_beliefs(self, project_goals: Dict[str, Any]) -> List[str]:
        """
        Extract beliefs from project goals.
        
        Args:
            project_goals: Project goal beliefs
            
        Returns:
            List of extracted beliefs
        """
        beliefs = []
        
        # Extract from objectives
        if "objectives" in project_goals and isinstance(project_goals["objectives"], list):
            beliefs.extend(project_goals["objectives"])
        
        # Extract from success criteria
        if "success_criteria" in project_goals and isinstance(project_goals["success_criteria"], list):
            beliefs.extend(project_goals["success_criteria"])
        
        # Extract from constraints
        if "constraints" in project_goals and isinstance(project_goals["constraints"], list):
            beliefs.extend(project_goals["constraints"])
        
        # Extract from description
        if "description" in project_goals and isinstance(project_goals["description"], str):
            sentences = re.split(r'[.!?]', project_goals["description"])
            beliefs.extend([s.strip() for s in sentences if len(s.strip()) > 10])
        
        return beliefs
    
    def _calculate_alignment(self, beliefs1: List[str], beliefs2: List[str]) -> float:
        """
        Calculate alignment between two sets of beliefs.
        
        Args:
            beliefs1: First set of beliefs
            beliefs2: Second set of beliefs
            
        Returns:
            Alignment score between 0.0 and 1.0
        """
        if not beliefs1 or not beliefs2:
            return 0.0
        
        # Calculate semantic similarity between beliefs
        # In a real implementation, this would use embeddings or NLP techniques
        # For this implementation, we'll use a simple keyword-based approach
        
        # Extract keywords from each belief
        keywords1 = self._extract_keywords(beliefs1)
        keywords2 = self._extract_keywords(beliefs2)
        
        # Calculate Jaccard similarity
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_keywords(self, beliefs: List[str]) -> set:
        """
        Extract keywords from a list of beliefs.
        
        Args:
            beliefs: List of belief statements
            
        Returns:
            Set of keywords
        """
        # Combine all beliefs into a single string
        text = " ".join(beliefs).lower()
        
        # Remove common stop words
        stop_words = {
            "a", "an", "the", "and", "or", "but", "if", "then", "else", "when",
            "at", "from", "by", "for", "with", "about", "against", "between",
            "into", "through", "during", "before", "after", "above", "below",
            "to", "of", "in", "on", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "having", "do", "does", "did", "doing",
            "can", "could", "should", "would", "may", "might", "must", "shall", "will"
        }
        
        # Split into words and filter out stop words
        words = re.findall(r'\b\w+\b', text)
        keywords = {word for word in words if word not in stop_words and len(word) > 2}
        
        return keywords
    
    def _generate_drift_analysis(
        self,
        overall_alignment: float,
        sage_goal_alignment: float,
        critic_goal_alignment: float,
        sage_critic_alignment: float,
        drift_detected: bool
    ) -> Dict[str, Any]:
        """
        Generate analysis of belief drift.
        
        Args:
            overall_alignment: Overall alignment score
            sage_goal_alignment: Alignment between SAGE and goals
            critic_goal_alignment: Alignment between CRITIC and goals
            sage_critic_alignment: Alignment between SAGE and CRITIC
            drift_detected: Whether drift is detected
            
        Returns:
            Dictionary containing drift analysis
        """
        # Determine primary drift source
        alignments = {
            "SAGE-Goal": sage_goal_alignment,
            "CRITIC-Goal": critic_goal_alignment,
            "SAGE-CRITIC": sage_critic_alignment
        }
        
        primary_drift = min(alignments.items(), key=lambda x: x[1])
        
        # Generate analysis
        analysis = {
            "overall_alignment": overall_alignment,
            "alignment_details": {
                "sage_goal_alignment": sage_goal_alignment,
                "critic_goal_alignment": critic_goal_alignment,
                "sage_critic_alignment": sage_critic_alignment
            },
            "drift_detected": drift_detected,
            "primary_drift_source": primary_drift[0],
            "primary_drift_score": primary_drift[1],
            "severity": "high" if overall_alignment < 0.5 else "medium" if overall_alignment < 0.7 else "low"
        }
        
        return analysis
    
    def _generate_recommendations(
        self,
        drift_detected: bool,
        overall_alignment: float,
        sage_goal_alignment: float,
        critic_goal_alignment: float,
        sage_critic_alignment: float
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on drift analysis.
        
        Args:
            drift_detected: Whether drift is detected
            overall_alignment: Overall alignment score
            sage_goal_alignment: Alignment between SAGE and goals
            critic_goal_alignment: Alignment between CRITIC and goals
            sage_critic_alignment: Alignment between SAGE and CRITIC
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not drift_detected:
            recommendations.append({
                "type": "info",
                "priority": "low",
                "description": "Belief alignment is within acceptable range. Continue monitoring."
            })
            return recommendations
        
        # Add recommendations based on alignment scores
        if sage_goal_alignment < self.alignment_threshold:
            recommendations.append({
                "type": "action",
                "priority": "high",
                "description": "SAGE analysis is drifting from project goals. Review SAGE prompts and update with clearer project objectives."
            })
        
        if critic_goal_alignment < self.alignment_threshold:
            recommendations.append({
                "type": "action",
                "priority": "high",
                "description": "CRITIC reviews are drifting from project goals. Update CRITIC evaluation criteria to better align with project objectives."
            })
        
        if sage_critic_alignment < self.alignment_threshold:
            recommendations.append({
                "type": "action",
                "priority": "medium",
                "description": "SAGE and CRITIC are not aligned with each other. Consider synchronizing their understanding of project requirements."
            })
        
        # Add general recommendations for severe drift
        if overall_alignment < 0.5:
            recommendations.append({
                "type": "action",
                "priority": "critical",
                "description": "Severe belief drift detected. Consider pausing the project and conducting a full alignment review."
            })
        
        return recommendations
    
    def _log_monitoring_result(
        self,
        project_id: str,
        overall_alignment: float,
        drift_detected: bool,
        drift_analysis: Dict[str, Any],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Log the monitoring result to the system.
        
        Args:
            project_id: Project identifier
            overall_alignment: Overall alignment score
            drift_detected: Whether drift is detected
            drift_analysis: Analysis of belief drift
            recommendations: List of recommendations
            
        Returns:
            Dictionary containing the monitoring result
        """
        # Generate version number for the log
        version = 1
        # In a real implementation, this would query existing logs to determine the next version
        
        log_tag = f"belief_drift_{project_id}_v{version}"
        
        result = {
            "project_id": project_id,
            "overall_alignment": overall_alignment,
            "drift_detected": drift_detected,
            "drift_analysis": drift_analysis,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat(),
            "version": self.version,
            "log_tag": log_tag
        }
        
        # In a real implementation, this would write to a persistent store
        logger.info("Belief drift monitoring result for project %s: drift=%s, alignment=%.2f", 
                   project_id, drift_detected, overall_alignment)
        
        # Log to console for demonstration
        print(f"Logged belief drift monitoring result to {log_tag}: {json.dumps(result, indent=2)}")
        
        return result


# Create singleton instance
drift_monitor = BeliefDriftMonitor()

def monitor_belief_drift(
    project_id: str,
    sage_summaries: List[Dict[str, Any]],
    critic_logs: List[Dict[str, Any]],
    project_goals: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Monitor belief drift using the Belief Drift Monitor.
    
    Args:
        project_id: Project identifier
        sage_summaries: List of recent SAGE summaries
        critic_logs: List of recent CRITIC logs
        project_goals: Project goal beliefs
        
    Returns:
        Dictionary containing the monitoring result
    """
    return drift_monitor.monitor_belief_drift(
        project_id,
        sage_summaries,
        critic_logs,
        project_goals
    )
