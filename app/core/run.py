from app.agents.hal_agent import handle_hal_task
from app.agents.ash_agent import handle_ash_task
from app.agents.ops_agent import handle_ops_task
from app.agents.memory_agent import handle_memory_task

AGENT_HANDLERS = {
    "hal": handle_hal_task,
    "ash": handle_ash_task,
    "ops-agent": handle_ops_task,
    "memory-agent": handle_memory_task
}

def run_agent(agent_id, task_input):
    if agent_id not in AGENT_HANDLERS:
        return f"Unknown agent: {agent_id}"
    handler = AGENT_HANDLERS[agent_id]
    return handler(task_input)
