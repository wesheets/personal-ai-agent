"""
Routes for managing and executing cognitive loops.
"""
import logging
import uuid
import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Body

# Import the real write_memory function
try:
    from app.api.modules.memory import write_memory
    memory_write_available = True
    logging.info("✅ Successfully imported write_memory from app.api.modules.memory")
except ImportError as e:
    logging.error(f"❌ Failed to import write_memory from app.api.modules.memory: {e}. Logging will fail.")
    memory_write_available = False
    # Define a mock write_memory if import fails to prevent server crash on call
    async def write_memory(memory_data: Dict[str, Any]) -> Dict[str, Any]:
        logging.error("Mock write_memory called because real import failed.")
        return {"status": "error", "message": "write_memory import failed", "written": False}

# Configure logging
logger = logging.getLogger("app.routes.loop_routes")
logging.basicConfig(level=logging.INFO) # Ensure logger is configured

router = APIRouter()

# --- Mock Agent Functions --- 
# (Replace with real agent calls when available)
async def mock_orchestrator(loop_id: str, instructions: str, context: Dict) -> Dict:
    logger.info(f"Running MOCK Orchestrator for loop_id: {loop_id}")
    # Simulate plan generation
    plan = {
        "steps": [
            {"step_id": 1, "description": "Mock: Research topic", "status": "pending"},
            {"step_id": 2, "description": "Mock: Analyze findings", "status": "pending"},
            {"step_id": 3, "description": "Mock: Generate response", "status": "pending"}
        ]
    }
    logger.info(f"[Loop {loop_id}] Orchestrator generated plan: {plan}")
    return plan

async def mock_hal(loop_id: str, plan: Dict, context: Dict) -> Dict:
    logger.info(f"Running MOCK HAL for loop_id: {loop_id}")
    # Simulate execution
    result = {
        "status": "success", 
        "result": "Mock HAL execution completed successfully.", 
        "tool_used": "mock_tool_v1"
    }
    logger.info(f"[Loop {loop_id}] HAL execution result: {result}")
    return result

async def mock_critic(loop_id: str, plan: Dict, hal_output: Dict) -> str:
    logger.info(f"Running MOCK Critic for loop_id: {loop_id}")
    reflection = "Mock Critic reflection: The plan was executed nominally, but could be improved."
    logger.info(f"[Loop {loop_id}] Critic reflection: {reflection}")
    return reflection

async def mock_sage(loop_id: str, plan: Dict, hal_output: Dict, critic_reflection: str) -> str:
    logger.info(f"Running MOCK Sage for loop_id: {loop_id}")
    summary = "Mock Sage summary: Loop completed with mock agents."
    logger.info(f"[Loop {loop_id}] Sage summary: {summary}")
    return summary

# --- Helper Function for Structured Logging --- 
async def log_structured_data(loop_id: str, memory_type: str, content: Dict[str, Any], tags: Optional[List[str]] = None) -> bool:
    """Helper to call write_memory and handle success/failure logging."""
    if not memory_write_available:
        logger.error(f"Cannot log {memory_type} for loop {loop_id}: write_memory not available.")
        return False

    logger.info(f"Attempting to log {memory_type} for loop {loop_id}")
    memory_payload = {
        "agent_id": f"loop_system_{loop_id}", # Use loop_id or a system ID
        "type": memory_type,
        "content": content,
        "tags": tags or []
    }
    try:
        # Call the real write_memory function
        result = await write_memory(memory_data=memory_payload) # Pass as single dict
        if result.get("status") == "success" and result.get("written") is True:
            logger.info(f"✅ Successfully logged {memory_type} for loop {loop_id}")
            return True
        else:
            logger.error(f"Failed to log {memory_type} for loop {loop_id}: {result.get('message')}")
            return False
    except Exception as e:
        logger.error(f"Exception during logging {memory_type} for loop {loop_id}: {e}", exc_info=True)
        return False

