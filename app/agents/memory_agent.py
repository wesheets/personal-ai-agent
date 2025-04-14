import json
import datetime
from typing import Dict, List, Optional, Any, Union

# Structured memory log
memory_log = []

def parse_log_message(message: str) -> Dict[str, Any]:
    """
    Parse a log message to extract structured information.
    
    Example input: "LOG: Core.Forge delegated task to Ops Agent"
    Example output: {
        "source": "Core.Forge",
        "target": "Ops Agent",
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

def handle_memory_task(task_input: str, project_id: Optional[str] = None, status: Optional[str] = None, task_type: Optional[str] = None) -> str:
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
        
        # Add project_id, status, and task_type if provided
        if project_id is not None:
            structured_entry["project_id"] = project_id
        if status is not None:
            structured_entry["status"] = status
        if task_type is not None:
            structured_entry["task_type"] = task_type
        
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
            
            # Add project_id, status, and task_type if provided
            if project_id is not None:
                structured_entry["project_id"] = project_id
            if status is not None:
                structured_entry["status"] = status
            if task_type is not None:
                structured_entry["task_type"] = task_type
                
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
    
    # New SEARCH mode implementation
    elif task_input.startswith("SEARCH:"):
        # Extract the search keyword
        keyword = task_input.replace("SEARCH:", "").strip().lower()
        
        # Search all memory entries for the keyword
        results = []
        for entry in memory_log:
            if isinstance(entry, dict):
                # For structured entries, search in all fields
                entry_str = json.dumps(entry).lower()
                if keyword in entry_str:
                    # Format the result with timestamp for better readability
                    timestamp = entry.get('timestamp', 'unknown')
                    if "raw_message" in entry:
                        results.append(f"[{timestamp}] {entry['raw_message']}")
                    else:
                        # Create a readable format for structured entries
                        source = entry.get('source', 'unknown')
                        entry_type = entry.get('type', 'log')
                        content = entry.get('input', '')
                        results.append(f"[{timestamp}] {source} - {entry_type}: {content}")
            else:
                # For legacy string entries
                if keyword in entry.lower():
                    results.append(entry)
        
        # Return formatted results
        if not results:
            return f"🔍 SEARCH: No memory entries found matching '{keyword}'"
        
        return f"🔍 SEARCH RESULTS FOR '{keyword}':\n" + "\n".join(results)
    
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
