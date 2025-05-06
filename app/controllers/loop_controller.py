#!/usr/bin/env python3.11
import json
import argparse
import os
import sys
import asyncio
import time # Batch 20.3: Added for polling timeout
from datetime import datetime, timedelta # Batch 20.3: Added for timeout calculation

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
from app.schemas.agent_input.architect_agent_input import ArchitectInstruction
from app.schemas.agent_output.architect_agent_output import ArchitectPlanResult
from app.schemas.agent_input.critic_agent_input import CriticPlanEvaluationInput
from app.schemas.agent_output.critic_agent_output import CriticPlanEvaluationResult
from app.schemas.agent_input.pessimist_agent_input import PessimistRiskAssessmentInput
from app.schemas.agent_output.pessimist_agent_output import PessimistRiskAssessmentResult
from app.utils.status import ResultStatus # Import status enum
from app.utils.justification_logger import log_justification # Import justification logging utility

# Define paths relative to PROJECT_ROOT
LOOP_SUMMARY_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json")
REJECTION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary_rejection_log.json")
LOOP_INTENT_DIR = os.path.join(PROJECT_ROOT, "app/memory/")
MEMORY_DIR = os.path.join(PROJECT_ROOT, "app/memory/")
# --- Batch 20.3: Operator Review Paths ---
REVIEW_QUEUE_DIR = "/home/ubuntu/review_queue/"
OPERATOR_INPUT_DIR = "/home/ubuntu/personal-ai-agent/operator_input/" # Corrected path in previous step
OPERATOR_OVERRIDE_LOG_PATH = os.path.join(MEMORY_DIR, "operator_override_log.json")
# --- End Batch 20.3 ---

# --- Batch 20.3: Operator Review Configuration ---
OPERATOR_REVIEW_TIMEOUT_SECONDS = 300 # 5 minutes
OPERATOR_REVIEW_POLL_INTERVAL_SECONDS = 5
# Define which actions/intents require operator review (example: all mutations for now)
# REQUIRES_OPERATOR_REVIEW = lambda intent_data: "mutation_request" in intent_data.get("intent_params", {}) # Removed incorrect lambda
# --- End Batch 20.3 ---

