"""
Critic Review Routes Module

This module defines the routes for the Critic Review system, which is responsible for
analyzing and providing feedback on content, code, and other artifacts.
"""

import logging
import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger("app.routes.critic_review_routes")

# Create router with API prefix
router = APIRouter(
    prefix="/api/critic",
    tags=["critic"],
    responses={404: {"description": "Not found"}}
)

class CriticReviewRequest(BaseModel):
    """
    Schema for critic review request.
    """
    content: str = Field(..., description="Content to review")
    content_type: str = Field(default="text", description="Type of content (text, code, plan, etc.)")
    review_depth: str = Field(default="standard", description="Depth of review (quick, standard, comprehensive)")
    focus_areas: List[str] = Field(default=[], description="Specific areas to focus on during review")
    context: Optional[str] = Field(None, description="Additional context for the review")

class CriticReviewResponse(BaseModel):
    """
    Schema for critic review response.
    """
    status: str
    message: str
    review_id: str
    summary: str
    strengths: List[Dict[str, Any]]
    weaknesses: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    overall_rating: float
    timestamp: str

@router.post("/review", response_model=CriticReviewResponse)
async def review_content(request: CriticReviewRequest = Body(...)):
    """
    Review content using the Critic system.
    
    Args:
        request: The critic review request containing content and review parameters
        
    Returns:
        CriticReviewResponse containing the review results
    """
    try:
        logger.info(f"Reviewing content of type {request.content_type} with depth {request.review_depth}")
        
        # Generate a unique review ID
        import uuid
        review_id = f"review_{uuid.uuid4().hex[:8]}"
        
        # In a real implementation, this would call the actual critic review system
        # For now, we'll generate a simple review based on the content type and review depth
        
        review_results = generate_review(
            content=request.content,
            content_type=request.content_type,
            review_depth=request.review_depth,
            focus_areas=request.focus_areas,
            context=request.context
        )
        
        logger.info(f"Successfully completed review with ID: {review_id}")
        
        return CriticReviewResponse(
            status="success",
            message="Review completed successfully",
            review_id=review_id,
            summary=review_results["summary"],
            strengths=review_results["strengths"],
            weaknesses=review_results["weaknesses"],
            suggestions=review_results["suggestions"],
            overall_rating=review_results["overall_rating"],
            timestamp=str(datetime.datetime.now())
        )
    except Exception as e:
        logger.error(f"Error reviewing content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to review content: {str(e)}")

def generate_review(
    content: str,
    content_type: str,
    review_depth: str,
    focus_areas: List[str],
    context: Optional[str]
) -> Dict[str, Any]:
    """
    Generate a review for the given content.
    
    Args:
        content: Content to review
        content_type: Type of content
        review_depth: Depth of review
        focus_areas: Specific areas to focus on
        context: Additional context
        
    Returns:
        Review results as a dictionary
    """
    # Simple content analysis based on length and complexity
    content_length = len(content)
    word_count = len(content.split())
    sentence_count = content.count('.') + content.count('!') + content.count('?')
    
    # Calculate complexity metrics
    avg_word_length = sum(len(word) for word in content.split()) / max(1, word_count)
    avg_sentence_length = word_count / max(1, sentence_count)
    
    # Generate review based on content type
    if content_type.lower() == "code":
        return generate_code_review(content, review_depth, focus_areas)
    elif content_type.lower() == "plan":
        return generate_plan_review(content, review_depth, focus_areas)
    else:
        # Default to text review
        return generate_text_review(content, content_length, word_count, avg_word_length, avg_sentence_length, review_depth, focus_areas)

