import os
import datetime
import time
import json
import uuid
import random

EXECUTION_LOG_DIR = "/home/ubuntu/personal-ai-agent/app/logs"
RUNTIME_ERROR_LOG_PATH = "/home/ubuntu/personal-ai-agent/app/memory/runtime_error_log.json"
OPERATOR_ESCALATION_QUEUE_PATH = "/home/ubuntu/personal-ai-agent/app/memory/operator_escalation_queue.json"

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

ERROR_CATEGORIES = {
    "ToolFailure": "ToolFailure", "ValidationError": "ValidationError", "MemoryAccessError": "MemoryAccessError",
    "SchemaMismatch": "SchemaMismatch", "ResourceUnavailable": "ResourceUnavailable", "TimeoutError": "TimeoutError",
    "UncaughtException": "UncaughtException", "GovernanceViolation": "GovernanceViolation",
    "OperatorInterventionRequired": "OperatorInterventionRequired", "UnknownError": "UnknownError",
    "CriticalInvariantViolation": "CriticalInvariantViolation",
    "UnhandledAgentException": "UnhandledAgentException",
    "UnknownRuntimeException": "UnknownRuntimeException"
}

CRITICAL_ERRORS_FOR_ESCALATION = [
    ERROR_CATEGORIES["CriticalInvariantViolation"],
    ERROR_CATEGORIES["UnhandledAgentException"],
    ERROR_CATEGORIES["UnknownRuntimeException"],
    ERROR_CATEGORIES["UncaughtException"]
]

def write_execution_log(loop_id, batch_id, content):
    log_file_path = os.path.join(EXECUTION_LOG_DIR, str(loop_id) + "_execution.log")
    try:
        os.makedirs(EXECUTION_LOG_DIR, exist_ok=True)
        with open(log_file_path, "a") as f:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            f.write(str(timestamp) + " - " + str(content) + "\n") # Ultra-safe concatenation with escaped newline
    except Exception as e:
        print("Failed to write execution log for " + str(loop_id) + ": " + str(e))

def log_runtime_error(loop_id, batch_id, error_category, error_message, severity,
                      error_details=None, overall_recovery_strategy="None",
                      overall_recovery_outcome="NotAttempted", recovery_attempts_list=None):
    timestamp_now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    log_entry = {
        "timestamp": timestamp_now,
        "loop_id": loop_id,
        "batch_id": batch_id,
        "error_category": error_category,
        "error_message": error_message,
        "error_details": error_details if error_details else {},
        "recovery_attempted": overall_recovery_strategy,
        "recovery_outcome": overall_recovery_outcome,
        "recovery_attempts": recovery_attempts_list if recovery_attempts_list else [],
        "severity": severity
    }
    try:
        data = []
        try:
            with open(RUNTIME_ERROR_LOG_PATH, "r") as f_read:
                file_content = f_read.read()
                if file_content.strip():
                    data = json.loads(file_content)
                    if not isinstance(data, list):
                        print("Warning: " + RUNTIME_ERROR_LOG_PATH + " did not contain a list. Reinitializing.")
                        data = []
        except FileNotFoundError:
            print("Warning: " + RUNTIME_ERROR_LOG_PATH + " not found. Will create a new one.")
        except json.JSONDecodeError:
            print("Warning: " + RUNTIME_ERROR_LOG_PATH + " contained invalid JSON. Reinitializing.")
            data = []
        data.append(log_entry)
        with open(RUNTIME_ERROR_LOG_PATH, "w") as f_write:
            json.dump(data, f_write, indent=2)
        return timestamp_now
    except Exception as e:
        print("Failed to log error to " + RUNTIME_ERROR_LOG_PATH + " for " + str(loop_id) + ": " + str(e))
        return None

