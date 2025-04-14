"""
Marketing & Growth Tools

This module provides tools for marketing and growth-related tasks including email campaign creation,
blog content generation, social media calendar planning, meme generation, landing page hero writing,
and tagline creation.
"""

import random
import datetime
from typing import Dict, List, Any, Optional

# Import the registry for tool registration
from ...registry import register_tool


def copy_email_campaign(product_name: str, audience: str = "customers", num_emails: int = 3) -> Dict[str, Any]:
    """
    Generate an email campaign sequence with multiple steps.
    
    Args:
        product_name: The name of the product or service
        audience: Target audience (customers, prospects, etc.)
        num_emails: Number of emails in the sequence
        
    Returns:
        A dictionary containing the email campaign and metadata
    """
    # Define audience-specific templates
    audience_templates = {
        "customers": {
            "tone": "friendly and appreciative",
            "focus": "product updates, usage tips, and loyalty rewards",
            "subject_prefix": "Your",
            "greeting": "Hi there,",
            "signature": "The [Company] Team"
        },
        "prospects": {
            "tone": "informative and persuasive",
            "focus": "benefits, social proof, and limited-time offers",
            "subject_prefix": "Discover",
            "greeting": "Hello,",
            "signature": "[Your Name]\n[Company]"
        },
        "churned": {
            "tone": "understanding and inviting",
            "focus": "improvements, new features, and win-back offers",
            "subject_prefix": "We've missed you -",
            "greeting": "Hi there,",
            "signature": "[Your Name]\nCustomer Success Manager"
        }
    }
    
    # Use default if audience not found
    template = audience_templates.get(audience.lower(), audience_templates["customers"])
    
    # Generate campaign structure
    campaign = {
        "name": f"{product_name} {audience.capitalize()} Campaign",
        "audience": audience,
        "emails": []
    }
    
    # Email types based on sequence position
    email_types = ["welcome", "value", "offer"]
    if num_emails > 3:
        email_types.extend(["testimonial", "case_study", "feature_highlight"] * 2)
    
    # Ensure we have enough email types
    while len(email_types) < num_emails:
        email_types.append(random.choice(["value", "offer", "testimonial"]))
    
    # Select email types for this campaign
    selected_types = email_types[:num_emails]
    
    # Generate each email in the sequence
    for i, email_type in enumerate(selected_types):
        # Calculate send date (every 3 days)
        send_date = (datetime.datetime.now() + datetime.timedelta(days=i*3)).strftime("%Y-%m-%d")
        
        # Generate email content based on type
        email = {
            "sequence_position": i + 1,
            "type": email_type,
            "send_date": send_date
        }
        
        if email_type == "welcome":
            email["subject"] = f"Welcome to {product_name}!"
            email["content"] = f"""
{template['greeting']}

Thank you for choosing {product_name}! We're thrilled to have you on board.

Here's what you can expect from us:

1. **Getting Started**: We've put together some resources to help you get the most out of {product_name}:
   - [Quick Start Guide](#)
   - [Video Tutorial](#)
   - [FAQ](#)

2. **Support When You Need It**: Our team is here to help! Reply to this email or contact us at support@example.com.

3. **What's Next**: Over the next few weeks, we'll share tips, best practices, and insider knowledge to help you succeed with {product_name}.

We're excited to be part of your journey!

Best regards,
{template['signature']}
"""
        
        elif email_type == "value":
            email["subject"] = f"{template['subject_prefix']} {product_name} Tip: Boost Your Results"
            email["content"] = f"""
{template['greeting']}

I wanted to share a quick tip to help you get even more value from {product_name}.

**Did you know?** Our users who [specific action] see [specific result] on average.

Here's how to do it in 3 simple steps:

1. Navigate to [feature] in your dashboard
2. Configure [specific setting]
3. Activate [specific option]

That's it! This small change can make a big difference in your results.

Want to learn more? Check out our [detailed guide](#) or [schedule a quick call](#) with our team.

{template['signature']}

P.S. We'd love to hear how {product_name} is working for you. Hit reply and let us know!
"""
        
        elif email_type == "offer":
            email["subject"] = f"Special Offer: Upgrade Your {product_name} Experience"
            email["content"] = f"""
{template['greeting']}

I'm reaching out with an exclusive offer for our valued {audience}.

**For a limited time**, you can [upgrade/access/unlock] [premium feature/service] at [discount/special terms].

This opportunity is available until [date], and includes:

- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

[CTA Button: Claim Your Offer]

Not ready to upgrade? No problem! Your current plan continues unchanged, and we're always here if you have questions.

{template['signature']}

P.S. This offer is exclusive to our [audience] and expires on [date].
"""
        
        elif email_type == "testimonial":
            email["subject"] = f"See How Others Are Succeeding with {product_name}"
            email["content"] = f"""
{template['greeting']}

Success stories from our community can provide valuable insights and inspiration.

Meet [Customer Name], who achieved [specific result] after using {product_name} for just [timeframe]:

> "{product_name} transformed how we [specific process]. We've seen [specific metric] increase by [percentage], and our team has saved [time/resources] each [day/week/month]."
>
> — [Customer Name], [Position] at [Company]

Want to learn how [Customer Name] did it? We've put together a [case study/guide/video] showing exactly how they configured {product_name} to achieve these results.

[CTA Button: See The Full Story]

Could your success story be next? We'd love to feature you!

{template['signature']}
"""
        
        elif email_type == "case_study":
            email["subject"] = f"Case Study: How [Company] Achieved [Result] with {product_name}"
            email["content"] = f"""
{template['greeting']}

Today, I'm sharing an in-depth look at how one of our clients transformed their [department/process] using {product_name}.

**The Challenge:**
[Company] was struggling with [specific problem]. They needed a solution that would [specific requirements].

**The Solution:**
After implementing {product_name}, [Company] was able to:

1. [Specific improvement]
2. [Specific improvement]
3. [Specific improvement]

**The Results:**
- [Specific metric] increased by [percentage]
- [Specific metric] reduced by [percentage]
- ROI achieved within [timeframe]

[CTA Button: Read the Full Case Study]

Could {product_name} deliver similar results for you? Let's discuss your specific needs.

{template['signature']}
"""
        
        elif email_type == "feature_highlight":
            email["subject"] = f"New in {product_name}: Introducing [Feature Name]"
            email["content"] = f"""
{template['greeting']}

We're excited to announce the release of [Feature Name], a powerful new addition to {product_name} designed to help you [benefit].

**What is [Feature Name]?**
[Brief description of the feature and its purpose]

**Key Benefits:**
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

**How to Get Started:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

[CTA Button: Try [Feature Name] Now]

We've created a quick [video/guide] to help you make the most of this new feature.

As always, we'd love to hear your feedback!

{template['signature']}
"""
        
        campaign["emails"].append(email)
    
    # Add campaign metrics
    campaign["metrics"] = {
        "estimated_open_rate": f"{random.randint(15, 40)}%",
        "estimated_click_rate": f"{random.randint(2, 15)}%",
        "recommended_send_time": f"{random.choice(['Morning', 'Afternoon', 'Evening'])} ({random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday'])})",
        "a_b_test_recommendation": random.choice([
            "Test different subject lines",
            "Test different CTAs",
            "Test different send times",
            "Test different email lengths"
        ])
    }
    
    return campaign


