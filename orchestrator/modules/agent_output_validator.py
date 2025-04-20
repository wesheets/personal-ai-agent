"""
Agent Output Validator Module

This module provides functionality to validate agent file outputs against predefined schemas
based on file type, agent role, and loop task.
"""

import json
import os
import sys
import re
import jsonschema
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Base path to the schema files
SCHEMA_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               'schemas', 'agent_output')

# File extension to schema mapping
FILE_SCHEMA_MAPPING = {
    ".jsx": "component_ui.schema.json",
    ".json": "data_model.schema.json",
    ".md": "doc_template.schema.json"
}

def get_schema_for_file(file_path: str, agent: str) -> str:
    """
    Maps file types to schema files based on file extension and agent role.
    
    Args:
        file_path (str): Path to the file to validate
        agent (str): The agent that created the file
        
    Returns:
        str: Path to the appropriate schema file
    """
    # Extract file extension
    _, ext = os.path.splitext(file_path)
    
    # Get schema filename from mapping
    schema_filename = FILE_SCHEMA_MAPPING.get(ext)
    
    # If no schema found for this extension, try to find a default schema
    if not schema_filename:
        # For now, we'll use a simple approach - in a real system, this would be more sophisticated
        if agent == "hal":
            schema_filename = "component_ui.schema.json"  # HAL typically works on UI components
        elif agent == "nova":
            schema_filename = "data_model.schema.json"    # NOVA typically works on data models
        elif agent == "critic":
            schema_filename = "doc_template.schema.json"  # CRITIC typically works on documentation
        else:
            raise ValueError(f"No schema found for file extension '{ext}' and agent '{agent}'")
    
    # Construct full path to schema file
    schema_path = os.path.join(SCHEMA_BASE_PATH, schema_filename)
    
    # Check if schema file exists
    if not os.path.exists(schema_path):
        raise ValueError(f"Schema file not found: {schema_path}")
    
    return schema_path

