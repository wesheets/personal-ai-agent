# loop_execution_mode_enforcer.py

def enforce_loop_mode(intent, proposed_actions):
    if intent.get("role") == "read_only":
        for action in proposed_actions:
            if action.get("type") == "mutation":
                return {"violation": True, "reason": "Mutation in read-only mode."}
    return {"violation": False}
