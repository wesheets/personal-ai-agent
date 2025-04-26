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

# Helper function to generate beliefs
async def generate_beliefs(topic: str, context: Optional[str] = None, 
                          perspective: str = "balanced", depth: str = "standard") -> List[BeliefInsight]:
    """
    Generate beliefs about a specific topic.
    
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

# POST endpoint for backward compatibility
@router.post("/beliefs", response_model=SageBeliefResponse)
async def post_sage_beliefs(request: SageBeliefRequest = Body(...)):
    """
    Get beliefs and insights about a specific topic (POST method).
    
    Args:
        request: The request body containing topic and optional parameters
        
    Returns:
        SageBeliefResponse containing the generated beliefs
    """
    try:
        logger.info(f"Processing POST request for sage beliefs on topic: {request.topic}")
        
        # Generate beliefs
        beliefs = await generate_beliefs(
            topic=request.topic,
            context=request.context,
            perspective=request.perspective,
            depth=request.depth
        )
        
        # Create response
        response = SageBeliefResponse(
            status="success",
            message="Beliefs generated successfully",
            topic=request.topic,
            beliefs=beliefs,
            timestamp=str(datetime.datetime.now())
        )
        
        logger.info(f"Successfully generated {len(beliefs)} beliefs for topic: {request.topic}")
        
        return response
    except Exception as e:
        logger.error(f"Error generating beliefs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate beliefs: {str(e)}")

# GET endpoint to support query parameters
@router.get("/beliefs", response_model=SageBeliefResponse)
async def get_sage_beliefs(
    domain: str = Query(..., description="The domain or topic to generate beliefs about"),
    context: Optional[str] = Query(None, description="Additional context for the beliefs"),
    perspective: str = Query("balanced", description="The perspective to consider (balanced, optimistic, critical)"),
    depth: str = Query("standard", description="The depth of insights (brief, standard, comprehensive)")
):
    """
    Get beliefs and insights about a specific topic (GET method).
    
    Args:
        domain: The domain or topic to generate beliefs about
        context: Additional context for the beliefs
        perspective: The perspective to consider
        depth: The depth of insights
        
    Returns:
        SageBeliefResponse containing the generated beliefs
    """
    try:
        logger.info(f"Processing GET request for sage beliefs on domain: {domain}")
        
        # Generate beliefs
        beliefs = await generate_beliefs(
            topic=domain,
            context=context,
            perspective=perspective,
            depth=depth
        )
        
        # Create response
        response = SageBeliefResponse(
            status="success",
            message="Beliefs generated successfully",
            topic=domain,
            beliefs=beliefs,
            timestamp=str(datetime.datetime.now())
        )
        
        logger.info(f"Successfully generated {len(beliefs)} beliefs for domain: {domain}")
        
        return response
    except Exception as e:
        logger.error(f"Error generating beliefs via GET: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate beliefs: {str(e)}")