def content_blog_generate(topic: str, tone: str = "professional", word_count: int = 1500) -> Dict[str, Any]:
    """
    Generate long-form blog content on a given topic.
    
    Args:
        topic: The blog topic
        tone: The tone of the content (professional, conversational, etc.)
        word_count: Target word count for the blog
        
    Returns:
        A dictionary containing the blog content and metadata
    """
    # Define tone templates
    tone_templates = {
        "professional": {
            "style": "formal and authoritative",
            "paragraph_length": "medium",
            "vocabulary": "industry-specific terminology with clear explanations",
            "structure": "logical and methodical"
        },
        "conversational": {
            "style": "friendly and approachable",
            "paragraph_length": "short to medium",
            "vocabulary": "everyday language with occasional colloquialisms",
            "structure": "flowing and natural"
        },
        "educational": {
            "style": "clear and instructive",
            "paragraph_length": "medium",
            "vocabulary": "precise with definitions of technical terms",
            "structure": "progressive building of concepts"
        },
        "persuasive": {
            "style": "compelling and convincing",
            "paragraph_length": "varied for emphasis",
            "vocabulary": "emotionally resonant and benefit-focused",
            "structure": "problem-solution-benefit"
        }
    }
    
    # Use default if tone not found
    template = tone_templates.get(tone.lower(), tone_templates["professional"])
    
    # Generate title options
    title_options = [
        f"The Ultimate Guide to {topic}",
        f"{topic}: What You Need to Know in 2025",
        f"How {topic} is Transforming the Industry",
        f"10 Essential Insights About {topic}",
        f"Understanding {topic}: A Comprehensive Overview"
    ]
    
    # Select title
    title = random.choice(title_options)
    
    # Generate blog structure
    structure = {
        "introduction": f"Introduction to {topic} and why it matters",
        "sections": [
            f"Background and context of {topic}",
            f"Key components of {topic}",
            f"Benefits and advantages of {topic}",
            f"Challenges and considerations with {topic}",
            f"Best practices for implementing {topic}",
            f"Future trends in {topic}"
        ],
        "conclusion": f"Summary of key points about {topic} and next steps"
    }
    
    # Generate meta description
    meta_description = f"Explore everything you need to know about {topic} in this comprehensive guide. Learn about the benefits, challenges, and best practices for implementation."
    
    # Generate keywords
    keywords = [topic]
    topic_parts = topic.split()
    for part in topic_parts:
        keywords.append(part)
    keywords.extend([
        f"{topic} guide",
        f"{topic} best practices",
        f"{topic} implementation",
        f"{topic} benefits",
        f"{topic} trends"
    ])
    
    # Generate the actual blog content
    content = f"""# {title}

## Introduction

{topic} has become increasingly important in today's rapidly evolving landscape. As organizations and individuals navigate the complexities of modern challenges, understanding the nuances of {topic} can provide a significant advantage.

This comprehensive guide explores the fundamental aspects of {topic}, its practical applications, and how you can leverage it effectively. Whether you're new to {topic} or looking to deepen your existing knowledge, this article offers valuable insights for all experience levels.

## Background and Context

### The Evolution of {topic}

{topic} didn't emerge overnight. Its development has been shaped by various factors including technological advancements, changing market demands, and evolving best practices.

Initially, {topic} was primarily used for [specific early application]. However, as understanding grew and technologies advanced, its applications expanded significantly. Today, {topic} encompasses a broad range of approaches and methodologies that can be tailored to specific needs and contexts.

### Why {topic} Matters Now

Several factors have contributed to the growing importance of {topic}:

1. **Increasing complexity** in business and technological environments
2. **Rising expectations** from stakeholders and customers
3. **Competitive pressures** driving the need for innovation and efficiency
4. **Regulatory changes** affecting how organizations operate

Organizations that effectively implement {topic} can gain a competitive edge, improve operational efficiency, and better meet the needs of their stakeholders.

## Key Components of {topic}

Understanding the fundamental components of {topic} is essential for successful implementation. These components work together to create a comprehensive framework that can be adapted to various contexts.

### Component 1: [First Key Element]

This foundational element focuses on [description of first component]. It provides the structure necessary for [specific benefit or function].

Key aspects include:
- [Specific aspect]
- [Specific aspect]
- [Specific aspect]

### Component 2: [Second Key Element]

Building on the foundation, this component addresses [description of second component]. It enables [specific benefit or function] through systematic application of [relevant principles or methods].

### Component 3: [Third Key Element]

This component integrates [description of third component], allowing for [specific benefit or function]. When properly implemented, it significantly enhances the overall effectiveness of {topic}.

## Benefits and Advantages

Implementing {topic} effectively can yield numerous benefits for organizations and individuals alike.

### Operational Benefits

- **Improved efficiency** through streamlined processes and reduced redundancy
- **Enhanced quality** of outputs and deliverables
- **Greater consistency** across operations and teams
- **Reduced costs** through optimization and waste reduction

### Strategic Benefits

- **Increased agility** and responsiveness to market changes
- **Better decision-making** based on improved insights and information
- **Enhanced innovation** capabilities
- **Stronger competitive positioning** in the marketplace

### Case Example: [Organization Name]

[Organization Name] implemented {topic} in [year] and saw remarkable results. Within [timeframe], they experienced:

- [Specific measurable result]
- [Specific measurable result]
- [Specific measurable result]

Their approach focused on [specific strategy], demonstrating the potential impact of well-executed {topic} initiatives.

## Challenges and Considerations

Despite its benefits, implementing {topic} is not without challenges. Being aware of these potential obstacles can help you navigate them effectively.

### Common Challenges

1. **Resistance to change** from stakeholders accustomed to established methods
2. **Resource constraints** including time, budget, and expertise
3. **Integration difficulties** with existing systems and processes
4. **Measurement complexities** in quantifying impact and ROI

### Mitigation Strategies

To address these challenges, consider the following approaches:

- **Stakeholder engagement**: Involve key stakeholders early and throughout the process
- **Phased implementation**: Break the initiative into manageable phases with clear milestones
- **Training and support**: Provide comprehensive training and ongoing support
- **Clear metrics**: Establish clear success metrics aligned with organizational objectives

## Best Practices for Implementation

Successful implementation of {topic} relies on following established best practices tailored to your specific context.

### Planning and Preparation

- **Conduct a thorough assessment** of current state and needs
- **Establish clear objectives** aligned with organizational goals
- **Develop a detailed implementation roadmap** with milestones and responsibilities
- **Secure necessary resources** including budget, personnel, and tools

### Execution

- **Start with pilot projects** to demonstrate value and refine approach
- **Maintain regular communication** with all stakeholders
- **Document processes and decisions** for future reference
- **Monitor progress** against established metrics

### Sustainability

- **Establish feedback mechanisms** for continuous improvement
- **Provide ongoing training** as needs evolve
- **Celebrate successes** to maintain momentum
- **Regularly review and update** your approach based on outcomes and changing needs

## Future Trends in {topic}

As {topic} continues to evolve, several emerging trends are shaping its future direction.

### Trend 1: [Emerging Trend]

[Description of first trend and its potential impact]

### Trend 2: [Emerging Trend]

[Description of second trend and its potential impact]

### Trend 3: [Emerging Trend]

[Description of third trend and its potential impact]

Organizations that stay abreast of these trends and adapt their approaches accordingly will be better positioned to leverage {topic} for competitive advantage.

## Conclusion

{topic} represents a powerful approach for addressing contemporary challenges and opportunities. By understanding its key components, benefits, and best practices for implementation, you can harness its potential to drive meaningful improvements.

Remember that successful implementation requires thoughtful planning, stakeholder engagement, and a commitment to continuous improvement. The journey may present challenges, but the potential rewards—enhanced efficiency, improved outcomes, and stronger competitive positioning—make it worthwhile.

As you embark on or continue your {topic} journey, focus on aligning your approach with your specific context and objectives. By doing so, you'll be well-positioned to realize the full benefits of {topic} now and in the future.

## Additional Resources

- [Resource 1]
- [Resource 2]
- [Resource 3]

*This article was last updated on [current date].*
"""
    
    # Calculate actual word count
    actual_word_count = len(content.split())
    
    # Generate reading time (average reading speed: 200-250 words per minute)
    reading_time_minutes = round(actual_word_count / 225)
    
    return {
        "title": title,
        "meta_description": meta_description,
        "keywords": keywords,
        "tone": tone,
        "tone_characteristics": template,
        "target_word_count": word_count,
        "actual_word_count": actual_word_count,
        "reading_time": f"{reading_time_minutes} min read",
        "structure": structure,
        "content": content,
        "suggested_images": [
            f"Header image representing {topic}",
            f"Diagram showing components of {topic}",
            f"Infographic highlighting benefits of {topic}",
            f"Chart showing trends in {topic}"
        ]
    }


