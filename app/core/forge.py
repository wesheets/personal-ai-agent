from app.core.run import run_agent

class CoreForge:
    def __init__(self):
        self.agent_id = "core-forge"

    def process_task(self, task):
        agent = task.get("target_agent", "")
        task_input = task.get("input", "")

        if not agent or not task_input:
            return "Task missing required fields."

        result = run_agent(agent, task_input)

        # Log the execution (replace with actual memory integration later)
        print(f"[Core.Forge] → Routed task to {agent}: {task_input}")
        print(f"[Core.Forge] ← Response: {result}")

        return {
            "status": "complete",
            "executor": self.agent_id,
            "routed_to": agent,
            "input": task_input,
            "output": result
        }
