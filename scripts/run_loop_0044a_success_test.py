#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime

# Adjust path to import from app
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Assuming scripts is one level below project root
APP_DIR_FOR_IMPORT = os.path.join(PROJECT_ROOT, "app")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Ensure app.controllers can be found
if APP_DIR_FOR_IMPORT not in sys.path:
    sys.path.insert(0, APP_DIR_FOR_IMPORT)

from app.controllers.loop_controller import run_loop # Assuming run_loop is the entry point

LOG_DIR = os.path.join(PROJECT_ROOT, "app/logs")
EXECUTION_LOG_PATH = os.path.join(LOG_DIR, "loop_0044a_execution.log")

async def main():
    print("Starting test script: run_loop_0044a_success_test.py")
    print("Simulating a successful loop outcome...")

    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    loop_id = "loop_0044a"
    iteration = 1 # For this test, iteration 1 will be success based on controller logic
    agent_id_for_test = "test_agent_0044a"
    
    # Modify loop_controller.py to accept agent_id or ensure it uses a consistent one for testing
    # For now, we assume run_loop in controller will use a test agent or we modify it.
    # The current loop_controller.py has a hardcoded agent_id="test_agent" in its simplified run_loop.
    # We will rely on that for now, but ideally, test scripts should control this.

    try:
        # The run_loop in the modified controller is simplified and directly calls track_emotion_drift.
        # It uses iteration % 2 to determine success/failure. Iteration 1 is failure.
        # Let's adjust iteration to 0 for success, or modify controller's test logic.
        # Based on current loop_controller.py: iteration % 2 == 0 is success.
        await run_loop(loop_id=loop_id, iteration=0) # Iteration 0 for success
        
        with open(EXECUTION_LOG_PATH, "w") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z - Test {loop_id} (Success Scenario) executed.\n")
            f.write(f"Expected outcome: Success. Emotion drift should reflect positive change for agent.\n")
        print(f"Loop {loop_id} simulation complete. Execution log at: {EXECUTION_LOG_PATH}")
        print("Please verify agent_emotion_profile.json and emotion_drift_tracker.json for expected updates.")

    except Exception as e:
        print(f"Error during test execution: {e}")
        with open(EXECUTION_LOG_PATH, "w") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z - Test {loop_id} (Success Scenario) FAILED to execute.\nError: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())

