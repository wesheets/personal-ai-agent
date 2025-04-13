"""
Media & Content Creation Tools

This module provides tools for media and content creation tasks including video intro generation,
product demo scripts, voiceover writing, and animation descriptions.
"""

import random
from typing import Dict, List, Any, Optional

# Import the registry for tool registration
from ...registry import register_tool


def video_intro_generate(product_name: str, duration_seconds: int = 30, style: str = "modern") -> Dict[str, Any]:
    """
    Generate a script and scene outline for a product intro video.
    
    Args:
        product_name: The name of the product
        duration_seconds: The target duration of the video in seconds
        style: The style of the video (modern, cinematic, casual, etc.)
        
    Returns:
        A dictionary containing the script, scene outline, and metadata
    """
    # Calculate approximate word count based on duration (avg 2.5 words per second)
    word_count = int(duration_seconds * 2.5)
    
    # Define style templates
    style_templates = {
        "modern": {
            "intro": "Clean, minimalist scenes with sleek transitions. Modern sans-serif typography.",
            "music": "Upbeat electronic with subtle percussion",
            "color_scheme": "High contrast, primarily whites and blues with accent colors",
            "transitions": "Quick cuts, subtle zoom transitions, clean wipes"
        },
        "cinematic": {
            "intro": "Dramatic lighting, depth of field effects. Serif typography with elegant animations.",
            "music": "Orchestral build with emotional crescendo",
            "color_scheme": "Rich, saturated colors with film-like grading",
            "transitions": "Slow fades, parallax effects, depth transitions"
        },
        "casual": {
            "intro": "Bright, friendly scenes with playful elements. Rounded typography with bouncy animations.",
            "music": "Light acoustic or pop track with positive energy",
            "color_scheme": "Warm, inviting colors with soft shadows",
            "transitions": "Energetic cuts, playful wipes, occasional zoom bounce"
        }
    }
    
    # Get style details or use default
    style_details = style_templates.get(style, style_templates["modern"])
    
    # Generate script based on style and product
    if style == "modern":
        script = f"""[Opening Shot: Sleek product reveal against minimal background]

VOICEOVER:
Introducing {product_name}.

[Product feature highlight with animated overlays]

VOICEOVER:
Designed for those who demand more.

[Quick sequence showing product in use]

VOICEOVER:
{product_name} seamlessly integrates into your workflow, saving you time and enhancing productivity.

[Close-up of key feature with subtle animation]

VOICEOVER:
With intuitive controls and powerful capabilities, it's everything you need.

[Final product shot with tagline animation]

VOICEOVER:
{product_name}. Simplify your process. Amplify your results.

[Logo reveal with call-to-action]"""
    
    elif style == "cinematic":
        script = f"""[Dramatic opening shot: Silhouette of product against sunrise]

VOICEOVER (deep, resonant):
In a world of complexity...

[Slow reveal of product with dramatic lighting]

VOICEOVER:
...one solution stands apart.

[Cinematic sequence of product from multiple angles]

VOICEOVER:
{product_name}. Crafted with precision. Designed for excellence.

[Emotional montage of people benefiting from product]

VOICEOVER:
Experience the transformation that only {product_name} can deliver.

[Epic reveal of full product with orchestral swell]

VOICEOVER:
{product_name}. Redefine what's possible.

[Elegant logo animation with tagline]"""
    
    else:  # casual
        script = f"""[Bright, friendly opening with person smiling]

VOICEOVER (upbeat, friendly):
Hey there! Ever wished there was an easier way?

[Playful animation introducing a common problem]

VOICEOVER:
We've all been there. That's why we created {product_name}!

[Person using product with satisfied expression]

VOICEOVER:
{product_name} makes everything so much simpler. Check this out!

[Quick, fun demonstration of key features]

VOICEOVER:
It's that easy! No more hassle, just smooth sailing.

[People enjoying benefits of the product]

VOICEOVER:
Join thousands of happy users and try {product_name} today!

[Friendly logo animation with casual call-to-action]"""
    
    # Generate scene outline
    scene_outline = [
        {
            "time_code": "00:00 - 00:05",
            "description": "Opening shot introducing the product",
            "visual_elements": ["Product silhouette", "Subtle background animation"],
            "audio": "Opening music begins, introductory voiceover"
        },
        {
            "time_code": "00:06 - 00:12",
            "description": "Product feature highlight sequence",
            "visual_elements": ["Close-up of product features", "Animated overlays"],
            "audio": "Music builds, voiceover explains key benefits"
        },
        {
            "time_code": "00:13 - 00:20",
            "description": "Demonstration of product in use",
            "visual_elements": ["User interaction", "Feature highlights"],
            "audio": "Continued music, detailed voiceover explanation"
        },
        {
            "time_code": "00:21 - 00:25",
            "description": "Testimonial or benefit visualization",
            "visual_elements": ["User satisfaction", "Benefit visualization"],
            "audio": "Music transition, emotional voiceover"
        },
        {
            "time_code": "00:26 - 00:30",
            "description": "Closing shot with call-to-action",
            "visual_elements": ["Product logo", "Call-to-action text", "Website/contact info"],
            "audio": "Music concludes, final voiceover with tagline"
        }
    ]
    
    return {
        "product_name": product_name,
        "duration_seconds": duration_seconds,
        "style": style,
        "style_details": style_details,
        "script": script,
        "scene_outline": scene_outline,
        "word_count": len(script.split()),
        "estimated_reading_time": f"{len(script.split()) / 2.5:.1f} seconds"
    }


