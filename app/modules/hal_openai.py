"""
OpenAI code generation module for HAL agent.

This module provides functions to generate React/JSX code using OpenAI's API,
specifically designed for use with the HAL agent's code generation capabilities.
"""

import openai
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("hal_openai")

def generate_react_component(task: str) -> str:
    """
    Generate React component code using OpenAI's API.
    
    Parameters:
    - task: The task description or requirements for the component
    
    Returns:
    - The generated React component code as a string
    """
    try:
        # Configure OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert React developer. Use Tailwind CSS for styling. Return only the code without explanations."},
                {"role": "user", "content": task}
            ]
        )
        
        # Extract the generated code
        generated_code = response.choices[0].message["content"]
        logger.info(f"✅ Successfully generated React component ({len(generated_code)} chars)")
        
        return generated_code
    except Exception as e:
        logger.error(f"❌ Error generating React component: {str(e)}")
        
        # Return a fallback component if generation fails
        return f"""
// Error generating component: {str(e)}
// Fallback component based on task: {task}
import React, { useState } from 'react';

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
