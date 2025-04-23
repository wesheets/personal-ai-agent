from fastapi import APIRouter
from app.schemas.self_reflection_schema import SelfInquiryRequest
from app.schemas.self_revision_schema import BeliefRevisionRequest
import json
from datetime import datetime

router = APIRouter()

# Constants for stability calculation
MAX_POSSIBLE_REVISIONS = 10  # After 10 revisions, stability would reach 0
STABILITY_THRESHOLD_WARNING = 0.6  # Below this triggers "changed_often_recently"
STABILITY_THRESHOLD_RISK = 0.25  # Below this triggers identity risk warning

@router.post("/reflect")
async def reflect_on_self(request: SelfInquiryRequest):
    with open("app/memory/core_beliefs.json") as f:
        beliefs = json.load(f)
    
    # Get recent revisions
    recent_revisions = []
    if "revision_log" in beliefs and beliefs["revision_log"]:
        recent_revisions = beliefs["revision_log"][-3:] if len(beliefs["revision_log"]) > 0 else []
    
    # Check if any revisions happened in the last 3 loops
    changed_recently = False
    if recent_revisions:
        changed_recently = any(rev.get("loop_id", "").startswith("loop_") for rev in recent_revisions)
    
    # Check for frequently changing beliefs
    volatility_flags = []
    changed_often_recently = False
    
    # Get belief stability scores
    belief_stability = beliefs.get("belief_stability", {})
    
    # Check for unstable beliefs
    for belief, stability in belief_stability.items():
        if stability < STABILITY_THRESHOLD_WARNING:
            # Count how many times this belief appears in recent revisions
            revision_count = sum(1 for rev in beliefs.get("revision_log", []) 
                               if rev.get("field_updated") == belief)
            
            if revision_count > 0:
                volatility_flags.append(f"{belief} belief has changed {revision_count} times")
                changed_often_recently = True
    
    # Check for identity risk
    identity_risk = None
    for belief, stability in belief_stability.items():
        if stability < STABILITY_THRESHOLD_RISK:
            identity_risk = {
                "status": "warning",
                "message": f"{belief} is approaching instability threshold"
            }
            break
    
    return {
        "status": "self-reflection",
        "beliefs": beliefs,
        "origin_prompt": request.prompt,
        "loop_id": request.loop_id,
        "reflected_at": datetime.utcnow().isoformat(),
        "recent_revisions": recent_revisions,
        "most_recent_revision": recent_revisions[-1] if recent_revisions else None,
        "changed_recently": changed_recently,
        "belief_stability": belief_stability,
        "volatility_flags": volatility_flags,
        "changed_often_recently": changed_often_recently,
        "identity_risk": identity_risk
    }

@router.post("/revise")
async def revise_belief(request: BeliefRevisionRequest):
    with open("app/memory/core_beliefs.json", "r+") as f:
        beliefs = json.load(f)

        # Add to revision log
        beliefs["revision_log"].append({
            "loop_id": request.loop_id,
            "reason": request.reason,
            "field_updated": request.field_updated,
            "new_value": request.new_value,
            "revised_at": datetime.utcnow().isoformat()
        })

        # Apply the belief change (only at top level)
        if request.field_updated in beliefs:
            beliefs[request.field_updated] = request.new_value
            
            # Update belief stability
            if "belief_stability" not in beliefs:
                beliefs["belief_stability"] = {}
                
            # Initialize stability if not present
            if request.field_updated not in beliefs["belief_stability"]:
                beliefs["belief_stability"][request.field_updated] = 1.0
                
            # Count revisions for this belief
            num_revisions = sum(1 for rev in beliefs["revision_log"] 
                              if rev.get("field_updated") == request.field_updated)
            
            # Calculate new stability score with decay function
            stability = max(1.0 - (num_revisions / MAX_POSSIBLE_REVISIONS), 0.0)
            beliefs["belief_stability"][request.field_updated] = stability

        f.seek(0)
        json.dump(beliefs, f, indent=2)
        f.truncate()

    return {
        "status": "belief-revised",
        "updated_field": request.field_updated,
        "new_value": request.new_value,
        "loop_id": request.loop_id,
        "stability": beliefs.get("belief_stability", {}).get(request.field_updated, 1.0)
    }