def log_operator_escalation(loop_id, batch_id, error_type, summary, recommended_action, confidence, error_ref_timestamp):
    escalation_entry = {
        "escalation_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "loop_id": loop_id,
        "batch_id": batch_id,
        "error_id_ref": error_ref_timestamp,
        "reason": error_type,
        "summary": summary,
        "recommended_operator_action": recommended_action,
        "confidence_in_escalation_need": confidence,
        "status": "pending_review",
        "operator_notes": "",
        "payload": {}
    }
    try:
        data = []
        try:
            with open(OPERATOR_ESCALATION_QUEUE_PATH, "r") as f_read:
                file_content = f_read.read()
                if file_content.strip():
                    data = json.loads(file_content)
                    if not isinstance(data, list):
                        print("Warning: " + OPERATOR_ESCALATION_QUEUE_PATH + " did not contain a list. Reinitializing.")
                        data = []
        except FileNotFoundError:
            print("Warning: " + OPERATOR_ESCALATION_QUEUE_PATH + " not found. Will create a new one.")
            with open(OPERATOR_ESCALATION_QUEUE_PATH, "w") as f_init:
                json.dump([], f_init)
        except json.JSONDecodeError:
            print("Warning: " + OPERATOR_ESCALATION_QUEUE_PATH + " contained invalid JSON. Reinitializing.")
            data = []
        data.append(escalation_entry)
        with open(OPERATOR_ESCALATION_QUEUE_PATH, "w") as f_write:
            json.dump(data, f_write, indent=2)
    except Exception as e:
        print("Failed to log escalation to " + OPERATOR_ESCALATION_QUEUE_PATH + " for " + str(loop_id) + ": " + str(e))

def simulated_operation(operation_name, current_attempt_num_for_failure, total_attempts_to_fail, error_type_to_raise, loop_id, batch_id):
    if current_attempt_num_for_failure <= total_attempts_to_fail:
        raise Exception("Simulated " + str(error_type_to_raise) + " in " + str(operation_name))
    return str(operation_name) + " completed successfully."

