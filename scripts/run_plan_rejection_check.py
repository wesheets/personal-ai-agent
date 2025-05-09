#!/usr/bin/env python3
import argparse
import sys
import os

# Adjust path to import from app.core
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
APP_DIR = os.path.join(PARENT_DIR, "app")
sys.path.insert(0, PARENT_DIR) # Add personal-ai-agent directory to path

from core.plan_rejector import PlanRejector

def main():
    parser = argparse.ArgumentParser(description="Run Plan Rejection Check for a given loop_id.")
    parser.add_argument("loop_id", type=str, help="The loop_id to process for plan rejection.")
    
    args = parser.parse_args()
    
    print(f"Initiating plan rejection check for loop_id: {args.loop_id}")
    
    # Define paths to the log files, assuming they are in app/logs and app/memory relative to personal-ai-agent root
    # These paths should match those used in the PlanRejector class or be configurable
    base_path = PARENT_DIR # /home/ubuntu/personal-ai-agent
    plan_selection_log_path = os.path.join(base_path, "app", "logs", "loop_plan_selection_log.json")
    rejection_log_path = os.path.join(base_path, "app", "logs", "plan_rejection_log.json")
    emotion_state_path = os.path.join(base_path, "app", "memory", "agent_emotion_state.json")
    trust_score_path = os.path.join(base_path, "app", "memory", "agent_trust_score.json") # Hypothetical
    invariants_path = os.path.join(base_path, "app", "memory", "promethios_invariants.json") # Hypothetical

    # Ensure log directories exist
    os.makedirs(os.path.join(base_path, "app", "logs"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "app", "memory"), exist_ok=True)

    rejector = PlanRejector(
        plan_selection_log_path=plan_selection_log_path,
        rejection_log_path=rejection_log_path,
        emotion_state_path=emotion_state_path,
        trust_score_path=trust_score_path,
        invariants_path=invariants_path
    )
    
    rejection_result = rejector.process_rejection_for_loop(args.loop_id)
    
    if rejection_result:
        print(f"Plan rejection processed for loop_id {args.loop_id}. Details logged.")
    else:
        # This could mean either the plan was approved or no plan was found for the loop_id
        # The PlanRejector class prints specific messages for these cases.
        print(f"Plan rejection check completed for loop_id {args.loop_id}.")

if __name__ == "__main__":
    main()

