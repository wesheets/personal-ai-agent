"""
Orchestrator Consultation Flow

This module implements the consultation flow for the Orchestrator, allowing it to
engage in a conversational session with the operator to clarify goals and develop
a strategic plan.
"""

import os
import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple

# Define question templates for different goal types
QUESTION_TEMPLATES = {
    "website": [
        "What is the primary purpose of this website? (e.g., portfolio, e-commerce, blog, SaaS landing page)",
        "Who is the target audience for this website?",
        "What are the key features or sections you want to include?",
        "Do you have any design preferences or existing brand guidelines?",
        "What is your timeline for launching this website?"
    ],
    "application": [
        "What problem does this application solve for users?",
        "Who are the primary users of this application?",
        "What are the core features that must be included in the MVP?",
        "Do you have any technical requirements or preferences (e.g., tech stack, hosting)?",
        "What is your timeline for developing and launching this application?"
    ],
    "marketing": [
        "What product or service are you marketing?",
        "Who is your target audience for this marketing campaign?",
        "What are your primary marketing goals? (e.g., brand awareness, lead generation, sales)",
        "What marketing channels do you want to focus on?",
        "What is your timeline and budget for this marketing effort?"
    ],
    "content": [
        "What type of content do you need? (e.g., blog posts, social media, video scripts)",
        "Who is the target audience for this content?",
        "What is the primary purpose of this content? (e.g., educate, entertain, convert)",
        "Do you have any specific topics or themes you want to cover?",
        "How will this content be distributed or published?"
    ],
    "general": [
        "Could you provide more details about what you're looking to achieve with this goal?",
        "Who are the primary stakeholders or users for this project?",
        "What would success look like for this project?",
        "Are there any specific constraints or requirements I should be aware of?",
        "What is your timeline for completing this project?"
    ]
}

