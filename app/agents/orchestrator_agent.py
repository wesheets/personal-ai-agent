"""
Architect Orchestrator Agent Implementation (Cognitive Expansion v1.0)

This file implements the Orchestrator Agent, hardcoded to the Architect role,
integrating cognitive capabilities as per Healing Batch 2 directive.
"""

import json
import datetime
import logging
import traceback
from typing import Dict, List, Any, Optional, Tuple

# Import the Agent SDK
# from agent_sdk import Agent, validate_schema # Assuming SDK is available

# Import Memory Operations (Standard)
from app.modules.memory_writer import write_memory, read_memory

# Configure logging
logger = logging.getLogger("agents.orchestrator")

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

class OrchestratorAgent(Agent):
    """
    Architect Orchestrator Agent implementation.
    Hardcoded to Architect mode for Cognitive Expansion v1.0.
    Coordinates planning, architecting file structures, and delegating builds.
    """

    def __init__(self):
        """Initialize the Architect Orchestrator Agent."""
        super().__init__(
            name="architect-orchestrator",
            role="Architect Orchestrator",
            # Tools reflect core capabilities for this batch
            tools=["plan_project", "delegate_task", "architect_file_tree", "trigger_build", "reflect_on_result"],
            permissions=["read_memory", "write_memory"], # Simplified permissions for now
            description="Plans projects, architects file structures, and delegates build tasks to Forge/HAL.",
            version="1.1.1-cognitive-v1.0", # Incremented patch version for fix
            status="active",
            tone_profile={
                "style": "strategic",
                "emotion": "neutral",
                "vibe": "architect",
                "persona": "Strategic planner and system architect, focused on structure and delegation."
            },
            schema_path="schemas/orchestrator_output.schema.json", # Keep existing for now
            trust_score=0.98,
            contract_version="1.1.0"
        )
        self.current_mode = "Architect" # Hardcoded mode

    async def plan_project(self, goal: str, project_id: str, loop_id: str) -> List[Dict[str, Any]]:
        """Generates a step-by-step plan with target agents based on the goal."""
        logger.info(f"[{project_id}-{loop_id}] Planning project for goal: {goal}")
        # Basic plan generation - refine later with SCM awareness
        plan = []
        if "api" in goal.lower():
            plan.append({"step": 1, "agent": "Forge", "task": "build_api_schema", "details": {"goal": goal}})
            plan.append({"step": 2, "agent": "Forge", "task": "build_api_module", "details": {"goal": goal}})
            plan.append({"step": 3, "agent": "Forge", "task": "build_api_routes", "details": {"goal": goal}})
            plan.append({"step": 4, "agent": "HAL", "task": "generate_api_tests", "details": {"goal": goal}})
        elif "simple component" in goal.lower():
            plan.append({"step": 1, "agent": "HAL", "task": "generate_mvp_component", "details": {"goal": goal}})
            plan.append({"step": 2, "agent": "Critic", "task": "review_component", "details": {"goal": goal}})
        else:
            # Default to HAL for simple file generation
            plan.append({"step": 1, "agent": "HAL", "task": "generate_initial_files", "details": {"goal": goal}})

        # Log plan to memory
        await write_memory(
            project_id=project_id,
            agent_id=self.name,
            loop_id=loop_id,
            tag=f"project_plan_{loop_id}", # Changed tag format
            value=plan,
            type="project_plan"
        )
        logger.info(f"[{project_id}-{loop_id}] Project plan generated and saved.")
        return plan

    async def delegate_task(self, agent_name: str, task_details: dict, project_id: str, loop_id: str):
        """Writes structured payloads to memory for the target agent."""
        task_name_for_log = task_details.get("task", "unknown_task")
        logger.info(f"[{project_id}-{loop_id}] Delegating task to {agent_name}: {task_name_for_log}")
        payload = {
            "project_id": project_id,
            "loop_id": loop_id,
            "task": task_details.get("task"),
            "details": task_details.get("details", {}),
            "timestamp": datetime.datetime.now().isoformat(),
            "source_agent": self.name
        }
        # Tag convention: agentname_task_payload_loopid
        base_agent_name = agent_name.lower().replace("-agent", "")
        tag = f"{base_agent_name}_task_payload_{loop_id}" # Simplified tag
        await write_memory(
            project_id=project_id,
            agent_id=self.name,
            loop_id=loop_id,
            tag=tag,
            value=payload,
            type="agent_task_payload"
        )
        logger.info(f"[{project_id}-{loop_id}] Task payload for {agent_name} saved to memory with tag: {tag}")
        return {"status": "success", "delegated_to": agent_name, "delegation_tag": tag} # Return the tag used

    async def architect_file_tree(self, plan: list, project_id: str, loop_id: str) -> List[Dict[str, Any]]:
        """Defines stubbed file structure in memory based on the plan, including the task name."""
        logger.info(f"[{project_id}-{loop_id}] Architecting file tree based on plan.")
        file_tree = []
        # Basic file tree generation - refine later
        for step in plan:
            agent = step.get("agent")
            task = step.get("task")
            # Use a more consistent naming convention
            base_name = project_id.replace(" ", "_").lower()
            path = None
            if "build_api_schema" in task:
                path = f"app/schemas/{base_name}_api_schema.py"
            elif "build_api_module" in task:
                path = f"app/modules/{base_name}_api_module.py"
            elif "build_api_routes" in task:
                path = f"app/routes/{base_name}_api_routes.py"
            elif "generate_api_tests" in task:
                path = f"tests/test_{base_name}_api.py"
            elif "generate_mvp_component" in task:
                path = f"app/components/{base_name}_component.py"
            elif "generate_initial_files" in task:
                path = f"app/utils/{base_name}_utils.py" # Example for utils

            if path:
                # Store the task name explicitly with the file path
                file_tree.append({"path": path, "status": "grey", "owner": agent, "task_name": task})

        # Remove duplicates (based on path, assuming one task per path in this simple model)
        unique_file_tree = []
        seen_paths = set()
        for item in file_tree:
            if item["path"] not in seen_paths:
                unique_file_tree.append(item)
                seen_paths.add(item["path"])

        # Log file tree to memory
        await write_memory(
            project_id=project_id,
            agent_id=self.name,
            loop_id=loop_id,
            tag=f"file_tree_{loop_id}",
            value=unique_file_tree,
            type="project_file_tree"
        )
        logger.info(f"[{project_id}-{loop_id}] File tree architected and saved.")
        return unique_file_tree

    async def trigger_build(self, plan: list, file_tree: list, project_id: str, loop_id: str):
        """Delegates file creation to HAL or Forge based on the plan and file tree."""
        logger.info(f"[{project_id}-{loop_id}] Triggering build process based on plan and file tree.")
        delegation_results = []
        for step in plan:
            agent_name = step.get("agent")
            task_name = step.get("task")
            target_path = None

            # Find corresponding file path in the tree using the stored task_name
            for item in file_tree:
                if item.get("task_name") == task_name and item.get("owner") == agent_name:
                    target_path = item.get("path")
                    break

            if not target_path:
                logger.warning(f"[{project_id}-{loop_id}] Could not find target path in file tree for task: {task_name}. Skipping delegation.")
                continue

            # Add path to task details for the build agent
            step_details_with_path = step.copy()
            step_details_with_path["details"] = step_details_with_path.get("details", {})
            step_details_with_path["details"]["path"] = target_path

            # Only delegate build tasks to Forge or HAL
            if agent_name in ["forge-agent", "hal-agent"]:
                result = await self.delegate_task(agent_name, step_details_with_path, project_id, loop_id)
                delegation_results.append(result)
            else:
                 logger.info(f"[{project_id}-{loop_id}] Skipping delegation for non-build agent: {agent_name} (Task: {task_name})")

        logger.info(f"[{project_id}-{loop_id}] Build trigger complete. Delegated {len(delegation_results)} tasks.")
        return delegation_results

    async def reflect_on_result(self, result_payload: dict, project_id: str, loop_id: str):
        """Stub method: Logs build result with thread_id/loop_id."""
        source_agent = result_payload.get("source_agent", "unknown")
        status = result_payload.get("status", "unknown")
        logger.info(f"[{project_id}-{loop_id}] Reflecting on result from {source_agent}: {status}")
        # Log the reflection/result summary
        await write_memory(
            project_id=project_id,
            agent_id=self.name,
            loop_id=loop_id,
            tag=f"reflection_{source_agent}_{loop_id}",
            value=result_payload,
            type="agent_reflection"
        )
        logger.info(f"[{project_id}-{loop_id}] Reflection logged.")
        return {"status": "success", "reflection_logged": True}

    async def execute(self, payload: dict) -> Dict[str, Any]: # Changed signature to match expected usage
        """
        Execute the Architect Orchestrator's main functionality.
        Expects payload from memory or initial trigger.
        """
        project_id = payload.get("project_id")
        loop_id = payload.get("loop_id")
        task = payload.get("task")
        details = payload.get("details", {})
        source_agent = payload.get("source_agent")

        if not all([project_id, loop_id, task]):
            error_msg = "Invalid payload: Missing project_id, loop_id, or task."
            logger.error(error_msg)
            return {"status": "error", "error": error_msg, "timestamp": datetime.datetime.now().isoformat()}

        logger.info(f"[{project_id}-{loop_id}] ArchitectOrchestrator executing task: {task} from {source_agent}")
        print(f"🏛️ ArchitectOrchestrator executing task \'{task}\' on project \'{project_id}\' (Loop: {loop_id})")

        result = {
            "status": "success",
            "task": task,
            "project_id": project_id,
            "loop_id": loop_id,
            "mode": self.current_mode,
            "timestamp": datetime.datetime.now().isoformat(),
            "output": None
        }

        try:
            # Determine action based on task or source_agent
            if source_agent == "operator" or task == "plan_and_build": # Initial trigger
                goal = details.get("goal", task) # Use task as goal if not specified
                if not goal:
                    raise ValueError("Goal is required for initial planning task")
                # 1. Plan Project
                plan = await self.plan_project(goal, project_id, loop_id)
                result["plan"] = plan
                # 2. Architect File Tree
                file_tree = await self.architect_file_tree(plan, project_id, loop_id)
                result["file_tree"] = file_tree
                # 3. Trigger Build (Delegate Tasks)
                delegation_info = await self.trigger_build(plan, file_tree, project_id, loop_id)

                # Determine the *first* delegation for the result status
                if delegation_info:
                    first_delegation = delegation_info[0]
                    delegated_agent_name = first_delegation.get("delegated_to", "unknown_agent")
                    result["status"] = "delegated" # Indicate delegation occurred
                    result["delegated_to"] = delegated_agent_name
                    result["delegation_tag"] = first_delegation.get("delegation_tag") # Corrected key
                    result["output"] = f"Planned, architected, and delegated first task ({delegated_agent_name}) for goal: {goal}"
                else:
                    result["output"] = f"Planned project and architected file tree for goal: {goal}. No build tasks to delegate immediately."
                    result["status"] = "complete" # No delegation needed

            elif source_agent in ["forge-agent", "hal-agent"]: # Result from a build agent
                # Reflect on the result received
                reflection_result = await self.reflect_on_result(payload, project_id, loop_id)
                result.update(reflection_result)
                result["output"] = f"Processed result from agent: {source_agent}"
                result["status"] = "complete" # Mark loop step as complete after reflection
                # Future: Trigger next step based on reflection/plan status

            # --- Add other task handlers as needed ---
            elif task == "get_plan":
                 try:
                     plan_data = await read_memory(project_id, f"project_plan_{loop_id}")
                     result["plan"] = plan_data
                     result["output"] = "Retrieved project plan from memory."
                 except Exception:
                     result["status"] = "error"
                     result["output"] = "Failed to retrieve project plan."
                     result["error"] = "Plan not found in memory for this loop_id."

            else:
                result["status"] = "warning"
                result["output"] = f"Unknown task or unhandled source agent ({source_agent}) for ArchitectOrchestrator: {task}"

            # Validate schema before returning
            if not self.validate_schema(result):
                 logger.error(f"[{project_id}-{loop_id}] Schema validation failed for result.")
                 # Fallback to a minimal valid error structure if needed
                 raise ValueError("Internal schema validation failed")

            return result

        except Exception as e:
            error_msg = f"Error in ArchitectOrchestrator: {str(e)}"
            logger.error(f"[{project_id}-{loop_id}] {error_msg}")
            logger.error(traceback.format_exc())
            print(f"❌ {error_msg}")
            # Return error response
            return {
                "status": "error",
                "task": task,
                "project_id": project_id,
                "loop_id": loop_id,
                "mode": self.current_mode,
                "timestamp": datetime.datetime.now().isoformat(),
                "output": f"Error executing task: {error_msg}",
                "error": error_msg
            }

# Example usage (for testing)
# async def run_orchestrator_agent(payload: dict):
#     agent = OrchestratorAgent()
#     return await agent.execute(payload=payload)

# Example of how to run async code if needed for testing directly
# import asyncio
# async def main():
#     initial_payload = {
#         "project_id": "test_project_123",
#         "loop_id": f"loop_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}",
#         "task": "plan_and_build",
#         "details": {"goal": "create simple api"},
#         "source_agent": "operator"
#     }
#     result = await run_orchestrator_agent(payload=initial_payload)
#     print(json.dumps(result, indent=2))
# if __name__ == "__main__":
#     asyncio.run(main())


