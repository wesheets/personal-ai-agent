#!/usr/bin/env python3.11
import json
import argparse
import os
import sys
import asyncio
import time # Batch 20.3: Added for polling timeout
from datetime import datetime, timedelta, timezone # Batch 20.3: Added for timeout calculation; Batch 21.2: Added timezone

# Get the directory of the current script (loop_controller.py)
CONTROLLER_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the 'app' directory
APP_DIR = os.path.dirname(CONTROLLER_DIR)
# Get the project root directory (one level above 'app')
PROJECT_ROOT = os.path.dirname(APP_DIR)

# Add the project root directory to sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Batch 21.4: Explicitly import app.agents to trigger __init__.py and agent registration ---
import app.agents
# --- End Batch 21.4 ---

# Now imports relative to the project root (app.*) should work
from app.validators.mutation_guard import process_mutation_request
from app.core.agent_registry import get_agent, AGENT_REGISTRY # Import agent registry function and registry itself for agent loading
# --- Batch 21.5 Remediation: Import specific agent input schemas --- 
# TODO: Replace with dynamic loading based on agent definition
from app.schemas.agents.belief_manager.belief_manager_schemas import BeliefManagerInput
# --- End Remediation ---
from app.schemas.agent_input.architect_agent_input import ArchitectInstruction
from app.schemas.agent_output.architect_agent_output import ArchitectPlanResult
from app.schemas.agent_input.critic_agent_input import CriticPlanEvaluationInput
from app.schemas.agent_output.critic_agent_output import CriticPlanEvaluationResult
from app.schemas.agent_input.pessimist_agent_input import PessimistRiskAssessmentInput
from app.schemas.agent_output.pessimist_agent_output import PessimistRiskAssessmentResult
# --- Batch 21.5 Remediation: Import AgentResult and ResultStatus --- 
from app.schemas.core.agent_result import AgentResult, ResultStatus # Import status enum and result model
# --- End Remediation ---
from app.utils.justification_logger import log_justification # Import justification logging utility
# --- Batch 21.5: Belief Editing Imports --- 
from app.schemas.agents.belief_manager.belief_manager_schemas import BeliefChangeProposal
from app.validators.belief_updater import apply_belief_update
# --- End Batch 21.5 ---

# Define paths relative to PROJECT_ROOT
LOOP_SUMMARY_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json")
REJECTION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary_rejection_log.json")
LOOP_INTENT_DIR = os.path.join(PROJECT_ROOT, "app/memory/")
MEMORY_DIR = os.path.join(PROJECT_ROOT, "app/memory/")
# --- Batch 20.3: Operator Review Paths ---
REVIEW_QUEUE_DIR = "/home/ubuntu/review_queue/"
OPERATOR_INPUT_DIR = "/home/ubuntu/operator_input/" # Corrected path
OPERATOR_OVERRIDE_LOG_PATH = os.path.join(MEMORY_DIR, "operator_override_log.json")
# --- End Batch 20.3 ---
# --- Batch 21.2: Complexity Metrics Path ---
COMPLEXITY_METRICS_PATH = os.path.join(MEMORY_DIR, "complexity_metrics.json")
# --- End Batch 21.2 ---
# --- Batch 21.2: Belief Surface Path ---
BELIEF_SURFACE_PATH = os.path.join(MEMORY_DIR, "belief_surface.json")
# --- End Batch 21.2 ---
# --- Batch 21.4: Agent Cognitive Budget Path ---
AGENT_BUDGET_PATH = os.path.join(MEMORY_DIR, "agent_cognitive_budget.json")
# --- End Batch 21.4 ---
# --- Batch 21.5: Proposed Belief Change Path --- 
PROPOSED_BELIEF_CHANGE_DIR = os.path.join(MEMORY_DIR, "proposed_belief_changes/")
# --- End Batch 21.5 ---

