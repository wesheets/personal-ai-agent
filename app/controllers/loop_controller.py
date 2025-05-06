#!/usr/bin/env python3.11
import json
import argparse
import os
import sys
import asyncio
import time # Batch 20.3: Added for polling timeout
from datetime import datetime, timedelta, timezone # Batch 20.3: Added for timeout calculation; Batch 21.2: Added timezone
from typing import Literal, List, Dict, Any # Batch 22.2: For Critic evaluation result; Batch 22.3: Added List, Dict, Any

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

from app.validators.mutation_guard import process_mutation_request
from app.core.agent_registry import get_agent, AGENT_REGISTRY, AgentNotFoundException # Batch 22.2: Import AgentNotFoundException
from app.schemas.agents.belief_manager.belief_manager_schemas import BeliefManagerInput
from app.schemas.agent_input.architect_agent_input import ArchitectInstruction
from app.schemas.agent_output.architect_agent_output import ArchitectPlanResult
from app.schemas.agent_input.critic_agent_input import CriticPlanEvaluationInput 
from app.schemas.agent_output.critic_agent_output import CriticPlanEvaluationResult
from app.schemas.agent_input.pessimist_agent_input import PessimistRiskAssessmentInput
from app.schemas.agent_output.pessimist_agent_output import PessimistRiskAssessmentResult
from app.schemas.core.agent_result import AgentResult, ResultStatus
from app.utils.justification_logger import log_justification
from app.schemas.agents.belief_manager.belief_manager_schemas import BeliefChangeProposal
from app.validators.belief_updater import apply_belief_update
from app.validators.archetype_classifier import ArchetypeClassifier
from app.validators.schema_updater import apply_schema_change # Batch 22.3: Import schema_updater

# Define paths relative to PROJECT_ROOT
LOOP_SUMMARY_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary.json")
LOOP_SUMMARY_REJECTION_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/loop_summary_rejection_log.json")
LOOP_INTENT_DIR = os.path.join(PROJECT_ROOT, "app/memory/")
MEMORY_DIR = os.path.join(PROJECT_ROOT, "app/memory/")
REVIEW_QUEUE_DIR = "/home/ubuntu/review_queue/"
OPERATOR_INPUT_DIR = "/home/ubuntu/operator_input/"
OPERATOR_OVERRIDE_LOG_PATH = os.path.join(MEMORY_DIR, "operator_override_log.json")
BELIEF_SURFACE_PATH = os.path.join(MEMORY_DIR, "belief_surface.json")
AGENT_BUDGET_PATH = os.path.join(MEMORY_DIR, "agent_cognitive_budget.json")
PROPOSED_BELIEF_CHANGE_DIR = os.path.join(MEMORY_DIR, "proposed_belief_changes/")
COMPLEXITY_BUDGET_PATH = os.path.join(MEMORY_DIR, "complexity_budget.json")
DRIFT_VIOLATION_LOG_PATH = "/home/ubuntu/drift_violation_log.json"
AGENT_TRUST_SCORE_PATH = os.path.join(MEMORY_DIR, "agent_trust_score.json")
BELIEF_CONFLICT_LOG_PATH = os.path.join(MEMORY_DIR, "belief_conflict_log.json")
# Batch 22.3: Path for schema change requests
SCHEMA_CHANGE_REQUEST_PATH = os.path.join(MEMORY_DIR, "schema_change_request.json")

OPERATOR_REVIEW_TIMEOUT_SECONDS = 300 
OPERATOR_REVIEW_POLL_INTERVAL_SECONDS = 5
AGENT_EXECUTION_COST = 5.0
AGENT_ERROR_PENALTY = 10.0
DEFAULT_LOOP_BASE_COST = 1.0
MINIMUM_BUDGET_THRESHOLD = 0

