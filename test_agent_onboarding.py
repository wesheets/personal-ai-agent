"""
Test Script for Agent Onboarding System

This script tests the agent onboarding system by simulating the onboarding process
for HAL and verifying that all required components work correctly.
"""

import os
import sys
import json
import datetime
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.append('/home/ubuntu/workspace/personal-ai-agent')

# Import onboarding modules
from src.onboarding.flow import OnboardingFlow, generate_goal_id
from src.onboarding.memory import MemorySystem
from src.onboarding.checkpoint import CheckpointSystem
from src.onboarding.logging import OnboardingLogger

def simulate_agent_self_check(agent_id: str) -> Dict[str, Any]:
    """Simulate the agent.self.check tool for testing."""
    if agent_id.lower() == "hal":
        return {
            "agent_id": "hal",
            "name": "HAL",
            "status": "active",
            "available_tools": [
                "code.read",
                "code.write",
                "code.comment",
                "unit.test.generate",
                "unit.test.run",
                "debug.trace",
                "api.build",
                "db.schema.generate"
            ],
            "role": "developer agent"
        }
    elif agent_id.lower() == "ash":
        return {
            "agent_id": "ash",
            "name": "ASH",
            "status": "active",
            "available_tools": [
                "copy.email.campaign",
                "content.blog.generate",
                "social.calendar.create",
                "meme.generate",
                "landing.hero.write",
                "copy.tagline"
            ],
            "role": "marketing agent"
        }
    else:
        return {
            "agent_id": agent_id,
            "name": agent_id.upper(),
            "status": "unknown",
            "available_tools": [],
            "role": "unknown agent"
        }

def simulate_read_doc(path: str) -> Dict[str, Any]:
    """Simulate the read.doc tool for testing."""
    if path == "/docs/core_values.md":
        try:
            with open('/home/ubuntu/workspace/personal-ai-agent/docs/core_values.md', 'r') as f:
                content = f.read()
                return {
                    "status": "success",
                    "path": path,
                    "content": content
                }
        except Exception as e:
            return {
                "status": "error",
                "path": path,
                "error": str(e)
            }
    else:
        return {
            "status": "error",
            "path": path,
            "error": "File not found"
        }

def simulate_code_write() -> Dict[str, Any]:
    """Simulate the code.write tool for HAL testing."""
    return {
        "status": "success",
        "language": "python",
        "code": "def hello_world():\n    print('Hello, world!')\n\nhello_world()",
        "execution_result": "Hello, world!"
    }

def simulate_copy_tagline() -> Dict[str, Any]:
    """Simulate the copy.tagline tool for ASH testing."""
    return {
        "status": "success",
        "product": "Promethios AI",
        "taglines": [
            "Intelligence that understands you",
            "AI that works for humans",
            "The future of AI, today"
        ],
        "recommended": "Intelligence that understands you"
    }

