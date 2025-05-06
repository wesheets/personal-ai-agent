#!/usr/bin/env python3.11
import json
import logging
import os
from datetime import datetime, timezone
import uuid

from app.core.base_agent import BaseAgent
from app.core.agent_registry import register, AgentCapability
from app.schemas.core.agent_result import ResultStatus
from app.utils.justification_logger import log_justification # Batch 21.2: For logging conflict detection

logger = logging.getLogger(__name__)

# Define paths relative to PROJECT_ROOT (assuming PROJECT_ROOT is defined elsewhere or passed)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BELIEF_CONFLICT_LOG_PATH = os.path.join(PROJECT_ROOT, "app/memory/belief_conflict_log.json")
BELIEF_WEIGHT_INDEX_PATH = os.path.join(PROJECT_ROOT, "app/memory/belief_weight_index.json") # Batch 21.3
BELIEF_SURFACE_PATH = os.path.join(PROJECT_ROOT, "app/memory/belief_surface.json") # Batch 21.3
PROMETHEUS_CREED_PATH = os.path.join(PROJECT_ROOT, "app/memory/promethios_creed.json") # Batch 21.3

def load_json_local(path):
    """Local JSON loader to avoid circular dependency if controller utils are used."""
    try:
        with open(path, 'r') as f:
            content = f.read()
            # Handle empty files based on expected structure
            if not content:
                if path.endswith("_log.json") or path.endswith("tracker.json"):
                    return []
                elif path.endswith("index.json") or path.endswith("surface.json") or path.endswith("budget.json") or path.endswith("score.json") or path.endswith("metrics.json") or path.endswith("creed.json"):
                    return {}
                else:
                    return {}
            return json.loads(content)
    except FileNotFoundError:
        print(f"Warning: File not found at {path}. Returning default value.")
        if path.endswith("_log.json") or path.endswith("tracker.json"):
            return []
        elif path.endswith("index.json") or path.endswith("surface.json") or path.endswith("budget.json") or path.endswith("score.json") or path.endswith("metrics.json") or path.endswith("creed.json"):
            return {}
        else:
            return {}
    except json.JSONDecodeError:
        print(f"Warning: Error decoding {path}. Reinitializing.")
        if path.endswith("_log.json") or path.endswith("tracker.json"):
            return []
        elif path.endswith("index.json") or path.endswith("surface.json") or path.endswith("budget.json") or path.endswith("score.json") or path.endswith("metrics.json") or path.endswith("creed.json"):
            return {}
        else:
            return {}

