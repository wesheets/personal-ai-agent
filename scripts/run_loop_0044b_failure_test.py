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
EXECUTION_LOG_PATH = os.path.join(LOG_DIR, "loop_0044b_execution.log")

async def main():
    print("Starting test script: run_loop_0044b_failure_test.py")
    print("Simulating a failed loop outcome...")

    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    loop_id = "loop_0044b"
    # Based on current loop_controller.py: iteration % 2 != 0 is failure.
    iteration = 1 # Iteration 1 for failure
    agent_id_for_test = "test_agent_0044b"

    try:
        # The run_loop in the modified controller is simplified and directly calls track_emotion_drift.
        await run_loop(loop_id=loop_id, iteration=iteration)
        with open(EXECUTION_LOG_PATH, "w") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z - Test {loop_id} (Failure Scenario) executed.\n")
            f.write(f"Expected outcome: Failure. Emotion drift should reflect negative change for agent.\n")
        print(f"Loop {loop_id} simulation complete. Execution log at: {EXECUTION_LOG_PATH}")
        print("Please verify agent_emotion_profile.json and emotion_drift_tracker.json for expected updates.")

    except Exception as e:
        print(f"Error during test execution: {e}")
        with open(EXECUTION_LOG_PATH, "w") as f:
            f.write(f"{datetime.utcnow().isoformat()}Z - Test {loop_id} (Failure Scenario) FAILED to execute.\nError: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())

