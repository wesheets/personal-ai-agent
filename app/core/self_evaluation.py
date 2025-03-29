from typing import Dict, Any, List, Optional
from app.providers import process_with_model

class SelfEvaluationPrompt:
    """
    Handles self-evaluation prompts for agent reflection
    """
    
    @staticmethod
    async def generate_rationale(
        model: str,
        agent_type: str,
        input_text: str,
        output_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate rationale, assumptions, and improvement suggestions
        
        Args:
            model: Model to use for generating rationale
            agent_type: Type of agent
            input_text: User input text
            output_text: Agent output text
            context: Additional context
            
        Returns:
            Dictionary containing rationale, assumptions, and improvement suggestions
        """
        # Create prompt for rationale generation
        prompt_chain = {
            "system": f"You are a reflection system for a {agent_type} agent. Your task is to analyze the agent's response to a user query and provide a thoughtful reflection on the reasoning process.",
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        user_input = f"""
I need you to analyze the following agent response and provide a reflection on the reasoning process.

USER QUERY:
{input_text}

AGENT RESPONSE:
{output_text}

Please answer the following questions:
1. What was your rationale for this response?
2. What assumptions did you make?
3. What could improve this next time?

Provide your answers in a clear, concise manner.
"""
        
        # Process with model
        result = await process_with_model(
            model=model,
            prompt_chain=prompt_chain,
            user_input=user_input,
            context=context
        )
        
        # Parse the response to extract rationale, assumptions, and improvement suggestions
        content = result.get("content", "")
        
        # Simple parsing - in a production system, you might want more robust parsing
        rationale = ""
        assumptions = ""
        improvement_suggestions = ""
        
        lines = content.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "rationale" in line.lower() or "1." in line:
                current_section = "rationale"
                rationale = line.split(":", 1)[1].strip() if ":" in line else ""
                continue
            elif "assumptions" in line.lower() or "2." in line:
                current_section = "assumptions"
                assumptions = line.split(":", 1)[1].strip() if ":" in line else ""
                continue
            elif "improve" in line.lower() or "3." in line:
                current_section = "improvement"
                improvement_suggestions = line.split(":", 1)[1].strip() if ":" in line else ""
                continue
            
            if current_section == "rationale" and not line.startswith(("1.", "2.", "3.")):
                rationale += " " + line if rationale else line
            elif current_section == "assumptions" and not line.startswith(("1.", "2.", "3.")):
                assumptions += " " + line if assumptions else line
            elif current_section == "improvement" and not line.startswith(("1.", "2.", "3.")):
                improvement_suggestions += " " + line if improvement_suggestions else line
        
        return {
            "rationale": rationale.strip(),
            "assumptions": assumptions.strip(),
            "improvement_suggestions": improvement_suggestions.strip()
        }
    
    @staticmethod
    async def generate_self_evaluation(
        model: str,
        agent_type: str,
        input_text: str,
        output_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate confidence level and failure points
        
        Args:
            model: Model to use for generating self-evaluation
            agent_type: Type of agent
            input_text: User input text
            output_text: Agent output text
            context: Additional context
            
        Returns:
            Dictionary containing confidence level and failure points
        """
        # Create prompt for self-evaluation
        prompt_chain = {
            "system": f"You are a self-evaluation system for a {agent_type} agent. Your task is to critically evaluate the agent's response to a user query and assess its confidence and potential failure points.",
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        user_input = f"""
I need you to evaluate the following agent response and provide a self-assessment.

USER QUERY:
{input_text}

AGENT RESPONSE:
{output_text}

Please answer the following questions:
1. How confident are you in this output? (Provide a confidence level and explanation)
2. What are possible failure points or limitations in this response?

Be honest and critical in your assessment.
"""
        
        # Process with model
        result = await process_with_model(
            model=model,
            prompt_chain=prompt_chain,
            user_input=user_input,
            context=context
        )
        
        # Parse the response to extract confidence level and failure points
        content = result.get("content", "")
        
        # Simple parsing - in a production system, you might want more robust parsing
        confidence_level = ""
        failure_points = ""
        
        lines = content.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "confident" in line.lower() or "1." in line:
                current_section = "confidence"
                confidence_level = line.split(":", 1)[1].strip() if ":" in line else ""
                continue
            elif "failure" in line.lower() or "limitations" in line.lower() or "2." in line:
                current_section = "failure"
                failure_points = line.split(":", 1)[1].strip() if ":" in line else ""
                continue
            
            if current_section == "confidence" and not line.startswith(("1.", "2.")):
                confidence_level += " " + line if confidence_level else line
            elif current_section == "failure" and not line.startswith(("1.", "2.")):
                failure_points += " " + line if failure_points else line
        
        return {
            "confidence_level": confidence_level.strip(),
            "failure_points": failure_points.strip()
        }
