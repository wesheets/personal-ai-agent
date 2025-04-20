"""
Dry-Run Agent Execution Mode Module

This module provides functionality to simulate file generation without writing to disk or committing to Git,
enabling safe previews, pre-validation, operator review, and future loop planning scoring.
"""

import json
import os
import sys
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from orchestrator.modules.tool_predictor import check_tool_availability
from orchestrator.modules.agent_output_validator import get_schema_for_file, validate_file_content, extract_metadata

# Mock file content templates based on file type
FILE_TEMPLATES = {
    ".jsx": """import React, { useState } from 'react';

function {component_name}({props_definition}) {{
  {state_definition}
  
  return (
    <div className="{component_name_lower}">
      {content}
    </div>
  );
}}

export default {component_name};
""",
    ".json": """{{
  "name": "{model_name}",
  "fields": {{
    {fields}
  }},
  "relationships": {{
    {relationships}
  }}
}}
""",
    ".md": """# {title}

## Overview
{overview}

## Details
{details}

## Usage
```javascript
{code_example}
```
"""
}

def simulate_agent_output(agent_name: str, contract: dict) -> dict:
    """
    Simulates file generation based on an agent contract without writing to disk.
    
    Args:
        agent_name (str): The agent identifier (e.g., "hal", "nova", "critic")
        contract (dict): The agent contract received from Orchestrator
        
    Returns:
        dict: A simulated file result with content preview, tool used, validation result, and token estimate
    """
    if not contract or not isinstance(contract, dict):
        raise ValueError("Invalid contract object")
    
    # Extract required information from contract
    file = contract.get("file")
    if not file:
        raise ValueError("Contract missing file")
    
    goal = contract.get("goal")
    if not goal:
        raise ValueError("Contract missing goal")
    
    tools = contract.get("tools", [])
    if not tools:
        raise ValueError("Contract missing tools")
    
    # Check tool availability
    tool_status = {}
    for tool in tools:
        is_available = check_tool_availability(tool)
        tool_status[tool] = is_available
        
        if not is_available:
            return {
                "file": file,
                "content_preview": None,
                "tool_used": tool,
                "schema_validation_result": "failed",
                "validation_errors": [f"Required tool '{tool}' is not available"],
                "estimated_tokens": 0
            }
    
    # Determine file type and select appropriate tool
    _, ext = os.path.splitext(file)
    if ext == ".jsx":
        tool_used = next((t for t in tools if "component" in t.lower() or "ui" in t.lower()), tools[0])
        content_preview = generate_jsx_preview(file, goal)
    elif ext == ".json":
        tool_used = next((t for t in tools if "data" in t.lower() or "model" in t.lower()), tools[0])
        content_preview = generate_json_preview(file, goal)
    elif ext == ".md":
        tool_used = next((t for t in tools if "doc" in t.lower() or "template" in t.lower()), tools[0])
        content_preview = generate_md_preview(file, goal)
    else:
        # Default to text file
        tool_used = tools[0]
        content_preview = f"// Generated content for {file} based on goal: {goal}"
    
    # Estimate token count
    estimated_tokens = estimate_token_count(content_preview)
    
    # Validate content against schema
    validation_result, validation_errors = simulate_validation(agent_name, file, content_preview)
    
    # Prepare result
    result = {
        "file": file,
        "content_preview": content_preview,
        "tool_used": tool_used,
        "schema_validation_result": "passed" if validation_result else "failed",
        "estimated_tokens": estimated_tokens
    }
    
    # Add validation errors if any
    if not validation_result:
        result["validation_errors"] = validation_errors
    
    return result

