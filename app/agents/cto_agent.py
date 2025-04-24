"""
CTO Agent Module

This module provides the implementation for the CTO agent, which is responsible for
auditing project memory, validating schema compliance, and identifying potential issues.

The CTO agent is part of the Promethios agent ecosystem and follows the Agent SDK pattern.
"""

from datetime import datetime
import logging
import traceback
from typing import Dict, Any, Optional, List

# Import schema
from app.schemas.cto_schema import CTOAuditRequest, CTOAuditResult, CTOErrorResult

# Import agent_sdk
try:
    from agent_sdk.agent_sdk import AgentSDK
    AGENT_SDK_AVAILABLE = True
except ImportError:
    AGENT_SDK_AVAILABLE = False
    print("❌ agent_sdk import failed")

# Import schema registry and validation utilities
try:
    from app.schema_registry import SCHEMA_REGISTRY
    from app.utils.schema_utils import validate_project_memory
    SCHEMA_UTILS_AVAILABLE = True
except ImportError:
    SCHEMA_UTILS_AVAILABLE = False
    print("❌ schema_utils import failed")

# Import project memory
try:
    from app.memory import PROJECT_MEMORY
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("❌ project_memory import failed")

# Import system log module
try:
    from memory.system_log import log_event
    SYSTEM_LOG_AVAILABLE = True
except ImportError:
    SYSTEM_LOG_AVAILABLE = False
    print("❌ system_log import failed")

# Configure logging
logger = logging.getLogger("agents.cto")

class CTOAgent:
    """
    CTO Agent for auditing project memory and schema compliance
    
    This agent is responsible for:
    1. Auditing project memory for schema compliance
    2. Identifying potential issues in the system
    3. Logging warnings and errors for further investigation
    """
    
    def __init__(self):
        """Initialize the CTO agent."""
        self.name = "CTO"
        self.description = "Technical auditor for project memory and schema compliance"
        self.tools = ["audit_memory", "validate_schema", "check_reflection"]
        
        # Initialize Agent SDK if available
        if AGENT_SDK_AVAILABLE:
            self.sdk = AgentSDK(agent_name="cto")
    
    def run_agent(self, request: CTOAuditRequest) -> CTOAuditResult:
        """
        Run the CTO agent with the given request.
        
        Args:
            request: The CTOAuditRequest containing project_id and tools
            
        Returns:
            CTOAuditResult containing the response and metadata
        """
        try:
            logger.info(f"Running CTO agent audit for project_id: {request.project_id}")
            print(f"🚀 CTO agent audit started")
            print(f"🆔 Project ID: {request.project_id}")
            print(f"🧰 Tools: {request.tools}")
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("CTO", f"Starting audit for project_id: {request.project_id}", request.project_id)
            
            # Check if memory is available
            if not MEMORY_AVAILABLE:
                error_msg = "Project memory is not available"
                logger.error(error_msg)
                return CTOErrorResult(
                    status="error",
                    message=error_msg,
                    project_id=request.project_id
                )
            
            # Get project memory
            memory = PROJECT_MEMORY.get(request.project_id, {})
            loop = memory.get("loop_count", 0)
            reflection = memory.get("last_reflection", {})
            
            # Validate project memory if schema utils are available
            issues = {}
            if SCHEMA_UTILS_AVAILABLE:
                validation = validate_project_memory(request.project_id, PROJECT_MEMORY)
                if validation:
                    issues["schema_violations"] = validation
            
            # Check reflection confidence
            if reflection.get("confidence", 1.0) < 0.5:
                issues["weak_reflection"] = reflection
            
            # Check agent completion
            if len(memory.get("completed_steps", [])) < 3:
                issues["agent_shortfall"] = memory.get("completed_steps", [])
            
            # Create result
            result = {
                "status": "success",
                "project_id": request.project_id,
                "loop": loop,
                "timestamp": datetime.utcnow().isoformat(),
                "issues_found": bool(issues),
                "issues": issues,
                "summary": f"CTO audit after loop {loop}: {'issues found' if issues else 'clean'}"
            }
            
            # Update project memory with audit results
            if MEMORY_AVAILABLE:
                PROJECT_MEMORY.setdefault(request.project_id, {}).setdefault("cto_reflections", []).append(result)
                
                # Add system flags if issues were found
                if issues:
                    PROJECT_MEMORY.setdefault(request.project_id, {}).setdefault("system_flags", []).append({
                        "timestamp": result["timestamp"],
                        "level": "warning",
                        "origin": "cto",
                        "issues": issues
                    })
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("CTO", f"Audit completed for project_id: {request.project_id}", request.project_id, {
                    "issues_found": bool(issues)
                })
            
            # Return result
            return CTOAuditResult(**result)
            
        except Exception as e:
            error_msg = f"Error running CTO agent: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            
            if SYSTEM_LOG_AVAILABLE:
                log_event("CTO", f"Error: {str(e)}", request.project_id)
            
            # Return error response
            return CTOErrorResult(
                status="error",
                message=error_msg,
                project_id=request.project_id
            )

# Create an instance of the agent
cto_agent = CTOAgent()

def run_cto_agent(project_id: str, tools: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run the CTO agent with the given project_id.
    
    This function provides backward compatibility with the legacy implementation
    while using the new Agent SDK pattern.
    
    Args:
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    # Create a request object
    request = CTOAuditRequest(
        project_id=project_id,
        tools=tools if tools is not None else ["audit_memory", "validate_schema", "check_reflection"]
    )
    
    # Run the agent
    result = cto_agent.run_agent(request)
    
    # Convert to dict for backward compatibility
    return result.dict()
