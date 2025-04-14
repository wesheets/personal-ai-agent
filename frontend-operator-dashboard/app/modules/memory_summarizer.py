"""
Memory summarization module for generating natural language summaries of agent memories.

This module provides functionality to summarize a list of memory entries into
a coherent natural language summary, either using simple concatenation or
more advanced AI-powered summarization.
"""

from typing import List, Dict, Optional
import logging

# Configure logging
logger = logging.getLogger("memory_summarizer")

def summarize_memories(memories: List[Dict]) -> str:
    """
    Generate a natural language summary of a list of memory entries.
    
    This is a simple implementation that concatenates memory content.
    In a production environment, this could be replaced with an AI-powered
    summarization using OpenAI or similar services.
    
    Args:
        memories: List of memory dictionaries to summarize
        
    Returns:
        A natural language summary of the memories
    """
    if not memories:
        return "No relevant memories to summarize."
    
    # Extract memory contents
    memory_contents = [memory.get("content", "") for memory in memories]
    
    # For now, implement a simple concatenation approach
    # This could be replaced with OpenAI summarization in the future
    
    # Get memory types and tags for context
    memory_types = set(memory.get("type", "") for memory in memories)
    all_tags = []
    for memory in memories:
        all_tags.extend(memory.get("tags", []))
    unique_tags = set(all_tags)
    
    # Create a simple summary
    agent_id = memories[0].get("agent_id", "unknown")
    
    summary = f"{agent_id.upper()} focused on "
    
    # Add topics from tags
    if unique_tags:
        topics = list(unique_tags)
        if len(topics) == 1:
            summary += f"{topics[0]}"
        elif len(topics) == 2:
            summary += f"{topics[0]} and {topics[1]}"
        else:
            summary += ", ".join(topics[:-1]) + f", and {topics[-1]}"
    else:
        # If no tags, use the first few words of each memory
        topics = []
        for content in memory_contents:
            words = content.split()
            if words:
                topics.append(" ".join(words[:3]) + "...")
        
        if topics:
            if len(topics) == 1:
                summary += f"{topics[0]}"
            elif len(topics) == 2:
                summary += f"{topics[0]} and {topics[1]}"
            else:
                summary += ", ".join(topics[:-1]) + f", and {topics[-1]}"
        else:
            summary += "various topics"
    
    summary += "."
    
    return summary

async def summarize_memories_with_ai(memories: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    """
    Generate an AI-powered summary of a list of memory entries.
    
    This is a placeholder for future implementation using OpenAI or similar services.
    
    Args:
        memories: List of memory dictionaries to summarize
        model: AI model to use for summarization
        
    Returns:
        An AI-generated summary of the memories
    """
    # This is a placeholder for future implementation
    # In a real implementation, this would call OpenAI or similar services
    
    try:
        # Import here to avoid circular imports
        from app.providers import process_with_model
        
        # Extract memory contents
        memory_contents = [memory.get("content", "") for memory in memories]
        combined_content = "\n\n".join(memory_contents)
        
        # Create prompt for summarization
        prompt_chain = {
            "system": "You are a memory summarization system. Your task is to create a concise, coherent summary of the following memory entries.",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        user_input = f"""
Please summarize the following memory entries into a single coherent sentence:

{combined_content}

Keep the summary concise and focus on the main themes or topics.
"""
        
        # Process with model
        result = await process_with_model(
            model=model,
            prompt_chain=prompt_chain,
            user_input=user_input
        )
        
        # Extract summary from result
        summary = result.get("content", "")
        
        return summary.strip()
    except Exception as e:
        logger.error(f"Error generating AI summary: {str(e)}")
        # Fall back to simple summarization
        return summarize_memories(memories)