def social_calendar_create(brand_name: str, platforms: List[str] = None, days: int = 30) -> Dict[str, Any]:
    """
    Generate a social media content calendar for a specified period.
    
    Args:
        brand_name: The name of the brand
        platforms: List of social media platforms to include
        days: Number of days to plan for
        
    Returns:
        A dictionary containing the social media calendar and metadata
    """
    # Default platforms if none provided
    if not platforms:
        platforms = ["Twitter", "LinkedIn", "Instagram", "Facebook"]
    
    # Define content types for each platform
    platform_content_types = {
        "Twitter": [
            "Industry news share",
            "Quick tip",
            "Poll",
            "Question to audience",
            "Behind the scenes",
            "Product feature highlight",
            "Customer spotlight",
            "Inspirational quote",
            "Statistics/data point",
            "Thread on key topic"
        ],
        "LinkedIn": [
            "Industry insight",
            "Company news",
            "Case study",
            "Employee spotlight",
            "Leadership article",
            "Industry report summary",
            "Event announcement",
            "Thought leadership",
            "Product update",
            "Career opportunity"
        ],
        "Instagram": [
            "Product showcase",
            "User-generated content",
            "Behind the scenes",
            "Team spotlight",
            "Inspirational quote",
            "Tutorial/How-to",
            "Day in the life",
            "Customer spotlight",
            "Product in action",
            "Story takeover"
        ],
        "Facebook": [
            "Company update",
            "Industry news",
            "Customer success story",
            "Event promotion",
            "Community spotlight",
            "Poll/Question",
            "Product announcement",
            "Video content",
            "Blog post share",
            "Contest/Giveaway"
        ],
        "TikTok": [
            "Trend participation",
            "Quick tutorial",
            "Behind the scenes",
            "Product demo",
            "Day in the life",
            "Customer testimonial",
            "Challenge",
            "FAQ answer",
            "Industry myth debunk",
            "Team spotlight"
        ],
        "Pinterest": [
            "Infographic",
            "How-to guide",
            "Product showcase",
            "Inspirational imagery",
            "Checklist",
            "Tutorial",
            "Seasonal content",
            "Industry tips",
            "Before and after",
            "Collection showcase"
        ],
        "YouTube": [
            "Product tutorial",
            "Industry expert interview",
            "Behind the scenes",
            "Customer testimonial",
            "Product review",
            "How-to guide",
            "Industry news roundup",
            "Q&A session",
            "Case study",
            "Event highlights"
        ]
    }
    
    # Define content themes
    content_themes = [
        "Product Education",
        "Industry Insights",
        "Customer Success",
        "Company Culture",
        "Thought Leadership",
        "Community Engagement",
        "Product Updates",
        "Tips & Tricks",
        "Industry News",
        "Events & Webinars"
    ]
    
    # Generate calendar
    calendar = {
        "brand": brand_name,
        "platforms": platforms,
        "period": f"{days} days",
        "start_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.datetime.now() + datetime.timedelta(days=days-1)).strftime("%Y-%m-%d"),
        "posts": []
    }
    
    # Generate posts for each day
    current_date = datetime.datetime.now()
    for day in range(days):
        post_date = current_date + datetime.timedelta(days=day)
        date_str = post_date.strftime("%Y-%m-%d")
        day_name = post_date.strftime("%A")
        
        # Determine how many posts for this day (more on weekdays, fewer on weekends)
        if day_name in ["Saturday", "Sunday"]:
            num_posts = min(len(platforms), 2)  # Fewer posts on weekends
        else:
            num_posts = min(len(platforms), 3)  # More posts on weekdays
        
        # Select platforms for this day
        day_platforms = random.sample(platforms, num_posts)
        
        # Select theme for the day
        day_theme = random.choice(content_themes)
        
        # Generate posts for each selected platform
        for platform in day_platforms:
            # Select content type for this platform
            content_type = random.choice(platform_content_types.get(platform, platform_content_types["Twitter"]))
            
            # Generate post content based on platform, content type, and theme
            post = {
                "date": date_str,
                "day": day_name,
                "platform": platform,
                "content_type": content_type,
                "theme": day_theme,
                "content": generate_post_content(brand_name, platform, content_type, day_theme),
                "hashtags": generate_hashtags(brand_name, platform, content_type, day_theme),
                "media_suggestion": generate_media_suggestion(platform, content_type)
            }
            
            calendar["posts"].append(post)
    
    # Add calendar metrics and recommendations
    calendar["metrics"] = {
        "total_posts": len(calendar["posts"]),
        "posts_per_platform": {platform: len([p for p in calendar["posts"] if p["platform"] == platform]) for platform in platforms},
        "theme_distribution": {theme: len([p for p in calendar["posts"] if p["theme"] == theme]) for theme in content_themes if any(p["theme"] == theme for p in calendar["posts"])}
    }
    
    calendar["recommendations"] = [
        "Schedule posts during peak engagement times for each platform",
        "Monitor performance and adjust content types based on engagement",
        "Maintain a consistent brand voice across all platforms",
        "Engage with comments and messages promptly",
        "Repurpose high-performing content across different platforms"
    ]
    
    return calendar