def load_json(path, is_list_default=True):
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content.strip(): 
                if os.path.basename(path).startswith("loop_intent"):
                    return None
                return [] if is_list_default else {}
            f.seek(0) # Rewind after reading to allow json.load to work
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found at {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        return [] if is_list_default else {}
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {path}. Returning default value.")
        if os.path.basename(path).startswith("loop_intent"):
            return None
        return [] if is_list_default else {}

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def log_agent_registration_drift(loop_id, agent_key, attempting_module, reason):
    drift_log = load_json(DRIFT_VIOLATION_LOG_PATH, is_list_default=False) 
    if not isinstance(drift_log, dict) or "drift_log_entries" not in drift_log:
        drift_log = {"drift_log_entries": []}
    
    entry = {
        "log_id": f"drift_{agent_key}_{loop_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "drift_type": "Agent Registration Drift",
        "severity": "High", 
        "agent_key": agent_key,
        "attempting_module": attempting_module,
        "loop_id": loop_id,
        "reason_for_failure": reason,
        "status": "logged_for_recovery"
    }
    drift_log["drift_log_entries"].append(entry)
    save_json(drift_log, DRIFT_VIOLATION_LOG_PATH)
    print(f"Loop {loop_id}: Logged agent registration drift for '{agent_key}': {reason}")

def log_loop_summary(loop_id, intent_description, status, archetype, timestamp_start_iso, summary_status="pending_review", summary_actions="Placeholder summary of actions.", artifacts=None, errors=None):
    summary_log = load_json(LOOP_SUMMARY_PATH)
    if not isinstance(summary_log, list):
        print(f"Warning: {LOOP_SUMMARY_PATH} is not a list. Reinitializing.")
        summary_log = []
    
    entry = {
        "loop_id": loop_id,
        "timestamp_start": timestamp_start_iso,
        "timestamp_end": datetime.now(timezone.utc).isoformat(),
        "intent_description": intent_description,
        "archetype": archetype,
        "status": status, 
        "summary_status": summary_status, 
        "summary_of_actions": summary_actions,
        "key_artifacts_produced": artifacts if artifacts is not None else [],
        "errors_encountered": errors if errors is not None else []
    }
    summary_log.append(entry)
    save_json(summary_log, LOOP_SUMMARY_PATH)

def log_summary_rejection(loop_id, reason, validator_agent_id="LoopControllerInternal"):
    rejection_log = load_json(LOOP_SUMMARY_REJECTION_LOG_PATH)
    if not isinstance(rejection_log, list):
        print(f"Warning: {LOOP_SUMMARY_REJECTION_LOG_PATH} is not a list. Reinitializing.")
        rejection_log = []
    entry = {
        "loop_id": loop_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "rejection_reason": reason,
        "validator_agent_id": validator_agent_id
    }
    rejection_log.append(entry)
    save_json(rejection_log, LOOP_SUMMARY_REJECTION_LOG_PATH)
    print(f"Loop {loop_id}: Logged summary rejection. Reason: {reason} by {validator_agent_id}")

async def evaluate_loop_summary(loop_id, loop_archetype, accumulated_complexity_cost, final_loop_status, summary_actions_str, key_artifacts_list, errors_list):
    print(f"Loop {loop_id}: Evaluating loop summary.")
    summary_status = "pending_review" 
    rejection_reason = ""
    validator_id = "LoopControllerInternal"

    # Batch 22.3: Robust handling of agent_trust_score.json structure
    trust_scores_data = load_json(AGENT_TRUST_SCORE_PATH, is_list_default=False) # Try loading as dict first
    current_trust_score = 0.75 # Default trust score

    if isinstance(trust_scores_data, dict):
        current_trust_score = trust_scores_data.get("system_average_trust", 0.75)
        print(f"Loop {loop_id}: Loaded system_average_trust: {current_trust_score} from dict.")
    elif isinstance(trust_scores_data, list) and trust_scores_data:
        # Calculate average if it's a list of agent scores
        total_score = 0
        count = 0
        for agent_score_entry in trust_scores_data:
            if isinstance(agent_score_entry, dict) and "score" in agent_score_entry:
                try:
                    total_score += float(agent_score_entry["score"])
                    count += 1
                except ValueError:
                    print(f"Loop {loop_id}: Invalid score format in agent_trust_score.json for entry: {agent_score_entry}")
        if count > 0:
            current_trust_score = total_score / count
            print(f"Loop {loop_id}: Calculated average trust score: {current_trust_score} from list of {count} agents.")
        else:
            print(f"Loop {loop_id}: agent_trust_score.json was a list, but no valid scores found. Using default trust score: {current_trust_score}.")
    else:
        print(f"Loop {loop_id}: agent_trust_score.json is not a dict or a non-empty list, or is empty/malformed. Using default trust score: {current_trust_score}.")

    belief_conflicts_data = load_json(BELIEF_CONFLICT_LOG_PATH)
    relevant_belief_conflicts = [c for c in belief_conflicts_data if c.get("loop_id") == loop_id and c.get("status") == "unresolved"]

    summary_details_for_critic = {
        "loop_id": loop_id,
        "archetype": loop_archetype,
        "cognitive_cost": accumulated_complexity_cost,
        "loop_status": final_loop_status,
        "trust_score_at_runtime": current_trust_score,
        "belief_conflicts": relevant_belief_conflicts,
        "summary_content": {
            "actions": summary_actions_str,
            "artifacts": key_artifacts_list,
            "errors": errors_list
        }
    }

    critic_agent = None
    try:
        critic_agent = get_agent("Critic")
    except AgentNotFoundException as e:
        log_agent_registration_drift(loop_id, "Critic", "app.controllers.loop_controller.evaluate_loop_summary", str(e))
        rejection_reason = "Critic agent not found for summary evaluation. Drift logged. Summary pending manual review."
        validator_id = "LoopControllerInternal_CriticNotFound"
        summary_status = "pending_review" 
        if rejection_reason: 
             log_summary_rejection(loop_id, rejection_reason, validator_id)
        return summary_status, rejection_reason
    
    if critic_agent:
        validator_id = "CriticAgent"
        try:
            print(f"Loop {loop_id}: Sending summary to Critic for evaluation.")
            simulated_critic_evaluation = "accepted" 
            simulated_critic_reason = "Summary meets quality standards."

            if current_trust_score < 0.5: 
                simulated_critic_evaluation = "rejected"
                simulated_critic_reason = f"Summary rejected due to low trust score at runtime ({current_trust_score:.2f})."
            elif accumulated_complexity_cost > 200 and loop_archetype == "Explore": 
                simulated_critic_evaluation = "rejected"
                simulated_critic_reason = f"Summary rejected: High cognitive cost ({accumulated_complexity_cost}) for an '{loop_archetype}' loop."
            elif relevant_belief_conflicts:
                simulated_critic_evaluation = "rejected"
                simulated_critic_reason = f"Summary rejected due to unresolved belief conflicts related to the loop: {len(relevant_belief_conflicts)} conflicts found."
            
            summary_status = simulated_critic_evaluation
            rejection_reason = simulated_critic_reason

            if summary_status == "rejected":
                log_summary_rejection(loop_id, rejection_reason, validator_id)
                print(f"Loop {loop_id}: Summary rejected by Critic. Reason: {rejection_reason}. Optional reroute suggestion could be triggered.")
            else:
                print(f"Loop {loop_id}: Summary accepted by Critic.")

        except Exception as e:
            print(f"Loop {loop_id}: Error during Critic summary evaluation: {e}")
            rejection_reason = f"Error during Critic summary evaluation: {e}. Summary pending manual review."
            summary_status = "pending_review"
            validator_id = "CriticAgent_Error"
            log_summary_rejection(loop_id, rejection_reason, validator_id)
    
    return summary_status, rejection_reason

def get_loop_intent_data(loop_id):
    intent_path = os.path.join(LOOP_INTENT_DIR, f"loop_intent_{loop_id}.json")
    renamed_intent_path = os.path.join(LOOP_INTENT_DIR, f"loop_intent_loop_{loop_id}.json")
    actual_path = None
    if os.path.exists(renamed_intent_path):
        actual_path = renamed_intent_path
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

def log_operator_override(loop_id, event_type, decision, reason, details):
    override_log = load_json(OPERATOR_OVERRIDE_LOG_PATH)
    if not isinstance(override_log, list):
        print(f"Warning: {OPERATOR_OVERRIDE_LOG_PATH} is not a list. Reinitializing.")
        override_log = []
    entry = {
        "log_id": f"op_{loop_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        "loop_id": loop_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type, # e.g., "mutation_review", "belief_change_review", "schema_change_review"
        "decision": decision, 
        "reason": reason,
        "reviewed_details": details
    }
    override_log.append(entry)
    save_json(override_log, OPERATOR_OVERRIDE_LOG_PATH)
    print(f"Logged operator decision for loop {loop_id} ({event_type}): {decision}")
    return entry["log_id"]

async def perform_operator_review(loop_id, review_data, review_type="mutation", proposal_id=None):
    print(f"Loop {loop_id}: Entering Operator Review Gate for {review_type} (Proposal ID: {proposal_id if proposal_id else 'N/A'}).")
    log_justification(loop_id, "loop_controller", f"Operator Review Pending ({review_type})", f"{review_type.capitalize()} (Proposal ID: {proposal_id if proposal_id else 'N/A'}) requires operator review. Blocking execution.", 1.0)
    
    # Batch 22.3: Standardize review file naming
    review_file_name_suffix = f"{review_type}_{proposal_id}" if proposal_id and review_type == "schema_change" else review_type
    review_file_path = os.path.join(REVIEW_QUEUE_DIR, f"review_request_loop_{loop_id}_{review_file_name_suffix}.json")
    operator_decision_file_path_pattern = os.path.join(OPERATOR_INPUT_DIR, f"review_decision_loop_{loop_id}_{review_file_name_suffix}.json")

    try:
        os.makedirs(REVIEW_QUEUE_DIR, exist_ok=True)
        save_json(review_data, review_file_path)
        print(f"Loop {loop_id}: Review request saved to {review_file_path}. Waiting for operator decision at {operator_decision_file_path_pattern}")
    except Exception as e:
        print(f"Loop {loop_id}: Failed to save review request file {review_file_path}: {e}")
        log_justification(loop_id, "loop_controller", f"Operator Review Error ({review_type})", f"Failed to save review request: {e}", 1.0)
        return {"decision": "error", "reason": "Failed to initiate review process."}

    start_time = datetime.now(timezone.utc)
    while datetime.now(timezone.utc) - start_time < timedelta(seconds=OPERATOR_REVIEW_TIMEOUT_SECONDS):
        if os.path.exists(operator_decision_file_path_pattern):
            print(f"Loop {loop_id}: Operator decision file found at {operator_decision_file_path_pattern}.")
            decision_data = load_json(operator_decision_file_path_pattern, is_list_default=False)
            if isinstance(decision_data, dict) and "decision" in decision_data:
                # Batch 22.3: Ensure proposal_id matches if it's a schema change review
                if review_type == "schema_change" and proposal_id and decision_data.get("proposal_id") != proposal_id:
                    print(f"Loop {loop_id}: Operator decision file proposal_id mismatch. Expected {proposal_id}, got {decision_data.get('proposal_id')}. Ignoring.")
                    # Potentially log this mismatch or handle as an error, for now, continue polling
                    await asyncio.sleep(OPERATOR_REVIEW_POLL_INTERVAL_SECONDS)
                    continue
                
                log_justification(loop_id, "loop_controller", f"Operator Review Complete ({review_type})", f"Operator decision '{decision_data['decision']}' received.", 1.0)
                # Log to operator_override_log.json
                log_operator_override(
                    loop_id=loop_id, 
                    event_type=review_type,
                    decision=decision_data["decision"],
                    reason=decision_data.get("justification", "No justification provided."),
                    details=review_data # Log the original data that was reviewed
                )
                try: # Cleanup the decision file
                    os.remove(operator_decision_file_path_pattern)
                    print(f"Loop {loop_id}: Cleaned up operator decision file {operator_decision_file_path_pattern}.")
                except OSError as e_remove:
                    print(f"Loop {loop_id}: Warning - Failed to remove operator decision file {operator_decision_file_path_pattern}: {e_remove}")
                try: # Cleanup the review request file
                    os.remove(review_file_path)
                    print(f"Loop {loop_id}: Cleaned up review request file {review_file_path}.")
                except OSError as e_remove_req:
                     print(f"Loop {loop_id}: Warning - Failed to remove review request file {review_file_path}: {e_remove_req}")
                return decision_data
            else:
                print(f"Loop {loop_id}: Operator decision file {operator_decision_file_path_pattern} is invalid. Waiting.")
        await asyncio.sleep(OPERATOR_REVIEW_POLL_INTERVAL_SECONDS)

    print(f"Loop {loop_id}: Operator review timed out for {review_type} (Proposal ID: {proposal_id if proposal_id else 'N/A'}).")
    log_justification(loop_id, "loop_controller", f"Operator Review Timeout ({review_type})", f"Operator review timed out after {OPERATOR_REVIEW_TIMEOUT_SECONDS} seconds.", 1.0)
    # Log timeout to operator_override_log.json
    log_operator_override(
        loop_id=loop_id, 
        event_type=review_type,
        decision="timeout", 
        reason=f"Operator review timed out after {OPERATOR_REVIEW_TIMEOUT_SECONDS} seconds.",
        details=review_data
    )
    try: # Cleanup the review request file on timeout
        os.remove(review_file_path)
        print(f"Loop {loop_id}: Cleaned up review request file {review_file_path} on timeout.")
    except OSError as e_remove_timeout:
            print(f"Loop {loop_id}: Warning - Failed to remove review request file {review_file_path} on timeout: {e_remove_timeout}")
    return {"decision": "timeout", "reason": "Operator review timed out."}

# Batch 22.3: Function to check for and process schema change proposals
async def check_and_process_schema_change_proposals(loop_id, current_loop_summary_actions):
    print(f"Loop {loop_id}: Checking for pending schema change proposals.")
    schema_change_requests = load_json(SCHEMA_CHANGE_REQUEST_PATH)
    if not isinstance(schema_change_requests, list):
        print(f"Warning: {SCHEMA_CHANGE_REQUEST_PATH} is not a list or not found. Skipping schema change processing.")
        return

    processed_a_proposal = False
    for proposal in schema_change_requests:
        if proposal.get("status") == "pending_review":
            # Check if this proposal was generated in the current loop to avoid immediate re-processing
            # This simple check might need refinement based on how SchemaManagerAgent posts proposals
            if proposal.get("loop_id_proposed") == loop_id and not proposal.get("loop_id_reviewed"):
                print(f"Loop {loop_id}: Found new schema proposal {proposal.get('proposal_id')} generated in this loop. Review will occur post-loop or in a subsequent loop.")
                current_loop_summary_actions.append(f"Schema proposal {proposal.get('proposal_id')} generated; pending operator review.")
                continue # Skip review in the same loop it was generated, unless explicitly designed for that

            print(f"Loop {loop_id}: Found pending schema proposal {proposal.get('proposal_id')}. Initiating operator review.")
            current_loop_summary_actions.append(f"Operator review initiated for schema proposal {proposal.get('proposal_id')}.")
            
            review_data = {
                "proposal_id": proposal.get("proposal_id"),
                "target_schema_path": proposal.get("target_schema_path"),
                "proposed_change_description": proposal.get("proposed_change_description"),
                "justification": proposal.get("justification"),
                "potential_impact": proposal.get("potential_impact"),
                "proposing_agent_id": proposal.get("proposing_agent_id"),
                "timestamp_proposed": proposal.get("timestamp")
            }
            operator_decision_data = await perform_operator_review(loop_id, review_data, review_type="schema_change", proposal_id=proposal.get("proposal_id"))
            
            proposal["loop_id_reviewed"] = loop_id
            proposal["timestamp_reviewed"] = datetime.now(timezone.utc).isoformat()

            if operator_decision_data.get("decision") == "approved":
                print(f"Loop {loop_id}: Schema proposal {proposal.get('proposal_id')} approved by operator. Simulating application.")
                proposal["status"] = "approved"
                current_loop_summary_actions.append(f"Schema proposal {proposal.get('proposal_id')} approved by operator.")
                # Call schema_updater.apply_schema_change
                simulation_success = apply_schema_change(proposal.get("proposal_id")) # schema_updater handles updating status to 'applied_simulated'
                if simulation_success:
                    print(f"Loop {loop_id}: Simulated application of schema proposal {proposal.get('proposal_id')} successful.")
                    current_loop_summary_actions.append(f"Simulated application of schema proposal {proposal.get('proposal_id')} successful.")
                else:
                    print(f"Loop {loop_id}: Simulated application of schema proposal {proposal.get('proposal_id')} failed or proposal not found/not approved for simulation.")
                    current_loop_summary_actions.append(f"Simulated application of schema proposal {proposal.get('proposal_id')} failed.")
                    # Status might be 'error_proposal_not_found' or 'aborted' if apply_schema_change fails before simulation
                    # If apply_schema_change itself sets a failure status, that will be in the file.
            elif operator_decision_data.get("decision") == "rejected":
                print(f"Loop {loop_id}: Schema proposal {proposal.get('proposal_id')} rejected by operator.")
                proposal["status"] = "rejected"
                current_loop_summary_actions.append(f"Schema proposal {proposal.get('proposal_id')} rejected by operator.")
            else: # Timeout or error
                print(f"Loop {loop_id}: Operator review for schema proposal {proposal.get('proposal_id')} resulted in {operator_decision_data.get('decision')}: {operator_decision_data.get('reason')}")
                proposal["status"] = "review_timeout" # Or another appropriate status
                current_loop_summary_actions.append(f"Operator review for schema proposal {proposal.get('proposal_id')} timed out or errored.")
            processed_a_proposal = True
            # Save changes to schema_change_request.json after each proposal is processed
            save_json(schema_change_requests, SCHEMA_CHANGE_REQUEST_PATH)
            print(f"Loop {loop_id}: Updated schema_change_request.json for proposal {proposal.get('proposal_id')}.")
            # Potentially break if only one proposal should be handled per loop, or continue to process all pending.
            # For now, let's assume we process all pending ones found at the start of this check.
    if processed_a_proposal:
        print(f"Loop {loop_id}: Finished processing pending schema change proposals.")
    else:
        print(f"Loop {loop_id}: No actionable pending schema change proposals found.")


async def run_loop(loop_id: str):
    timestamp_start_iso = datetime.now(timezone.utc).isoformat()
    print(f"Starting Loop ID: {loop_id} at {timestamp_start_iso}")
    accumulated_complexity_cost = DEFAULT_LOOP_BASE_COST
    current_loop_summary_actions = []
    key_artifacts = []
    loop_errors = []

    intent_data = get_loop_intent_data(loop_id)
    if not intent_data:
        log_loop_summary(loop_id, "Intent data not found or invalid", "failure", "Unknown", timestamp_start_iso, summary_status="rejected", summary_actions="Loop failed: Intent data not found or invalid.", errors=["Intent data not found or invalid"])
        return

    intent_description = intent_data.get("intent_description", "No description provided.")
    target_agent_key = intent_data.get("target_agent", "Orchestrator") 
    agent_input_data = intent_data.get("agent_input", {})

    # Archetype Classification (Batch 22.1) - MODIFIED for Batch 22.3 fix
    classifier = ArchetypeClassifier()
    # The classify_intent method expects: intent_description: str, target_components: list = None, parameters: dict = None, tools_used: list = None
    # We have intent_description and agent_input_data (can be parameters).
    # target_agent_key can be a target_component.
    # tools_used is not readily available here before agent execution.
    loop_archetype = classifier.classify_intent(intent_description=intent_description, 
                                                target_components=[target_agent_key] if target_agent_key else None, 
                                                parameters=agent_input_data)
    print(f"Loop {loop_id}: Classified archetype as '{loop_archetype}'.")
    # Assuming estimate_cost is a method in ArchetypeClassifier, if not, this needs adjustment or a default value.
    # For now, let's add a placeholder for cost estimation if the method doesn't exist.
    estimated_archetype_cost = 0
    if hasattr(classifier, 'estimate_cost'):
        estimated_archetype_cost = classifier.estimate_cost(loop_archetype)
    else:
        print(f"Warning: ArchetypeClassifier does not have 'estimate_cost' method. Using default cost 0 for archetype.")

    current_loop_summary_actions.append(f"Archetype: {loop_archetype}, Est. Cost: {estimated_archetype_cost}.")
    accumulated_complexity_cost += estimated_archetype_cost

    # Complexity Budget Check (Batch 22.1)
    complexity_budget = load_json(COMPLEXITY_BUDGET_PATH, is_list_default=False)
    domain_budget = complexity_budget.get("domains", {}).get(intent_data.get("domain", "general"), {"budget": 100, "spent": 0})
    archetype_specific_budget_key = f"archetype_{loop_archetype}_budget"
    archetype_budget_value = domain_budget.get(archetype_specific_budget_key, domain_budget.get("budget")) # Fallback to domain budget
    
    remaining_budget_for_archetype = archetype_budget_value - domain_budget.get(f"archetype_{loop_archetype}_spent", 0)
    current_loop_cost_estimate = estimated_archetype_cost # Cost of this specific loop

    if remaining_budget_for_archetype < current_loop_cost_estimate:
        budget_check_passed = False
        print(f"Loop {loop_id}: Complexity budget for archetype '{loop_archetype}' in domain '{intent_data.get('domain', 'general')}' nearly exceeded or insufficient (Remaining: {remaining_budget_for_archetype}, Est. Cost: {current_loop_cost_estimate}).")
        current_loop_summary_actions.append(f"Budget Check Failed: Archetype '{loop_archetype}' budget low (Rem: {remaining_budget_for_archetype}, Est: {current_loop_cost_estimate}). Requires Operator review or will be rejected.")
    else:
        budget_check_passed = True
        print(f"Loop {loop_id}: Complexity budget check passed for archetype '{loop_archetype}'.")
        current_loop_summary_actions.append(f"Budget Check Passed: Sufficient budget available.")

    # --- Main Agent Execution Logic --- 
    agent_to_run = None
    try:
        agent_to_run = get_agent(target_agent_key)
        current_loop_summary_actions.append(f"Target agent '{target_agent_key}' loaded.")
    except AgentNotFoundException as e:
        error_message = f"{target_agent_key}: Agent not found. Drift logged."
        print(f"Loop {loop_id}: {error_message} Details: {e}")
        log_agent_registration_drift(loop_id, target_agent_key, "app.controllers.loop_controller.run_loop", str(e))
        loop_errors.append(error_message)
        current_loop_summary_actions.append(error_message)
        # End loop if primary agent not found
        final_status = "failure"
        summary_status, _ = await evaluate_loop_summary(loop_id, loop_archetype, accumulated_complexity_cost, final_status, "; ".join(current_loop_summary_actions), key_artifacts, loop_errors)
        log_loop_summary(loop_id, intent_description, final_status, loop_archetype, timestamp_start_iso, summary_status=summary_status, summary_actions="; ".join(current_loop_summary_actions), artifacts=key_artifacts, errors=loop_errors)
        return

    agent_result: AgentResult = None
    if agent_to_run:
        try:
            print(f"Loop {loop_id}: Executing agent '{target_agent_key}' with input: {agent_input_data}")
            if target_agent_key == "BeliefManager":
                try:
                    belief_manager_input = BeliefManagerInput(**agent_input_data)
                    agent_result = await agent_to_run.run(belief_manager_input)
                except Exception as pydantic_error:
                    raise ValueError(f"Input validation failed for BeliefManager: {pydantic_error}") from pydantic_error
            else:
                 agent_result = await agent_to_run.run(agent_input_data) 
            
            current_loop_summary_actions.append(f"Agent '{target_agent_key}' executed. Status: {agent_result.status.value if agent_result else 'Unknown'}.")
            if agent_result and agent_result.output:
                key_artifacts.append(f"{target_agent_key}_output: {str(agent_result.output)[:200]}...") 

        except Exception as e:
            error_message = f"Error during {target_agent_key} execution: {e}"
            print(f"Loop {loop_id}: {error_message}")
            loop_errors.append(error_message)
            current_loop_summary_actions.append(error_message)
            accumulated_complexity_cost += AGENT_ERROR_PENALTY
            agent_result = AgentResult(status=ResultStatus.FAILURE, errors=[str(e)])

    # --- Post-Agent Execution Processing --- 
    final_status = "success" if agent_result and agent_result.status == ResultStatus.SUCCESS else "failure"

    # Belief Change Proposal Handling (Batch 21.5)
    if target_agent_key == "BeliefManager" and agent_result and agent_result.status == ResultStatus.SUCCESS and isinstance(agent_result.output, BeliefChangeProposal):
        proposal: BeliefChangeProposal = agent_result.output
        proposal_file_name = f"proposed_belief_change_loop_{loop_id}.json"
        proposal_file_path = os.path.join(PROPOSED_BELIEF_CHANGE_DIR, proposal_file_name)
        os.makedirs(PROPOSED_BELIEF_CHANGE_DIR, exist_ok=True)
        save_json(proposal.model_dump(), proposal_file_path)
        current_loop_summary_actions.append(f"Belief change proposal saved to {proposal_file_path}.")
        key_artifacts.append(proposal_file_path)

        review_data_belief = {
            "type": "belief_change_proposal",
            "loop_id": loop_id,
            "proposal_file": proposal_file_path,
            "proposal_details": proposal.model_dump()
        }
        operator_decision_data_belief = await perform_operator_review(loop_id, review_data_belief, review_type="belief_change")
        
        if operator_decision_data_belief.get("decision") == "approved":
            print(f"Loop {loop_id}: Belief change proposal approved by operator.")
            current_loop_summary_actions.append("Belief change proposal approved by operator.")
            update_successful = apply_belief_update(proposal_id=proposal.proposal_id, proposal_data=proposal.model_dump(), belief_surface_path=BELIEF_SURFACE_PATH, operator_override_log_path=OPERATOR_OVERRIDE_LOG_PATH, loop_id=loop_id)
            if update_successful:
                current_loop_summary_actions.append(f"Belief surface updated successfully for proposal {proposal.proposal_id}.")
            else:
                current_loop_summary_actions.append(f"Failed to apply belief update for proposal {proposal.proposal_id}.")
                loop_errors.append(f"Belief update failed for {proposal.proposal_id}")
                final_status = "failure"
        elif operator_decision_data_belief.get("decision") == "rejected":
            print(f"Loop {loop_id}: Belief change proposal rejected by operator.")
            current_loop_summary_actions.append("Belief change proposal rejected by operator.")
        else: 
            print(f"Loop {loop_id}: Operator review for belief change resulted in {operator_decision_data_belief.get('decision')}: {operator_decision_data_belief.get('reason')}")
            current_loop_summary_actions.append(f"Operator review for belief change timed out or errored. No update applied.")
            final_status = "failure" 

    # Mutation Guard (Batch 20.3)
    if intent_data.get("is_mutation", False):
        print(f"Loop {loop_id}: Mutation flag detected. Processing with MutationGuard.")
        current_loop_summary_actions.append("Mutation flag detected. Initiating MutationGuard process.")
        mutation_request_data = {
            "loop_id": loop_id,
            "intent": intent_description,
            "proposed_actions": agent_result.output if agent_result else "No actions from agent.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        operator_decision_data_mutation = await process_mutation_request(loop_id, mutation_request_data, OPERATOR_OVERRIDE_LOG_PATH, REVIEW_QUEUE_DIR, OPERATOR_INPUT_DIR, OPERATOR_REVIEW_TIMEOUT_SECONDS, OPERATOR_REVIEW_POLL_INTERVAL_SECONDS)

        if operator_decision_data_mutation.get("decision") == "approved":
            current_loop_summary_actions.append("Mutation approved by Operator.")
            print(f"Loop {loop_id}: Mutation approved. (Actual mutation application logic would follow here)")
        elif operator_decision_data_mutation.get("decision") == "rejected":
            current_loop_summary_actions.append("Mutation rejected by Operator. Loop actions halted.")
            final_status = "failure" 
            loop_errors.append("Mutation rejected by Operator.")
        else: 
            current_loop_summary_actions.append(f"Mutation review timed out or errored. Loop actions halted. Reason: {operator_decision_data_mutation.get('reason')}")
            final_status = "failure"
            loop_errors.append(f"Mutation review timeout/error: {operator_decision_data_mutation.get('reason')}")

    # Batch 22.3: Check and process schema change proposals
    if final_status != "failure": 
        await check_and_process_schema_change_proposals(loop_id, current_loop_summary_actions)

    # Update Complexity Budget (Batch 22.1)
    if budget_check_passed: 
        domain_budget_update_key_spent = f"archetype_{loop_archetype}_spent"
        domain_budget[domain_budget_update_key_spent] = domain_budget.get(domain_budget_update_key_spent, 0) + current_loop_cost_estimate 
        domain_budget["spent"] = domain_budget.get("spent", 0) + current_loop_cost_estimate 
        
        complexity_budget.get("domains", {})[intent_data.get("domain", "general")] = domain_budget
        complexity_budget["global_budget"]["spent"] = complexity_budget.get("global_budget", {}).get("spent", 0) + current_loop_cost_estimate
        save_json(complexity_budget, COMPLEXITY_BUDGET_PATH)
        current_loop_summary_actions.append(f"Complexity budget updated. Spent: {current_loop_cost_estimate} for archetype '{loop_archetype}'.")

    # Evaluate Loop Summary (Batch 22.2)
    summary_status, rejection_reason = await evaluate_loop_summary(
        loop_id, loop_archetype, accumulated_complexity_cost, final_status, "; ".join(current_loop_summary_actions), key_artifacts, loop_errors
    )
    if summary_status == "rejected":
        current_loop_summary_actions.append(f"Loop summary rejected. Reason: {rejection_reason}")

    # Final Logging
    log_loop_summary(loop_id, intent_description, final_status, loop_archetype, timestamp_start_iso, summary_status=summary_status, summary_actions="; ".join(current_loop_summary_actions), artifacts=key_artifacts, errors=loop_errors)
    print(f"Finished Loop ID: {loop_id} at {datetime.now(timezone.utc).isoformat()}. Final Status: {final_status}, Summary Status: {summary_status}")

async def main():
    parser = argparse.ArgumentParser(description="Orchestration Loop Controller")
    parser.add_argument("--loop-id", type=str, required=True, help="Unique ID for this loop execution.")
    args = parser.parse_args()
    await run_loop(args.loop_id)

if __name__ == "__main__":
    asyncio.run(main())

