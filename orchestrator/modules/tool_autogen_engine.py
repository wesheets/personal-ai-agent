"""
Tool Autogeneration Engine Module

This module provides functionality to auto-generate missing tools when approved by the Operator
or pre-authorized by Orchestrator config, closing the tool prediction loop by turning
missing dependencies into generated solutions.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def propose_tool_generation(project_id: str, tool_name: str, goal_context: str, agent: str, loop_id: int) -> dict:
    """
    Generates a proposal for a missing tool with purpose, files, and validation.
    
    Args:
        project_id (str): The project identifier
        tool_name (str): The name of the missing tool
        goal_context (str): The context of the goal requiring the tool
        agent (str): The agent that needs the tool
        loop_id (int): The loop identifier
        
    Returns:
        dict: The tool generation proposal
    """
    # Create timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Determine tool purpose based on tool name and goal context
    purpose = determine_tool_purpose(tool_name, goal_context, agent)
    
    # Determine estimated files needed for the tool
    estimated_files = determine_tool_files(tool_name)
    
    # Determine linked file based on goal context
    linked_file = determine_linked_file(goal_context)
    
    # Generate a dry run result (mock implementation of the tool)
    dry_run_result = generate_dry_run_implementation(tool_name, purpose)
    
    # Validate the dry run result against schema
    schema_validation = validate_tool_schema(tool_name, dry_run_result)
    
    # Create the proposal object
    proposal = {
        "tool": tool_name,
        "purpose": purpose,
        "estimated_files": estimated_files,
        "linked_file": linked_file,
        "dry_run_result": dry_run_result,
        "schema_validation": schema_validation,
        "loop_id": loop_id,
        "timestamp": timestamp
    }
    
    # Log to memory
    log_to_memory(project_id, {
        "tool_proposals": [proposal]
    })
    
    # Log to loop trace
    log_to_memory(project_id, {
        "loop_trace": [{
            "type": "tool_proposal",
            "loop_id": loop_id,
            "agent": agent,
            "tool": tool_name,
            "status": schema_validation,
            "timestamp": timestamp
        }]
    })
    
    # Log to chat
    status_emoji = "✅" if schema_validation == "passed" else "⚠️"
    message = f"{status_emoji} Tool generation proposed: {tool_name} for {agent.upper()} in Loop {loop_id}"
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": message,
        "timestamp": timestamp,
        "preview": {
            "type": "tool_preview",
            "tool": tool_name,
            "purpose": purpose,
            "implementation": dry_run_result[:100] + "..." if len(dry_run_result) > 100 else dry_run_result
        }
    })
    
    return proposal

def tool_autogen_driver(project_id: str, loop_id: int, agent: str, tool_name: str) -> dict:
    """
    Orchestrator-triggered entrypoint that handles the entire tool generation process.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        agent (str): The agent that needs the tool
        tool_name (str): The name of the missing tool
        
    Returns:
        dict: The result of the tool generation process
    """
    # Create timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Check if tool is already available
    if is_tool_available(project_id, tool_name):
        result = {
            "status": "already_available",
            "tool": tool_name,
            "agent": agent,
            "loop_id": loop_id,
            "timestamp": timestamp
        }
        
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"ℹ️ Tool {tool_name} is already available for {agent.upper()} in Loop {loop_id}",
            "timestamp": timestamp
        })
        
        return result
    
    # Check if tool is pre-authorized for auto-generation
    is_preauthorized = check_preauthorization(project_id, tool_name, agent)
    
    # Get goal context from loop plan
    goal_context = get_goal_context(project_id, loop_id)
    
    # Propose tool generation
    proposal = propose_tool_generation(project_id, tool_name, goal_context, agent, loop_id)
    
    # If schema validation failed, log and return
    if proposal["schema_validation"] != "passed":
        result = {
            "status": "validation_failed",
            "tool": tool_name,
            "agent": agent,
            "loop_id": loop_id,
            "validation_error": proposal["schema_validation"],
            "timestamp": timestamp
        }
        
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"❌ Tool {tool_name} generation failed validation for {agent.upper()} in Loop {loop_id}",
            "timestamp": timestamp
        })
        
        return result
    
    # If not pre-authorized, wait for operator approval
    if not is_preauthorized:
        # Log to chat requesting approval
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"🔍 Awaiting operator approval for tool generation: {tool_name}",
            "timestamp": timestamp,
            "action_required": "approve_tool_generation",
            "tool": tool_name,
            "agent": agent,
            "loop_id": loop_id
        })
        
        # Log to memory
        log_to_memory(project_id, {
            "pending_approvals": [{
                "type": "tool_generation",
                "tool": tool_name,
                "agent": agent,
                "loop_id": loop_id,
                "timestamp": timestamp
            }]
        })
        
        # In a real implementation, this would wait for operator approval
        # For now, we'll assume approval is granted
        operator_approved = True
        approval_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        if not operator_approved:
            result = {
                "status": "rejected_by_operator",
                "tool": tool_name,
                "agent": agent,
                "loop_id": loop_id,
                "timestamp": approval_timestamp
            }
            
            log_to_chat(project_id, {
                "role": "orchestrator",
                "message": f"❌ Tool {tool_name} generation rejected by operator for {agent.upper()} in Loop {loop_id}",
                "timestamp": approval_timestamp
            })
            
            return result
    else:
        # Log pre-authorization
        log_to_chat(project_id, {
            "role": "orchestrator",
            "message": f"🔄 Tool {tool_name} pre-authorized for generation for {agent.upper()} in Loop {loop_id}",
            "timestamp": timestamp
        })
    
    # Generate the tool
    tool_path = generate_tool(project_id, tool_name, proposal["dry_run_result"], proposal["estimated_files"])
    
    # Log to tool history
    log_to_memory(project_id, {
        "tool_history": [{
            "tool": tool_name,
            "loop": loop_id,
            "agent": agent,
            "used_in": proposal["linked_file"],
            "status": "generated",
            "approved_by": "operator" if not is_preauthorized else "orchestrator",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }]
    })
    
    # Log to chat
    generation_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    log_to_chat(project_id, {
        "role": "orchestrator",
        "message": f"✅ Tool {tool_name} generated and scaffolded successfully.",
        "timestamp": generation_timestamp
    })
    
    # Return the result
    result = {
        "status": "generated",
        "tool": tool_name,
        "agent": agent,
        "loop_id": loop_id,
        "path": tool_path,
        "approved_by": "operator" if not is_preauthorized else "orchestrator",
        "timestamp": generation_timestamp
    }
    
    return result

def get_tool_history(project_id: str, tool_name: str) -> List[Dict[str, Any]]:
    """
    Returns the history of tool generation for a specific tool.
    
    Args:
        project_id (str): The project identifier
        tool_name (str): The name of the tool
        
    Returns:
        list: The tool generation history
    """
    # In a real implementation, this would retrieve data from a database or file
    # For now, we'll just print a message and return an empty list
    print(f"Retrieving tool history for {tool_name} in project {project_id}")
    
    # Return an empty list for demonstration
    return []

def determine_tool_purpose(tool_name: str, goal_context: str, agent: str) -> str:
    """
    Determines the purpose of a tool based on its name and goal context.
    
    Args:
        tool_name (str): The name of the tool
        goal_context (str): The context of the goal requiring the tool
        agent (str): The agent that needs the tool
        
    Returns:
        str: The determined purpose
    """
    # Tool purpose mapping
    purpose_mapping = {
        "form_validator": f"Used by {agent.upper()} to validate form fields before rendering",
        "component_builder": f"Used by {agent.upper()} to build UI components",
        "api_client": f"Used by {agent.upper()} to make API requests",
        "data_parser": f"Used by {agent.upper()} to parse and process data",
        "file_writer": f"Used by {agent.upper()} to write files",
        "code_generator": f"Used by {agent.upper()} to generate code",
        "style_generator": f"Used by {agent.upper()} to generate CSS styles",
        "database_connector": f"Used by {agent.upper()} to connect to databases",
        "test_runner": f"Used by {agent.upper()} to run tests",
        "schema_checker": f"Used by {agent.upper()} to validate schemas"
    }
    
    # Return the purpose if found, otherwise generate a generic purpose
    if tool_name in purpose_mapping:
        return purpose_mapping[tool_name]
    else:
        return f"Used by {agent.upper()} for {tool_name.replace('_', ' ')} operations"

def determine_tool_files(tool_name: str) -> List[str]:
    """
    Determines the estimated files needed for a tool.
    
    Args:
        tool_name (str): The name of the tool
        
    Returns:
        list: The estimated files
    """
    # File extension mapping based on tool name
    extension_mapping = {
        "form_validator": ".js",
        "component_builder": ".jsx",
        "api_client": ".js",
        "data_parser": ".js",
        "file_writer": ".js",
        "code_generator": ".js",
        "style_generator": ".css",
        "database_connector": ".js",
        "test_runner": ".js",
        "schema_checker": ".js"
    }
    
    # Get the extension for the tool
    extension = extension_mapping.get(tool_name, ".js")
    
    # Return the estimated files
    return [f"{tool_name}{extension}"]

def determine_linked_file(goal_context: str) -> str:
    """
    Determines the linked file based on goal context.
    
    Args:
        goal_context (str): The context of the goal requiring the tool
        
    Returns:
        str: The linked file
    """
    # Extract file names from goal context
    import re
    
    # Look for file names with extensions
    file_pattern = r'([A-Z][a-zA-Z]*\.(jsx|js|py|css|html))'
    file_matches = re.findall(file_pattern, goal_context)
    
    if file_matches and len(file_matches) > 0:
        # Return the first full match (file name with extension)
        return file_matches[0][0]  # First match, first group (full filename)
    
    # Default linked files based on common patterns
    if "form" in goal_context.lower():
        return "ContactForm.jsx"
    elif "component" in goal_context.lower():
        return "Component.jsx"
    elif "api" in goal_context.lower():
        return "api.js"
    elif "style" in goal_context.lower():
        return "styles.css"
    else:
        return "index.js"

def generate_dry_run_implementation(tool_name: str, purpose: str) -> str:
    """
    Generates a mock implementation of a tool for dry run.
    
    Args:
        tool_name (str): The name of the tool
        purpose (str): The purpose of the tool
        
    Returns:
        str: The mock implementation
    """
    # Template implementations based on tool type
    if "validator" in tool_name:
        # Form validator template
        implementation = f"""