def generate_post_content(brand_name: str, platform: str, content_type: str, theme: str) -> str:
    """Helper function to generate post content based on parameters."""
    
    # Platform-specific content templates
    if platform == "Twitter":
        if content_type == "Industry news share":
            return f"Just in: [Industry news headline]. What does this mean for #[industry]? Our take: [brief opinion]. #[industry]news #{brand_name}"
        
        elif content_type == "Quick tip":
            return f"💡 Quick Tip: [Actionable advice related to {theme}]. This simple change can make a big difference! #[industry]tips #{brand_name}"
        
        elif content_type == "Poll":
            return f"We want to hear from you! What's your biggest challenge with [topic related to {theme}]?\n\n⚪ [Option 1]\n⚪ [Option 2]\n⚪ [Option 3]\n⚪ [Option 4]\n\n#{brand_name} #[industry]poll"
        
        else:
            return f"[Content related to {content_type} and {theme}] #{brand_name} #[relevant hashtag]"
    
    elif platform == "LinkedIn":
        if content_type == "Industry insight":
            return f"""Our analysis of recent trends in [industry]:

1️⃣ [Key insight 1]
2️⃣ [Key insight 2]
3️⃣ [Key insight 3]

What are you seeing in your organization? Share your experiences below.

#[Industry] #{brand_name} #[RelevantTopic]"""
        
        elif content_type == "Case study":
            return f"""📊 Case Study: How [Client Company] achieved [specific result] with {brand_name}

Challenge: [Brief description of client's challenge]

Solution: [How our product/service helped]

Results:
✅ [Specific metric improvement]
✅ [Specific metric improvement]
✅ [Specific metric improvement]

Read the full case study: [Link]

#[Industry] #{brand_name} #CaseStudy"""
        
        else:
            return f"""[Attention-grabbing headline related to {content_type} and {theme}]

[First paragraph with key information]

[Second paragraph with supporting details]

[Call to action]

#[Industry] #{brand_name} #[RelevantTopic]"""
    
    elif platform == "Instagram":
        if content_type == "Behind the scenes":
            return f"""📸 Behind the scenes at {brand_name}! 

[Description of what's happening in the image/video]

This is how we [relevant process/activity]. Our team is passionate about [relevant value proposition].

#behindthescenes #{brand_name.lower()} #[industry] #[relevant hashtag]"""
        
        elif content_type == "Product showcase":
            return f"""Introducing [product/feature name] - designed to [key benefit].

✨ [Feature 1]
✨ [Feature 2]
✨ [Feature 3]

Available now! Link in bio to learn more.

#{brand_name.lower()} #[product category] #[industry]"""
        
        else:
            return f"""[Engaging caption related to {content_type} and {theme}]

[Additional context or story]

[Call to action]

#{brand_name.lower()} #[relevant hashtag] #[relevant hashtag]"""
    
    else:  # Default format for other platforms
        return f"[Content related to {content_type} and {theme} formatted appropriately for {platform}] #{brand_name} #[relevant hashtag]"