def generate_text_review(
    content: str,
    content_length: int,
    word_count: int,
    avg_word_length: float,
    avg_sentence_length: float,
    review_depth: str,
    focus_areas: List[str]
) -> Dict[str, Any]:
    """Generate a review for text content."""
    # Calculate base rating
    base_rating = 0.7  # Start with a neutral-positive rating
    
    # Adjust rating based on metrics
    if avg_sentence_length > 25:
        base_rating -= 0.1  # Penalize very long sentences
    elif avg_sentence_length < 10:
        base_rating -= 0.05  # Slight penalty for very short sentences
        
    if avg_word_length > 7:
        base_rating -= 0.05  # Penalize very complex vocabulary
        
    if word_count < 50:
        base_rating -= 0.1  # Penalize very short content
    elif word_count > 1000:
        base_rating += 0.05  # Bonus for substantial content
        
    # Ensure rating is within bounds
    overall_rating = max(0.1, min(0.95, base_rating))
    
    # Generate review components
    strengths = [
        {"aspect": "Length", "description": f"The content contains {word_count} words, which is sufficient for its purpose."} if word_count > 100 else {"aspect": "Conciseness", "description": "The content is concise and to the point."},
        {"aspect": "Structure", "description": "The content has a clear structure with appropriate paragraphs."}
    ]
    
    weaknesses = []
    if avg_sentence_length > 25:
        weaknesses.append({"aspect": "Sentence Length", "description": f"Average sentence length is {avg_sentence_length:.1f} words, which may be difficult to read."})
    if avg_word_length > 7:
        weaknesses.append({"aspect": "Vocabulary", "description": f"Average word length is {avg_word_length:.1f} characters, which may indicate overly complex vocabulary."})
    if word_count < 50:
        weaknesses.append({"aspect": "Content Depth", "description": "The content is quite brief and may benefit from more detail."})
    
    suggestions = [
        {"aspect": "Clarity", "description": "Consider breaking down longer sentences for improved readability."},
        {"aspect": "Structure", "description": "Adding subheadings could improve the organization of the content."},
        {"aspect": "Engagement", "description": "Consider adding examples or analogies to make the content more engaging."}
    ]
    
    # Add focus area specific feedback if provided
    if "clarity" in [area.lower() for area in focus_areas]:
        suggestions.append({"aspect": "Clarity", "description": "Pay special attention to defining technical terms and concepts for the audience."})
    if "conciseness" in [area.lower() for area in focus_areas]:
        suggestions.append({"aspect": "Conciseness", "description": "Review for redundant phrases and unnecessary qualifiers."})
    
    # Generate summary based on review depth
    if review_depth.lower() == "quick":
        summary = f"Quick review of text content ({word_count} words). Overall quality is {'good' if overall_rating > 0.7 else 'average' if overall_rating > 0.5 else 'needs improvement'}."
    elif review_depth.lower() == "comprehensive":
        summary = f"Comprehensive review of text content ({word_count} words, {avg_sentence_length:.1f} words per sentence). The content is {'well-structured and clear' if overall_rating > 0.7 else 'adequate but could be improved' if overall_rating > 0.5 else 'in need of significant revision'}. Key areas for improvement include sentence structure, vocabulary choice, and content organization."
    else:
        # Standard review
        summary = f"Review of text content ({word_count} words). The content is {'well-written' if overall_rating > 0.7 else 'adequate' if overall_rating > 0.5 else 'in need of revision'} with {'good' if avg_sentence_length < 20 else 'somewhat complex'} sentence structure."
    
    return {
        "summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "overall_rating": overall_rating
    }

def generate_code_review(
    content: str,
    review_depth: str,
    focus_areas: List[str]
) -> Dict[str, Any]:
    """Generate a review for code content."""
    # Simple code analysis
    line_count = content.count('\n') + 1
    comment_lines = content.count('#') + content.count('//') + content.count('/*') + content.count('*/')
    function_count = content.count('def ') + content.count('function ') + content.count('func ')
    class_count = content.count('class ')
    
    # Calculate comment ratio
    comment_ratio = comment_lines / max(1, line_count)
    
    # Calculate base rating
    base_rating = 0.7  # Start with a neutral-positive rating
    
    # Adjust rating based on metrics
    if comment_ratio < 0.1:
        base_rating -= 0.1  # Penalize low comment ratio
    elif comment_ratio > 0.3:
        base_rating += 0.05  # Bonus for good documentation
        
    if function_count == 0 and line_count > 20:
        base_rating -= 0.1  # Penalize long code without functions
        
    # Ensure rating is within bounds
    overall_rating = max(0.1, min(0.95, base_rating))
    
    # Generate review components
    strengths = [
        {"aspect": "Structure", "description": f"The code contains {function_count} functions and {class_count} classes, showing good organization."} if function_count > 0 or class_count > 0 else {"aspect": "Simplicity", "description": "The code is straightforward and concise."},
        {"aspect": "Documentation", "description": f"The code has a comment ratio of {comment_ratio:.1%}, which is good."} if comment_ratio > 0.2 else {"aspect": "Readability", "description": "The code uses clear variable names."}
    ]
    
    weaknesses = []
    if comment_ratio < 0.1:
        weaknesses.append({"aspect": "Documentation", "description": f"Comment ratio is only {comment_ratio:.1%}, which may make the code harder to understand."})
    if function_count == 0 and line_count > 20:
        weaknesses.append({"aspect": "Modularity", "description": "The code lacks function definitions, which could improve reusability and readability."})
    
    suggestions = [
        {"aspect": "Documentation", "description": "Add more comments explaining the purpose of complex logic."},
        {"aspect": "Error Handling", "description": "Consider adding try-except blocks for robust error handling."},
        {"aspect": "Testing", "description": "Add unit tests to verify the functionality."}
    ]
    
    # Add focus area specific feedback if provided
    if "performance" in [area.lower() for area in focus_areas]:
        suggestions.append({"aspect": "Performance", "description": "Review loops and data structures for optimization opportunities."})
    if "security" in [area.lower() for area in focus_areas]:
        suggestions.append({"aspect": "Security", "description": "Validate all inputs and sanitize data to prevent security vulnerabilities."})
    
    # Generate summary based on review depth
    if review_depth.lower() == "quick":
        summary = f"Quick review of code ({line_count} lines). Overall quality is {'good' if overall_rating > 0.7 else 'average' if overall_rating > 0.5 else 'needs improvement'}."
    elif review_depth.lower() == "comprehensive":
        summary = f"Comprehensive review of code ({line_count} lines, {function_count} functions, {class_count} classes). The code is {'well-structured and documented' if overall_rating > 0.7 else 'functional but could be improved' if overall_rating > 0.5 else 'in need of significant refactoring'}. Key areas for improvement include documentation, modularity, and error handling."
    else:
        # Standard review
        summary = f"Review of code ({line_count} lines). The code is {'well-written' if overall_rating > 0.7 else 'adequate' if overall_rating > 0.5 else 'in need of refactoring'} with {'good' if comment_ratio > 0.2 else 'insufficient'} documentation."
    
    return {
        "summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "overall_rating": overall_rating
    }