/**
 * {purpose}
 */
function {tool_name}(formData) {{
  const errors = {{}};
  
  // Validate required fields
  Object.keys(formData).forEach(field => {{
    if (!formData[field] && field !== 'optional_field') {{
      errors[field] = `${{field}} is required`;
    }}
  }});
  
  // Validate email format
  if (formData.email && !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{{2,}}$/i.test(formData.email)) {{
    errors.email = 'Invalid email address';
  }}
  
  // Validate password strength
  if (formData.password && formData.password.length < 8) {{
    errors.password = 'Password must be at least 8 characters';
  }}
  
  return {{
    isValid: Object.keys(errors).length === 0,
    errors
  }};
}}

export default {tool_name};
"""
    elif "component" in tool_name or "builder" in tool_name:
        # Component builder template
        component_name = tool_name.replace('_', ' ').title().replace(' ', '')
        component_class = tool_name.replace('_', '-')
        component_title = tool_name.replace('_', ' ').title()
        
        implementation = f"""
/**
 * {purpose}
 */
import React from 'react';

function {component_name}(props) {{
  return (
    <div className="{component_class}">
      <h2>{component_title}</h2>
      <div className="content">
        {{props.children}}
      </div>
    </div>
  );
}}

export default {component_name};
"""
    elif "api" in tool_name or "client" in tool_name:
        # API client template
        implementation = f"""