def generate_hashtags(brand_name: str, platform: str, content_type: str, theme: str) -> List[str]:
    """Helper function to generate hashtags based on parameters."""
    
    # Base hashtags that work across platforms
    base_hashtags = [
        brand_name.lower().replace(" ", ""),
        theme.lower().replace(" ", ""),
        content_type.lower().replace(" ", "").replace("/", "")
    ]
    
    # Platform-specific hashtag counts and styles
    if platform == "Twitter":
        # Twitter: fewer hashtags, more specific
        additional_hashtags = ["business", "tips", "strategy"]
        max_hashtags = 3
    
    elif platform == "Instagram":
        # Instagram: many hashtags, mix of popular and niche
        additional_hashtags = ["instabusiness", "growth", "success", "entrepreneur", 
                              "business", "marketing", "digital", "strategy", "innovation"]
        max_hashtags = 10
    
    elif platform == "LinkedIn":
        # LinkedIn: professional, industry-focused
        additional_hashtags = ["business", "professional", "leadership", "innovation", "strategy"]
        max_hashtags = 5
    
    else:
        # Default for other platforms
        additional_hashtags = ["business", "marketing", "digital"]
        max_hashtags = 4
    
    # Select random additional hashtags
    selected_additional = random.sample(additional_hashtags, min(max_hashtags - len(base_hashtags), len(additional_hashtags)))
    
    # Combine and return
    return base_hashtags + selected_additional


def generate_media_suggestion(platform: str, content_type: str) -> Dict[str, Any]:
    """Helper function to generate media suggestions based on parameters."""
    
    # Define media types by platform
    platform_media = {
        "Twitter": ["Image", "GIF", "Short video", "Infographic", "Poll", "Text only"],
        "LinkedIn": ["Image", "Document", "Article", "Video", "Infographic", "Carousel"],
        "Instagram": ["Image", "Carousel", "Reels", "Stories", "IGTV"],
        "Facebook": ["Image", "Video", "Carousel", "Live video", "Event", "Link preview"],
        "TikTok": ["Short video", "Duet", "Stitch", "Tutorial video"],
        "Pinterest": ["Pin image", "Idea pin", "Infographic", "Product pin"],
        "YouTube": ["Video", "Short", "Live stream", "Premiere"]
    }
    
    # Get media types for this platform
    media_types = platform_media.get(platform, ["Image", "Video"])
    
    # Select appropriate media type based on content type
    if "video" in content_type.lower():
        media_type = "Video" if "Video" in media_types else random.choice(media_types)
    elif "infographic" in content_type.lower():
        media_type = "Infographic" if "Infographic" in media_types else random.choice(media_types)
    elif "poll" in content_type.lower():
        media_type = "Poll" if "Poll" in media_types else random.choice(media_types)
    else:
        media_type = random.choice(media_types)
    
    # Generate media suggestion
    suggestion = {
        "type": media_type,
        "description": f"[Description of suggested {media_type.lower()} content]",
        "dimensions": get_media_dimensions(platform, media_type)
    }
    
    return suggestion


def get_media_dimensions(platform: str, media_type: str) -> str:
    """Helper function to get recommended media dimensions."""
    
    dimensions = {
        "Twitter": {
            "Image": "1200 x 675 pixels",
            "Video": "1280 x 720 pixels"
        },
        "LinkedIn": {
            "Image": "1200 x 627 pixels",
            "Video": "1920 x 1080 pixels"
        },
        "Instagram": {
            "Image": "1080 x 1080 pixels (square)",
            "Carousel": "1080 x 1080 pixels (square)",
            "Reels": "1080 x 1920 pixels (9:16)"
        },
        "Facebook": {
            "Image": "1200 x 630 pixels",
            "Video": "1280 x 720 pixels"
        }
    }
    
    # Get platform dimensions or default
    platform_dims = dimensions.get(platform, {"Image": "1200 x 1200 pixels", "Video": "1280 x 720 pixels"})
    
    # Get media type dimensions or default
    return platform_dims.get(media_type, "Standard dimensions for platform")


