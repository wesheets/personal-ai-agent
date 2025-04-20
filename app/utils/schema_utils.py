import jsonschema
from app.schema_registry import SCHEMA_REGISTRY

def validate_project_memory(project_id: str, project_memory):
    """
    Validates the project memory against the schema registry.
    Returns a list of validation errors or None if validation passes.
    """
    memory = project_memory.get(project_id, {})
    validation_errors = []
    
    # Validate each schema-defined memory structure
    for memory_key, schema in SCHEMA_REGISTRY.get("memory_schema", {}).items():
        if memory_key in memory:
            try:
                jsonschema.validate(instance=memory[memory_key], schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                validation_errors.append({
                    "memory_key": memory_key,
                    "error": str(e),
                    "path": list(e.path) if hasattr(e, 'path') else []
                })
    
    # Check for decay patterns
    # 1. Missing required memory keys
    required_keys = ["loop_count", "completed_steps", "last_reflection"]
    for key in required_keys:
        if key not in memory:
            validation_errors.append({
                "memory_key": key,
                "error": f"Required memory key '{key}' is missing",
                "path": []
            })
    
    # 2. Check for repeated failed tools if tool_history exists
    if "tool_history" in memory:
        tool_history = memory["tool_history"]
        failed_tools = {}
        
        for tool_entry in tool_history[-10:]:  # Check last 10 tool usages
            tool_name = tool_entry.get("tool_name")
            success = tool_entry.get("success", True)
            
            if not success:
                failed_tools[tool_name] = failed_tools.get(tool_name, 0) + 1
        
        for tool_name, failure_count in failed_tools.items():
            if failure_count >= 3:  # If a tool failed 3 or more times recently
                validation_errors.append({
                    "memory_key": "tool_history",
                    "error": f"Tool '{tool_name}' has failed {failure_count} times in recent history",
                    "path": ["tool_history"]
                })
    
    return validation_errors if validation_errors else None
