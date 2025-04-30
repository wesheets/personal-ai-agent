# app/core/agent_types.py
from enum import Enum

class AgentCapability(Enum):
    """Defines the capabilities an agent can possess."""
    # General Capabilities
    PLANNING = "PLANNING"
    TASK_DECOMPOSITION = "TASK_DECOMPOSITION"
    REASONING = "REASONING"
    SELF_REFLECTION = "SELF_REFLECTION"
    VALIDATION = "VALIDATION" # Added missing capability for CriticAgent
    ARCHITECTURE = "ARCHITECTURE" # Added missing capability for OrchestratorAgent
    REFLECTION = "REFLECTION" # Added missing capability for OrchestratorAgent
    TONE_ANALYSIS = "TONE_ANALYSIS" # Added missing capability (discovered via final run)
    INTENT_ALIGNMENT = "INTENT_ALIGNMENT" # Added missing capability (discovered via final run)

    # Execution Capabilities
    CODE_GENERATION = "CODE_GENERATION"
    DEBUGGING = "DEBUGGING"
    TOOL_USE = "TOOL_USE"
    WEB_BROWSING = "WEB_BROWSING"
    FILE_MANAGEMENT = "FILE_MANAGEMENT"
    PROMPTING = "PROMPTING" # Added missing capability (discovered via discovery run)
    LIGHT_BUILD = "LIGHT_BUILD" # Added missing capability (discovered via final run)

    # Memory Capabilities
    MEMORY_READ = "MEMORY_READ"
    MEMORY_WRITE = "MEMORY_WRITE"
    VECTOR_SEARCH = "VECTOR_SEARCH"

    # Specialized Capabilities
    UI_GENERATION = "UI_GENERATION"
    DATA_ANALYSIS = "DATA_ANALYSIS"
    SYSTEM_MONITORING = "SYSTEM_MONITORING"
    SECURITY_ANALYSIS = "SECURITY_ANALYSIS"
    ETHICAL_REASONING = "ETHICAL_REASONING"
    BUILD_AUTONOMY = "BUILD_AUTONOMY" # From Forge agent
    RESEARCH = "RESEARCH" # Added missing capability (discovered via discovery run)
    UX_PLANNING = "UX_PLANNING" # Added missing capability (discovered via discovery run)
    REJECTION = "REJECTION" # Added missing capability (discovered via discovery run)
    # Add more capabilities as needed

