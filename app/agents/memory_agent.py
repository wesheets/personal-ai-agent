import json
import datetime
from typing import Dict, List, Optional, Any, Union

# Structured memory log
memory_log = []

def parse_log_message(message: str) -> Dict[str, Any]:
    """
    Parse a log message to extract structured information.
    
    Example input: "LOG: Core.Forge delegated task to HAL"
    Example output: {
        "source": "Core.Forge",
        "target": "HAL",
        "type": "delegation",
        "input": "task",
        "timestamp": "2025-04-09T00:38:49.123456"
    }
    """
    # Default structure with current timestamp
    timestamp = datetime.datetime.now().isoformat()
    
    # Default values
    structured_log = {
        "source": "unknown",
        "target": "unknown",
        "type": "log",
        "input": message,
        "timestamp": timestamp
    }
    
    # Try to extract structured information from the message
    if "delegated" in message:
        parts = message.split()
        for i, word in enumerate(parts):
            if word == "delegated" and i > 0 and i+3 < len(parts) and parts[i+2] == "to":
                structured_log["source"] = parts[i-1]
                structured_log["target"] = parts[i+3]
                structured_log["type"] = "delegation"
                structured_log["input"] = parts[i+1]
                break
    elif "initialized" in message:
        parts = message.split()
        for i, word in enumerate(parts):
            if word == "initialized" and i > 0:
                structured_log["source"] = parts[i-1]
                structured_log["type"] = "initialization"
                break
    elif "completed" in message:
        parts = message.split()
        for i, word in enumerate(parts):
            if word == "completed" and i > 0:
                structured_log["source"] = parts[i-1]
                structured_log["type"] = "completion"
                break
    elif "error" in message.lower():
        parts = message.split()
        for i, word in enumerate(parts):
            if word.lower() == "error" and i > 0:
                structured_log["source"] = parts[i-1]
                structured_log["type"] = "error"
                break
    
    return structured_log

def handle_memory_task(task_input: str) -> str:
    """
    Handle memory-related tasks with structured logging.
    
    Args:
        task_input: The input task string
        
    Returns:
        A string response based on the task
    """
    if task_input.startswith("LOG:"):
        # Extract the actual log message
        entry = task_input.replace("LOG:", "").strip()
        
        # Parse the log message to extract structured information
        structured_entry = parse_log_message(entry)
        
        # Store both the structured entry and the original message for backward compatibility
        structured_entry["raw_message"] = entry
        memory_log.append(structured_entry)
        
        return f"🧠 Memory Logged: {entry}"
    
    elif task_input.startswith("STRUCTURED_LOG:"):
        # Direct structured log input (JSON format)
        try:
            # Remove the prefix and parse the JSON
            json_str = task_input.replace("STRUCTURED_LOG:", "").strip()
            structured_entry = json.loads(json_str)
            
            # Ensure timestamp exists
            if "timestamp" not in structured_entry:
                structured_entry["timestamp"] = datetime.datetime.now().isoformat()
                
            # Store the structured entry
            memory_log.append(structured_entry)
            
            return f"🧠 Structured Memory Logged: {json.dumps(structured_entry)}"
        except json.JSONDecodeError:
            return f"🧠 Error: Invalid JSON format in structured log"
    
    elif task_input == "SHOW":
        # Return the 10 most recent logs in a readable format
        if not memory_log:
            return "🧠 No recent memory."
        
        result = []
        for entry in memory_log[-10:]:
            if isinstance(entry, dict):
                # Format structured entry
                if "raw_message" in entry:
                    result.append(entry["raw_message"])
                else:
                    # Format structured entry without raw message
                    formatted = f"[{entry.get('timestamp', 'unknown')}] "
                    formatted += f"{entry.get('source', 'unknown')} "
                    
                    if entry.get('type') == "delegation":
                        formatted += f"delegated {entry.get('input', 'task')} to {entry.get('target', 'unknown')}"
                    else:
                        formatted += f"{entry.get('type', 'log')}: {entry.get('input', '')}"
                    
                    result.append(formatted)
            else:
                # Handle legacy string entries
                result.append(entry)
        
        return "\n".join(result)
    
    elif task_input == "SHOW_STRUCTURED":
        # Return the 10 most recent logs in structured JSON format
        if not memory_log:
            return "🧠 No recent memory."
        
        return json.dumps(memory_log[-10:], indent=2)
    
    elif task_input == "FULL":
        # Return all logs in a readable format
        if not memory_log:
            return "🧠 Memory is empty."
        
        result = []
        for entry in memory_log:
            if isinstance(entry, dict):
                # Format structured entry
                if "raw_message" in entry:
                    result.append(entry["raw_message"])
                else:
                    # Format structured entry without raw message
                    formatted = f"[{entry.get('timestamp', 'unknown')}] "
                    formatted += f"{entry.get('source', 'unknown')} "
                    
                    if entry.get('type') == "delegation":
                        formatted += f"delegated {entry.get('input', 'task')} to {entry.get('target', 'unknown')}"
                    else:
                        formatted += f"{entry.get('type', 'log')}: {entry.get('input', '')}"
                    
                    result.append(formatted)
            else:
                # Handle legacy string entries
                result.append(entry)
        
        return "\n".join(result)
    
    elif task_input == "FULL_STRUCTURED":
        # Return all logs in structured JSON format
        if not memory_log:
            return "🧠 Memory is empty."
        
        return json.dumps(memory_log, indent=2)
    
    elif task_input.startswith("QUERY:"):
        # Simple query functionality
        query = task_input.replace("QUERY:", "").strip().lower()
        
        results = []
        for entry in memory_log:
            if isinstance(entry, dict):
                # Search in structured entry
                entry_str = json.dumps(entry).lower()
                if query in entry_str:
                    if "raw_message" in entry:
                        results.append(entry["raw_message"])
                    else:
                        results.append(json.dumps(entry))
            else:
                # Search in legacy string entry
                if query in entry.lower():
                    results.append(entry)
        
        if not results:
            return f"🧠 No memory entries found matching query: '{query}'"
        
        return "\n".join(results)
    
    else:
        return f"🧠 MemoryAgent did not understand: '{task_input}'"

def add_memory_entry(message: str, details: str = "", source: str = "system") -> Dict[str, Any]:
    """
    Add a new memory entry programmatically.
    
    Args:
        message: The main message
        details: Additional details
        source: The source of the memory entry
        
    Returns:
        The created memory entry
    """
    timestamp = datetime.datetime.now().isoformat()
    
    structured_entry = {
        "source": source,
        "type": "log",
        "input": message,
        "details": details,
        "timestamp": timestamp,
        "raw_message": f"{source}: {message}"
    }
    
    memory_log.append(structured_entry)
    return structured_entry