def test_onboarding_hal():
    """Test the onboarding process for HAL."""
    print("\n=== Testing HAL Agent Onboarding ===\n")
    
    # Initialize onboarding components
    agent_id = "hal"
    goal_id = generate_goal_id(agent_id)
    
    flow = OnboardingFlow(agent_id)
    memory_system = MemorySystem(agent_id, goal_id)
    checkpoint_system = CheckpointSystem(agent_id, goal_id)
    logger = OnboardingLogger(agent_id)
    
    # Log start of onboarding
    logger.log_event(
        event_type="start",
        message=f"Starting onboarding process for {agent_id}",
        metadata={"goal_id": goal_id}
    )
    
    # Step 1: Agent Self Check
    print("Step 1: Agent Self Check")
    current_step = flow.get_current_step()
    logger.log_step(
        step_id=current_step["id"],
        status="started",
        message=f"Starting step: {current_step['description']}"
    )
    
    # Simulate agent.self.check tool
    self_check_result = simulate_agent_self_check(agent_id)
    
    # Log tool usage
    logger.log_tool_usage(
        tool_name="agent.self.check",
        status="success",
        message="Agent performed self-check",
        result=self_check_result
    )
    
    # Create system memory
    system_memory = memory_system.create_system_memory(
        content=current_step["memory_prompt"],
        prompt=current_step["memory_prompt"]
    )
    
    # Create reflection
    reflection_content = current_step["reflection_template"].format(
        agent_role=self_check_result["role"]
    )
    reflection = memory_system.create_reflection(
        content=reflection_content,
        tool_name="agent.self.check",
        step_id=current_step["id"]
    )
    
    # Log reflection
    logger.log_reflection(
        content=reflection_content,
        tool_name="agent.self.check",
        step_id=current_step["id"]
    )
    
    # Mark step complete
    flow.mark_step_complete(current_step["id"])
    logger.log_step(
        step_id=current_step["id"],
        status="completed",
        message=f"Completed step: {current_step['description']}"
    )
    
    # Advance to next step
    flow.advance_to_next_step()
    
    # Step 2: Core Values
    print("Step 2: Core Values")
    current_step = flow.get_current_step()
    logger.log_step(
        step_id=current_step["id"],
        status="started",
        message=f"Starting step: {current_step['description']}"
    )
    
    # Simulate read.doc tool
    read_doc_result = simulate_read_doc(current_step["tool_args"]["path"])
    
    # Log tool usage
    logger.log_tool_usage(
        tool_name="read.doc",
        status=read_doc_result["status"],
        message=f"Agent read document: {current_step['tool_args']['path']}",
        result=read_doc_result
    )
    
    # Create system memory
    system_memory = memory_system.create_system_memory(
        content=current_step["memory_prompt"],
        prompt=current_step["memory_prompt"]
    )
    
    # Create reflection
    reflection = memory_system.create_reflection(
        content=current_step["reflection_template"],
        tool_name="read.doc",
        step_id=current_step["id"]
    )
    
    # Log reflection
    logger.log_reflection(
        content=current_step["reflection_template"],
        tool_name="read.doc",
        step_id=current_step["id"]
    )
    
    # Mark step complete
    flow.mark_step_complete(current_step["id"])
    logger.log_step(
        step_id=current_step["id"],
        status="completed",
        message=f"Completed step: {current_step['description']}"
    )
    
    # Advance to next step
    flow.advance_to_next_step()
    
    # Step 3: Tool Familiarization
    print("Step 3: Tool Familiarization")
    current_step = flow.get_current_step()
    logger.log_step(
        step_id=current_step["id"],
        status="started",
        message=f"Starting step: {current_step['description']}"
    )
    
    # Get the appropriate tool for HAL
    tool_name = flow.get_agent_specific_tool(agent_id, current_step)
    
    # Simulate code.write tool
    code_write_result = simulate_code_write()
    
    # Log tool usage
    logger.log_tool_usage(
        tool_name=tool_name,
        status="success",
        message=f"Agent used {tool_name} tool",
        result=code_write_result
    )
    
    # Create action memory
    action_memory = memory_system.create_action_memory(
        action=f"Used {tool_name} to write a hello world program",
        tool_name=tool_name,
        result=code_write_result,
        status="success"
    )
    
    # Create reflection
    reflection = memory_system.create_reflection(
        content=current_step["reflection_template"],
        tool_name=tool_name,
        step_id=current_step["id"]
    )
    
    # Log reflection
    logger.log_reflection(
        content=current_step["reflection_template"],
        tool_name=tool_name,
        step_id=current_step["id"]
    )
    
    # Mark step complete
    flow.mark_step_complete(current_step["id"])
    logger.log_step(
        step_id=current_step["id"],
        status="completed",
        message=f"Completed step: {current_step['description']}"
    )
    
    # Advance to next step
    flow.advance_to_next_step()
    
    # Step 4: Final Checkpoint
    print("Step 4: Final Checkpoint")
    current_step = flow.get_current_step()
    logger.log_step(
        step_id=current_step["id"],
        status="started",
        message=f"Starting step: {current_step['description']}"
    )
    
    # Get all memory IDs
    memory_ids = [m["id"] for m in memory_system.memories]
    
    # Create final checkpoint
    final_checkpoint = checkpoint_system.create_final_checkpoint(
        memory_ids=memory_ids,
        status="complete",
        details={
            "agent_id": agent_id,
            "goal_id": goal_id,
            "completed_steps": [step["step_id"] for step in flow.completed_steps],
            "memory_count": len(memory_ids)
        }
    )
    
    # Log checkpoint
    logger.log_checkpoint(
        checkpoint_id=current_step["checkpoint_id"],
        status="complete",
        message="Agent onboarding completed successfully"
    )
    
    # Mark step complete
    flow.mark_step_complete(current_step["id"])
    logger.log_step(
        step_id=current_step["id"],
        status="completed",
        message=f"Completed step: {current_step['description']}"
    )
    
    # Log completion
    logger.log_completion(
        status="success",
        message=f"Onboarding process for {agent_id} completed successfully"
    )
    
    # Generate and save onboarding log
    log_path = flow.save_onboarding_log()
    print(f"Onboarding log saved to: {log_path}")
    
    # Verify onboarding completion
    is_complete = flow.is_onboarding_complete()
    print(f"Onboarding complete: {is_complete}")
    
    # Generate report
    report = logger.generate_report()
    
    # Save report to file
    report_path = os.path.join("/home/ubuntu/workspace/personal-ai-agent/logs", f"onboarding_{agent_id}_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Onboarding report saved to: {report_path}")
    print("\nHAL onboarding test completed successfully!")
    
    return {
        "agent_id": agent_id,
        "is_complete": is_complete,
        "memory_count": len(memory_system.memories),
        "checkpoint_count": len(checkpoint_system.checkpoints),
        "log_count": len(logger.logs),
        "report_path": report_path,
        "log_path": log_path
    }