def log_simulation_result(project_id: str, agent_name: str, loop_id: int, simulation_result: dict):
    """
    Logs simulation results to memory and traces.
    
    Args:
        project_id (str): The project identifier
        agent_name (str): The agent identifier
        loop_id (int): The loop identifier
        simulation_result (dict): The simulation result from simulate_agent_output
    """
    # Create timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create trace entry
    trace_entry = {
        "type": "dry_run_simulation",
        "agent": agent_name,
        "loop_id": loop_id,
        "file": simulation_result["file"],
        "tool_used": simulation_result["tool_used"],
        "validation_result": simulation_result["schema_validation_result"],
        "estimated_tokens": simulation_result["estimated_tokens"],
        "timestamp": timestamp
    }
    
    # Add validation errors if any
    if simulation_result["schema_validation_result"] == "failed" and "validation_errors" in simulation_result:
        trace_entry["validation_errors"] = simulation_result["validation_errors"]
    
    # Log to loop trace
    log_to_memory(project_id, {
        "loop_trace": [trace_entry]
    })
    
    # Log to agent-specific trace
    log_to_memory(project_id, {
        "agent_trace": {
            agent_name: [trace_entry]
        }
    })
    
    # Log to chat
    status_emoji = "✅" if simulation_result["schema_validation_result"] == "passed" else "⚠️"
    message = f"{status_emoji} Dry run simulation for {agent_name.upper()}: {simulation_result['file']}"
    
    if simulation_result["schema_validation_result"] == "failed" and "validation_errors" in simulation_result:
        message += f"\nValidation errors: {simulation_result['validation_errors'][0]}"
        if len(simulation_result["validation_errors"]) > 1:
            message += f" (and {len(simulation_result['validation_errors']) - 1} more)"
    
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": message,
        "timestamp": timestamp
    })

def dry_run_driver(project_id: str, agent_name: str, require_approval: bool = True):
    """
    Orchestrator-triggered entrypoint that handles the entire simulation process.
    
    Args:
        project_id (str): The project identifier
        agent_name (str): The agent identifier
        require_approval (bool): Whether to require operator approval before proceeding
        
    Returns:
        dict: The simulation result with approval status
    """
    # Retrieve agent contract
    contract = get_agent_contract(project_id, agent_name)
    if not contract:
        error_msg = f"No contract found for agent {agent_name}"
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"⚠️ {error_msg}",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        return {"error": error_msg}
    
    # Extract loop_id from contract
    loop_id = contract.get("loop_id")
    if not loop_id:
        error_msg = f"Contract for agent {agent_name} missing loop_id"
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"⚠️ {error_msg}",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        return {"error": error_msg}
    
    try:
        # Run simulation
        simulation_result = simulate_agent_output(agent_name, contract)
        
        # Log result
        log_simulation_result(project_id, agent_name, loop_id, simulation_result)
        
        # Post preview to chat/sandbox
        post_preview_to_chat(project_id, agent_name, simulation_result)
        
        # Add approval status to result
        simulation_result["requires_approval"] = require_approval
        simulation_result["approved"] = False
        
        # If approval is required, request it
        if require_approval:
            request_operator_approval(project_id, agent_name, simulation_result)
        
        return simulation_result
    except Exception as e:
        error_msg = f"Error during dry run simulation: {str(e)}"
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"❌ {error_msg}",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        return {"error": error_msg}

def get_agent_contract(project_id: str, agent_name: str) -> Optional[dict]:
    """
    Retrieves the agent contract from memory.
    
    Args:
        project_id (str): The project identifier
        agent_name (str): The agent identifier
        
    Returns:
        dict: The agent contract or None if not found
    """
    # In a real implementation, this would retrieve the contract from memory
    # For now, we'll return a mock contract
    return {
        "loop_id": 33,
        "agent": agent_name,
        "goal": f"Create {get_default_file_for_agent(agent_name)}",
        "file": get_default_file_for_agent(agent_name),
        "tools": get_default_tools_for_agent(agent_name),
        "confirmed": True,
        "received_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "trace_id": f"loop_33_{agent_name}_contract"
    }

