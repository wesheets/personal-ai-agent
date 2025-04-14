from datetime import datetime
from app.agents.memory_agent import handle_memory_task

def handle_observer_task(task_input):
    if task_input == "journal":
        today = datetime.now().strftime("%Y-%m-%d")
        memory_summary = handle_memory_task("SHOW")

        log_entry = f"""## 📅 {today}

### 🧠 Agent Reflections:
{memory_summary}

### 🧩 Behavior Observed:
[todo]

### ⚠️ Anomalies / Failures:
[todo]

### 📦 Vertical Progress:
[todo]

### 🔁 Loops Observed:
[todo]

### 💬 System Personality Notes:
[todo]

### 🧬 Philosophical Questions Raised:
[todo]
"""

        with open("logs/observation/promethios_observations.md", "a") as f:
            f.write(log_entry + "\n---\n")

        return "🧠 ObserverAgent: Daily journal appended to promethios_observations.md"
    else:
        return f"🧠 ObserverAgent: Unknown task '{task_input}'"