# --- Batch 20.3: Operator Review Configuration ---
OPERATOR_REVIEW_TIMEOUT_SECONDS = 300 # 5 minutes
OPERATOR_REVIEW_POLL_INTERVAL_SECONDS = 5
# --- End Batch 20.3 ---

# --- Batch 21.4: Cognitive Budget Configuration --- 
AGENT_EXECUTION_COST = 5.0
AGENT_ERROR_PENALTY = 10.0
# --- End Batch 21.4 ---

def load_json(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content:
                # Handle empty files based on expected structure
                if os.path.basename(path).startswith("loop_intent"):
                    return None
                elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json", "debt_token_budget.json", "agent_trust_score.json", "complexity_metrics.json", "agent_cognitive_budget.json", "operator_override_log.json"]:
                     return {}
                else:
                    # Default to list for logs
                    return []
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: File not found at {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json", "debt_token_budget.json", "agent_trust_score.json", "complexity_metrics.json", "agent_cognitive_budget.json", "operator_override_log.json"]:
             return {}
        else:
            return []
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        elif os.path.basename(path) in ["belief_surface.json", "promethios_creed.json", "debt_token_budget.json", "agent_trust_score.json", "complexity_metrics.json", "agent_cognitive_budget.json", "operator_override_log.json"]:
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": reason
    }
    rejection_log.append(entry)
    save_json(rejection_log, REJECTION_LOG_PATH)

def get_loop_intent_data(loop_id):
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

def log_operator_override(loop_id, decision, reason, details):
    override_log = load_json(OPERATOR_OVERRIDE_LOG_PATH)
    # Ensure it's a list, initialize if not
    if not isinstance(override_log, list):
        print(f"Warning: {OPERATOR_OVERRIDE_LOG_PATH} is not a list. Reinitializing.")
        override_log = []
        
    entry = {
        "log_id": f"op_{loop_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "loop_id": loop_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": decision, # 'approved', 'rejected', 'timeout', 'invalid_input'
        "reason": reason,
        "reviewed_details": details
    }
    override_log.append(entry)
    save_json(override_log, OPERATOR_OVERRIDE_LOG_PATH)
    print(f"Logged operator decision for loop {loop_id}: {decision}")
    return entry["log_id"] # Return the log ID for reference

def perform_operator_review(loop_id, review_data, review_type="mutation"):
    """Handles the blocking operator review process. Review data is the data needing review."""
    print(f"Loop {loop_id}: Entering Operator Review Gate for {review_type}.")
    log_justification(loop_id, "loop_controller", f"Operator Review Pending ({review_type})", f"{review_type.capitalize()} requires operator review. Blocking execution.", 1.0)

    # 1. Write request to review queue
    review_file_path = os.path.join(REVIEW_QUEUE_DIR, f"review_request_{loop_id}_{review_type}.json")
    try:
        os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True)
        save_json(review_data, review_file_path)
        print(f"Loop {loop_id}: Review request written to {review_file_path}")
    except Exception as e:
        reason = f"Failed to write review request to queue: {e}"
        print(f"Loop {loop_id}: Error - {reason}")
        log_id = log_operator_override(loop_id, "rejected", reason, review_data)
        log_justification(loop_id, "loop_controller", f"Operator Review Failed ({review_type} Queue Write)", reason, 1.0)
        return False, reason, log_id # Reject if cannot write to queue

    # 2. Poll for operator input
    decision_file_path = os.path.join(OPERATOR_INPUT_DIR, f"review_decision_{loop_id}_{review_type}.json")
    start_time = datetime.now(timezone.utc)
    timeout_time = start_time + timedelta(seconds=OPERATOR_REVIEW_TIMEOUT_SECONDS)

    print(f"Loop {loop_id}: Polling for operator decision at {decision_file_path} (Timeout: {OPERATOR_REVIEW_TIMEOUT_SECONDS}s)")
    while datetime.now(timezone.utc) < timeout_time:
        if os.path.exists(decision_file_path):
            print(f"Loop {loop_id}: Found decision file: {decision_file_path}")
            decision_data = load_json(decision_file_path)
            if decision_data and isinstance(decision_data, dict):
                decision = decision_data.get("decision", "").lower()
                reason = decision_data.get("reason", "No reason provided.")

                if decision == "approved":
                    print(f"Loop {loop_id}: Operator approved {review_type}. Reason: {reason}")
                    log_id = log_operator_override(loop_id, "approved", reason, review_data)
                    log_justification(loop_id, "loop_controller", f"Operator Review Approved ({review_type})", f"Operator approved {review_type}. Reason: {reason}", 1.0)
                    # Clean up files
                    try: os.remove(review_file_path)
                    except OSError: pass
                    try: os.remove(decision_file_path)
                    except OSError: pass
                    return True, "Operator approved.", log_id
                elif decision == "rejected":
                    print(f"Loop {loop_id}: Operator rejected {review_type}. Reason: {reason}")
                    log_id = log_operator_override(loop_id, "rejected", reason, review_data)
                    log_justification(loop_id, "loop_controller", f"Operator Review Rejected ({review_type})", f"Operator rejected {review_type}. Reason: {reason}", 1.0)
                    # Clean up files
                    try: os.remove(review_file_path)
                    except OSError: pass
                    try: os.remove(decision_file_path)
                    except OSError: pass
                    return False, f"Operator rejected: {reason}", log_id
                else:
                    reason = f"Invalid decision ('{decision}') in decision file: {decision_file_path}"
                    print(f"Loop {loop_id}: Error - {reason}")
                    log_id = log_operator_override(loop_id, "invalid_input", reason, review_data)
                    log_justification(loop_id, "loop_controller", f"Operator Review Failed ({review_type} Invalid Input)", reason, 1.0)
                    # Clean up files
                    try: os.remove(review_file_path)
                    except OSError: pass
                    # Keep invalid decision file for inspection? Or remove?
                    # try: os.remove(decision_file_path)
                    # except OSError: pass
                    return False, reason, log_id
            else:
                reason = f"Invalid or empty decision file: {decision_file_path}"
                print(f"Loop {loop_id}: Error - {reason}")
                log_id = log_operator_override(loop_id, "invalid_input", reason, review_data)
                log_justification(loop_id, "loop_controller", f"Operator Review Failed ({review_type} Invalid File)", reason, 1.0)
                # Clean up files
                try: os.remove(review_file_path)
                except OSError: pass
                # Keep invalid decision file for inspection?
                # try: os.remove(decision_file_path)
                # except OSError: pass
                return False, reason, log_id

        # Wait before polling again
        time.sleep(OPERATOR_REVIEW_POLL_INTERVAL_SECONDS)

    # 3. Handle Timeout
    reason = f"Operator review for {review_type} timed out after {OPERATOR_REVIEW_TIMEOUT_SECONDS} seconds."
    print(f"Loop {loop_id}: Timeout - {reason}")
    log_id = log_operator_override(loop_id, "timeout", reason, review_data)
    log_justification(loop_id, "loop_controller", f"Operator Review Timeout ({review_type})", reason, 1.0)
    # Clean up request file on timeout
    try: os.remove(review_file_path)
    except OSError: pass
    return False, reason, log_id