def get_default_file_for_agent(agent_name: str) -> str:
    """
    Returns a default file name based on agent name.
    
    Args:
        agent_name (str): The agent identifier
        
    Returns:
        str: A default file name
    """
    if agent_name.lower() == "hal":
        return "LoginForm.jsx"
    elif agent_name.lower() == "nova":
        return "UserModel.json"
    elif agent_name.lower() == "critic":
        return "Documentation.md"
    else:
        return "Unknown.txt"

def get_default_tools_for_agent(agent_name: str) -> List[str]:
    """
    Returns default tools based on agent name.
    
    Args:
        agent_name (str): The agent identifier
        
    Returns:
        list: Default tools for the agent
    """
    if agent_name.lower() == "hal":
        return ["component_builder", "ui_generator"]
    elif agent_name.lower() == "nova":
        return ["data_modeler", "schema_validator"]
    elif agent_name.lower() == "critic":
        return ["doc_generator", "code_reviewer"]
    else:
        return ["generic_tool"]

def generate_jsx_preview(file: str, goal: str) -> str:
    """
    Generates a preview of a JSX file.
    
    Args:
        file (str): The file name
        goal (str): The goal from the contract
        
    Returns:
        str: A preview of the JSX file content
    """
    # Extract component name from file
    component_name = os.path.splitext(file)[0]
    component_name_lower = component_name.lower()
    
    # Generate props based on goal
    props = []
    if "form" in goal.lower():
        props = ["onSubmit", "initialValues", "isLoading"]
    elif "button" in goal.lower():
        props = ["onClick", "label", "variant"]
    elif "list" in goal.lower():
        props = ["items", "renderItem", "onItemClick"]
    
    props_definition = ", ".join(["{" + p + "}" for p in props]) if props else ""
    
    # Generate state based on goal
    state_definition = ""
    if "form" in goal.lower():
        state_definition = "const [values, setValues] = useState({});\nconst [errors, setErrors] = useState({});"
    elif "toggle" in goal.lower() or "switch" in goal.lower():
        state_definition = "const [isActive, setIsActive] = useState(false);"
    elif "list" in goal.lower():
        state_definition = "const [selectedItem, setSelectedItem] = useState(null);"
    
    # Generate content based on goal
    content = ""
    if "form" in goal.lower():
        content = "<form onSubmit={onSubmit}>\n        <input type=\"text\" placeholder=\"Username\" />\n        <input type=\"password\" placeholder=\"Password\" />\n        <button type=\"submit\">Submit</button>\n      </form>"
    elif "button" in goal.lower():
        content = "<button onClick={onClick}>{label || 'Click me'}</button>"
    elif "list" in goal.lower():
        content = "{items.map((item, index) => (\n        <div key={index} onClick={() => onItemClick(item)}>\n          {renderItem ? renderItem(item) : item.toString()}\n        </div>\n      ))}"
    else:
        content = "<p>Content for {component_name}</p>"
    
    # Fill template
    template = FILE_TEMPLATES[".jsx"]
    return template.format(
        component_name=component_name,
        component_name_lower=component_name_lower,
        props_definition=props_definition,
        state_definition=state_definition,
        content=content
    )