def generate_plan_review(
    content: str,
    review_depth: str,
    focus_areas: List[str]
) -> Dict[str, Any]:
    """Generate a review for plan content."""
    # Simple plan analysis
    line_count = content.count('\n') + 1
    step_count = content.count('Step ') + content.count('- ') + content.count('* ')
    
    # Calculate base rating
    base_rating = 0.7  # Start with a neutral-positive rating
    
    # Adjust rating based on metrics
    if step_count < 3:
        base_rating -= 0.1  # Penalize plans with very few steps
    elif step_count > 10:
        base_rating += 0.05  # Bonus for detailed plans
        
    if line_count < 10:
        base_rating -= 0.05  # Penalize very brief plans
        
    # Ensure rating is within bounds
    overall_rating = max(0.1, min(0.95, base_rating))
    
    # Generate review components
    strengths = [
        {"aspect": "Structure", "description": f"The plan contains {step_count} steps, providing good detail."} if step_count > 5 else {"aspect": "Conciseness", "description": "The plan is focused and to the point."},
        {"aspect": "Clarity", "description": "The plan uses clear language to describe the steps."}
    ]
    
    weaknesses = []
    if step_count < 3:
        weaknesses.append({"aspect": "Detail", "description": f"The plan only has {step_count} steps, which may not provide sufficient guidance."})
    if line_count < 10:
        weaknesses.append({"aspect": "Depth", "description": "The plan is quite brief and may benefit from more explanation."})
    
    suggestions = [
        {"aspect": "Dependencies", "description": "Consider adding dependencies between steps to clarify the sequence."},
        {"aspect": "Timeframes", "description": "Add estimated timeframes for each step to improve planning."},
        {"aspect": "Contingencies", "description": "Include alternative approaches or contingency plans for critical steps."}
    ]
    
    # Add focus area specific feedback if provided
    if "feasibility" in [area.lower() for area in focus_areas]:
        suggestions.append({"aspect": "Feasibility", "description": "Assess resource requirements for each step to ensure the plan is realistic."})
    if "completeness" in [area.lower() for area in focus_areas]:
        suggestions.append({"aspect": "Completeness", "description": "Verify that all necessary steps are included to achieve the goal."})
    
    # Generate summary based on review depth
    if review_depth.lower() == "quick":
        summary = f"Quick review of plan ({step_count} steps). Overall quality is {'good' if overall_rating > 0.7 else 'average' if overall_rating > 0.5 else 'needs improvement'}."
    elif review_depth.lower() == "comprehensive":
        summary = f"Comprehensive review of plan ({step_count} steps, {line_count} lines). The plan is {'well-structured and detailed' if overall_rating > 0.7 else 'adequate but could be improved' if overall_rating > 0.5 else 'in need of significant revision'}. Key areas for improvement include step detail, dependencies, and contingency planning."
    else:
        # Standard review
        summary = f"Review of plan ({step_count} steps). The plan is {'well-designed' if overall_rating > 0.7 else 'adequate' if overall_rating > 0.5 else 'in need of revision'} with {'sufficient' if step_count > 5 else 'limited'} detail."
    
    return {
        "summary": summary,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "overall_rating": overall_rating
    }