def meme_generate(topic: str, style: str = "humorous", format: str = "image_with_text") -> Dict[str, Any]:
    """
    Generate a meme concept based on the provided topic and style.
    
    Args:
        topic: The topic or subject of the meme
        style: The style of humor (humorous, satirical, etc.)
        format: The meme format (image_with_text, comparison, etc.)
        
    Returns:
        A dictionary containing the meme concept and metadata
    """
    # Define meme templates by format
    meme_templates = {
        "image_with_text": [
            "Distracted Boyfriend",
            "Drake Hotline Bling",
            "Two Buttons",
            "Change My Mind",
            "Expanding Brain",
            "Woman Yelling at Cat",
            "Surprised Pikachu",
            "This is Fine"
        ],
        "comparison": [
            "Expectation vs. Reality",
            "Then vs. Now",
            "What People Think I Do vs. What I Actually Do",
            "Upgrade Button",
            "Expectations vs. Reality"
        ],
        "reaction": [
            "Confused Math Lady",
            "Blinking Guy",
            "Disaster Girl",
            "Hide the Pain Harold",
            "Roll Safe Think About It"
        ],
        "dialogue": [
            "Is This a Pigeon?",
            "Always Has Been",
            "Gru's Plan",
            "Batman Slapping Robin"
        ]
    }
    
    # Define humor styles
    humor_styles = {
        "humorous": {
            "tone": "light and playful",
            "approach": "relatable situations and mild exaggeration",
            "audience": "general audience"
        },
        "satirical": {
            "tone": "ironic and critical",
            "approach": "exaggeration to highlight absurdity",
            "audience": "those familiar with the topic"
        },
        "absurdist": {
            "tone": "random and unexpected",
            "approach": "non-sequiturs and surreal elements",
            "audience": "niche audience with specific humor preferences"
        },
        "meta": {
            "tone": "self-referential",
            "approach": "jokes about memes themselves",
            "audience": "internet-savvy audience familiar with meme culture"
        }
    }
    
    # Get templates for the selected format or default
    templates = meme_templates.get(format, meme_templates["image_with_text"])
    
    # Select a template
    template = random.choice(templates)
    
    # Get humor style details or default
    style_details = humor_styles.get(style, humor_styles["humorous"])
    
    # Generate meme concept based on format
    if format == "image_with_text":
        if template == "Drake Hotline Bling":
            concept = {
                "template": template,
                "panel_1_text": f"[Traditional/conventional approach to {topic}]",
                "panel_2_text": f"[Clever/innovative approach to {topic}]"
            }
        
        elif template == "Expanding Brain":
            concept = {
                "template": template,
                "panel_1_text": f"[Basic approach to {topic}]",
                "panel_2_text": f"[Improved approach to {topic}]",
                "panel_3_text": f"[Advanced approach to {topic}]",
                "panel_4_text": f"[Absurdly complex or silly approach to {topic}]"
            }
        
        elif template == "Woman Yelling at Cat":
            concept = {
                "template": template,
                "woman_text": f"[Someone advocating for conventional {topic} approach]",
                "cat_text": f"[Me with my unconventional but effective {topic} solution]"
            }
        
        else:
            concept = {
                "template": template,
                "top_text": f"[Humorous setup about {topic}]",
                "bottom_text": f"[Unexpected punchline about {topic}]"
            }
    
    elif format == "comparison":
        concept = {
            "template": template,
            "left_panel": f"[Idealized version of {topic}]",
            "right_panel": f"[Realistic version of {topic}]"
        }
    
    elif format == "reaction":
        concept = {
            "template": template,
            "context": f"[Specific situation related to {topic}]",
            "reaction": f"[Humorous reaction to the situation]"
        }
    
    elif format == "dialogue":
        if template == "Gru's Plan":
            concept = {
                "template": template,
                "panel_1_text": f"[First step in a plan related to {topic}]",
                "panel_2_text": f"[Second step in the plan]",
                "panel_3_text": f"[Unexpected negative outcome]",
                "panel_4_text": f"[Same text as panel 3, with Gru's realization]"
            }
        else:
            concept = {
                "template": template,
                "character_1_text": f"[Statement about {topic}]",
                "character_2_text": f"[Humorous contradiction or response]"
            }
    
    else:
        concept = {
            "template": "Custom",
            "description": f"[Custom meme concept about {topic}]"
        }
    
    # Generate visual description
    visual_description = f"Meme using the '{template}' template with text relating to {topic} in a {style} style."
    
    # Generate usage recommendations
    usage_recommendations = [
        f"Share on social media platforms where your audience discusses {topic}",
        "Consider your audience's familiarity with this meme template",
        f"Use as part of a larger {topic}-related campaign",
        "Test with a small audience before wider distribution"
    ]
    
    return {
        "topic": topic,
        "style": style,
        "style_details": style_details,
        "format": format,
        "template": template,
        "concept": concept,
        "visual_description": visual_description,
        "usage_recommendations": usage_recommendations,
        "potential_platforms": ["Twitter", "Instagram", "Facebook", "Reddit", "LinkedIn"]
    }


def copy_tagline(brand_name: str, industry: str, tone: str = "professional") -> Dict[str, Any]:
    """
    Generate a punchy brand statement or tagline.
    
    Args:
        brand_name: The name of the brand
        industry: The industry or sector
        tone: The tone of the tagline (professional, bold, etc.)
        
    Returns:
        A dictionary containing tagline options and metadata
    """
    # Define tone characteristics
    tone_characteristics = {
        "professional": {
            "style": "clear, confident, and trustworthy",
            "vocabulary": "industry-appropriate with emphasis on reliability",
            "structure": "straightforward and direct"
        },
        "bold": {
            "style": "assertive, distinctive, and memorable",
            "vocabulary": "strong, impactful words with emotional resonance",
            "structure": "often short, sometimes using unexpected phrasing"
        },
        "innovative": {
            "style": "forward-thinking, fresh, and dynamic",
            "vocabulary": "terms related to progress, future, and transformation",
            "structure": "may use wordplay or novel constructions"
        },
        "friendly": {
            "style": "approachable, warm, and conversational",
            "vocabulary": "everyday language with positive emotional appeal",
            "structure": "inviting and inclusive"
        },
        "luxury": {
            "style": "sophisticated, exclusive, and refined",
            "vocabulary": "elegant terms suggesting quality and prestige",
            "structure": "often understated with emphasis on excellence"
        }
    }
    
    # Get tone details or default to professional
    tone_details = tone_characteristics.get(tone, tone_characteristics["professional"])
    
    # Define industry-specific themes
    industry_themes = {
        "technology": ["innovation", "future", "solution", "transformation", "efficiency"],
        "finance": ["security", "growth", "stability", "prosperity", "confidence"],
        "healthcare": ["wellbeing", "care", "vitality", "support", "improvement"],
        "education": ["knowledge", "growth", "potential", "future", "development"],
        "retail": ["experience", "quality", "selection", "satisfaction", "value"],
        "food": ["taste", "quality", "experience", "tradition", "satisfaction"],
        "travel": ["adventure", "discovery", "experience", "escape", "journey"],
        "real estate": ["home", "future", "investment", "community", "lifestyle"],
        "marketing": ["impact", "results", "strategy", "visibility", "growth"],
        "consulting": ["expertise", "results", "insight", "transformation", "partnership"]
    }
    
    # Get industry themes or use generic themes
    themes = industry_themes.get(industry.lower(), ["quality", "innovation", "service", "excellence", "solution"])
    
    # Generate tagline structures based on tone
    if tone == "professional":
        structures = [
            f"[Industry] excellence, delivered.",
            f"Your partner in [industry] success.",
            f"Trusted [industry] solutions since [year].",
            f"Setting the standard in [industry].",
            f"[Industry] solutions for the modern world."
        ]
    
    elif tone == "bold":
        structures = [
            f"Revolutionizing [industry].",
            f"[Industry], reimagined.",
            f"Break the [industry] boundaries.",
            f"Challenge [industry] conventions.",
            f"Boldly advancing [industry]."
        ]
    
    elif tone == "innovative":
        structures = [
            f"The future of [industry] is here.",
            f"Redefining [industry] for tomorrow.",
            f"[Industry] innovation unleashed.",
            f"Tomorrow's [industry] solutions, today.",
            f"Pioneering the next generation of [industry]."
        ]
    
    elif tone == "friendly":
        structures = [
            f"[Industry] made simple.",
            f"Your [industry] journey starts here.",
            f"We make [industry] feel like home.",
            f"[Industry] with a personal touch.",
            f"[Industry] that puts you first."
        ]
    
    elif tone == "luxury":
        structures = [
            f"[Industry] excellence, redefined.",
            f"The art of [industry].",
            f"[Industry] without compromise.",
            f"Exceptional [industry] experiences.",
            f"The pinnacle of [industry]."
        ]
    
    else:
        structures = [
            f"[Brand] - [industry] solutions that work.",
            f"Your [industry] partner.",
            f"Better [industry] starts here.",
            f"[Industry] made better.",
            f"The [industry] experts."
        ]
    
    # Generate taglines
    taglines = []
    
    # Structure-based taglines
    for structure in structures:
        tagline = structure.replace("[industry]", industry.lower())
        taglines.append(tagline)
    
    # Theme-based taglines
    for theme in themes:
        if tone == "professional":
            taglines.append(f"Professional {theme} for your {industry} needs.")
            taglines.append(f"Delivering {theme} in {industry}.")
        
        elif tone == "bold":
            taglines.append(f"Unleashing {theme} in {industry}.")
            taglines.append(f"{theme.capitalize()}. Redefined.")
        
        elif tone == "innovative":
            taglines.append(f"Innovating {industry} through {theme}.")
            taglines.append(f"Reimagining {theme} for the future of {industry}.")
        
        elif tone == "friendly":
            taglines.append(f"{theme.capitalize()} you can count on.")
            taglines.append(f"Your partner in {theme}.")
        
        elif tone == "luxury":
            taglines.append(f"The essence of {theme}.")
            taglines.append(f"Exceptional {theme}. Always.")
    
    # Brand-specific taglines
    brand_taglines = [
        f"{brand_name}. {random.choice(themes).capitalize()} redefined.",
        f"{brand_name}: Where {industry} meets {random.choice(themes)}.",
        f"{random.choice(themes).capitalize()} is in our DNA.",
        f"With {brand_name}, expect more.",
        f"{brand_name}: The {industry} {random.choice(themes)} experts."
    ]
    taglines.extend(brand_taglines)
    
    # Remove duplicates and limit to 10 options
    unique_taglines = list(set(taglines))
    final_taglines = random.sample(unique_taglines, min(10, len(unique_taglines)))
    
    # Sort by length (shortest first)
    final_taglines.sort(key=len)
    
    return {
        "brand_name": brand_name,
        "industry": industry,
        "tone": tone,
        "tone_characteristics": tone_details,
        "themes": themes,
        "taglines": final_taglines,
        "recommendations": {
            "shortest": final_taglines[0],
            "most_memorable": random.choice(final_taglines[1:3]),
            "most_professional": next((t for t in final_taglines if "professional" in t.lower() or "excellence" in t.lower()), final_taglines[-1])
        }
    }