def product_demo_script(product_name: str, features: List[str], audience: str = "general") -> Dict[str, Any]:
    """
    Generate a full written UI walkthrough for a product demo.
    
    Args:
        product_name: The name of the product
        features: List of features to highlight in the demo
        audience: Target audience (general, technical, executive, etc.)
        
    Returns:
        A dictionary containing the demo script and metadata
    """
    # Ensure we have at least some features
    if not features:
        features = ["User Interface", "Core Functionality", "Integration Capabilities", "Analytics Dashboard"]
    
    # Define audience-specific language and focus
    audience_templates = {
        "general": {
            "intro": f"Welcome to this demonstration of {product_name}. Today, I'll show you how {product_name} can simplify your workflow and improve productivity.",
            "technical_level": "moderate",
            "focus": "usability and benefits",
            "conclusion": f"As you've seen, {product_name} offers an intuitive experience with powerful features that can transform how you work. We invite you to try it for yourself."
        },
        "technical": {
            "intro": f"In this technical walkthrough of {product_name}, we'll explore the architecture, integration capabilities, and advanced features that make it a robust solution.",
            "technical_level": "high",
            "focus": "implementation details and technical capabilities",
            "conclusion": f"To summarize, {product_name} provides a comprehensive technical framework with extensive APIs, robust security, and scalable architecture to meet your development needs."
        },
        "executive": {
            "intro": f"Thank you for joining this executive overview of {product_name}. I'll demonstrate how this solution delivers measurable ROI and addresses key business challenges.",
            "technical_level": "low",
            "focus": "business value and strategic advantages",
            "conclusion": f"In conclusion, {product_name} offers clear business value through increased efficiency, reduced costs, and improved outcomes, positioning your organization for success in today's competitive landscape."
        }
    }
    
    # Get audience template or use default
    audience_template = audience_templates.get(audience, audience_templates["general"])
    
    # Generate the demo script
    script = f"""# {product_name} Product Demonstration Script

## Introduction
{audience_template["intro"]}

## Demo Overview
During this demonstration, we'll cover:
"""

    # Add features to overview
    for i, feature in enumerate(features):
        script += f"\n{i+1}. {feature}"
    
    script += "\n\n## Walkthrough\n"
    
    # Generate walkthrough for each feature
    for i, feature in enumerate(features):
        script += f"""
### {feature}

**Narrator:** Now let's look at the {feature} of {product_name}.

**Screen Action:** [Display the {feature.lower().replace(' ', '_')} screen/section]

**Narrator:** """
        
        # Generate feature-specific content based on audience
        if audience == "technical":
            script += f"""Here we can see the {feature} component, which is built on a [relevant technology] framework. Notice the API endpoints available for integration with your existing systems.

**Screen Action:** [Highlight API documentation or technical specifications]

**Narrator:** The architecture allows for customization through configuration files located in the settings directory. You can modify these parameters to adapt to your specific requirements.

**Screen Action:** [Demonstrate configuration options or code examples]

**Narrator:** Performance optimization is achieved through [technical explanation], resulting in response times under 100ms even with large datasets."""
        
        elif audience == "executive":
            script += f"""The {feature} delivers measurable business impact by streamlining operations that typically consume significant resources.

**Screen Action:** [Show ROI calculator or business metrics dashboard]

**Narrator:** Based on customer data, organizations implementing this feature have seen an average 27% reduction in processing time and 32% decrease in operational costs.

**Screen Action:** [Display case study highlights or comparison charts]

**Narrator:** The competitive advantage here is clear - while other solutions offer basic functionality, {product_name}'s {feature} provides comprehensive capabilities that position your organization ahead of the curve."""
        
        else:  # general audience
            script += f"""This intuitive interface makes it easy to [primary action related to feature]. Let me show you how it works.

**Screen Action:** [Demonstrate primary user flow for the feature]

**Narrator:** Users particularly appreciate how they can [benefit of feature] with just a few clicks. Let's try that now.

**Screen Action:** [Complete a common task using the feature]

**Narrator:** Notice how the system provides helpful feedback and guidance throughout the process, making it accessible even for first-time users."""
    
    # Add conclusion
    script += f"""

## Conclusion
{audience_template["conclusion"]}

## Q&A Preparation
Below are anticipated questions and suggested responses:

1. **Question:** How difficult is implementation?
   **Response:** [Tailor based on audience technical level]

2. **Question:** What kind of support is available?
   **Response:** We offer comprehensive support including documentation, training, and dedicated customer success managers.

3. **Question:** How does pricing work?
   **Response:** We offer flexible pricing models based on [relevant factors]. I'd be happy to connect you with our sales team for a customized quote.

## Demo Notes
- Total estimated demo time: 20 minutes
- Ensure all features are working before presentation
- Have backup screenshots available in case of technical issues
- Focus on [audience_template["focus"]]
"""
    
    # Generate key talking points
    talking_points = []
    for feature in features:
        if audience == "technical":
            talking_points.append(f"Technical architecture of {feature}")
            talking_points.append(f"Integration capabilities with existing systems")
            talking_points.append(f"Performance metrics and optimization")
        elif audience == "executive":
            talking_points.append(f"ROI and business impact of {feature}")
            talking_points.append(f"Competitive advantages in the market")
            talking_points.append(f"Strategic value proposition")
        else:
            talking_points.append(f"User benefits of {feature}")
            talking_points.append(f"Ease of use and intuitive design")
            talking_points.append(f"Time-saving capabilities")
    
    return {
        "product_name": product_name,
        "audience": audience,
        "features": features,
        "script": script,
        "talking_points": talking_points,
        "technical_level": audience_template["technical_level"],
        "focus": audience_template["focus"],
        "estimated_duration_minutes": 15 + (len(features) * 3)
    }


