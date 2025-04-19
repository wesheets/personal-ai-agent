"""
Schema Registry Module

This module defines the schema registry for validating various data structures
in the application. It provides type definitions for expected fields in different
parts of the system, particularly for project memory validation, API request validation,
agent role validation, loop structure validation, and reflection validation.
"""

from typing import Dict, Any, Type

# Schema registry for different data structures in the application
SCHEMA_REGISTRY = {
    "memory": {
        "project": {
            "project_id": str,
            "timestamp": str,
            "status": str,
            "next_recommended_step": str,
            "loop_status": str,
            "agents": dict,
            "task_log": list,
            "logic_modules": dict,
            "registry": dict
        }
    },
    "api": {
        "/api/agent/run": {
            "method": "POST",
            "input": {
                "project_id": str,
                "agent": str
            },
            "output": {
                "status": str,
                "message": str
            }
        },
        "/api/loop/start": {
            "method": "POST",
            "input": {
                "project_id": str
            },
            "output": {
                "status": str,
                "details": dict
            }
        }
    },
    "agents": {
        "hal": {
            "role": "initial builder",
            "dependencies": [],
            "produces": ["README.md", "requirements.txt"],
            "unlocks": ["nova"]
        },
        "nova": {
            "role": "logic writer",
            "dependencies": ["hal"],
            "produces": ["api_routes", "logic_modules"],
            "unlocks": ["critic"]
        },
        "critic": {
            "role": "review + logic auditor",
            "dependencies": ["nova"],
            "produces": ["feedback_log", "next_agent_recommendation"],
            "unlocks": ["ash", "orchestrator"]
        },
        "ash": {
            "role": "documenter",
            "dependencies": ["critic"],
            "produces": ["README updates", "documentation"],
            "unlocks": ["sage"]
        },
        "sage": {
            "role": "reflection + loop closer",
            "dependencies": ["ash"],
            "produces": ["summary", "final reflections"],
            "unlocks": ["hal"]
        }
    },
    "loop": {
        "required_agents": ["hal", "nova", "critic", "ash", "sage"],
        "max_loops": 5,
        "exit_conditions": ["loop_complete == true", "loop_count >= max_loops"]
    },
    "reflection": {
        "goal": str,
        "summary": str,
        "confidence": float,
        "tags": list
    }
}
