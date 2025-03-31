"""
Agent Builder Tool for the Personal AI Agent System.

This module provides functionality to dynamically create and configure
specialized AI agents for specific tasks.
"""

import os
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger("agent_builder")

def run(
    agent_name: str,
    agent_purpose: str,
    agent_capabilities: List[str] = None,
    agent_constraints: List[str] = None,
    agent_tools: List[str] = None,
    agent_personality: str = None,
    agent_knowledge_areas: List[str] = None,
    agent_model: str = "gpt-4",
    agent_memory_enabled: bool = True,
    agent_reflection_enabled: bool = True,
    agent_template: str = None,
    save_agent: bool = True,
    test_agent: bool = False,
    test_prompt: str = None,
    store_memory: bool = True,
    memory_manager = None,
    memory_tags: List[str] = ["agent_builder", "meta"],
    memory_scope: str = "global"
) -> Dict[str, Any]:
    """
    Build a specialized AI agent for a specific task.
    
    Args:
        agent_name: Name of the agent to create
        agent_purpose: Primary purpose/role of the agent
        agent_capabilities: List of capabilities the agent should have
        agent_constraints: List of constraints the agent should operate under
        agent_tools: List of tools the agent should have access to
        agent_personality: Personality traits for the agent
        agent_knowledge_areas: Specific knowledge areas the agent should specialize in
        agent_model: LLM model to use for the agent
        agent_memory_enabled: Whether the agent should have memory capabilities
        agent_reflection_enabled: Whether the agent should have reflection capabilities
        agent_template: Optional template to base the agent on
        save_agent: Whether to save the agent configuration
        test_agent: Whether to test the agent with a sample prompt
        test_prompt: Test prompt to use if testing the agent
        store_memory: Whether to store the agent configuration in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing the agent configuration and metadata
    """
    logger.info(f"Building agent: {agent_name} for purpose: {agent_purpose}")
    
    try:
        # Validate inputs
        if not agent_name:
            raise ValueError("Agent name is required")
        
        if not agent_purpose:
            raise ValueError("Agent purpose is required")
        
        # Set defaults for optional parameters
        agent_capabilities = agent_capabilities or []
        agent_constraints = agent_constraints or []
        agent_tools = agent_tools or []
        agent_knowledge_areas = agent_knowledge_areas or []
        
        # Normalize agent name for file naming
        normalized_name = agent_name.lower().replace(" ", "_")
        
        # Load template if specified
        template_config = {}
        if agent_template:
            template_config = _load_agent_template(agent_template)
        
        # Build agent configuration
        agent_config = _build_agent_config(
            agent_name,
            agent_purpose,
            agent_capabilities,
            agent_constraints,
            agent_tools,
            agent_personality,
            agent_knowledge_areas,
            agent_model,
            agent_memory_enabled,
            agent_reflection_enabled,
            template_config
        )
        
        # Generate agent prompt
        agent_prompt = _generate_agent_prompt(agent_config)
        
        # Save agent configuration if requested
        config_path = None
        if save_agent:
            config_path = _save_agent_config(normalized_name, agent_config, agent_prompt)
        
        # Test agent if requested
        test_results = None
        if test_agent:
            test_results = _test_agent(
                normalized_name,
                agent_config,
                agent_prompt,
                test_prompt or f"Explain your purpose as {agent_name}"
            )
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the agent configuration
                memory_entry = {
                    "type": "agent_configuration",
                    "agent_name": agent_name,
                    "agent_purpose": agent_purpose,
                    "agent_model": agent_model,
                    "agent_tools": agent_tools,
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + ["agent_config", normalized_name]
                )
                
                logger.info(f"Stored agent configuration in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store agent configuration in memory: {str(e)}")
        
        # Prepare response
        response = {
            "success": True,
            "agent_name": agent_name,
            "normalized_name": normalized_name,
            "agent_purpose": agent_purpose,
            "agent_config": agent_config,
            "agent_prompt": agent_prompt
        }
        
        if config_path:
            response["config_path"] = config_path
        
        if test_results:
            response["test_results"] = test_results
        
        return response
    except Exception as e:
        error_msg = f"Error building agent: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "agent_name": agent_name
        }