def audio_voiceover_write(content_type: str, duration_seconds: int = 60, tone: str = "professional") -> Dict[str, Any]:
    """
    Generate a voiceover script for audio content.
    
    Args:
        content_type: The type of content (explainer, tutorial, ad, etc.)
        duration_seconds: The target duration of the audio in seconds
        tone: The tone of the voiceover (professional, friendly, dramatic, etc.)
        
    Returns:
        A dictionary containing the voiceover script and metadata
    """
    # Calculate approximate word count based on duration (avg 2.5 words per second)
    word_count = int(duration_seconds * 2.5)
    
    # Define tone templates
    tone_templates = {
        "professional": {
            "pacing": "measured",
            "vocabulary": "industry-standard terminology",
            "sentence_structure": "clear, concise statements",
            "transitions": "logical transitions between points"
        },
        "friendly": {
            "pacing": "conversational",
            "vocabulary": "accessible, everyday language",
            "sentence_structure": "questions and personal anecdotes",
            "transitions": "casual connectors and rhetorical questions"
        },
        "dramatic": {
            "pacing": "varied for emphasis",
            "vocabulary": "evocative, emotional language",
            "sentence_structure": "building tension with varied length",
            "transitions": "emotional pivots and dramatic pauses"
        },
        "educational": {
            "pacing": "deliberate with pauses for comprehension",
            "vocabulary": "clear explanations of technical terms",
            "sentence_structure": "explanatory with examples",
            "transitions": "sequential building of concepts"
        }
    }
    
    # Get tone details or use default
    tone_details = tone_templates.get(tone, tone_templates["professional"])
    
    # Generate script based on content type and tone
    script = ""
    
    if content_type == "explainer":
        if tone == "professional":
            script = f"""[VOICEOVER SCRIPT: PROFESSIONAL EXPLAINER]

Welcome to this overview of [Product/Service/Concept].

[3-second pause for intro graphic]

In today's competitive landscape, understanding [key concept] is essential for success. Let's examine what makes it valuable.

[2-second pause]

First, [Product/Service/Concept] provides three key benefits:

One: Improved efficiency through streamlined processes.
Two: Enhanced accuracy with advanced algorithms.
Three: Significant cost reduction compared to traditional methods.

[2-second pause]

Let's explore how implementation works in practice.

[3-second pause for transition graphic]

The process begins with a comprehensive assessment of your current systems.

Next, our team integrates the solution with minimal disruption to operations.

Finally, we provide detailed analytics to measure performance improvements.

[2-second pause]

Organizations implementing this solution have reported an average 27% increase in productivity.

[2-second pause]

Contact our team today to schedule a consultation and discover how [Product/Service/Concept] can transform your operations.

[3-second pause for closing graphic]"""
        
        elif tone == "friendly":
            script = f"""[VOICEOVER SCRIPT: FRIENDLY EXPLAINER]

Hey there! Ever wondered about [Product/Service/Concept]? Let me break it down for you!

[3-second pause for intro graphic]

So here's the thing - we all face challenges with [common problem], right? I know I certainly did before discovering this solution!

[2-second pause]

Let me share what makes this so awesome:

First off, you'll save tons of time - who doesn't want that?
Plus, it's super easy to use, even if you're not tech-savvy.
And my personal favorite part? You'll actually enjoy the process!

[2-second pause]

So how does it work? Let me walk you through it.

[3-second pause for transition graphic]

You start by simply answering a few questions about your needs - nothing complicated!

Then, the system does its magic behind the scenes (pretty cool, right?).

Before you know it, you've got exactly what you need, tailored just for you.

[2-second pause]

I've seen so many people just like you transform their experience with this solution. Sarah from Chicago told me she couldn't believe how much easier her life became!

[2-second pause]

Why not give it a try? You've got nothing to lose and everything to gain!

[3-second pause for closing graphic]"""
        
        else:  # default to educational
            script = f"""[VOICEOVER SCRIPT: EDUCATIONAL EXPLAINER]

Welcome to our lesson on [Product/Service/Concept].

[3-second pause for intro graphic]

Today we'll explore the fundamental principles behind this important topic. By the end of this explanation, you'll understand both how it works and why it matters.

[2-second pause]

Let's begin with a definition: [Product/Service/Concept] refers to [clear, concise definition].

[2-second pause]

This concept is built on three key principles:

The first principle is [principle one]. This means that [explanation with example].

The second principle involves [principle two]. To illustrate this, consider [practical example].

The third principle centers on [principle three]. This is important because [relevance explanation].

[3-second pause for transition graphic]

Now, let's examine how these principles work together in practice.

When [first step occurs], it triggers [resulting action]. This leads to [outcome], which demonstrates [principle in action].

[2-second pause]

To help solidify your understanding, let's review a case study.

[brief case study example]

[2-second pause]

To summarize what we've learned: [Product/Service/Concept] works by [concise summary]. Understanding this helps us [practical application].

[2-second pause]

In our next lesson, we'll build on these fundamentals to explore [related topic].

[3-second pause for closing graphic]"""
    
    elif content_type == "advertisement":
        if tone == "dramatic":
            script = f"""[VOICEOVER SCRIPT: DRAMATIC ADVERTISEMENT]

[Begin with 2 seconds of silence for impact]

In a world where ordinary solutions fail...

[3-second pause for dramatic visuals]

One innovation stands apart.

[2-second pause]

Introducing [Product/Service] – the revolutionary approach that's changing everything.

[dramatic music swell]

Imagine a reality where [common problem] no longer limits your potential.

Where every challenge becomes an opportunity.

Where you define what's possible.

[2-second pause]

This isn't just another option.

This is transformation.

[3-second pause for emotional testimonial visuals]

People who've experienced [Product/Service] describe it as "life-changing."

"I never thought it was possible," says [customer name].

"Everything is different now."

[music builds to crescendo]

Why accept limitations when you can transcend them?

Why settle for ordinary when extraordinary awaits?

[2-second pause]

[Product/Service]. Redefine your reality.

[Contact information with 3-second pause]

Available now. But some opportunities only come once.

[3-second pause for final dramatic visual]"""
        
        elif tone == "professional":
            script = f"""[VOICEOVER SCRIPT: PROFESSIONAL ADVERTISEMENT]

[Professional music bed begins]

For organizations seeking competitive advantage, efficiency is essential.

[2-second pause]

Introducing [Product/Service] – the comprehensive solution designed for today's business challenges.

[2-second pause]

Our proprietary system delivers measurable results:
- 37% increase in operational efficiency
- 42% reduction in processing time
- 29% improvement in customer satisfaction metrics

[2-second pause]

Developed by industry experts and refined through extensive testing, [Product/Service] integrates seamlessly with your existing infrastructure.

[2-second pause]

Leading organizations across [industry sectors] have implemented our solution with exceptional outcomes.

[2-second pause]

[Company name], a recognized industry leader, reported significant performance improvements within the first quarter of implementation.

[2-second pause]

Our dedicated team provides comprehensive onboarding and ongoing support to ensure optimal results.

[2-second pause]

[Product/Service]. Engineered for excellence. Designed for results.

[2-second pause]

Contact our consultants today to schedule a personalized demonstration.

[Contact information with 3-second pause]

[Professional music fades]"""
        
        else:  # default to friendly
            script = f"""[VOICEOVER SCRIPT: FRIENDLY ADVERTISEMENT]

[Upbeat, friendly music begins]

Hey there! Tired of dealing with [common problem]? We totally get it!

[2-second pause]

That's why we created [Product/Service] – the super simple way to [key benefit]!

[2-second pause]

Check out what makes us different:
- It's incredibly easy to use – no technical skills needed!
- You'll save hours every week (imagine what you could do with that time!)
- And it actually makes [relevant task] fun – seriously!

[2-second pause]

Don't just take our word for it! Listen to what Sarah from Chicago had to say:

"I was skeptical at first, but wow! [Product/Service] has completely changed how I [relevant activity]. I can't imagine going back to my old way of doing things!"

[2-second pause]

Right now, we're offering an amazing deal for new customers:
Get started today and receive [special offer]!

[2-second pause]

[Product/Service] – because life's too short for [common problem]!

[2-second pause]

Visit our website or give us a call today! What are you waiting for?

[Contact information with 3-second pause]

[Friendly music fades]"""
    
    elif content_type == "tutorial":
        if tone == "educational":
            script = f"""[VOICEOVER SCRIPT: EDUCATIONAL TUTORIAL]

Welcome to this step-by-step tutorial on [specific task or process].

[3-second pause for intro graphic]

By the end of this guide, you'll be able to [learning objective] with confidence. Let's begin.

[2-second pause]

Before we start, ensure you have the following:
- [required item 1]
- [required item 2]
- [required item 3]

[2-second pause]

Step 1: [First action to take]
Begin by [detailed instruction]. Make sure that [important consideration]. This establishes [reason for this step].

[3-second pause for demonstration]

Step 2: [Second action to take]
Next, [detailed instruction]. Pay special attention to [specific detail], as this will affect [outcome].

[3-second pause for demonstration]

Step 3: [Third action to take]
Now, [detailed instruction]. A common mistake here is [potential error]. Avoid this by [preventative measure].

[3-second pause for demonstration]

Step 4: [Fourth action to take]
Continue by [detailed instruction]. This step is important because [explanation of significance].

[3-second pause for demonstration]

Step 5: [Final action to take]
Finally, [detailed instruction]. Verify your work by checking that [confirmation indicator].

[2-second pause]

Let's review what we've accomplished:
- We started with [summary of step 1]
- Then we [summary of step 2]
- Next, we [summary of step 3]
- Followed by [summary of step 4]
- And completed the process with [summary of step 5]

[2-second pause]

Congratulations! You've successfully learned how to [learning objective]. With practice, this process will become second nature.

[2-second pause]

For additional resources and advanced techniques, visit [resource location].

[3-second pause for closing graphic]"""
        
        else:  # default to friendly
            script = f"""[VOICEOVER SCRIPT: FRIENDLY TUTORIAL]

Hey everyone! Welcome to this super easy tutorial on [specific task or process].

[3-second pause for intro graphic]

Don't worry if you're new to this – I'll walk you through everything step by step, and before you know it, you'll be [learning objective] like a pro!

[2-second pause]

First, let's grab everything we need:
- You'll want [required item 1]
- Also [required item 2]
- And don't forget [required item 3]

[2-second pause]

Got everything? Awesome! Let's jump right in.

Step 1: Let's start with [first action]
This is really straightforward – just [simplified instruction]. I like to [personal tip] because it makes things so much easier!

[3-second pause for demonstration]

Step 2: Now for [second action]
All you need to do is [simplified instruction]. See how I'm [specific technique]? That little trick saves me so much time!

[3-second pause for demonstration]

Step 3: Here comes [third action]
This part is actually my favorite! Just [simplified instruction]. If you mess up here, no worries at all – just [simple fix] and keep going.

[3-second pause for demonstration]

Step 4: We're almost there! Let's [fourth action]
Simply [simplified instruction]. Isn't that cool? I remember when I first learned this, it was such a game-changer!

[3-second pause for demonstration]

Step 5: Last step – let's finish with [final action]
Just [simplified instruction] and... ta-da! You did it!

[2-second pause]

Let's take a quick look at what we just created. Doesn't that look great? You should be super proud of yourself!

[2-second pause]

If you enjoyed this tutorial, don't forget to check out my other guides. And if you have any questions, just drop them in the comments below – I'm always happy to help!

[3-second pause for closing graphic]"""
    
    # Calculate actual word count
    actual_word_count = len(script.split())
    
    # Calculate actual duration
    actual_duration = actual_word_count / 2.5
    
    # Generate timing markers
    timing_markers = []
    current_time = 0
    for paragraph in script.split("\n\n"):
        paragraph_word_count = len(paragraph.split())
        paragraph_duration = paragraph_word_count / 2.5
        
        # Skip empty paragraphs
        if paragraph_word_count == 0:
            continue
        
        timing_markers.append({
            "time_code": f"{int(current_time // 60):02d}:{int(current_time % 60):02d}",
            "text": paragraph,
            "word_count": paragraph_word_count,
            "duration_seconds": paragraph_duration
        })
        
        current_time += paragraph_duration
    
    return {
        "content_type": content_type,
        "tone": tone,
        "tone_details": tone_details,
        "script": script,
        "target_duration_seconds": duration_seconds,
        "actual_duration_seconds": actual_duration,
        "target_word_count": word_count,
        "actual_word_count": actual_word_count,
        "timing_markers": timing_markers,
        "reading_pace_wpm": 150  # 2.5 words per second = 150 words per minute
    }


