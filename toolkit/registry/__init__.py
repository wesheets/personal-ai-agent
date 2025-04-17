# toolkit/registry/__init__.py

def get_toolkit(name):
    # TEMP MOCK for dynamic toolkit lookup
    return f"Toolkit '{name}' loaded (stub)"

def get_agent_role(agent_id):
    return {
        "hal": "builder",
        "nova": "designer",
        "ash": "executor",
        "critic": "reviewer",
        "orchestrator": "planner"
    }.get(agent_id, "generalist")

def format_tools_prompt(tools):
    if not tools:
        return "No tools assigned."
    return f"Agent has access to the following tools: {', '.join(tools)}"

def format_nova_prompt(ui_task):
    return f"NOVA, design this UI component: {ui_task}"

def get_agent_themes():
    return {
        "hal": "precision + recursion",
        "nova": "creativity + clarity",
        "ash": "speed + automation",
        "critic": "caution + refinement",
        "orchestrator": "strategy + delegation"
    }
