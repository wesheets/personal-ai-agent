from app.providers.openai_provider import OpenAIProvider
import logging

logger = logging.getLogger("agents")

# Initialize OpenAI provider
try:
    openai_provider = OpenAIProvider()
    logger.info("✅ OpenAI provider initialized successfully for SiteGen agent")
except Exception as e:
    logger.error(f"❌ Failed to initialize OpenAI provider for SiteGen agent: {str(e)}")
    openai_provider = None

async def handle_sitegen_task(task_input):
    try:
        if not openai_provider:
            return f"🏗️ SiteGen Agent Error: OpenAI provider not initialized. Falling back to static response for: '{task_input}'."
        
        # Create a prompt chain with SiteGen's specific tone and domain
        prompt_chain = {
            "system": "You are SiteGen, an intelligent system for planning commercial sites. You analyze zoning requirements, create optimal layouts, and evaluate market-fit for construction projects. You speak with a professional, analytical tone and focus on practical solutions.",
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Process the task through OpenAI
        response = await openai_provider.process_with_prompt_chain(
            prompt_chain=prompt_chain,
            user_input=task_input
        )
        
        return f"🏗️ {response['content']}"
    except Exception as e:
        logger.error(f"Error in SiteGen agent: {str(e)}")
        return f"🏗️ SiteGen Agent Error: {str(e)}. Falling back to static response for: '{task_input}'."

# Synchronous wrapper for backward compatibility
def handle_sitegen_task_sync(task_input):
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    result = loop.run_until_complete(handle_sitegen_task(task_input))
    return result

# For backward compatibility with existing code
def handle_sitegen_task(task_input):
    return handle_sitegen_task_sync(task_input)
