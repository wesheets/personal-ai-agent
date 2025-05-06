#!/usr/bin/env python3.11
import json
import os
from datetime import datetime
from collections import defaultdict

# Define paths
BASE_MEMORY_PATH = "/home/ubuntu/personal-ai-agent/app/memory"
JUSTIFICATION_LOG_PATH = os.path.join(BASE_MEMORY_PATH, "loop_justification_log.json")
REGRET_LOG_PATH = os.path.join(BASE_MEMORY_PATH, "loop_regret_score.json")
BLAME_LOG_PATH = os.path.join(BASE_MEMORY_PATH, "agent_blame_log.json")
TRUST_SCORE_PATH = os.path.join(BASE_MEMORY_PATH, "agent_trust_score.json")
REHAB_PATHWAYS_PATH = os.path.join(BASE_MEMORY_PATH, "trust_rehabilitation_pathways.json")
LOOP_SUMMARY_PATH = os.path.join(BASE_MEMORY_PATH, "loop_summary.json") # Added for loop status

def load_json_log(path):
    """Loads a JSON log file, returning an empty list on error."""
    try:
        with open(path, 'r') as f:
            content = f.read()
            if not content.strip():
                return []
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: Log file not found at {path}. Returning empty list.")
        return []
    except json.JSONDecodeError as e:
        print(f"Warning: Could not decode JSON from {path}: {e}. Returning empty list.")
        return []