class ConsultationSession:
    """
    Manages a consultation session between the Orchestrator and the operator.
    
    This class handles the flow of asking questions, storing responses, and
    generating a strategic plan based on the operator's input.
    """
    
    def __init__(self, operator_id: str, goal: str):
        """
        Initialize a new consultation session.
        
        Args:
            operator_id: ID of the operator
            goal: Initial goal statement from the operator
        """
        self.session_id = str(uuid.uuid4())
        self.timestamp = datetime.datetime.now().isoformat()
        self.operator_id = operator_id
        self.mode = "strategic"
        self.goal = goal
        self.goal_type = self._determine_goal_type(goal)
        self.questions = []
        self.current_question_index = 0
        self.plan = None
        
        # Generate initial questions based on goal type
        self._generate_questions()
        
    def _determine_goal_type(self, goal: str) -> str:
        """
        Determine the type of goal based on the goal statement.
        
        Args:
            goal: Goal statement from the operator
            
        Returns:
            Goal type (website, application, marketing, content, or general)
        """
        goal_lower = goal.lower()
        
        if any(keyword in goal_lower for keyword in ["website", "site", "webpage", "landing page", "web design"]):
            return "website"
        elif any(keyword in goal_lower for keyword in ["app", "application", "software", "platform", "system", "tool"]):
            return "application"
        elif any(keyword in goal_lower for keyword in ["marketing", "campaign", "promotion", "advertis", "brand"]):
            return "marketing"
        elif any(keyword in goal_lower for keyword in ["content", "blog", "article", "post", "video", "podcast"]):
            return "content"
        else:
            return "general"
            
    def _generate_questions(self) -> None:
        """Generate questions based on the goal type."""
        # Get question templates for the determined goal type
        templates = QUESTION_TEMPLATES.get(self.goal_type, QUESTION_TEMPLATES["general"])
        
        # Create question objects
        for i, question_text in enumerate(templates):
            self.questions.append({
                "question_id": f"q{i+1}",
                "question": question_text,
                "answer": None,
                "timestamp": None
            })
            
    def get_next_question(self) -> Optional[Dict[str, Any]]:
        """
        Get the next question to ask the operator.
        
        Returns:
            Question object or None if all questions have been answered
        """
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None
        
    def answer_question(self, question_id: str, answer: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Record the operator's answer to a question.
        
        Args:
            question_id: ID of the question being answered
            answer: Operator's answer to the question
            
        Returns:
            Tuple of (has_more_questions, next_question)
        """
        # Find the question with the given ID
        for i, question in enumerate(self.questions):
            if question["question_id"] == question_id:
                # Record the answer and timestamp
                question["answer"] = answer
                question["timestamp"] = datetime.datetime.now().isoformat()
                
                # If this is the current question, advance to the next
                if i == self.current_question_index:
                    self.current_question_index += 1
                
                # Check if we have more questions
                if self.current_question_index < len(self.questions):
                    return True, self.questions[self.current_question_index]
                else:
                    return False, None
                    
        # Question not found
        raise ValueError(f"Question with ID {question_id} not found")
        
    def generate_plan(self) -> Dict[str, Any]:
        """
        Generate a strategic plan based on the operator's answers.
        
        Returns:
            Plan object with phases, tools, and agents
        """
        # Ensure all questions have been answered
        if any(q["answer"] is None for q in self.questions):
            raise ValueError("Cannot generate plan until all questions have been answered")
            
        # Create a plan based on the goal type and answers
        plan = {
            "title": f"{self.goal_type.capitalize()} Development Plan",
            "description": f"Strategic plan for: {self.goal}",
            "phases": []
        }
        
        # Add phases based on goal type
        if self.goal_type == "website":
            plan["phases"] = self._generate_website_phases()
        elif self.goal_type == "application":
            plan["phases"] = self._generate_application_phases()
        elif self.goal_type == "marketing":
            plan["phases"] = self._generate_marketing_phases()
        elif self.goal_type == "content":
            plan["phases"] = self._generate_content_phases()
        else:
            plan["phases"] = self._generate_general_phases()
            
        self.plan = plan
        return plan
        
    def _generate_website_phases(self) -> List[Dict[str, Any]]:
        """Generate phases for a website development plan."""
        return [
            {
                "phase_id": "phase1",
                "title": "Design and Planning",
                "description": "Create website design, sitemap, and content plan",
                "estimated_duration": "1-2 weeks",
                "tools": ["design.ui.component.scaffold", "brand.palette.suggest", "logo.generate"],
                "agents": ["ASH"]
            },
            {
                "phase_id": "phase2",
                "title": "Development",
                "description": "Build website frontend and backend components",
                "estimated_duration": "2-4 weeks",
                "tools": ["code.write", "api.build", "db.schema.generate"],
                "agents": ["HAL"]
            },
            {
                "phase_id": "phase3",
                "title": "Launch and Optimization",
                "description": "Deploy website, test, and optimize for performance",
                "estimated_duration": "1-2 weeks",
                "tools": ["deploy.github.setup", "env.secret.check", "payment.init"],
                "agents": ["HAL", "ASH"]
            }
        ]
        
    def _generate_application_phases(self) -> List[Dict[str, Any]]:
        """Generate phases for an application development plan."""
        return [
            {
                "phase_id": "phase1",
                "title": "Requirements and Design",
                "description": "Define requirements, create wireframes, and design UI/UX",
                "estimated_duration": "2-3 weeks",
                "tools": ["design.ui.component.scaffold", "responsive.layout.create", "db.schema.generate"],
                "agents": ["ASH", "HAL"]
            },
            {
                "phase_id": "phase2",
                "title": "Core Development",
                "description": "Develop core application features and backend services",
                "estimated_duration": "4-8 weeks",
                "tools": ["code.write", "api.build", "unit.test.generate", "unit.test.run"],
                "agents": ["HAL"]
            },
            {
                "phase_id": "phase3",
                "title": "Testing and Deployment",
                "description": "Perform testing, bug fixing, and deploy to production",
                "estimated_duration": "2-3 weeks",
                "tools": ["debug.trace", "deploy.github.setup", "env.secret.check"],
                "agents": ["HAL"]
            }
        ]
        
    def _generate_marketing_phases(self) -> List[Dict[str, Any]]:
        """Generate phases for a marketing campaign plan."""
        return [
            {
                "phase_id": "phase1",
                "title": "Strategy and Content Creation",
                "description": "Develop marketing strategy and create initial content",
                "estimated_duration": "2-3 weeks",
                "tools": ["copy.email.campaign", "content.blog.generate", "landing.hero.write"],
                "agents": ["ASH"]
            },
            {
                "phase_id": "phase2",
                "title": "Campaign Launch",
                "description": "Launch marketing campaigns across selected channels",
                "estimated_duration": "1-2 weeks",
                "tools": ["social.calendar.create", "meme.generate", "copy.tagline"],
                "agents": ["ASH"]
            },
            {
                "phase_id": "phase3",
                "title": "Analysis and Optimization",
                "description": "Analyze campaign performance and optimize for better results",
                "estimated_duration": "Ongoing",
                "tools": ["pricing.generate", "checkout.offer.create"],
                "agents": ["ASH", "HAL"]
            }
        ]
        
    def _generate_content_phases(self) -> List[Dict[str, Any]]:
        """Generate phases for a content creation plan."""
        return [
            {
                "phase_id": "phase1",
                "title": "Content Strategy",
                "description": "Develop content strategy and editorial calendar",
                "estimated_duration": "1-2 weeks",
                "tools": ["content.blog.generate", "social.calendar.create"],
                "agents": ["ASH"]
            },
            {
                "phase_id": "phase2",
                "title": "Content Creation",
                "description": "Create and refine content across selected formats",
                "estimated_duration": "2-4 weeks",
                "tools": ["copy.tagline", "video.intro.generate", "product.demo.script"],
                "agents": ["ASH"]
            },
            {
                "phase_id": "phase3",
                "title": "Distribution and Promotion",
                "description": "Distribute content and promote across channels",
                "estimated_duration": "Ongoing",
                "tools": ["copy.email.campaign", "meme.generate", "landing.hero.write"],
                "agents": ["ASH"]
            }
        ]
        
    def _generate_general_phases(self) -> List[Dict[str, Any]]:
        """Generate phases for a general project plan."""
        return [
            {
                "phase_id": "phase1",
                "title": "Research and Planning",
                "description": "Research requirements and develop project plan",
                "estimated_duration": "1-2 weeks",
                "tools": ["content.blog.generate", "design.ui.component.scaffold"],
                "agents": ["ASH", "HAL"]
            },
            {
                "phase_id": "phase2",
                "title": "Development and Implementation",
                "description": "Execute on project plan and develop deliverables",
                "estimated_duration": "3-6 weeks",
                "tools": ["code.write", "api.build", "copy.tagline"],
                "agents": ["HAL", "ASH"]
            },
            {
                "phase_id": "phase3",
                "title": "Review and Launch",
                "description": "Review deliverables, make refinements, and launch",
                "estimated_duration": "1-2 weeks",
                "tools": ["deploy.github.setup", "env.secret.check"],
                "agents": ["HAL", "ASH"]
            }
        ]
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the consultation session to a dictionary.
        
        Returns:
            Dictionary representation of the consultation session
        """
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "operator_id": self.operator_id,
            "mode": self.mode,
            "goal": self.goal,
            "goal_type": self.goal_type,
            "questions": self.questions,
            "current_question_index": self.current_question_index,
            "plan": self.plan
        }
        
    def save(self, directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/sessions") -> str:
        """
        Save the consultation session to a file.
        
        Args:
            directory: Directory to save the session file
            
        Returns:
            Path to the saved session file
        """
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Generate the filename
        filename = f"session_{self.session_id}.json"
        filepath = os.path.join(directory, filename)
        
        # Write the session to file
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
        return filepath
        
    @classmethod
    def load(cls, session_id: str, directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/sessions") -> "ConsultationSession":
        """
        Load a consultation session from a file.
        
        Args:
            session_id: ID of the session to load
            directory: Directory where session files are stored
            
        Returns:
            Loaded ConsultationSession object
        """
        # Generate the filepath
        filename = f"session_{session_id}.json"
        filepath = os.path.join(directory, filename)
        
        # Read the session from file
        with open(filepath, "r") as f:
            session_data = json.load(f)
            
        # Create a new session object
        session = cls(session_data["operator_id"], session_data["goal"])
        
        # Update the session with the loaded data
        session.session_id = session_data["session_id"]
        session.timestamp = session_data["timestamp"]
        session.mode = session_data["mode"]
        session.goal_type = session_data["goal_type"]
        session.questions = session_data["questions"]
        session.current_question_index = session_data["current_question_index"]
        session.plan = session_data["plan"]
        
        return session


class ConsultationManager:
    """
    Manages consultation sessions between the Orchestrator and operators.
    
    This class provides methods for creating, retrieving, and managing
    consultation sessions.
    """
    
    def __init__(self, sessions_directory: str = "/home/ubuntu/workspace/personal-ai-agent/logs/sessions"):
        """
        Initialize the consultation manager.
        
        Args:
            sessions_directory: Directory to store session files
        """
        self.sessions_directory = sessions_directory
        os.makedirs(sessions_directory, exist_ok=True)
        self.active_sessions = {}
        
    def create_session(self, operator_id: str, goal: str) -> ConsultationSession:
        """
        Create a new consultation session.
        
        Args:
            operator_id: ID of the operator
            goal: Initial goal statement from the operator
            
        Returns:
            New ConsultationSession object
        """
        session = ConsultationSession(operator_id, goal)
        self.active_sessions[session.session_id] = session
        session.save(self.sessions_directory)
        return session
        
    def get_session(self, session_id: str) -> ConsultationSession:
        """
        Get an existing consultation session.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            ConsultationSession object
        """
        # Check if the session is already in memory
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
            
        # Try to load the session from file
        try:
            session = ConsultationSession.load(session_id, self.sessions_directory)
            self.active_sessions[session_id] = session
            return session
        except FileNotFoundError:
            raise ValueError(f"Session with ID {session_id} not found")
            
    def answer_question(self, session_id: str, question_id: str, answer: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Record an answer to a question in a consultation session.
        
        Args:
            session_id: ID of the session
            question_id: ID of the question being answered
            answer: Operator's answer to the question
            
        Returns:
            Tuple of (has_more_questions, next_question, plan)
            If has_more_questions is False, plan will contain the generated plan
        """
        session = self.get_session(session_id)
        has_more_questions, next_question = session.answer_question(question_id, answer)
        
        # Save the updated session
        session.save(self.sessions_directory)
        
        # If no more questions, generate the plan
        plan = None
        if not has_more_questions:
            plan = session.generate_plan()
            session.save(self.sessions_directory)
            
        return has_more_questions, next_question, plan
        
    def get_plan(self, session_id: str) -> Dict[str, Any]:
        """
        Get the plan for a consultation session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Plan object
        """
        session = self.get_session(session_id)
        
        # If the plan hasn't been generated yet, generate it
        if session.plan is None:
            # Ensure all questions have been answered
            if any(q["answer"] is None for q in session.questions):
                raise ValueError("Cannot generate plan until all questions have been answered")
                
            session.generate_plan()
            session.save(self.sessions_directory)
            
        return session.plan
        
    def list_sessions(self, operator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all consultation sessions, optionally filtered by operator ID.
        
        Args:
            operator_id: Optional operator ID to filter by
            
        Returns:
            List of session summary dictionaries
        """
        sessions = []
        
        # List all session files in the directory
        for filename in os.listdir(self.sessions_directory):
            if filename.startswith("session_") and filename.endswith(".json"):
                filepath = os.path.join(self.sessions_directory, filename)
                
                try:
                    with open(filepath, "r") as f:
                        session_data = json.load(f)
                        
                    # Filter by operator ID if provided
                    if operator_id is None or session_data["operator_id"] == operator_id:
                        # Create a summary of the session
                        summary = {
                            "session_id": session_data["session_id"],
                            "timestamp": session_data["timestamp"],
                            "operator_id": session_data["operator_id"],
                            "goal": session_data["goal"],
                            "goal_type": session_data["goal_type"],
                            "status": "complete" if session_data["plan"] is not None else "in_progress",
                            "questions_answered": sum(1 for q in session_data["questions"] if q["answer"] is not None),
                            "total_questions": len(session_data["questions"])
                        }
                        
                        sessions.append(summary)
                except Exception as e:
                    print(f"Error loading session from {filepath}: {e}")
                    
        # Sort sessions by timestamp (newest first)
        sessions.sort(key=lambda s: s["timestamp"], reverse=True)
        
        return sessions