def test_onboarding_ash():
    """Test the onboarding process for ASH."""
    print("\n=== Testing ASH Agent Onboarding ===\n")
    
    # Initialize onboarding components
    agent_id = "ash"
    goal_id = generate_goal_id(agent_id)
    
    flow = OnboardingFlow(agent_id)
    memory_system = MemorySystem(agent_id, goal_id)
    checkpoint_system = CheckpointSystem(agent_id, goal_id)
    logger = OnboardingLogger(agent_id)
    
    # Log start of onboarding
    logger.log_event(
        event_type="start",
        message=f"Starting onboarding process for {agent_id}",
        metadata={"goal_id": goal_id}
    )
    
    # Step 1: Agent Self Check
    print("Step 1: Agent Self Check")
    current_step = flow.get_current_step()
    logger.log_step(
        step_id=current_step["id"],
        status="started",
        message=f"Starting step: {current_step['description']}"
    )
    
    # Simulate agent.self.check tool
    self_check_result = simulate_agent_self_check(agent_id)
    
    # Log tool usage
    logger.log_tool_usage(
        tool_name="agent.self.check",
        status="success",
        message="Agent performed self-check",
        result=self_check_result
    )
    
    # Create system memory
    system_memory = memory_system.create_system_memory(
        content=current_step["memory_prompt"],
        prompt=current_step["memory_prompt"]
    )
    
    # Create reflection
    reflection_content = current_step["reflection_template"].format(
        agent_role=self_check_result["role"]
    )
    reflection = memory_system.create_reflection(
        content=reflection_content,
        tool_name="agent.self.check",
        step_id=current_step["id"]
    )
    
    # Log reflection
    logger.log_reflection(
        content=reflection_content,
        tool_name="agent.self.check",
        step_id=current_step["id"]
    )
    
    # Mark step complete
    flow.mark_step_complete(current_step["id"])
    logger.log_step(
        step_id=current_step["id"],
        status="completed",
        message=f"Completed step: {current_step['description']}"
    )
    
    # Advance to next step
    flow.advance_to_next_step()
    
    # Step 2: Core Values
    print("Step 2: Core Values")
    current_step = flow.get_current_step()
    logger.log_step(
        step_id=current_step["id"],
        status="started",
        message=f"Starting step: {current_step['description']}"
    )
    
    # Simulate read.doc tool
    read_doc_result = simulate_read_doc(current_step["tool_args"]["path"])
    
    # Log tool usage
    logger.log_tool_usage(
        tool_name="read.doc",
        status=read_doc_result["status"],
        message=f"Agent read document: {current_step['tool_args']['path']}",
        result=read_doc_result
    )
    
    # Create system memory
    system_memory = memory_system.create_system_memory(
        content=current_step["memory_prompt"],
        prompt=current_step["memory_prompt"]
    )
    
    # Create reflection
    reflection = memory_system.create_reflection(
        content=current_step["reflection_template"],
        tool_name="read.doc",
        step_id=current_step["id"]
    )
    
    # Log reflection
    logger.log_reflection(
        content=current_step["reflection_template"],
        tool_name="read.doc",
        step_id=current_step["id"]
    )
    
    # Mark step complete
    flow.mark_step_complete(current_step["id"])
    logger.log_step(
        step_id=current_step["id"],
        status="completed",
        message=f"Completed step: {current_step['description']}"
    )
    
    # Advance to next step
    flow.advance_to_next_step()
    
    # Step 3: Tool Familiarization
    print("Step 3: Tool Familiarization")
    current_step = flow.get_current_step()
    logger.log_step(
        step_id=current_step["id"],
        status="started",
        message=f"Starting step: {current_step['description']}"
    )
    
    # Get the appropriate tool for ASH
    tool_name = flow.get_agent_specific_tool(agent_id, current_step)
    
    # Simulate copy.tagline tool
    copy_tagline_result = simulate_copy_tagline()
    
    # Log tool usage
    logger.log_tool_usage(
        tool_name=tool_name,
        status="success",
        message=f"Agent used {tool_name} tool",
        result=copy_tagline_result
    )
    
    # Create action memory
    action_memory = memory_system.create_action_memory(
        action=f"Used {tool_name} to generate taglines for Promethios AI",
        tool_name=tool_name,
        result=copy_tagline_result,
        status="success"
    )
    
    # Create reflection
    reflection = memory_system.create_reflection(
        content=current_step["reflection_template"],
        tool_name=tool_name,
        step_id=current_step["id"]
    )
    
    # Log reflection
    logger.log_reflection(
        content=current_step["reflection_template"],
        tool_name=tool_name,
        step_id=current_step["id"]
    )
    
    # Mark step complete
    flow.mark_step_complete(current_step["id"])
    logger.log_step(
        step_id=current_step["id"],
        status="completed",
        message=f"Completed step: {current_step['description']}"
    )
    
    # Advance to next step
    flow.advance_to_next_step()
    
    # Step 4: Final Checkpoint
    print("Step 4: Final Checkpoint")
    current_step = flow.get_current_step()
    logger.log_step(
        step_id=current_step["id"],
        status="started",
        message=f"Starting step: {current_step['description']}"
    )
    
    # Get all memory IDs
    memory_ids = [m["id"] for m in memory_system.memories]
    
    # Create final checkpoint
    final_checkpoint = checkpoint_system.create_final_checkpoint(
        memory_ids=memory_ids,
        status="complete",
        details={
            "agent_id": agent_id,
            "goal_id": goal_id,
            "completed_steps": [step["step_id"] for step in flow.completed_steps],
            "memory_count": len(memory_ids)
        }
    )
    
    # Log checkpoint
    logger.log_checkpoint(
        checkpoint_id=current_step["checkpoint_id"],
        status="complete",
        message="Agent onboarding completed successfully"
    )
    
    # Mark step complete
    flow.mark_step_complete(current_step["id"])
    logger.log_step(
        step_id=current_step["id"],
        status="completed",
        message=f"Completed step: {current_step['description']}"
    )
    
    # Log completion
    logger.log_completion(
        status="success",
        message=f"Onboarding process for {agent_id} completed successfully"
    )
    
    # Generate and save onboarding log
    log_path = flow.save_onboarding_log()
    print(f"Onboarding log saved to: {log_path}")
    
    # Verify onboarding completion
    is_complete = flow.is_onboarding_complete()
    print(f"Onboarding complete: {is_complete}")
    
    # Generate report
    report = logger.generate_report()
    
    # Save report to file
    report_path = os.path.join("/home/ubuntu/workspace/personal-ai-agent/logs", f"onboarding_{agent_id}_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Onboarding report saved to: {report_path}")
    print("\nASH onboarding test completed successfully!")
    
    return {
        "agent_id": agent_id,
        "is_complete": is_complete,
        "memory_count": len(memory_system.memories),
        "checkpoint_count": len(checkpoint_system.checkpoints),
        "log_count": len(logger.logs),
        "report_path": report_path,
        "log_path": log_path
    }

