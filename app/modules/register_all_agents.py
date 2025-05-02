"""
Register All Agents Module

This module provides a centralized place to register all agents in the system.
It imports all agent handler functions and registers them with the agent registry.
"""

from app.modules.agent_registry import register_agent
from app.agents.hal import run_hal_agent
from app.agents.nova import run_nova_agent
from app.agents.critic import run_critic_agent
from app.agents.ash import run_ash_agent
from app.agents.sage import run_sage_agent

def register_all_agents():
    """
    Register all available agents with the central registry.
    This function should be called during application startup.
    """
    register_agent("hal", run_hal_agent)
    register_agent("nova", run_nova_agent)
    register_agent("critic", run_critic_agent)
    register_agent("ash", run_ash_agent)
    register_agent("sage", run_sage_agent)
    
    # Add any additional agents here in the future
    
    # Optional: register orchestrator if available
    try:
        from app.agents.orchestrator import run_orchestrator_agent
        register_agent("orchestrator", run_orchestrator_agent)
    except ImportError:
        print("⚠️ Orchestrator agent not available, skipping registration")