# --- API Endpoint --- 
@router.post("/create", tags=["Loop Execution"])
async def create_loop(payload: Dict = Body(...)) -> Dict[str, Any]:
    """
    Creates and executes a cognitive loop based on the provided payload.
    Payload should include: plan_id, loop_type, instructions, context, metadata.
    """
    plan_id = payload.get("plan_id", "unknown_plan")
    instructions = payload.get("instructions", "No instructions provided.")
    context = payload.get("context", {})
    loop_id = str(uuid.uuid4())
    start_time = datetime.datetime.now().isoformat()
    
    logger.info(f"➡️ Entering create_loop endpoint for plan_id: {plan_id}")
    logger.info(f"Generated loop_id: {loop_id}")

    # --- Simple Loop Record Keeping (Optional, replace with DB later) ---
    # (Skipping file-based loop store for this rebuild, focus on core logic)
    logger.info(f"✅ Mock created loop record with ID: {loop_id}.")

    # --- Cognitive Loop Execution --- 
    logger.info(f"🚀 Starting cognitive loop execution for loop_id: {loop_id}")
    mutation_logged = False
    reflection_logged = False
    all_reflections_logged = True # Assume true initially

    try:
        # 1. Orchestrator
        logger.info(f"[Loop {loop_id}] Calling Orchestrator...")
        plan = await mock_orchestrator(loop_id, instructions, context)

        # 2. HAL
        logger.info(f"[Loop {loop_id}] Calling HAL...")
        hal_output = await mock_hal(loop_id, plan, context)
        hal_agent_output = hal_output.get("result", "HAL output missing")
        hal_tool_used = hal_output.get("tool_used", "unknown_tool")

        # 3. Log HAL Output (Mutation)
        loop_trace_content = {
            "loop_id": loop_id,
            "plan": plan, # Log the plan generated by Orchestrator
            "agent_output": hal_agent_output,
            "tool_used": hal_tool_used,
            # timestamp added automatically by write_memory
        }
        mutation_logged = await log_structured_data(loop_id, "loop_trace", loop_trace_content, tags=["HAL_execution"])
        if not mutation_logged:
             logger.warning(f"[Loop {loop_id}] Failed to log mutation to loop_trace.")

        # 4. Critic
        logger.info(f"[Loop {loop_id}] Calling Critic...")
        critic_reflection = await mock_critic(loop_id, plan, hal_output)

        # 5. Log Critic Reflection
        critic_reflection_content = {
            "loop_id": loop_id,
            "agent": "Critic",
            "text": critic_reflection,
            # timestamp added automatically by write_memory
        }
        critic_log_success = await log_structured_data(loop_id, "reflection_thread", critic_reflection_content, tags=["Critic_reflection"])
        if not critic_log_success:
            all_reflections_logged = False

        # 6. Sage
        logger.info(f"[Loop {loop_id}] Calling Sage...")
        sage_summary = await mock_sage(loop_id, plan, hal_output, critic_reflection)

        # 7. Log Sage Reflection
        sage_reflection_content = {
            "loop_id": loop_id,
            "agent": "Sage",
            "text": sage_summary,
            # timestamp added automatically by write_memory
        }
        sage_log_success = await log_structured_data(loop_id, "reflection_thread", sage_reflection_content, tags=["Sage_summary"])
        if not sage_log_success:
            all_reflections_logged = False
            
        reflection_logged = all_reflections_logged # Set final status based on both logs
        if not reflection_logged:
            logger.warning(f"[Loop {loop_id}] Failed to log one or both reflections.")

        logger.info(f"✅ Cognitive loop execution completed successfully for loop_id: {loop_id}")
        final_status = "completed"

    except Exception as loop_exception:
        logger.error(f"❌ Cognitive loop execution failed for loop_id: {loop_id}: {loop_exception}", exc_info=True)
        final_status = "failed"

    # --- Return Response --- 
    response = {
        "status": final_status,
        "loop_id": loop_id,
        "mutation_logged": mutation_logged,
        "reflection_logged": reflection_logged,
        "agents": ["orchestrator", "hal", "critic", "sage"] # List agents involved
    }
    logger.info(f"🏁 Returning final response for loop_id: {loop_id} with status: {final_status}")
    return response