def update_complexity_metrics(loop_id, duration_sec=None, tokens=None, agent_calls=None, mutation_complexity=None):
    metrics_data = load_json(COMPLEXITY_METRICS_PATH)
    if not isinstance(metrics_data, dict) or 'metrics' not in metrics_data:
        print(f"Warning: {COMPLEXITY_METRICS_PATH} is invalid or uninitialized. Reinitializing.")
        metrics_data = {"metrics": {"average_loop_duration_sec": None, "average_tokens_per_loop": None, "average_agent_calls_per_loop": None, "mutation_request_complexity_score": None}, "last_updated": None}

    updated = False
    current_metrics = metrics_data.get('metrics', {})

    if duration_sec is not None:
        prev_avg_duration = current_metrics.get("average_loop_duration_sec")
        if prev_avg_duration is None:
            current_metrics["average_loop_duration_sec"] = duration_sec
        else:
            # Simplistic: just update with latest for now
            current_metrics["average_loop_duration_sec"] = duration_sec
        updated = True
        print(f"Loop {loop_id}: Updated loop duration metric to {duration_sec:.2f}s")
        log_justification(loop_id, "loop_controller", "Complexity Metric Update", f"Loop duration updated to {duration_sec:.2f}s", 0.8)

    if tokens is not None:
        # TODO: Implement token tracking and averaging
        current_metrics["average_tokens_per_loop"] = tokens # Placeholder
        updated = True
        print(f"Loop {loop_id}: Updated token usage metric (placeholder: {tokens})")
        log_justification(loop_id, "loop_controller", "Complexity Metric Update", f"Token usage updated (placeholder: {tokens})", 0.8)

    if agent_calls is not None:
        prev_avg_calls = current_metrics.get("average_agent_calls_per_loop")
        if prev_avg_calls is None:
            current_metrics["average_agent_calls_per_loop"] = agent_calls
        else:
            # Simplistic: just update with latest for now
            current_metrics["average_agent_calls_per_loop"] = agent_calls
        updated = True
        print(f"Loop {loop_id}: Updated agent calls metric to {agent_calls}")
        log_justification(loop_id, "loop_controller", "Complexity Metric Update", f"Agent calls updated to {agent_calls}", 0.8)

    if mutation_complexity is not None:
        # TODO: Implement mutation complexity tracking and averaging
        current_metrics["mutation_request_complexity_score"] = mutation_complexity # Placeholder
        updated = True
        print(f"Loop {loop_id}: Updated mutation complexity metric (placeholder: {mutation_complexity})")
        log_justification(loop_id, "loop_controller", "Complexity Metric Update", f"Mutation complexity updated (placeholder: {mutation_complexity})", 0.8)

    if updated:
        metrics_data["metrics"] = current_metrics
        metrics_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        save_json(metrics_data, COMPLEXITY_METRICS_PATH)
        print(f"Loop {loop_id}: Complexity metrics saved.")

