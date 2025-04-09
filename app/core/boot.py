from app.core.forge import CoreForge
from app.core.delegate import delegate_to_agent
from app.agents.memory_agent import handle_memory_task

def boot_promethios():
    core = CoreForge()

    print("🧠 PROMETHIOS OS v1.0.0 INITIALIZING...")

    task = {
        "target_agent": "hal",
        "input": "What is your system status?"
    }

    result = core.process_task(task)

    memory_entry = f"LOG: Core.Forge executed initial task → {task['target_agent']} → Response: {result['output']}"
    handle_memory_task(memory_entry)

    print("🧠 SYSTEM MEMORY:")
    print(handle_memory_task("SHOW"))
    
    # Schedule ObserverAgent journaling at end of boot
    observer_task = {
        "target_agent": "observer",
        "input": "journal"
    }
    
    # Execute the journaling task
    observer_result = core.process_task(observer_task)
    
    # Log the journal trigger to memory
    journal_log = "LOG: Observer journal triggered by Core.Forge boot loop"
    handle_memory_task(journal_log)
    
    print("📓 OBSERVER JOURNAL TRIGGERED")
    print(f"Observer response: {observer_result.get('output', 'No response')}")
