from typing import Dict, Any, List, Optional, Union
from enum import Enum, auto
from pydantic import BaseModel, Field

class TaskCategory(str, Enum):
    """Task categories for agent interactions"""
    CODE = "code"
    STRATEGY = "strategy"
    RESEARCH = "research"
    DESIGN = "design"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    TROUBLESHOOTING = "troubleshooting"
    EXPLANATION = "explanation"
    CREATIVE = "creative"
    OTHER = "other"

class TaskMetadata(BaseModel):
    """
    Metadata for task categorization and next step suggestions
    """
    task_category: TaskCategory = Field(
        default=TaskCategory.OTHER,
        description="Category of the task"
    )
    suggested_next_step: Optional[str] = Field(
        default=None,
        description="Suggested next step for the user or system"
    )
    priority: bool = Field(
        default=False,
        description="Whether this task is high priority"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Custom tags for the task"
    )
    
    class Config:
        use_enum_values = True

class TaskTagger:
    """
    Handles task categorization and next step suggestions
    """
    
    @staticmethod
    async def categorize_task(
        input_text: str,
        output_text: str,
        model: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TaskMetadata:
        """
        Categorize a task based on input and output
        
        Args:
            input_text: User input text
            output_text: Agent output text
            model: Model to use for categorization
            context: Additional context
            
        Returns:
            TaskMetadata object with category and suggested next step
        """
        from app.providers import process_with_model
        
        # Create prompt for task categorization
        prompt_chain = {
            "system": "You are a task categorization system. Your job is to analyze user inputs and agent responses to categorize tasks and suggest logical next steps.",
            "temperature": 0.3,
            "max_tokens": 300
        }
        
        # List all available categories
        categories = [cat.value for cat in TaskCategory]
        categories_str = ", ".join(categories)
        
        user_input = f"""
Analyze the following user input and agent response:

USER INPUT:
{input_text}

AGENT RESPONSE:
{output_text}

1. Categorize this task into exactly ONE of these categories: {categories_str}
2. Suggest a logical next step that would follow this interaction
3. Determine if this task should be marked as high priority (true/false)
4. Suggest 1-3 relevant tags for this task

Format your response exactly as follows:
CATEGORY: [category]
NEXT_STEP: [suggested next step]
PRIORITY: [true/false]
TAGS: [tag1, tag2, tag3]
"""
        
        # Process with model
        result = await process_with_model(
            model=model,
            prompt_chain=prompt_chain,
            user_input=user_input,
            context=context
        )
        
        # Parse the response to extract category and next step
        content = result.get("content", "")
        
        # Default values
        category = TaskCategory.OTHER
        next_step = None
        priority = False
        tags = []
        
        # Parse the response
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("CATEGORY:"):
                category_str = line.replace("CATEGORY:", "").strip().lower()
                # Find the closest matching category
                for cat in TaskCategory:
                    if cat.value.lower() == category_str:
                        category = cat
                        break
            elif line.startswith("NEXT_STEP:"):
                next_step = line.replace("NEXT_STEP:", "").strip()
            elif line.startswith("PRIORITY:"):
                priority_str = line.replace("PRIORITY:", "").strip().lower()
                priority = priority_str == "true"
            elif line.startswith("TAGS:"):
                tags_str = line.replace("TAGS:", "").strip()
                tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        
        return TaskMetadata(
            task_category=category,
            suggested_next_step=next_step,
            priority=priority,
            tags=tags
        )

# Singleton instance
_task_tagger = None

def get_task_tagger() -> TaskTagger:
    """
    Get the singleton TaskTagger instance
    """
    global _task_tagger
    if _task_tagger is None:
        _task_tagger = TaskTagger()
    return _task_tagger