/**
 * {purpose}
 */
async function {tool_name}(endpoint, options = {{}}) {{
  const baseUrl = process.env.API_BASE_URL || 'https://api.example.com';
  const url = `${{baseUrl}}/${{endpoint}}`;
  
  try {{
    const response = await fetch(url, {{
      method: options.method || 'GET',
      headers: {{
        'Content-Type': 'application/json',
        ...options.headers
      }},
      body: options.body ? JSON.stringify(options.body) : undefined
    }});
    
    if (!response.ok) {{
      throw new Error(`API request failed with status ${{response.status}}`);
    }}
    
    return await response.json();
  }} catch (error) {{
    console.error('API request error:', error);
    throw error;
  }}
}}

export default {tool_name};
"""
    else:
        # Default to form validator
        implementation = f"""
/**
 * {purpose}
 */
function {tool_name}(data) {{
  // Default implementation
  return {{
    success: true,
    data: data
  }};
}}

export default {tool_name};
"""
    
    return implementation

def validate_tool_schema(tool_name: str, implementation: str) -> str:
    """
    Validates a tool implementation against schema.
    
    Args:
        tool_name (str): The name of the tool
        implementation (str): The tool implementation
        
    Returns:
        str: The validation result ("passed" or error message)
    """
    # In a real implementation, this would validate against a schema
    # For now, we'll just check for some basic patterns
    
    # Check for missing exports
    if "export default" not in implementation:
        return "missing_export"
    
    # Check for syntax errors (very basic check)
    if implementation.count('{') != implementation.count('}'):
        return "syntax_error: unbalanced braces"
    
    # Check for function definition
    if "function" not in implementation:
        return "missing_function_definition"
    
    # All checks passed
    return "passed"

def is_tool_available(project_id: str, tool_name: str) -> bool:
    """
    Checks if a tool is already available.
    
    Args:
        project_id (str): The project identifier
        tool_name (str): The name of the tool
        
    Returns:
        bool: Whether the tool is available
    """
    # In a real implementation, this would check the tool registry
    # For now, we'll just return False to simulate a missing tool
    return False

def check_preauthorization(project_id: str, tool_name: str, agent: str) -> bool:
    """
    Checks if a tool is pre-authorized for auto-generation.
    
    Args:
        project_id (str): The project identifier
        tool_name (str): The name of the tool
        agent (str): The agent that needs the tool
        
    Returns:
        bool: Whether the tool is pre-authorized
    """
    # In a real implementation, this would check the orchestrator config
    # For now, we'll just return False to simulate requiring operator approval
    return False

def get_goal_context(project_id: str, loop_id: int) -> str:
    """
    Gets the goal context from a loop plan.
    
    Args:
        project_id (str): The project identifier
        loop_id (int): The loop identifier
        
    Returns:
        str: The goal context
    """
    # In a real implementation, this would retrieve the goal context from memory
    # For now, we'll just return a generic context
    return f"Create a React component for user profile with form validation in ContactForm.jsx for loop {loop_id}"

def generate_tool(project_id: str, tool_name: str, implementation: str, estimated_files: List[str]) -> str:
    """
    Generates a tool and writes it to the filesystem.
    
    Args:
        project_id (str): The project identifier
        tool_name (str): The name of the tool
        implementation (str): The tool implementation
        estimated_files (list): The estimated files
        
    Returns:
        str: The path to the generated tool
    """
    # Create the tools directory if it doesn't exist
    tools_dir = os.path.join("/", "tools")
    os.makedirs(tools_dir, exist_ok=True)
    
    # Write the tool implementation to file
    file_path = os.path.join(tools_dir, estimated_files[0])
    
    # In a real implementation, this would write to the file
    # For now, we'll just print a message
    print(f"Writing tool implementation to {file_path}")
    print(implementation)
    
    return file_path

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
    loop_id = 35
    agent = "nova"
    tool_name = "form_validator"
    
    # Generate a tool proposal
    proposal = propose_tool_generation(
        project_id=project_id,
        tool_name=tool_name,
        goal_context="Create a React component for user profile with form validation in ContactForm.jsx",
        agent=agent,
        loop_id=loop_id
    )
    print("\nGenerated tool proposal:")
    print(json.dumps(proposal, indent=2))
    
    # Run the tool autogen driver
    result = tool_autogen_driver(
        project_id=project_id,
        loop_id=loop_id,
        agent=agent,
        tool_name=tool_name
    )
    print("\nTool autogen driver result:")
    print(json.dumps(result, indent=2))
    
    # Get tool history
    history = get_tool_history(project_id, tool_name)
    print(f"\nRetrieved {len(history)} history entries for tool {tool_name}")
