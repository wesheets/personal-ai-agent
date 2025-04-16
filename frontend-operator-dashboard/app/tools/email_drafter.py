"""
Email Drafter Tool for the Personal AI Agent System.

This module provides functionality to draft, format, and optimize
email content for various purposes and audiences.
"""

import os
import json
import time
import random
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger("email_drafter")

def run(
    subject: str,
    purpose: str,
    recipient_type: str = "professional",
    tone: str = "formal",
    key_points: List[str] = None,
    sender_name: str = None,
    recipient_name: str = None,
    recipient_email: str = None,
    include_greeting: bool = True,
    include_signature: bool = True,
    signature_text: str = None,
    max_length: str = "medium",
    include_call_to_action: bool = True,
    call_to_action: str = None,
    format_as_html: bool = False,
    store_memory: bool = False,
    memory_manager = None,
    memory_tags: List[str] = ["email", "communication"],
    memory_scope: str = "agent"
) -> Dict[str, Any]:
    """
    Draft an email based on specified parameters.
    
    Args:
        subject: Email subject line
        purpose: Purpose of the email (e.g., introduction, follow-up, request, proposal)
        recipient_type: Type of recipient (professional, personal, customer, etc.)
        tone: Tone of the email (formal, friendly, persuasive, urgent, etc.)
        key_points: List of key points to include in the email
        sender_name: Name of the sender
        recipient_name: Name of the recipient
        recipient_email: Email address of the recipient
        include_greeting: Whether to include a greeting
        include_signature: Whether to include a signature
        signature_text: Custom signature text
        max_length: Maximum length of the email (short, medium, long)
        include_call_to_action: Whether to include a call to action
        call_to_action: Custom call to action text
        format_as_html: Whether to format the email as HTML
        store_memory: Whether to store the email in memory
        memory_manager: Memory manager instance for storing results
        memory_tags: Tags to apply to the memory entry
        memory_scope: Scope for the memory entry (agent or global)
        
    Returns:
        Dictionary containing the drafted email and related information
    """
    logger.info(f"Drafting email with subject: {subject}")
    
    try:
        # Validate inputs
        if not subject:
            raise ValueError("Email subject is required")
        
        if not purpose:
            raise ValueError("Email purpose is required")
        
        if max_length not in ["short", "medium", "long"]:
            raise ValueError(f"Invalid max_length: {max_length}. Supported values: short, medium, long")
        
        if tone not in ["formal", "friendly", "persuasive", "urgent", "apologetic", "appreciative", "neutral", "enthusiastic"]:
            logger.warning(f"Unusual tone specified: {tone}. Will attempt to adapt.")
        
        # Set default key points if not provided
        if key_points is None:
            key_points = []
        
        # Generate email content
        email_content = _generate_email_content(
            subject,
            purpose,
            recipient_type,
            tone,
            key_points,
            sender_name,
            recipient_name,
            include_greeting,
            include_signature,
            signature_text,
            max_length,
            include_call_to_action,
            call_to_action
        )
        
        # Format as HTML if requested
        if format_as_html:
            email_html = _format_as_html(
                email_content,
                subject,
                sender_name,
                recipient_name,
                recipient_email
            )
        else:
            email_html = None
        
        # Analyze the email
        email_analysis = _analyze_email(
            email_content,
            subject,
            purpose,
            tone,
            key_points
        )
        
        # Store in memory if requested
        if store_memory and memory_manager:
            try:
                # Create a memory entry with the email content
                memory_entry = {
                    "type": "email_draft",
                    "subject": subject,
                    "purpose": purpose,
                    "recipient_type": recipient_type,
                    "tone": tone,
                    "content_preview": email_content[:100] + ("..." if len(email_content) > 100 else ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                memory_manager.add_memory(
                    content=json.dumps(memory_entry),
                    scope=memory_scope,
                    tags=memory_tags + [f"purpose_{purpose}", f"tone_{tone}"]
                )
                
                logger.info(f"Stored email draft in memory with tags: {memory_tags}")
            except Exception as e:
                logger.error(f"Failed to store email draft in memory: {str(e)}")
        
        return {
            "success": True,
            "subject": subject,
            "content": email_content,
            "html": email_html,
            "analysis": email_analysis,
            "word_count": len(email_content.split()),
            "character_count": len(email_content)
        }
    except Exception as e:
        error_msg = f"Error drafting email: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "subject": subject
        }

def _generate_email_content(
    subject: str,
    purpose: str,
    recipient_type: str,
    tone: str,
    key_points: List[str],
    sender_name: Optional[str],
    recipient_name: Optional[str],
    include_greeting: bool,
    include_signature: bool,
    signature_text: Optional[str],
    max_length: str,
    include_call_to_action: bool,
    call_to_action: Optional[str]
) -> str:
    """
    Generate email content based on specified parameters.
    
    Args:
        subject: Email subject line
        purpose: Purpose of the email
        recipient_type: Type of recipient
        tone: Tone of the email
        key_points: List of key points to include
        sender_name: Name of the sender
        recipient_name: Name of the recipient
        include_greeting: Whether to include a greeting
        include_signature: Whether to include a signature
        signature_text: Custom signature text
        max_length: Maximum length of the email
        include_call_to_action: Whether to include a call to action
        call_to_action: Custom call to action text
        
    Returns:
        Generated email content
    """
    # Initialize email parts
    email_parts = []
    
    # Add greeting if requested
    if include_greeting:
        greeting = _generate_greeting(recipient_name, recipient_type, tone)
        email_parts.append(greeting)
    
    # Generate introduction based on purpose
    introduction = _generate_introduction(purpose, subject, tone)
    email_parts.append(introduction)
    
    # Generate body content based on key points
    body = _generate_body(purpose, key_points, tone, max_length)
    email_parts.append(body)
    
    # Add call to action if requested
    if include_call_to_action:
        action_text = _generate_call_to_action(purpose, call_to_action, tone)
        email_parts.append(action_text)
    
    # Generate closing
    closing = _generate_closing(purpose, tone)
    email_parts.append(closing)
    
    # Add signature if requested
    if include_signature:
        signature = _generate_signature(sender_name, signature_text, tone)
        email_parts.append(signature)
    
    # Combine all parts
    email_content = "\n\n".join(email_parts)
    
    return email_content

def _generate_greeting(
    recipient_name: Optional[str],
    recipient_type: str,
    tone: str
) -> str:
    """
    Generate an appropriate greeting for the email.
    
    Args:
        recipient_name: Name of the recipient
        recipient_type: Type of recipient
        tone: Tone of the email
        
    Returns:
        Greeting text
    """
    if recipient_name:
        if tone == "formal":
            return f"Dear {recipient_name},"
        elif tone == "friendly":
            return f"Hi {recipient_name},"
        elif tone == "enthusiastic":
            return f"Hello {recipient_name}!"
        else:
            return f"Hello {recipient_name},"
    else:
        if recipient_type == "professional" or tone == "formal":
            return "Dear Sir/Madam,"
        elif recipient_type == "team":
            return "Hello Team,"
        elif recipient_type == "customer":
            return "Dear Valued Customer,"
        elif tone == "friendly":
            return "Hi there,"
        else:
            return "Hello,"

def _generate_introduction(
    purpose: str,
    subject: str,
    tone: str
) -> str:
    """
    Generate an introduction paragraph based on the email purpose.
    
    Args:
        purpose: Purpose of the email
        subject: Email subject
        tone: Tone of the email
        
    Returns:
        Introduction paragraph
    """
    # Introductions based on purpose
    if purpose == "introduction":
        if tone == "formal":
            return f"I am writing to introduce myself and discuss {subject}. I hope this email finds you well."
        elif tone == "friendly":
            return f"I wanted to reach out and introduce myself regarding {subject}. I hope you're having a great day!"
        elif tone == "enthusiastic":
            return f"I'm excited to connect with you about {subject}! I've been looking forward to this opportunity."
        else:
            return f"I'm reaching out to introduce myself and discuss {subject}."
    
    elif purpose == "follow-up":
        if tone == "formal":
            return f"I am writing to follow up regarding our previous discussion about {subject}. I appreciate your time and consideration on this matter."
        elif tone == "friendly":
            return f"I wanted to check in with you about our conversation on {subject}. Thanks for your time on this!"
        elif tone == "urgent":
            return f"I'm following up urgently regarding {subject}. This requires your prompt attention."
        else:
            return f"I'm following up on our previous discussion about {subject}."
    
    elif purpose == "request":
        if tone == "formal":
            return f"I am writing to request your assistance regarding {subject}. Your expertise would be greatly appreciated in this matter."
        elif tone == "friendly":
            return f"I hope you're doing well! I'm reaching out because I could use your help with {subject}."
        elif tone == "urgent":
            return f"I urgently need your assistance with {subject}. This is a time-sensitive matter that requires immediate attention."
        else:
            return f"I'm writing to request your help with {subject}."
    
    elif purpose == "proposal":
        if tone == "formal":
            return f"I am pleased to present a proposal regarding {subject}. After careful consideration, I believe this will be beneficial for all parties involved."
        elif tone == "persuasive":
            return f"I'm excited to share a compelling proposal about {subject} that I believe will significantly benefit your organization."
        elif tone == "enthusiastic":
            return f"I have an exciting proposal about {subject} that I can't wait to share with you! I think you'll find this opportunity very promising."
        else:
            return f"I'd like to propose an idea regarding {subject} for your consideration."
    
    elif purpose == "thank you":
        if tone == "formal":
            return f"I am writing to express my sincere gratitude regarding {subject}. Your contribution has been invaluable."
        elif tone == "appreciative":
            return f"I wanted to take a moment to thank you for {subject}. Your support means a great deal to me."
        elif tone == "enthusiastic":
            return f"I can't thank you enough for {subject}! Your help has made such a positive impact."
        else:
            return f"Thank you so much for {subject}. I truly appreciate your assistance."
    
    elif purpose == "apology":
        if tone == "formal":
            return f"I am writing to extend my sincere apologies regarding {subject}. I understand the inconvenience this may have caused."
        elif tone == "apologetic":
            return f"I want to sincerely apologize for {subject}. I understand how this affected you, and I take full responsibility."
        else:
            return f"I'm very sorry about {subject}. I apologize for any inconvenience this has caused."
    
    elif purpose == "information":
        if tone == "formal":
            return f"I am writing to provide you with information regarding {subject}. Please find the details below for your review."
        elif tone == "friendly":
            return f"I wanted to share some information with you about {subject}. Here's what you need to know!"
        else:
            return f"I'm reaching out with some information about {subject} that I thought would be helpful for you."
    
    else:
        # Generic introduction for other purposes
        return f"I hope this email finds you well. I'm writing regarding {subject}."

def _generate_body(
    purpose: str,
    key_points: List[str],
    tone: str,
    max_length: str
) -> str:
    """
    Generate the body content of the email.
    
    Args:
        purpose: Purpose of the email
        key_points: List of key points to include
        tone: Tone of the email
        max_length: Maximum length of the email
        
    Returns:
        Body content
    """
    # Determine target paragraph count based on length
    if max_length == "short":
        target_paragraphs = 1
    elif max_length == "medium":
        target_paragraphs = 2
    else:  # long
        target_paragraphs = 3
    
    # If key points are provided, use them to structure the body
    if key_points:
        # For short emails, combine key points into a single paragraph
        if max_length == "short":
            points_text = ", ".join(key_points[:-1])
            if len(key_points) > 1:
                points_text += f", and {key_points[-1]}"
            else:
                points_text = key_points[0]
            
            return _format_paragraph(points_text, tone)
        
        # For medium and long emails, create a paragraph or bullet points
        else:
            if len(key_points) <= 3 or tone == "formal":
                # Create paragraphs for each key point
                paragraphs = []
                for point in key_points[:target_paragraphs]:
                    paragraphs.append(_format_paragraph(point, tone))
                return "\n\n".join(paragraphs)
            else:
                # Create bullet points for more than 3 key points
                intro = _format_paragraph("Here are the key points:", tone)
                bullets = []
                for point in key_points:
                    bullets.append(f"• {point}")
                return intro + "\n\n" + "\n".join(bullets)
    
    # If no key points are provided, generate generic content based on purpose
    else:
        paragraphs = []
        
        # Generate paragraphs based on purpose
        if purpose == "introduction":
            paragraphs.append(_get_introduction_paragraph(tone))
            if target_paragraphs > 1:
                paragraphs.append(_get_background_paragraph(tone))
            if target_paragraphs > 2:
                paragraphs.append(_get_value_proposition_paragraph(tone))
        
        elif purpose == "follow-up":
            paragraphs.append(_get_follow_up_paragraph(tone))
            if target_paragraphs > 1:
                paragraphs.append(_get_progress_paragraph(tone))
            if target_paragraphs > 2:
                paragraphs.append(_get_next_steps_paragraph(tone))
        
        elif purpose == "request":
            paragraphs.append(_get_request_paragraph(tone))
            if target_paragraphs > 1:
                paragraphs.append(_get_context_paragraph(tone))
            if target_paragraphs > 2:
                paragraphs.append(_get_appreciation_paragraph(tone))
        
        elif purpose == "proposal":
            paragraphs.append(_get_proposal_paragraph(tone))
            if target_paragraphs > 1:
                paragraphs.append(_get_benefits_paragraph(tone))
            if target_paragraphs > 2:
                paragraphs.append(_get_implementation_paragraph(tone))
        
        elif purpose == "thank you":
            paragraphs.append(_get_gratitude_paragraph(tone))
            if target_paragraphs > 1:
                paragraphs.append(_get_impact_paragraph(tone))
            if target_paragraphs > 2:
                paragraphs.append(_get_future_paragraph(tone))
        
        elif purpose == "apology":
            paragraphs.append(_get_apology_paragraph(tone))
            if target_paragraphs > 1:
                paragraphs.append(_get_explanation_paragraph(tone))
            if target_paragraphs > 2:
                paragraphs.append(_get_resolution_paragraph(tone))
        
        elif purpose == "information":
            paragraphs.append(_get_information_paragraph(tone))
            if target_paragraphs > 1:
                paragraphs.append(_get_details_paragraph(tone))
            if target_paragraphs > 2:
                paragraphs.append(_get_additional_info_paragraph(tone))
        
        else:
            # Generic paragraphs for other purposes
            for i in range(target_paragraphs):
                paragraphs.append(_get_generic_paragraph(i + 1, tone))
        
        return "\n\n".join(paragraphs)

def _format_paragraph(content: str, tone: str) -> str:
    """
    Format a paragraph based on the specified tone.
    
    Args:
        content: Paragraph content
        tone: Tone of the email
        
    Returns:
        Formatted paragraph
    """
    # Add tone-specific modifiers
    if tone == "formal":
        # No modification needed, formal is the default
        return content
    elif tone == "friendly":
        # Add a friendly phrase if not already present
        friendly_phrases = ["I hope", "I think", "I believe", "I'm glad"]
        if not any(phrase in content for phrase in friendly_phrases):
            return f"I think {content[0].lower()}{content[1:]}"
        return content
    elif tone == "persuasive":
        # Add persuasive elements if not already present
        persuasive_phrases = ["certainly", "definitely", "absolutely", "without doubt"]
        if not any(phrase in content.lower() for phrase in persuasive_phrases):
            return f"I'm certain that {content[0].lower()}{content[1:]}"
        return content
    elif tone == "urgent":
        # Add urgency if not already present
        urgent_phrases = ["urgent", "immediately", "as soon as possible", "promptly"]
        if not any(phrase in content.lower() for phrase in urgent_phrases):
            return f"Urgently, {content}"
        return content
    elif tone == "enthusiastic":
        # Add enthusiasm if not already present
        if "!" not in content:
            return f"{content.rstrip('.')}!"
        return content
    else:
        # No modification for other tones
        return content

def _generate_call_to_action(
    purpose: str,
    custom_cta: Optional[str],
    tone: str
) -> str:
    """
    Generate a call to action based on the email purpose.
    
    Args:
        purpose: Purpose of the email
        custom_cta: Custom call to action text
        tone: Tone of the email
        
    Returns:
        Call to action text
    """
    if custom_cta:
        return custom_cta
    
    # Generate CTA based on purpose and tone
    if purpose == "introduction":
        if tone == "formal":
            return "I would appreciate the opportunity to discuss this matter further at your convenience."
        elif tone == "friendly":
            return "I'd love to chat more about this. Would you have time for a quick call this week?"
        elif tone == "persuasive":
            return "Let's schedule a meeting to explore how we can work together effectively."
        else:
            return "Please let me know if you'd like to discuss this further."
    
    elif purpose == "follow-up":
        if tone == "formal":
            return "I look forward to your response regarding the next steps."
        elif tone == "urgent":
            return "Please provide your feedback by the end of the day so we can proceed accordingly."
        else:
            return "Could you please let me know your thoughts on this by the end of the week?"
    
    elif purpose == "request":
        if tone == "formal":
            return "I would greatly appreciate your assistance in this matter at your earliest convenience."
        elif tone == "urgent":
            return "Please respond with your decision by [DATE] as this is a time-sensitive matter."
        else:
            return "Could you please help with this when you get a chance?"
    
    elif purpose == "proposal":
        if tone == "formal":
            return "I would welcome the opportunity to discuss this proposal in more detail at a time that suits you."
        elif tone == "persuasive":
            return "Let's schedule a meeting next week to discuss how we can implement this proposal and start seeing results."
        else:
            return "Please review this proposal and let me know your thoughts."
    
    elif purpose == "information":
        if tone == "formal":
            return "Please do not hesitate to contact me should you require any clarification or additional information."
        else:
            return "Let me know if you need any more information about this."
    
    else:
        # Generic CTA for other purposes
        return "Please let me know if you have any questions or concerns."

def _generate_closing(purpose: str, tone: str) -> str:
    """
    Generate an appropriate closing for the email.
    
    Args:
        purpose: Purpose of the email
        tone: Tone of the email
        
    Returns:
        Closing text
    """
    if tone == "formal":
        return "Thank you for your attention to this matter."
    elif tone == "friendly":
        return "Thanks so much for your time!"
    elif tone == "appreciative":
        return "I truly appreciate your support and consideration."
    elif tone == "urgent":
        return "Thank you for your prompt attention to this matter."
    elif tone == "enthusiastic":
        return "I'm really looking forward to your response!"
    elif purpose == "thank you":
        return "Once again, thank you for your support."
    elif purpose == "apology":
        return "I appreciate your understanding in this matter."
    else:
        return "Thank you for your time and consideration."

def _generate_signature(
    sender_name: Optional[str],
    signature_text: Optional[str],
    tone: str
) -> str:
    """
    Generate an email signature.
    
    Args:
        sender_name: Name of the sender
        signature_text: Custom signature text
        tone: Tone of the email
        
    Returns:
        Signature text
    """
    # Use custom signature if provided
    if signature_text:
        return signature_text
    
    # Generate signature based on tone and sender name
    if tone == "formal":
        closing = "Sincerely,"
    elif tone == "friendly" or tone == "enthusiastic":
        closing = "Best,"
    elif tone == "appreciative":
        closing = "With gratitude,"
    else:
        closing = "Regards,"
    
    if sender_name:
        return f"{closing}\n{sender_name}"
    else:
        return closing

def _format_as_html(
    content: str,
    subject: str,
    sender_name: Optional[str],
    recipient_name: Optional[str],
    recipient_email: Optional[str]
) -> str:
    """
    Format the email content as HTML.
    
    Args:
        content: Email content
        subject: Email subject
        sender_name: Name of the sender
        recipient_name: Name of the recipient
        recipient_email: Email address of the recipient
        
    Returns:
        HTML formatted email
    """
    # Split content into paragraphs
    paragraphs = content.split("\n\n")
    
    # Convert paragraphs to HTML
    html_paragraphs = []
    for paragraph in paragraphs:
        if paragraph.startswith("•"):
            # Convert bullet points to HTML list
            bullet_points = paragraph.split("\n")
            html_list = "<ul>\n"
            for point in bullet_points:
                if point.strip():
                    html_list += f"  <li>{point.strip('• ')}</li>\n"
            html_list += "</ul>"
            html_paragraphs.append(html_list)
        else:
            # Regular paragraph
            html_paragraphs.append(f"<p>{paragraph}</p>")
    
    # Combine HTML paragraphs
    html_body = "\n".join(html_paragraphs)
    
    # Create HTML email
    html_email = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{subject}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
    p {{ margin-bottom: 16px; }}
    ul {{ margin-bottom: 16px; }}
    .signature {{ margin-top: 30px; color: #666; border-top: 1px solid #eee; padding-top: 10px; }}
  </style>
</head>
<body>
  {html_body}
</body>
</html>"""
    
    return html_email

def _analyze_email(
    content: str,
    subject: str,
    purpose: str,
    tone: str,
    key_points: List[str]
) -> Dict[str, Any]:
    """
    Analyze the email content for quality and effectiveness.
    
    Args:
        content: Email content
        subject: Email subject
        purpose: Purpose of the email
        tone: Tone of the email
        key_points: List of key points
        
    Returns:
        Analysis results
    """
    # Calculate basic metrics
    word_count = len(content.split())
    character_count = len(content)
    sentence_count = len([s for s in content.split('.') if s.strip()])
    average_word_length = sum(len(word) for word in content.split()) / max(1, word_count)
    
    # Analyze readability (simplified Flesch-Kincaid)
    if sentence_count > 0:
        words_per_sentence = word_count / sentence_count
        readability_score = 206.835 - (1.015 * words_per_sentence) - (84.6 * (average_word_length / 5))
        readability_score = max(0, min(100, readability_score))
    else:
        words_per_sentence = 0
        readability_score = 50  # Default middle value
    
    # Determine readability level
    if readability_score >= 90:
        readability_level = "Very Easy"
    elif readability_score >= 80:
        readability_level = "Easy"
    elif readability_score >= 70:
        readability_level = "Fairly Easy"
    elif readability_score >= 60:
        readability_level = "Standard"
    elif readability_score >= 50:
        readability_level = "Fairly Difficult"
    elif readability_score >= 30:
        readability_level = "Difficult"
    else:
        readability_level = "Very Difficult"
    
    # Check if all key points are included
    key_points_included = []
    for point in key_points:
        # Check if the key point or similar text is in the content
        words = set(point.lower().split())
        significant_words = [w for w in words if len(w) > 3]  # Only consider significant words
        
        if len(significant_words) > 0:
            # Calculate percentage of significant words found in content
            content_lower = content.lower()
            words_found = sum(1 for word in significant_words if word in content_lower)
            percentage = words_found / len(significant_words)
            
            key_points_included.append({
                "point": point,
                "included": percentage > 0.5,  # Consider included if more than 50% of words are found
                "match_percentage": round(percentage * 100)
            })
    
    # Analyze tone consistency
    tone_words = _get_tone_words(tone)
    tone_word_count = sum(1 for word in tone_words if word.lower() in content.lower())
    tone_consistency = min(100, (tone_word_count * 100) // max(1, len(tone_words)))
    
    # Determine email length category
    if word_count < 75:
        length_category = "Very Short"
    elif word_count < 150:
        length_category = "Short"
    elif word_count < 300:
        length_category = "Medium"
    elif word_count < 500:
        length_category = "Long"
    else:
        length_category = "Very Long"
    
    return {
        "metrics": {
            "word_count": word_count,
            "character_count": character_count,
            "sentence_count": sentence_count,
            "average_word_length": round(average_word_length, 1),
            "words_per_sentence": round(words_per_sentence, 1),
            "length_category": length_category
        },
        "readability": {
            "score": round(readability_score, 1),
            "level": readability_level
        },
        "content_analysis": {
            "key_points_included": key_points_included,
            "tone_consistency": tone_consistency,
            "has_greeting": content.split("\n\n")[0].endswith(","),
            "has_signature": "Sincerely" in content or "Regards" in content or "Best" in content
        },
        "suggestions": _generate_suggestions(
            word_count,
            readability_score,
            tone_consistency,
            key_points_included
        )
    }

def _get_tone_words(tone: str) -> List[str]:
    """
    Get words associated with a specific tone.
    
    Args:
        tone: Tone of the email
        
    Returns:
        List of words associated with the tone
    """
    tone_word_map = {
        "formal": ["respectfully", "accordingly", "regarding", "hereby", "therefore", "furthermore", "thus", "consequently", "nevertheless", "pursuant"],
        "friendly": ["thanks", "great", "hope", "glad", "wonderful", "appreciate", "looking forward", "chat", "touch base", "catch up"],
        "persuasive": ["opportunity", "benefit", "advantage", "value", "recommend", "suggest", "consider", "effective", "proven", "results"],
        "urgent": ["immediate", "urgent", "promptly", "as soon as possible", "critical", "time-sensitive", "deadline", "priority", "crucial", "expedite"],
        "apologetic": ["apologize", "sorry", "regret", "mistake", "inconvenience", "unfortunate", "amends", "rectify", "resolve", "understand"],
        "appreciative": ["thank", "grateful", "appreciate", "valued", "recognition", "acknowledge", "indebted", "pleased", "honored", "thankful"],
        "neutral": ["inform", "update", "provide", "note", "observe", "state", "indicate", "mention", "report", "advise"],
        "enthusiastic": ["excited", "thrilled", "delighted", "fantastic", "amazing", "wonderful", "excellent", "outstanding", "incredible", "brilliant"]
    }
    
    return tone_word_map.get(tone, ["please", "thank you", "regards"])

def _generate_suggestions(
    word_count: int,
    readability_score: float,
    tone_consistency: int,
    key_points_included: List[Dict[str, Any]]
) -> List[str]:
    """
    Generate suggestions for improving the email.
    
    Args:
        word_count: Number of words in the email
        readability_score: Readability score
        tone_consistency: Tone consistency percentage
        key_points_included: Analysis of key points inclusion
        
    Returns:
        List of suggestions
    """
    suggestions = []
    
    # Length suggestions
    if word_count < 50:
        suggestions.append("Consider adding more detail to make your message clearer.")
    elif word_count > 500:
        suggestions.append("The email is quite long. Consider condensing it for better readability.")
    
    # Readability suggestions
    if readability_score < 50:
        suggestions.append("The text may be difficult to read. Consider using shorter sentences and simpler words.")
    
    # Tone suggestions
    if tone_consistency < 70:
        suggestions.append("The tone could be more consistent throughout the email.")
    
    # Key points suggestions
    missing_points = [item["point"] for item in key_points_included if not item["included"]]
    if missing_points:
        if len(missing_points) == 1:
            suggestions.append(f"Consider including this key point: {missing_points[0]}")
        else:
            suggestions.append(f"Consider including these key points: {', '.join(missing_points)}")
    
    # Add generic suggestions if none specific
    if not suggestions:
        suggestions.append("Proofread for any spelling or grammar errors before sending.")
        suggestions.append("Consider adding a specific deadline or date if you're requesting action.")
    
    return suggestions

# Helper functions for generating paragraphs based on purpose

def _get_introduction_paragraph(tone: str) -> str:
    """Generate a paragraph for introducing yourself."""
    if tone == "formal":
        return "I am [Your Name/Position] at [Your Organization]. Our organization specializes in [brief description of services/products]."
    elif tone == "friendly":
        return "I thought I'd take a moment to introduce myself. I'm [Your Name] and I work with [Your Organization], where we help clients with [brief description of services/products]."
    elif tone == "enthusiastic":
        return "I'm thrilled to introduce myself! I'm [Your Name] from [Your Organization], and we're passionate about [brief description of services/products]!"
    else:
        return "My name is [Your Name] from [Your Organization]. We specialize in [brief description of services/products]."

def _get_background_paragraph(tone: str) -> str:
    """Generate a paragraph about background information."""
    if tone == "formal":
        return "Our organization has extensive experience in this field, having worked with numerous clients across various industries. We have developed a comprehensive understanding of the challenges and opportunities in this domain."
    elif tone == "friendly":
        return "I've been working in this field for several years now, and I've had the chance to work on some really interesting projects. I've seen firsthand the kinds of challenges that companies like yours often face."
    else:
        return "We have significant experience in this area, having worked with many clients to address similar challenges. Our approach is based on proven methodologies and best practices."

def _get_value_proposition_paragraph(tone: str) -> str:
    """Generate a paragraph about value proposition."""
    if tone == "formal":
        return "We believe our expertise could be particularly valuable for your organization. Our approach has consistently delivered measurable results for our clients, including improved efficiency, reduced costs, and enhanced performance."
    elif tone == "persuasive":
        return "What sets us apart is our unique approach to solving these challenges. We've developed a methodology that consistently delivers 30% better results than traditional approaches, saving our clients both time and resources."
    else:
        return "I believe we could add significant value to your organization. Our approach has helped similar clients achieve their goals more efficiently and effectively."

def _get_follow_up_paragraph(tone: str) -> str:
    """Generate a paragraph for following up."""
    if tone == "formal":
        return "I am following up regarding our previous discussion. As mentioned, we discussed [brief recap of previous conversation] and agreed to reconnect about next steps."
    elif tone == "urgent":
        return "I'm following up urgently on our previous conversation about [topic]. This matter requires immediate attention as the deadline is approaching rapidly."
    else:
        return "I wanted to follow up on our conversation about [topic]. We discussed some interesting possibilities, and I'm eager to continue the discussion."

def _get_progress_paragraph(tone: str) -> str:
    """Generate a paragraph about progress made."""
    if tone == "formal":
        return "Since our last communication, we have made significant progress on the matters we discussed. Specifically, we have [description of progress made], which positions us well for the next phase."
    elif tone == "friendly":
        return "I've been working on the items we talked about, and I'm happy to report that we've made good progress! So far, we've [description of progress made], and things are coming along nicely."
    else:
        return "We've made progress on the items we discussed. Specifically, we've [description of progress made], which sets us up well for the next steps."

def _get_next_steps_paragraph(tone: str) -> str:
    """Generate a paragraph about next steps."""
    if tone == "formal":
        return "Moving forward, I propose the following next steps: [list of proposed actions]. This approach will ensure we maintain momentum and achieve our objectives within the established timeframe."
    elif tone == "urgent":
        return "We need to take immediate action on the following items: [list of urgent actions]. These steps are critical to meet our upcoming deadline and avoid potential complications."
    else:
        return "Here's what I think we should do next: [list of proposed actions]. This will help us keep moving forward and stay on track with our timeline."

def _get_request_paragraph(tone: str) -> str:
    """Generate a paragraph for making a request."""
    if tone == "formal":
        return "I am writing to request [specific request]. This would greatly assist our efforts to [purpose of request]."
    elif tone == "urgent":
        return "I urgently need [specific request]. This is time-sensitive because [reason for urgency], and we need to address this by [deadline]."
    else:
        return "I'm hoping you can help me with [specific request]. This would really help us with [purpose of request]."

def _get_context_paragraph(tone: str) -> str:
    """Generate a paragraph providing context for a request."""
    if tone == "formal":
        return "The context for this request is as follows: [background information]. Understanding this background will clarify the importance and relevance of this request to our overall objectives."
    elif tone == "persuasive":
        return "Let me explain why this is so important: [compelling context]. This directly impacts our ability to [benefit or outcome], which is a key priority for us this quarter."
    else:
        return "Here's some background on why I'm asking: [context information]. This will help you understand how your assistance fits into the bigger picture."

def _get_appreciation_paragraph(tone: str) -> str:
    """Generate a paragraph expressing appreciation."""
    if tone == "formal":
        return "I greatly appreciate your consideration of this request. Your expertise in this area is highly regarded, and your assistance would be invaluable to our efforts."
    elif tone == "appreciative":
        return "I can't tell you how much I would appreciate your help with this. Your knowledge in this area is exceptional, and it would make a significant difference to have your input."
    else:
        return "Thanks so much for considering this request. I really value your expertise, and your help would make a big difference."

def _get_proposal_paragraph(tone: str) -> str:
    """Generate a paragraph for making a proposal."""
    if tone == "formal":
        return "I would like to propose [description of proposal]. This approach has been carefully considered to address the specific requirements and objectives we have identified."
    elif tone == "persuasive":
        return "I'm excited to propose a solution that I believe will transform how you approach [relevant area]: [description of proposal]. This innovative approach directly addresses the challenges you've been facing."
    else:
        return "I'd like to propose the following: [description of proposal]. I think this approach would work well based on what we've discussed."

def _get_benefits_paragraph(tone: str) -> str:
    """Generate a paragraph about benefits."""
    if tone == "formal":
        return "The benefits of this proposal include: [list of benefits]. These advantages align directly with your stated objectives and would contribute significantly to your desired outcomes."
    elif tone == "persuasive":
        return "Here's why this approach will deliver exceptional results: [compelling benefits]. Our clients who have implemented similar solutions have seen [specific results], often exceeding their initial expectations."
    else:
        return "This approach offers several key benefits: [list of benefits]. These advantages would help you achieve your goals more effectively."

def _get_implementation_paragraph(tone: str) -> str:
    """Generate a paragraph about implementation."""
    if tone == "formal":
        return "Regarding implementation, we propose a phased approach: [description of implementation plan]. This methodology minimizes disruption while ensuring systematic progress toward the desired outcome."
    elif tone == "friendly":
        return "When it comes to putting this into action, we'd keep things simple and straightforward: [implementation plan]. We'd work closely with your team every step of the way to make sure everything goes smoothly."
    else:
        return "For implementation, we recommend the following approach: [implementation plan]. This would allow for a smooth transition and effective adoption."

def _get_gratitude_paragraph(tone: str) -> str:
    """Generate a paragraph expressing gratitude."""
    if tone == "formal":
        return "I would like to express my sincere gratitude for [reason for thanks]. Your contribution has been invaluable and is greatly appreciated."
    elif tone == "appreciative":
        return "I cannot thank you enough for [reason for thanks]. Your support has meant so much to me, and I am truly grateful for your generosity and kindness."
    else:
        return "Thank you so much for [reason for thanks]. I really appreciate your help and support."

def _get_impact_paragraph(tone: str) -> str:
    """Generate a paragraph about the impact of someone's help."""
    if tone == "formal":
        return "Your assistance has had a significant positive impact. Specifically, it has enabled us to [description of impact], which has substantially advanced our objectives."
    elif tone == "appreciative":
        return "I want you to know just how much of a difference your help has made. Because of you, we were able to [description of impact], which has been absolutely transformative for us."
    else:
        return "Your help has made a real difference. It allowed us to [description of impact], which has been really important for our progress."

def _get_future_paragraph(tone: str) -> str:
    """Generate a paragraph about future collaboration."""
    if tone == "formal":
        return "I look forward to the opportunity to collaborate further in the future. Your expertise and support would be most welcome as we continue to address challenges and pursue opportunities in this area."
    elif tone == "friendly":
        return "I hope we'll have the chance to work together again soon! It's been a pleasure, and I think there are lots of other interesting projects where we could collaborate."
    else:
        return "I hope we can work together again in the future. Your input has been valuable, and I'd welcome the chance to collaborate on other projects."

def _get_apology_paragraph(tone: str) -> str:
    """Generate a paragraph for apologizing."""
    if tone == "formal":
        return "I would like to extend my sincere apologies for [reason for apology]. I understand this has caused inconvenience, and I take full responsibility for this situation."
    elif tone == "apologetic":
        return "I am truly sorry for [reason for apology]. I understand how this affected you, and I feel terrible about the inconvenience and frustration it has caused."
    else:
        return "I'm really sorry about [reason for apology]. I know this has been inconvenient for you, and I apologize for the problems it's caused."

def _get_explanation_paragraph(tone: str) -> str:
    """Generate a paragraph explaining a situation."""
    if tone == "formal":
        return "I would like to provide context regarding this situation. [Explanation of what happened]. While this explains the circumstances, it does not excuse the inconvenience caused."
    elif tone == "apologetic":
        return "I want to explain what happened, though I know explanations don't undo the inconvenience. [Explanation of what happened]. I should have handled this differently, and I regret not doing so."
    else:
        return "Let me explain what happened: [explanation of what happened]. I understand this doesn't change the inconvenience you experienced, but I wanted you to know the full situation."

def _get_resolution_paragraph(tone: str) -> str:
    """Generate a paragraph about resolving an issue."""
    if tone == "formal":
        return "To address this matter, I propose the following resolution: [description of resolution]. Additionally, we have implemented measures to prevent similar occurrences in the future, including [preventive measures]."
    elif tone == "apologetic":
        return "I'm committed to making this right. Here's what I'll do: [description of resolution]. I've also taken steps to make sure this doesn't happen again by [preventive measures]."
    else:
        return "Here's how I'd like to resolve this: [description of resolution]. I've also put some changes in place to prevent this from happening again."

def _get_information_paragraph(tone: str) -> str:
    """Generate a paragraph providing information."""
    if tone == "formal":
        return "I would like to provide you with the following information regarding [topic]: [key information]. This data has been carefully verified for accuracy and relevance."
    elif tone == "friendly":
        return "I wanted to share some information with you about [topic]. Here's what you need to know: [key information]. I thought you'd find this helpful!"
    else:
        return "Here's the information you requested about [topic]: [key information]. Let me know if you need any clarification."

def _get_details_paragraph(tone: str) -> str:
    """Generate a paragraph with additional details."""
    if tone == "formal":
        return "For additional context, please note the following details: [specific details]. These elements are particularly relevant to understanding the complete picture."
    elif tone == "friendly":
        return "I thought you might also find these details useful: [specific details]. They give a bit more background that helps explain the situation better."
    else:
        return "Here are some additional details that might be helpful: [specific details]. These points provide important context."

def _get_additional_info_paragraph(tone: str) -> str:
    """Generate a paragraph with supplementary information."""
    if tone == "formal":
        return "Furthermore, you may find the following supplementary information valuable: [additional information]. This provides a comprehensive overview of all relevant aspects of the matter."
    elif tone == "friendly":
        return "One more thing that might interest you: [additional information]. I thought this was a pretty interesting aspect that's worth knowing about."
    else:
        return "Also, you might want to know that [additional information]. This relates to what we discussed and could be useful for your consideration."

def _get_generic_paragraph(paragraph_number: int, tone: str) -> str:
    """Generate a generic paragraph based on position and tone."""
    if paragraph_number == 1:
        if tone == "formal":
            return "I am writing to address the matter at hand with the attention it deserves. The situation requires careful consideration of all relevant factors to ensure an appropriate response."
        elif tone == "friendly":
            return "I wanted to reach out about this because I think it's something we should discuss. There are a few aspects to consider that I think would be helpful to talk through."
        else:
            return "I'm writing about the current situation and wanted to share some thoughts. There are several important factors to consider as we move forward."
    elif paragraph_number == 2:
        if tone == "formal":
            return "Upon careful analysis, several key considerations emerge. These factors must be weighed appropriately to determine the optimal course of action that aligns with our objectives and constraints."
        elif tone == "friendly":
            return "When I think about this more, a few important points come to mind. I believe these considerations will help us figure out the best way to proceed given what we're trying to accomplish."
        else:
            return "After considering the situation, I've identified several important factors. These points should help guide our decision-making process as we determine next steps."
    else:
        if tone == "formal":
            return "Moving forward, a strategic approach is recommended. This would entail systematic implementation of the identified measures while maintaining flexibility to adapt as circumstances evolve."
        elif tone == "friendly":
            return "As we think about next steps, I think we should take a practical approach. We can put these ideas into action while staying flexible enough to adjust if we need to as things develop."
        else:
            return "For next steps, I recommend we proceed strategically. We should implement these measures systematically while remaining adaptable to changing circumstances."
