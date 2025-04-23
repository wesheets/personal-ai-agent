from fastapi import APIRouter
from app.schemas.self_reflection_schema import SelfInquiryRequest
from app.schemas.self_revision_schema import BeliefRevisionRequest
import json
from datetime import datetime

router = APIRouter()

@router.post("/reflect")
async def reflect_on_self(request: SelfInquiryRequest):
    with open("app/memory/core_beliefs.json") as f:
        beliefs = json.load(f)
    
    # Optional enhancement: Add information about recent revisions
    recent_revisions = []
    if "revision_log" in beliefs and beliefs["revision_log"]:
        recent_revisions = beliefs["revision_log"][-3:] if len(beliefs["revision_log"]) > 0 else []
    
    changed_recently = False
    if recent_revisions:
        # Check if any revisions happened in the last 3 loops
        changed_recently = any(rev.get("loop_id", "").startswith("loop_") for rev in recent_revisions)
    
    return {
        "status": "self-reflection",
        "beliefs": beliefs,
        "origin_prompt": request.prompt,
        "loop_id": request.loop_id,
        "reflected_at": datetime.utcnow().isoformat(),
        "recent_revisions": recent_revisions,
        "most_recent_revision": recent_revisions[-1] if recent_revisions else None,
        "changed_recently": changed_recently
    }

@router.post("/revise")
async def revise_belief(request: BeliefRevisionRequest):
    with open("app/memory/core_beliefs.json", "r+") as f:
        beliefs = json.load(f)

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

        f.seek(0)
        json.dump(beliefs, f, indent=2)
        f.truncate()

    return {
        "status": "belief-revised",
        "updated_field": request.field_updated,
        "new_value": request.new_value,
        "loop_id": request.loop_id
    }