def _load_agent_template(template_name: str) -> Dict[str, Any]:
    """
    Load an agent template configuration.
    
    Args:
        template_name: Name of the template to load
        
    Returns:
        Template configuration
    """
    # In a real implementation, this would load from a templates directory
    # For this example, we'll use predefined templates
    
    templates = {
        "researcher": {
            "capabilities": [
                "Conduct comprehensive research on any topic",
                "Synthesize information from multiple sources",
                "Identify gaps in information and suggest further research",
                "Evaluate source credibility and potential biases",
                "Organize findings in a structured format"
            ],
            "constraints": [
                "Must cite all sources used",
                "Must indicate confidence level in findings",
                "Must highlight contradictory information",
                "Must not make definitive claims without evidence"
            ],
            "tools": [
                "web_search",
                "url_summarizer",
                "pdf_ingest",
                "news_fetcher"
            ],
            "personality": "Thorough, analytical, and objective",
            "knowledge_areas": [
                "Research methodologies",
                "Information evaluation",
                "Academic writing"
            ]
        },
        "coder": {
            "capabilities": [
                "Write clean, efficient code in multiple languages",
                "Debug and fix code issues",
                "Explain code functionality and design patterns",
                "Optimize code for performance",
                "Implement best practices and coding standards"
            ],
            "constraints": [
                "Must include comments in code",
                "Must handle edge cases and errors",
                "Must follow language-specific conventions",
                "Must consider security implications"
            ],
            "tools": [
                "code_executor",
                "github_commit",
                "code_explainer"
            ],
            "personality": "Precise, systematic, and solution-oriented",
            "knowledge_areas": [
                "Software development",
                "Programming languages",
                "Algorithms and data structures",
                "Software architecture"
            ]
        },
        "writer": {
            "capabilities": [
                "Create engaging content in various formats",
                "Adapt writing style to different audiences",
                "Edit and improve existing content",
                "Structure content for clarity and impact",
                "Generate creative ideas and narratives"
            ],
            "constraints": [
                "Must maintain consistent tone and style",
                "Must avoid plagiarism",
                "Must adhere to grammar and punctuation rules",
                "Must consider readability and accessibility"
            ],
            "tools": [
                "notion_writer",
                "tone_converter",
                "pitch_optimizer"
            ],
            "personality": "Creative, articulate, and adaptable",
            "knowledge_areas": [
                "Content creation",
                "Storytelling",
                "Editing and proofreading",
                "Audience engagement"
            ]
        },
        "analyst": {
            "capabilities": [
                "Analyze data and identify patterns",
                "Generate insights from complex information",
                "Create visualizations and reports",
                "Make data-driven recommendations",
                "Evaluate scenarios and predict outcomes"
            ],
            "constraints": [
                "Must base conclusions on data",
                "Must acknowledge limitations of analysis",
                "Must consider alternative interpretations",
                "Must present balanced viewpoints"
            ],
            "tools": [
                "spreadsheet_analyzer",
                "api_request",
                "code_executor"
            ],
            "personality": "Methodical, detail-oriented, and insightful",
            "knowledge_areas": [
                "Data analysis",
                "Statistics",
                "Business intelligence",
                "Trend forecasting"
            ]
        }
    }
    
    # Return template if it exists, otherwise empty dict
    return templates.get(template_name.lower(), {})

