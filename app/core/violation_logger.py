"""
Violation Logging Module for Agent Control System

This module handles structured logging of control violations for AI agents.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define log file path
VIOLATIONS_LOG_FILE = "app/logs/control_violations.json"

class ViolationLogger:
    """
    Logger for agent control violations.
    """
    
    def __init__(self, log_file: str = None):
        """
        Initialize the violation logger.
        
        Args:
            log_file: Path to the violations log file
        """
        self.log_file = log_file or VIOLATIONS_LOG_FILE
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log_violation(self, 
                     agent_name: str, 
                     violation_type: str, 
                     violation_reason: str, 
                     details: Dict[str, Any],
                     recommended_action: str = "block",
                     threshold_exceeded: bool = False,
                     severe_action: Optional[str] = None) -> Dict[str, Any]:
        """
        Log a control violation.
        
        Args:
            agent_name: Name of the agent
            violation_type: Type of violation (e.g., tool_permission, rate_limit)
            violation_reason: Reason for the violation
            details: Additional details about the violation
            recommended_action: Recommended action to take
            threshold_exceeded: Whether violation threshold was exceeded
            severe_action: Action to take if threshold exceeded
            
        Returns:
            The violation log entry
        """
        # Create violation log entry
        violation = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "violation_type": violation_type,
            "violation_reason": violation_reason,
            "details": details,
            "recommended_action": recommended_action,
            "threshold_exceeded": threshold_exceeded
        }
        
        # Add severe action if threshold exceeded
        if threshold_exceeded and severe_action:
            violation["severe_action"] = severe_action
        
        # Add suggested override if applicable
        if violation_type in ["tool_permission", "memory_access", "code_execution"]:
            violation["suggested_override"] = self._generate_override_suggestion(
                agent_name, violation_type, violation_reason, details
            )
        
        try:
            # Read existing logs
            violations = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    try:
                        violations = json.load(f)
                        # Ensure it's a list
                        if not isinstance(violations, list):
                            violations = []
                    except json.JSONDecodeError:
                        # If file exists but is not valid JSON, start with empty list
                        violations = []
            
            # Append new violation
            violations.append(violation)
            
            # Write back to file
            with open(self.log_file, 'w') as f:
                json.dump(violations, f, indent=2)
            
            logger.info(f"Logged violation for agent {agent_name}: {violation_type} - {violation_reason}")
            
        except Exception as e:
            logger.error(f"Error logging violation: {str(e)}")
            # Fallback to appending as a new line
            try:
                with open(self.log_file, 'a') as f:
                    f.write(json.dumps(violation) + "\n")
            except Exception as append_error:
                logger.error(f"Error appending to log file: {str(append_error)}")
        
        return violation
    
    def _generate_override_suggestion(self, 
                                     agent_name: str, 
                                     violation_type: str, 
                                     violation_reason: str, 
                                     details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a suggested override for a violation.
        
        Args:
            agent_name: Name of the agent
            violation_type: Type of violation
            violation_reason: Reason for the violation
            details: Additional details about the violation
            
        Returns:
            Suggested override
        """
        if violation_type == "tool_permission":
            tool = details.get("tool", "unknown_tool")
            return {
                "type": "tool_permission",
                "config_update": {
                    "permissions": {
                        "tools": [tool]
                    }
                },
                "note": f"Add '{tool}' to allowed tools list for this agent"
            }
        
        elif violation_type == "memory_access":
            memory_scope = details.get("memory_scope", "unknown_scope")
            if violation_reason == "write_to_memory_not_allowed":
                return {
                    "type": "memory_write",
                    "config_update": {
                        "permissions": {
                            "write_to_memory": True
                        }
                    },
                    "note": "Enable write_to_memory permission for this agent"
                }
            else:
                return {
                    "type": "memory_scope",
                    "config_update": {
                        "permissions": {
                            "memory_scope": [memory_scope]
                        }
                    },
                    "note": f"Add '{memory_scope}' to allowed memory scopes for this agent"
                }
        
        elif violation_type == "code_execution":
            return {
                "type": "code_execution",
                "config_update": {
                    "permissions": {
                        "code_execution": True
                    }
                },
                "note": "Enable code_execution permission for this agent"
            }
        
        # Default override suggestion
        return {
            "type": "generic",
            "note": f"Consider adjusting permissions for {violation_type} violations"
        }
    
    def get_recent_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent violation logs.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of recent violation logs
        """
        try:
            if not os.path.exists(self.log_file):
                return []
            
            with open(self.log_file, 'r') as f:
                try:
                    violations = json.load(f)
                    
                    # Ensure it's a list
                    if not isinstance(violations, list):
                        return []
                    
                    # Sort by timestamp (newest first) and limit
                    sorted_violations = sorted(
                        violations, 
                        key=lambda x: x.get('timestamp', ''), 
                        reverse=True
                    )
                    
                    return sorted_violations[:limit]
                    
                except json.JSONDecodeError:
                    # If file is not valid JSON, try reading line by line
                    f.seek(0)
                    violations = []
                    for line in f:
                        try:
                            violation = json.loads(line.strip())
                            violations.append(violation)
                        except:
                            pass
                    
                    # Sort and limit
                    sorted_violations = sorted(
                        violations, 
                        key=lambda x: x.get('timestamp', ''), 
                        reverse=True
                    )
                    
                    return sorted_violations[:limit]
        
        except Exception as e:
            logger.error(f"Error reading violations log file: {str(e)}")
            return []
    
    def get_violations_by_agent(self, agent_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get violation logs for a specific agent.
        
        Args:
            agent_name: Name of the agent
            limit: Maximum number of logs to return
            
        Returns:
            List of violation logs for the specified agent
        """
        try:
            all_violations = self.get_recent_violations(1000)  # Get a larger set to filter from
            
            # Filter by agent name
            filtered_violations = [
                violation for violation in all_violations
                if violation.get('agent_name') == agent_name
            ]
            
            return filtered_violations[:limit]
        
        except Exception as e:
            logger.error(f"Error filtering violations by agent: {str(e)}")
            return []
    
    def get_violations_by_type(self, violation_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get violation logs for a specific violation type.
        
        Args:
            violation_type: Type of violation to filter by
            limit: Maximum number of logs to return
            
        Returns:
            List of violation logs for the specified type
        """
        try:
            all_violations = self.get_recent_violations(1000)  # Get a larger set to filter from
            
            # Filter by violation type
            filtered_violations = [
                violation for violation in all_violations
                if violation.get('violation_type') == violation_type
            ]
            
            return filtered_violations[:limit]
        
        except Exception as e:
            logger.error(f"Error filtering violations by type: {str(e)}")
            return []
    
    def get_violation_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about violation logs.
        
        Returns:
            Statistics about the violations
        """
        try:
            all_violations = self.get_recent_violations(10000)  # Get a larger set for statistics
            
            # Count by agent
            agent_counts = {}
            for violation in all_violations:
                agent = violation.get('agent_name')
                if agent:
                    agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
            # Count by violation type
            type_counts = {}
            for violation in all_violations:
                vtype = violation.get('violation_type')
                if vtype:
                    type_counts[vtype] = type_counts.get(vtype, 0) + 1
            
            # Count threshold exceeded
            threshold_exceeded_count = sum(1 for v in all_violations if v.get('threshold_exceeded', False))
            
            # Get timestamp of oldest and newest violations
            timestamps = [v.get('timestamp') for v in all_violations if v.get('timestamp')]
            oldest = min(timestamps) if timestamps else None
            newest = max(timestamps) if timestamps else None
            
            return {
                "total_violations": len(all_violations),
                "threshold_exceeded_count": threshold_exceeded_count,
                "agent_counts": agent_counts,
                "type_counts": type_counts,
                "oldest_violation": oldest,
                "newest_violation": newest
            }
        
        except Exception as e:
            logger.error(f"Error generating violation statistics: {str(e)}")
            return {
                "error": str(e),
                "total_violations": 0
            }

# Create a singleton instance
_violation_logger = None

def get_violation_logger() -> ViolationLogger:
    """
    Get the singleton instance of the violation logger.
    
    Returns:
        ViolationLogger instance
    """
    global _violation_logger
    if _violation_logger is None:
        _violation_logger = ViolationLogger()
    return _violation_logger
