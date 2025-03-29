"""
Control Enforcer Module

This module enforces runtime permissions, execution limits, and memory restrictions for AI agents
based on the phase-control-schema.json configuration.
"""

import os
import json
import time
import logging
import threading
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import jsonschema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ControlEnforcer:
    """
    Middleware that enforces agent permissions and restrictions based on control schema.
    """
    
    def __init__(self, schema_path: str = None):
        """
        Initialize the control enforcer with a schema path.
        
        Args:
            schema_path: Path to the control schema JSON file
        """
        self.schema_path = schema_path or "app/phase-control-schema.json"
        self.schema = self._load_schema()
        self.agent_schemas = {}  # Cache for agent-specific schemas
        self.action_counters = {}  # Track actions for rate limiting
        self.violation_counts = {}  # Track violations per agent
        self.agent_start_times = {}  # Track agent start times for lifecycle management
        
        # Create locks for thread safety
        self.counter_lock = threading.Lock()
        self.schema_lock = threading.Lock()
    
    def _load_schema(self) -> Dict[str, Any]:
        """
        Load the control schema from file.
        
        Returns:
            The loaded schema as a dictionary
        """
        try:
            with open(self.schema_path, 'r') as f:
                schema = json.load(f)
            logger.info(f"Loaded control schema from {self.schema_path}")
            return schema
        except Exception as e:
            logger.error(f"Error loading control schema: {str(e)}")
            # Return a minimal default schema
            return {
                "permissions": {
                    "tools": [],
                    "code_execution": False,
                    "memory_scope": [],
                    "write_to_memory": False,
                    "max_retries": 0,
                    "escalate_on_confidence_below": 1.0,
                    "rate_limit_per_minute": 1,
                    "allow_github_commits": False,
                    "agent_lifecycle": {
                        "max_run_time_sec": 60,
                        "expire_after_completion": True
                    }
                },
                "schema_version": "1.0.0",
                "schema_id": "default-control-schema"
            }
    
    def load_agent_schema(self, agent_name: str, agent_config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load an agent-specific schema, which may reference or override the base schema.
        
        Args:
            agent_name: Name of the agent
            agent_config_path: Path to the agent's config file
            
        Returns:
            The agent's control schema
        """
        with self.schema_lock:
            # Check if we already have this agent's schema cached
            if agent_name in self.agent_schemas:
                return self.agent_schemas[agent_name]
            
            # If no config path provided, use default location
            if not agent_config_path:
                agent_config_path = f"app/prompts/{agent_name}.json"
            
            try:
                # Load agent config
                with open(agent_config_path, 'r') as f:
                    agent_config = json.load(f)
                
                # Check if agent config references the control schema
                if "control_schema" in agent_config:
                    # If it's a string, it's a reference to another schema file
                    if isinstance(agent_config["control_schema"], str):
                        schema_ref = agent_config["control_schema"]
                        if schema_ref == "default":
                            agent_schema = self.schema.copy()
                        else:
                            # Load the referenced schema
                            with open(schema_ref, 'r') as f:
                                agent_schema = json.load(f)
                    # If it's a dict, it contains overrides
                    elif isinstance(agent_config["control_schema"], dict):
                        # Start with base schema
                        agent_schema = self.schema.copy()
                        
                        # Apply overrides
                        self._apply_overrides(agent_schema, agent_config["control_schema"])
                    else:
                        logger.warning(f"Invalid control_schema format for agent {agent_name}, using default")
                        agent_schema = self.schema.copy()
                else:
                    # No control schema specified, use default
                    agent_schema = self.schema.copy()
                
                # Cache the schema
                self.agent_schemas[agent_name] = agent_schema
                return agent_schema
                
            except Exception as e:
                logger.error(f"Error loading agent schema for {agent_name}: {str(e)}")
                # Return the default schema
                return self.schema.copy()
    
    def _apply_overrides(self, base_schema: Dict[str, Any], overrides: Dict[str, Any]) -> None:
        """
        Apply overrides to a base schema.
        
        Args:
            base_schema: The base schema to modify
            overrides: The overrides to apply
        """
        # Check if permission elevation is allowed
        allow_elevation = base_schema.get("override_rules", {}).get("allow_permission_elevation", False)
        
        # Apply overrides recursively
        for key, value in overrides.items():
            if key in base_schema:
                if isinstance(value, dict) and isinstance(base_schema[key], dict):
                    # Recursively apply nested overrides
                    self._apply_overrides(base_schema[key], value)
                else:
                    # Check for permission elevation
                    if not allow_elevation and key in ["tools", "code_execution", "memory_scope", "write_to_memory", "allow_github_commits"]:
                        # For boolean permissions, only allow restriction (True -> False)
                        if isinstance(value, bool) and isinstance(base_schema[key], bool):
                            if value and not base_schema[key]:
                                logger.warning(f"Permission elevation not allowed: {key}")
                                continue
                        
                        # For list permissions, only allow restriction (removing items)
                        if isinstance(value, list) and isinstance(base_schema[key], list):
                            if any(item not in base_schema[key] for item in value):
                                logger.warning(f"Permission elevation not allowed: {key}")
                                continue
                    
                    # Apply the override
                    base_schema[key] = value
            else:
                # Add new key if it doesn't exist in base schema
                base_schema[key] = value
    
    def register_agent_start(self, agent_name: str) -> None:
        """
        Register the start of an agent's execution.
        
        Args:
            agent_name: Name of the agent
        """
        with self.counter_lock:
            self.agent_start_times[agent_name] = time.time()
            self.action_counters[agent_name] = {
                "last_minute_actions": 0,
                "last_minute_start": time.time(),
                "total_actions": 0,
                "retry_counts": {}
            }
            self.violation_counts[agent_name] = 0
    
    def check_lifecycle(self, agent_name: str) -> bool:
        """
        Check if an agent has exceeded its lifecycle limits.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if the agent should continue, False if it should terminate
        """
        with self.counter_lock:
            # If agent not registered, register it now
            if agent_name not in self.agent_start_times:
                self.register_agent_start(agent_name)
                return True
            
            # Get agent schema
            agent_schema = self.load_agent_schema(agent_name)
            lifecycle = agent_schema["permissions"]["agent_lifecycle"]
            
            # Check max run time
            current_time = time.time()
            run_time = current_time - self.agent_start_times[agent_name]
            
            if run_time > lifecycle["max_run_time_sec"]:
                logger.warning(f"Agent {agent_name} exceeded max run time of {lifecycle['max_run_time_sec']} seconds")
                self._log_violation(agent_name, "lifecycle", "max_run_time_exceeded", 
                                   {"run_time": run_time, "max_run_time": lifecycle["max_run_time_sec"]})
                return False
            
            return True
    
    def check_rate_limit(self, agent_name: str) -> bool:
        """
        Check if an agent has exceeded its rate limit.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if the action is allowed, False if rate limited
        """
        with self.counter_lock:
            # If agent not registered, register it now
            if agent_name not in self.action_counters:
                self.register_agent_start(agent_name)
            
            # Get agent schema
            agent_schema = self.load_agent_schema(agent_name)
            rate_limit = agent_schema["permissions"]["rate_limit_per_minute"]
            
            # Get counter data
            counter_data = self.action_counters[agent_name]
            current_time = time.time()
            
            # Reset counter if a minute has passed
            if current_time - counter_data["last_minute_start"] > 60:
                counter_data["last_minute_actions"] = 0
                counter_data["last_minute_start"] = current_time
            
            # Check rate limit
            if counter_data["last_minute_actions"] >= rate_limit:
                logger.warning(f"Agent {agent_name} exceeded rate limit of {rate_limit} actions per minute")
                self._log_violation(agent_name, "rate_limit", "rate_limit_exceeded", 
                                   {"actions": counter_data["last_minute_actions"], "limit": rate_limit})
                return False
            
            # Increment counter
            counter_data["last_minute_actions"] += 1
            counter_data["total_actions"] += 1
            
            return True
    
    def check_retry_limit(self, agent_name: str, action_id: str) -> bool:
        """
        Check if an agent has exceeded its retry limit for a specific action.
        
        Args:
            agent_name: Name of the agent
            action_id: Identifier for the action being retried
            
        Returns:
            True if the retry is allowed, False if retry limit exceeded
        """
        with self.counter_lock:
            # If agent not registered, register it now
            if agent_name not in self.action_counters:
                self.register_agent_start(agent_name)
            
            # Get agent schema
            agent_schema = self.load_agent_schema(agent_name)
            max_retries = agent_schema["permissions"]["max_retries"]
            
            # Get retry counts
            retry_counts = self.action_counters[agent_name]["retry_counts"]
            
            # Initialize retry count if not exists
            if action_id not in retry_counts:
                retry_counts[action_id] = 0
            
            # Check retry limit
            if retry_counts[action_id] >= max_retries:
                logger.warning(f"Agent {agent_name} exceeded retry limit of {max_retries} for action {action_id}")
                self._log_violation(agent_name, "retry_limit", "retry_limit_exceeded", 
                                   {"action_id": action_id, "retries": retry_counts[action_id], "limit": max_retries})
                return False
            
            # Increment retry count
            retry_counts[action_id] += 1
            
            return True
    
    def check_tool_permission(self, agent_name: str, tool_name: str) -> bool:
        """
        Check if an agent has permission to use a specific tool.
        
        Args:
            agent_name: Name of the agent
            tool_name: Name of the tool
            
        Returns:
            True if the tool use is allowed, False if not
        """
        # Get agent schema
        agent_schema = self.load_agent_schema(agent_name)
        allowed_tools = agent_schema["permissions"]["tools"]
        
        # Special case for github_commit
        if tool_name == "github_commit" and not agent_schema["permissions"]["allow_github_commits"]:
            logger.warning(f"Agent {agent_name} attempted to use github_commit without permission")
            self._log_violation(agent_name, "tool_permission", "github_commit_not_allowed", 
                               {"tool": tool_name})
            return False
        
        # Check if tool is in allowed list
        if tool_name not in allowed_tools:
            logger.warning(f"Agent {agent_name} attempted to use unauthorized tool: {tool_name}")
            self._log_violation(agent_name, "tool_permission", "unauthorized_tool", 
                               {"tool": tool_name, "allowed_tools": allowed_tools})
            return False
        
        return True
    
    def check_code_execution(self, agent_name: str) -> bool:
        """
        Check if an agent has permission to execute code.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if code execution is allowed, False if not
        """
        # Get agent schema
        agent_schema = self.load_agent_schema(agent_name)
        code_execution = agent_schema["permissions"]["code_execution"]
        
        if not code_execution:
            logger.warning(f"Agent {agent_name} attempted code execution without permission")
            self._log_violation(agent_name, "code_execution", "code_execution_not_allowed", {})
            return False
        
        return True
    
    def check_memory_access(self, agent_name: str, memory_scope: str, write_operation: bool = False) -> bool:
        """
        Check if an agent has permission to access a specific memory scope.
        
        Args:
            agent_name: Name of the agent
            memory_scope: The memory scope being accessed
            write_operation: Whether this is a write operation
            
        Returns:
            True if memory access is allowed, False if not
        """
        # Get agent schema
        agent_schema = self.load_agent_schema(agent_name)
        allowed_scopes = agent_schema["permissions"]["memory_scope"]
        write_to_memory = agent_schema["permissions"]["write_to_memory"]
        
        # Check write permission
        if write_operation and not write_to_memory:
            logger.warning(f"Agent {agent_name} attempted to write to memory without permission")
            self._log_violation(agent_name, "memory_access", "write_to_memory_not_allowed", 
                               {"memory_scope": memory_scope})
            return False
        
        # Check scope permission
        if memory_scope not in allowed_scopes:
            logger.warning(f"Agent {agent_name} attempted to access unauthorized memory scope: {memory_scope}")
            self._log_violation(agent_name, "memory_access", "unauthorized_memory_scope", 
                               {"memory_scope": memory_scope, "allowed_scopes": allowed_scopes})
            return False
        
        return True
    
    def check_confidence(self, agent_name: str, confidence: float) -> Dict[str, Any]:
        """
        Check if an agent's confidence level requires escalation.
        
        Args:
            agent_name: Name of the agent
            confidence: Confidence level (0.0 to 1.0)
            
        Returns:
            Dict with escalation info: {"escalate": bool, "reason": str}
        """
        # Get agent schema
        agent_schema = self.load_agent_schema(agent_name)
        threshold = agent_schema["permissions"]["escalate_on_confidence_below"]
        
        if confidence < threshold:
            logger.info(f"Agent {agent_name} confidence {confidence} below threshold {threshold}, escalating")
            return {
                "escalate": True,
                "reason": f"Confidence {confidence} below threshold {threshold}"
            }
        
        return {
            "escalate": False
        }
    
    def _log_violation(self, agent_name: str, violation_type: str, violation_reason: str, details: Dict[str, Any]) -> None:
        """
        Log a violation to the control_violations.json file.
        
        Args:
            agent_name: Name of the agent
            violation_type: Type of violation
            violation_reason: Reason for the violation
            details: Additional details about the violation
        """
        # Increment violation count
        with self.counter_lock:
            self.violation_counts[agent_name] = self.violation_counts.get(agent_name, 0) + 1
        
        # Create violation log entry
        violation = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "violation_type": violation_type,
            "violation_reason": violation_reason,
            "details": details,
            "violation_count": self.violation_counts[agent_name]
        }
        
        # Get agent schema for violation handling
        agent_schema = self.load_agent_schema(agent_name)
        violation_handling = agent_schema.get("violation_handling", {})
        
        # Add recommended action
        action = violation_handling.get("action_on_violation", "block")
        violation["recommended_action"] = action
        
        # Check if threshold exceeded
        threshold = violation_handling.get("violation_threshold", 3)
        if self.violation_counts[agent_name] >= threshold:
            severe_action = violation_handling.get("severe_action", "terminate")
            violation["threshold_exceeded"] = True
            violation["severe_action"] = severe_action
        else:
            violation["threshold_exceeded"] = False
        
        # Log to file
        log_file = "app/logs/control_violations.json"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        try:
            # Read existing logs
            violations = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    try:
                        violations = json.load(f)
                    except json.JSONDecodeError:
                        violations = []
            
            # Append new violation
            violations.append(violation)
            
            # Write back to file
            with open(log_file, 'w') as f:
                json.dump(violations, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error logging violation: {str(e)}")
            # Fallback to appending
            try:
                with open(log_file, 'a') as f:
                    f.write(json.dumps(violation) + "\n")
            except:
                pass
        
        # Check if guardian notification is needed
        notify_guardian = violation_handling.get("notify_guardian", True)
        if notify_guardian:
            self._notify_guardian(violation)
        
        # Check if human notification is needed
        notify_human = violation_handling.get("notify_human", False)
        if notify_human:
            self._notify_human(violation)
    
    def _notify_guardian(self, violation: Dict[str, Any]) -> None:
        """
        Notify the guardian agent about a violation.
        
        Args:
            violation: The violation details
        """
        # This would typically involve sending a message to the guardian agent
        # For now, just log it
        logger.info(f"Guardian notification: {violation}")
        
        # In a real implementation, this would trigger the guardian agent
        # Example:
        # guardian_agent.notify_violation(violation)
    
    def _notify_human(self, violation: Dict[str, Any]) -> None:
        """
        Notify a human operator about a violation.
        
        Args:
            violation: The violation details
        """
        # This would typically involve sending an email, Slack message, etc.
        # For now, just log it
        logger.warning(f"Human notification: {violation}")
        
        # In a real implementation, this would send a notification
        # Example:
        # notification_service.send_email(
        #     to="admin@example.com",
        #     subject=f"Agent violation: {violation['agent_name']}",
        #     body=json.dumps(violation, indent=2)
        # )
    
    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Validate a schema against the JSON schema definition.
        
        Args:
            schema: The schema to validate
            
        Returns:
            True if valid, False if not
        """
        try:
            # This would validate against a formal JSON schema definition
            # For now, just check required fields
            required_fields = ["permissions", "schema_version", "schema_id"]
            for field in required_fields:
                if field not in schema:
                    logger.error(f"Schema missing required field: {field}")
                    return False
            
            # Check permissions fields
            permissions = schema["permissions"]
            required_permission_fields = [
                "tools", "code_execution", "memory_scope", "write_to_memory",
                "max_retries", "rate_limit_per_minute", "agent_lifecycle"
            ]
            for field in required_permission_fields:
                if field not in permissions:
                    logger.error(f"Permissions missing required field: {field}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating schema: {str(e)}")
            return False
    
    def handle_violation(self, agent_name: str, violation_type: str) -> Dict[str, Any]:
        """
        Handle a violation based on the agent's schema.
        
        Args:
            agent_name: Name of the agent
            violation_type: Type of violation
            
        Returns:
            Dict with action info: {"action": str, "message": str}
        """
        # Get agent schema
        agent_schema = self.load_agent_schema(agent_name)
        violation_handling = agent_schema.get("violation_handling", {})
        
        # Get violation count
        violation_count = self.violation_counts.get(agent_name, 0)
        
        # Determine action
        if violation_count >= violation_handling.get("violation_threshold", 3):
            action = violation_handling.get("severe_action", "terminate")
        else:
            action = violation_handling.get("action_on_violation", "block")
        
        return {
            "action": action,
            "message": f"Violation of type {violation_type} detected. Action: {action}."
        }

# Create a singleton instance
_enforcer = None

def get_enforcer() -> ControlEnforcer:
    """
    Get the singleton instance of the control enforcer.
    
    Returns:
        ControlEnforcer instance
    """
    global _enforcer
    if _enforcer is None:
        _enforcer = ControlEnforcer()
    return _enforcer

# Middleware function for FastAPI
async def control_enforcer_middleware(request, call_next):
    """
    FastAPI middleware to enforce agent controls.
    
    Args:
        request: The incoming request
        call_next: The next middleware in the chain
        
    Returns:
        The response
    """
    # Extract agent name from request
    agent_name = None
    path = request.url.path
    
    # Check if this is an agent API call
    if path.startswith("/agent/"):
        agent_name = path.split("/")[2]
    
    if agent_name:
        enforcer = get_enforcer()
        
        # Check lifecycle
        if not enforcer.check_lifecycle(agent_name):
            return JSONResponse(
                status_code=403,
                content={"error": "Agent lifecycle limit exceeded"}
            )
        
        # Check rate limit
        if not enforcer.check_rate_limit(agent_name):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
    
    # Continue with the request
    response = await call_next(request)
    return response
