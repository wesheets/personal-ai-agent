"""
OpenAI code generation module for HAL agent.
This module provides functions to generate React/JSX code using OpenAI's API,
specifically designed for use with the HAL agent's code generation capabilities.

Enhanced with retry handler and error classification for improved resilience.
"""
import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("hal_openai")

# Import retry handler and error classifier
try:
    from app.utils.retry_handler import retry_with_backoff
    from app.utils.error_classification import classify_error, log_error_to_memory
    hardening_available = True
    logger.info("✅ Hardening utilities loaded successfully")
except ImportError as e:
    hardening_available = False
    logger.warning(f"⚠️ Hardening utilities not available, falling back to basic error handling: {str(e)}")

# Safely import OpenAI
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logger.info("✅ Using OpenAI client v1.0.0+")
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("⚠️ OPENAI_API_KEY environment variable not set")
    else:
        logger.info("✅ OpenAI client initialized successfully with API key from environment")
        logger.info(f"🔑 OpenAI API key (masked): {'*' * 8 + os.getenv('OPENAI_API_KEY')[-4:] if os.getenv('OPENAI_API_KEY') else ''}")
    
    openai_available = True
except Exception as e:
    logger.error(f"❌ OpenAI failed to initialize: {e}")
    openai_available = False

def generate_react_component(task: str) -> str:
    """
    Generate a React component based on a task description using OpenAI.
    
    Args:
        task: Description of the component to generate
        
    Returns:
        String containing the generated React component code
    """
    if not openai_available:
        logger.error("❌ OpenAI client is not available")
        raise Exception("OpenAI client is not available")
        
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ OpenAI API key is not set")
        raise Exception("OpenAI API key is not set")
    
    try:
        # Define the function to retry
        def call_openai_with_model(model_name):
            return client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": task}
                ]
            )
        
        # Try to use gpt-4o model first
        try:
            # Use retry handler if available
            if hardening_available:
                response = retry_with_backoff(
                    lambda: call_openai_with_model("gpt-4o"),
                    retries=3,
                    backoff=1.5
                )
                model_used = "gpt-4o"
                logger.info("✅ Using gpt-4o model with retry handler")
            else:
                # Fallback to direct call if hardening not available
                response = call_openai_with_model("gpt-4o")
                model_used = "gpt-4o"
                logger.info("✅ Using gpt-4o model")
        except Exception as model_error:
            # Classify the error if hardening is available
            if hardening_available:
                error_category = classify_error(model_error)
                logger.warning(f"⚠️ {error_category} encountered with gpt-4o: {str(model_error)}")
            
            error_str = str(model_error).lower()
            
            # If gpt-4o is not available, fallback to gpt-4.1
            if "model_not_found" in error_str or "not found" in error_str:
                logger.warning(f"⚠️ gpt-4o model not found, falling back to gpt-4.1: {str(model_error)}")
                try:
                    # Use retry handler if available
                    if hardening_available:
                        response = retry_with_backoff(
                            lambda: call_openai_with_model("gpt-4.1"),
                            retries=3,
                            backoff=1.5
                        )
                        model_used = "gpt-4.1"
                        logger.info("✅ Using gpt-4.1 model (fallback) with retry handler")
                    else:
                        response = call_openai_with_model("gpt-4.1")
                        model_used = "gpt-4.1"
                        logger.info("✅ Using gpt-4.1 model (fallback)")
                except Exception as fallback_error:
                    # Classify the error if hardening is available
                    if hardening_available:
                        error_category = classify_error(fallback_error)
                        logger.warning(f"⚠️ {error_category} encountered with gpt-4.1: {str(fallback_error)}")
                    
                    # If gpt-4.1 also fails, check if it's a quota issue
                    fallback_error_str = str(fallback_error).lower()
                    if "insufficient_quota" in fallback_error_str or "exceeded your current quota" in fallback_error_str:
                        logger.warning(f"⚠️ Quota exceeded for gpt-4.1, falling back to gpt-3.5-turbo: {str(fallback_error)}")
                        
                        # Use retry handler if available
                        if hardening_available:
                            response = retry_with_backoff(
                                lambda: call_openai_with_model("gpt-3.5-turbo"),
                                retries=3,
                                backoff=1.5
                            )
                            model_used = "gpt-3.5-turbo"
                            logger.info("✅ Using gpt-3.5-turbo model (quota fallback) with retry handler")
                        else:
                            response = call_openai_with_model("gpt-3.5-turbo")
                            model_used = "gpt-3.5-turbo"
                            logger.info("✅ Using gpt-3.5-turbo model (quota fallback)")
                        
                        # Log quota issue for monitoring
                        print("⚠️ QUOTA_ALERT: OpenAI quota exceeded, using gpt-3.5-turbo fallback")
                    else:
                        # If it's another error, re-raise it
                        raise fallback_error
            # If it's a quota issue with gpt-4o, try gpt-3.5-turbo directly
            elif "insufficient_quota" in error_str or "exceeded your current quota" in error_str:
                logger.warning(f"⚠️ Quota exceeded for gpt-4o, falling back to gpt-3.5-turbo: {str(model_error)}")
                
                # Use retry handler if available
                if hardening_available:
                    response = retry_with_backoff(
                        lambda: call_openai_with_model("gpt-3.5-turbo"),
                        retries=3,
                        backoff=1.5
                    )
                    model_used = "gpt-3.5-turbo"
                    logger.info("✅ Using gpt-3.5-turbo model (quota fallback) with retry handler")
                else:
                    response = call_openai_with_model("gpt-3.5-turbo")
                    model_used = "gpt-3.5-turbo"
                    logger.info("✅ Using gpt-3.5-turbo model (quota fallback)")
                
                # Log quota issue for monitoring
                print("⚠️ QUOTA_ALERT: OpenAI quota exceeded, using gpt-3.5-turbo fallback")
            else:
                # If it's another error, re-raise it
                raise model_error
        
        # Extract the generated code
        code = response.choices[0].message.content
        
        # Log the parsed response
        logger.info(f"✅ Successfully generated React component ({len(code)} chars)")
        print(f"✅ HAL model used: {model_used}")
        print("✅ Raw OpenAI response:", response.choices[0].message.content[:120])
        print(f"📝 Parsed OpenAI response: {code[:100]}...")
        print("✅ HAL generated code:\n", code)
        
        return code
    except Exception as e:
        # Classify and log the error if hardening is available
        if hardening_available:
            error_category = classify_error(e)
            logger.error(f"❌ {error_category} generating React component: {str(e)}")
            
            # Try to log to memory if available
            try:
                from app.modules.hal_memory import write_memory
                log_error_to_memory(
                    memory_writer=write_memory,
                    project_id="system",
                    agent_id="hal",
                    e=e,
                    operation="generate_react_component"
                )
                logger.info(f"✅ Logged {error_category} to memory")
            except ImportError:
                logger.warning("⚠️ Could not log error to memory: hal_memory module not available")
        else:
            logger.error(f"❌ Error generating React component: {str(e)}")
        
        print(f"❌ Fallback reason: OpenAI is unavailable - {str(e)}")
        
        # Return a fallback component if generation fails
        fallback_code = f"""
// Error generating component: {str(e)}
// Fallback component based on task: {task}
import React, {{ useState }} from 'react';
export default function FallbackComponent() {{
  const [error, setError] = useState("Failed to generate component");
  
  return (
    <div className="p-4 border border-red-300 rounded bg-red-50">
      <h2 className="text-lg font-semibold text-red-700">Component Generation Error</h2>
      <p className="text-red-600">{{error}}</p>
      <div className="mt-4 p-2 bg-white rounded border border-gray-200">
        <p className="text-gray-700">Task description:</p>
        <pre className="mt-2 p-2 bg-gray-50 rounded text-sm">{{task}}</pre>
      </div>
    </div>
  );
}}
"""
        # Log memory write failure
        print("❌ Memory write will contain fallback HTML due to OpenAI error")
        return fallback_code
