from typing import Dict, Any, List, Optional
from app.providers import process_with_model
from app.core.shared_memory import get_shared_memory

class MemoryContextReviewer:
    """
    Handles memory context review to help agents connect past memories to current tasks
    """
    
    def __init__(self):
        self.shared_memory = get_shared_memory()
    
    async def retrieve_and_analyze_memories(
        self,
        model: str,
        agent_type: str,
        input_text: str,
        limit: int = 5,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant memories and analyze their connection to the current task
        
        Args:
            model: Model to use for analysis
            agent_type: Type of agent
            input_text: User input text (current task)
            limit: Maximum number of memories to retrieve
            context: Additional context
            
        Returns:
            Dictionary containing memories and analysis
        """
        # Retrieve relevant memories from both agent-specific and global scopes
        agent_memories = await self.shared_memory.search_memories(
            query=input_text,
            limit=limit,
            scope="agent",
            agent_name=agent_type
        )
        
        global_memories = await self.shared_memory.search_memories(
            query=input_text,
            limit=limit,
            scope="global"
        )
        
        # Combine and deduplicate memories
        memory_ids = set()
        combined_memories = []
        
        for memory in agent_memories + global_memories:
            if memory["id"] not in memory_ids:
                memory_ids.add(memory["id"])
                combined_memories.append(memory)
        
        # Sort by similarity
        combined_memories.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        combined_memories = combined_memories[:limit]
        
        # If no memories found, return empty result
        if not combined_memories:
            return {
                "memories": [],
                "memory_context": "",
                "analysis": "No relevant memories found."
            }
        
        # Format memories as context
        memory_context = await self.shared_memory.format_memories_as_context(combined_memories)
        
        # Generate analysis of how memories connect to the current task
        analysis = await self._analyze_memory_connections(
            model=model,
            agent_type=agent_type,
            input_text=input_text,
            memory_context=memory_context,
            context=context
        )
        
        return {
            "memories": combined_memories,
            "memory_context": memory_context,
            "analysis": analysis
        }
    
    async def _analyze_memory_connections(
        self,
        model: str,
        agent_type: str,
        input_text: str,
        memory_context: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Analyze how memories connect to the current task
        
        Args:
            model: Model to use for analysis
            agent_type: Type of agent
            input_text: User input text (current task)
            memory_context: Formatted memory context
            context: Additional context
            
        Returns:
            Analysis of memory connections
        """
        # Create prompt for memory analysis
        prompt_chain = {
            "system": f"You are a memory analysis system for a {agent_type} agent. Your task is to analyze how previous memories relate to the current task and identify connections that might be helpful.",
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        user_input = f"""
I need you to analyze how the following previous memories relate to the current task.

CURRENT TASK:
{input_text}

PREVIOUS MEMORIES:
{memory_context}

Please answer the following question:
How do these previous memories connect to the current task? Identify specific patterns, relevant information, or insights that could be helpful.

Provide a concise analysis focusing on the most relevant connections.
"""
        
        # Process with model
        result = await process_with_model(
            model=model,
            prompt_chain=prompt_chain,
            user_input=user_input,
            context=context
        )
        
        return result.get("content", "")

# Singleton instance
_memory_context_reviewer = None

def get_memory_context_reviewer() -> MemoryContextReviewer:
    """
    Get the singleton MemoryContextReviewer instance
    """
    global _memory_context_reviewer
    if _memory_context_reviewer is None:
        _memory_context_reviewer = MemoryContextReviewer()
    return _memory_context_reviewer
