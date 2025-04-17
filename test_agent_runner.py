
import os
import sys
import json
import time
import traceback

# Import project_state for tracking project status
from app.modules.project_state import read_project_state, update_project_state
PROJECT_STATE_AVAILABLE = True

def run_hal_agent(task, project_id, tools):
    try:
        print(f"🤖 HAL agent execution started")
        
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if README.md already exists
            if "README.md" in project_state.get("files_created", []):
                print(f"⏩ README.md already exists, skipping duplicate write")
                return {
                    "status": "skipped",
                    "notes": "README.md already exists, skipping duplicate write.",
                    "output": project_state,
                    "project_state": project_state
                }
        
        # Initialize list of created files
        files_created = []
        
        # Simulate file creation
        files_created.append(f"/verticals/{project_id}/README.md")
        
        # Update project state
        project_state_data = {
            "status": "in_progress",
            "files_created": files_created,
            "agents_involved": ["hal"],
            "latest_agent_action": {
                "agent": "hal",
                "action": f"Created initial files for project {project_id}"
            },
            "next_recommended_step": "Run NOVA to design the project",
            "tool_usage": {
                "file_writer": 1
            }
        }
        
        update_project_state(project_id, project_state_data)
        
        # Return result with files_created list
        return {
            "status": "success",
            "message": f"HAL successfully created files for project {project_id}",
            "files_created": files_created,
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
    except Exception as e:
        print(f"❌ Error in run_hal_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing HAL agent: {str(e)}",
            "files_created": [],
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

def run_nova_agent(task, project_id, tools):
    print(f"🤖 NOVA agent execution started")
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if HAL has created initial files
            if "hal" not in project_state.get("agents_involved", []):
                print(f"⏩ HAL has not created initial files yet, cannot proceed")
                return {
                    "status": "blocked",
                    "notes": "Cannot create UI - HAL has not yet created initial project files.",
                    "project_state": project_state
                }
        
        # Simulate NOVA execution
        result = {
            "message": f"NOVA received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state
        project_state_data = {
            "agents_involved": ["nova"],
            "latest_agent_action": {
                "agent": "nova",
                "action": f"Designed project {project_id}"
            },
            "next_recommended_step": "Run ASH to create documentation",
            "tool_usage": {}
        }
        
        update_project_state(project_id, project_state_data)
        
        return result
    except Exception as e:
        print(f"❌ Error in run_nova_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing NOVA agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

def run_ash_agent(task, project_id, tools):
    print(f"🤖 ASH agent execution started")
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if project is ready for deployment
            if project_state.get("status") != "ready_for_deploy":
                print(f"⏩ Project not ready for deployment yet")
                return {
                    "status": "on_hold",
                    "notes": "Project not ready for deployment yet.",
                    "project_state": project_state
                }
        
        # Simulate ASH execution
        result = {
            "message": f"ASH received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state
        project_state_data = {
            "agents_involved": ["ash"],
            "latest_agent_action": {
                "agent": "ash",
                "action": f"Created documentation for project {project_id}"
            },
            "next_recommended_step": "Run CRITIC to review the project",
            "tool_usage": {}
        }
        
        update_project_state(project_id, project_state_data)
        
        return result
    except Exception as e:
        print(f"❌ Error in run_ash_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing ASH agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

def run_critic_agent(task, project_id, tools):
    print(f"🤖 CRITIC agent execution started")
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
            
            # Check if NOVA has created UI files
            if "nova" not in project_state.get("agents_involved", []):
                print(f"⏩ NOVA has not created UI files yet, cannot review")
                return {
                    "status": "blocked",
                    "notes": "Cannot review UI – NOVA has not yet created any frontend files.",
                    "project_state": project_state
                }
        
        # Simulate CRITIC execution
        result = {
            "message": f"CRITIC received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state
        project_state_data = {
            "status": "ready_for_deploy",
            "agents_involved": ["critic"],
            "latest_agent_action": {
                "agent": "critic",
                "action": f"Reviewed project {project_id}"
            },
            "next_recommended_step": "Run ASH to deploy",
            "tool_usage": {}
        }
        
        update_project_state(project_id, project_state_data)
        
        return result
    except Exception as e:
        print(f"❌ Error in run_critic_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing CRITIC agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

def run_orchestrator_agent(task, project_id, tools):
    print(f"🤖 ORCHESTRATOR agent execution started")
    
    try:
        # Read project state if available
        project_state = {}
        if PROJECT_STATE_AVAILABLE:
            project_state = read_project_state(project_id)
            print(f"📊 Project state read for {project_id}")
        
        # Simulate ORCHESTRATOR execution
        result = {
            "message": f"ORCHESTRATOR received task for project {project_id}",
            "task": task,
            "tools": tools,
            "project_state": project_state
        }
        
        # Update project state
        project_state_data = {
            "agents_involved": ["orchestrator"],
            "latest_agent_action": {
                "agent": "orchestrator",
                "action": f"Orchestrated project {project_id}"
            },
            "tool_usage": {}
        }
        
        update_project_state(project_id, project_state_data)
        
        return result
    except Exception as e:
        print(f"❌ Error in run_orchestrator_agent: {str(e)}")
        traceback.print_exc()
        
        return {
            "status": "error",
            "message": f"Error executing ORCHESTRATOR agent: {str(e)}",
            "task": task,
            "tools": tools,
            "error": str(e),
            "project_state": project_state if 'project_state' in locals() else {}
        }

# Map agent_id to runner function
AGENT_RUNNERS = {
    "hal": run_hal_agent,
    "nova": run_nova_agent,
    "ash": run_ash_agent,
    "critic": run_critic_agent,
    "orchestrator": run_orchestrator_agent
}