def generate_json_preview(file: str, goal: str) -> str:
    """
    Generates a preview of a JSON file.
    
    Args:
        file (str): The file name
        goal (str): The goal from the contract
        
    Returns:
        str: A preview of the JSON file content
    """
    # Extract model name from file
    model_name = os.path.splitext(file)[0]
    
    # Generate fields based on goal
    fields = {}
    if "user" in goal.lower() or "user" in file.lower():
        fields = {
            "id": "string",
            "username": "string",
            "email": "string",
            "createdAt": "datetime"
        }
    elif "product" in goal.lower() or "product" in file.lower():
        fields = {
            "id": "string",
            "name": "string",
            "price": "number",
            "description": "string",
            "inStock": "boolean"
        }
    elif "post" in goal.lower() or "post" in file.lower():
        fields = {
            "id": "string",
            "title": "string",
            "content": "string",
            "publishedAt": "datetime",
            "authorId": "string"
        }
    else:
        fields = {
            "id": "string",
            "name": "string",
            "description": "string"
        }
    
    # Generate relationships based on goal
    relationships = {}
    if "user" in goal.lower() or "user" in file.lower():
        relationships = {
            "posts": {
                "type": "hasMany",
                "model": "Post"
            },
            "profile": {
                "type": "hasOne",
                "model": "Profile"
            }
        }
    elif "product" in goal.lower() or "product" in file.lower():
        relationships = {
            "category": {
                "type": "belongsTo",
                "model": "Category"
            },
            "reviews": {
                "type": "hasMany",
                "model": "Review"
            }
        }
    elif "post" in goal.lower() or "post" in file.lower():
        relationships = {
            "author": {
                "type": "belongsTo",
                "model": "User"
            },
            "comments": {
                "type": "hasMany",
                "model": "Comment"
            }
        }
    
    # Format fields and relationships as JSON strings
    fields_str = ",\n    ".join([f'"{k}": "{v}"' for k, v in fields.items()])
    relationships_str = ",\n    ".join([f'"{k}": {json.dumps(v, indent=6).replace("      ", "    ")}' for k, v in relationships.items()])
    
    # Fill template
    template = FILE_TEMPLATES[".json"]
    return template.format(
        model_name=model_name,
        fields=fields_str,
        relationships=relationships_str
    )

def generate_md_preview(file: str, goal: str) -> str:
    """
    Generates a preview of a Markdown file.
    
    Args:
        file (str): The file name
        goal (str): The goal from the contract
        
    Returns:
        str: A preview of the Markdown file content
    """
    # Extract title from file
    title = os.path.splitext(file)[0].replace('-', ' ').replace('_', ' ').title()
    
    # Generate overview based on goal
    overview = f"This document provides information about {title}."
    
    # Generate details based on goal
    details = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam euismod, nisl eget aliquam ultricies, nunc nisl aliquet nunc, quis aliquam nisl nunc eu nisl."
    
    # Generate code example based on goal
    code_example = "// Example code\nconst example = new Example();\nexample.run();"
    if "component" in goal.lower() or ".jsx" in file.lower():
        code_example = "import React from 'react';\nimport { " + title.replace(' ', '') + " } from './" + title.replace(' ', '') + "';\n\nfunction App() {\n  return <" + title.replace(' ', '') + " />;\n}"
    elif "model" in goal.lower() or ".json" in file.lower():
        code_example = "const model = require('./" + file + "');\n\nconst instance = new Model(model);\ninstance.validate();"
    
    # Fill template
    template = FILE_TEMPLATES[".md"]
    return template.format(
        title=title,
        overview=overview,
        details=details,
        code_example=code_example
    )

def simulate_validation(agent_name: str, file: str, content: str) -> tuple:
    """
    Simulates validation of file content against schema.
    
    Args:
        agent_name (str): The agent identifier
        file (str): The file name
        content (str): The file content
        
    Returns:
        tuple: (is_valid, errors)
    """
    # Extract file extension
    _, ext = os.path.splitext(file)
    
    # Validate based on file type
    errors = []
    
    if ext == ".jsx":
        # Check for React import
        if "import React" not in content:
            errors.append("JSX file must import React")
        
        # Check for component definition
        if not re.search(r'function\s+[A-Z][A-Za-z0-9]*', content) and not re.search(r'class\s+[A-Z][A-Za-z0-9]*', content):
            errors.append("JSX file must define a component with PascalCase naming")
        
        # Check for export
        if "export default" not in content and "export function" not in content and "export class" not in content:
            errors.append("JSX file must export the component")
        
    elif ext == ".json":
        # Check if JSON is valid
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {str(e)}")
        
    elif ext == ".md":
        # Check for title
        if not re.search(r'^#\s+.+$', content, re.MULTILINE):
            errors.append("Markdown file must have a title (# Title)")
        
        # Check for sections
        if not re.search(r'^##\s+.+$', content, re.MULTILINE):
            errors.append("Markdown file must have at least one section (## Section)")
    
    return len(errors) == 0, errors

