"""
Reflection Logging Logic

This module implements the reflection logging functionality for tools that require reflection.
"""

import datetime
import json
import os
from typing import Dict, Any, List, Optional

# Create a directory for storing reflections if it doesn't exist
os.makedirs('/home/ubuntu/workspace/personal-ai-agent/toolkit/reflections', exist_ok=True)

def write_reflection(tool_name: str, result: Any, goal_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Write a reflection memory after successful tool execution.
    
    Args:
        tool_name: Name of the tool that was executed
        result: Result returned by the tool
        goal_id: Optional identifier for the current goal or task
        
    Returns:
        A dictionary containing the reflection memory
    """
    # Generate a timestamp for the reflection
    timestamp = datetime.datetime.now().isoformat()
    
    # Generate a unique ID for the reflection
    reflection_id = f"reflection_{int(datetime.datetime.now().timestamp())}_{tool_name.replace('.', '_')}"
    
    # Create the reflection memory structure
    reflection = {
        "id": reflection_id,
        "timestamp": timestamp,
        "tool": tool_name,
        "goal_id": goal_id or "unknown_goal",
        "tags": ["reflection", f"tool:{tool_name}"],
        "content": generate_reflection_content(tool_name, result)
    }
    
    # If goal_id is provided, add it as a tag
    if goal_id:
        reflection["tags"].append(f"goal_id:{goal_id}")
    
    # Save the reflection to a file
    save_reflection(reflection)
    
    return reflection


def generate_reflection_content(tool_name: str, result: Any) -> Dict[str, str]:
    """
    Generate reflection content based on the tool and its result.
    
    Args:
        tool_name: Name of the tool that was executed
        result: Result returned by the tool
        
    Returns:
        A dictionary containing the reflection content
    """
    # Initialize basic reflection content
    content = {
        "summary": f"Reflection on using {tool_name}",
        "learning": "",
        "effectiveness": "",
        "future_applications": ""
    }
    
    # Generate tool-specific reflection content
    if tool_name == "agent.self.check":
        content["summary"] = "Reflection on agent self-diagnostic check"
        content["learning"] = f"The agent's health score is {result.get('health_score', 'unknown')}. " + \
                             f"Current status: {result.get('agent_status', 'unknown')}."
        
        if result.get("errors", {}).get("recent_count", 0) > 0:
            content["effectiveness"] = "The self-check identified errors that need to be addressed to improve agent performance."
        else:
            content["effectiveness"] = "The self-check confirmed the agent is operating normally."
        
        content["future_applications"] = "Regular self-checks should be performed to monitor agent health and address issues proactively."
    
    elif tool_name == "guardian.escalate":
        content["summary"] = f"Reflection on escalating a {result.get('issue_type', 'unknown')} issue"
        content["learning"] = f"A {result.get('severity', 'unknown')} severity issue was escalated: {result.get('reflection', {}).get('summary', 'unknown issue')}."
        content["effectiveness"] = "The escalation process helped identify and address a potential issue before it became critical."
        content["future_applications"] = "Similar issues should be monitored and escalated appropriately in the future."
    
    elif tool_name == "task.finish.check":
        completion_status = result.get("completion_status", "unknown")
        content["summary"] = f"Reflection on task completion check (Status: {completion_status})"
        
        if completion_status == "complete":
            content["learning"] = "All checkpoints for the task have been completed successfully."
        else:
            missing_count = len(result.get("missing_checkpoints", []))
            content["learning"] = f"The task is {result.get('completion_percentage', 0)}% complete with {missing_count} checkpoints remaining."
        
        content["effectiveness"] = "The completion check provided clear visibility into task progress and remaining work."
        content["future_applications"] = "Regular completion checks should be performed throughout task execution to ensure all requirements are met."
    
    elif tool_name == "agent.escalate.reason":
        content["summary"] = f"Reflection on task escalation (Status: {result.get('status', 'unknown')})"
        content["learning"] = f"Task {result.get('task_id', 'unknown')} was escalated due to: {result.get('reason', {}).get('summary', 'unknown reason')}."
        content["effectiveness"] = "The escalation provided clear documentation of the issue and recommended actions."
        content["future_applications"] = "Similar situations should be handled with appropriate escalation to ensure timely resolution."
    
    elif tool_name == "pricing.generate":
        content["summary"] = "Reflection on generating pricing tiers"
        content["learning"] = f"Generated {len(result.get('tiers', []))} pricing tiers for {result.get('product_name', 'the product')}."
        content["effectiveness"] = f"The recommended tier to highlight is {result.get('recommendations', {}).get('highlight_tier', 'unknown')}."
        content["future_applications"] = "Pricing should be regularly reviewed and adjusted based on market conditions and customer feedback."
    
    elif tool_name == "payment.init":
        content["summary"] = "Reflection on payment configuration setup"
        content["learning"] = f"Configured payment for {result.get('product', {}).get('name', 'the product')} with {len(result.get('payment_methods', []))} payment methods."
        content["effectiveness"] = "The payment configuration includes both frontend and backend implementation code for easy integration."
        content["future_applications"] = "Payment configurations should be tested thoroughly in sandbox environments before production deployment."
    
    elif tool_name == "copy.email.campaign":
        content["summary"] = "Reflection on email campaign creation"
        content["learning"] = f"Created a {result.get('name', 'email campaign')} with {len(result.get('emails', []))} emails."
        content["effectiveness"] = f"The campaign targets {result.get('audience', 'unknown')} audience with estimated open rate of {result.get('metrics', {}).get('estimated_open_rate', 'unknown')}."
        content["future_applications"] = "Email campaigns should be A/B tested and refined based on performance metrics."
    
    elif tool_name == "content.blog.generate":
        content["summary"] = "Reflection on blog content generation"
        content["learning"] = f"Generated a {result.get('actual_word_count', 0)}-word blog post titled '{result.get('title', 'unknown')}'."
        content["effectiveness"] = f"The content has an estimated reading time of {result.get('reading_time', 'unknown')} and covers key aspects of the topic."
        content["future_applications"] = "Blog content should be enhanced with relevant images and formatted for readability."
    
    elif tool_name == "landing.hero.write":
        content["summary"] = "Reflection on landing page hero content creation"
        content["learning"] = f"Created hero content for {result.get('product_name', 'the product')} targeting {result.get('target_audience', 'unknown')} audience."
        content["effectiveness"] = "The hero content includes a compelling headline, subheader, and call-to-action with testing alternatives."
        content["future_applications"] = "Landing page elements should be A/B tested to optimize conversion rates."
    
    else:
        # Generic reflection for other tools
        content["summary"] = f"Reflection on using {tool_name}"
        content["learning"] = f"The tool was used successfully and returned a result of type {type(result).__name__}."
        content["effectiveness"] = "The tool provided the expected functionality and results."
        content["future_applications"] = "This tool should be considered for similar tasks in the future."
    
    return content


def save_reflection(reflection: Dict[str, Any]) -> None:
    """
    Save a reflection to a file.
    
    Args:
        reflection: The reflection memory to save
    """
    # Create a filename based on the reflection ID
    filename = f"/home/ubuntu/workspace/personal-ai-agent/toolkit/reflections/{reflection['id']}.json"
    
    # Write the reflection to the file
    with open(filename, 'w') as f:
        json.dump(reflection, f, indent=2)


def get_reflections(tool_name: Optional[str] = None, goal_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve stored reflections, optionally filtered by tool name or goal ID.
    
    Args:
        tool_name: Optional tool name to filter by
        goal_id: Optional goal ID to filter by
        limit: Maximum number of reflections to return
        
    Returns:
        A list of reflection memories
    """
    reflections = []
    reflections_dir = '/home/ubuntu/workspace/personal-ai-agent/toolkit/reflections'
    
    # Ensure the directory exists
    if not os.path.exists(reflections_dir):
        return reflections
    
    # List all reflection files
    reflection_files = [f for f in os.listdir(reflections_dir) if f.endswith('.json')]
    
    # Sort by creation time (newest first)
    reflection_files.sort(key=lambda f: os.path.getctime(os.path.join(reflections_dir, f)), reverse=True)
    
    # Load and filter reflections
    for filename in reflection_files[:limit * 2]:  # Load more than needed to account for filtering
        file_path = os.path.join(reflections_dir, filename)
        try:
            with open(file_path, 'r') as f:
                reflection = json.load(f)
                
                # Apply filters
                if tool_name and reflection.get('tool') != tool_name:
                    continue
                
                if goal_id and reflection.get('goal_id') != goal_id:
                    continue
                
                reflections.append(reflection)
                
                # Stop if we have enough reflections
                if len(reflections) >= limit:
                    break
                    
        except Exception as e:
            print(f"Error loading reflection from {file_path}: {e}")
    
    return reflections


# Function to be called after successful tool execution
def process_tool_reflection(tool_name: str, result: Any, requires_reflection: bool, goal_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Process tool reflection after successful execution.
    
    Args:
        tool_name: Name of the tool that was executed
        result: Result returned by the tool
        requires_reflection: Whether the tool requires reflection
        goal_id: Optional identifier for the current goal or task
        
    Returns:
        A reflection memory if the tool requires reflection, None otherwise
    """
    if requires_reflection:
        return write_reflection(tool_name, result, goal_id)
    return None
