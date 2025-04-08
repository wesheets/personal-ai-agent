memory_log = []

def handle_memory_task(task_input):
    if task_input.startswith("LOG:"):
        entry = task_input.replace("LOG:", "").strip()
        memory_log.append(entry)
        return f"🧠 Memory Logged: {entry}"
    elif task_input == "SHOW":
        return "\n".join(memory_log[-10:]) or "🧠 No recent memory."
    elif task_input == "FULL":
        return "\n".join(memory_log) or "🧠 Memory is empty."
    else:
        return f"🧠 MemoryAgent did not understand: '{task_input}'"
