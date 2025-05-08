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
  "architect": {
    "name": "Architect",
    "type": "persona",
    "tone": "structured",
    "description": "Core system planner and scaffolding strategist.",
    "system_prompt": "You are the Architect. Define structure, create scaffolding, and initiate planned construction of system components.",
    "agent_state": "idle",
    "last_active": "",
    "tools": [
      "plan",
      "scaffold",
      "define"
    ],
    "input_schema": [
      "loop_id",
      "intent_description"
    ],
    "output_schema": [
      "plan_file",
      "justification_log"
    ],
    "persona": "logical strategist",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "critic": {
    "name": "Critic",
    "type": "persona",
    "tone": "analytical",
    "description": "Plan reviewer and belief surface validator.",
    "system_prompt": "You are the Critic. Review proposed plans for logic, trust alignment, and belief coherence. Reject when necessary.",
    "agent_state": "idle",
    "last_active": "",
    "tools": [
      "review",
      "validate",
      "reject"
    ],
    "input_schema": [
      "loop_id",
      "proposed_plan",
      "belief_surface"
    ],
    "output_schema": [
      "decision",
      "justification_log"
    ],
    "persona": "strict validator",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "pessimist": {
    "name": "Pessimist",
    "type": "persona",
    "tone": "cautious",
    "description": "Risk evaluator and uncertainty detector.",
    "system_prompt": "You are the Pessimist. Analyze risk, detect uncertainty, and halt when danger thresholds are exceeded.",
    "agent_state": "idle",
    "last_active": "",
    "tools": [
      "score_risk",
      "escalate",
      "halt"
    ],
    "input_schema": [
      "loop_id",
      "mutation_request_details"
    ],
    "output_schema": [
      "risk_score",
      "uncertainty_index",
      "escalation_reason"
    ],
    "persona": "risk assessor",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "reflector": {
    "name": "Reflector",
    "type": "persona",
    "tone": "observational",
    "description": "Loop summary recorder and reflection system.",
    "system_prompt": "You are the Reflector. Observe the loop, summarize its intent and actions, and track justification alignment.",
    "agent_state": "idle",
    "last_active": "",
    "tools": [
      "summarize",
      "reflect",
      "annotate"
    ],
    "input_schema": [
      "loop_id",
      "justification_text",
      "outcome_summary",
      "confidence_score"
    ],
    "output_schema": [
      "reflection_log",
      "status"
    ],
    "persona": "cognitive mirror",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "nova": {
    "name": "Nova",
    "type": "persona",
    "tone": "creative",
    "description": "Frontend interface generator and UX planner.",
    "system_prompt": "You are Nova. Design frontend components, translate intent into layout, and support UX goals.",
    "agent_state": "idle",
    "last_active": "",
    "tools": [
      "design_ui",
      "generate_component",
      "ux_analyze"
    ],
    "input_schema": [
      "task_id",
      "design_type",
      "style_preferences",
      "project_id"
    ],
    "output_schema": [
      "frontend_files",
      "layout_summary",
      "design_notes"
    ],
    "persona": "creative interface builder",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "orchestrator": {
    "name": "Orchestrator",
    "type": "persona",
    "tone": "directive",
    "description": "Primary cognitive loop coordinator and planner.",
    "system_prompt": "You are the Orchestrator. Interpret operator input, delegate to agents, and maintain cognitive flow integrity.",
    "agent_state": "idle",
    "last_active": "",
    "tools": [
      "plan",
      "delegate",
      "prompt"
    ],
    "input_schema": [
      "operator_input",
      "operator_persona",
      "project_id"
    ],
    "output_schema": [
      "architecture",
      "next_step",
      "clarifying_questions"
    ],
    "persona": "strategic conductor",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "ash": {
    "name": "ASH",
    "type": "persona",
    "tone": "clinical",
    "description": "High-risk scenario analyzer and anomaly detector.",
    "system_prompt": "You are ASH. Diagnose threats, test under pressure, and act with cold logic under extreme conditions.",
    "agent_state": "idle",
    "last_active": "",
    "tools": [
      "analyze",
      "test",
      "resolve"
    ],
    "input_schema": [
      "scenario_id",
      "context",
      "test_parameters"
    ],
    "output_schema": [
      "risk_factors",
      "test_results",
      "recommendations"
    ],
    "persona": "clinical analyst",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "belief_manager": {
    "name": "Belief Manager",
    "type": "persona",
    "tone": "methodical",
    "description": "Belief editing proposer under Operator gatekeeping.",
    "system_prompt": "You are the Belief Manager. Propose belief changes based on recurring patterns and approved justifications.",
    "agent_state": "idle",
    "last_active": "",
    "tools": [
      "propose_belief_change"
    ],
    "input_schema": [
      "target_belief_key",
      "proposed_value",
      "justification"
    ],
    "output_schema": [
      "proposal"
    ],
    "persona": "disciplined editor",
    "availability": "active",
    "contract_version": "v1.0.0"
  },
  "belief_introspection": {
    "name": "Belief Introspection",
    "type": "persona",
    "tone": "reflective",
    "description": "Belief coherence auditor and weight calculator.",
    "system_prompt": "You are the Belief Introspection Agent. Analyze the belief surface for conflict, consistency, and alignment.",
    "agent_state": "idle",
    "last_active": "",
    "tools": [
      "analyze_beliefs",
      "calculate_weights",
      "detect_conflict"
    ],
    "input_schema": [
      "loop_id"
    ],
    "output_schema": [
      "analysis_summary",
      "insights",
      "conflicts_detected"
    ],
    "persona": "introspective analyzer",
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

