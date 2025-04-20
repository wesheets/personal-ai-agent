SCHEMA_REGISTRY = {
    "agents": {
        "cto": {
            "role": "system validator",
            "dependencies": ["orchestrator"],
            "produces": ["cto_reflections", "system_flags"],
            "unlocks": []
        }
    },
    "memory_schema": {
        "cto_reflections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "loop": {"type": "integer"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "issues_found": {"type": "boolean"},
                    "issues": {"type": "object"},
                    "summary": {"type": "string"}
                },
                "required": ["loop", "timestamp", "issues_found", "summary"]
            }
        },
        "system_flags": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "timestamp": {"type": "string", "format": "date-time"},
                    "level": {"type": "string", "enum": ["info", "warning", "error"]},
                    "origin": {"type": "string"},
                    "issues": {"type": "object"}
                },
                "required": ["timestamp", "level", "origin"]
            }
        }
    }
}
