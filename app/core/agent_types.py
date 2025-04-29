# app/core/agent_types.py
from enum import Enum

class AgentCapability(Enum):
    """Defines the capabilities an agent can possess."""
    # General Capabilities
    PLANNING = "PLANNING"
    TASK_DECOMPOSITION = "TASK_DECOMPOSITION"
    REASONING = "REASONING"
    SELF_REFLECTION = "SELF_REFLECTION"
    
    # Execution Capabilities
    CODE_GENERATION = "CODE_GENERATION"
    DEBUGGING = "DEBUGGING"
    TOOL_USE = "TOOL_USE"
    WEB_BROWSING = "WEB_BROWSING"
    FILE_MANAGEMENT = "FILE_MANAGEMENT"
    
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
    # Add more capabilities as needed

