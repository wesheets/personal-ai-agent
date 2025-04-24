"""
SAGE Agent Module

This module provides the implementation for the SAGE agent,
which analyzes CRITIC-approved loops, logs belief/emotion scores,
and generates structured belief maps.
"""
import logging
import traceback
import datetime
import json
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger("agents.sage")

# Import memory functions if available
try:
    from app.modules.memory_api import write_memory
    memory_available = True
except ImportError:
    memory_available = False
    logger.warning("⚠️ Memory module not available, using mock implementation")
    
    # Mock implementation for testing
    async def write_memory(agent_id, memory_type, tag, value):
        logger.info(f"Mock memory write: {agent_id}, {memory_type}, {tag}, {len(str(value))} chars")
        return {"status": "success", "message": "Mock memory write successful"}

class SageAgent:
    """
    SageAgent analyzes CRITIC-approved loops, logs belief/emotion scores,
    and generates structured belief maps.
    """
    def __init__(self, tools: List[str] = None):
        self.agent_id = "sage"
        self.name = "Sage"
        self.description = "Analyzes CRITIC-approved loops, logs belief/emotion scores"
        self.tools = tools or ["reflect", "summarize", "score_belief"]
    
    async def reflect(self, loop_id: str, summary_text: str) -> Dict[str, Any]:
        """
        Analyze a loop summary to extract key beliefs and their confidence levels.
        
        Args:
            loop_id: Unique identifier for the loop
            summary_text: Summary text to analyze for beliefs
            
        Returns:
            Dict containing belief scores and reflection
        """
        try:
            logger.info(f"SAGE reflecting on loop summary for loop: {loop_id}")
            
            # Extract key beliefs from summary
            # In a real implementation, this would use more sophisticated NLP
            # For now, we'll use a simple approach to extract key points
            
            # Sample beliefs extraction logic
            beliefs = []
            
            # Split summary into sentences and analyze each one
            sentences = summary_text.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Simple heuristic: longer sentences likely contain beliefs
                if len(sentence) > 30:
                    # Generate confidence based on sentence structure
                    confidence = min(0.5 + (len(sentence) / 200), 0.95)
                    
                    # Simple sentiment analysis for emotional weight
                    positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'improve', 'efficient']
                    negative_words = ['bad', 'poor', 'negative', 'fail', 'issue', 'problem', 'error', 'slow']
                    
                    emotional_weight = 0.0
                    for word in positive_words:
                        if word in sentence.lower():
                            emotional_weight += 0.2
                    
                    for word in negative_words:
                        if word in sentence.lower():
                            emotional_weight -= 0.2
                    
                    # Clamp emotional weight to [-1, 1]
                    emotional_weight = max(-1.0, min(1.0, emotional_weight))
                    
                    # Add belief to list
                    beliefs.append({
                        "belief": sentence,
                        "confidence": round(confidence, 2),
                        "emotional_weight": round(emotional_weight, 2) if emotional_weight != 0 else None
                    })
            
            # If no beliefs were extracted, add a default one
            if not beliefs:
                beliefs.append({
                    "belief": "Insufficient information to extract clear beliefs from summary",
                    "confidence": 0.3,
                    "emotional_weight": None
                })
            
            # Generate reflection based on beliefs
            reflection = self._generate_reflection(beliefs)
            
            # Prepare result
            result = {
                "status": "success",
                "belief_scores": beliefs,
                "reflection_text": reflection,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "loop_id": loop_id
            }
            
            # Log to memory if available
            if memory_available:
                memory_tag = f"sage_summary_{loop_id}"
                memory_result = await write_memory(
                    agent_id=self.agent_id,
                    memory_type="loop",
                    tag=memory_tag,
                    value=json.dumps(result)
                )
                logger.info(f"Memory write result: {memory_result}")
            else:
                logger.warning("Memory module not available, skipping memory write")
            
            return result
        
        except Exception as e:
            error_msg = f"Error in SAGE reflection: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Return error response
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id
            }
    
    async def summarize(self, loop_id: str, content: str) -> Dict[str, Any]:
        """
        Generate a concise summary of the provided content.
        
        Args:
            loop_id: Unique identifier for the loop
            content: Content to summarize
            
        Returns:
            Dict containing the summary
        """
        try:
            logger.info(f"SAGE summarizing content for loop: {loop_id}")
            
            # Simple summarization logic
            # In a real implementation, this would use more sophisticated NLP
            
            # Count words in content
            word_count = len(content.split())
            
            # Generate a simple summary based on first few sentences
            sentences = content.split('.')
            summary_sentences = sentences[:min(3, len(sentences))]
            summary = '. '.join(summary_sentences) + '.'
            
            # Prepare result
            result = {
                "status": "success",
                "summary": summary,
                "original_word_count": word_count,
                "summary_word_count": len(summary.split()),
                "compression_ratio": len(summary.split()) / max(1, word_count),
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "loop_id": loop_id
            }
            
            # Log to memory if available
            if memory_available:
                memory_tag = f"sage_summary_{loop_id}"
                memory_result = await write_memory(
                    agent_id=self.agent_id,
                    memory_type="loop",
                    tag=memory_tag,
                    value=json.dumps(result)
                )
                logger.info(f"Memory write result: {memory_result}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in SAGE summarization: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Return error response
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id
            }
    
    async def score_belief(self, loop_id: str, belief: str) -> Dict[str, Any]:
        """
        Score a specific belief for confidence and emotional weight.
        
        Args:
            loop_id: Unique identifier for the loop
            belief: Belief statement to score
            
        Returns:
            Dict containing the belief score
        """
        try:
            logger.info(f"SAGE scoring belief for loop: {loop_id}")
            
            # Simple belief scoring logic
            # In a real implementation, this would use more sophisticated NLP
            
            # Generate confidence based on sentence structure
            confidence = min(0.5 + (len(belief) / 200), 0.95)
            
            # Simple sentiment analysis for emotional weight
            positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'improve', 'efficient']
            negative_words = ['bad', 'poor', 'negative', 'fail', 'issue', 'problem', 'error', 'slow']
            
            emotional_weight = 0.0
            for word in positive_words:
                if word in belief.lower():
                    emotional_weight += 0.2
            
            for word in negative_words:
                if word in belief.lower():
                    emotional_weight -= 0.2
            
            # Clamp emotional weight to [-1, 1]
            emotional_weight = max(-1.0, min(1.0, emotional_weight))
            
            # Prepare result
            result = {
                "status": "success",
                "belief": belief,
                "confidence": round(confidence, 2),
                "emotional_weight": round(emotional_weight, 2) if emotional_weight != 0 else None,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "loop_id": loop_id
            }
            
            # Log to memory if available
            if memory_available:
                memory_tag = f"sage_belief_{loop_id}_{hash(belief) % 10000}"
                memory_result = await write_memory(
                    agent_id=self.agent_id,
                    memory_type="loop",
                    tag=memory_tag,
                    value=json.dumps(result)
                )
                logger.info(f"Memory write result: {memory_result}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in SAGE belief scoring: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            # Return error response
            return {
                "status": "error",
                "message": error_msg,
                "loop_id": loop_id
            }
    
    def _generate_reflection(self, beliefs: List[Dict[str, Any]]) -> str:
        """
        Generate a reflection based on the extracted beliefs.
        
        Args:
            beliefs: List of belief dictionaries with confidence and emotional weight
            
        Returns:
            Reflection text summarizing the beliefs
        """
        if not beliefs:
            return "No clear beliefs could be extracted from the summary."
        
        # Count beliefs by emotional weight
        positive_beliefs = [b for b in beliefs if b.get("emotional_weight", 0) > 0]
        negative_beliefs = [b for b in beliefs if b.get("emotional_weight", 0) < 0]
        neutral_beliefs = [b for b in beliefs if b.get("emotional_weight", 0) == 0 or b.get("emotional_weight") is None]
        
        # Sort beliefs by confidence
        high_confidence = [b for b in beliefs if b.get("confidence", 0) > 0.7]
        
        # Generate reflection
        reflection_parts = []
        
        # Overall tone
        if len(positive_beliefs) > len(negative_beliefs):
            reflection_parts.append("The summary suggests a generally positive outlook.")
        elif len(negative_beliefs) > len(positive_beliefs):
            reflection_parts.append("The summary suggests some concerns or challenges.")
        else:
            reflection_parts.append("The summary presents a balanced perspective.")
        
        # High confidence beliefs
        if high_confidence:
            reflection_parts.append(f"With high confidence, we can assert that: {high_confidence[0]['belief']}")
        
        # Additional insights
        if len(beliefs) > 1:
            reflection_parts.append(f"Additional insights include: {beliefs[1]['belief']}")
        
        # Recommendations based on emotional weight
        if negative_beliefs:
            reflection_parts.append("Areas that may need attention include addressing the negative aspects identified in the summary.")
        
        # Join all parts
        reflection = " ".join(reflection_parts)
        
        return reflection

# Main function to run the sage agent
async def run_sage_agent(task: str, project_id: str, tools: List[str] = None) -> Dict[str, Any]:
    """
    Run the SAGE agent with the given task, project_id, and tools.
    
    Args:
        task: The task to execute
        project_id: The project identifier
        tools: List of tools to use (optional)
        
    Returns:
        Dict containing the result of the execution
    """
    try:
        logger.info(f"Running SAGE agent with task: {task}, project_id: {project_id}")
        
        # Initialize tools if None
        if tools is None:
            tools = ["reflect", "summarize", "score_belief"]
        
        # Create sage agent instance
        sage = SageAgent(tools)
        
        # Parse task to determine action
        if task.startswith("reflect:"):
            # Extract loop_id and summary_text from task
            parts = task.split(":", 1)[1].strip().split("|")
            if len(parts) < 2:
                raise ValueError("Invalid reflect task format. Expected 'reflect:loop_id|summary_text'")
            
            loop_id = parts[0].strip()
            summary_text = parts[1].strip()
            
            # Call reflect method
            return await sage.reflect(loop_id, summary_text)
            
        elif task.startswith("summarize:"):
            # Extract loop_id and content from task
            parts = task.split(":", 1)[1].strip().split("|")
            if len(parts) < 2:
                raise ValueError("Invalid summarize task format. Expected 'summarize:loop_id|content'")
            
            loop_id = parts[0].strip()
            content = parts[1].strip()
            
            # Call summarize method
            return await sage.summarize(loop_id, content)
            
        elif task.startswith("score_belief:"):
            # Extract loop_id and belief from task
            parts = task.split(":", 1)[1].strip().split("|")
            if len(parts) < 2:
                raise ValueError("Invalid score_belief task format. Expected 'score_belief:loop_id|belief'")
            
            loop_id = parts[0].strip()
            belief = parts[1].strip()
            
            # Call score_belief method
            return await sage.score_belief(loop_id, belief)
            
        else:
            # Default to mock reflection for testing
            logger.warning(f"Unknown task format: {task}. Using mock reflection.")
            
            # Create mock summary text
            mock_summary = f"This is a mock summary for project {project_id}. It contains some positive aspects like improved user experience and efficient code structure. However, there are also some concerns about scalability and performance under heavy load."
            
            # Call reflect method with mock data
            return await sage.reflect(f"mock-{project_id}", mock_summary)
            
    except Exception as e:
        error_msg = f"Error running SAGE agent: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # Return error response
        return {
            "status": "error",
            "message": error_msg,
            "task": task,
            "tools": tools if tools else [],
            "project_id": project_id
        }

# Test function for isolated testing
async def test_sage_agent():
    """
    Test the SAGE agent in isolation.
    
    Returns:
        Dict containing test results
    """
    print("\n=== Testing SAGE Agent in isolation ===\n")
    
    try:
        # Create test data
        loop_id = "test-loop-123"
        summary_text = "This project implements a collaborative document editing platform. The user interface is clean and intuitive, making it easy for new users to get started. The backend architecture uses microservices for scalability, but there are concerns about the complexity of deployment and maintenance. Overall, the project shows promise but needs more work on documentation and testing."
        
        # Run the agent with reflect task
        task = f"reflect:{loop_id}|{summary_text}"
        result = await run_sage_agent(task, "test-project")
        
        # Print the result
        print(f"\nReflect Result:")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Reflection: {result.get('reflection_text', 'No reflection')}")
        print(f"Beliefs: {len(result.get('belief_scores', []))} extracted")
        
        # Test summarization
        content = "This is a lengthy document that contains multiple paragraphs of information about the project. It discusses various aspects including architecture, user interface, performance considerations, and future plans. The document is quite detailed and would benefit from summarization to extract the key points quickly."
        task = f"summarize:{loop_id}|{content}"
        summarize_result = await run_sage_agent(task, "test-project")
        
        print(f"\nSummarize Result:")
        print(f"Status: {summarize_result.get('status', 'unknown')}")
        print(f"Summary: {summarize_result.get('summary', 'No summary')}")
        
        # Test belief scoring
        belief = "The microservice architecture provides good scalability but increases operational complexity"
        task = f"score_belief:{loop_id}|{belief}"
        score_result = await run_sage_agent(task, "test-project")
        
        print(f"\nScore Belief Result:")
        print(f"Status: {score_result.get('status', 'unknown')}")
        print(f"Confidence: {score_result.get('confidence', 'unknown')}")
        print(f"Emotional Weight: {score_result.get('emotional_weight', 'unknown')}")
        
        return {
            "reflect_result": result,
            "summarize_result": summarize_result,
            "score_result": score_result
        }
        
    except Exception as e:
        error_msg = f"Error testing SAGE agent: {str(e)}"
        print(f"❌ {error_msg}")
        print(traceback.format_exc())
        
        return {
            "status": "error",
            "message": error_msg
        }
