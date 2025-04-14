from app.agents.memory_agent import handle_memory_task

def handle_trainer_task(task_input):
    if task_input == "train":
        logs = handle_memory_task("SHOW")
        lessons = []

        if "failed" in logs.lower():
            lessons.append("Ash needs better fault tolerance.")
        if "blocked" in logs.lower():
            lessons.append("HAL constraint logic needs refinement.")
        if "static fallback" in logs.lower():
            lessons.append("Ensure all agents use OpenAIProvider.")

        with open("training/agent_lessons.md", "a") as f:
            for line in lessons:
                f.write(f"- [ ] {line}\n")

        return f"TrainerAgent: {len(lessons)} lesson(s) added."

    return f"TrainerAgent: Unknown task '{task_input}'"
