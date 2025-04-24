"""
GUARDIAN Agent Implementation

This module implements the GUARDIAN agent responsible for handling escalations,
system halts, operator alerts, and rollback operations.
"""

import logging
import json
import datetime
from typing import Dict, List, Any, Optional

from agent_sdk.agent_sdk import Agent
from app.schemas.guardian_schema import (
    GuardianAlertRequest,
    GuardianResponse,
    GuardianRollbackRequest,
    GuardianRollbackResult,
    GuardianErrorResult
)

# Configure logging
logger = logging.getLogger("guardian_agent")

class GuardianAgent(Agent):
    """
    GUARDIAN agent for handling system escalations and emergency responses.
    
    This agent is responsible for:
    - Halting system operations when critical issues are detected
    - Alerting human operators about system issues
    - Rolling back loops to previous states
    - Raising flags for potential issues
    """
    
    def __init__(self):
        """Initialize the GUARDIAN agent with required configuration."""
        super().__init__(
            name="GUARDIAN",
            role="Escalation Handler",
            tools=["halt", "alert_operator", "rollback_loop", "raise_flag"],
            permissions=["system_halt", "operator_notification", "loop_rollback"],
            description="Handles system escalations, emergency responses, and operator alerts",
            version="1.0.0",
            status="active",
            tone_profile={
                "formality": "high",
                "urgency": "high",
                "directness": "high"
            },
            schema_path="app/schemas/guardian_schema.py",
            trust_score=0.95,
            contract_version="1.0.0"
        )
        
        # Initialize alert counter
        self.alert_counter = 0
        
        # Initialize alert history
        self.alert_history = []
        
        logger.info("GUARDIAN agent initialized")
    
    def execute(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the GUARDIAN agent's functionality based on the request.
        
        Args:
            request_data: Dictionary containing the request data
            
        Returns:
            Dictionary containing the response data
        """
        try:
            # Validate request against schema
            request = GuardianAlertRequest(**request_data)
            
            # Generate alert ID
            self.alert_counter += 1
            alert_id = f"alert_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{self.alert_counter}"
            
            # Process the alert based on type and severity
            actions_taken = []
            system_status = "running"
            operator_notified = False
            rollback_status = None
            
            # Handle different alert types
            if request.alert_type == "security" and request.severity in ["high", "critical"]:
                actions_taken.append("system_halt")
                system_status = "halted"
                actions_taken.append("operator_notification")
                operator_notified = True
                self._halt_system(request.description)
                self._notify_operator(alert_id, request.description, request.severity)
            
            elif request.alert_type == "performance" and request.severity in ["high", "critical"]:
                actions_taken.append("performance_mitigation")
                system_status = "degraded"
                if request.severity == "critical":
                    actions_taken.append("operator_notification")
                    operator_notified = True
                    self._notify_operator(alert_id, request.description, request.severity)
            
            elif request.alert_type == "compliance":
                actions_taken.append("raise_flag")
                if request.severity in ["high", "critical"]:
                    actions_taken.append("operator_notification")
                    operator_notified = True
                    self._notify_operator(alert_id, request.description, request.severity)
            
            elif request.alert_type == "error":
                if request.loop_id:
                    actions_taken.append("rollback_loop")
                    rollback_status = "initiated"
                    self._rollback_loop(request.loop_id, request.description)
                if request.severity in ["high", "critical"]:
                    actions_taken.append("operator_notification")
                    operator_notified = True
                    self._notify_operator(alert_id, request.description, request.severity)
            
            # Create response
            response = GuardianResponse(
                status="success",
                alert_id=alert_id,
                alert_type=request.alert_type,
                severity=request.severity,
                actions_taken=actions_taken,
                system_status=system_status,
                operator_notified=operator_notified,
                rollback_status=rollback_status,
                message=f"Alert processed successfully: {', '.join(actions_taken)}"
            )
            
            # Log the alert
            self._log_alert(alert_id, request, response)
            
            return response.dict()
        
        except Exception as e:
            logger.error(f"Error processing alert: {str(e)}")
            error_response = GuardianErrorResult(
                message=f"Error processing alert: {str(e)}",
                alert_type=request_data.get("alert_type"),
                severity=request_data.get("severity"),
                loop_id=request_data.get("loop_id")
            )
            return error_response.dict()
    
    def _halt_system(self, reason: str) -> None:
        """
        Halt system operations.
        
        Args:
            reason: Reason for halting the system
        """
        logger.warning(f"SYSTEM HALT initiated: {reason}")
        # In a real implementation, this would trigger system shutdown procedures
        print(f"🔴 SYSTEM HALT: {reason}")
    
    def _notify_operator(self, alert_id: str, description: str, severity: str) -> None:
        """
        Notify human operator about an issue.
        
        Args:
            alert_id: Unique identifier for the alert
            description: Description of the issue
            severity: Severity level of the issue
        """
        logger.info(f"Operator notification sent: {alert_id} - {description} (Severity: {severity})")
        # In a real implementation, this would send notifications via email, SMS, etc.
        print(f"📢 OPERATOR ALERT ({severity}): {description}")
    
    def _rollback_loop(self, loop_id: str, reason: str) -> None:
        """
        Roll back a loop to a previous state.
        
        Args:
            loop_id: Identifier for the loop to roll back
            reason: Reason for the rollback
        """
        logger.info(f"Loop rollback initiated for {loop_id}: {reason}")
        # In a real implementation, this would trigger loop rollback procedures
        print(f"⏮️ LOOP ROLLBACK ({loop_id}): {reason}")
    
    def _log_alert(self, alert_id: str, request: GuardianAlertRequest, response: GuardianResponse) -> None:
        """
        Log alert details for future reference.
        
        Args:
            alert_id: Unique identifier for the alert
            request: Original alert request
            response: Response to the alert
        """
        alert_record = {
            "alert_id": alert_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "request": request.dict(),
            "response": response.dict()
        }
        self.alert_history.append(alert_record)
        logger.info(f"Alert logged: {alert_id}")
    
    def rollback_loop(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Roll back a loop to a previous state.
        
        Args:
            request_data: Dictionary containing the rollback request data
            
        Returns:
            Dictionary containing the rollback result
        """
        try:
            # Validate request against schema
            request = GuardianRollbackRequest(**request_data)
            
            # Simulate rollback operation
            original_step = 5  # This would be retrieved from the actual loop state
            current_step = request.rollback_to_step or (original_step - 1)
            
            # Log the rollback
            logger.info(f"Rolling back loop {request.loop_id} from step {original_step} to step {current_step}")
            
            # Create response
            response = GuardianRollbackResult(
                status="success",
                loop_id=request.loop_id,
                original_step=original_step,
                current_step=current_step,
                reason=request.reason,
                message=f"Loop {request.loop_id} successfully rolled back to step {current_step}"
            )
            
            return response.dict()
        
        except Exception as e:
            logger.error(f"Error rolling back loop: {str(e)}")
            error_response = GuardianErrorResult(
                message=f"Error rolling back loop: {str(e)}",
                loop_id=request_data.get("loop_id")
            )
            return error_response.dict()


# Create singleton instance
guardian_agent = GuardianAgent()

def process_alert(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an alert using the GUARDIAN agent.
    
    Args:
        request_data: Dictionary containing the alert request data
        
    Returns:
        Dictionary containing the alert response
    """
    return guardian_agent.execute(request_data)

def process_rollback(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a rollback request using the GUARDIAN agent.
    
    Args:
        request_data: Dictionary containing the rollback request data
        
    Returns:
        Dictionary containing the rollback result
    """
    return guardian_agent.rollback_loop(request_data)
