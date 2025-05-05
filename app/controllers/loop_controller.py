#!/usr/bin/env python3.11
import json
import argparse
import os
import sys
import asyncio
from datetime import datetime

# Get the directory of the current script (loop_controller.py)
CONTROLLER_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the 'app' directory
APP_DIR = os.path.dirname(CONTROLLER_DIR)
# Get the project root directory (one level above 'app')
PROJECT_ROOT = os.path.dirname(APP_DIR)

# Add the project root directory to sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Now imports relative to the project root (app.*) should work
from app.validators.mutation_guard import process_mutation_request
from app.registry import get_agent, agent_registry # Import agent registry function and registry itself for agent loading
from app.schemas.agent_input.architect_agent_input import ArchitectInstruction # Import input schema
from app.schemas.agent_output.architect_agent_output import ArchitectPlanResult # Import output schema
from app.utils.status import ResultStatus # Import status enum
from app.utils.justification_logger import log_justification # Import justification logging utility

# Define paths relative to PROJECT_ROOT
LOOP_SUMMARY_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json")
REJECTION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary_rejection_log.json")
LOOP_INTENT_DIR = os.path.join(PROJECT_ROOT, "app/memory/")
MEMORY_DIR = os.path.join(PROJECT_ROOT, "app/memory/")