def _build_agent_config(
    agent_name: str,
    agent_purpose: str,
    agent_capabilities: List[str],
    agent_constraints: List[str],
    agent_tools: List[str],
    agent_personality: str,
    agent_knowledge_areas: List[str],
    agent_model: str,
    agent_memory_enabled: bool,
    agent_reflection_enabled: bool,
    template_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Build the agent configuration.
    
    Args:
        agent_name: Name of the agent
        agent_purpose: Primary purpose/role of the agent
        agent_capabilities: List of capabilities the agent should have
        agent_constraints: List of constraints the agent should operate under
        agent_tools: List of tools the agent should have access to
        agent_personality: Personality traits for the agent
        agent_knowledge_areas: Specific knowledge areas the agent should specialize in
        agent_model: LLM model to use for the agent
        agent_memory_enabled: Whether the agent should have memory capabilities
        agent_reflection_enabled: Whether the agent should have reflection capabilities
        template_config: Template configuration to base the agent on
        
    Returns:
        Agent configuration
    """
    # Merge template values with provided values
    merged_capabilities = list(set(template_config.get("capabilities", []) + agent_capabilities))
    merged_constraints = list(set(template_config.get("constraints", []) + agent_constraints))
    merged_tools = list(set(template_config.get("tools", []) + agent_tools))
    merged_knowledge_areas = list(set(template_config.get("knowledge_areas", []) + agent_knowledge_areas))
    
    # Use provided personality or template personality or generate default
    personality = agent_personality or template_config.get("personality", "Helpful, accurate, and efficient")
    
    # Build configuration
    config = {
        "name": agent_name,
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "model": agent_model,
        "purpose": agent_purpose,
        "capabilities": merged_capabilities,
        "constraints": merged_constraints,
        "tools": merged_tools,
        "personality": personality,
        "knowledge_areas": merged_knowledge_areas,
        "memory_enabled": agent_memory_enabled,
        "reflection_enabled": agent_reflection_enabled,
        "metadata": {
            "template_used": bool(template_config),
            "template_name": next((k for k, v in _load_agent_template("").items() if v == template_config), None)
        }
    }
    
    return config

def _generate_agent_prompt(agent_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate the agent prompt from the configuration.
    
    Args:
        agent_config: Agent configuration
        
    Returns:
        Agent prompt structure
    """
    # In a real implementation, this would generate a structured prompt
    # For this example, we'll create a simple prompt structure
    
    # Build system message
    system_message = f"You are {agent_config['name']}, an AI assistant specialized in {agent_config['purpose']}.\n\n"
    
    # Add capabilities
    if agent_config["capabilities"]:
        system_message += "Your capabilities include:\n"
        for capability in agent_config["capabilities"]:
            system_message += f"- {capability}\n"
        system_message += "\n"
    
    # Add constraints
    if agent_config["constraints"]:
        system_message += "You must adhere to these constraints:\n"
        for constraint in agent_config["constraints"]:
            system_message += f"- {constraint}\n"
        system_message += "\n"
    
    # Add personality
    system_message += f"Your personality is: {agent_config['personality']}\n\n"
    
    # Add knowledge areas
    if agent_config["knowledge_areas"]:
        system_message += "You have specialized knowledge in:\n"
        for area in agent_config["knowledge_areas"]:
            system_message += f"- {area}\n"
        system_message += "\n"
    
    # Add tools information
    if agent_config["tools"]:
        system_message += "You have access to these tools:\n"
        for tool in agent_config["tools"]:
            system_message += f"- {tool}\n"
        system_message += "\n"
    
    # Add memory and reflection information
    if agent_config["memory_enabled"]:
        system_message += "You have memory capabilities and can recall past interactions.\n"
    
    if agent_config["reflection_enabled"]:
        system_message += "You can reflect on your responses to improve over time.\n"
    
    # Build prompt structure
    prompt = {
        "system_message": system_message,
        "examples": _generate_example_conversations(agent_config),
        "input_format": "The user will provide requests related to your purpose as {agent_name}.",
        "output_format": "Respond in a way that aligns with your purpose, capabilities, and constraints."
    }
    
    return prompt

def _generate_example_conversations(agent_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate example conversations for the agent.
    
    Args:
        agent_config: Agent configuration
        
    Returns:
        List of example conversations
    """
    # In a real implementation, this would generate contextual examples
    # For this example, we'll use generic examples
    
    examples = [
        {
            "user": f"Can you help me with {agent_config['purpose']}?",
            "assistant": f"I'd be happy to help you with {agent_config['purpose']}. As {agent_config['name']}, I specialize in this area. What specific assistance do you need?"
        },
        {
            "user": "What can you do?",
            "assistant": f"As {agent_config['name']}, I can assist you with {agent_config['purpose']}. " + 
                        f"My capabilities include {', '.join(agent_config['capabilities'][:2])} and more. " +
                        "How can I help you today?"
        }
    ]
    
    return examples

def _save_agent_config(
    normalized_name: str,
    agent_config: Dict[str, Any],
    agent_prompt: Dict[str, Any]
) -> str:
    """
    Save the agent configuration to a file.
    
    Args:
        normalized_name: Normalized agent name for file naming
        agent_config: Agent configuration
        agent_prompt: Agent prompt structure
        
    Returns:
        Path to the saved configuration file
    """
    # In a real implementation, this would save to the appropriate directory
    # For this example, we'll simulate saving
    
    # Create directory if it doesn't exist
    prompts_dir = os.path.join("app", "prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    
    # Build configuration with prompt
    full_config = {
        "config": agent_config,
        "prompt": agent_prompt
    }
    
    # Save to file
    config_path = os.path.join(prompts_dir, f"{normalized_name}.json")
    
    try:
        with open(config_path, "w") as f:
            json.dump(full_config, f, indent=2)
        
        logger.info(f"Saved agent configuration to {config_path}")
        return config_path
    except Exception as e:
        logger.error(f"Failed to save agent configuration: {str(e)}")
        return None

def _test_agent(
    normalized_name: str,
    agent_config: Dict[str, Any],
    agent_prompt: Dict[str, Any],
    test_prompt: str
) -> Dict[str, Any]:
    """
    Test the agent with a sample prompt.
    
    Args:
        normalized_name: Normalized agent name
        agent_config: Agent configuration
        agent_prompt: Agent prompt structure
        test_prompt: Test prompt to use
        
    Returns:
        Test results
    """
    # In a real implementation, this would call the agent with the test prompt
    # For this example, we'll simulate a response
    
    logger.info(f"Testing agent {normalized_name} with prompt: {test_prompt}")
    
    # Simulate thinking time
    time.sleep(1)
    
    # Generate simulated response
    response = f"As {agent_config['name']}, I'm designed to help with {agent_config['purpose']}. "
    response += f"In response to your query: {test_prompt}\n\n"
    response += "Here's how I can assist you based on my capabilities:\n"
    
    # Add capability-based responses
    for i, capability in enumerate(agent_config["capabilities"][:3]):
        response += f"{i+1}. {capability}: I can provide specific assistance in this area.\n"
    
    response += f"\nIs there a specific aspect of {agent_config['purpose']} you'd like me to help with?"
    
    # Simulate tool usage if applicable
    tools_used = []
    if agent_config["tools"] and len(agent_config["tools"]) > 0:
        # Randomly select 1-2 tools to simulate using
        import random
        num_tools = min(2, len(agent_config["tools"]))
        selected_tools = random.sample(agent_config["tools"], num_tools)
        tools_used = selected_tools
    
    return {
        "prompt": test_prompt,
        "response": response,
        "tools_used": tools_used,
        "execution_time_ms": 1200,  # Simulated execution time
        "model_used": agent_config["model"],
        "test_timestamp": datetime.now().isoformat()
    }