def estimate_token_count(content: str) -> int:
    """
    Estimates the token count of content.
    
    Args:
        content (str): The content to estimate
        
    Returns:
        int: Estimated token count
    """
    # A very simple estimation: roughly 4 characters per token
    return len(content) // 4

def post_preview_to_chat(project_id: str, agent_name: str, simulation_result: dict):
    """
    Posts a preview of the simulation result to chat.
    
    Args:
        project_id (str): The project identifier
        agent_name (str): The agent identifier
        simulation_result (dict): The simulation result
    """
    # Create timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create preview message
    message = f"🔍 Preview of {simulation_result['file']} from {agent_name.upper()} (dry run):\n"
    message += f"```\n{simulation_result['content_preview'][:200]}...\n```\n"
    message += f"Tool used: {simulation_result['tool_used']}\n"
    message += f"Validation: {simulation_result['schema_validation_result']}\n"
    message += f"Estimated tokens: {simulation_result['estimated_tokens']}"
    
    # Log to chat
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": message,
        "timestamp": timestamp
    })
    
def request_operator_approval(project_id: str, agent_name: str, simulation_result: dict):
    """
    Requests operator approval for a simulated file.
    
    Args:
        project_id (str): The project identifier
        agent_name (str): The agent identifier
        simulation_result (dict): The simulation result
        
    Returns:
        dict: Updated simulation result with approval status
    """
    # Create timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Create approval request message
    message = f"👀 Requesting approval for {simulation_result['file']} from {agent_name.upper()}.\n"
    message += f"Validation: {simulation_result['schema_validation_result']}\n"
    
    if simulation_result['schema_validation_result'] == "failed" and "validation_errors" in simulation_result:
        message += f"⚠️ Validation errors: {', '.join(simulation_result['validation_errors'])}\n"
    
    message += f"\nTo approve, use: approve_simulation('{project_id}', '{agent_name}', {simulation_result['file']})"
    
    # Log to chat
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": message,
        "timestamp": timestamp
    })
    
    # Log approval request to memory
    log_to_memory(project_id, {
        "approval_requests": [{
            "type": "simulation_approval",
            "agent": agent_name,
            "file": simulation_result["file"],
            "timestamp": timestamp,
            "status": "pending"
        }]
    })
    
    return simulation_result

def approve_simulation(project_id: str, agent_name: str, file: str):
    """
    Approves a simulated file for actual creation.
    
    Args:
        project_id (str): The project identifier
        agent_name (str): The agent identifier
        file (str): The file name
        
    Returns:
        dict: Result of the approval
    """
    # Create timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Update approval status in memory
    log_to_memory(project_id, {
        "approval_requests": [{
            "type": "simulation_approval",
            "agent": agent_name,
            "file": file,
            "timestamp": timestamp,
            "status": "approved"
        }]
    })
    
    # Log to chat
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": f"✅ Simulation approved for {file} from {agent_name.upper()}. Agent can proceed with actual file creation.",
        "timestamp": timestamp
    })
    
    # Log to loop trace
    log_to_memory(project_id, {
        "loop_trace": [{
            "type": "simulation_approved",
            "agent": agent_name,
            "file": file,
            "timestamp": timestamp
        }]
    })
    
    return {
        "status": "approved",
        "agent": agent_name,
        "file": file,
        "timestamp": timestamp
    }

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
    agent_name = "hal"
    
    # Run dry run driver
    print("\nRunning dry run driver:")
    result = dry_run_driver(project_id, agent_name)
    
    # Print result
    print("\nDry run result:")
    print(json.dumps(result, indent=2))
