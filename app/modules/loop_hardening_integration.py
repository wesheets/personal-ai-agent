"""
Loop Hardening Integration Module

This module integrates all the loop hardening components with the existing system.
It provides a unified interface for using the loop metrics, project lock manager,
snapshot optimizer, auditor agent, belief versioning, and summary realism scorer.

Schema Compatibility Note:
- All changes are modular (appending new fields, not overwriting)
- Changes are tagged as schema_patch_core or schema_patch_ui
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from datetime import datetime, timedelta
import uuid
import statistics

# Import loop hardening modules
from app.modules.loop_metrics import LoopMetricsTracker, get_loop_metrics_tracker
from app.modules.project_lock_manager import ProjectLockManager, get_project_lock_manager
from app.modules.snapshot_optimizer import SnapshotOptimizer, get_snapshot_optimizer
from app.modules.auditor_agent import AuditorAgent, get_auditor_agent
from app.modules.belief_versioning import (
    BeliefVersionManager, get_belief_version_manager,
    SemanticVersion, BeliefLock
)
from app.modules.summary_realism_scorer import (
    SummaryRealismScorer, get_summary_realism_scorer,
    SummaryDimension, AdaptiveThreshold, ConfidenceMetric
)

# Import existing system modules
from app.modules.loop import run_agent_from_loop  # Using the function from loop.py instead of LoopExecutor
from app.modules.post_loop_summary_handler import process_loop_reflection  # Import function instead of class
from app.modules.core_beliefs_integration import parse_core_beliefs, inject_belief_references, get_threshold_value  # Import functions instead of class
from app.modules.agent_dispatch import AgentDispatcher, create_dispatcher
from app.modules.tiered_orchestrator import (  # Import functions instead of class
    OrchestratorMode,
    get_orchestrator_mode_config,
    enrich_loop_with_mode_info,
    get_mode_config,
    get_depth_for_mode,
    get_agents_for_mode,
    enrich_loop_with_mode,
    adjust_agent_plan_for_mode,
    determine_optimal_mode
)

# Import schemas
from app.schemas.loop_trace import (
    LoopTrace, LoopTraceCreate, LoopTraceUpdate, LoopMetrics, LoopSummary,
    SnapshotInfo, AuditInfo, BeliefVersionInfo, ProjectLockInfo
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Schema patch version tracking
SCHEMA_PATCH_VERSION = {
    "core": "1.0.2",
    "ui": "1.0.1"
}

class LoopHardeningIntegration:
    """
    Class for integrating loop hardening components with the existing system.
    
    This class provides methods for initializing and using all loop hardening
    components in a unified way.
    """
    
    def __init__(self):
        """Initialize the loop hardening integration."""
        logger.info("Initializing loop hardening integration")
        
        # Initialize component instances
        self.metrics_tracker = get_loop_metrics_tracker()
        self.lock_manager = get_project_lock_manager()
        self.snapshot_optimizer = get_snapshot_optimizer()
        self.auditor_agent = get_auditor_agent()
        self.belief_version_manager = get_belief_version_manager()
        self.summary_realism_scorer = get_summary_realism_scorer()
        
        # Initialize existing system components
        # Note: We don't initialize LoopExecutor as it doesn't exist in the system
        # Instead we'll use the run_agent_from_loop function directly
        # Note: We don't initialize PostLoopSummaryHandler as it doesn't exist in the system
        # Instead we'll use the process_loop_reflection function directly
        # Note: We don't initialize CoreBeliefsManager as it doesn't exist in the system
        # Instead we'll use the core_beliefs_integration functions directly
        # Note: We don't initialize TieredOrchestrator as it doesn't exist in the system
        # Instead we'll use the tiered_orchestrator functions directly
        
        # We'll initialize the agent_dispatcher when needed with the specific loop_id
        self.agent_dispatcher = None
        
        # Load core beliefs
        self.core_beliefs = parse_core_beliefs()
        
        # Generate a default loop_id for internal use
        self.default_loop_id = str(uuid.uuid4())
        
        # Initialize adaptive thresholds for performance metrics
        self.adaptive_thresholds = {
            "execution_time": AdaptiveThreshold("execution_time", 0.3, 0.7, 0.1),
            "memory_usage": AdaptiveThreshold("memory_usage", 0.3, 0.7, 0.1),
            "belief_references": AdaptiveThreshold("belief_references", 0.3, 0.7, 0.1)
        }
        
        # Initialize confidence metrics for summary scoring
        self.confidence_metrics = ConfidenceMetric(base_confidence=0.6)
        
        logger.info("Loop hardening integration initialized")
    
    def _get_agent_dispatcher(self, loop_id: Optional[str] = None) -> AgentDispatcher:
        """
        Get or create an agent dispatcher for a specific loop.
        
        Args:
            loop_id: The ID of the loop, uses default_loop_id if not provided
            
        Returns:
            AgentDispatcher instance
        """
        if loop_id is None:
            loop_id = self.default_loop_id
            
        # Create a new dispatcher for this loop_id
        return create_dispatcher(loop_id)
    
    async def pre_loop_execution(self, loop_id: str, parent_id: Optional[str] = None,
                               project_id: Optional[str] = None,
                               orchestrator_mode: str = "BALANCED",
                               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform pre-loop execution tasks.
        
        Args:
            loop_id: The ID of the loop
            parent_id: Optional parent loop ID
            project_id: Optional project ID
            orchestrator_mode: Orchestrator mode (FAST, BALANCED, THOROUGH, RESEARCH)
            metadata: Optional metadata
            
        Returns:
            Dictionary with pre-execution results
        """
        logger.info(f"Performing pre-loop execution tasks for loop {loop_id}")
        
        # Initialize agent dispatcher for this loop
        self.agent_dispatcher = self._get_agent_dispatcher(loop_id)
        
        results = {}
        metadata = metadata or {}
        
        # Add schema patch version to metadata
        metadata["schema_patch_version"] = SCHEMA_PATCH_VERSION
        
        # Start metrics tracking
        metrics_start_result = await self.metrics_tracker.start_tracking(loop_id)
        results["metrics_tracking"] = metrics_start_result
        
        # Acquire project lock if project_id is provided
        if project_id:
            # Enhanced: Use semantic lock types based on orchestrator mode
            lock_type = "exclusive" if orchestrator_mode in ["THOROUGH", "RESEARCH"] else "shared"
            lock_duration = 60 if orchestrator_mode == "FAST" else (
                120 if orchestrator_mode == "BALANCED" else (
                    300 if orchestrator_mode == "THOROUGH" else 600
                )
            )
            
            lock_result = await self.lock_manager.acquire_lock(
                project_id=project_id,
                owner=f"loop:{loop_id}",
                lock_type=lock_type,
                duration_minutes=lock_duration
            )
            results["project_lock"] = lock_result
        
        # Create initial snapshot
        if orchestrator_mode in ["THOROUGH", "RESEARCH"]:
            # Enhanced: Use more detailed snapshot metadata
            snapshot_metadata = {
                "stage": "pre_execution",
                "orchestrator_mode": orchestrator_mode,
                "parent_id": parent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "schema_patch_core": SCHEMA_PATCH_VERSION["core"]
            }
            
            snapshot_result = await self.snapshot_optimizer.create_snapshot(
                loop_id=loop_id,
                snapshot_type="full",
                metadata=snapshot_metadata
            )
            results["initial_snapshot"] = snapshot_result
        
        # Set up orchestrator mode using functions instead of class
        mode = orchestrator_mode.lower()
        try:
            mode_enum = OrchestratorMode(mode)
            mode = mode_enum.value
        except ValueError:
            logger.warning(f"Invalid mode '{mode}', defaulting to BALANCED")
            mode = OrchestratorMode.BALANCED.value
            
        orchestrator_result = get_orchestrator_mode_config(mode)
        results["orchestrator_config"] = orchestrator_result
        
        # Create loop trace
        loop_trace = LoopTraceCreate(
            id=loop_id,
            parent_id=parent_id,
            start_time=datetime.utcnow().isoformat(),
            status="running",
            depth=0 if not parent_id else None,  # Will be set by depth controller
            orchestrator_mode=orchestrator_mode,
            metadata=metadata
        )
        
        # Use model_dump instead of dict for Pydantic v2 compatibility
        try:
            results["loop_trace"] = loop_trace.model_dump()
        except AttributeError:
            # Fallback for older Pydantic versions
            results["loop_trace"] = loop_trace.dict()
        
        logger.info(f"Pre-loop execution tasks completed for loop {loop_id}")
        return results
    
    async def execute_loop(self, project_id: str) -> Dict[str, Any]:
        """
        Execute a loop for a project using the run_agent_from_loop function.
        
        Args:
            project_id: The ID of the project
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"Executing loop for project {project_id}")
        
        # Use the run_agent_from_loop function from loop.py
        result = run_agent_from_loop(project_id)
        
        logger.info(f"Loop execution completed for project {project_id}")
        return result
    
    async def process_loop_summary(self, loop_id: str, 
                                 override_fatigue: bool = False,
                                 override_max_reruns: bool = False,
                                 override_by: Optional[str] = None,
                                 safety_checks: List[str] = ["all"],
                                 override_safety_blocks: bool = False) -> Dict[str, Any]:
        """
        Process loop summary using the process_loop_reflection function.
        
        Args:
            loop_id: The ID of the loop
            override_fatigue: Whether to override fatigue-based finalization
            override_max_reruns: Whether to override max reruns limit
            override_by: Who performed the override
            safety_checks: List of safety checks to run
            override_safety_blocks: Whether to override safety blocks
            
        Returns:
            Dictionary with summary processing results
        """
        logger.info(f"Processing loop summary for loop {loop_id}")
        
        # Use the process_loop_reflection function from post_loop_summary_handler.py
        result = await process_loop_reflection(
            loop_id=loop_id,
            override_fatigue=override_fatigue,
            override_max_reruns=override_max_reruns,
            override_by=override_by,
            safety_checks=safety_checks,
            override_safety_blocks=override_safety_blocks
        )
        
        # Enhanced: Add multi-dimensional scoring metadata
        if "alignment_score" in result:
            # Add schema_patch_core tag to indicate schema changes
            result["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
            
            # Add multi-dimensional scoring details if not already present
            if "dimension_scores" not in result:
                result["dimension_scores"] = {
                    "factual_accuracy": round(result.get("alignment_score", 0.5) * 0.9 + 0.05, 2),
                    "logical_consistency": round(result.get("alignment_score", 0.5) * 0.85 + 0.1, 2),
                    "emotional_congruence": round(result.get("alignment_score", 0.5) * 0.8 + 0.1, 2),
                    "temporal_coherence": round(result.get("alignment_score", 0.5) * 0.9 + 0.05, 2)
                }
            
            # Add confidence metrics if not already present
            if "confidence" not in result:
                # Calculate confidence based on various factors
                confidence = self.confidence_metrics.base_confidence
                
                # Add factors based on available data
                if result.get("bias_echo", False):
                    self.confidence_metrics.add_factor("bias_echo_detected", -0.2)
                
                if result.get("reflection_fatigue", 0) > 0.5:
                    self.confidence_metrics.add_factor("high_reflection_fatigue", -0.15)
                
                if result.get("safety_blocks_triggered", []):
                    self.confidence_metrics.add_factor("safety_blocks_triggered", -0.25)
                
                if result.get("alignment_score", 0) > 0.8:
                    self.confidence_metrics.add_factor("high_alignment_score", 0.15)
                
                result["confidence"] = round(self.confidence_metrics.calculate(), 2)
                result["confidence_explanation"] = self.confidence_metrics.get_explanation()
        
        logger.info(f"Loop summary processing completed for loop {loop_id}")
        return result
    
    async def inject_core_beliefs(self, loop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject core beliefs into loop data using the inject_belief_references function.
        
        Args:
            loop_data: The loop data
            
        Returns:
            Loop data enriched with belief references
        """
        logger.info(f"Injecting core beliefs into loop data")
        
        # Use the inject_belief_references function from core_beliefs_integration.py
        enriched_data = inject_belief_references(loop_data)
        
        # Enhanced: Add belief dependency tracking
        if "beliefs_referenced" in enriched_data:
            belief_dependencies = {}
            for belief_id in enriched_data["beliefs_referenced"]:
                # Get dependencies for this belief
                dependencies = await self.belief_version_manager.get_dependencies(belief_id)
                if dependencies:
                    belief_dependencies[belief_id] = dependencies
            
            # Add to enriched data
            if belief_dependencies:
                enriched_data["belief_dependencies"] = belief_dependencies
                enriched_data["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
        
        logger.info(f"Core beliefs injection completed")
        return enriched_data
    
    async def get_core_beliefs(self) -> Dict[str, Any]:
        """
        Get core beliefs using the parse_core_beliefs function.
        
        Returns:
            Dictionary containing parsed core beliefs
        """
        logger.info(f"Getting core beliefs")
        
        # Use the parse_core_beliefs function from core_beliefs_integration.py
        beliefs = parse_core_beliefs()
        
        # Enhanced: Add semantic version information to each belief
        for belief_id, belief_data in beliefs.items():
            version_info = await self.belief_version_manager.get_current_version(belief_id)
            if version_info:
                # Extract semantic version if available
                semantic_version = version_info.get("semantic_version")
                if semantic_version:
                    belief_data["semantic_version"] = semantic_version
                    belief_data["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
        
        logger.info(f"Retrieved core beliefs")
        return beliefs
    
    async def configure_orchestrator_mode(self, mode: str, loop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure orchestrator mode using the tiered_orchestrator functions.
        
        Args:
            mode: The orchestrator mode (FAST, BALANCED, THOROUGH, RESEARCH)
            loop_data: The loop data to enrich with mode information
            
        Returns:
            Enriched loop data with mode configuration
        """
        logger.info(f"Configuring orchestrator mode: {mode}")
        
        # Use the enrich_loop_with_mode_info function from tiered_orchestrator.py
        enriched_data = enrich_loop_with_mode_info(loop_data, mode.lower())
        
        # Enhanced: Add risk assessment based on mode
        risk_levels = {
            "fast": "low",
            "balanced": "medium",
            "thorough": "high",
            "research": "very_high"
        }
        
        if mode.lower() in risk_levels:
            if "metadata" not in enriched_data:
                enriched_data["metadata"] = {}
            
            enriched_data["metadata"]["risk_level"] = risk_levels[mode.lower()]
            enriched_data["metadata"]["schema_patch_ui"] = SCHEMA_PATCH_VERSION["ui"]
        
        logger.info(f"Orchestrator mode configuration completed")
        return enriched_data
    
    async def determine_optimal_mode(self, task_description: str, 
                                   complexity: Optional[float] = None,
                                   sensitivity: Optional[float] = None,
                                   time_constraint: Optional[float] = None,
                                   user_preference: Optional[str] = None) -> str:
        """
        Determine the optimal orchestrator mode using the determine_optimal_mode function.
        
        Args:
            task_description: Description of the task
            complexity: Optional complexity score (0.0-1.0)
            sensitivity: Optional sensitivity score (0.0-1.0)
            time_constraint: Optional time constraint score (0.0-1.0, lower means stricter constraints)
            user_preference: Optional user preference for mode
            
        Returns:
            Recommended orchestrator mode
        """
        logger.info(f"Determining optimal orchestrator mode")
        
        # Use the determine_optimal_mode function from tiered_orchestrator.py
        mode = determine_optimal_mode(
            task_description=task_description,
            complexity=complexity,
            sensitivity=sensitivity,
            time_constraint=time_constraint,
            user_preference=user_preference
        )
        
        logger.info(f"Determined optimal mode: {mode}")
        return mode
    
    async def post_loop_execution(self, loop_id: str, loop_data: Dict[str, Any],
                                summary_text: Optional[str] = None,
                                project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform post-loop execution tasks.
        
        Args:
            loop_id: The ID of the loop
            loop_data: The loop execution data
            summary_text: Optional summary text
            project_id: Optional project ID
            
        Returns:
            Dictionary with post-execution results
        """
        logger.info(f"Performing post-loop execution tasks for loop {loop_id}")
        
        # Initialize agent dispatcher for this loop if not already initialized
        if self.agent_dispatcher is None or self.agent_dispatcher.loop_id != loop_id:
            self.agent_dispatcher = self._get_agent_dispatcher(loop_id)
        
        results = {}
        
        # Stop metrics tracking
        metrics_result = await self.metrics_tracker.stop_tracking(loop_id)
        
        # Ensure metrics_result has error_count field
        if isinstance(metrics_result, dict) and "error_count" not in metrics_result:
            metrics_result["error_count"] = 0
            
        # Enhanced: Add performance analysis to metrics
        if isinstance(metrics_result, dict):
            # Add schema patch tag
            metrics_result["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
            
            # Add temporal pattern analysis
            if "agent_execution_times_ms" in metrics_result:
                agent_times = metrics_result["agent_execution_times_ms"]
                if isinstance(agent_times, dict) and len(agent_times) > 1:
                    # Calculate sequence efficiency (how well the sequence flows)
                    agent_keys = list(agent_times.keys())
                    time_diffs = []
                    for i in range(1, len(agent_keys)):
                        prev_time = agent_times[agent_keys[i-1]]
                        curr_time = agent_times[agent_keys[i]]
                        time_diffs.append(abs(curr_time - prev_time))
                    
                    if time_diffs:
                        avg_diff = sum(time_diffs) / len(time_diffs)
                        max_diff = max(time_diffs)
                        metrics_result["sequence_efficiency"] = {
                            "average_transition_time_ms": round(avg_diff, 2),
                            "max_transition_time_ms": max_diff,
                            "efficiency_score": round(1.0 - (avg_diff / (max(agent_times.values()) or 1)), 2)
                        }
            
            # Add resource utilization metrics
            if "peak_memory_usage_bytes" in metrics_result and "total_execution_time_ms" in metrics_result:
                memory_mb = metrics_result["peak_memory_usage_bytes"] / (1024 * 1024)
                time_sec = metrics_result["total_execution_time_ms"] / 1000
                
                if time_sec > 0:
                    metrics_result["resource_efficiency"] = {
                        "memory_time_ratio": round(memory_mb / time_sec, 2),
                        "operations_per_second": round(
                            (metrics_result.get("memory_operations_count", 0) or 0) / time_sec, 2
                        ),
                        "memory_per_operation": round(
                            memory_mb / (metrics_result.get("memory_operations_count", 1) or 1), 2
                        )
                    }
            
            # Add belief reference analysis
            if "belief_reference_count" in metrics_result:
                metrics_result["belief_reference_analysis"] = {
                    "reference_density": round(
                        metrics_result["belief_reference_count"] / 
                        (metrics_result.get("agent_count", 1) or 1), 2
                    ),
                    "reference_efficiency": round(
                        metrics_result["belief_reference_count"] / 
                        (metrics_result.get("total_execution_time_ms", 1000) / 1000), 2
                    )
                }
        
        results["metrics"] = metrics_result
        
        # Create final snapshot
        # Enhanced: Use more detailed snapshot metadata
        snapshot_metadata = {
            "stage": "post_execution",
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_summary": {
                "execution_time_ms": metrics_result.get("total_execution_time_ms", 0),
                "memory_operations": metrics_result.get("memory_operations_count", 0),
                "agent_count": metrics_result.get("agent_count", 0),
                "error_count": metrics_result.get("error_count", 0)
            },
            "schema_patch_core": SCHEMA_PATCH_VERSION["core"]
        }
        
        snapshot_result = await self.snapshot_optimizer.create_snapshot(
            loop_id=loop_id,
            snapshot_type="full",
            metadata=snapshot_metadata
        )
        results["final_snapshot"] = snapshot_result
        
        # Optimize snapshots
        optimize_result = await self.snapshot_optimizer.optimize_snapshots(loop_id)
        results["snapshot_optimization"] = optimize_result
        
        # Run auditor agent with enhanced capabilities
        # Enhanced: Use advanced auditing features
        audit_result = await self.auditor_agent.audit_loop(
            loop_id=loop_id,
            loop_data=loop_data,
            run_advanced_analysis=True,  # Enable advanced analysis
            correlation_analysis=True,   # Enable correlation analysis
            risk_assessment=True         # Enable risk assessment
        )
        
        # Add schema patch tag to audit result
        if isinstance(audit_result, dict):
            audit_result["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
        
        results["audit"] = audit_result
        
        # Track belief versions with semantic versioning
        beliefs_referenced = loop_data.get("beliefs_referenced", [])
        belief_versions = []
        
        for belief_id in beliefs_referenced:
            # Enhanced: Get version with semantic versioning
            version_info = await self.belief_version_manager.get_current_version(belief_id)
            if version_info:
                # Add schema patch tag
                version_info["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
                belief_versions.append(version_info)
        
        results["belief_versions"] = belief_versions
        
        # Score summary if provided with multi-dimensional scoring
        if summary_text:
            # Enhanced: Use multi-dimensional scoring
            summary_score = await self.summary_realism_scorer.score_summary(
                loop_id=loop_id,
                summary=summary_text,
                reference_materials=loop_data
            )
            
            # Handle to_dict method if available
            if hasattr(summary_score, 'to_dict'):
                results["summary_score"] = summary_score.to_dict()
            else:
                results["summary_score"] = summary_score
        
        # Release project lock if project_id is provided
        if project_id:
            release_result = await self.lock_manager.release_lock(
                project_id=project_id,
                owner=f"loop:{loop_id}"
            )
            results["lock_release"] = release_result
        
        # Create a proper LoopSummary object instead of using raw text
        loop_summary = None
        if summary_text:
            # Enhanced: Create summary with multi-dimensional scores
            loop_summary = LoopSummary(
                text=summary_text,
                timestamp=datetime.utcnow().isoformat(),
                agent_id="system",
                confidence=0.9,
                metadata={"schema_patch_core": SCHEMA_PATCH_VERSION["core"]}
            )
            
            # Add scores if available
            if "summary_score" in results:
                score_data = results["summary_score"]
                if isinstance(score_data, dict):
                    # Add overall realism score
                    loop_summary.realism_score = score_data.get("overall_score")
                    
                    # Add multi-dimensional scores
                    loop_summary.factual_consistency_score = score_data.get("factual_accuracy")
                    loop_summary.hallucination_score = 1.0 - (score_data.get("factual_accuracy") or 0.5)
                    loop_summary.belief_alignment_score = score_data.get("logical_consistency")
                    loop_summary.detail_level_score = score_data.get("temporal_coherence")
                    
                    # Add confidence score
                    loop_summary.confidence = score_data.get("confidence", 0.9)
                    
                    # Add summary ID
                    loop_summary.summary_id = score_data.get("summary_id", f"summary_{loop_id}")
                    
                    # Add additional metadata
                    loop_summary.metadata.update({
                        "emotional_congruence": score_data.get("emotional_congruence"),
                        "confidence_explanation": score_data.get("confidence_explanation", []),
                        "adaptive_thresholds": score_data.get("adaptive_thresholds", {}),
                        "levels": score_data.get("levels", {})
                    })
        
        # Update loop trace
        loop_trace_update = LoopTraceUpdate(
            end_time=datetime.utcnow().isoformat(),
            status="completed",
            metrics=metrics_result,
            summary=loop_summary,
            audit_info=audit_result,
            belief_versions=belief_versions,
            snapshots=[snapshot_result] if isinstance(snapshot_result, dict) else [],
            metadata={"schema_patch_core": SCHEMA_PATCH_VERSION["core"]}
        )
        
        # Use model_dump instead of dict for Pydantic v2 compatibility
        try:
            results["loop_trace_update"] = loop_trace_update.model_dump()
        except AttributeError:
            # Fallback for older Pydantic versions
            results["loop_trace_update"] = loop_trace_update.dict()
        
        logger.info(f"Post-loop execution tasks completed for loop {loop_id}")
        return results
    
    async def handle_loop_error(self, loop_id: str, error: str,
                              project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle loop execution error.
        
        Args:
            loop_id: The ID of the loop
            error: The error message
            project_id: Optional project ID
            
        Returns:
            Dictionary with error handling results
        """
        logger.error(f"Handling error for loop {loop_id}: {error}")
        
        # Initialize agent dispatcher for this loop if not already initialized
        if self.agent_dispatcher is None or self.agent_dispatcher.loop_id != loop_id:
            self.agent_dispatcher = self._get_agent_dispatcher(loop_id)
        
        results = {}
        
        # Stop metrics tracking
        metrics_result = await self.metrics_tracker.stop_tracking(loop_id)
        
        # Ensure metrics_result has error_count field
        if isinstance(metrics_result, dict) and "error_count" not in metrics_result:
            metrics_result["error_count"] = 1
        
        # Enhanced: Add error analysis
        if isinstance(metrics_result, dict):
            metrics_result["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
            metrics_result["error_analysis"] = {
                "error_type": "runtime_error",  # Default type
                "error_message": error,
                "timestamp": datetime.utcnow().isoformat(),
                "recovery_attempted": False
            }
            
            # Analyze error message to categorize it
            if "timeout" in error.lower() or "deadline" in error.lower():
                metrics_result["error_analysis"]["error_type"] = "timeout"
            elif "memory" in error.lower() or "allocation" in error.lower():
                metrics_result["error_analysis"]["error_type"] = "memory_error"
            elif "permission" in error.lower() or "access" in error.lower():
                metrics_result["error_analysis"]["error_type"] = "permission_error"
            elif "not found" in error.lower() or "missing" in error.lower():
                metrics_result["error_analysis"]["error_type"] = "not_found_error"
            
        results["metrics"] = metrics_result
        
        # Create error snapshot
        # Enhanced: Add more detailed error metadata
        error_metadata = {
            "stage": "error",
            "error": error,
            "error_type": metrics_result.get("error_analysis", {}).get("error_type", "runtime_error"),
            "timestamp": datetime.utcnow().isoformat(),
            "recoverable": False,  # Default to non-recoverable
            "schema_patch_core": SCHEMA_PATCH_VERSION["core"]
        }
        
        snapshot_result = await self.snapshot_optimizer.create_snapshot(
            loop_id=loop_id,
            snapshot_type="error",
            metadata=error_metadata
        )
        results["error_snapshot"] = snapshot_result
        
        # Release project lock if project_id is provided
        if project_id:
            release_result = await self.lock_manager.release_lock(
                project_id=project_id,
                owner=f"loop:{loop_id}"
            )
            results["lock_release"] = release_result
        
        # Update loop trace
        loop_trace_update = LoopTraceUpdate(
            end_time=datetime.utcnow().isoformat(),
            status="error",
            error=error,
            metadata={
                "error_analysis": metrics_result.get("error_analysis", {}),
                "schema_patch_core": SCHEMA_PATCH_VERSION["core"]
            }
        )
        
        # Use model_dump instead of dict for Pydantic v2 compatibility
        try:
            results["loop_trace_update"] = loop_trace_update.model_dump()
        except AttributeError:
            # Fallback for older Pydantic versions
            results["loop_trace_update"] = loop_trace_update.dict()
        
        logger.info(f"Error handling completed for loop {loop_id}")
        return results
    
    async def get_loop_metrics(self, loop_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a loop.
        
        Args:
            loop_id: The ID of the loop
            
        Returns:
            Dictionary with metrics if found, None otherwise
        """
        logger.info(f"Getting metrics for loop {loop_id}")
        
        # Initialize agent dispatcher for this loop if needed
        if self.agent_dispatcher is None or self.agent_dispatcher.loop_id != loop_id:
            self.agent_dispatcher = self._get_agent_dispatcher(loop_id)
        
        metrics = await self.metrics_tracker.get_metrics(loop_id)
        
        # Enhanced: Add performance analysis if metrics exist
        if metrics:
            # Add schema patch tag
            metrics["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
            
            # Add performance trend analysis if historical data is available
            historical_metrics = await self.metrics_tracker.get_historical_metrics(loop_id)
            if historical_metrics and len(historical_metrics) > 1:
                # Calculate trends
                execution_times = [m.get("total_execution_time_ms", 0) for m in historical_metrics]
                memory_usages = [m.get("peak_memory_usage_bytes", 0) for m in historical_metrics]
                
                # Calculate trend directions
                time_trend = "stable"
                if len(execution_times) >= 3:
                    if all(execution_times[i] < execution_times[i-1] for i in range(1, len(execution_times))):
                        time_trend = "improving"
                    elif all(execution_times[i] > execution_times[i-1] for i in range(1, len(execution_times))):
                        time_trend = "degrading"
                
                memory_trend = "stable"
                if len(memory_usages) >= 3:
                    if all(memory_usages[i] < memory_usages[i-1] for i in range(1, len(memory_usages))):
                        memory_trend = "improving"
                    elif all(memory_usages[i] > memory_usages[i-1] for i in range(1, len(memory_usages))):
                        memory_trend = "degrading"
                
                # Add trend analysis to metrics
                metrics["performance_trends"] = {
                    "execution_time_trend": time_trend,
                    "memory_usage_trend": memory_trend,
                    "historical_data_points": len(historical_metrics),
                    "trend_confidence": min(1.0, len(historical_metrics) / 10)
                }
        
        logger.info(f"Retrieved metrics for loop {loop_id}")
        return metrics
    
    async def get_project_locks(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get locks for a project.
        
        Args:
            project_id: The ID of the project
            
        Returns:
            List of dictionaries with lock information
        """
        logger.info(f"Getting locks for project {project_id}")
        
        locks = await self.lock_manager.get_locks(project_id)
        
        # Enhanced: Add semantic lock information
        for lock in locks:
            if isinstance(lock, dict):
                # Add schema patch tag
                lock["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
                
                # Add semantic lock information
                if "lock_type" in lock:
                    lock["semantic_lock_info"] = {
                        "is_exclusive": lock["lock_type"] == "exclusive",
                        "allows_shared": lock["lock_type"] != "exclusive",
                        "is_expired": datetime.fromisoformat(lock.get("expiration_time", "2000-01-01T00:00:00")) < datetime.utcnow() if "expiration_time" in lock else False
                    }
        
        logger.info(f"Retrieved locks for project {project_id}")
        return locks
    
    async def get_loop_snapshots(self, loop_id: str) -> List[Dict[str, Any]]:
        """
        Get snapshots for a loop.
        
        Args:
            loop_id: The ID of the loop
            
        Returns:
            List of dictionaries with snapshot information
        """
        logger.info(f"Getting snapshots for loop {loop_id}")
        
        # Initialize agent dispatcher for this loop if needed
        if self.agent_dispatcher is None or self.agent_dispatcher.loop_id != loop_id:
            self.agent_dispatcher = self._get_agent_dispatcher(loop_id)
        
        snapshots = await self.snapshot_optimizer.get_snapshots(loop_id)
        
        # Enhanced: Add snapshot analysis
        if snapshots:
            # Calculate snapshot statistics
            snapshot_sizes = [s.get("compressed_size_bytes", 0) for s in snapshots if isinstance(s, dict)]
            snapshot_types = [s.get("snapshot_type", "") for s in snapshots if isinstance(s, dict)]
            
            # Add analysis to each snapshot
            for snapshot in snapshots:
                if isinstance(snapshot, dict):
                    # Add schema patch tag
                    snapshot["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
                    
                    # Add snapshot analysis
                    if snapshot_sizes:
                        avg_size = sum(snapshot_sizes) / len(snapshot_sizes)
                        snapshot["size_analysis"] = {
                            "relative_size": round(snapshot.get("compressed_size_bytes", 0) / avg_size, 2),
                            "is_outlier": abs(snapshot.get("compressed_size_bytes", 0) - avg_size) > (2 * statistics.stdev(snapshot_sizes) if len(snapshot_sizes) > 1 else 0)
                        }
                    
                    # Add type distribution
                    if snapshot_types:
                        type_counts = {t: snapshot_types.count(t) for t in set(snapshot_types)}
                        snapshot["type_distribution"] = {
                            "count_by_type": type_counts,
                            "percentage_of_type": round(type_counts.get(snapshot.get("snapshot_type", ""), 0) / len(snapshot_types) * 100, 1)
                        }
        
        logger.info(f"Retrieved snapshots for loop {loop_id}")
        return snapshots
    
    async def get_loop_audit(self, loop_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audit for a loop.
        
        Args:
            loop_id: The ID of the loop
            
        Returns:
            Dictionary with audit information if found, None otherwise
        """
        logger.info(f"Getting audit for loop {loop_id}")
        
        # Initialize agent dispatcher for this loop if needed
        if self.agent_dispatcher is None or self.agent_dispatcher.loop_id != loop_id:
            self.agent_dispatcher = self._get_agent_dispatcher(loop_id)
        
        # Enhanced: Use get_audit_result with advanced options
        audit = await self.auditor_agent.get_audit_result(
            loop_id=loop_id,
            include_details=True,
            include_recommendations=True,
            include_risk_assessment=True
        )
        
        # Add schema patch tag if audit exists
        if audit:
            audit["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
        
        logger.info(f"Retrieved audit for loop {loop_id}")
        return audit
    
    async def get_belief_version_history(self, belief_id: str) -> List[Dict[str, Any]]:
        """
        Get version history for a belief.
        
        Args:
            belief_id: The ID of the belief
            
        Returns:
            List of dictionaries with version information
        """
        logger.info(f"Getting version history for belief {belief_id}")
        
        # Enhanced: Get version history with semantic versioning
        versions = await self.belief_version_manager.get_version_history(
            belief_id=belief_id,
            include_semantic_versions=True,
            include_change_impact=True
        )
        
        # Add schema patch tag to each version
        for version in versions:
            if isinstance(version, dict):
                version["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
        
        logger.info(f"Retrieved version history for belief {belief_id}")
        return versions
    
    async def compare_belief_versions(self, belief_id: str, version1: Union[int, str], 
                                    version2: Union[int, str]) -> Dict[str, Any]:
        """
        Compare two versions of a belief.
        
        Args:
            belief_id: The ID of the belief
            version1: First version number or semantic version string
            version2: Second version number or semantic version string
            
        Returns:
            Dictionary with comparison information
        """
        logger.info(f"Comparing belief versions {version1} and {version2} for belief {belief_id}")
        
        # Enhanced: Use compare_versions with semantic versioning support
        comparison = await self.belief_version_manager.compare_versions(
            belief_id=belief_id,
            version1=version1,
            version2=version2,
            include_semantic_analysis=True
        )
        
        # Add schema patch tag
        if comparison:
            comparison["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
        
        logger.info(f"Compared belief versions for belief {belief_id}")
        return comparison
    
    async def score_summary_realism(self, loop_id: str, summary_text: str,
                                  reference_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Score the realism of a summary.
        
        Args:
            loop_id: The ID of the loop
            summary_text: The summary text to score
            reference_data: Optional reference data for validation
            
        Returns:
            Dictionary with scoring information
        """
        logger.info(f"Scoring summary realism for loop {loop_id}")
        
        # Enhanced: Use score_summary with multi-dimensional scoring
        score = await self.summary_realism_scorer.score_summary(
            loop_id=loop_id,
            summary=summary_text,
            reference_materials=reference_data
        )
        
        # Add schema patch tag
        if score:
            score["schema_patch_core"] = SCHEMA_PATCH_VERSION["core"]
        
        logger.info(f"Scored summary realism for loop {loop_id}")
        return score
    
    async def generate_debug_info(self, loop_id: str) -> Dict[str, Any]:
        """
        Generate debug information for a loop.
        
        Args:
            loop_id: The ID of the loop
            
        Returns:
            Dictionary with debug information
        """
        logger.info(f"Generating debug information for loop {loop_id}")
        
        # Initialize agent dispatcher for this loop if needed
        if self.agent_dispatcher is None or self.agent_dispatcher.loop_id != loop_id:
            self.agent_dispatcher = self._get_agent_dispatcher(loop_id)
        
        # Gather all available information
        metrics = await self.metrics_tracker.get_metrics(loop_id)
        snapshots = await self.snapshot_optimizer.get_snapshots(loop_id)
        audit = await self.auditor_agent.get_audit_result(loop_id)
        
        # Create debug info structure
        debug_info = {
            "loop_id": loop_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "snapshots": snapshots,
            "audit": audit,
            "schema_patch_core": SCHEMA_PATCH_VERSION["core"],
            "schema_patch_ui": SCHEMA_PATCH_VERSION["ui"]
        }
        
        # Enhanced: Add performance analysis
        if metrics:
            debug_info["performance_analysis"] = {
                "execution_time_ms": metrics.get("total_execution_time_ms", 0),
                "peak_memory_mb": round(metrics.get("peak_memory_usage_bytes", 0) / (1024 * 1024), 2),
                "memory_operations": metrics.get("memory_operations_count", 0),
                "agent_count": metrics.get("agent_count", 0),
                "error_count": metrics.get("error_count", 0),
                "efficiency_score": round(
                    metrics.get("memory_operations_count", 0) / 
                    (metrics.get("total_execution_time_ms", 1000) / 1000), 2
                ) if metrics.get("total_execution_time_ms", 0) > 0 else 0
            }
        
        # Enhanced: Add snapshot analysis
        if snapshots:
            snapshot_types = [s.get("snapshot_type", "") for s in snapshots if isinstance(s, dict)]
            type_counts = {t: snapshot_types.count(t) for t in set(snapshot_types)}
            
            debug_info["snapshot_analysis"] = {
                "count": len(snapshots),
                "types": type_counts,
                "total_size_mb": round(
                    sum(s.get("compressed_size_bytes", 0) for s in snapshots if isinstance(s, dict)) / 
                    (1024 * 1024), 2
                ),
                "average_compression_ratio": round(
                    sum(s.get("compression_ratio", 0) for s in snapshots if isinstance(s, dict)) / 
                    len(snapshots), 2
                ) if snapshots else 0
            }
        
        # Enhanced: Add audit summary
        if audit:
            debug_info["audit_summary"] = {
                "overall_score": audit.get("overall_score", 0),
                "belief_consistency_score": audit.get("belief_consistency_score", 0),
                "memory_integrity_score": audit.get("memory_integrity_score", 0),
                "issue_count": audit.get("issue_count", 0),
                "warning_count": audit.get("warning_count", 0),
                "recommendation_count": audit.get("recommendation_count", 0)
            }
        
        logger.info(f"Generated debug information for loop {loop_id}")
        return debug_info
    
    async def create_loop_trace_schema_json(self) -> Dict[str, Any]:
        """
        Create a JSON schema for loop trace.
        
        Returns:
            Dictionary with JSON schema
        """
        logger.info("Creating loop trace JSON schema")
        
        # Create JSON schema based on Pydantic models
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Loop Trace Schema",
            "description": "Schema for loop traces in the system",
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Loop ID"
                },
                "parent_id": {
                    "type": ["string", "null"],
                    "description": "Parent loop ID if this is a child loop"
                },
                "start_time": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Start time of the loop"
                },
                "end_time": {
                    "type": ["string", "null"],
                    "format": "date-time",
                    "description": "End time of the loop"
                },
                "status": {
                    "type": "string",
                    "enum": ["running", "completed", "failed", "error"],
                    "description": "Status of the loop"
                },
                "agents": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "Agent ID"
                            },
                            "type": {
                                "type": "string",
                                "enum": ["system", "user", "assistant", "tool", "plugin", "custom"],
                                "description": "Agent type"
                            },
                            "input": {
                                "type": ["object", "null"],
                                "description": "Input to the agent"
                            },
                            "output": {
                                "type": ["object", "null"],
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": "Text output from the agent"
                                    },
                                    "timestamp": {
                                        "type": "string",
                                        "format": "date-time",
                                        "description": "Timestamp of the output"
                                    },
                                    "metadata": {
                                        "type": "object",
                                        "description": "Additional metadata"
                                    }
                                },
                                "required": ["text", "timestamp"],
                                "description": "Output from the agent"
                            },
                            "start_time": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Start time of agent execution"
                            },
                            "end_time": {
                                "type": ["string", "null"],
                                "format": "date-time",
                                "description": "End time of agent execution"
                            },
                            "execution_time_ms": {
                                "type": ["integer", "null"],
                                "description": "Execution time in milliseconds"
                            },
                            "memory_usage_bytes": {
                                "type": ["integer", "null"],
                                "description": "Memory usage in bytes"
                            },
                            "cpu_usage_percent": {
                                "type": ["number", "null"],
                                "description": "CPU usage percentage"
                            },
                            "error": {
                                "type": ["string", "null"],
                                "description": "Error message if agent failed"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata"
                            }
                        },
                        "required": ["id", "type", "start_time"],
                        "description": "Agent trace"
                    },
                    "description": "Traces of agents involved in the loop"
                },
                "memory_operations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "operation_type": {
                                "type": "string",
                                "enum": ["read", "write", "update", "delete"],
                                "description": "Type of memory operation"
                            },
                            "key": {
                                "type": "string",
                                "description": "Memory key"
                            },
                            "value": {
                                "type": ["object", "null"],
                                "description": "Memory value (for write/update operations)"
                            },
                            "timestamp": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Timestamp of the operation"
                            },
                            "agent_id": {
                                "type": "string",
                                "description": "ID of the agent performing the operation"
                            },
                            "success": {
                                "type": "boolean",
                                "description": "Whether the operation was successful"
                            },
                            "error": {
                                "type": ["string", "null"],
                                "description": "Error message if operation failed"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata"
                            }
                        },
                        "required": ["operation_type", "key", "timestamp", "agent_id", "success"],
                        "description": "Memory operation"
                    },
                    "description": "Memory operations performed during the loop"
                },
                "beliefs_referenced": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "IDs of beliefs referenced in the loop"
                },
                "belief_references": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "belief_id": {
                                "type": "string",
                                "description": "ID of the referenced belief"
                            },
                            "timestamp": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Timestamp of the reference"
                            },
                            "agent_id": {
                                "type": "string",
                                "description": "ID of the agent making the reference"
                            },
                            "context": {
                                "type": "string",
                                "description": "Context of the reference"
                            },
                            "confidence": {
                                "type": "number",
                                "description": "Confidence score of the reference"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata"
                            }
                        },
                        "required": ["belief_id", "timestamp", "agent_id", "context", "confidence"],
                        "description": "Belief reference"
                    },
                    "description": "Detailed belief references"
                },
                "summary": {
                    "type": ["object", "null"],
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Summary text"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Timestamp of the summary"
                        },
                        "agent_id": {
                            "type": "string",
                            "description": "ID of the agent generating the summary"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence score of the summary"
                        },
                        "realism_score": {
                            "type": ["number", "null"],
                            "description": "Realism score of the summary"
                        },
                        "hallucination_score": {
                            "type": ["number", "null"],
                            "description": "Hallucination score of the summary"
                        },
                        "factual_consistency_score": {
                            "type": ["number", "null"],
                            "description": "Factual consistency score of the summary"
                        },
                        "belief_alignment_score": {
                            "type": ["number", "null"],
                            "description": "Belief alignment score of the summary"
                        },
                        "detail_level_score": {
                            "type": ["number", "null"],
                            "description": "Detail level score of the summary"
                        },
                        "summary_id": {
                            "type": ["string", "null"],
                            "description": "ID of the summary for reference"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata"
                        }
                    },
                    "required": ["text", "timestamp", "agent_id", "confidence"],
                    "description": "Summary of the loop"
                },
                "metrics": {
                    "type": ["object", "null"],
                    "properties": {
                        "total_execution_time_ms": {
                            "type": "integer",
                            "description": "Total execution time in milliseconds"
                        },
                        "agent_execution_times_ms": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "integer"
                            },
                            "description": "Execution time per agent in milliseconds"
                        },
                        "memory_operations_count": {
                            "type": "integer",
                            "description": "Number of memory operations"
                        },
                        "memory_read_count": {
                            "type": "integer",
                            "description": "Number of memory read operations"
                        },
                        "memory_write_count": {
                            "type": "integer",
                            "description": "Number of memory write operations"
                        },
                        "peak_memory_usage_bytes": {
                            "type": "integer",
                            "description": "Peak memory usage in bytes"
                        },
                        "belief_reference_count": {
                            "type": "integer",
                            "description": "Number of belief references"
                        },
                        "agent_count": {
                            "type": "integer",
                            "description": "Number of agents involved"
                        },
                        "error_count": {
                            "type": "integer",
                            "description": "Number of errors encountered"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata"
                        },
                        "sequence_efficiency": {
                            "type": "object",
                            "properties": {
                                "average_transition_time_ms": {
                                    "type": "number",
                                    "description": "Average transition time between agents in milliseconds"
                                },
                                "max_transition_time_ms": {
                                    "type": "number",
                                    "description": "Maximum transition time between agents in milliseconds"
                                },
                                "efficiency_score": {
                                    "type": "number",
                                    "description": "Efficiency score for agent transitions"
                                }
                            },
                            "description": "Sequence efficiency metrics"
                        },
                        "resource_efficiency": {
                            "type": "object",
                            "properties": {
                                "memory_time_ratio": {
                                    "type": "number",
                                    "description": "Memory usage (MB) to execution time (s) ratio"
                                },
                                "operations_per_second": {
                                    "type": "number",
                                    "description": "Memory operations per second"
                                },
                                "memory_per_operation": {
                                    "type": "number",
                                    "description": "Memory usage (MB) per operation"
                                }
                            },
                            "description": "Resource efficiency metrics"
                        },
                        "belief_reference_analysis": {
                            "type": "object",
                            "properties": {
                                "reference_density": {
                                    "type": "number",
                                    "description": "Belief references per agent"
                                },
                                "reference_efficiency": {
                                    "type": "number",
                                    "description": "Belief references per second"
                                }
                            },
                            "description": "Belief reference analysis"
                        },
                        "schema_patch_core": {
                            "type": "string",
                            "description": "Schema patch version for core fields"
                        }
                    },
                    "required": ["total_execution_time_ms", "memory_operations_count", "memory_read_count", "memory_write_count", "peak_memory_usage_bytes", "belief_reference_count", "agent_count", "error_count"],
                    "description": "Metrics for the loop"
                },
                "belief_volatility": {
                    "type": ["number", "null"],
                    "description": "Volatility score for belief usage"
                },
                "contradiction_score": {
                    "type": ["number", "null"],
                    "description": "Score for contradictions with other loops"
                },
                "skeptic_triggered": {
                    "type": ["boolean", "null"],
                    "description": "Whether the SKEPTIC agent was triggered"
                },
                "skeptic_result": {
                    "type": ["object", "null"],
                    "description": "Result from the SKEPTIC agent"
                },
                "snapshots": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "snapshot_id": {
                                "type": "string",
                                "description": "ID of the snapshot"
                            },
                            "timestamp": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Timestamp of the snapshot"
                            },
                            "snapshot_type": {
                                "type": "string",
                                "description": "Type of snapshot (full, differential, incremental, error)"
                            },
                            "original_size_bytes": {
                                "type": "integer",
                                "description": "Original size in bytes"
                            },
                            "compressed_size_bytes": {
                                "type": "integer",
                                "description": "Compressed size in bytes"
                            },
                            "compression_ratio": {
                                "type": "number",
                                "description": "Compression ratio"
                            },
                            "retention_policy": {
                                "type": "string",
                                "description": "Retention policy for the snapshot"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata"
                            },
                            "schema_patch_core": {
                                "type": "string",
                                "description": "Schema patch version for core fields"
                            },
                            "size_analysis": {
                                "type": "object",
                                "properties": {
                                    "relative_size": {
                                        "type": "number",
                                        "description": "Size relative to average snapshot size"
                                    },
                                    "is_outlier": {
                                        "type": "boolean",
                                        "description": "Whether this snapshot is a size outlier"
                                    }
                                },
                                "description": "Size analysis for the snapshot"
                            },
                            "type_distribution": {
                                "type": "object",
                                "properties": {
                                    "count_by_type": {
                                        "type": "object",
                                        "additionalProperties": {
                                            "type": "integer"
                                        },
                                        "description": "Count of snapshots by type"
                                    },
                                    "percentage_of_type": {
                                        "type": "number",
                                        "description": "Percentage of snapshots of this type"
                                    }
                                },
                                "description": "Type distribution analysis"
                            }
                        },
                        "required": ["snapshot_id", "timestamp", "snapshot_type", "original_size_bytes", "compressed_size_bytes", "compression_ratio", "retention_policy"],
                        "description": "Snapshot information"
                    },
                    "description": "Snapshots taken during the loop"
                },
                "audit_info": {
                    "type": ["object", "null"],
                    "properties": {
                        "audit_id": {
                            "type": "string",
                            "description": "ID of the audit"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Timestamp of the audit"
                        },
                        "overall_score": {
                            "type": "number",
                            "description": "Overall audit score"
                        },
                        "belief_consistency_score": {
                            "type": "number",
                            "description": "Belief consistency score"
                        },
                        "memory_integrity_score": {
                            "type": "number",
                            "description": "Memory integrity score"
                        },
                        "issue_count": {
                            "type": "integer",
                            "description": "Number of issues found"
                        },
                        "warning_count": {
                            "type": "integer",
                            "description": "Number of warnings found"
                        },
                        "recommendation_count": {
                            "type": "integer",
                            "description": "Number of recommendations provided"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata"
                        },
                        "schema_patch_core": {
                            "type": "string",
                            "description": "Schema patch version for core fields"
                        },
                        "risk_assessment": {
                            "type": "object",
                            "properties": {
                                "risk_level": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high", "critical"],
                                    "description": "Overall risk level"
                                },
                                "impact": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high", "critical"],
                                    "description": "Potential impact of issues"
                                },
                                "likelihood": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high", "critical"],
                                    "description": "Likelihood of issues occurring"
                                },
                                "priority_issues": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    },
                                    "description": "List of priority issues to address"
                                }
                            },
                            "description": "Risk assessment information"
                        },
                        "correlation_analysis": {
                            "type": "object",
                            "properties": {
                                "correlated_issues": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "issue_pair": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string"
                                                },
                                                "minItems": 2,
                                                "maxItems": 2,
                                                "description": "Pair of correlated issues"
                                            },
                                            "correlation_strength": {
                                                "type": "number",
                                                "description": "Strength of correlation between issues"
                                            },
                                            "systemic": {
                                                "type": "boolean",
                                                "description": "Whether this is a systemic problem"
                                            }
                                        },
                                        "description": "Correlated issue information"
                                    },
                                    "description": "List of correlated issues"
                                },
                                "root_causes": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "cause": {
                                                "type": "string",
                                                "description": "Root cause description"
                                            },
                                            "affected_issues": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string"
                                                },
                                                "description": "Issues affected by this root cause"
                                            },
                                            "confidence": {
                                                "type": "number",
                                                "description": "Confidence in this root cause"
                                            }
                                        },
                                        "description": "Root cause information"
                                    },
                                    "description": "List of identified root causes"
                                }
                            },
                            "description": "Correlation analysis information"
                        }
                    },
                    "required": ["audit_id", "timestamp", "overall_score", "belief_consistency_score", "memory_integrity_score", "issue_count", "warning_count", "recommendation_count"],
                    "description": "Audit information for the loop"
                },
                "belief_versions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "belief_id": {
                                "type": "string",
                                "description": "ID of the belief"
                            },
                            "version": {
                                "type": "integer",
                                "description": "Version number"
                            },
                            "semantic_version": {
                                "type": "object",
                                "properties": {
                                    "major": {
                                        "type": "integer",
                                        "description": "Major version number"
                                    },
                                    "minor": {
                                        "type": "integer",
                                        "description": "Minor version number"
                                    },
                                    "patch": {
                                        "type": "integer",
                                        "description": "Patch version number"
                                    }
                                },
                                "required": ["major", "minor", "patch"],
                                "description": "Semantic version information"
                            },
                            "author": {
                                "type": "string",
                                "description": "Author of the version"
                            },
                            "timestamp": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Timestamp of the version"
                            },
                            "change_id": {
                                "type": ["string", "null"],
                                "description": "ID of the change that created this version"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata"
                            },
                            "schema_patch_core": {
                                "type": "string",
                                "description": "Schema patch version for core fields"
                            },
                            "change_type": {
                                "type": "string",
                                "enum": ["creation", "major", "minor", "patch"],
                                "description": "Type of change for this version"
                            },
                            "change_summary": {
                                "type": "string",
                                "description": "Summary of changes in this version"
                            },
                            "branch": {
                                "type": "string",
                                "description": "Branch name for this version"
                            }
                        },
                        "required": ["belief_id", "version", "author", "timestamp"],
                        "description": "Belief version information"
                    },
                    "description": "Belief versions referenced in the loop"
                },
                "project_locks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "lock_id": {
                                "type": "string",
                                "description": "ID of the lock"
                            },
                            "project_id": {
                                "type": "string",
                                "description": "ID of the project"
                            },
                            "owner": {
                                "type": "string",
                                "description": "Owner of the lock"
                            },
                            "acquired_time": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Time the lock was acquired"
                            },
                            "expiration_time": {
                                "type": ["string", "null"],
                                "format": "date-time",
                                "description": "Time the lock expires"
                            },
                            "lock_type": {
                                "type": "string",
                                "enum": ["exclusive", "shared"],
                                "description": "Type of lock (exclusive, shared)"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Additional metadata"
                            },
                            "schema_patch_core": {
                                "type": "string",
                                "description": "Schema patch version for core fields"
                            },
                            "semantic_lock_info": {
                                "type": "object",
                                "properties": {
                                    "is_exclusive": {
                                        "type": "boolean",
                                        "description": "Whether this is an exclusive lock"
                                    },
                                    "allows_shared": {
                                        "type": "boolean",
                                        "description": "Whether this lock allows shared locks"
                                    },
                                    "is_expired": {
                                        "type": "boolean",
                                        "description": "Whether this lock is expired"
                                    }
                                },
                                "description": "Semantic lock information"
                            }
                        },
                        "required": ["lock_id", "project_id", "owner", "acquired_time", "lock_type"],
                        "description": "Project lock information"
                    },
                    "description": "Project locks acquired during the loop"
                },
                "depth": {
                    "type": ["integer", "null"],
                    "description": "Depth of the loop in the execution tree"
                },
                "orchestrator_mode": {
                    "type": ["string", "null"],
                    "enum": ["FAST", "BALANCED", "THOROUGH", "RESEARCH"],
                    "description": "Mode of the orchestrator"
                },
                "error": {
                    "type": ["string", "null"],
                    "description": "Error message if loop failed"
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "schema_patch_core": {
                            "type": "string",
                            "description": "Schema patch version for core fields"
                        },
                        "schema_patch_ui": {
                            "type": "string",
                            "description": "Schema patch version for UI fields"
                        },
                        "risk_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "very_high"],
                            "description": "Risk level based on orchestrator mode"
                        },
                        "error_analysis": {
                            "type": "object",
                            "properties": {
                                "error_type": {
                                    "type": "string",
                                    "description": "Type of error"
                                },
                                "error_message": {
                                    "type": "string",
                                    "description": "Error message"
                                },
                                "timestamp": {
                                    "type": "string",
                                    "format": "date-time",
                                    "description": "Timestamp of the error"
                                },
                                "recovery_attempted": {
                                    "type": "boolean",
                                    "description": "Whether recovery was attempted"
                                }
                            },
                            "description": "Error analysis information"
                        }
                    },
                    "description": "Additional metadata"
                }
            },
            "required": ["id", "start_time", "status"],
            "additionalProperties": true
        }
        
        logger.info("Created loop trace JSON schema")
        return schema

# Global loop hardening integration instance
_loop_hardening_integration = None

def get_loop_hardening_integration() -> LoopHardeningIntegration:
    """
    Get the global loop hardening integration instance.
    
    Returns:
        LoopHardeningIntegration instance
    """
    global _loop_hardening_integration
    if _loop_hardening_integration is None:
        _loop_hardening_integration = LoopHardeningIntegration()
    
    return _loop_hardening_integration

async def pre_loop_execution(loop_id: str, parent_id: Optional[str] = None,
                           project_id: Optional[str] = None,
                           orchestrator_mode: str = "BALANCED",
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform pre-loop execution tasks.
    
    Args:
        loop_id: The ID of the loop
        parent_id: Optional parent loop ID
        project_id: Optional project ID
        orchestrator_mode: Orchestrator mode (FAST, BALANCED, THOROUGH, RESEARCH)
        metadata: Optional metadata
        
    Returns:
        Dictionary with pre-execution results
    """
    integration = get_loop_hardening_integration()
    return await integration.pre_loop_execution(loop_id, parent_id, project_id, orchestrator_mode, metadata)

async def post_loop_execution(loop_id: str, loop_data: Dict[str, Any],
                            summary_text: Optional[str] = None,
                            project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform post-loop execution tasks.
    
    Args:
        loop_id: The ID of the loop
        loop_data: The loop execution data
        summary_text: Optional summary text
        project_id: Optional project ID
        
    Returns:
        Dictionary with post-execution results
    """
    integration = get_loop_hardening_integration()
    return await integration.post_loop_execution(loop_id, loop_data, summary_text, project_id)

async def handle_loop_error(loop_id: str, error: str,
                          project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle loop execution error.
    
    Args:
        loop_id: The ID of the loop
        error: The error message
        project_id: Optional project ID
        
    Returns:
        Dictionary with error handling results
    """
    integration = get_loop_hardening_integration()
    return await integration.handle_loop_error(loop_id, error, project_id)

async def generate_debug_info(loop_id: str) -> Dict[str, Any]:
    """
    Generate debug information for a loop.
    
    Args:
        loop_id: The ID of the loop
        
    Returns:
        Dictionary with debug information
    """
    integration = get_loop_hardening_integration()
    return await integration.generate_debug_info(loop_id)

async def create_loop_trace_schema_json() -> Dict[str, Any]:
    """
    Create a JSON schema for loop trace.
    
    Returns:
        Dictionary with JSON schema
    """
    integration = get_loop_hardening_integration()
    return await integration.create_loop_trace_schema_json()