def save_json(data, path):
    """Saves data to a JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def check_rehab_conditions(pathway, loop_data):
    """Checks if conditions for a specific rehab pathway are met for a loop.
       Basic implementation based on condition_description string matching.
    """
    condition = pathway.get("condition_description", "")
    status = loop_data.get("status")
    confidence = loop_data.get("initial_confidence")
    risk = loop_data.get("initial_risk")
    regret = loop_data.get("regret_score")
    agent_role = loop_data.get("agent_role") # Assumes this is added to loop_data
    critic_decision = loop_data.get("critic_decision") # Assumes this is added
    pessimist_risk = loop_data.get("pessimist_risk_score") # Assumes this is added

    try:
        if pathway["pathway_id"] == "successful_loop_high_confidence":
            return status == 'success' and confidence is not None and confidence > 0.7 and regret is not None and regret <= 0
        elif pathway["pathway_id"] == "successful_loop_low_confidence_surprise":
            return status == 'success' and (
                (confidence is not None and confidence < 0.5) or 
                (risk is not None and risk > 0.7)
            )
        elif pathway["pathway_id"] == "critic_approved_plan":
            # This requires linking justification log entries for critic to the architect's loop
            # Simplified: Assume loop_data contains critic_decision if relevant
            return agent_role == 'architect' and critic_decision == 'approved'
        elif pathway["pathway_id"] == "pessimist_low_risk_assessment":
            # Simplified: Assume loop_data contains pessimist_risk_score if relevant
            return agent_role == 'architect' and pessimist_risk is not None and pessimist_risk < 0.3
    except Exception as e:
        print(f"Error checking condition for pathway {pathway.get('pathway_id')}: {e}")
        return False
    return False

def calculate_trust_scores():
    """Calculates trust scores for agents based on available logs, including rehab pathways."""
    justification_log = load_json_log(JUSTIFICATION_LOG_PATH)
    regret_log = load_json_log(REGRET_LOG_PATH)
    blame_log = load_json_log(BLAME_LOG_PATH)
    trust_scores = load_json_log(TRUST_SCORE_PATH)
    rehab_pathways = load_json_log(REHAB_PATHWAYS_PATH)
    loop_summary = load_json_log(LOOP_SUMMARY_PATH)

    # --- Data Aggregation ---
    agent_data = defaultdict(lambda: {
        'confidence_sum': 0.0,
        'confidence_count': 0,
        'regret_sum': 0.0,
        'regret_count': 0,
        'blame_count': 0,
        'loops': defaultdict(lambda: {
            'initial_confidence': None,
            'initial_risk': None,
            'regret_score': None,
            'status': None,
            'agent_role': None, # Placeholder
            'critic_decision': None, # Placeholder
            'pessimist_risk_score': None # Placeholder
        })
    })

    # Process Justification Log for confidence, roles, decisions
    for entry in justification_log:
        agent_id = entry.get('agent_id')
        loop_id = entry.get('loop_id')
        if not agent_id or not loop_id:
            continue
        
        confidence = entry.get('confidence_score')
        risk = entry.get('risk_score') # Assuming Pessimist logs risk_score
        action = entry.get('action_decision')

        if confidence is not None:
            agent_data[agent_id]['confidence_sum'] += float(confidence)
            agent_data[agent_id]['confidence_count'] += 1
            # Store initial confidence/risk per loop if architect/pessimist
            if agent_id == 'architect' and action == 'Plan Generation':
                 agent_data[agent_id]['loops'][loop_id]['initial_confidence'] = float(confidence)
                 agent_data[agent_id]['loops'][loop_id]['agent_role'] = 'architect'
            if agent_id == 'pessimist' and action == 'Risk Assessment':
                 agent_data[agent_id]['loops'][loop_id]['initial_risk'] = float(risk) if risk is not None else None
                 # Also store pessimist risk score for architect's loop data if architect is involved
                 if 'architect' in agent_data:
                     if loop_id in agent_data['architect']['loops']:
                         agent_data['architect']['loops'][loop_id]['pessimist_risk_score'] = float(risk) if risk is not None else None
        
        # Store critic decision for architect's loop data
        if agent_id == 'critic' and action == 'Plan Review':
             if 'architect' in agent_data:
                 if loop_id in agent_data['architect']['loops']:
                     # Basic assumption: 'Approved' vs 'Rejected'
                     decision = 'approved' if 'Approved' in entry.get('justification_text', '') else 'rejected'
                     agent_data['architect']['loops'][loop_id]['critic_decision'] = decision

    # Process Regret Log
    loop_regret = {entry.get('loop_id'): entry for entry in regret_log if entry.get('loop_id')}
    for agent_id, data in agent_data.items():
        for loop_id, loop_details in data['loops'].items():
            if loop_id in loop_regret:
                regret_entry = loop_regret[loop_id]
                regret_score = regret_entry.get('regret_score')
                if regret_score is not None:
                    data['regret_sum'] += float(regret_score)
                    data['regret_count'] += 1
                    loop_details['regret_score'] = float(regret_score)
                # Use regret log's confidence/risk if justification log didn't capture it
                if loop_details['initial_confidence'] is None:
                    loop_details['initial_confidence'] = regret_entry.get('initial_confidence')
                if loop_details['initial_risk'] is None:
                    loop_details['initial_risk'] = regret_entry.get('initial_risk')

    # Process Loop Summary for status
    loop_status = {entry.get('loop_id'): entry.get('status') for entry in loop_summary if entry.get('loop_id')}
    for agent_id, data in agent_data.items():
        for loop_id, loop_details in data['loops'].items():
             if loop_id in loop_status:
                 loop_details['status'] = loop_status[loop_id]

    # Process Blame Log
    for entry in blame_log:
        agent_id = entry.get('responsible_agent')
        if agent_id:
            agent_data[agent_id]['blame_count'] += 1

    # --- Calculate and Update Scores ---
    updated_trust_scores = {entry.get('agent_id'): entry for entry in trust_scores if entry.get('agent_id')}
    current_time = datetime.utcnow().isoformat() + "Z"

    for agent_id, data in agent_data.items():
        # Calculate Base Score (as before)
        base_score = 0.5
        confidence_factor = 0.0
        regret_factor = 0.0
        blame_factor = 0.0
        data_points = data['confidence_count'] + data['regret_count'] + data['blame_count']

        if data['confidence_count'] > 0:
            avg_confidence = data['confidence_sum'] / data['confidence_count']
            confidence_factor = (avg_confidence - 0.5) * 0.3
        else:
            avg_confidence = None

        if data['regret_count'] > 0:
            avg_regret = data['regret_sum'] / data['regret_count']
            regret_factor = -avg_regret * 0.4
        else:
            avg_regret = None

        if data['blame_count'] > 0:
            blame_factor = -min(data['blame_count'] * 0.1, 0.3)

        calculated_base_score = base_score + confidence_factor + regret_factor + blame_factor

        # Calculate Rehab Bonus
        rehab_bonus = 0.0
        completed_pathways = []
        for loop_id, loop_details in data['loops'].items():
            if loop_details['status']: # Only consider loops with a final status
                for pathway in rehab_pathways:
                    if check_rehab_conditions(pathway, loop_details):
                        rehab_bonus += pathway.get("trust_bonus", 0.0)
                        completed_pathways.append(pathway.get("pathway_id"))
        
        # Apply Rehab Bonus and Clamp Score
        score = calculated_base_score + rehab_bonus
        score = max(0.0, min(1.0, score))

        # Update Summary String
        factors_summary = f"Conf: {f'{avg_confidence:.2f}' if avg_confidence is not None else 'N/A'} (n={data['confidence_count']}) | Regret: {f'{avg_regret:.2f}' if avg_regret is not None else 'N/A'} (n={data['regret_count']}) | Blame: {data['blame_count']}"
        if rehab_bonus > 0:
            factors_summary += f" | Rehab: +{rehab_bonus:.2f} ({','.join(completed_pathways)})"

        updated_trust_scores[agent_id] = {
            'agent_id': agent_id,
            'score': round(score, 3),
            'last_updated': current_time,
            'data_points_used': data_points, # Note: Doesn't include rehab pathway count yet
            'contributing_factors_summary': factors_summary
        }
        print(f"Updated trust score for {agent_id}: {score:.3f} (Base: {calculated_base_score:.3f}, Rehab: {rehab_bonus:.3f})")

    # Save updated scores
    save_json(list(updated_trust_scores.values()), TRUST_SCORE_PATH)
    print(f"Trust scores saved to {TRUST_SCORE_PATH}")

if __name__ == "__main__":
    print("Calculating agent trust scores...")
    calculate_trust_scores()
    print("Trust score calculation complete.")