def load_json(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content:
                # Handle empty files based on expected structure
                if os.path.basename(path).startswith("loop_intent"):
                    return None
                elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json", "debt_token_budget.json", "agent_trust_score.json"]:
                     return {}
                else:
                    # Default to list for logs
                    return [] 
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: File not found at {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json", "debt_token_budget.json", "agent_trust_score.json"]:
             return {}
        else:
            return []
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json", "debt_token_budget.json", "agent_trust_score.json"]:
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

# --- Batch 20.3: Operator Override Log Function --- 
def log_operator_override(loop_id, decision, reason, details):
    override_log = load_json(OPERATOR_OVERRIDE_LOG_PATH)
    if not isinstance(override_log, list):
        print(f"Warning: {OPERATOR_OVERRIDE_LOG_PATH} is not a list. Reinitializing.")
        override_log = []
    entry = {
        "log_id": f"op_{loop_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
        "loop_id": loop_id,
        "timestamp": datetime.utcnow().isoformat(),
        "decision": decision, # 'approved', 'rejected', 'timeout', 'invalid_input'
        "reason": reason,
        "reviewed_details": details
    }
    override_log.append(entry)
    save_json(override_log, OPERATOR_OVERRIDE_LOG_PATH)
    print(f"Logged operator decision for loop {loop_id}: {decision}")
# --- End Batch 20.3 ---

# --- Batch 20.3: Operator Review Gate Function --- 
def perform_operator_review(loop_id, intent_data):
    """Handles the blocking operator review process."""
    print(f"Loop {loop_id}: Entering Operator Review Gate.")
    log_justification(loop_id, "loop_controller", "Operator Review Pending", "Mutation requires operator review. Blocking execution.", 1.0)
    
    # 1. Write request to review queue
    review_file_path = os.path.join(REVIEW_QUEUE_DIR, f"review_request_{loop_id}.json")
    try:
        os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True)
        save_json(intent_data, review_file_path)
        print(f"Loop {loop_id}: Review request written to {review_file_path}")
    except Exception as e:
        reason = f"Failed to write review request to queue: {e}"
        print(f"Loop {loop_id}: Error - {reason}")
        log_operator_override(loop_id, "rejected", reason, intent_data)
        log_justification(loop_id, "loop_controller", "Operator Review Failed (Queue Write)", reason, 1.0)
        return False, reason # Reject if cannot write to queue

    # 2. Poll for operator input
    decision_file_path = os.path.join(OPERATOR_INPUT_DIR, f"review_decision_{loop_id}.json")
    start_time = datetime.utcnow()
    timeout_time = start_time + timedelta(seconds=OPERATOR_REVIEW_TIMEOUT_SECONDS)
    
    print(f"Loop {loop_id}: Polling for operator decision at {decision_file_path} (Timeout: {OPERATOR_REVIEW_TIMEOUT_SECONDS}s)")
    while datetime.utcnow() < timeout_time:
        if os.path.exists(decision_file_path):
            print(f"Loop {loop_id}: Found decision file: {decision_file_path}")
            decision_data = load_json(decision_file_path)
            if decision_data and isinstance(decision_data, dict):
                decision = decision_data.get("decision", "").lower()
                reason = decision_data.get("reason", "No reason provided.")
                
                if decision == "approved":
                    print(f"Loop {loop_id}: Operator approved. Reason: {reason}")
                    log_operator_override(loop_id, "approved", reason, intent_data)
                    log_justification(loop_id, "loop_controller", "Operator Review Approved", f"Operator approved mutation. Reason: {reason}", 1.0)
                    # Clean up files
                    try: os.remove(review_file_path) 
                    except OSError: pass
                    try: os.remove(decision_file_path) 
                    except OSError: pass
                    return True, "Operator approved."
                elif decision == "rejected":
                    print(f"Loop {loop_id}: Operator rejected. Reason: {reason}")
                    log_operator_override(loop_id, "rejected", reason, intent_data)
                    log_justification(loop_id, "loop_controller", "Operator Review Rejected", f"Operator rejected mutation. Reason: {reason}", 1.0)
                    # Clean up files
                    try: os.remove(review_file_path) 
                    except OSError: pass
                    try: os.remove(decision_file_path) 
                    except OSError: pass
                    return False, f"Operator rejected: {reason}"
                else:
                    reason = f"Invalid decision ('{decision}') in decision file: {decision_file_path}"
                    print(f"Loop {loop_id}: Error - {reason}")
                    log_operator_override(loop_id, "invalid_input", reason, intent_data)
                    log_justification(loop_id, "loop_controller", "Operator Review Failed (Invalid Input)", reason, 1.0)
                    # Clean up files
                    try: os.remove(review_file_path) 
                    except OSError: pass
                    # Keep invalid decision file for inspection? Or remove?
                    # try: os.remove(decision_file_path) 
                    # except OSError: pass
                    return False, reason
            else:
                reason = f"Invalid or empty decision file: {decision_file_path}"
                print(f"Loop {loop_id}: Error - {reason}")
                log_operator_override(loop_id, "invalid_input", reason, intent_data)
                log_justification(loop_id, "loop_controller", "Operator Review Failed (Invalid File)", reason, 1.0)
                # Clean up files
                try: os.remove(review_file_path) 
                except OSError: pass
                # Keep invalid decision file for inspection?
                # try: os.remove(decision_file_path) 
                # except OSError: pass
                return False, reason
        
        # Wait before polling again
        time.sleep(OPERATOR_REVIEW_POLL_INTERVAL_SECONDS)

    # 3. Handle Timeout
    reason = f"Operator review timed out after {OPERATOR_REVIEW_TIMEOUT_SECONDS} seconds."
    print(f"Loop {loop_id}: Timeout - {reason}")
    log_operator_override(loop_id, "timeout", reason, intent_data)
    log_justification(loop_id, "loop_controller", "Operator Review Timeout", reason, 1.0)
    # Clean up request file on timeout
    try: os.remove(review_file_path) 
    except OSError: pass
    return False, reason
# --- End Batch 20.3 ---

def initialize_loop(loop_id):
    print(f"Initializing loop: {loop_id}")
    log_justification(loop_id, "loop_controller", "Loop Initialization", f"Starting loop {loop_id}", 1.0)
    # Dynamically load agents registered via decorator
    agents_dir = os.path.join(PROJECT_ROOT, "app/agents")
    for filename in os.listdir(agents_dir):
        if filename.endswith(".py") and filename != "__init__.py" and filename != "base_agent.py":
            module_name = f"app.agents.{filename[:-3]}"
            try:
                __import__(module_name)
                print(f"Dynamically loaded agent module: {module_name}")
            except Exception as e:
                print(f"Warning: Could not dynamically load agent module {module_name}: {e}. Skipping.")

async def run_loop_steps(loop_id, intent_data):
    """Runs loop steps, including agent invocations and checks."""
    print(f"Running steps for loop: {loop_id}")
    log_justification(loop_id, "loop_controller", "Start Loop Steps", f"Beginning execution of steps for loop {loop_id}", 1.0)
    overall_success = True
    step_message = "Loop steps completed."
    architect_plan_file = None # Store plan file path
    critic_approved = None # Store critic decision
    operator_approved = None # Batch 20.3: Store operator decision
    # requires_review = False # Batch 20.3: Flag if review was needed # Removed incorrect variable

    # --- Batch 17.0: Invoke Architect Agent --- 
    # ... (existing Architect logic) ...
    target_architect_key = "architect_agent"
    if intent_data and target_architect_key in intent_data.get("target_components", []):
        print(f"Intent targets {target_architect_key}. Invoking Architect...")
        log_justification(loop_id, "loop_controller", "Agent Invocation Attempt", f"Attempting to invoke agent: {target_architect_key}", 1.0)
        ArchitectAgentClass = get_agent("architect")
        if ArchitectAgentClass:
            architect_agent = ArchitectAgentClass()
            architect_payload = ArchitectInstruction(
                loop_id=loop_id,
                intent_description=intent_data.get("intent_description", "No description provided"),
            )
            try:
                architect_result = await architect_agent.run(architect_payload)
                if architect_result.status == ResultStatus.SUCCESS:
                    architect_plan_file = architect_result.memory_update.get("plan_file") # Get plan file path
                    if architect_plan_file:
                        print(f"Architect agent completed successfully. Proposed plan saved to: {architect_plan_file}")
                        log_justification(loop_id, "loop_controller", "Agent Invocation Success (Architect)", f"Agent {target_architect_key} completed successfully. Plan saved to {architect_plan_file}", 1.0)
                    else:
                        print(f"Architect agent completed but did not return a plan file path.")
                        log_justification(loop_id, "loop_controller", "Agent Invocation Warning (Architect)", f"Agent {target_architect_key} completed but did not return a plan file path.", 0.5)
                else:
                    print(f"Architect agent failed: {architect_result.error_message}")
                    log_justification(loop_id, "loop_controller", "Agent Invocation Failure (Architect)", f"Agent {target_architect_key} failed: {architect_result.error_message}", 1.0)
                    overall_success = False
                    step_message = f"Architect agent failed: {architect_result.error_message}"
            except Exception as e:
                print(f"Error invoking Architect agent: {e}")
                log_justification(loop_id, "loop_controller", "Agent Invocation Error (Architect)", f"Error invoking agent {target_architect_key}: {e}", 1.0)
                overall_success = False
                step_message = f"Error invoking Architect agent: {e}"
        else:
            print(f"Architect agent not found in registry.")
            log_justification(loop_id, "loop_controller", "Agent Invocation Failure (Architect)", f"Agent {target_architect_key} not found in registry.", 1.0)
            overall_success = False
            step_message = f"Architect agent not found."
    else:
        print("Intent does not target Architect agent. Skipping Architect invocation.")
        log_justification(loop_id, "loop_controller", "Agent Invocation Skipped (Architect)", "Intent does not target Architect agent.", 0.1)

    # --- Batch 18.0: Invoke Critic Agent (if Architect ran) --- 
    # ... (existing Critic logic) ...
    target_critic_key = "critic_agent"
    if overall_success and architect_plan_file and target_critic_key in intent_data.get("target_components", []):
        print(f"Architect plan exists ({architect_plan_file}). Invoking Critic...")
        log_justification(loop_id, "loop_controller", "Agent Invocation Attempt", f"Attempting to invoke agent: {target_critic_key}", 1.0)
        CriticAgentClass = get_agent("Critic") # Use correct key 'Critic'
        if CriticAgentClass:
            critic_agent = CriticAgentClass()
            critic_payload = CriticPlanEvaluationInput(
                loop_id=loop_id,
                plan_file_path=architect_plan_file,
                intent_description=intent_data.get("intent_description", "No description provided")
            )
            try:
                critic_result = await critic_agent.run(critic_payload)
                if critic_result.status == ResultStatus.SUCCESS:
                    critic_approved = critic_result.approved
                    print(f"Critic agent completed. Approved: {critic_approved}. Justification: {critic_result.justification}")
                    log_justification(loop_id, "loop_controller", "Agent Invocation Success (Critic)", f"Agent {target_critic_key} completed. Approved: {critic_approved}. Justification: {critic_result.justification}", 1.0)
                    if not critic_approved:
                        overall_success = False
                        step_message = f"Critic rejected the plan: {critic_result.justification}"
                        log_justification(loop_id, "loop_controller", "Plan Rejected (Critic)", f"Critic rejected the plan: {critic_result.justification}", 1.0)
                else:
                    print(f"Critic agent failed: {critic_result.error_message}")
                    log_justification(loop_id, "loop_controller", "Agent Invocation Failure (Critic)", f"Agent {target_critic_key} failed: {critic_result.error_message}", 1.0)
                    overall_success = False
                    step_message = f"Critic agent failed: {critic_result.error_message}"
            except Exception as e:
                print(f"Error invoking Critic agent: {e}")
                log_justification(loop_id, "loop_controller", "Agent Invocation Error (Critic)", f"Error invoking agent {target_critic_key}: {e}", 1.0)
                overall_success = False
                step_message = f"Error invoking Critic agent: {e}"
        else:
            print(f"Critic agent not found in registry.")
            log_justification(loop_id, "loop_controller", "Agent Invocation Failure (Critic)", f"Agent {target_critic_key} not found in registry.", 1.0)
            overall_success = False
            step_message = f"Critic agent not found."
    elif target_critic_key in intent_data.get("target_components", []):
        print("Critic invocation skipped (Architect did not run or failed, or no plan file)." if overall_success else "Critic invocation skipped due to prior failure.")
        log_justification(loop_id, "loop_controller", "Agent Invocation Skipped (Critic)", "Critic invocation skipped (Architect did not run or failed, or no plan file)." if overall_success else "Critic invocation skipped due to prior failure.", 0.1)

    # --- Batch 20.3: Operator Review Gate --- 
    # Check if operator review is required *based on the intent flag*
    if overall_success and intent_data.get("requires_operator_review", False):
        operator_approved, operator_message = perform_operator_review(loop_id, intent_data)
        if not operator_approved:
            overall_success = False
            step_message = f"Operator review resulted in rejection or failure: {operator_message}. Halting loop {loop_id}."
            print(step_message)
            log_justification(loop_id, "loop_controller", "Loop Halted (Operator Review)", step_message, 1.0)
    elif overall_success:
        print(f"Loop {loop_id}: Operator review not required by intent. Skipping gate.")
        log_justification(loop_id, "loop_controller", "Operator Review Skipped", "Operator review not required by intent.", 0.1)
    # --- End Batch 20.3 (Modified for Flag Check) ---

    # --- Batch 19.1: Post-Mutation Validation (Placeholder) ---
    # ... (existing validation logic) ...

    # --- Batch 19.0: Mutation Execution (if applicable and all checks passed) ---
    if overall_success and "mutation_request" in intent_data.get("intent_params", {}):
        print(f"Loop {loop_id}: Proceeding to mutation guard...")
        log_justification(loop_id, "loop_controller", "Mutation Guard Invocation", "Attempting to process mutation request via mutation guard.", 1.0)
        try:
            # Pass the full intent_data to mutation guard for context (like requires_operator_review flag for Batch 20.4 check)
            mutation_success, mutated_files, mutation_message = await process_mutation_request(loop_id, intent_data)
            if not mutation_success:
                overall_success = False
                step_message = f"Mutation Guard rejected or failed the mutation: {mutation_message}"
                print(f"Loop {loop_id}: {step_message}")
                log_justification(loop_id, "loop_controller", "Mutation Rejected/Failed", step_message, 1.0)
            else:
                print(f"Loop {loop_id}: Mutation Guard approved and executed mutation successfully. Message: {mutation_message}")
                log_justification(loop_id, "loop_controller", "Mutation Success", f"Mutation Guard approved and executed mutation. Message: {mutation_message}", 1.0)
                # Potentially trigger post-mutation validation here if needed
        except Exception as e:
            print(f"Loop {loop_id}: Error during mutation processing: {e}")
            log_justification(loop_id, "loop_controller", "Mutation Error", f"Error during mutation processing: {e}", 1.0)
            overall_success = False
            step_message = f"Error during mutation processing: {e}"
    elif "mutation_request" in intent_data.get("intent_params", {}):
        print(f"Loop {loop_id}: Mutation skipped due to prior failure or rejection.")
        log_justification(loop_id, "loop_controller", "Mutation Skipped", "Mutation skipped due to prior failure or rejection.", 0.1)

    # --- Batch 20.3: Basic Blame Attribution on Failure --- 
    if not overall_success:
        print(f"Loop {loop_id} failed. Attempting blame attribution...")
        log_justification(loop_id, "loop_controller", "Blame Attribution Attempt", "Loop failed, attempting to attribute blame.", 0.8)
        blame_log_path = os.path.join(MEMORY_DIR, "agent_blame_log.json")
        blame_log = load_json(blame_log_path)
        if not isinstance(blame_log, list):
            print(f"Warning: {blame_log_path} is not a list. Reinitializing.")
            blame_log = []
        
        blame_reason = step_message # Use the last failure message as the reason
        suspected_agent = "unknown"
        # Simple heuristic: If Critic rejected, blame Critic. If Operator rejected/timed out, blame Operator process.
        if "Critic rejected" in blame_reason:
            suspected_agent = "Critic"
        elif "Operator rejected" in blame_reason or "Operator review timed out" in blame_reason:
            suspected_agent = "OperatorReviewProcess"
        elif "Architect agent failed" in blame_reason:
            suspected_agent = "Architect"
        elif "Mutation Guard rejected" in blame_reason or "Mutation failed" in blame_reason:
             # Try to get agent from mutation details if possible
             mutation_details = intent_data.get("intent_params", {}).get("mutation_request", {})
             suspected_agent = mutation_details.get("responsible_agent_id", "MutationGuard")
        elif "agent not found" in blame_reason:
             if "Architect" in blame_reason: suspected_agent = "ArchitectRegistry"
             elif "Critic" in blame_reason: suspected_agent = "CriticRegistry"
             else: suspected_agent = "AgentRegistry"
        else:
            suspected_agent = "loop_controller" # Default blame

        blame_entry = {
            "blame_id": f"blame_{loop_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            "loop_id": loop_id,
            "timestamp": datetime.utcnow().isoformat(),
            "suspected_agent_id": suspected_agent,
            "reason": blame_reason,
            "confidence_score": 0.6 # Default confidence
        }
        blame_log.append(blame_entry)
        save_json(blame_log, blame_log_path)
        print(f"Logged potential blame for loop {loop_id} to {blame_log_path}")
        log_justification(loop_id, "loop_controller", "Blame Attributed", f"Attributed blame to {suspected_agent}. Reason: {blame_reason}", 0.8)
    # --- End Batch 20.3 ---

    print(f"Finished steps for loop: {loop_id}. Overall Success: {overall_success}")
    log_justification(loop_id, "loop_controller", "End Loop Steps", f"Finished execution of steps for loop {loop_id}. Success: {overall_success}", 1.0)
    return overall_success

async def main(loop_id):
    initialize_loop(loop_id)
    intent_data = get_loop_intent_data(loop_id)
    
    if not intent_data:
        print(f"Error: Could not load intent data for loop {loop_id}. Aborting.")
        log_loop_summary(loop_id, "Unknown Intent", "Failed - Intent Load Error")
        log_rejection(loop_id, "Failed to load intent data.")
        log_justification(loop_id, "loop_controller", "Loop Aborted", "Failed to load intent data.", 1.0)
        return

    intent_description = intent_data.get("intent_name", "No description provided")
    print(f"Processing loop {loop_id} with intent: {intent_description}")
    log_justification(loop_id, "loop_controller", "Process Intent", f"Processing intent: {intent_description}", 1.0)

    # Read relevant memory surfaces
    read_memory_surface(loop_id, "belief_surface.json")
    read_memory_surface(loop_id, "promethios_creed.json")

    # Run the main loop steps
    success = await run_loop_steps(loop_id, intent_data)

    # Finalize loop
    print(f"Finalizing loop: {loop_id} with status: {success}")
    log_justification(loop_id, "loop_controller", "Loop Finalization", f"Finalizing loop {loop_id}. Overall Success: {success}", 1.0)
    log_loop_summary(loop_id, intent_description, "Success" if success else "Failure")
    if not success:
        log_rejection(loop_id, "Loop execution failed.") # Generic reason, specific reason logged during steps

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a specific loop controller process.")
    parser.add_argument("--loop_id", required=True, help="The ID of the loop to process.")
    args = parser.parse_args()
    
    asyncio.run(main(args.loop_id))

