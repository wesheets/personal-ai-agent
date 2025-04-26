from fastapi import APIRouter, Body, Query, HTTPException
from typing import List, Optional
import datetime
import logging
from pydantic import BaseModel

# Import schemas
from app.schemas.sage_beliefs_schema import (
    SageBeliefRequest,
    SageBeliefResponse,
    BeliefInsight
)

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/sage", tags=["sage"])

async def generate_beliefs(topic: str, context: Optional[str] = None, 
                          perspective: str = "balanced", depth: str = "standard") -> List[BeliefInsight]:
    """
    Generate beliefs and insights about a specific topic.
    
    Args:
        topic: The topic to generate beliefs about
        context: Additional context for the beliefs
        perspective: The perspective to consider (balanced, optimistic, critical)
        depth: The depth of insights (brief, standard, comprehensive)
        
    Returns:
        List of BeliefInsight objects
    """
    logger.info(f"Generating beliefs for topic: {topic}, perspective: {perspective}, depth: {depth}")
    
    try:
        # Default insights that don't rely on external services
        insights = [
            BeliefInsight(
                title="Continuous Learning",
                content=f"In {topic}, continuous learning and adaptation are essential for long-term success.",
                confidence=0.95,
                sources=["Research studies", "Expert consensus"]
            ),
            BeliefInsight(
                title="Compound Effect",
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
        
        logger.info(f"Successfully generated {len(insights)} beliefs for topic: {topic}")
        return insights
    except Exception as e:
        logger.error(f"Error in generate_beliefs: {str(e)}")
        # Return a minimal set of insights rather than raising an exception
        return [
            BeliefInsight(
                title="Fallback Insight",
                content=f"When exploring {topic}, it's important to consider multiple perspectives.",
                confidence=0.7,
                sources=["General knowledge"]
            )
        ]

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
        
        # Validate required fields
        if not request.topic or not request.topic.strip():
            logger.warning("Invalid request: Missing or empty topic field")
            return SageBeliefResponse(
                status="error",
                message="Invalid request: Topic field is required and cannot be empty",
                topic="",
                beliefs=[],
                timestamp=str(datetime.datetime.now())
            )
        
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
        
        # Return error response with 200 status code instead of raising exception
        return SageBeliefResponse(
            status="error",
            message=f"Failed to generate beliefs: {str(e)}",
            topic=request.topic if hasattr(request, 'topic') else "",
            beliefs=[],
            timestamp=str(datetime.datetime.now())
        )

# GET endpoint to support query parameters
@router.get("/beliefs", response_model=SageBeliefResponse)
async def get_sage_beliefs(
    domain: Optional[str] = Query(None, description="The domain or topic to generate beliefs about"),
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
        
        # Validate required fields
        if not domain or not domain.strip():
            logger.warning("Invalid request: Missing or empty domain parameter")
            return SageBeliefResponse(
                status="error",
                message="Invalid request: Domain parameter is required and cannot be empty",
                topic="",
                beliefs=[],
                timestamp=str(datetime.datetime.now())
            )
        
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
        
        # Return error response with 200 status code instead of raising exception
        return SageBeliefResponse(
            status="error",
            message=f"Failed to generate beliefs: {str(e)}",
            topic=domain if domain else "",
            beliefs=[],
            timestamp=str(datetime.datetime.now())
        )