def update_agent_budget(loop_id, agent_key, cost, penalty=0.0):
    """Loads, updates, and saves the cognitive budget for a specific agent."""
    budget_data = load_json(AGENT_BUDGET_PATH)
    if not isinstance(budget_data, dict):
        print(f"Warning: {AGENT_BUDGET_PATH} is invalid or uninitialized. Reinitializing.")
        budget_data = {"agents": {}, "last_updated": None}

    agent_budgets = budget_data.get("agents", {})
    current_budget = agent_budgets.get(agent_key, {"remaining_budget": 100.0, "total_spent": 0.0, "last_update_loop": None})

    total_deduction = cost + penalty
    current_budget["remaining_budget"] -= total_deduction
    current_budget["total_spent"] += total_deduction
    current_budget["last_update_loop"] = loop_id

    agent_budgets[agent_key] = current_budget
    budget_data["agents"] = agent_budgets
    budget_data["last_updated"] = datetime.now(timezone.utc).isoformat()

    save_json(budget_data, AGENT_BUDGET_PATH)
    print(f"Loop {loop_id}: Updated budget for agent '{agent_key}'. Cost: {cost}, Penalty: {penalty}. Remaining: {current_budget['remaining_budget']:.2f}")
    log_justification(loop_id, "loop_controller", f"Budget Update ({agent_key})", f"Cost: {cost}, Penalty: {penalty}. Remaining: {current_budget['remaining_budget']:.2f}", 0.8)

