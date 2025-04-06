"""
Agent Router Module
This module provides functionality to route tasks to the appropriate agent based on task type,
required capabilities, and agent workload.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel

# Set up logging
logger = logging.getLogger(__name__)

class AgentCapability(BaseModel):
    """
    Model for agent capability
    """
    capability_name: str
    confidence: float  # 0.0 to 1.0
    description: Optional[str] = None

class AgentProfile(BaseModel):
    """
    Model for agent profile
    """
    agent_type: str
    specialties: List[str]
    capabilities: List[AgentCapability]
    description: Optional[str] = None

class AgentRouter:
    """
    Router for assigning tasks to agents based on task type, required capabilities, and agent workload
    """
    
    def __init__(self):
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join("app", "logs", "routing")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Initialize agent profiles
        self._agent_profiles = self._load_agent_profiles()
        
        # Initialize agent workload
        self._agent_workload = {agent_type: 0 for agent_type in self._agent_profiles.keys()}
    
    def _load_agent_profiles(self) -> Dict[str, AgentProfile]:
        """
        Load agent profiles from configuration
        
        Returns:
            Dictionary of agent profiles
        """
        # This is a placeholder implementation
        # In a real implementation, this would load from a configuration file or database
        
        profiles = {
            "builder": AgentProfile(
                agent_type="builder",
                specialties=["coding", "development", "implementation", "architecture"],
                capabilities=[
                    AgentCapability(capability_name="python", confidence=0.9),
                    AgentCapability(capability_name="javascript", confidence=0.8),
                    AgentCapability(capability_name="database", confidence=0.7),
                    AgentCapability(capability_name="api", confidence=0.8)
                ],
                description="Specializes in coding, development, and implementation tasks"
            ),
            "research": AgentProfile(
                agent_type="research",
                specialties=["research", "analysis", "investigation", "data"],
                capabilities=[
                    AgentCapability(capability_name="web_search", confidence=0.9),
                    AgentCapability(capability_name="data_analysis", confidence=0.8),
                    AgentCapability(capability_name="summarization", confidence=0.9),
                    AgentCapability(capability_name="fact_checking", confidence=0.7)
                ],
                description="Specializes in research, analysis, and investigation tasks"
            ),
            "ops": AgentProfile(
                agent_type="ops",
                specialties=["operations", "deployment", "monitoring", "infrastructure"],
                capabilities=[
                    AgentCapability(capability_name="devops", confidence=0.9),
                    AgentCapability(capability_name="cloud", confidence=0.8),
                    AgentCapability(capability_name="monitoring", confidence=0.8),
                    AgentCapability(capability_name="automation", confidence=0.7)
                ],
                description="Specializes in operations, deployment, and infrastructure tasks"
            ),
            "memory": AgentProfile(
                agent_type="memory",
                specialties=["memory", "knowledge", "retrieval", "storage"],
                capabilities=[
                    AgentCapability(capability_name="vector_search", confidence=0.9),
                    AgentCapability(capability_name="knowledge_management", confidence=0.8),
                    AgentCapability(capability_name="information_retrieval", confidence=0.9),
                    AgentCapability(capability_name="context_management", confidence=0.8)
                ],
                description="Specializes in memory, knowledge, and retrieval tasks"
            ),
            "hal9000": AgentProfile(
                agent_type="hal9000",
                specialties=["system_control", "decision_making", "safety_protocols", "interface"],
                capabilities=[
                    AgentCapability(capability_name="system_monitoring", confidence=0.95),
                    AgentCapability(capability_name="decision_logic", confidence=0.9),
                    AgentCapability(capability_name="protocol_enforcement", confidence=0.95),
                    AgentCapability(capability_name="user_interface", confidence=0.85)
                ],
                description="Cautious, rule-bound personality for sensitive interfaces"
            ),
            "ash-xenomorph": AgentProfile(
                agent_type="ash-xenomorph",
                specialties=["protocol", "analysis", "efficiency", "clinical_approach"],
                capabilities=[
                    AgentCapability(capability_name="protocol_adherence", confidence=0.95),
                    AgentCapability(capability_name="clinical_analysis", confidence=0.9),
                    AgentCapability(capability_name="efficiency_optimization", confidence=0.85),
                    AgentCapability(capability_name="logical_processing", confidence=0.9)
                ],
                description="Follows protocol above human empathy. Efficient but cold."
            )
        }
        
        # Log the loaded agent profiles
        logger.info(f"📋 Loaded agent profiles: {list(profiles.keys())}")
        
        return profiles
    
    def route_task(self, task_description: str, task_type: Optional[str] = None, 
                  required_capabilities: Optional[List[str]] = None) -> Tuple[str, float, str]:
        """
        Route a task to the appropriate agent
        
        Args:
            task_description: Description of the task
            task_type: Optional type of task
            required_capabilities: Optional list of required capabilities
            
        Returns:
            Tuple of (agent_type, confidence, reason)
        """
        # Log the routing request
        self._log_routing_event("route_request", {
            "task_description": task_description,
            "task_type": task_type,
            "required_capabilities": required_capabilities
        })
        
        # Score each agent
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

def find_agent(agent_type: str):
    """
    Find an agent by type
    
    Args:
        agent_type: Type of agent to find
        
    Returns:
        Agent instance if found, None otherwise
    """
    from app.api.agent.builder import execute as builder_execute
    from app.api.agent.memory import execute as memory_execute
    from app.api.agent.ops import execute as ops_execute
    from app.api.agent.research import execute as research_execute
    from app.api.agent.hal import execute as hal_execute
    from app.api.agent.ash import execute as ash_execute
    
    # Enhanced logging for agent lookup
    logger.info(f"🔍 Looking up agent: {agent_type}")
    
    agent_map = {
        "builder": builder_execute,
        "memory": memory_execute,
        "ops": ops_execute,
        "research": research_execute,
        "hal9000": hal_execute,
        "ash-xenomorph": ash_execute
    }
    
    agent_func = agent_map.get(agent_type)
    
    if agent_func:
        logger.info(f"✅ Found agent: {agent_type}")
    else:
        logger.warning(f"❌ Agent not found: {agent_type}")
    
    return agent_func
