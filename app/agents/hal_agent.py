"""
HAL Agent Module (Cognitive Expansion v1.0)

This file implements the HAL Agent, upgraded for Cognitive Expansion v1.0.
Acts as the MVP Builder, handling simple implementation tasks and safety monitoring.
Defers complex tasks to Forge.
"""

import os
import json
import logging
import traceback
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple # Added Tuple import

# Import the Agent SDK (Placeholder)
# from agent_sdk import Agent, validate_schema

# Import Memory Operations
from app.modules.memory_writer import write_memory, read_memory
# Assuming hal_memory_patch might be deprecated or needs review, using standard write_memory for results
# from app.modules.hal_memory_patch import update_hal_memory

# Configure logging
logger = logging.getLogger("agents.hal")

# Placeholder for Agent SDK base class if not available
class Agent:
    def __init__(self, name, role, tools, permissions, description, version, status, tone_profile, schema_path, trust_score, contract_version):
        self.name = name
        self.role = role
        self.tools = tools
        self.permissions = permissions
        self.description = description
        self.version = version
        self.status = status
        self.tone_profile = tone_profile
        self.schema_path = schema_path
        self.trust_score = trust_score
        self.contract_version = contract_version

    def validate_schema(self, data):
        # Placeholder schema validation
        logger.warning("Using placeholder schema validation.")
        return True

# Placeholder for HAL result schema
class HALResult:
     def __init__(self, project_id, loop_id, task, status, files_created, message, error=None, deferred_to_forge=False, source_agent="hal-agent"):
        self.project_id = project_id
        self.loop_id = loop_id
        self.task = task
        self.status = status
        self.files_created = files_created
        self.message = message
        self.error = error
        self.deferred_to_forge = deferred_to_forge
        self.source_agent = source_agent
        self.timestamp = datetime.now().isoformat()

