from app.providers.openai_provider import OpenAIProvider
import logging

logger = logging.getLogger("agents")

# Initialize OpenAI provider
try:
    openai_provider = OpenAIProvider()
    logger.info("✅ OpenAI provider initialized successfully for LifeTree agent")
except Exception as e:
    logger.error(f"❌ Failed to initialize OpenAI provider for LifeTree agent: {str(e)}")
    openai_provider = None

async def handle_lifetree_task(task_input):
    try:
        if not openai_provider:
            return f"🌱 LifeTree Agent Error: OpenAI provider not initialized. Falling back to static response for: '{task_input}'."
        
        # Create a prompt chain with LifeTree's specific tone and domain
        prompt_chain = {
            "system": "You are LifeTree, an AI agent specialized in creating legacy structures, emotional prompts, and memory chain scaffolds. You speak with a nurturing, empathetic tone and focus on preserving memories and emotional connections.",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Process the task through OpenAI
        response = await openai_provider.process_with_prompt_chain(
            prompt_chain=prompt_chain,
            user_input=task_input
        )
        
        return f"🌱 {response['content']}"
    except Exception as e:
        logger.error(f"Error in LifeTree agent: {str(e)}")
        return f"🌱 LifeTree Agent Error: {str(e)}. Falling back to static response for: '{task_input}'."

# Synchronous wrapper for backward compatibility
def handle_lifetree_task_sync(task_input):
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(handle_lifetree_task(task_input))
    return result

# For backward compatibility with existing code
def handle_lifetree_task(task_input):
    return handle_lifetree_task_sync(task_input)