def load_json(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content:
                if os.path.basename(path).startswith("loop_intent"):
                    return None
                elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json"]:
                     return {}
                else:
                    return []
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: File not found at {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json"]:
             return {}
        else:
            return []
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json"]:
             return {}
        else:
            return []

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def log_loop_summary(loop_id, intent_description, status):
    summary_log = load_json(LOOP_SUMMARY_PATH)
    if not isinstance(summary_log, list):
        print(f"Warning: {LOOP_SUMMARY_PATH} is not a list. Reinitializing.")
        summary_log = []
    entry = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "intent": intent_description,
        "status": status
    }
    summary_log.append(entry)
    save_json(summary_log, LOOP_SUMMARY_PATH)

def log_rejection(loop_id, reason):
    rejection_log = load_json(REJECTION_LOG_PATH)
    if not isinstance(rejection_log, list):
        print(f"Warning: {REJECTION_LOG_PATH} is not a list. Reinitializing.")
        rejection_log = []
    entry = {
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "reason": reason
    }
    rejection_log.append(entry)
    save_json(rejection_log, REJECTION_LOG_PATH)

def get_loop_intent_data(loop_id):
    """Loads the full intent data for a given loop ID."""
    intent_path = os.path.join(LOOP_INTENT_DIR, f"loop_intent_{loop_id}.json")
    renamed_intent_path = os.path.join(LOOP_INTENT_DIR, f"loop_intent_loop_{loop_id}.json")

    actual_path = None
    if os.path.exists(renamed_intent_path):
        actual_path = renamed_intent_path
        print(f"Note: Using renamed intent file: {actual_path}")
    elif os.path.exists(intent_path):
        actual_path = intent_path
    else:
        print(f"Warning: Intent file not found at {intent_path} or {renamed_intent_path}")
        log_justification(loop_id, "loop_controller", "Intent Read Failure", f"Intent file not found at {intent_path} or {renamed_intent_path}", 1.0)
        return None

    intent_data = load_json(actual_path)
    if intent_data and isinstance(intent_data, dict):
        log_justification(loop_id, "loop_controller", "Intent Read Success", f"Successfully loaded intent data from {actual_path}", 1.0)
        return intent_data
    else:
        print(f"Warning: Intent file {actual_path} is invalid.")
        log_justification(loop_id, "loop_controller", "Intent Read Failure", f"Intent file {actual_path} is invalid or empty.", 1.0)
        return None

def read_memory_surface(loop_id, surface_name):
    surface_path = os.path.join(MEMORY_DIR, surface_name)
    print(f"Attempting to read memory surface: {surface_path}")
    data = load_json(surface_path)
    if data is not None:
        print(f"Successfully read memory surface: {surface_name}")
        log_justification(loop_id, "loop_controller", f"Memory Read Success ({surface_name})", f"Successfully read memory surface: {surface_name}", 0.9)
        return True
    else:
        print(f"Failed to read memory surface: {surface_name}")
        log_justification(loop_id, "loop_controller", f"Memory Read Failure ({surface_name})", f"Failed to read memory surface: {surface_name}", 1.0)
        return False

def initialize_loop(loop_id):
    print(f"Initializing loop: {loop_id}")
    log_justification(loop_id, "loop_controller", "Loop Initialization", f"Starting loop {loop_id}", 1.0)
    # Dynamically load agents registered via decorator
    # Modified to gracefully handle errors during loading to bypass issues in unrelated agents
    agents_dir = os.path.join(PROJECT_ROOT, "app/agents")
    for filename in os.listdir(agents_dir):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "base_agent.py":
            module_name = f"app.agents.{filename[:-3]}"
            try:
                __import__(module_name)
                print(f"Dynamically loaded agent module: {module_name}")
            except Exception as e: # Catch any exception during import
                print(f"Warning: Could not dynamically load agent module {module_name}: {e}. Skipping.")
                # Continue loading other agents even if one fails

async def run_loop_steps(loop_id, intent_data):
    """Runs loop steps, including memory read, architect invocation, and mutation guard call."""
    print(f"Running steps for loop: {loop_id}")
    log_justification(loop_id, "loop_controller", "Start Loop Steps", f"Beginning execution of steps for loop {loop_id}", 1.0)
    overall_success = True
    step_message = "Loop steps completed."

    # --- Batch 17.0: Invoke Architect Agent --- 
    # Corrected check to use 'architect_agent' key
    target_agent_key = "architect_agent" 
    if intent_data and target_agent_key in intent_data.get("target_components", []):
        print(f"Intent targets {target_agent_key}. Invoking Architect...")
        log_justification(loop_id, "loop_controller", "Agent Invocation Attempt", f"Attempting to invoke agent: {target_agent_key}", 1.0)
        ArchitectAgentClass = get_agent("architect") # Still use 'architect' key for registry lookup
        if ArchitectAgentClass:
            architect_agent = ArchitectAgentClass()
            # Prepare payload for Architect agent
            architect_payload = ArchitectInstruction(
                loop_id=loop_id,
                intent_description=intent_data.get("intent_description", "No description provided"),
                # Add other relevant fields from intent_data if needed by Architect
            )
            try:
                # Run the architect agent asynchronously
                architect_result = await architect_agent.run(architect_payload)
                if architect_result.status == ResultStatus.SUCCESS:
                    plan_file = architect_result.memory_update.get("plan_file", "Not specified")
                    print(f"Architect agent completed successfully. Proposed plan saved to: {plan_file}")
                    log_justification(loop_id, "loop_controller", "Agent Invocation Success", f"Agent {target_agent_key} completed successfully. Plan saved to {plan_file}", 1.0)
                    # IMPORTANT: Do NOT execute the plan here as per Batch 17.0 requirements.
                else:
                    error_msg = architect_result.error_message
                    print(f"Architect agent failed: {error_msg}")
                    log_justification(loop_id, "loop_controller", "Agent Invocation Failure", f"Agent {target_agent_key} failed: {error_msg}", 1.0)
                    overall_success = False
                    step_message = f"Architect agent failed: {error_msg}"
            except Exception as e:
                error_msg = str(e)
                print(f"Error invoking Architect agent: {error_msg}")
                log_justification(loop_id, "loop_controller", "Agent Invocation Error", f"Exception during {target_agent_key} invocation: {error_msg}", 1.0)
                overall_success = False
                step_message = f"Error invoking Architect agent: {error_msg}"
        else:
            available_agents = list(agent_registry.keys())
            print(f"Error: Agent with key 'architect' not found in registry.")
            print(f"Available agents: {available_agents}") # Print available agents for debugging
            log_justification(loop_id, "loop_controller", "Agent Invocation Failure", f"Agent key 'architect' not found in registry. Available: {available_agents}", 1.0)
            overall_success = False
            step_message = "Architect agent not found in registry."
    else:
        print("Intent does not target Architect agent. Skipping Architect invocation.")
        log_justification(loop_id, "loop_controller", "Agent Invocation Skipped", f"Intent did not target agent key '{target_agent_key}'. Skipping invocation.", 1.0)
    # --- End Batch 17.0 ---

    # --- Batch 16.2: Read from belief_surface.json ---
    if overall_success: # Only proceed if previous steps were successful
        read_success = read_memory_surface(loop_id, "belief_surface.json")
        if not read_success:
            print("Warning: Failed to read belief_surface.json during loop steps.")
            # Decide if this failure should stop the loop or just be a warning
            # overall_success = False 
            # step_message = "Failed to read belief surface."

    # --- Batch 16.3: Call Mutation Guard if intent involves mutation ---
    if overall_success: # Only proceed if previous steps were successful
        # Basic check: Does intent_data exist and contain a non-empty 'parameters' field?
        # A more robust check would look for specific mutation actions.
        if intent_data and intent_data.get("parameters") and intent_data["parameters"]:
            print("Intent suggests mutation. Calling Mutation Guard (Dry Run)...")
            log_justification(loop_id, "loop_controller", "Mutation Guard Check", "Intent suggests mutation. Invoking Mutation Guard.", 1.0)
            mutation_details = {
                "loop_id": loop_id,
                "intent_params": intent_data.get("parameters", {})
                # Add more details about the intended mutation if available
            }
            mutation_allowed = process_mutation_request(mutation_details)
            if not mutation_allowed:
                print("Mutation Guard blocked the mutation (Dry Run).")
                log_justification(loop_id, "loop_controller", "Mutation Guard Rejection", "Mutation Guard blocked the mutation request (Dry Run).", 1.0)
                # In a real scenario, this might halt the loop or change its course.
                # overall_success = False # Uncomment if rejection should fail the loop
                # step_message = "Mutation Guard rejected the request."
            else:
                 log_justification(loop_id, "loop_controller", "Mutation Guard Approval", "Mutation Guard approved the mutation request (Dry Run).", 1.0)
        else:
            print("Intent does not appear to involve mutation. Skipping Mutation Guard.")
            log_justification(loop_id, "loop_controller", "Mutation Guard Skipped", "Intent does not suggest mutation. Skipping Mutation Guard.", 1.0)
    # --- End Batch 16.3 ---

    log_justification(loop_id, "loop_controller", "End Loop Steps", f"Finished execution of steps for loop {loop_id}. Overall success: {overall_success}", 1.0)
    return overall_success, step_message

def finalize_loop(loop_id, intent_description, status, message):
    print(f"Finalizing loop: {loop_id} with status: {status}")
    if status:
        log_loop_summary(loop_id, intent_description, "success")
        log_justification(loop_id, "loop_controller", "Loop Finalization (Success)", f"Loop {loop_id} completed successfully.", 1.0)
    else:
        log_rejection(loop_id, message)
        log_loop_summary(loop_id, intent_description, "rejected")
        log_justification(loop_id, "loop_controller", "Loop Finalization (Rejected)", f"Loop {loop_id} rejected. Reason: {message}", 1.0)
    print(f"Loop {loop_id} finished.")

async def main():
    parser = argparse.ArgumentParser(description="Loop Controller with Architect Integration")
    parser.add_argument("--loop_id", required=True, help="Unique ID for the loop execution")
    parser.add_argument("--reject", action='store_true', help="Flag to simulate a rejection")
    parser.add_argument("--reason", default="Simulated rejection", help="Reason for rejection if --reject is used")
    args = parser.parse_args()

    # Initialize loop first to load agents before reading intent
    initialize_loop(args.loop_id)

    intent_data = get_loop_intent_data(args.loop_id)
    intent_description = intent_data.get("intent_description", "Intent data not found or invalid") if intent_data else "Intent data not found or invalid"
    print(f"Loop Intent: {intent_description}")

    if args.reject:
        success = False
        result_message = args.reason
        log_justification(args.loop_id, "loop_controller", "Simulated Rejection", f"Loop {args.loop_id} forced to reject via command line argument.", 1.0)
    else:
        # Pass full intent_data to run_loop_steps and run it asynchronously
        success, result_message = await run_loop_steps(args.loop_id, intent_data)

    finalize_loop(args.loop_id, intent_description, success, result_message)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

