"""
Orchestrator API Endpoints

This module implements the API endpoints for the Orchestrator Multi-Modal Planning
& Approval System, exposing the functionality through a RESTful API.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple, Callable

# Import orchestrator components
from src.orchestrator.consultation import ConsultationManager
from src.orchestrator.approval import ApprovalManager
from src.orchestrator.credentials import CredentialManager, CredentialIntake
from src.orchestrator.checkpoint import CheckpointManager
from src.orchestrator.logging import OrchestratorLogger
from src.orchestrator.reflection import ReflectionManager

class OrchestratorAPI:
    """
    Provides API endpoints for the Orchestrator Multi-Modal Planning & Approval System.
    
    This class integrates all the orchestrator components and exposes their
    functionality through a set of API endpoints.
    """
    
    def __init__(
        self,
        memory_writer: Callable,
        base_directory: str = "/home/ubuntu/workspace/personal-ai-agent"
    ):
        """
        Initialize the orchestrator API.
        
        Args:
            memory_writer: Function to write memories
            base_directory: Base directory for logs and data
        """
        self.base_directory = base_directory
        self.logs_directory = os.path.join(base_directory, "logs")
        
        # Initialize component managers
        self.consultation_manager = ConsultationManager(
            sessions_directory=os.path.join(self.logs_directory, "sessions")
        )
        
        self.approval_manager = ApprovalManager(
            consultation_manager=self.consultation_manager,
            goals_directory=os.path.join(self.logs_directory, "goals")
        )
        
        self.credential_manager = CredentialManager(
            secrets_directory=os.path.join(self.logs_directory, "secrets")
        )
        
        self.credential_intake = CredentialIntake(
            credential_manager=self.credential_manager
        )
        
        self.checkpoint_manager = CheckpointManager(
            checkpoints_directory=os.path.join(self.logs_directory, "checkpoints")
        )
        
        self.logger = OrchestratorLogger(
            logs_directory=self.logs_directory
        )
        
        self.reflection_manager = ReflectionManager(
            reflections_directory=os.path.join(self.logs_directory, "reflections")
        )
        
        # Set memory writer for components that need it
        self.memory_writer = memory_writer
        self.logger.set_memory_writer(memory_writer)
        self.reflection_manager.set_memory_writer(memory_writer)
        
    def consult(self, operator_id: str, goal: str) -> Dict[str, Any]:
        """
        Begin a consultation session with the operator.
        
        Args:
            operator_id: ID of the operator
            goal: Initial goal statement from the operator
            
        Returns:
            Consultation session details
        """
        # Create a new consultation session
        session = self.consultation_manager.create_session(operator_id, goal)
        
        # Log the start of consultation
        self.logger.log_consultation_start(goal, operator_id, session.session_id)
        
        # Log the questions being asked
        self.logger.log_consultation_questions(session.session_id, len(session.questions))
        
        # Get the first question
        next_question = session.get_next_question()
        
        return {
            "session_id": session.session_id,
            "mode": session.mode,
            "goal": session.goal,
            "goal_type": session.goal_type,
            "next_question": next_question
        }
        
    def respond_to_question(self, session_id: str, question_id: str, answer: str) -> Dict[str, Any]:
        """
        Record an answer to a consultation question and get the next question or plan.
        
        Args:
            session_id: ID of the consultation session
            question_id: ID of the question being answered
            answer: Operator's answer to the question
            
        Returns:
            Next question or generated plan
        """
        # Record the answer and get the next question
        has_more_questions, next_question, plan = self.consultation_manager.answer_question(
            session_id, question_id, answer
        )
        
        # If no more questions, generate the plan and log it
        if not has_more_questions and plan:
            session = self.consultation_manager.get_session(session_id)
            self.logger.log_plan_creation(session_id, plan["title"], len(plan["phases"]))
            self.logger.log_awaiting_approval(session_id)
            
        return {
            "has_more_questions": has_more_questions,
            "next_question": next_question,
            "plan": plan
        }
        
    def confirm(self, session_id: str, approved: bool, modifications: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Confirm or reject a plan proposed during consultation.
        
        Args:
            session_id: ID of the consultation session
            approved: Whether the plan is approved
            modifications: Optional modifications to the plan
            
        Returns:
            Goal details if approved, error if rejected
        """
        if not approved:
            return {
                "status": "rejected",
                "message": "Plan rejected by operator",
                "session_id": session_id
            }
            
        # Confirm the plan and create a goal
        goal = self.approval_manager.confirm_plan(session_id, approved, modifications)
        
        if not goal:
            return {
                "status": "error",
                "message": "Failed to create goal from plan",
                "session_id": session_id
            }
            
        # Log the plan approval
        self.logger.log_plan_approved(session_id, goal.goal_id)
        
        # Get the next task to delegate
        next_task = self.approval_manager.get_next_task(goal.goal_id)
        
        return {
            "status": "approved",
            "message": "Plan approved and goal created",
            "session_id": session_id,
            "goal_id": goal.goal_id,
            "goal_title": goal.title,
            "goal_description": goal.description,
            "next_task": next_task
        }
        
    def credentials(self, goal_id: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store credentials for a goal.
        
        Args:
            goal_id: ID of the goal
            credentials: Dictionary of credentials to store
            
        Returns:
            Status of the credential storage
        """
        try:
            # Gather and store the credentials
            credential_id = self.credential_intake.gather_credentials(goal_id, credentials)
            
            # Log the credential storage
            credential_types = list(credentials.keys())
            self.logger.log_credentials_stored(goal_id, credential_types)
            
            return {
                "status": "success",
                "message": "Credentials stored successfully",
                "credential_id": credential_id,
                "goal_id": goal_id
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e),
                "goal_id": goal_id
            }
            
    def checkpoint(
        self,
        agent_id: str,
        goal_id: str,
        subgoal_id: str,
        checkpoint_name: str,
        checkpoint_type: str,
        output_memory_id: str,
        auto_approve_if_silent: bool = False,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a checkpoint for a task.
        
        Args:
            agent_id: ID of the agent creating the checkpoint
            goal_id: ID of the goal
            subgoal_id: ID of the subgoal
            checkpoint_name: Name of the checkpoint
            checkpoint_type: Type of checkpoint ("hard" or "soft")
            output_memory_id: ID of the memory containing the output
            auto_approve_if_silent: Whether to auto-approve if no response
            details: Additional details about the checkpoint
            
        Returns:
            Checkpoint details
        """
        try:
            # Create the checkpoint
            checkpoint = self.checkpoint_manager.create_checkpoint(
                checkpoint_name=checkpoint_name,
                checkpoint_type=checkpoint_type,
                goal_id=goal_id,
                subgoal_id=subgoal_id,
                agent_id=agent_id,
                output_memory_id=output_memory_id,
                auto_approve_if_silent=auto_approve_if_silent,
                details=details
            )
            
            # Log the checkpoint creation
            self.logger.log_checkpoint_created(goal_id, checkpoint_name, checkpoint_type, agent_id)
            
            # Auto-approve soft checkpoints if configured
            status = checkpoint.status
            if checkpoint_type == "soft" and auto_approve_if_silent:
                # Auto-approve after a delay (in a real system)
                # For now, we'll just approve it immediately
                checkpoint = self.checkpoint_manager.approve_checkpoint(
                    checkpoint.checkpoint_id,
                    feedback="Auto-approved due to auto_approve_if_silent setting"
                )
                status = checkpoint.status
                
                # Log the auto-approval
                if status == "approved":
                    self.logger.log_checkpoint_approved(goal_id, checkpoint_name, agent_id)
                    
            return {
                "status": "success",
                "checkpoint_id": checkpoint.checkpoint_id,
                "checkpoint_status": status,
                "message": f"Checkpoint '{checkpoint_name}' created successfully",
                "requires_approval": checkpoint_type == "hard" or not auto_approve_if_silent
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
    def review_status(self, goal_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List pending checkpoints.
        
        Args:
            goal_id: Optional goal ID to filter by
            
        Returns:
            List of pending checkpoints
        """
        # Get pending checkpoints
        pending_checkpoints = self.checkpoint_manager.get_pending_checkpoints(goal_id)
        
        # Group by goal
        checkpoints_by_goal = {}
        for checkpoint in pending_checkpoints:
            goal_id = checkpoint["goal_id"]
            if goal_id not in checkpoints_by_goal:
                checkpoints_by_goal[goal_id] = []
            checkpoints_by_goal[goal_id].append(checkpoint)
            
        return {
            "status": "success",
            "pending_count": len(pending_checkpoints),
            "pending_checkpoints": pending_checkpoints,
            "checkpoints_by_goal": checkpoints_by_goal
        }
        
    def approve(
        self,
        checkpoint_id: str,
        approved: bool,
        feedback: Optional[str] = None,
        modifications: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Approve or reject a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            approved: Whether the checkpoint is approved
            feedback: Optional feedback from the operator
            modifications: Optional modifications to the output
            
        Returns:
            Updated checkpoint details
        """
        try:
            # Get the checkpoint
            checkpoint = self.checkpoint_manager.get_checkpoint(checkpoint_id)
            
            if approved:
                # Approve the checkpoint
                updated_checkpoint = self.checkpoint_manager.approve_checkpoint(
                    checkpoint_id, feedback, modifications
                )
                
                # Log the approval
                self.logger.log_checkpoint_approved(
                    updated_checkpoint.goal_id,
                    updated_checkpoint.checkpoint_name,
                    updated_checkpoint.agent_id
                )
                
                # Check if we can proceed with the next task
                can_proceed = self.checkpoint_manager.can_proceed(
                    updated_checkpoint.goal_id,
                    updated_checkpoint.subgoal_id
                )
                
                # Get the next task if we can proceed
                next_task = None
                if can_proceed:
                    next_task = self.approval_manager.get_next_task(updated_checkpoint.goal_id)
                    
                return {
                    "status": "success",
                    "message": "Checkpoint approved",
                    "checkpoint_id": checkpoint_id,
                    "checkpoint_status": updated_checkpoint.status,
                    "can_proceed": can_proceed,
                    "next_task": next_task
                }
            else:
                # Reject the checkpoint
                updated_checkpoint = self.checkpoint_manager.reject_checkpoint(
                    checkpoint_id, feedback or "Rejected by operator"
                )
                
                # Log the rejection
                self.logger.log_checkpoint_rejected(
                    updated_checkpoint.goal_id,
                    updated_checkpoint.checkpoint_name,
                    updated_checkpoint.agent_id,
                    feedback or "Rejected by operator"
                )
                
                return {
                    "status": "success",
                    "message": "Checkpoint rejected",
                    "checkpoint_id": checkpoint_id,
                    "checkpoint_status": updated_checkpoint.status
                }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
    def delegate(self, goal_id: str, subgoal_id: str) -> Dict[str, Any]:
        """
        Delegate a task to an agent.
        
        Args:
            goal_id: ID of the goal
            subgoal_id: ID of the subgoal to delegate
            
        Returns:
            Delegation details
        """
        try:
            # Delegate the task
            delegation = self.approval_manager.delegate_task(goal_id, subgoal_id)
            
            # Log the delegation
            self.logger.log_task_delegation(
                goal_id,
                delegation["agent_id"],
                delegation["title"],
                delegation["tools"]
            )
            
            return {
                "status": "success",
                "message": f"Task delegated to {delegation['agent_id']}",
                "delegation": delegation
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
    def create_reflection(
        self,
        goal_id: str,
        phase_title: str,
        phase_number: int,
        total_phases: int,
        agent_contributions: Dict[str, List[str]],
        outcomes: List[str],
        start_time: str,
        end_time: str
    ) -> Dict[str, Any]:
        """
        Create a reflection for a completed phase.
        
        Args:
            goal_id: ID of the goal
            phase_title: Title of the completed phase
            phase_number: Number of the phase (1-based)
            total_phases: Total number of phases
            agent_contributions: Dictionary mapping agent IDs to lists of contributions
            outcomes: List of outcomes achieved in this phase
            start_time: ISO format timestamp when the phase started
            end_time: ISO format timestamp when the phase completed
            
        Returns:
            Reflection details
        """
        try:
            # Create the reflection
            memory_id = self.reflection_manager.create_phase_reflection(
                goal_id=goal_id,
                phase_title=phase_title,
                phase_number=phase_number,
                total_phases=total_phases,
                agent_contributions=agent_contributions,
                outcomes=outcomes,
                start_time=start_time,
                end_time=end_time
            )
            
            return {
                "status": "success",
                "message": "Reflection created successfully",
                "memory_id": memory_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
    def create_goal_reflection(
        self,
        goal_id: str,
        goal_title: str,
        phase_count: int,
        agent_contributions: Dict[str, List[str]],
        outcomes: List[str],
        start_time: str,
        end_time: str
    ) -> Dict[str, Any]:
        """
        Create a reflection for a completed goal.
        
        Args:
            goal_id: ID of the goal
            goal_title: Title of the completed goal
            phase_count: Number of phases in the goal
            agent_contributions: Dictionary mapping agent IDs to lists of contributions
            outcomes: List of outcomes achieved in this goal
            start_time: ISO format timestamp when the goal started
            end_time: ISO format timestamp when the goal completed
            
        Returns:
            Reflection details
        """
        try:
            # Create the reflection
            memory_id = self.reflection_manager.create_goal_reflection(
                goal_id=goal_id,
                goal_title=goal_title,
                phase_count=phase_count,
                agent_contributions=agent_contributions,
                outcomes=outcomes,
                start_time=start_time,
                end_time=end_time
            )
            
            # Log the goal completion
            self.logger.log_goal_completed(goal_id, goal_title)
            
            return {
                "status": "success",
                "message": "Goal reflection created successfully",
                "memory_id": memory_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
            
    def get_action_log(self, goal_id: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Get the action log for a goal.
        
        Args:
            goal_id: Optional goal ID to filter by
            limit: Maximum number of entries to return
            
        Returns:
            Action log entries
        """
        # Get the action log
        log_entries = self.logger.get_action_log(limit=limit, goal_id=goal_id)
        
        return {
            "status": "success",
            "count": len(log_entries),
            "log_entries": log_entries
        }
        
    def get_progress_report(self, goal_id: str) -> Dict[str, Any]:
        """
        Get a progress report for a goal.
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            Progress report
        """
        # Generate the progress report
        report = self.logger.generate_progress_report(goal_id)
        
        # Save the report
        report_path = self.logger.save_progress_report(goal_id)
        
        return {
            "status": "success",
            "report": report,
            "report_path": report_path
        }