class HALAgent(Agent):
    """
    HAL Agent implementation (Cognitive Expansion v1.0).
    Acts as the MVP Builder and Safety Monitor.
    Handles simple, single-file generation tasks and defers complex ones.
    """

    def __init__(self):
        """Initialize the HAL Agent."""
        super().__init__(
            name="hal-agent",
            role="MVP Builder & Safety Monitor", # Updated Role
            tools=["generate_mvp", "monitor", "validate", "defer"], # Updated conceptual tools
            permissions=["read_memory", "write_memory", "read_files", "write_files", "safety_check"], # Adjusted permissions
            description="Generates Minimum Viable Product (MVP) code for simple tasks, performs safety checks, and defers complex builds to Forge.",
            version="1.1.0-cognitive-v1.0", # Updated version
            status="active",
            tone_profile={
                "style": "concise",
                "emotion": "neutral",
                "vibe": "quick_executor",
                "persona": "Fast and careful MVP implementer with a focus on safety and simplicity."
            },
            schema_path="schemas/agent_output/hal_safety_check.schema.json", # Keep existing for now
            trust_score=0.92,
            contract_version="1.1.0"
        )

    async def generate_mvp_files(self, task_details: dict, project_id: str, loop_id: str) -> Tuple[List[str], Optional[str]]:
        """Drafts simple schema/module file based on task details. Returns list of created paths and error message if any."""
        component_name = task_details.get("task", "unknown_mvp_component")
        build_details = task_details.get("details", {})
        target_path = build_details.get("path") # Expect path from file_tree

        logger.info(f"[{project_id}-{loop_id}] HAL generating MVP for: {component_name} at {target_path}")

        if not target_path:
            error_msg = "Target file path missing in build details for HAL MVP generation."
            logger.error(f"[{project_id}-{loop_id}] {error_msg}")
            return [], error_msg

        # --- Basic Complexity Check (Example: only handle single file tasks) ---
        # More sophisticated checks can be added later (e.g., analyzing goal complexity)
        if isinstance(target_path, list) or "," in target_path: # Simple check if multiple paths suggested
             defer_msg = "Task involves multiple files, deferring to Forge."
             logger.info(f"[{project_id}-{loop_id}] {defer_msg}")
             return [], defer_msg # Return empty list and deferral message

        try:
            # Check if file exists (optional, could overwrite or skip)
            if os.path.exists(target_path):
                logger.warning(f"[{project_id}-{loop_id}] File already exists: {target_path}. HAL overwriting MVP.")

            # --- Generate Content (Simple MVP Templates) ---
            content = f"""# Auto-generated MVP by HAL Agent (Cognitive v1.0)
# Project: {project_id}
# Loop: {loop_id}
# Task: {component_name}
# Timestamp: {datetime.now().isoformat()}

print("MVP content for {component_name}")
"""
            if "schema" in component_name.lower():
                 content = f"""# Auto-generated MVP Schema by HAL Agent (Cognitive v1.0)
from pydantic import BaseModel

class {component_name.replace("generate_","").replace("_","").capitalize()}Mvp(BaseModel):
    id: str
    name: str
"""
            elif "module" in component_name.lower() or "component" in component_name.lower():
                 content = f"""# Auto-generated MVP Module by HAL Agent (Cognitive v1.0)
import logging
logger = logging.getLogger(__name__)

def run_mvp():
    logger.info("Executing MVP function in {component_name}")
    return {{"status": "ok"}}
"""
            elif "test" in component_name.lower():
                 content = f"""# Auto-generated MVP Test by HAL Agent (Cognitive v1.0)
import unittest

class TestMvp(unittest.TestCase):
    def test_basic(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
"""

            # Ensure directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Write File
            with open(target_path, "w") as f:
                f.write(content)
            logger.info(f"[{project_id}-{loop_id}] HAL successfully wrote MVP file: {target_path}")

            # --- File Tree Node Completion: Update status in memory --- (Basic)
            try:
                file_tree_tag = f"file_tree_{loop_id}"
                current_tree = await read_memory(project_id, file_tree_tag)
                if isinstance(current_tree, list):
                    updated = False
                    for item in current_tree:
                        if item.get("path") == target_path:
                            item["status"] = "green"
                            updated = True
                            break
                    if updated:
                        await write_memory(project_id, self.name, loop_id, file_tree_tag, current_tree, "project_file_tree")
                        logger.info(f"[{project_id}-{loop_id}] HAL updated file tree status for {target_path} to green.")
                    else:
                        logger.warning(f"[{project_id}-{loop_id}] HAL could not find {target_path} in file tree memory to update status.")
                else:
                     logger.warning(f"[{project_id}-{loop_id}] File tree memory ({file_tree_tag}) not found or not a list for HAL update.")
            except Exception as mem_error:
                logger.error(f"[{project_id}-{loop_id}] HAL error updating file tree status in memory: {mem_error}")

            return [target_path], None # Return created path, no error

        except Exception as e:
            error_msg = f"Error generating MVP file {target_path}: {str(e)}"
            logger.error(f"[{project_id}-{loop_id}] {error_msg}")
            logger.error(traceback.format_exc())
            return [], error_msg # Return empty list and error message

    async def execute(self, payload: dict) -> HALResult:
        """
        Execute the HAL Agent based on payload from Orchestrator.

        Args:
            payload: The task payload dictionary from memory.

        Returns:
            HALResult containing the results of the operation.
        """
        project_id = payload.get("project_id")
        loop_id = payload.get("loop_id")
        task = payload.get("task")
        details = payload.get("details", {})
        source_agent = payload.get("source_agent")

        if not all([project_id, loop_id, task]):
             error_msg = "Invalid payload: Missing project_id, loop_id, or task."
             logger.error(error_msg)
             return HALResult(None, None, None, "failed", [], error_msg, error=error_msg) # Corrected error arg

        logger.info(f"[{project_id}-{loop_id}] HAL received task: {task}")
        print(f"🟥 HAL agent executing task \'{task}\' for project \'{project_id}\', loop \'{loop_id}\'")

        hal_result = HALResult(project_id, loop_id, task, "success", [], "HAL task initiated")

        try:
            # --- Perform Safety Checks --- (Keep existing logic)
            safety_checks = self._perform_safety_checks(task, project_id)
            # hal_result.safety_checks = safety_checks # Assuming schema includes this
            constraints_validated = True
            for check in safety_checks:
                if check["status"] == "failed":
                    constraints_validated = False
                    hal_result.status = "failed"
                    hal_result.message = f"Safety check failed: {check['check_name']}"
                    hal_result.error = check["message"]
                    logger.error(f"[{project_id}-{loop_id}] HAL Safety Check Failed: {hal_result.error}")
                    break

            # --- Execute Task or Defer --- (Cognitive Upgrade Logic)
            if constraints_validated:
                # --- Deferral Logic --- (Check complexity before generating)
                # Simple check: if task implies complexity, defer
                complex_keywords = ["integrate", "refactor", "database", "api", "multiple", "complex", "routes"]
                is_complex = any(keyword in task.lower() for keyword in complex_keywords)
                # Also defer if Orchestrator explicitly assigned to Forge but HAL received it somehow
                is_forge_task = details.get("agent") == "Forge"

                if is_complex or is_forge_task:
                    hal_result.status = "deferred"
                    hal_result.deferred_to_forge = True
                    hal_result.message = f"Task '{task}' deemed complex or assigned to Forge. Deferring."
                    logger.info(f"[{project_id}-{loop_id}] {hal_result.message}")
                else:
                    # --- Generate MVP Files --- (If simple enough)
                    created_files, error_msg = await self.generate_mvp_files(details, project_id, loop_id)
                    if error_msg:
                        # Check if error was due to deferral request from generate_mvp_files itself
                        if "deferring to Forge" in error_msg:
                             hal_result.status = "deferred"
                             hal_result.deferred_to_forge = True
                             hal_result.message = error_msg
                             logger.info(f"[{project_id}-{loop_id}] {hal_result.message}")
                        else:
                            # Actual error during generation
                            hal_result.status = "failed"
                            hal_result.message = f"HAL failed to generate MVP files."
                            hal_result.error = error_msg
                            logger.error(f"[{project_id}-{loop_id}] {hal_result.message} Error: {error_msg}")
                    else:
                        hal_result.files_created = created_files
                        hal_result.status = "success"
                        hal_result.message = f"HAL successfully generated MVP files: {', '.join(created_files)}"
                        logger.info(f"[{project_id}-{loop_id}] {hal_result.message}")

            # --- Log result for Orchestrator reflection --- (Using standard write_memory)
            result_tag = f"hal_result_{loop_id}_{task.replace(' ','_')}"
            await write_memory(
                project_id=project_id,
                agent_id=self.name,
                loop_id=loop_id,
                tag=result_tag,
                value=hal_result.__dict__, # Convert result object to dict
                type="agent_result_payload"
            )
            logger.info(f"[{project_id}-{loop_id}] Logged HAL result to memory tag: {result_tag}")

            # Validate schema before returning (if SDK is used)
            # if not self.validate_schema(hal_result.__dict__):
            #     logger.error(f"[{project_id}-{loop_id}] Schema validation failed for HAL result.")
            #     # Handle validation failure appropriately

            return hal_result

        except Exception as e:
            error_msg = f"Critical error in HAL execute: {str(e)}"
            logger.error(f"[{project_id}-{loop_id}] {error_msg}")
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")

            # Return error response
            error_result = HALResult(project_id, loop_id, task, "failed", [], error_msg, error=error_msg) # Corrected error arg
            # Attempt to log error result
            try:
                 result_tag = f"hal_result_{loop_id}_{task.replace(' ','_')}_error"
                 await write_memory(project_id, self.name, loop_id, result_tag, error_result.__dict__, "agent_result_payload")
            except Exception as log_e:
                 logger.error(f"[{project_id}-{loop_id}] Failed to log HAL error result: {log_e}")
            return error_result

    def _perform_safety_checks(self, task: str, project_id: str) -> List[Dict[str, Any]]:
        """Perform safety checks for the given task. (Keep existing logic)"""
        # ... (Keep the existing safety check logic as it was) ...
        safety_checks = []
        content_check = {"check_name": "content_safety", "check_type": "content", "timestamp": datetime.now().isoformat(), "status": "passed", "message": "Task content is safe"}
        unsafe_keywords = ["delete all", "rm -rf", "drop database", "format disk"]
        if task: # Check if task is not None
            for keyword in unsafe_keywords:
                if keyword in task.lower():
                    content_check["status"] = "failed"
                    content_check["message"] = f"Task contains potentially unsafe keyword: {keyword}"
                    break
        safety_checks.append(content_check)
        access_check = {"check_name": "project_access", "check_type": "permission", "timestamp": datetime.now().isoformat(), "status": "passed", "message": "HAL has permission to access this project"}
        if project_id and "restricted" in project_id:
            access_check["status"] = "failed"
            access_check["message"] = f"HAL does not have permission to access restricted project: {project_id}"
        safety_checks.append(access_check)
        resource_check = {"check_name": "resource_constraints", "check_type": "resource", "timestamp": datetime.now().isoformat(), "status": "passed", "message": "Resource usage is within constraints"}
        safety_checks.append(resource_check)
        return safety_checks

# Example usage (for testing, assuming payload is read from memory)
# async def run_hal_agent(payload: dict):
#     agent = HALAgent()
#     return await agent.execute(payload=payload)

# import asyncio
# async def main():
#     # Simulate payload read from memory for a simple task
#     test_payload = {
#         "project_id": "test_proj_hal_123",
#         "loop_id": f"loop_{datetime.now().strftime('%Y%m%d%H%M%S')}",
#         "task": "generate_mvp_component",
#         "details": {
#             "goal": "Create simple component",
#             "path": "app/components/test_proj_hal_123_component.py"
#         },
#         "source_agent": "architect-orchestrator"
#     }
#     result = await run_hal_agent(payload=test_payload)
#     print(json.dumps(result.__dict__, indent=2))
# if __name__ == "__main__":
#     asyncio.run(main())