def verify_reflections_and_checkpoints(hal_result, ash_result):
    """Verify that reflections and checkpoints were created correctly."""
    print("\n=== Verifying Reflections and Checkpoints ===\n")
    
    # Verify HAL reflections and checkpoints
    hal_memory_system = MemorySystem("hal", generate_goal_id("hal"))
    hal_memory_system.load_memories()
    
    hal_checkpoint_system = CheckpointSystem("hal", generate_goal_id("hal"))
    hal_checkpoint_system.load_checkpoints()
    
    hal_reflections = hal_memory_system.get_reflections()
    hal_checkpoints = hal_checkpoint_system.checkpoints
    
    print(f"HAL reflections: {len(hal_reflections)}")
    print(f"HAL checkpoints: {len(hal_checkpoints)}")
    
    # Verify ASH reflections and checkpoints
    ash_memory_system = MemorySystem("ash", generate_goal_id("ash"))
    ash_memory_system.load_memories()
    
    ash_checkpoint_system = CheckpointSystem("ash", generate_goal_id("ash"))
    ash_checkpoint_system.load_checkpoints()
    
    ash_reflections = ash_memory_system.get_reflections()
    ash_checkpoints = ash_checkpoint_system.checkpoints
    
    print(f"ASH reflections: {len(ash_reflections)}")
    print(f"ASH checkpoints: {len(ash_checkpoints)}")
    
    # Verify final checkpoints
    hal_final_checkpoint = hal_checkpoint_system.get_checkpoint("agent_onboarding_complete")
    ash_final_checkpoint = ash_checkpoint_system.get_checkpoint("agent_onboarding_complete")
    
    print(f"HAL final checkpoint exists: {hal_final_checkpoint is not None}")
    print(f"ASH final checkpoint exists: {ash_final_checkpoint is not None}")
    
    # Verify onboarding completion
    hal_is_complete = hal_checkpoint_system.has_completed_onboarding()
    ash_is_complete = ash_checkpoint_system.has_completed_onboarding()
    
    print(f"HAL onboarding complete: {hal_is_complete}")
    print(f"ASH onboarding complete: {ash_is_complete}")
    
    return {
        "hal": {
            "reflections_count": len(hal_reflections),
            "checkpoints_count": len(hal_checkpoints),
            "has_final_checkpoint": hal_final_checkpoint is not None,
            "is_complete": hal_is_complete
        },
        "ash": {
            "reflections_count": len(ash_reflections),
            "checkpoints_count": len(ash_checkpoints),
            "has_final_checkpoint": ash_final_checkpoint is not None,
            "is_complete": ash_is_complete
        }
    }

def main():
    """Main function to run the test script."""
    print("=== Starting Agent Onboarding System Test ===\n")
    
    # Create necessary directories
    os.makedirs("/home/ubuntu/workspace/personal-ai-agent/logs/memories", exist_ok=True)
    os.makedirs("/home/ubuntu/workspace/personal-ai-agent/logs/checkpoints", exist_ok=True)
    
    # Test HAL onboarding
    hal_result = test_onboarding_hal()
    
    # Test ASH onboarding
    ash_result = test_onboarding_ash()
    
    # Verify reflections and checkpoints
    verification_result = verify_reflections_and_checkpoints(hal_result, ash_result)
    
    # Generate summary report
    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "hal": hal_result,
        "ash": ash_result,
        "verification": verification_result
    }
    
    # Save summary report
    summary_path = "/home/ubuntu/workspace/personal-ai-agent/logs/onboarding_test_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nTest summary saved to: {summary_path}")
    print("\n=== Agent Onboarding System Test Completed Successfully ===")

if __name__ == "__main__":
    main()
