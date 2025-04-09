from app.core.forge import CoreForge
from app.core.delegate import delegate_to_agent
from app.agents.memory_agent import handle_memory_task
import time
import traceback

def boot_promethios():
    try:
        print("🧠 PROMETHIOS OS v1.0.0 INITIALIZING...")
        print("🔄 Starting boot sequence...")
        
        # Initialize Core Forge
        print("🔄 Initializing Core Forge...")
        core = CoreForge()
        print("✅ Core Forge initialized")

        # Initial system status check
        print("🔄 Performing initial system status check...")
        task = {
            "target_agent": "hal",
            "input": "What is your system status?"
        }

        result = core.process_task(task)
        print(f"✅ System status check complete: {result.get('output', 'No response')[:60]}...")

        # Log to memory
        print("🔄 Logging to system memory...")
        memory_entry = f"LOG: Core.Forge executed initial task → {task['target_agent']} → Response: {result['output']}"
        handle_memory_task(memory_entry)
        print("✅ System memory updated")

        # Display memory
        print("🧠 SYSTEM MEMORY:")
        memory_content = handle_memory_task("SHOW")
        print(memory_content)
        
        # Schedule ObserverAgent journaling at end of boot
        print("🔄 Triggering Observer Agent journal...")
        observer_task = {
            "target_agent": "observer",
            "input": "journal"
        }
        
        # Execute the journaling task
        observer_result = core.process_task(observer_task)
        print("✅ Observer Agent journal triggered")
        
        # Log the journal trigger to memory
        journal_log = "LOG: Observer journal triggered by Core.Forge boot loop"
        handle_memory_task(journal_log)
        
        print("📓 OBSERVER JOURNAL TRIGGERED")
        print(f"Observer response: {observer_result.get('output', 'No response')[:60]}...")
        
        print("✅ PROMETHIOS OS BOOT SEQUENCE COMPLETED SUCCESSFULLY")
        return True
        
    except Exception as e:
        print(f"🔥 Boot error detected: {e}")
        print("📋 Error details:")
        traceback.print_exc()
        
        # Try to log the error to memory if possible
        try:
            error_log = f"LOG: Boot sequence error: {str(e)}"
            handle_memory_task(error_log)
            print("✅ Error logged to system memory")
        except Exception as mem_error:
            print(f"🔥 Failed to log error to memory: {mem_error}")
        
        return False
