from app.core.run import run_agent

def delegate_to_agent(from_agent, to_agent, task_input):
    print(f"[{from_agent} → {to_agent}] Task delegated: {task_input}")
    result = run_agent(to_agent, task_input)
    print(f"[{to_agent} → {from_agent}] Result: {result}")
    return result