def validate_agent_file_output(agent: str, file_path: str, schema_path: Optional[str] = None) -> dict:
    """
    Reads the agent's file output and validates it against the appropriate schema.
    
    Args:
        agent (str): The agent that created the file
        file_path (str): Path to the file to validate
        schema_path (str, optional): Path to the schema file to use for validation
                                    If not provided, will be determined from file_path
        
    Returns:
        dict: Validation result with status and errors
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return {
            "valid": False,
            "errors": [f"File not found: {file_path}"]
        }
    
    try:
        # Read file content
        with open(file_path, 'r') as file:
            file_content = file.read()
        
        # If schema_path not provided, determine it from file_path
        if not schema_path:
            schema_path = get_schema_for_file(file_path, agent)
        
        # Load schema
        with open(schema_path, 'r') as schema_file:
            schema = json.load(schema_file)
        
        # Create validation object
        validation_object = {
            "fileContent": file_content,
            "metadata": extract_metadata(file_path, file_content, agent),
            "validation": {
                "errors": []
            }
        }
        
        # Validate against schema
        validator = jsonschema.Draft7Validator(schema)
        errors = list(validator.iter_errors(validation_object))
        
        if errors:
            # Format error messages
            error_messages = []
            for error in errors:
                if error.path:
                    path = '.'.join(str(p) for p in error.path)
                    error_messages.append(f"Error at '{path}': {error.message}")
                else:
                    error_messages.append(f"Error: {error.message}")
            
            return {
                "valid": False,
                "errors": error_messages
            }
        
        # Additional validation based on file type
        additional_errors = validate_file_content(file_path, file_content, agent)
        if additional_errors:
            return {
                "valid": False,
                "errors": additional_errors
            }
        
        # If we get here, validation passed
        return {
            "valid": True,
            "errors": []
        }
        
    except ValueError as e:
        return {
            "valid": False,
            "errors": [str(e)]
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Unexpected error during validation: {str(e)}"]
        }

def extract_metadata(file_path: str, file_content: str, agent: str) -> dict:
    """
    Extracts metadata from the file content based on file type.
    
    Args:
        file_path (str): Path to the file
        file_content (str): Content of the file
        agent (str): The agent that created the file
        
    Returns:
        dict: Metadata extracted from the file
    """
    _, ext = os.path.splitext(file_path)
    
    # Extract metadata based on file type
    if ext == ".jsx":
        return extract_jsx_metadata(file_content)
    elif ext == ".json":
        return extract_json_metadata(file_content)
    elif ext == ".md":
        return extract_md_metadata(file_content)
    else:
        # Default metadata
        return {
            "agent": agent,
            "fileType": ext,
            "createdAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }

def extract_jsx_metadata(file_content: str) -> dict:
    """
    Extracts metadata from a JSX file.
    
    Args:
        file_content (str): Content of the JSX file
        
    Returns:
        dict: Metadata extracted from the file
    """
    # Extract component name
    component_name_match = re.search(r'function\s+([A-Z][A-Za-z0-9]*)', file_content)
    if not component_name_match:
        component_name_match = re.search(r'class\s+([A-Z][A-Za-z0-9]*)', file_content)
    
    component_name = component_name_match.group(1) if component_name_match else "Unknown"
    
    # Check if component has props
    has_props = "props" in file_content
    
    # Check if component has state
    has_state = "useState" in file_content or "this.state" in file_content
    
    # Extract dependencies
    import_matches = re.findall(r'import\s+.*?from\s+[\'"](.+?)[\'"]', file_content)
    dependencies = import_matches if import_matches else []
    
    return {
        "componentName": component_name,
        "hasProps": has_props,
        "hasState": has_state,
        "dependencies": dependencies
    }

def extract_json_metadata(file_content: str) -> dict:
    """
    Extracts metadata from a JSON file.
    
    Args:
        file_content (str): Content of the JSON file
        
    Returns:
        dict: Metadata extracted from the file
    """
    try:
        # Parse JSON
        json_data = json.loads(file_content)
        
        # Extract model name if available
        model_name = "Unknown"
        if isinstance(json_data, dict):
            if "name" in json_data:
                model_name = json_data["name"]
            elif "title" in json_data:
                model_name = json_data["title"]
            elif "model" in json_data:
                model_name = json_data["model"]
        
        # Extract fields
        fields = []
        if isinstance(json_data, dict) and "fields" in json_data:
            fields = list(json_data["fields"].keys())
        elif isinstance(json_data, dict):
            fields = list(json_data.keys())
        
        # Extract relationships (simplified)
        relationships = []
        if isinstance(json_data, dict) and "relationships" in json_data:
            relationships = list(json_data["relationships"].keys())
        elif isinstance(json_data, dict):
            for key, value in json_data.items():
                if isinstance(value, dict) and "id" in value:
                    relationships.append(key)
        
        return {
            "modelName": model_name,
            "fields": fields,
            "relationships": relationships
        }
    except json.JSONDecodeError:
        return {
            "modelName": "Invalid",
            "fields": [],
            "relationships": []
        }

def extract_md_metadata(file_content: str) -> dict:
    """
    Extracts metadata from a Markdown file.
    
    Args:
        file_content (str): Content of the Markdown file
        
    Returns:
        dict: Metadata extracted from the file
    """
    # Extract title
    title_match = re.search(r'^#\s+(.+)$', file_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Unknown"
    
    # Extract sections
    section_matches = re.findall(r'^##\s+(.+)$', file_content, re.MULTILINE)
    sections = section_matches if section_matches else []
    
    # Check if file has code examples
    has_code_examples = '```' in file_content
    
    return {
        "title": title,
        "sections": sections,
        "hasCodeExamples": has_code_examples
    }

def validate_file_content(file_path: str, file_content: str, agent: str) -> List[str]:
    """
    Performs additional validation on file content based on file type.
    
    Args:
        file_path (str): Path to the file
        file_content (str): Content of the file
        agent (str): The agent that created the file
        
    Returns:
        list: List of validation errors, empty if valid
    """
    _, ext = os.path.splitext(file_path)
    errors = []
    
    # Validate based on file type
    if ext == ".jsx":
        # Check for React import
        if "import React" not in file_content and "import { React" not in file_content:
            errors.append("JSX file must import React")
        
        # Check for component definition
        if not re.search(r'function\s+[A-Z][A-Za-z0-9]*', file_content) and not re.search(r'class\s+[A-Z][A-Za-z0-9]*', file_content):
            errors.append("JSX file must define a component with PascalCase naming")
        
        # Check for export
        if "export default" not in file_content and "export function" not in file_content and "export class" not in file_content:
            errors.append("JSX file must export the component")
        
    elif ext == ".json":
        # Check if JSON is valid
        try:
            json.loads(file_content)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")
        
    elif ext == ".md":
        # Check for title
        if not re.search(r'^#\s+.+$', file_content, re.MULTILINE):
            errors.append("Markdown file must have a title (# Title)")
        
        # Check for sections
        if not re.search(r'^##\s+.+$', file_content, re.MULTILINE):
            errors.append("Markdown file must have at least one section (## Section)")
    
    return errors

def validate_and_log_output(project_id: str, agent: str, file_path: str) -> dict:
    """
    Runs validation on an agent's file output and logs the results.
    
    Args:
        project_id (str): The project identifier
        agent (str): The agent that created the file
        file_path (str): Path to the file to validate
        
    Returns:
        dict: Validation result with status and errors
    """
    # Get file name for logging
    file_name = os.path.basename(file_path)
    
    # Validate the file
    validation_result = validate_agent_file_output(agent, file_path)
    
    # Create timestamp for logging
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create trace entry
    trace_entry = {
        "type": "file_validation",
        "agent": agent,
        "file": file_name,
        "status": "passed" if validation_result["valid"] else "failed",
        "timestamp": timestamp
    }
    
    if not validation_result["valid"]:
        trace_entry["errors"] = validation_result["errors"]
    
    # Log to loop trace
    log_to_memory(project_id, {
        "loop_trace": [trace_entry]
    })
    
    # If validation failed, log to plan deviations
    if not validation_result["valid"]:
        deviation_entry = {
            "type": "file_validation_failed",
            "agent": agent,
            "file": file_name,
            "errors": validation_result["errors"],
            "timestamp": timestamp,
            "resolution": "file_rejected"
        }
        
        log_to_memory(project_id, {
            "plan_deviations": [deviation_entry]
        })
        
        # Log to CTO warnings
        cto_warning = {
            "type": "file_validation_failed",
            "agent": agent,
            "file": file_name,
            "errors": validation_result["errors"],
            "timestamp": timestamp,
            "severity": "medium"
        }
        
        log_to_memory(project_id, {
            "cto_warnings": [cto_warning]
        })
        
        # Log to chat
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"❌ File validation failed for {file_name} created by {agent.upper()}: {validation_result['errors'][0]}",
            "timestamp": timestamp
        })
        
        # Move file to rejected_output directory
        handle_rejected_file(file_path)
        
        # Notify CRITIC
        notify_critic(project_id, agent, file_path, validation_result["errors"])
    else:
        # Log success to chat
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"✅ File validation passed for {file_name} created by {agent.upper()}",
            "timestamp": timestamp
        })
    
    return validation_result

def handle_rejected_file(file_path: str):
    """
    Handles a rejected file by moving it to the rejected_output directory.
    
    Args:
        file_path (str): Path to the rejected file
    """
    # Create rejected_output directory if it doesn't exist
    rejected_dir = os.path.join(os.path.dirname(file_path), "rejected_output")
    os.makedirs(rejected_dir, exist_ok=True)
    
    # Get file name
    file_name = os.path.basename(file_path)
    
    # Create new path with timestamp to avoid overwriting
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    new_file_name = f"{timestamp}_{file_name}"
    new_file_path = os.path.join(rejected_dir, new_file_name)
    
    # Move file
    try:
        os.rename(file_path, new_file_path)
        print(f"Moved rejected file to {new_file_path}")
    except Exception as e:
        print(f"Error moving rejected file: {str(e)}")

def notify_critic(project_id: str, agent: str, file_path: str, errors: List[str]):
    """
    Notifies CRITIC about a validation failure.
    
    Args:
        project_id (str): The project identifier
        agent (str): The agent that created the file
        file_path (str): Path to the rejected file
        errors (List[str]): List of validation errors
    """
    # In a real implementation, this would trigger a CRITIC review
    # For now, we'll just print a message
    file_name = os.path.basename(file_path)
    print(f"Notifying CRITIC about validation failure for {file_name} created by {agent}")
    print(f"Errors: {errors}")

def log_to_memory(project_id: str, data: dict):
    """
    Logs data to project memory.
    
    Args:
        project_id (str): The project ID
        data (dict): The data to log
    """
    # In a real implementation, this would store data in a database or file
    print(f"Logging to memory for project {project_id}:")
    print(json.dumps(data, indent=2))

def log_to_chat(project_id: str, message: dict):
    """
    Logs a message to the chat.
    
    Args:
        project_id (str): The project ID
        message (dict): The message to log
    """
    # In a real implementation, this would add the message to the chat
    print(f"Logging to chat for project {project_id}:")
    print(json.dumps(message, indent=2))

if __name__ == "__main__":
    # Example usage
    project_id = "lifetree_001"
    agent = "hal"
    file_path = "src/components/UserProfile.jsx"
    
    # Validate and log output
    result = validate_and_log_output(project_id, agent, file_path)
    
    print("\nValidation result:")
    print(json.dumps(result, indent=2))
