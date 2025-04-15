# /app/utils/prompt_cleaner.py

import re

def clean_prompt(prompt: str) -> str:
    """
    Sanitizes prompts to protect privacy and abstract internal agent architecture
    before any LLM call.
    
    This function removes:
    - Known agent names (HAL, ASH, NOVA, ORCHESTRATOR)
    - Platform names (Promethios, Life Tree, LifeTree, Prometheus)
    - Email addresses
    - UUID-like strings
    - User names if tagged (e.g., 'user: John Doe')
    
    Args:
        prompt (str): The original prompt text to be sanitized
        
    Returns:
        str: The sanitized prompt with sensitive information redacted
    """
    # Strip known agent names
    prompt = re.sub(r"\b(HAL|ASH|NOVA|ORCHESTRATOR)\b", "Agent", prompt)

    # Remove platform names
    prompt = re.sub(r"\b(Promethios|Life Tree|LifeTree|Prometheus)\b", "the system", prompt)

    # Redact emails - improved pattern to handle complex cases with + signs
    prompt = re.sub(r"[\w\+\.-]+@[\w\.-]+\.\w+", "[REDACTED_EMAIL]", prompt)
    
    # Additional pass to catch any remaining email fragments
    prompt = re.sub(r"\w+\+\[REDACTED_EMAIL\]", "[REDACTED_EMAIL]", prompt)

    # Redact UUID-like strings
    prompt = re.sub(r"[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}", "[REDACTED_UUID]", prompt, flags=re.I)

    # Redact user names if tagged (e.g., 'user: John Doe')
    prompt = re.sub(r"user:\s*[\w\s]+", "user: [REDACTED_USER]", prompt, flags=re.I)

    return prompt