def save_json_local(data, path):
    """Local JSON saver."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')

def log_belief_conflict(loop_id: str, conflict_type: str, belief_ids: list[str], description: str, confidence: float):
    """Logs a detected belief conflict."""
    conflict_log = load_json_local(BELIEF_CONFLICT_LOG_PATH)
    if not isinstance(conflict_log, list):
        print(f"Warning: {BELIEF_CONFLICT_LOG_PATH} is not a list. Reinitializing.")
        conflict_log = []
        
    entry = {
        "conflict_id": f"conf_{loop_id}_{uuid.uuid4().hex[:8]}",
        "loop_id": loop_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "conflict_type": conflict_type, # e.g., "contradiction", "value_mismatch", "logical_inconsistency"
        "involved_belief_ids": belief_ids, # List of keys/IDs of conflicting beliefs
        "description": description,
        "confidence_score": confidence,
        "resolution_status": "unresolved" # Initial status
    }
    conflict_log.append(entry)
    save_json_local(conflict_log, BELIEF_CONFLICT_LOG_PATH)
    print(f"Logged belief conflict: {entry['conflict_id']}")
    return entry['conflict_id']

# --- Batch 21.3: Belief Weighting Logic --- 
def calculate_and_update_belief_weights(loop_id: str, belief_data: dict, agent_key: str) -> tuple[dict, list]:
    """Calculates belief weights and updates the index."""
    weight_index_data = load_json_local(BELIEF_WEIGHT_INDEX_PATH)
    if not isinstance(weight_index_data, dict) or "index" not in weight_index_data:
        print(f"Warning: {BELIEF_WEIGHT_INDEX_PATH} is invalid. Reinitializing.")
        weight_index_data = {"index": {}, "calculation_metadata": {"last_run_timestamp": None, "method_used": None}}
        
    creed_data = load_json_local(PROMETHEUS_CREED_PATH)
    creed_beliefs = creed_data.get("beliefs", {}) if isinstance(creed_data, dict) else {}
    
    belief_index = weight_index_data.get("index", {})
    updated_weights = False
    justification_refs = []
    calculation_method = "simple_keyword_creed_check_v1"
    now_iso = datetime.now(timezone.utc).isoformat()

    logger.info(f"Calculating belief weights using method: {calculation_method}")
    just_id = log_justification(loop_id, agent_key, "Weight Calculation Start", f"Starting belief weight calculation using {calculation_method}", 0.8)
    if just_id: justification_refs.append(just_id)

    for belief_id, belief_content in belief_data.items():
        weight = 0.5 # Default weight
        source = "default"
        
        # Example Logic: Check if belief is in creed
        if belief_id in creed_beliefs:
            weight = 0.9
            source = "derived_from_creed"
        # Example Logic: Check for keywords (simple)
        elif isinstance(belief_content, str):
            if "core principle" in belief_content.lower() or "must" in belief_content.lower():
                weight = 0.8
                source = "keyword_based"
            elif "preference" in belief_content.lower() or "should" in belief_content.lower():
                weight = 0.4
                source = "keyword_based"
        
        # Update index if weight changed or belief is new to index
        if belief_id not in belief_index or belief_index[belief_id].get("weight") != weight:
            belief_index[belief_id] = {
                "weight": weight,
                "source": source,
                "last_updated": now_iso
            }
            updated_weights = True
            logger.info(f"Updated weight for belief 	{belief_id}	 to {weight} (source: {source})")
            just_id = log_justification(loop_id, agent_key, "Belief Weight Update", f"Set weight for 	{belief_id}	 to {weight} ({source})", 0.7, linked_refs=justification_refs[-1:])
            if just_id: justification_refs.append(just_id)

    if updated_weights:
        weight_index_data["index"] = belief_index
        weight_index_data["calculation_metadata"] = {
            "last_run_timestamp": now_iso,
            "method_used": calculation_method
        }
        save_json_local(weight_index_data, BELIEF_WEIGHT_INDEX_PATH)
        logger.info(f"Saved updated belief weights to {BELIEF_WEIGHT_INDEX_PATH}")
        just_id = log_justification(loop_id, agent_key, "Weight Index Saved", f"Saved updated belief weight index.", 0.9, linked_refs=justification_refs[-1:])
        if just_id: justification_refs.append(just_id)
    else:
        logger.info("No belief weights needed updating.")
        just_id = log_justification(loop_id, agent_key, "Weight Calculation No Update", "No belief weights required updating.", 0.6, linked_refs=justification_refs[-1:])
        if just_id: justification_refs.append(just_id)
        
    return weight_index_data, justification_refs
# --- End Batch 21.3 ---

@register(
    key="belief_introspection",
    name="Belief Introspection Agent",
    capabilities=[AgentCapability.REFLECTION, AgentCapability.MEMORY_READ, AgentCapability.MEMORY_WRITE] # Added MEMORY_WRITE for weights
)
class BeliefIntrospectionAgent(BaseAgent):
    """Agent responsible for analyzing the belief surface for consistency, insights, and weights."""
    agent_key = "belief_introspection" # Added class variable

    # Define input/output schemas when created
    # input_schema = BeliefIntrospectionRequest
    # output_schema = BeliefIntrospectionResult

    async def run(self, payload: dict) -> dict:
        """
        Analyzes the belief_surface.json for patterns, conflicts, or insights.
        Batch 21.2: Added basic conflict detection.
        Batch 21.3: Added belief weight calculation.
        """
        loop_id = payload.get("loop_id", "unknown_loop")
        # Use constant paths defined at module level
        belief_surface_path = BELIEF_SURFACE_PATH 
        logger.info(f"BeliefIntrospectionAgent running for loop {loop_id}")
        status = ResultStatus.SUCCESS
        analysis_summary = ""
        conflicts_detected_details = [] # Store details for logging
        insights_generated = []
        belief_count = 0
        justification_refs = [] # Store justification IDs from this agent
        memory_updates = {} # Batch 21.3: Store memory updates

        try:
            logger.info(f"Attempting to load and analyze belief surface at {belief_surface_path}")
            if not os.path.exists(belief_surface_path):
                logger.warning(f"Belief surface file not found at {belief_surface_path}. Cannot perform introspection.")
                status = ResultStatus.ERROR
                analysis_summary = "Belief surface file not found."
                just_id = log_justification(loop_id, self.__class__.agent_key, "Introspection Failure", analysis_summary, 1.0)
                if just_id: justification_refs.append(just_id)
            else:
                belief_data = load_json_local(belief_surface_path)
                
                if isinstance(belief_data, dict):
                    belief_count = len(belief_data)
                    analysis_summary = f"Successfully loaded belief surface. Found {belief_count} beliefs."
                    logger.info(analysis_summary)
                    just_id = log_justification(loop_id, self.__class__.agent_key, "Belief Load Success", analysis_summary, 0.9)
                    if just_id: justification_refs.append(just_id)
                    
                    # --- Batch 21.3: Calculate Belief Weights --- 
                    updated_weight_index, weight_just_refs = calculate_and_update_belief_weights(loop_id, belief_data, self.__class__.agent_key)
                    justification_refs.extend(weight_just_refs)
                    memory_updates["belief_weight_index.json"] = "updated" # Indicate update
                    analysis_summary += f" Calculated/updated belief weights."
                    # --- End Batch 21.3 ---
                    
                    # --- Basic Analysis Example (can be expanded) ---
                    if "core_principle_1" in belief_data:
                        insight_text = "Insight: Core principle 1 is present in the belief surface."
                        insights_generated.append(insight_text)
                        just_id = log_justification(loop_id, self.__class__.agent_key, "Insight Generated", insight_text, 0.7, linked_refs=justification_refs[-1:])
                        if just_id: justification_refs.append(just_id)
                    
                    # --- Conflict Detection Logic (Batch 21.2) ---
                    logger.info("Starting conflict detection...")
                    belief_items = list(belief_data.items())
                    detected_conflict_ids = []
                    
                    # Example: Check for direct contradictions (e.g., belief X is true AND belief X is false)
                    if belief_data.get("user_preference_color") == "blue" and belief_data.get("user_preference_color_alt") == "red":
                         conflict_desc = "Contradictory color preferences found ('blue' and 'red')."
                         conflict_id = log_belief_conflict(
                             loop_id=loop_id,
                             conflict_type="contradiction",
                             belief_ids=["user_preference_color", "user_preference_color_alt"], # Assuming these are the keys
                             description=conflict_desc,
                             confidence=0.9
                         )
                         if conflict_id:
                             detected_conflict_ids.append(conflict_id)
                             conflicts_detected_details.append({"id": conflict_id, "description": conflict_desc})
                             just_id = log_justification(loop_id, self.__class__.agent_key, "Conflict Detected", conflict_desc, 0.9, linked_refs=justification_refs[-1:])
                             if just_id: justification_refs.append(just_id)

                    # Add more sophisticated conflict detection rules here based on belief structure

                    conflict_count = len(detected_conflict_ids)
                    analysis_summary += f" Detected {conflict_count} potential conflicts." 
                    logger.info(f"Conflict detection finished. Found {conflict_count} conflicts.")
                    just_id = log_justification(loop_id, self.__class__.agent_key, "Conflict Detection Summary", f"Conflict detection finished. Found {conflict_count} conflicts.", 0.8, linked_refs=justification_refs[-1:])
                    if just_id: justification_refs.append(just_id)
                    
                else:
                    logger.error(f"Belief surface at {belief_surface_path} is not a valid JSON object.")
                    status = ResultStatus.ERROR
                    analysis_summary = "Belief surface is not a valid JSON object."
                    just_id = log_justification(loop_id, self.__class__.agent_key, "Introspection Failure", analysis_summary, 1.0)
                    if just_id: justification_refs.append(just_id)

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from belief surface {belief_surface_path}: {e}", exc_info=True)
            status = ResultStatus.ERROR
            analysis_summary = f"Failed to decode belief surface JSON: {e}"
            just_id = log_justification(loop_id, self.__class__.agent_key, "Introspection Failure", analysis_summary, 1.0)
            if just_id: justification_refs.append(just_id)
        except Exception as e:
            logger.error(f"Error during belief introspection for loop {loop_id}: {e}", exc_info=True)
            status = ResultStatus.ERROR
            analysis_summary = f"Introspection failed due to an unexpected error: {e}"
            just_id = log_justification(loop_id, self.__class__.agent_key, "Introspection Failure", analysis_summary, 1.0)
            if just_id: justification_refs.append(just_id)

        # Result structure (assuming a standard output schema will be defined later)
        result = {
            "task_id": payload.get("task_id", "unknown_task"),
            "loop_id": loop_id,
            "status": status.value,
            "analysis_summary": analysis_summary,
            "belief_count": belief_count,
            "conflicts_detected": conflicts_detected_details, # List of dicts with id and description
            "insights_generated": insights_generated,
            "memory_updates": memory_updates, # Batch 21.3
            "justification_ids": justification_refs # Include justifications generated by this agent
        }

        logger.info(f"BeliefIntrospectionAgent finished for loop {loop_id} with status {status}")
        return result

