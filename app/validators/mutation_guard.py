#!/usr/bin/env python3.11
import json
import os
import asyncio # Batch 20.2: Added for async agent call
from datetime import datetime
import traceback
import logging # Added for detailed logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths
BASE_MEMORY_PATH = "/home/ubuntu/personal-ai-agent/app/memory"
GUARD_LOG_PATH = "/home/ubuntu/personal-ai-agent/app/logs/mutation_guard.log"
MUTATION_LOG_PATH = os.path.join(BASE_MEMORY_PATH, "mutation_log.json")
DEBT_TOKEN_BUDGET_PATH = os.path.join(BASE_MEMORY_PATH, "debt_token_budget.json")
AGENT_TRUST_SCORE_PATH = os.path.join(BASE_MEMORY_PATH, "agent_trust_score.json") # Batch 20.2
MUTATION_REQUEST_PATH = os.path.join(BASE_MEMORY_PATH, "mutation_request.json") # Although request often comes via params
MUTATION_BACKLOG_PATH = os.path.join(BASE_MEMORY_PATH, "mutation_backlog.json") # Batch 20.3
LOOP_JUSTIFICATION_LOG_PATH = os.path.join(BASE_MEMORY_PATH, "loop_justification_log.json") # Batch 20.4
OPERATOR_OVERRIDE_LOG_PATH = os.path.join(BASE_MEMORY_PATH, "operator_override_log.json") # Batch 20.4

# --- Batch 20.2: Define Trust Check Thresholds ---
MIN_TRUST_SCORE_THRESHOLD = 0.4 # Minimum score required to attempt mutation
MIN_DATA_POINTS_THRESHOLD = 3   # Minimum data points required for score to be considered valid
MAX_PESSIMIST_RISK_THRESHOLD = 0.7 # Maximum risk score allowed by Pessimist
# --- End Batch 20.2 ---

# --- Batch 20.2: Import Agent related components ---
# Assuming these are correctly placed relative to project root
from app.registry import get_agent
from app.schemas.agent_input.pessimist_agent_input import PessimistRiskAssessmentInput
from app.utils.status import ResultStatus
# --- End Batch 20.2 ---

# --- Helper functions for JSON loading/saving ---
def load_json(path):
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content:
                # Handle empty files based on expected structure
                if os.path.basename(path) in ["debt_token_budget.json", "agent_trust_score.json"]:
                    logger.warning(f"Warning: File {path} is empty. Returning None.")
                    return None
                elif os.path.basename(path) in ["mutation_request.json"]:
                     return {} # Default empty dict
                else:
                    # Default to list for logs like mutation_log, mutation_backlog, justification, operator_override
                    return [] 
            return json.loads(content)
    except FileNotFoundError:
        logger.warning(f"Warning: Log file not found at {path}. Returning default empty structure.")
        if os.path.basename(path) in ["debt_token_budget.json", "agent_trust_score.json"]:
            return None
        elif os.path.basename(path) in ["mutation_request.json"]:
             return {}
        else:
            return []
    except json.JSONDecodeError:
        logger.warning(f"Warning: Could not decode JSON from {path}. Returning default empty structure.")
        if os.path.basename(path) in ["debt_token_budget.json", "agent_trust_score.json"]:
            return None
        elif os.path.basename(path) in ["mutation_request.json"]:
             return {}
        else:
            return []

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
# --- End Helper functions ---