def landing_hero_write(product_name: str, value_prop: str, industry: str, cta: str = "Get Started") -> Dict[str, Any]:
    """
    Generate homepage headline and subheader content.
    
    Args:
        product_name: The name of the product
        value_prop: The core value proposition
        industry: The industry or sector
        cta: The call-to-action text
        
    Returns:
        A dictionary containing landing page hero content and metadata
    """
    # Define industry-specific pain points and aspirations
    industry_specifics = {
        "technology": {
            "pain_points": ["complexity", "inefficiency", "security risks", "outdated systems", "integration challenges"],
            "aspirations": ["innovation", "efficiency", "scalability", "competitive advantage", "digital transformation"],
            "audience": ["IT professionals", "developers", "CTOs", "technology leaders", "digital teams"]
        },
        "finance": {
            "pain_points": ["risk management", "compliance burden", "operational inefficiency", "data security", "customer retention"],
            "aspirations": ["growth", "security", "compliance", "customer trust", "operational excellence"],
            "audience": ["financial advisors", "bankers", "CFOs", "compliance officers", "investors"]
        },
        "healthcare": {
            "pain_points": ["administrative burden", "patient experience", "compliance", "data management", "staff burnout"],
            "aspirations": ["patient outcomes", "operational efficiency", "regulatory compliance", "staff satisfaction", "innovation"],
            "audience": ["healthcare providers", "administrators", "clinicians", "medical staff", "practice managers"]
        },
        "education": {
            "pain_points": ["engagement", "personalization", "resource constraints", "assessment challenges", "administrative burden"],
            "aspirations": ["student success", "teaching excellence", "innovation", "accessibility", "community building"],
            "audience": ["educators", "administrators", "students", "parents", "educational technologists"]
        },
        "marketing": {
            "pain_points": ["ROI measurement", "channel fragmentation", "content creation", "audience targeting", "campaign management"],
            "aspirations": ["brand growth", "engagement", "conversion", "customer loyalty", "data-driven decisions"],
            "audience": ["marketers", "brand managers", "CMOs", "content creators", "digital strategists"]
        },
        "ecommerce": {
            "pain_points": ["cart abandonment", "customer acquisition costs", "inventory management", "fulfillment challenges", "returns"],
            "aspirations": ["conversion", "customer loyalty", "operational efficiency", "growth", "competitive advantage"],
            "audience": ["online retailers", "ecommerce managers", "store owners", "fulfillment teams", "digital merchants"]
        }
    }
    
    # Get industry specifics or use generic
    industry_data = industry_specifics.get(industry.lower(), {
        "pain_points": ["inefficiency", "complexity", "competition", "resource constraints", "customer demands"],
        "aspirations": ["growth", "efficiency", "innovation", "customer satisfaction", "competitive advantage"],
        "audience": ["professionals", "managers", "executives", "teams", "specialists"]
    })
    
    # Select pain points and aspirations to focus on
    pain_point = random.choice(industry_data["pain_points"])
    aspiration = random.choice(industry_data["aspirations"])
    audience = random.choice(industry_data["audience"])
    
    # Generate headline variations
    headlines = [
        # Benefit-focused headlines
        f"Transform Your {industry.capitalize()} with {product_name}",
        f"Achieve {aspiration.capitalize()} in {industry.capitalize()} with {product_name}",
        f"{value_prop} with {product_name}",
        
        # Problem-solution headlines
        f"Eliminate {pain_point.capitalize()} in Your {industry.capitalize()} Business",
        f"Say Goodbye to {industry.capitalize()} {pain_point.capitalize()}",
        f"Solving {industry.capitalize()}'s Biggest {pain_point.capitalize()} Challenge",
        
        # Question headlines
        f"Ready to Transform Your {industry.capitalize()} {aspiration.capitalize()}?",
        f"What if Your {industry.capitalize()} Business Could {value_prop}?",
        f"Are {pain_point.capitalize()} Issues Holding Your {industry.capitalize()} Back?",
        
        # Statement headlines
        f"The {industry.capitalize()} Platform Built for {audience.capitalize()}",
        f"{product_name}: {industry.capitalize()} {aspiration.capitalize()} Made Simple",
        f"The Future of {industry.capitalize()} Starts with {product_name}"
    ]
    
    # Generate subheader variations
    subheaders = [
        # Elaboration on value proposition
        f"{product_name} helps {audience} {value_prop.lower()} through innovative solutions designed specifically for the {industry} industry.",
        f"Our platform enables {audience} to overcome {pain_point} and achieve {aspiration}, setting new standards in {industry}.",
        f"Purpose-built for {industry} professionals, {product_name} delivers the tools you need to {value_prop.lower()}.",
        
        # Feature-benefit focused
        f"Featuring advanced {industry}-specific tools that help you tackle {pain_point} while driving {aspiration} across your organization.",
        f"Combining powerful analytics, intuitive workflows, and industry expertise to help {audience} excel in today's competitive {industry} landscape.",
        f"Our comprehensive solution addresses the unique challenges of {industry}, empowering your team to focus on what matters most.",
        
        # Social proof oriented
        f"Join thousands of {industry} professionals who have transformed their approach to {aspiration} with our innovative platform.",
        f"Trusted by leading {industry} organizations to solve their most pressing {pain_point} challenges and drive meaningful results.",
        f"See why {audience} across the globe choose {product_name} to revolutionize their {industry} operations and outcomes.",
        
        # Action oriented
        f"Start eliminating {pain_point} today while building a foundation for sustainable {aspiration} in your {industry} business.",
        f"Take the first step toward transforming your {industry} approach and achieving unprecedented results.",
        f"Discover how our tailored solutions can address your specific {industry} challenges and help you reach your goals faster."
    ]
    
    # Generate CTA variations
    cta_variations = [
        cta,
        f"Try {product_name} Free",
        f"Start Your {aspiration.capitalize()} Journey",
        f"Solve {pain_point.capitalize()} Now",
        f"See {product_name} in Action",
        f"Request a Demo",
        f"Join Leading {industry.capitalize()} Businesses"
    ]
    
    # Select final content
    selected_headline = random.choice(headlines)
    selected_subheader = random.choice(subheaders)
    selected_cta = random.choice(cta_variations)
    
    # Generate alternative versions
    headline_alternatives = random.sample([h for h in headlines if h != selected_headline], min(3, len(headlines) - 1))
    subheader_alternatives = random.sample([s for s in subheaders if s != selected_subheader], min(3, len(subheaders) - 1))
    
    # Generate visual suggestions
    visual_suggestions = [
        f"Hero image showing {audience} achieving {aspiration} in a {industry} setting",
        f"Abstract graphic representing the solution to {pain_point} challenges",
        f"Split screen showing {industry} before/after using {product_name}",
        f"Animated illustration of the key {product_name} features most relevant to {industry}",
        f"Video background showing {product_name} in action in a {industry} environment"
    ]
    
    return {
        "product_name": product_name,
        "industry": industry,
        "value_proposition": value_prop,
        "target_audience": audience,
        "primary_content": {
            "headline": selected_headline,
            "subheader": selected_subheader,
            "cta_text": selected_cta,
            "cta_url": "#",  # Placeholder URL
            "recommended_visual": random.choice(visual_suggestions)
        },
        "alternatives": {
            "headlines": headline_alternatives,
            "subheaders": subheader_alternatives,
            "cta_variations": [c for c in cta_variations if c != selected_cta][:3]
        },
        "testing_recommendations": [
            f"A/B test the primary headline against '{headline_alternatives[0]}'",
            "Test different visual elements to see which resonates best with your audience",
            f"Compare conversion rates between '{selected_cta}' and '{cta_variations[0 if cta_variations[0] != selected_cta else 1]}'"
        ],
        "visual_suggestions": visual_suggestions
    }


