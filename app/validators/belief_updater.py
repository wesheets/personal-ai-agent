import json
import os
from datetime import datetime
import uuid
from app.schemas.agents.belief_manager.belief_manager_schemas import BeliefChangeProposal

BELIEF_SURFACE_PATH = "/home/ubuntu/personal-ai-agent-phase21/app/memory/belief_surface.json"
LEGACY_TRACKER_PATH = "/home/ubuntu/personal-ai-agent-phase21/app/memory/legacy_alignment_tracker.json"

def load_json(file_path):
    """Loads JSON data from a file."""
    if not os.path.exists(file_path):
        return [] if file_path == LEGACY_TRACKER_PATH else {}
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {file_path}: {e}")
        # Depending on severity, might raise error or return default
        return [] if file_path == LEGACY_TRACKER_PATH else {}

def save_json(data, file_path):
    """Saves data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving {file_path}: {e}")
        # Handle error appropriately

def apply_belief_update(proposal: BeliefChangeProposal):
    """Applies an approved belief change proposal to the belief surface and logs it."""

    if proposal.status != "approved":
        print(f"Skipping update for proposal {proposal.proposal_id}: Status is {proposal.status}")
        return False

    print(f"Applying approved belief update for proposal {proposal.proposal_id}...")

    # 1. Load Belief Surface
    belief_surface = load_json(BELIEF_SURFACE_PATH)
    original_value = belief_surface.get(proposal.target_belief_key)

    # 2. Apply Change
    change_applied = False
    if proposal.proposed_change_type == "added":
        if proposal.target_belief_key not in belief_surface:
            belief_surface[proposal.target_belief_key] = proposal.proposed_value
            change_applied = True
        else:
            print(f"Warning: Belief key '{proposal.target_belief_key}' already exists. Use 'modified' to change.")
            # Optionally, treat as modification or reject
            belief_surface[proposal.target_belief_key] = proposal.proposed_value # Overwrite for now
            change_applied = True
    elif proposal.proposed_change_type == "modified":
        if proposal.target_belief_key in belief_surface:
            belief_surface[proposal.target_belief_key] = proposal.proposed_value
            change_applied = True
        else:
            print(f"Warning: Belief key '{proposal.target_belief_key}' not found for modification. Cannot apply.")
    elif proposal.proposed_change_type == "removed":
        if proposal.target_belief_key in belief_surface:
            del belief_surface[proposal.target_belief_key]
            change_applied = True
        else:
            print(f"Warning: Belief key '{proposal.target_belief_key}' not found for removal. Cannot apply.")

    # 3. Save Updated Belief Surface (only if change was applied)
    if change_applied:
        save_json(belief_surface, BELIEF_SURFACE_PATH)
        print(f"Belief surface updated for key: {proposal.target_belief_key}")

        # 4. Load Legacy Tracker
        legacy_tracker = load_json(LEGACY_TRACKER_PATH)

        # 5. Create Log Entry
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "loop_id": proposal.loop_id,
            "agent_id": proposal.proposing_agent_id, # Agent who proposed
            "change_type": proposal.proposed_change_type,
            "belief_key": proposal.target_belief_key,
            "previous_value": original_value, # Value before change
            "new_value": proposal.proposed_value if proposal.proposed_change_type != "removed" else None,
            "justification_ref": proposal.justification, # Using full justification text for now
            "operator_approval_ref": proposal.operator_review_ref
        }

        # 6. Append Log Entry
        legacy_tracker.append(log_entry)

        # 7. Save Updated Legacy Tracker
        save_json(legacy_tracker, LEGACY_TRACKER_PATH)
        print(f"Legacy alignment tracker updated for proposal {proposal.proposal_id}")
        return True
    else:
        print(f"No changes applied to belief surface for proposal {proposal.proposal_id}.")
        return False

# Example Usage (for testing purposes)
if __name__ == '__main__':
    # Create dummy proposal data
    test_proposal_data = {
        "proposal_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "loop_id": "test_loop_001",
        "proposing_agent_id": "belief_manager_agent",
        "target_belief_key": "test_belief_for_update",
        "proposed_change_type": "added",
        "current_value": None,
        "proposed_value": {"detail": "This is a test value"},
        "justification": "Testing the belief updater.",
        "status": "approved", # Must be approved to apply
        "operator_review_ref": "op_review_123"
    }
    test_proposal = BeliefChangeProposal(**test_proposal_data)

    # Ensure dummy files exist for testing
    if not os.path.exists(BELIEF_SURFACE_PATH):
        save_json({}, BELIEF_SURFACE_PATH)
    if not os.path.exists(LEGACY_TRACKER_PATH):
        save_json([], LEGACY_TRACKER_PATH)

    print("--- Running Belief Updater Test --- ")
    success = apply_belief_update(test_proposal)
    print(f"Update successful: {success}")

    # Verify content (manual check or add assertions)
    print("\nBelief Surface Content:")
    print(load_json(BELIEF_SURFACE_PATH))
    print("\nLegacy Tracker Content:")
    print(load_json(LEGACY_TRACKER_PATH))
    print("--- Test Complete --- ")

