"""
Sage Beliefs Routes Module
This module defines the routes for the Sage Beliefs system, which is responsible for
providing wisdom, insights, and philosophical perspectives on various topics.
"""
import logging
import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field
# Import schemas
from app.schemas.sage_beliefs_schema import SageBeliefRequest, SageBeliefResponse, BeliefInsight
# Configure logging
logger = logging.getLogger("app.routes.sage_beliefs_routes")
# Create router with API prefix
router = APIRouter(
    prefix="/api/sage",
    tags=["sage"],
    responses={404: {"description": "Not found"}}
)

# Add GET endpoint to handle requests with query parameters
@router.get("/beliefs", response_model=SageBeliefResponse)
async def get_sage_beliefs_get(
    domain: str = Query(None, description="Domain or topic to get beliefs about"),
    perspective: str = Query("balanced", description="Perspective to consider (balanced, optimistic, critical)"),
    depth: str = Query("standard", description="Depth of insights (brief, standard, comprehensive)")
):
    """
    Retrieve sage beliefs and insights on a given topic using GET method.
    
    Args:
        domain: Domain or topic to get beliefs about
        perspective: Perspective to consider
        depth: Depth of insights
        
    Returns:
        SageBeliefResponse containing the beliefs and insights
    """
    try:
        logger.info(f"Retrieving sage beliefs for domain: {domain} (GET method)")
        
        # Validate domain parameter
        if not domain:
            raise HTTPException(
                status_code=422,
                detail="Domain parameter is required"
            )
        
        # Generate a unique belief ID
        import uuid
        belief_id = f"belief_{uuid.uuid4().hex[:8]}"
        
        # In a real implementation, this would call the actual sage beliefs system
        # For now, we'll generate insights based on the domain and perspective
        
        beliefs_results = generate_beliefs(
            topic=domain,
            context=None,
            perspective=perspective,
            depth=depth
        )
        
        return SageBeliefResponse(
            status="success",
            message="Beliefs retrieved successfully",
            belief_id=belief_id,
            topic=domain,
            perspective=perspective,
            insights=beliefs_results,
            timestamp=str(datetime.datetime.now())
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.error(f"Error retrieving sage beliefs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve beliefs: {str(e)}")

# Keep the original POST endpoint for backward compatibility
@router.post("/beliefs", response_model=SageBeliefResponse)
async def get_sage_beliefs(request: SageBeliefRequest = Body(...)):
    """
    Retrieve sage beliefs and insights on a given topic.
    
    Args:
        request: The sage belief request containing topic and context
        
    Returns:
        SageBeliefResponse containing the beliefs and insights
    """
    try:
        logger.info(f"Retrieving sage beliefs for topic: {request.topic}")
        
        # Generate a unique belief ID
        import uuid
        belief_id = f"belief_{uuid.uuid4().hex[:8]}"
        
        # In a real implementation, this would call the actual sage beliefs system
        # For now, we'll generate insights based on the topic and perspective
        
        beliefs_results = generate_beliefs(
            topic=request.topic,
            context=request.context,
            perspective=request.perspective,
            depth=request.depth
        )
        
        return SageBeliefResponse(
            status="success",
            message="Beliefs retrieved successfully",
            belief_id=belief_id,
            topic=request.topic,
            perspective=request.perspective,
            insights=beliefs_results,
            timestamp=str(datetime.datetime.now())
        )
    except Exception as e:
        logger.error(f"Error retrieving sage beliefs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve beliefs: {str(e)}")

def generate_beliefs(topic: str, context: Optional[str], perspective: str = "balanced", depth: str = "standard") -> List[BeliefInsight]:
    """
    Generate beliefs and insights based on the topic and perspective.
    
    Args:
        topic: The topic to generate beliefs about
        context: Additional context for the beliefs
        perspective: The perspective to consider
        depth: The depth of insights
        
    Returns:
        List of belief insights
    """
    # In a real implementation, this would use an LLM or other system to generate insights
    # For now, we'll return some sample insights based on the topic
    
    insights = []
    
    # Sample insights for software development
    if topic.lower() in ["software_development", "software development", "programming", "coding"]:
        insights = [
            BeliefInsight(
                title="Simplicity Over Complexity",
                content="The best code is often the simplest code. Complexity should be avoided unless absolutely necessary.",
                confidence=0.92,
                sources=["Clean Code by Robert C. Martin", "The Pragmatic Programmer"]
            ),
            BeliefInsight(
                title="Test-Driven Development",
                content="Writing tests before code leads to better design and more maintainable systems.",
                confidence=0.85,
                sources=["Test-Driven Development by Example", "Extreme Programming Explained"]
            ),
            BeliefInsight(
                title="Continuous Learning",
                content="The field evolves rapidly, requiring continuous learning and adaptation.",
                confidence=0.95,
                sources=["The Clean Coder", "Apprenticeship Patterns"]
            )
        ]
    # Sample insights for artificial intelligence
    elif topic.lower() in ["ai", "artificial intelligence", "machine learning", "ml"]:
        insights = [
            BeliefInsight(
                title="Data Quality Matters",
                content="The quality of AI systems is fundamentally limited by the quality of their training data.",
                confidence=0.94,
                sources=["Data Science for Business", "Practical Statistics for Data Scientists"]
            ),
            BeliefInsight(
                title="Ethical Considerations",
                content="AI development must prioritize ethical considerations and potential societal impacts.",
                confidence=0.91,
                sources=["Weapons of Math Destruction", "Human Compatible"]
            ),
            BeliefInsight(
                title="Explainability",
                content="As AI systems become more complex, explainability becomes increasingly important for trust and adoption.",
                confidence=0.88,
                sources=["Interpretable Machine Learning", "The Book of Why"]
            )
        ]
    # Generic insights for other topics
    else:
        insights = [
            BeliefInsight(
                title="First Principles Thinking",
                content="Breaking down complex problems to their fundamental truths and building up from there.",
                confidence=0.89,
                sources=["Thinking, Fast and Slow", "Poor Charlie's Almanack"]
            ),
            BeliefInsight(
                title="Continuous Improvement",
                content="Small, consistent improvements compound over time to create significant progress.",
                confidence=0.93,
                sources=["Atomic Habits", "The Compound Effect"]
            ),
            BeliefInsight(
                title="Balance of Perspectives",
                content="Considering multiple viewpoints leads to more robust understanding and better decisions.",
                confidence=0.87,
                sources=["Thinking in Systems", "Factfulness"]
            )
        ]
    
    # Adjust insights based on perspective
    if perspective.lower() == "optimistic":
        for insight in insights:
            insight.content = insight.content.replace("challenges", "opportunities")
            insight.content = insight.content.replace("problems", "possibilities")
            insight.confidence = min(1.0, insight.confidence + 0.05)
    elif perspective.lower() == "critical":
        for insight in insights:
            insight.content = "While " + insight.content.lower() + ", it's important to recognize the limitations and challenges this presents."
            insight.confidence = max(0.5, insight.confidence - 0.1)
    
    # Adjust number of insights based on depth
    if depth.lower() == "brief":
        insights = insights[:1]
    elif depth.lower() == "comprehensive" and len(insights) >= 3:
        # Add an additional insight for comprehensive depth
        insights.append(
            BeliefInsight(
                title="Interconnected Knowledge",
                content=f"{topic} does not exist in isolation but is connected to many other fields and domains of knowledge.",
                confidence=0.82,
                sources=["Range by David Epstein", "Where Good Ideas Come From"]
            )
        )
    
    return insights