def animation_describe(element_type: str, animation_type: str, duration_ms: int = 500) -> Dict[str, Any]:
    """
    Generate a description of an animation for a UI element.
    
    Args:
        element_type: The type of element to animate (button, card, modal, etc.)
        animation_type: The type of animation (fade, slide, bounce, etc.)
        duration_ms: The duration of the animation in milliseconds
        
    Returns:
        A dictionary containing the animation description, CSS, and metadata
    """
    # Define animation templates
    animation_templates = {
        "fade": {
            "description": "Gradually changes opacity from 0 to 1",
            "css_keyframes": """@keyframes fadeAnimation {
  from { opacity: 0; }
  to { opacity: 1; }
}""",
            "css_animation": """animation: fadeAnimation {{duration}}ms ease-in-out forwards;""",
            "js_implementation": """element.style.opacity = 0;
element.style.transition = 'opacity {{duration}}ms ease-in-out';
setTimeout(() => { element.style.opacity = 1; }, 10);""",
            "timing_function": "ease-in-out",
            "properties_affected": ["opacity"]
        },
        "slide": {
            "description": "Moves element from outside the viewport to its final position",
            "css_keyframes": """@keyframes slideAnimation {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}""",
            "css_animation": """animation: slideAnimation {{duration}}ms ease-out forwards;""",
            "js_implementation": """element.style.transform = 'translateX(-100%)';
element.style.transition = 'transform {{duration}}ms ease-out';
setTimeout(() => { element.style.transform = 'translateX(0)'; }, 10);""",
            "timing_function": "ease-out",
            "properties_affected": ["transform"]
        },
        "bounce": {
            "description": "Adds a springy, bouncing effect to the element's entrance",
            "css_keyframes": """@keyframes bounceAnimation {
  0% { transform: scale(0.3); opacity: 0; }
  40% { transform: scale(1.1); opacity: 1; }
  60% { transform: scale(0.9); }
  100% { transform: scale(1); }
}""",
            "css_animation": """animation: bounceAnimation {{duration}}ms cubic-bezier(0.215, 0.610, 0.355, 1.000) forwards;""",
            "js_implementation": """element.style.transform = 'scale(0.3)';
element.style.opacity = 0;
element.style.transition = 'transform {{duration}}ms cubic-bezier(0.215, 0.610, 0.355, 1.000), opacity {{duration_half}}ms ease-in';
setTimeout(() => {
  element.style.opacity = 1;
  element.style.transform = 'scale(1)';
}, 10);""",
            "timing_function": "cubic-bezier(0.215, 0.610, 0.355, 1.000)",
            "properties_affected": ["transform", "opacity"]
        },
        "rotate": {
            "description": "Rotates the element into view",
            "css_keyframes": """@keyframes rotateAnimation {
  from { transform: rotate(-180deg); opacity: 0; }
  to { transform: rotate(0); opacity: 1; }
}""",
            "css_animation": """animation: rotateAnimation {{duration}}ms ease-in-out forwards;""",
            "js_implementation": """element.style.transform = 'rotate(-180deg)';
element.style.opacity = 0;
element.style.transition = 'transform {{duration}}ms ease-in-out, opacity {{duration_half}}ms ease-in';
setTimeout(() => {
  element.style.opacity = 1;
  element.style.transform = 'rotate(0)';
}, 10);""",
            "timing_function": "ease-in-out",
            "properties_affected": ["transform", "opacity"]
        },
        "pulse": {
            "description": "Creates a pulsing effect to draw attention",
            "css_keyframes": """@keyframes pulseAnimation {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}""",
            "css_animation": """animation: pulseAnimation {{duration}}ms ease-in-out infinite;""",
            "js_implementation": """function pulse() {
  element.style.transform = 'scale(1)';
  element.style.transition = 'transform {{duration_half}}ms ease-in-out';
  setTimeout(() => {
    element.style.transform = 'scale(1.05)';
    setTimeout(() => {
      element.style.transform = 'scale(1)';
      setTimeout(pulse, {{duration}});
    }, {{duration_half}});
  }, 10);
}
pulse();""",
            "timing_function": "ease-in-out",
            "properties_affected": ["transform"]
        }
    }
    
    # Get animation template or use default
    animation_template = animation_templates.get(animation_type, animation_templates["fade"])
    
    # Replace duration placeholders
    css_animation = animation_template["css_animation"].replace("{{duration}}", str(duration_ms))
    css_keyframes = animation_template["css_keyframes"]
    
    js_implementation = animation_template["js_implementation"].replace("{{duration}}", str(duration_ms))
    js_implementation = js_implementation.replace("{{duration_half}}", str(int(duration_ms / 2)))
    
    # Generate element-specific CSS
    element_css = f""".{element_type} {{
  {css_animation}
}}

{css_keyframes}"""
    
    # Generate React implementation
    react_implementation = ""
    if animation_type == "fade":
        react_implementation = f"""import {{ useState, useEffect }} from 'react';
import './styles.css'; // Include your CSS with the keyframes

function Animated{element_type.capitalize()}() {{
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {{
    setIsVisible(true);
  }}, []);
  
  return (
    <div className="{element_type}" style={{
      opacity: 0,
      animation: isVisible ? 'fadeAnimation {duration_ms}ms ease-in-out forwards' : 'none'
    }}>
      {/* {element_type.capitalize()} content */}
    </div>
  );
}}"""
    elif animation_type == "slide":
        react_implementation = f"""import {{ useState, useEffect }} from 'react';
import './styles.css'; // Include your CSS with the keyframes

function Animated{element_type.capitalize()}() {{
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {{
    setIsVisible(true);
  }}, []);
  
  return (
    <div className="{element_type}" style={{
      transform: 'translateX(-100%)',
      animation: isVisible ? 'slideAnimation {duration_ms}ms ease-out forwards' : 'none'
    }}>
      {/* {element_type.capitalize()} content */}
    </div>
  );
}}"""
    
    # Generate usage examples
    usage_examples = {
        "css": f"""<div class="{element_type}">
  <!-- {element_type} content -->
</div>

<style>
{element_css}
</style>""",
        
        "javascript": f"""<div id="my-{element_type}">
  <!-- {element_type} content -->
</div>

<script>
  const element = document.getElementById('my-{element_type}');
  {js_implementation}
</script>""",
        
        "react": react_implementation
    }
    
    # Generate animation behavior description
    behavior_description = f"This animation {animation_template['description']} for the {element_type} element. "
    behavior_description += f"It takes {duration_ms}ms to complete and affects {', '.join(animation_template['properties_affected'])}. "
    
    if animation_type == "fade":
        behavior_description += f"The {element_type} will smoothly appear by transitioning from fully transparent to fully visible."
    elif animation_type == "slide":
        behavior_description += f"The {element_type} will slide in from the left side of the screen to its final position."
    elif animation_type == "bounce":
        behavior_description += f"The {element_type} will start small, then overshoot its final size before settling, creating a springy effect."
    elif animation_type == "rotate":
        behavior_description += f"The {element_type} will rotate from -180 degrees to 0 degrees while fading in."
    elif animation_type == "pulse":
        behavior_description += f"The {element_type} will continuously grow slightly larger and then return to its original size, creating a heartbeat-like effect."
    
    return {
        "element_type": element_type,
        "animation_type": animation_type,
        "duration_ms": duration_ms,
        "behavior_description": behavior_description,
        "css": element_css,
        "timing_function": animation_template["timing_function"],
        "properties_affected": animation_template["properties_affected"],
        "usage_examples": usage_examples
    }


# Register all Media & Content Creation tools
register_tool(
    name="video.intro.generate",
    description="Generate a script and scene outline for a product intro video",
    category="Media & Content Creation",
    timeout_seconds=60,
    max_retries=2,
    requires_reflection=True,
    handler=video_intro_generate
)

register_tool(
    name="product.demo.script",
    description="Generate a full written UI walkthrough for a product demo",
    category="Media & Content Creation",
    timeout_seconds=90,
    max_retries=2,
    requires_reflection=True,
    handler=product_demo_script
)

register_tool(
    name="audio.voiceover.write",
    description="Generate a voiceover script for audio content",
    category="Media & Content Creation",
    timeout_seconds=60,
    max_retries=3,
    requires_reflection=False,
    handler=audio_voiceover_write
)

register_tool(
    name="animation.describe",
    description="Generate a description of an animation for a UI element",
    category="Media & Content Creation",
    timeout_seconds=30,
    max_retries=3,
    requires_reflection=False,
    handler=animation_describe
)
