"""
Toolkit Registry for Promethios Agents

This module provides a registry of tools available to different agents based on domain.
It enables specialized toolkits for HAL, ASH, and NOVA agents to produce SaaS-grade outputs.
"""

# Toolkit registry that maps agent IDs to domains and their associated tools
TOOLKIT_REGISTRY = {
    "hal": {
        "saas": ["scope.shaper", "mvp.planner", "feature.writer", "pricing.modeler"]
    },
    "ash": {
        "saas": ["architecture.explainer", "api.docifier", "onboarding.writer"]
    },
    "nova": {
        "saas": ["layout.hero", "layout.dashboard", "component.card", "cta.prompt"],
        "themes": ["calming", "premium", "bold", "minimalist"]
    }
}

# Agent roles for system prompts
AGENT_ROLES = {
    "hal": "SaaS Architect",
    "ash": "Documentation & UX Explainer",
    "nova": "UI Designer & Copy Generator"
}


def get_toolkit(agent_id: str, domain: str = "saas") -> list:
    """
    Retrieve the toolkit for a specific agent and domain.
    
    Args:
        agent_id (str): The identifier of the agent (hal, ash, nova)
        domain (str, optional): The domain/context for the toolkit. Defaults to "saas".
        
    Returns:
        list: A list of tool identifiers available to the agent for the specified domain.
              Returns an empty list if agent_id or domain is not found.
    """
    return TOOLKIT_REGISTRY.get(agent_id, {}).get(domain, [])


def get_agent_role(agent_id: str) -> str:
    """
    Retrieve the system role for a specific agent.
    
    Args:
        agent_id (str): The identifier of the agent (hal, ash, nova)
        
    Returns:
        str: The system role description for the agent.
             Returns an empty string if agent_id is not found.
    """
    return AGENT_ROLES.get(agent_id, "")


def get_agent_themes(agent_id: str) -> list:
    """
    Retrieve the available themes for a specific agent.
    
    Args:
        agent_id (str): The identifier of the agent (hal, ash, nova)
        
    Returns:
        list: A list of theme identifiers available to the agent.
              Returns an empty list if agent_id is not found or has no themes.
    """
    return TOOLKIT_REGISTRY.get(agent_id, {}).get("themes", [])


def format_tools_prompt(tools: list) -> str:
    """
    Format a list of tools into a prompt string.
    
    Args:
        tools (list): List of tool identifiers
        
    Returns:
        str: A formatted string for inclusion in agent prompts
    """
    if not tools:
        return ""
    
    tools_str = ", ".join(tools)
    return f"You have access to the following tools: {tools_str}.\nUse them to create a production-ready result."


def format_nova_prompt(tools: list, themes: list = None) -> str:
    """
    Format a specialized prompt for NOVA with layout templates and themes.
    
    Args:
        tools (list): List of tool identifiers (layout templates)
        themes (list, optional): List of theme identifiers. Defaults to None.
        
    Returns:
        str: A formatted string for inclusion in NOVA's prompts
    """
    if not tools:
        return ""
    
    # Format layout templates
    layout_templates = []
    for tool in tools:
        if tool.startswith("layout."):
            layout_templates.append(tool.replace("layout.", ""))
        elif tool.startswith("component."):
            layout_templates.append(tool.replace("component.", ""))
        elif tool.startswith("cta."):
            layout_templates.append(tool.replace("cta.", "CTA"))
        else:
            layout_templates.append(tool)
    
    templates_str = ", ".join(layout_templates)
    prompt = f"You have access to layout templates: {templates_str}."
    
    # Add theme suggestion if available
    if themes and len(themes) > 0:
        themes_str = " and ".join(themes[:2])  # Use first two themes
        prompt += f"\nSuggested tone: {themes_str}. Use Tailwind-friendly classes."
    
    # Add styling structure
    prompt += "\nFollow this prompt styling structure: hero → dashboard → CTA → footer"
    
    return prompt