def log_guard_event(loop_id, mutation_details, status, reason=""):
    """Logs mutation events (attempt, success, failure) to the guard log."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "loop_id": loop_id,
        "status": status, # e.g., 'attempting', 'approved', 'rejected', 'success', 'failure'
        "mutation_details": mutation_details,
        "reason": reason
    }
    os.makedirs(os.path.dirname(GUARD_LOG_PATH), exist_ok=True)
    with open(GUARD_LOG_PATH, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def log_intended_mutation(loop_id, file_path, action):
    """Logs the intention to perform a mutation to mutation_log.json."""
    mutation_log = load_json(MUTATION_LOG_PATH)
    if not isinstance(mutation_log, list):
        logger.warning(f"Warning: {MUTATION_LOG_PATH} is not a list. Reinitializing.")
        mutation_log = []
    
    entry = {
        "loop_id": loop_id,
        "timestamp_intended": datetime.utcnow().isoformat(),
        "timestamp_finalized": None,
        "component_modified": file_path,
        "diff_summary": f"{action.capitalize()} operation intended",
        "status": "intended",
        "reason": None
    }
    mutation_log.append(entry)
    save_json(mutation_log, MUTATION_LOG_PATH)
    logger.info(f"Mutation Guard: Logged intended mutation for {file_path} in loop {loop_id}")

# --- Batch 20.3: Function to log to mutation backlog --- 
def log_to_mutation_backlog(loop_id, agent_id, request_params, rejection_reason):
    """Logs a rejected mutation request to the backlog."""
    backlog = load_json(MUTATION_BACKLOG_PATH)
    if not isinstance(backlog, list):
        logger.warning(f"Warning: {MUTATION_BACKLOG_PATH} is not a list. Reinitializing.")
        backlog = []
    
    entry = {
        "backlog_id": f"bklg_{loop_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}", # Unique ID
        "loop_id": loop_id,
        "timestamp_added": datetime.utcnow().isoformat(),
        "responsible_agent_id": agent_id,
        "mutation_request": request_params,
        "rejection_reason": rejection_reason,
        "status": "pending", # Initial status in backlog
        "priority": 0.5 # Default priority, can be adjusted later
    }
    backlog.append(entry)
    save_json(backlog, MUTATION_BACKLOG_PATH)
    logger.info(f"Mutation Guard: Added rejected mutation from loop {loop_id} to backlog. Reason: {rejection_reason}")
# --- End Batch 20.3 --- 

def execute_file_write(file_path, content):
    """Attempts to write content to a file."""
    if not file_path or not os.path.isabs(file_path):
        raise ValueError("Invalid or non-absolute file path provided.")
    parent_dir = os.path.dirname(file_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

# Batch 20.2: Make function async to call Pessimist
async def process_mutation_request(loop_id, mutation_details):
    """Processes a mutation request, performing governance checks, logging intention, attempting execution, and handling errors."""
    logger.info(f"Mutation Guard: Received mutation request for loop {loop_id}: {mutation_details}")
    
    # Extract request parameters (assuming structure from intent)
    request_params = mutation_details.get("intent_params", {}).get("mutation_request", {})
    responsible_agent_id = mutation_details.get("responsible_agent_id") or request_params.get("responsible_agent_id", "unknown_agent") # Get agent ID
    action = request_params.get('action')
    file_path = request_params.get('file_path')
    content = request_params.get('content') # Specific to 'write'
    estimated_cost = request_params.get('estimated_cost', 0.1) # Default cost if not provided
    requires_operator_review = mutation_details.get("requires_operator_review", False) # Batch 20.4: Check if operator review was required

    try:
        # --- Batch 20.2: Pessimist Risk Assessment --- 
        logger.info(f"Mutation Guard: Invoking Pessimist for risk assessment...")
        PessimistAgentClass = get_agent("pessimist")
        if not PessimistAgentClass:
            raise RuntimeError("Mutation request rejected: Pessimist agent not found in registry.")
        
        pessimist_agent = PessimistAgentClass()
        
        logger.info(f"Mutation Guard: Preparing Pessimist payload for loop {loop_id}...")
        pessimist_payload = PessimistRiskAssessmentInput(
            loop_id=loop_id,
            mutation_request_details=request_params 
        )
        logger.info(f"Mutation Guard: Pessimist payload created: {pessimist_payload.model_dump_json(indent=2)}")
        logger.info(f"Mutation Guard: Calling pessimist_agent.run for loop {loop_id}...")
        
        pessimist_result = None
        try:
            pessimist_result = await pessimist_agent.run(pessimist_payload)
            logger.info(f"Mutation Guard: pessimist_agent.run completed for loop {loop_id}.")
        except Exception as agent_call_error:
            tb_str = traceback.format_exc()
            logger.error(f"Mutation Guard: Exception occurred DURING await pessimist_agent.run for loop {loop_id}. Type: {type(agent_call_error).__name__}, Error: {agent_call_error}. Traceback: {tb_str}")
            raise agent_call_error
        
        if pessimist_result is None:
             raise RuntimeError("Pessimist agent call did not return a result.")

        if pessimist_result.status != ResultStatus.SUCCESS:
            error_msg = pessimist_result.error_message or "Pessimist assessment failed without specific error."
            raise PermissionError(f"Mutation request rejected: Pessimist assessment failed. Reason: {error_msg}")
        
        pessimist_risk_score = pessimist_result.risk_score
        pessimist_justification = pessimist_result.justification
        logger.info(f"Mutation Guard: Pessimist assessment complete. Score: {pessimist_risk_score:.3f}. Justification: {pessimist_justification}")
        
        if pessimist_risk_score > MAX_PESSIMIST_RISK_THRESHOLD:
            raise PermissionError(f"Mutation request rejected: Pessimist risk score ({pessimist_risk_score:.3f}) exceeds threshold ({MAX_PESSIMIST_RISK_THRESHOLD}). Reason: {pessimist_justification}")
        logger.info(f"Mutation Guard: Pessimist risk check passed ({pessimist_risk_score:.3f} <= {MAX_PESSIMIST_RISK_THRESHOLD}).")
        # --- End Batch 20.2 Pessimist Check ---

        # --- Batch 20.1: Basic Governance Checks --- 
        logger.info("Mutation Guard: Performing basic governance checks...")
        # 1. Format Check
        if not action or not file_path:
             raise ValueError("Mutation request rejected: Missing 'action' or 'file_path'.")
        if action == 'write' and content is None:
             raise ValueError("Mutation request rejected: Missing 'content' for 'write' action.")
        if not isinstance(estimated_cost, (int, float)) or estimated_cost < 0:
             raise ValueError("Mutation request rejected: Invalid 'estimated_cost'. Must be a non-negative number.")
        logger.info("Mutation Guard: Format check passed.")

        # 2. Budget Check
        budget_data = load_json(DEBT_TOKEN_BUDGET_PATH)
        if budget_data is None or 'current_budget' not in budget_data:
            raise RuntimeError(f"Mutation request rejected: Cannot read current budget from {DEBT_TOKEN_BUDGET_PATH}.")
        current_budget = budget_data['current_budget']
        if current_budget < estimated_cost:
            raise PermissionError(f"Mutation request rejected: Insufficient budget. Required: {estimated_cost}, Available: {current_budget}.")
        logger.info(f"Mutation Guard: Budget check passed. Required: {estimated_cost}, Available: {current_budget}.")
        # --- End Batch 20.1 Checks ---

        # --- Batch 20.2: Trust Score Check ---
        logger.info(f"Mutation Guard: Performing trust check for agent '{responsible_agent_id}'...")
        trust_scores_data = load_json(AGENT_TRUST_SCORE_PATH)
        agent_score_info = None
        if isinstance(trust_scores_data, list):
            for agent_info in trust_scores_data:
                if agent_info.get('agent_id') == responsible_agent_id:
                    agent_score_info = agent_info
                    break
        
        if agent_score_info is None:
            raise PermissionError(f"Mutation request rejected: Trust score not found for agent '{responsible_agent_id}'.")
        
        agent_score = agent_score_info.get('score')
        data_points = agent_score_info.get('data_points_used', 0)

        if agent_score is None:
             raise PermissionError(f"Mutation request rejected: Invalid trust score data for agent '{responsible_agent_id}'.")

        if data_points < MIN_DATA_POINTS_THRESHOLD:
            raise PermissionError(f"Mutation request rejected: Insufficient data points ({data_points}) for agent '{responsible_agent_id}' trust score. Minimum required: {MIN_DATA_POINTS_THRESHOLD}.")
        logger.info(f"Mutation Guard: Data points check passed ({data_points} >= {MIN_DATA_POINTS_THRESHOLD}).")

        if agent_score < MIN_TRUST_SCORE_THRESHOLD:
            raise PermissionError(f"Mutation request rejected: Agent '{responsible_agent_id}' trust score ({agent_score:.3f}) is below threshold ({MIN_TRUST_SCORE_THRESHOLD}).")
        logger.info(f"Mutation Guard: Trust score check passed ({agent_score:.3f} >= {MIN_TRUST_SCORE_THRESHOLD}).")
        # --- End Batch 20.2 Check ---

        # --- Batch 20.4: Critic Approval Check ---
        logger.info(f"Mutation Guard: Performing Critic approval check for loop {loop_id}...")
        justification_log = load_json(LOOP_JUSTIFICATION_LOG_PATH)
        critic_approved = False
        if isinstance(justification_log, list):
            for entry in reversed(justification_log): # Check recent entries first
                if entry.get("loop_id") == loop_id and entry.get("agent_id") == "Critic":
                    if entry.get("decision") == "approved":
                        critic_approved = True
                        logger.info(f"Mutation Guard: Critic approval found for loop {loop_id}.")
                        break
                    else:
                        # Found Critic decision but it wasn't approval
                        logger.info(f"Mutation Guard: Critic decision found for loop {loop_id}, but was not 'approved' (Decision: {entry.get('decision')}).")
                        break # Stop searching once a critic decision for this loop is found
        
        if not critic_approved:
            raise PermissionError(f"Mutation request rejected: Critic approval not found or decision was not 'approved' for loop {loop_id}.")
        logger.info(f"Mutation Guard: Critic approval check passed.")
        # --- End Batch 20.4 Critic Check ---

        # --- Batch 20.4: Operator Approval Check (if required) ---
        # This check happens *after* other checks, assuming Operator review is the final gate
        if requires_operator_review:
            logger.info(f"Mutation Guard: Performing Operator approval check for loop {loop_id} (review was required)...")
            operator_log = load_json(OPERATOR_OVERRIDE_LOG_PATH)
            operator_approved = False
            if isinstance(operator_log, list):
                for entry in reversed(operator_log):
                    if entry.get("loop_id") == loop_id:
                        if entry.get("decision") == "approved":
                            operator_approved = True
                            logger.info(f"Mutation Guard: Operator approval found for loop {loop_id}.")
                            break
                        else:
                            # Found Operator decision but it wasn't approval
                            logger.info(f"Mutation Guard: Operator decision found for loop {loop_id}, but was not 'approved' (Decision: {entry.get('decision')}).")
                            break # Stop searching once an operator decision for this loop is found
            
            if not operator_approved:
                raise PermissionError(f"Mutation request rejected: Operator approval required but not found or decision was not 'approved' for loop {loop_id}.")
            logger.info(f"Mutation Guard: Operator approval check passed.")
        else:
            logger.info(f"Mutation Guard: Operator approval check skipped for loop {loop_id} (review was not required)...")
        # --- End Batch 20.4 Operator Check ---

        # If all checks pass, log attempt and intention
        log_guard_event(loop_id, request_params, 'approved', reason="Pessimist, format, budget, trust, Critic, and Operator (if required) checks passed.")
        log_intended_mutation(loop_id, file_path, action)

        # Proceed with execution
        mutated_files_list = []
        mutation_success = False
        mutation_message = ""

        if action == 'write':
            execute_file_write(file_path, content)
            logger.info(f"Mutation Guard: Successfully executed write action for {file_path}")
            log_guard_event(loop_id, request_params, 'success') # Log execution success
            mutated_files_list.append(file_path)
            mutation_success = True
            mutation_message = f"Successfully wrote to {file_path}"
        # Add other actions like 'append', 'delete' here later
        else:
            raise ValueError(f"Unsupported mutation action: {action}")

    except (ValueError, PermissionError, RuntimeError, Exception) as e:
        # --- Batch 20.3: Log to Backlog on Rejection --- 
        if 'agent_call_error' in locals() and e is agent_call_error:
             error_message = f"Mutation failed during agent call: {type(e).__name__} - {e}"
        else:
             error_message = f"Mutation failed: {type(e).__name__} - {e}"
        logger.error(f"Mutation Guard: {error_message}")
        
        # Log rejection event to guard log
        log_guard_event(loop_id, request_params, 'rejected', reason=error_message)
        
        # Log the rejected request to the backlog
        log_to_mutation_backlog(loop_id, responsible_agent_id, request_params, error_message)
        # --- End Batch 20.3 Modification --- 

        mutation_success = False
        mutation_message = error_message # Return the error message
        mutated_files_list = []

    # Return success status, list of mutated files, and a message
    return mutation_success, mutated_files_list, mutation_message

# Async wrapper for direct execution if needed
async def main_async():
    logger.info("Mutation Guard (Execution Enabled with Governance Checks - Async)")
    # Ensure budget file exists for testing
    save_json({"current_budget": 1.0, "last_updated": datetime.utcnow().isoformat()+"Z"}, DEBT_TOKEN_BUDGET_PATH)
    # Ensure trust score file exists for testing
    save_json([
        {"agent_id": "test_agent_ok", "score": 0.7, "data_points_used": 5, "last_updated": "", "contributing_factors_summary": ""},
        {"agent_id": "test_agent_low_score", "score": 0.2, "data_points_used": 10, "last_updated": "", "contributing_factors_summary": ""},
        {"agent_id": "test_agent_low_data", "score": 0.8, "data_points_used": 1, "last_updated": "", "contributing_factors_summary": ""},
        {"agent_id": "test_agent_high_risk", "score": 0.8, "data_points_used": 5, "last_updated": "", "contributing_factors_summary": ""} # For Pessimist test
    ], AGENT_TRUST_SCORE_PATH)
    # Ensure backlog file exists and is empty for testing
    save_json([], MUTATION_BACKLOG_PATH)
    # Ensure justification log exists for testing
    save_json([
        {"loop_id": "loop_0022a", "agent_id": "Critic", "decision": "approved", "justification": "Plan aligns with intent.", "timestamp": "..."},
        {"loop_id": "loop_0022b", "agent_id": "Critic", "decision": "rejected", "justification": "Plan deviates significantly.", "timestamp": "..."},
        {"loop_id": "loop_0022c", "agent_id": "Critic", "decision": "approved", "justification": "Plan aligns.", "timestamp": "..."},
        {"loop_id": "loop_0022d", "agent_id": "Critic", "decision": "approved", "justification": "Plan aligns.", "timestamp": "..."}
    ], LOOP_JUSTIFICATION_LOG_PATH)
    # Ensure operator log exists for testing
    save_json([
        {"loop_id": "loop_0022c", "decision": "approved", "reason": "Test approval", "timestamp": "..."},
        {"loop_id": "loop_0022d", "decision": "rejected", "reason": "Test rejection", "timestamp": "..."}
    ], OPERATOR_OVERRIDE_LOG_PATH)

    # Example request - Success (Critic Approved, Operator Not Required)
    example_request_success_critic = {
        "responsible_agent_id": "test_agent_ok",
        "intent_params": {
            "mutation_request": {
                "action": "write",
                "file_path": "/home/ubuntu/test_mutation_critic_success.txt",
                "content": "Critic approved this.",
                "estimated_cost": 0.1
            }
        },
        "requires_operator_review": False
    }
    success, files, msg = await process_mutation_request("loop_0022a", example_request_success_critic)
    print(f"Test loop_0022a (Critic Success): Success={success}, Files={files}, Message={msg}")

    # Example request - Fail (Critic Rejected)
    example_request_fail_critic = {
        "responsible_agent_id": "test_agent_ok",
        "intent_params": {
            "mutation_request": {
                "action": "write",
                "file_path": "/home/ubuntu/test_mutation_critic_fail.txt",
                "content": "Critic rejected this.",
                "estimated_cost": 0.1
            }
        },
        "requires_operator_review": False
    }
    success, files, msg = await process_mutation_request("loop_0022b", example_request_fail_critic)
    print(f"Test loop_0022b (Critic Fail): Success={success}, Files={files}, Message={msg}")

    # Example request - Success (Critic & Operator Approved)
    example_request_success_op = {
        "responsible_agent_id": "test_agent_ok",
        "intent_params": {
            "mutation_request": {
                "action": "write",
                "file_path": "/home/ubuntu/test_mutation_op_success.txt",
                "content": "Operator approved this.",
                "estimated_cost": 0.1
            }
        },
        "requires_operator_review": True
    }
    success, files, msg = await process_mutation_request("loop_0022c", example_request_success_op)
    print(f"Test loop_0022c (Operator Success): Success={success}, Files={files}, Message={msg}")

    # Example request - Fail (Operator Rejected)
    example_request_fail_op = {
        "responsible_agent_id": "test_agent_ok",
        "intent_params": {
            "mutation_request": {
                "action": "write",
                "file_path": "/home/ubuntu/test_mutation_op_fail.txt",
                "content": "Operator rejected this.",
                "estimated_cost": 0.1
            }
        },
        "requires_operator_review": True
    }
    success, files, msg = await process_mutation_request("loop_0022d", example_request_fail_op)
    print(f"Test loop_0022d (Operator Fail): Success={success}, Files={files}, Message={msg}")

if __name__ == "__main__":
    # asyncio.run(main_async()) # Keep commented out unless direct testing is needed
    pass

