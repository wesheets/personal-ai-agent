"""
OpenAI code generation module for HAL agent.

This module provides functions to generate React/JSX code using OpenAI's API,
specifically designed for use with the HAL agent's code generation capabilities.
"""

import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("hal_openai")

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
    client = None

def generate_react_component(task: str) -> str:
    """
    Generate React component code using OpenAI's API.
    
    Parameters:
    - task: The task description or requirements for the component
    
    Returns:
    - The generated React component code as a string
    """
    try:
        # Check if OpenAI is available
        if not openai_available:
            logger.error("❌ OpenAI client is not available")
            raise Exception("OpenAI client is not available")
            
        # Check if API key is set
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("❌ OpenAI API key is not set")
            raise Exception("OpenAI API key is not set")
        
        # Try to use gpt-4o model first
        try:
            # Use the OpenAI client v1.0.0+
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": task}
                ]
            )
            model_used = "gpt-4o"
            logger.info("✅ Using gpt-4o model")
        except Exception as model_error:
            # If gpt-4o is not available, fallback to gpt-4.1
            if "model_not_found" in str(model_error).lower() or "not found" in str(model_error).lower():
                logger.warning(f"⚠️ gpt-4o model not found, falling back to gpt-4.1: {str(model_error)}")
                response = client.chat.completions.create(
                    model="gpt-4.1",
                    messages=[
                        {"role": "user", "content": task}
                    ]
                )
                model_used = "gpt-4.1"
                logger.info("✅ Using gpt-4.1 model (fallback)")
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