def simulate_loop_0074_retry_success(loop_id, batch_id):
    print("\n") # Explicit newline print
    print("--- Simulating " + str(loop_id) + " for batch " + str(batch_id) + ": Retry Success Case ---")
    write_execution_log(loop_id, batch_id, "Starting " + str(loop_id) + " simulation: Retry Success Case.")
    op_name = "FetchExternalAPIResource"
    error_cat = ERROR_CATEGORIES["ToolFailure"]
    attempts_to_fail = 1
    recovery_attempts_log = []
    op_succeeded = False
    final_outcome = "Failure"
    for attempt_num in range(1, MAX_RETRIES + 2):
        if op_succeeded: break
        if attempt_num > MAX_RETRIES + 1 : break
        attempt_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        current_recovery_attempt_details = {"attempt_number": attempt_num, "timestamp": attempt_timestamp, "strategy_used": "Retry", "parameters": {"max_retries_configured": MAX_RETRIES, "delay_seconds_configured": RETRY_DELAY_SECONDS}, "outcome": "Failure", "details": ""}
        try:
            write_execution_log(loop_id, batch_id, "Attempting " + op_name + ", try #" + str(attempt_num))
            print("Attempting " + op_name + ", try #" + str(attempt_num))
            simulated_operation(op_name, attempt_num, attempts_to_fail, error_cat, loop_id, batch_id)
            op_succeeded = True
            current_recovery_attempt_details["outcome"] = "Success"
            current_recovery_attempt_details["details"] = op_name + " succeeded on attempt " + str(attempt_num) + "."
            final_outcome = "Success"
            write_execution_log(loop_id, batch_id, op_name + " succeeded on try #" + str(attempt_num) + ".")
            print(op_name + " succeeded on try #" + str(attempt_num) + ".")
        except Exception as e:
            write_execution_log(loop_id, batch_id, op_name + " failed on try #" + str(attempt_num) + ": " + str(e))
            print(op_name + " failed on try #" + str(attempt_num) + ": " + str(e))
            current_recovery_attempt_details["details"] = "Failed on attempt " + str(attempt_num) + ": " + str(e)
            if attempt_num <= MAX_RETRIES:
                write_execution_log(loop_id, batch_id, "Retrying " + op_name + " after " + str(RETRY_DELAY_SECONDS) + "s...")
                print("Retrying " + op_name + " after " + str(RETRY_DELAY_SECONDS) + "s...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                write_execution_log(loop_id, batch_id, op_name + " unexpectedly failed all retries despite low attempts_to_fail.")
                print(op_name + " unexpectedly failed all retries.")
        recovery_attempts_log.append(current_recovery_attempt_details)
        if op_succeeded : break
    log_runtime_error(loop_id=loop_id, batch_id=batch_id, error_category=error_cat, error_message=op_name + " encountered " + error_cat + ". Overall recovery outcome: " + final_outcome + ".", severity="Warning" if final_outcome == "Success" else "Error", error_details={"component": op_name, "initial_failures_simulated": attempts_to_fail}, overall_recovery_strategy="Retry", overall_recovery_outcome=final_outcome, recovery_attempts_list=recovery_attempts_log)
    write_execution_log(loop_id, batch_id, "Finished " + str(loop_id) + " simulation.")
    print("--- Finished simulation for " + str(loop_id) + " ---")

def simulate_loop_0075_retry_fail_safe_halt(loop_id, batch_id):
    print("\n")
    print("--- Simulating " + str(loop_id) + " for batch " + str(batch_id) + ": Retry Fail -> Safe Halt Case ---")
    write_execution_log(loop_id, batch_id, "Starting " + str(loop_id) + " simulation: Retry Fail -> Safe Halt Case.")
    op_name = "CriticalDataValidation"
    error_cat = ERROR_CATEGORIES["ValidationError"]
    attempts_to_fail = MAX_RETRIES
    recovery_attempts_log = []
    final_outcome = "Failure"
    overall_strategy = "Retry"
    for attempt_num in range(1, MAX_RETRIES + 1):
        attempt_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        current_recovery_attempt_details = {"attempt_number": attempt_num, "timestamp": attempt_timestamp, "strategy_used": "Retry", "parameters": {"max_retries_configured": MAX_RETRIES, "delay_seconds_configured": RETRY_DELAY_SECONDS}, "outcome": "Failure", "details": ""}
        try:
            write_execution_log(loop_id, batch_id, "Attempting " + op_name + ", try #" + str(attempt_num))
            print("Attempting " + op_name + ", try #" + str(attempt_num))
            simulated_operation(op_name, attempt_num, attempts_to_fail, error_cat, loop_id, batch_id)
            current_recovery_attempt_details["outcome"] = "Success"
            current_recovery_attempt_details["details"] = op_name + " unexpectedly succeeded."
            final_outcome = "Success"
            write_execution_log(loop_id, batch_id, op_name + " unexpectedly succeeded.")
            print(op_name + " unexpectedly succeeded.")
            recovery_attempts_log.append(current_recovery_attempt_details)
            break
        except Exception as e:
            write_execution_log(loop_id, batch_id, op_name + " failed on try #" + str(attempt_num) + ": " + str(e))
            print(op_name + " failed on try #" + str(attempt_num) + ": " + str(e))
            current_recovery_attempt_details["details"] = "Failed on attempt " + str(attempt_num) + ": " + str(e)
            recovery_attempts_log.append(current_recovery_attempt_details)
            if attempt_num < MAX_RETRIES:
                write_execution_log(loop_id, batch_id, "Retrying " + op_name + " after " + str(RETRY_DELAY_SECONDS) + "s...")
                print("Retrying " + op_name + " after " + str(RETRY_DELAY_SECONDS) + "s...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                write_execution_log(loop_id, batch_id, op_name + " failed after " + str(MAX_RETRIES) + " retries. Initiating Safe Halt.")
                print(op_name + " failed after " + str(MAX_RETRIES) + " retries. Initiating Safe Halt.")
                final_outcome = "Failure"
                overall_strategy = "SafeHalt"
                log_runtime_error(loop_id=loop_id, batch_id=batch_id, error_category=error_cat, error_message=op_name + " led to Safe Halt after " + str(MAX_RETRIES) + " failed retries for " + error_cat + ".", severity="Critical", error_details={"component": op_name, "reason_for_halt": "Exceeded max recovery attempts for " + error_cat + "."}, overall_recovery_strategy=overall_strategy, overall_recovery_outcome=final_outcome, recovery_attempts_list=recovery_attempts_log)
                write_execution_log(loop_id, batch_id, "SAFE HALT simulated for " + str(loop_id) + " due to " + op_name + " (" + error_cat + ") failure.")
                print("SAFE HALT simulated for " + str(loop_id) + " due to " + op_name + " (" + error_cat + ") failure.")
                break
    write_execution_log(loop_id, batch_id, "Finished " + str(loop_id) + " simulation.")
    print("--- Finished simulation for " + str(loop_id) + " ---")

def simulate_loop_0076_critical_escalation(loop_id, batch_id):
    print("\n")
    print("--- Simulating " + str(loop_id) + " for batch " + str(batch_id) + ": Critical Failure -> Escalation Case ---")
    write_execution_log(loop_id, batch_id, "Starting " + str(loop_id) + " simulation: Critical Failure -> Escalation Case.")
    op_name = "CoreAgentIntegrityCheck"
    error_cat = ERROR_CATEGORIES["UnhandledAgentException"]
    error_message_detail = "Simulated critical " + error_cat + " in " + op_name + "."
    try:
        write_execution_log(loop_id, batch_id, "Attempting critical operation: " + op_name)
        print("Attempting critical operation: " + op_name)
        raise Exception(error_message_detail)
    except Exception as e:
        write_execution_log(loop_id, batch_id, "Critical error caught in " + str(loop_id) + ": " + str(e))
        print("Critical error caught in " + str(loop_id) + ": " + str(e))
        error_ref_ts = log_runtime_error(loop_id=loop_id, batch_id=batch_id, error_category=error_cat, error_message=str(e), severity="Critical", error_details={"component": op_name, "context": "Simulating direct critical failure leading to escalation."}, overall_recovery_strategy="EscalateToOperator", overall_recovery_outcome="Failure")
        if error_ref_ts:
            log_operator_escalation(loop_id=loop_id, batch_id=batch_id, error_type=error_cat, summary="Critical error (" + error_cat + ") in " + op_name + ". Loop halted for review.", recommended_action="Operator review: Investigate " + error_cat + " in " + op_name + ". Check runtime logs.", confidence=1.0, error_ref_timestamp=error_ref_ts)
        write_execution_log(loop_id, batch_id, "CRITICAL: Loop " + str(loop_id) + " halted due to " + error_cat + ". Escalation logged. Awaiting Operator review (simulation)...")
        print("CRITICAL: Loop " + str(loop_id) + " halted due to " + error_cat + ". Awaiting Operator review (simulation)...")
    write_execution_log(loop_id, batch_id, "Finished " + str(loop_id) + " simulation.")
    print("--- Finished simulation for " + str(loop_id) + " ---")

def simulate_loop_0077_compound_failure(loop_id, batch_id):
    print("\n")
    print("--- Simulating " + str(loop_id) + " for batch " + str(batch_id) + ": Compound Failure Case ---")
    write_execution_log(loop_id, batch_id, "Starting " + str(loop_id) + " simulation: Compound Failure Case.")
    op_name1 = "PrimaryDatabaseQuery"
    error_cat1 = ERROR_CATEGORIES["MemoryAccessError"]
    attempts_to_fail1 = MAX_RETRIES
    recovery_attempts_log1 = []
    op1_succeeded = False
    write_execution_log(loop_id, batch_id, "Stage 1: Attempting " + op_name1 + " with potential " + error_cat1)
    print("Stage 1: Attempting " + op_name1 + " with potential " + error_cat1)
    for attempt_num in range(1, MAX_RETRIES + 1):
        attempt_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        current_recovery_attempt_details = {"attempt_number": attempt_num, "timestamp": attempt_timestamp, "strategy_used": "Retry", "parameters": {"max_retries_configured": MAX_RETRIES, "delay_seconds_configured": RETRY_DELAY_SECONDS}, "outcome": "Failure", "details": ""}
        try:
            write_execution_log(loop_id, batch_id, "Attempting " + op_name1 + ", try #" + str(attempt_num))
            print("Attempting " + op_name1 + ", try #" + str(attempt_num))
            simulated_operation(op_name1, attempt_num, attempts_to_fail1, error_cat1, loop_id, batch_id)
            op1_succeeded = True
            current_recovery_attempt_details["outcome"] = "Success"
            current_recovery_attempt_details["details"] = op_name1 + " succeeded on attempt " + str(attempt_num) + "."
            write_execution_log(loop_id, batch_id, op_name1 + " succeeded on try #" + str(attempt_num) + ".")
            print(op_name1 + " succeeded on try #" + str(attempt_num) + ".")
            recovery_attempts_log1.append(current_recovery_attempt_details)
            break
        except Exception as e:
            write_execution_log(loop_id, batch_id, op_name1 + " failed on try #" + str(attempt_num) + ": " + str(e))
            print(op_name1 + " failed on try #" + str(attempt_num) + ": " + str(e))
            current_recovery_attempt_details["details"] = "Failed on attempt " + str(attempt_num) + ": " + str(e)
            recovery_attempts_log1.append(current_recovery_attempt_details)
            if attempt_num < MAX_RETRIES:
                write_execution_log(loop_id, batch_id, "Retrying " + op_name1 + " after " + str(RETRY_DELAY_SECONDS) + "s...")
                print("Retrying " + op_name1 + " after " + str(RETRY_DELAY_SECONDS) + "s...")
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                write_execution_log(loop_id, batch_id, op_name1 + " failed all " + str(MAX_RETRIES) + " retries.")
                print(op_name1 + " failed all " + str(MAX_RETRIES) + " retries.")
    log_runtime_error(loop_id=loop_id, batch_id=batch_id, error_category=error_cat1, error_message=op_name1 + " failed all retries for " + error_cat1 + ". Proceeding to fallback.", severity="Error", error_details={"component": op_name1}, overall_recovery_strategy="Retry", overall_recovery_outcome="Failure" if not op1_succeeded else "Success", recovery_attempts_list=recovery_attempts_log1)
    if not op1_succeeded:
        op_name2 = "FallbackCacheGeneration"
        write_execution_log(loop_id, batch_id, "Stage 2: " + op_name1 + " failed. Attempting fallback operation " + op_name2 + ".")
        print("Stage 2: " + op_name1 + " failed. Attempting fallback operation which will also fail critically.")
        error_cat2 = ERROR_CATEGORIES["CriticalInvariantViolation"]
        error_message_detail2 = "Critical " + error_cat2 + " during fallback operation " + op_name2 + " after " + op_name1 + " failure."
        try:
            raise Exception(error_message_detail2)
        except Exception as e2:
            write_execution_log(loop_id, batch_id, "Critical error during fallback " + op_name2 + " in " + str(loop_id) + ": " + str(e2))
            print("Critical error during fallback in " + str(loop_id) + ": " + str(e2))
            error_ref_ts2 = log_runtime_error(loop_id=loop_id, batch_id=batch_id, error_category=error_cat2, error_message=str(e2), severity="Critical", error_details={"component": op_name2, "context": "Fallback after " + op_name1 + " failure.", "triggering_error_category": error_cat1}, overall_recovery_strategy="EscalateToOperator", overall_recovery_outcome="Failure")
            if error_ref_ts2:
                log_operator_escalation(loop_id=loop_id, batch_id=batch_id, error_type=error_cat2, summary="Critical fallback failure (" + error_cat2 + ") in " + op_name2 + ". Loop halted.", recommended_action="Operator review: Investigate " + error_cat2 + " in fallback " + op_name2 + ". Original error " + error_cat1 + ".", confidence=1.0, error_ref_timestamp=error_ref_ts2)
            write_execution_log(loop_id, batch_id, "CRITICAL: Loop " + str(loop_id) + " halted due to compound failure " + error_cat2 + ". Escalation logged. Awaiting Operator review (simulation)...")
            print("CRITICAL: Loop " + str(loop_id) + " halted due to compound failure leading to " + error_cat2 + ". Awaiting Operator review (simulation)...")
    write_execution_log(loop_id, batch_id, "Finished " + str(loop_id) + " simulation.")
    print("--- Finished simulation for " + str(loop_id) + " ---")

if __name__ == "__main__":
    print("Ultra-Minimal loop_controller.py __main__ block. Use run_loop_XXXX.py for specific log regeneration.")

