#!/usr/bin/env python3
import argparse
import json
import os
import sys

# Add the project root to the Python path to allow importing app modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

from app.core.plan_escalation_detector import PlanEscalationDetector

def main():
    parser = argparse.ArgumentParser(description="Run plan escalation check for a given loop_id.")
    parser.add_argument("loop_id", help="The loop_id to check for plan escalation.")
    parser.add_argument("--config", help="Path to a JSON config file for fallback logic.", default=None)
    
    args = parser.parse_args()

    loop_id = args.loop_id
    fallback_config = None

    if args.config:
        try:
            with open(args.config, "r") as f:
                fallback_config = json.load(f)
            print(f"Loaded fallback configuration from: {args.config}")
        except Exception as e:
            print(f"Error loading fallback configuration from {args.config}: {e}. Using default fallback settings.")
            # Default config will be handled by PlanEscalationDetector if None is passed

    # Define paths to log files (these could also be configurable or derived)
    base_log_path = os.path.join(PROJECT_ROOT, "app", "logs") # /home/ubuntu/personal-ai-agent/app/logs
    multi_plan_comparison_path = os.path.join(base_log_path, "multi_plan_comparison.json")
    plan_rejection_log_path = os.path.join(base_log_path, "plan_rejection_log.json")
    loop_plan_selection_log_path = os.path.join(base_log_path, "loop_plan_selection_log.json")
    plan_escalation_log_path = os.path.join(base_log_path, "plan_escalation_log.json")

    print(f"Initializing PlanEscalationDetector for loop_id: {loop_id}")
    print(f"  Multi-plan comparison log: {multi_plan_comparison_path}")
    print(f"  Plan rejection log: {plan_rejection_log_path}")
    print(f"  Loop plan selection log: {loop_plan_selection_log_path}")
    print(f"  Plan escalation log: {plan_escalation_log_path}")
    print(f"  Fallback config: {fallback_config}")

    # Ensure log directory exists
    os.makedirs(base_log_path, exist_ok=True)

    detector = PlanEscalationDetector(
        multi_plan_comparison_path=multi_plan_comparison_path,
        plan_rejection_log_path=plan_rejection_log_path,
        loop_plan_selection_log_path=loop_plan_selection_log_path,
        plan_escalation_log_path=plan_escalation_log_path,
        fallback_config=fallback_config
    )

    print(f"\nChecking for escalation for loop_id: {loop_id}...")
    escalation_result = detector.check_for_escalation(loop_id)

    if escalation_result:
        print(f"\nEscalation occurred for loop_id {loop_id}.")
        print(f"  Log Entry ID: {escalation_result.get('log_entry_id')}")
        print(f"  Reason: {escalation_result.get('escalation_reason')}")
        print(f"  Recommended Action: {escalation_result.get('recommended_action')}")
        print(f"  Operator Alert Flag: {escalation_result.get('operator_alert_flag')}")
        print(f"  Fallback Triggered: {escalation_result.get('fallback_triggered')}")
        if escalation_result.get('fallback_triggered'):
            print(f"  Fallback Details: {escalation_result.get('fallback_details')}")
        print(f"  Details logged to: {plan_escalation_log_path}")
    else:
        print(f"\nNo escalation was necessary for loop_id {loop_id} based on current logs.")

if __name__ == "__main__":
    main()

