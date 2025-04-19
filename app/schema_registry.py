"""
Schema Registry Module

This module defines the schema registry for validating various data structures
in the application. It provides type definitions for expected fields in different
parts of the system, particularly for project memory validation.
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
    }
}
