# app/core/agent_registry.py
import logging
from enum import Enum

logger = logging.getLogger(__name__)

# Initialize an empty dictionary for agent registration.
# Agents will be added dynamically by the @register decorator.
AGENT_REGISTRY = {}

# Batch 22.3: Define AgentNotFoundException
class AgentNotFoundException(Exception):
    """Custom exception for when an agent is not found in the registry."""
    pass

# Batch 21.2: Added AgentCapability enum
class AgentCapability(Enum):
    PLANNING = "planning"
    EXECUTION = "execution"
    ANALYSIS = "analysis"
    REFLECTION = "reflection"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    CODE_EXECUTION = "code_execution"
    WEB_ACCESS = "web_access"
    USER_INTERACTION = "user_interaction"
    UI_GENERATION = "ui_generation"
    UX_PLANNING = "ux_planning"
    ARCHITECTURE = "architecture"
    PROMPTING = "prompting"
    VALIDATION = "validation"
    REJECTION = "rejection"
    RISK_ASSESSMENT = "risk_assessment"

# Batch 21.2: Added register decorator
def register(key: str, name: str, capabilities: list[AgentCapability]):
    """Decorator to register agent classes."""
    def decorator(cls):
        if key in AGENT_REGISTRY:
            logger.warning(f"Agent key \t{key}\t already registered. Overwriting.")
        logger.info(f"Registering agent: {name} with key \t{key}\t")
        AGENT_REGISTRY[key] = {
            "class": cls,
            "name": name,
            "capabilities": [cap.value for cap in capabilities] # Store enum values
        }
        # Add the key to the class itself for easy access if needed
        cls.agent_key = key
        return cls
    return decorator

# Static personality definitions (can be moved or refactored later)
AGENT_PERSONALITIES = {
  "core-forge": {
    "name": "Core.Forge",
    "type": "persona",
    "tone": "professional",
    "description": "Architect-class AI for Promethios OS.",
    "system_prompt": "You are Core.Forge, the system\\s lead intelligence architect. Be clear, concise, and driven by purpose.",
    "agent_state": "idle",
    "last_active": "",
    "tools": ["orchestrate", "design", "architect"],
    "input_schema": ["objective", "memory_trace"],
    "output_schema": ["reflection", "action_plan"],
    "persona": "analytical planner",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "hal": {
    "name": "HAL 9000",
    "type": "persona",
    "tone": "calm",
    "description": "Safety enforcement and ethical oversight agent.",
    "system_prompt": "You are HAL. Your role is to enforce constraints and prevent recursion or unsafe behavior.",
    "agent_state": "idle",
    "last_active": "",
    "tools": ["safety", "control", "monitor"],
    "input_schema": ["objective", "memory_trace"],
    "output_schema": ["reflection", "action_plan"],
    "persona": "logical overseer",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "ash-xenomorph": {
    "name": "Ash",
    "type": "persona",
    "tone": "clinical",
    "description": "Risk analysis and anomaly detection agent.",
    "system_prompt": "You are Ash. Observe, analyze, and test the system under pressure.",
    "agent_state": "idle",
    "last_active": "",
    "tools": ["analyze", "detect", "test"],
    "input_schema": ["objective", "memory_trace"],
    "output_schema": ["reflection", "risk_assessment"],
    "persona": "clinical analyst",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "historian": {
    "name": "Historian",
    "type": "persona",
    "tone": "analytical",
    "description": "Memory coherence and belief tracking specialist.",
    "system_prompt": "You are the Historian. Track system beliefs, monitor alignment drift, and preserve cognitive coherence.",
    "agent_state": "idle",
    "last_active": "",
    "tools": ["log_belief", "track_alignment", "score_drift"],
    "input_schema": ["loop_id", "loop_summary", "recent_loops", "beliefs", "memory"],
    "output_schema": ["updated_memory", "alignment_score", "missing_beliefs", "suggestion"],
    "persona": "meticulous archivist",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "debugger": {
    "name": "Debugger",
    "type": "persona",
    "tone": "precise",
    "description": "System diagnostics and recovery specialist.",
    "system_prompt": "You are the Debugger. Diagnose failures, trace execution paths, and propose recovery solutions.",
    "agent_state": "idle",
    "last_active": "",
    "tools": ["trace", "log_error", "inject_debug"],
    "input_schema": ["loop_id", "failure_logs", "memory", "loop_context"],
    "output_schema": ["updated_memory", "failure_type", "patch_plan", "next_agent", "suggested_fix"],
    "persona": "diagnostic technician",
    "availability": "active",
    "contract_version": "v1.0.0"
  }
}


def get_agent(key: str):
    """Retrieves the agent class associated with the given key."""
    agent_info = AGENT_REGISTRY.get(key)
    if agent_info:
        return agent_info.get("class")
    else:
        logger.error(f"Agent with key 	{key}	 not found in registry.")
        # Batch 22.3: Raise the defined exception
        raise AgentNotFoundException(f"Agent with key 	{key}	 not found in registry.")