async def execute_loop(loop_id):
    start_time = time.time() # Batch 21.2: Start timer
    agent_call_count = 0 # Batch 21.2: Initialize agent call counter
    print(f"\n--- Starting Loop: {loop_id} ---")

    # 1. Load Loop Intent
    intent_data = get_loop_intent_data(loop_id)
    if not intent_data:
        print(f"Loop {loop_id}: Failed to load intent data. Aborting.")
        log_loop_summary(loop_id, "Unknown", "Failed - Intent Load Error")
        return

    intent_description = intent_data.get("objective", "No objective provided.")
    target_components = intent_data.get("target_components", [])
    initial_prompt = intent_data.get("initial_prompt", "")
    mutation_requests = intent_data.get("mutation_requests", [])
    agent_inputs = intent_data.get("agent_inputs", [])
    requires_operator_review = intent_data.get("requires_operator_review", False) # Batch 20.3

    print(f"Loop {loop_id}: Objective - {intent_description}")
    log_justification(loop_id, "loop_controller", "Loop Start", f"Objective: {intent_description}", 1.0)

    # 2. Process Mutation Requests (if any)
    mutation_approved = True
    mutation_rejection_reason = ""
    if mutation_requests:
        print(f"Loop {loop_id}: Processing {len(mutation_requests)} mutation request(s)...")
        # Batch 20.3: Check if Operator Review is required *before* Mutation Guard
        if requires_operator_review:
            approved, reason, _ = perform_operator_review(loop_id, intent_data, review_type="mutation") # Pass full intent for context
            if not approved:
                mutation_approved = False
                mutation_rejection_reason = reason
                print(f"Loop {loop_id}: Mutation rejected by Operator Review Gate. Reason: {reason}")
            else:
                print(f"Loop {loop_id}: Mutation approved by Operator Review Gate.")
        
        # Only proceed to Mutation Guard if Operator Review approved (or wasn't required)
        if mutation_approved:
            for i, req in enumerate(mutation_requests):
                print(f"Loop {loop_id}: Applying Mutation Guard to request {i+1}...")
                # Pass loop_id to mutation guard - Batch 21.3
                guard_result = await process_mutation_request(loop_id, req)
                # Robustly check the guard_result structure
                is_approved = False
                rejection_reason_from_guard = "Mutation Guard rejected request (reason not explicitly provided in result)."
                if isinstance(guard_result, dict):
                    is_approved = guard_result.get("approved", False)
                    if not is_approved:
                        rejection_reason_from_guard = guard_result.get("reason", rejection_reason_from_guard)
                else:
                    # If not a dict, it's likely an error or unexpected return, treat as rejected
                    rejection_reason_from_guard = f"Mutation Guard returned unexpected result: {str(guard_result)[:200]}"

                log_justification(loop_id, "mutation_guard", f"Mutation Request {i+1} Processed", f"Target: {req.get('target_surface')}, Action: {req.get('action')}, Status: {'Approved' if is_approved else 'Rejected'}. Details: {str(guard_result)[:200]}", 1.0)
                
                if not is_approved:
                    mutation_approved = False
                    mutation_rejection_reason = rejection_reason_from_guard
                    print(f"Loop {loop_id}: Mutation request {i+1} rejected by Mutation Guard. Reason: {mutation_rejection_reason}")
                    log_rejection(loop_id, f"Mutation Guard: {mutation_rejection_reason}")
                    break # Stop processing further mutations if one fails
                else:
                    print(f"Loop {loop_id}: Mutation request {i+1} approved by Mutation Guard.")
                    # Actual mutation application logic would go here if guard passes
                    # For now, we just log approval
                    log_justification(loop_id, "loop_controller", f"Mutation Request {i+1} Approved", f"Mutation Guard approved request for {req.get('target_surface')}", 0.9)

    if not mutation_approved:
        print(f"Loop {loop_id}: Aborting due to mutation rejection. Reason: {mutation_rejection_reason}")
        log_loop_summary(loop_id, intent_description, f"Failed - Mutation Rejected: {mutation_rejection_reason}")
        # Batch 21.2: Log complexity even on failure
        duration = time.time() - start_time
        update_complexity_metrics(loop_id, duration_sec=duration, agent_calls=agent_call_count)
        return

    # 3. Invoke Target Agents (if any)
    agent_results = {}
    belief_proposal_result = None # Batch 21.5: Store belief proposal if generated
    if target_components:
        print(f"Loop {loop_id}: Invoking {len(target_components)} target component(s): {', '.join(target_components)}")
        for agent_key in target_components:
            agent_input_data = next((item["input_data"] for item in agent_inputs if item["agent_key"] == agent_key), None)
            if agent_input_data is None:
                print(f"Loop {loop_id}: Warning - No input data found for agent '{agent_key}'. Skipping invocation.")
                log_justification(loop_id, "loop_controller", f"Agent Invocation Skipped ({agent_key})", "No input data found in intent file.", 0.7)
                continue

            try:
                agent_class = get_agent(agent_key)
                if agent_class:
                    print(f"Loop {loop_id}: Invoking agent '{agent_key}'...")
                    log_justification(loop_id, "loop_controller", f"Agent Invocation Start ({agent_key})", f"Invoking agent {agent_key}", 0.9)
                    agent_call_count += 1

                    # --- Batch 21.5 Remediation: Validate/Convert Input Data --- 
                    validated_input = None
                    try:
                        # TODO: Need a way to get the expected input model type dynamically
                        # For now, hardcode for belief_manager
                        if agent_key == "belief_manager":
                            validated_input = BeliefManagerInput(**agent_input_data)
                        else:
                            # Assume other agents might handle dicts or have different models
                            # This needs a more robust solution later
                            validated_input = agent_input_data # Pass raw dict if not belief_manager
                    except Exception as validation_error: # Catch Pydantic validation errors etc.
                        print(f"Loop {loop_id}: Error validating input for agent '{agent_key}': {validation_error}")
                        log_justification(loop_id, "loop_controller", f"Agent Input Validation Error ({agent_key})", f"Error: {validation_error}", 1.0)
                        # Apply penalty and potentially skip/fail
                        update_agent_budget(loop_id, agent_key, 0, AGENT_ERROR_PENALTY) # No execution cost, just penalty
                        continue # Skip this agent
                    # --- End Remediation ---
                    
                    # --- Batch 21.4: Budget Check (Placeholder - Needs Trust/Gating Logic) ---
                    # budget_data = load_json(AGENT_BUDGET_PATH)
                    # agent_budget = budget_data.get("agents", {}).get(agent_key, {}).get("remaining_budget", 100.0)
                    # if agent_budget < AGENT_EXECUTION_COST:
                    #     print(f"Loop {loop_id}: Agent '{agent_key}' has insufficient budget ({agent_budget:.2f}). Skipping.")
                    #     log_justification(loop_id, "loop_controller", f"Agent Invocation Skipped ({agent_key})", f"Insufficient budget ({agent_budget:.2f})", 0.8)
                    #     continue # Skip agent if budget too low (example gating)
                    # --- End Batch 21.4 ---
                    
                    agent_start_time = time.time()
                    agent_instance = agent_class() # Instantiate the agent
                    # Pass the validated input model instance
                    result: AgentResult = await agent_instance.run(validated_input, loop_id) # Type hint result
                    agent_duration = time.time() - agent_start_time
                    
                    # --- Batch 21.5 Remediation: Store AgentResult directly --- 
                    # agent_results[agent_key] = result.model_dump() # Store dict representation if needed elsewhere
                    agent_results[agent_key] = result # Store the actual AgentResult object
                    # --- End Remediation ---
                    
                    # --- Batch 21.4 & 21.5 Remediation: Update Budget based on AgentResult --- 
                    cost = AGENT_EXECUTION_COST # Base cost
                    penalty = 0.0
                    # Check status and error_message from AgentResult
                    if result.status != ResultStatus.SUCCESS or result.error_message:
                        penalty = AGENT_ERROR_PENALTY
                        error_info = f"Error: {result.error_message}" if result.error_message else "Status was not SUCCESS."
                        print(f"Loop {loop_id}: Agent '{agent_key}' encountered errors ({error_info}). Applying budget penalty.")
                        log_justification(loop_id, "loop_controller", f"Agent Error Penalty ({agent_key})", f"Applying penalty of {penalty} due to errors: {error_info}", 0.8)
                    update_agent_budget(loop_id, agent_key, cost, penalty)
                    # --- End Remediation ---

                    # --- Batch 21.5 Remediation: Use result.status for logging --- 
                    print(f"Loop {loop_id}: Agent '{agent_key}' finished in {agent_duration:.2f}s. Status: {result.status.value}")
                    log_justification(loop_id, "loop_controller", f"Agent Invocation End ({agent_key})", f"Agent {agent_key} finished. Status: {result.status.value}, Duration: {agent_duration:.2f}s", 0.9)
                    # --- End Remediation ---
                    
                    # --- Batch 21.5 Remediation: Check AgentResult for belief proposal --- 
                    if agent_key == "belief_manager" and result.status == ResultStatus.SUCCESS and result.output:
                        # Assuming result.output is the dict representation from model_dump() in the agent
                        proposal_data = result.output.get("proposal") 
                        if proposal_data:
                            try:
                                belief_proposal_result = BeliefChangeProposal(**proposal_data)
                                print(f"Loop {loop_id}: Captured Belief Change Proposal {belief_proposal_result.proposal_id} from {agent_key}.")
                                log_justification(loop_id, "loop_controller", "Belief Proposal Captured", f"Captured proposal {belief_proposal_result.proposal_id} from {agent_key}", 0.9)
                            except Exception as e:
                                print(f"Loop {loop_id}: Error parsing belief proposal from {agent_key}: {e}")
                                log_justification(loop_id, "loop_controller", "Belief Proposal Parse Error", f"Error parsing proposal from {agent_key}: {e}", 1.0)
                                # Handle error - perhaps fail the loop?
                                log_loop_summary(loop_id, intent_description, f"Failed - Belief Proposal Parse Error")
                                duration = time.time() - start_time
                                update_complexity_metrics(loop_id, duration_sec=duration, agent_calls=agent_call_count)
                                return
                        else:
                            print(f"Loop {loop_id}: Belief Manager agent {agent_key} ran successfully but did not return a proposal in the expected output format.")
                            log_justification(loop_id, "loop_controller", "Belief Proposal Missing", f"Agent {agent_key} did not return a proposal in output.", 0.8)
                    # --- End Remediation ---
                else:
                    print(f"Loop {loop_id}: Error - Agent '{agent_key}' not found in registry.")
                    log_justification(loop_id, "loop_controller", f"Agent Invocation Failed ({agent_key})", "Agent not found in registry.", 1.0)
                    # Consider failing the loop if a critical agent is missing
            except Exception as e:
                print(f"Loop {loop_id}: Error invoking agent '{agent_key}': {e}")
                log_justification(loop_id, "loop_controller", f"Agent Invocation Error ({agent_key})", f"Error during invocation: {e}", 1.0)
                # Apply budget penalty for unexpected errors during invocation
                # Check if agent_key exists before applying penalty
                if agent_key in AGENT_REGISTRY: # Check if agent was ever registered
                    update_agent_budget(loop_id, agent_key, 0, AGENT_ERROR_PENALTY) # No execution cost, just penalty for error
                # Decide if loop should fail based on the error

    # --- Batch 21.5: Handle Belief Change Proposal Review and Application --- 
    if belief_proposal_result:
        proposal_file_path = os.path.join(PROPOSED_BELIEF_CHANGE_DIR, f"proposed_belief_change_{loop_id}.json")
        print(f"Loop {loop_id}: Processing Belief Change Proposal {belief_proposal_result.proposal_id}.")
        
        # Save initial proposal
        save_json(belief_proposal_result.model_dump(), proposal_file_path)
        print(f"Loop {loop_id}: Saved proposal to {proposal_file_path}")
        
        # Perform Operator Review for the belief proposal
        approved, reason, operator_log_id = perform_operator_review(loop_id, belief_proposal_result.model_dump(), review_type="belief_change")
        
        if approved:
            print(f"Loop {loop_id}: Belief change proposal {belief_proposal_result.proposal_id} approved by operator.")
            belief_proposal_result.status = "approved"
            belief_proposal_result.operator_review_ref = operator_log_id
            
            # Apply the update
            update_success = apply_belief_update(belief_proposal_result)
            if update_success:
                print(f"Loop {loop_id}: Belief update applied successfully.")
                log_justification(loop_id, "belief_updater", "Belief Update Success", f"Successfully applied proposal {belief_proposal_result.proposal_id}", 1.0)
            else:
                print(f"Loop {loop_id}: Failed to apply belief update for proposal {belief_proposal_result.proposal_id}.")
                log_justification(loop_id, "belief_updater", "Belief Update Failure", f"Failed to apply proposal {belief_proposal_result.proposal_id}", 1.0)
                # Decide if loop should fail here
        else:
            print(f"Loop {loop_id}: Belief change proposal {belief_proposal_result.proposal_id} rejected or timed out. Reason: {reason}")
            belief_proposal_result.status = "rejected" # Or 'timeout' if applicable, though perform_operator_review logs specific status
            belief_proposal_result.operator_review_ref = operator_log_id
            belief_proposal_result.rejection_reason = reason
            # Log rejection specifically for belief change context if needed
            log_justification(loop_id, "loop_controller", "Belief Proposal Rejected", f"Proposal {belief_proposal_result.proposal_id} rejected/timed out. Reason: {reason}", 1.0)
            # Loop likely continues, but belief is not changed

        # Save the final state of the proposal (approved/rejected)
        save_json(belief_proposal_result.model_dump(), proposal_file_path)
        print(f"Loop {loop_id}: Updated proposal status saved to {proposal_file_path}")
    # --- End Batch 21.5 ---

    # 4. Final Validation (Placeholder)
    print(f"Loop {loop_id}: Performing final validation...")
    # Add checks based on expected_outcome in intent_data if needed
    validation_passed = True # Assume success for now
    log_justification(loop_id, "loop_controller", "Final Validation", f"Validation status: {'Passed' if validation_passed else 'Failed'}", 0.9 if validation_passed else 1.0)

    # 5. Log Summary
    final_status = "Completed" if validation_passed else "Failed - Validation Error"
    log_loop_summary(loop_id, intent_description, final_status)
    print(f"--- Loop {loop_id} Finished: {final_status} ---")

    # Batch 21.2: Log final complexity metrics
    duration = time.time() - start_time
    update_complexity_metrics(loop_id, duration_sec=duration, agent_calls=agent_call_count)
    print(f"Loop {loop_id}: Total execution time: {duration:.2f} seconds")

async def main():
    parser = argparse.ArgumentParser(description="Execute a specific control loop.")
    parser.add_argument("loop_id", help="The ID of the loop to execute (e.g., 0001)")
    args = parser.parse_args()

    # Ensure necessary directories exist
    os.makedirs(MEMORY_DIR, exist_ok=True)
    os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True) # Batch 20.3
    os.makedirs(OPERATOR_INPUT_DIR, exist_ok=True) # Batch 20.3
    os.makedirs(PROPOSED_BELIEF_CHANGE_DIR, exist_ok=True) # Batch 21.5
    os.makedirs(os.path.dirname(LOOP_SUMMARY_PATH), exist_ok=True) # Ensure log dir exists
    os.makedirs(os.path.dirname(REJECTION_LOG_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(OPERATOR_OVERRIDE_LOG_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(COMPLEXITY_METRICS_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(AGENT_BUDGET_PATH), exist_ok=True)

    await execute_loop(args.loop_id)

if __name__ == "__main__":
    asyncio.run(main())