# Register all Marketing & Growth tools
register_tool(
    name="copy.email.campaign",
    description="Generate an email campaign sequence with multiple steps",
    category="Marketing & Growth",
    timeout_seconds=60,
    max_retries=2,
    requires_reflection=True,
    handler=copy_email_campaign
)

register_tool(
    name="content.blog.generate",
    description="Generate long-form blog content on a given topic",
    category="Marketing & Growth",
    timeout_seconds=90,
    max_retries=2,
    requires_reflection=True,
    handler=content_blog_generate
)

register_tool(
    name="social.calendar.create",
    description="Generate a social media content calendar for a specified period",
    category="Marketing & Growth",
    timeout_seconds=60,
    max_retries=3,
    requires_reflection=False,
    handler=social_calendar_create
)

register_tool(
    name="meme.generate",
    description="Generate a meme concept based on the provided topic and style",
    category="Marketing & Growth",
    timeout_seconds=30,
    max_retries=3,
    requires_reflection=False,
    handler=meme_generate
)

register_tool(
    name="copy.tagline",
    description="Generate a punchy brand statement or tagline",
    category="Marketing & Growth",
    timeout_seconds=30,
    max_retries=3,
    requires_reflection=False,
    handler=copy_tagline
)

register_tool(
    name="landing.hero.write",
    description="Generate homepage headline and subheader content",
    category="Marketing & Growth",
    timeout_seconds=45,
    max_retries=2,
    requires_reflection=True,
    handler=landing_hero_write
)
