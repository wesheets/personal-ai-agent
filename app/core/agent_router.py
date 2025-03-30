"""
Agent Router for the Personal AI Agent System.

This module provides functionality to route tasks to appropriate agents
based on task type, metadata, and agent capabilities.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCapability(BaseModel):
    """Model for an agent capability"""
    capability_name: str
    confidence: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentProfile(BaseModel):
    """Model for an agent profile"""
    agent_type: str
    capabilities: List[AgentCapability] = Field(default_factory=list)
    specialties: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentRouter:
    """
    Router for directing tasks to appropriate agents based on task requirements.
    
    This class handles:
    - Matching task requirements to agent capabilities
    - Routing tasks to the most appropriate agent
    - Tracking agent availability and workload
    """
    
    def __init__(self):
        """Initialize the AgentRouter"""
        # Set up logging directory
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                    "logs", "execution_logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Initialize agent profiles
        self._agent_profiles = self._initialize_agent_profiles()
        
        # Track agent workload
        self._agent_workload = {agent_type: 0 for agent_type in self._agent_profiles.keys()}
    
    def _initialize_agent_profiles(self) -> Dict[str, AgentProfile]:
        """
        Initialize agent profiles with their capabilities
        
        Returns:
            Dictionary of agent profiles
        """
        profiles = {}
        
        # Builder Agent
        builder_capabilities = [
            AgentCapability(capability_name="code_generation", confidence=0.9),
            AgentCapability(capability_name="debugging", confidence=0.85),
            AgentCapability(capability_name="refactoring", confidence=0.8),
            AgentCapability(capability_name="architecture_design", confidence=0.75)
        ]
        profiles["builder"] = AgentProfile(
            agent_type="builder",
            capabilities=builder_capabilities,
            specialties=["development", "implementation", "coding"],
            metadata={"personality": "Blunt, precise, senior backend engineer"}
        )
        
        # Researcher Agent
        researcher_capabilities = [
            AgentCapability(capability_name="information_gathering", confidence=0.95),
            AgentCapability(capability_name="data_analysis", confidence=0.85),
            AgentCapability(capability_name="competitive_analysis", confidence=0.8),
            AgentCapability(capability_name="trend_identification", confidence=0.75)
        ]
        profiles["researcher"] = AgentProfile(
            agent_type="researcher",
            capabilities=researcher_capabilities,
            specialties=["research", "analysis", "investigation"],
            metadata={"personality": "Thorough, analytical, detail-oriented"}
        )
        
        # Planner Agent
        planner_capabilities = [
            AgentCapability(capability_name="task_decomposition", confidence=0.9),
            AgentCapability(capability_name="dependency_management", confidence=0.85),
            AgentCapability(capability_name="resource_allocation", confidence=0.8),
            AgentCapability(capability_name="risk_assessment", confidence=0.75)
        ]
        profiles["planner"] = AgentProfile(
            agent_type="planner",
            capabilities=planner_capabilities,
            specialties=["planning", "coordination", "strategy"],
            metadata={"personality": "Strategic, senior PM style"}
        )
        
        # Ops Agent
        ops_capabilities = [
            AgentCapability(capability_name="deployment", confidence=0.9),
            AgentCapability(capability_name="monitoring", confidence=0.85),
            AgentCapability(capability_name="infrastructure_management", confidence=0.8),
            AgentCapability(capability_name="performance_optimization", confidence=0.75)
        ]
        profiles["ops"] = AgentProfile(
            agent_type="ops",
            capabilities=ops_capabilities,
            specialties=["operations", "deployment", "infrastructure"],
            metadata={"personality": "Reliable, systematic, efficiency-focused"}
        )
        
        # Memory Agent
        memory_capabilities = [
            AgentCapability(capability_name="information_retrieval", confidence=0.95),
            AgentCapability(capability_name="context_management", confidence=0.9),
            AgentCapability(capability_name="knowledge_organization", confidence=0.85),
            AgentCapability(capability_name="pattern_recognition", confidence=0.8)
        ]
        profiles["memory"] = AgentProfile(
            agent_type="memory",
            capabilities=memory_capabilities,
            specialties=["retrieval", "storage", "context"],
            metadata={"personality": "Associative, contextual, detail-oriented"}
        )
        
        return profiles
    
    def route_task(
        self,
        task_description: str,
        task_type: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
        preferred_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route a task to the most appropriate agent
        
        Args:
            task_description: Description of the task
            task_type: Type of task (e.g., code, research, planning)
            required_capabilities: List of required capabilities
            preferred_agent: Preferred agent type (if any)
            metadata: Additional task metadata
            
        Returns:
            Routing result with assigned agent and confidence
        """
        metadata = metadata or {}
        required_capabilities = required_capabilities or []
        
        # Log the routing request
        logger.info(f"Routing task: {task_description[:50]}...")
        self._log_routing_event("route_request", {
            "task_description": task_description,
            "task_type": task_type,
            "required_capabilities": required_capabilities,
            "preferred_agent": preferred_agent,
            "metadata": metadata
        })
        
        # If preferred agent is specified and exists, use it
        if preferred_agent and preferred_agent in self._agent_profiles:
            agent_type = preferred_agent
            confidence = 1.0
            reason = "Explicitly requested agent"
        else:
            # Find the best agent for the task
            agent_type, confidence, reason = self._find_best_agent(
                task_description, task_type, required_capabilities, metadata
            )
        
        # Update agent workload
        self._agent_workload[agent_type] += 1
        
        # Log the routing result
        result = {
            "assigned_agent": agent_type,
            "confidence": confidence,
            "reason": reason,
            "agent_profile": self._agent_profiles[agent_type].dict(),
            "current_workload": self._agent_workload[agent_type]
        }
        
        self._log_routing_event("route_result", result)
        
        return result
    
    def _find_best_agent(
        self,
        task_description: str,
        task_type: Optional[str],
        required_capabilities: List[str],
        metadata: Dict[str, Any]
    ) -> tuple:
        """
        Find the best agent for a task
        
        Args:
            task_description: Description of the task
            task_type: Type of task
            required_capabilities: List of required capabilities
            metadata: Additional task metadata
            
        Returns:
            Tuple of (agent_type, confidence, reason)
        """
        # Initialize scores
        scores = {agent_type: 0.0 for agent_type in self._agent_profiles.keys()}
        reasons = {agent_type: [] for agent_type in self._agent_profiles.keys()}
        
        # Score based on task type
        if task_type:
            for agent_type, profile in self._agent_profiles.items():
                if task_type.lower() in [s.lower() for s in profile.specialties]:
                    scores[agent_type] += 2.0
                    reasons[agent_type].append(f"Specializes in {task_type}")
        
        # Score based on required capabilities
        if required_capabilities:
            for agent_type, profile in self._agent_profiles.items():
                agent_capabilities = {c.capability_name.lower(): c.confidence for c in profile.capabilities}
                for capability in required_capabilities:
                    if capability.lower() in agent_capabilities:
                        confidence = agent_capabilities[capability.lower()]
                        scores[agent_type] += confidence
                        reasons[agent_type].append(f"Has capability: {capability} ({confidence:.2f})")
        
        # Score based on keywords in task description
        task_lower = task_description.lower()
        for agent_type, profile in self._agent_profiles.items():
            # Check for specialty keywords
            for specialty in profile.specialties:
                if specialty.lower() in task_lower:
                    scores[agent_type] += 1.0
                    reasons[agent_type].append(f"Task mentions specialty: {specialty}")
            
            # Check for capability keywords
            for capability in profile.capabilities:
                if capability.capability_name.lower() in task_lower:
                    scores[agent_type] += 0.5
                    reasons[agent_type].append(f"Task mentions capability: {capability.capability_name}")
        
        # Adjust for workload
        for agent_type in scores:
            workload_penalty = min(self._agent_workload[agent_type] * 0.1, 0.5)
            scores[agent_type] -= workload_penalty
            if workload_penalty > 0:
                reasons[agent_type].append(f"Workload penalty: -{workload_penalty:.2f}")
        
        # Find the best agent
        best_agent = max(scores.items(), key=lambda x: x[1])
        agent_type = best_agent[0]
        score = best_agent[1]
        
        # Calculate confidence (normalize score to 0-1 range)
        max_possible_score = 5.0  # Approximate maximum possible score
        confidence = min(score / max_possible_score, 1.0)
        
        # Compile reason
        reason = "; ".join(reasons[agent_type])
        
        return agent_type, confidence, reason
    
    def update_agent_workload(self, agent_type: str, change: int = -1):
        """
        Update the workload for an agent
        
        Args:
            agent_type: Type of agent
            change: Change in workload (negative for completion)
        """
        if agent_type in self._agent_workload:
            self._agent_workload[agent_type] = max(0, self._agent_workload[agent_type] + change)
            
            # Log the workload update
            self._log_routing_event("workload_update", {
                "agent_type": agent_type,
                "change": change,
                "current_workload": self._agent_workload[agent_type]
            })
    
    def get_agent_profile(self, agent_type: str) -> Optional[AgentProfile]:
        """
        Get the profile for an agent
        
        Args:
            agent_type: Type of agent
            
        Returns:
            Agent profile if found, None otherwise
        """
        return self._agent_profiles.get(agent_type)
    
    def get_all_agent_profiles(self) -> Dict[str, AgentProfile]:
        """
        Get all agent profiles
        
        Returns:
            Dictionary of agent profiles
        """
        return self._agent_profiles
    
    def _log_routing_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log a routing event
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Create the log entry
        log_entry = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # Generate a timestamp for the log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(self.logs_dir, f"routing_{event_type}_{timestamp}.json")
        
        # Write the log entry
        with open(log_path, "w") as f:
            json.dump(log_entry, f, indent=2)

# Singleton instance
_agent_router = None

def get_agent_router() -> AgentRouter:
    """
    Get the singleton AgentRouter instance
    """
    global _agent_router
    if _agent_router is None:
        _agent_router = AgentRouter()
    return _agent_router
