# app/toolkit/registry/__init__.py
# This is a bridge module to ensure proper import path resolution
# It imports from the main toolkit.registry module to avoid import errors

try:
    from toolkit.registry import get_toolkit, get_agent_role, format_tools_prompt, format_nova_prompt, get_agent_themes
except ImportError:
    # Fallback implementation if the main module can't be imported
    def get_toolkit(name, domain="saas"):
        """
        Get toolkit for the specified agent and domain.
        This is a fallback implementation if the main module can't be imported.
        """
        print(f"⚠️ Using fallback toolkit implementation for {name} in {domain} domain")
        return f"Toolkit '{name}' loaded (stub)"

    def get_agent_role(agent_id):
        """
        Get role for the specified agent.
        This is a fallback implementation if the main module can't be imported.
        """
        return {
            "hal": "builder",
            "nova": "designer",
            "ash": "executor",
            "critic": "reviewer",
            "orchestrator": "planner"
        }.get(agent_id, "generalist")

    def format_tools_prompt(tools):
        """
        Format tools prompt for the specified tools.
        This is a fallback implementation if the main module can't be imported.
        """
        if not tools:
            return "No tools assigned."
        return f"Agent has access to the following tools: {', '.join(tools)}"

    def format_nova_prompt(ui_task):
        """
        Format NOVA prompt for the specified UI task.
        This is a fallback implementation if the main module can't be imported.
        """
        return f"NOVA, design this UI component: {ui_task}"

    def get_agent_themes():
        """
        Get themes for all agents.
        This is a fallback implementation if the main module can't be imported.
        """
        return {
            "hal": "precision + recursion",
            "nova": "creativity + clarity",
            "ash": "speed + automation",
            "critic": "caution + refinement",
            "orchestrator": "strategy + delegation"
        }
