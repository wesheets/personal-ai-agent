"""
Skeptic Agent Module

This module provides functionality to question assumptions, challenge claims,
and provide critical analysis of information.

# memory_tag: recovered_20250427
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class SkepticAgent:
    """
    SkepticAgent challenges assumptions, questions claims, and provides
    critical analysis to prevent groupthink and confirmation bias.
    """
    
    def __init__(self):
        """Initialize the SkepticAgent."""
        self.name = "SkepticAgent"
        self.version = "1.0.0"
        self.description = "Questions assumptions and challenges claims to prevent confirmation bias"
        self.perspective = "Skeptic"
    
    def challenge_claim(self, claim: str, evidence: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Challenges a claim by identifying potential weaknesses and requesting evidence.
        
        Args:
            claim (str): The claim to challenge
            evidence (Optional[List[Dict[str, Any]]]): Optional evidence supporting the claim
            
        Returns:
            Dict[str, Any]: Challenge results with identified weaknesses and questions
        """
        # Initialize result
        result = {
            "claim": claim,
            "has_evidence": evidence is not None and len(evidence) > 0,
            "weaknesses": [],
            "questions": [],
            "challenge_strength": 0.0
        }
        
        # Check for absolute language
        absolute_terms = ["always", "never", "all", "none", "every", "only", "best", "worst"]
        for term in absolute_terms:
            if term.lower() in claim.lower():
                result["weaknesses"].append({
                    "type": "absolute_language",
                    "term": term,
                    "description": f"Claim uses absolute term '{term}' which is rarely defensible"
                })
                result["questions"].append(f"Are there exceptions to this '{term}' statement?")
        
        # Check for vague language
        vague_terms = ["many", "some", "few", "several", "various", "most", "often", "generally"]
        for term in vague_terms:
            if term.lower() in claim.lower():
                result["weaknesses"].append({
                    "type": "vague_language",
                    "term": term,
                    "description": f"Claim uses vague term '{term}' which lacks precision"
                })
                result["questions"].append(f"Can you quantify what '{term}' means in this context?")
        
        # Check for evidence
        if not result["has_evidence"]:
            result["weaknesses"].append({
                "type": "lack_of_evidence",
                "description": "Claim is presented without supporting evidence"
            })
            result["questions"].append("What evidence supports this claim?")
        
        # Calculate challenge strength based on weaknesses
        result["challenge_strength"] = min(1.0, len(result["weaknesses"]) * 0.25)
        
        return result
    
    def evaluate_argument(self, 
        argument: str, 
        supporting_evidence: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates the strength of an argument and its supporting evidence.
        
        Args:
            argument (str): The argument to evaluate
            supporting_evidence (Optional[List[Dict[str, Any]]]): Optional supporting evidence
            
        Returns:
            Dict[str, Any]: Evaluation results with identified logical fallacies and evidence assessment
        """
        # Initialize result
        result = {
            "argument": argument,
            "has_evidence": supporting_evidence is not None and len(supporting_evidence) > 0,
            "logical_fallacies": [],
            "evidence_quality": 0.0,
            "argument_strength": 0.0,
            "questions": []
        }
        
        # Check for common logical fallacies
        fallacies = {
            "ad hominem": ["attack", "character", "person"],
            "straw man": ["misrepresent", "exaggerate", "distort"],
            "false dichotomy": ["either", "or", "only two", "black and white"],
            "appeal to authority": ["expert", "authority", "scientist", "study"],
            "slippery slope": ["lead to", "eventually", "ultimately", "end up"],
            "hasty generalization": ["all", "everyone", "always", "never"]
        }
        
        for fallacy, keywords in fallacies.items():
            for keyword in keywords:
                if keyword.lower() in argument.lower():
                    result["logical_fallacies"].append({
                        "type": fallacy,
                        "keyword": keyword,
                        "description": f"Argument may contain a {fallacy} fallacy"
                    })
                    result["questions"].append(f"Is this argument using a {fallacy} fallacy?")
                    break
        
        # Evaluate evidence quality if provided
        if result["has_evidence"]:
            # Placeholder for evidence quality assessment
            # In a real implementation, this would analyze the credibility and relevance of evidence
            result["evidence_quality"] = 0.7  # Default moderate quality
        else:
            result["evidence_quality"] = 0.0
            result["questions"].append("What evidence supports this argument?")
        
        # Calculate argument strength based on fallacies and evidence
        fallacy_penalty = min(0.8, len(result["logical_fallacies"]) * 0.2)
        result["argument_strength"] = max(0.0, result["evidence_quality"] - fallacy_penalty)
        
        return result
    
    def identify_assumptions(self, statement: str) -> Dict[str, Any]:
        """
        Identifies implicit assumptions in a statement.
        
        Args:
            statement (str): The statement to analyze
            
        Returns:
            Dict[str, Any]: Analysis results with identified assumptions
        """
        # Initialize result
        result = {
            "statement": statement,
            "assumptions": [],
            "questions": []
        }
        
        # Check for common assumption indicators
        assumption_indicators = {
            "value_assumption": ["good", "bad", "better", "worse", "should", "ought", "must"],
            "causal_assumption": ["because", "since", "leads to", "results in", "causes"],
            "factual_assumption": ["obviously", "clearly", "certainly", "everyone knows"]
        }
        
        for assumption_type, indicators in assumption_indicators.items():
            for indicator in indicators:
                if indicator.lower() in statement.lower():
                    result["assumptions"].append({
                        "type": assumption_type,
                        "indicator": indicator,
                        "description": f"Statement contains a {assumption_type.replace('_', ' ')}"
                    })
                    result["questions"].append(f"What {assumption_type.replace('_', ' ')} is being made with '{indicator}'?")
                    break
        
        return result
    
    def generate_counterargument(self, 
        argument: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates a counterargument to challenge the given argument.
        
        Args:
            argument (str): The argument to counter
            context (Optional[Dict[str, Any]]): Optional context information
            
        Returns:
            Dict[str, Any]: Counterargument with reasoning and alternative perspective
        """
        # Initialize result
        result = {
            "original_argument": argument,
            "counterargument": "This claim requires further evidence and consideration of alternative explanations.",
            "reasoning": "Skeptical evaluation suggests the original argument may not account for all factors.",
            "alternative_perspective": "A more balanced view would consider multiple interpretations of the available evidence."
        }
        
        # In a real implementation, this would generate a specific counterargument
        # based on the content of the original argument and available context
        
        return result
    
    def skeptic_analysis(self, 
        content: str, 
        evidence: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Performs a comprehensive skeptical analysis of content.
        
        This is the main entry point for the skeptic agent.
        
        Args:
            content (str): The content to analyze
            evidence (Optional[List[Dict[str, Any]]]): Optional evidence related to the content
            context (Optional[Dict[str, Any]]): Optional context information
            
        Returns:
            Dict[str, Any]: Comprehensive skeptical analysis
        """
        # Challenge claims in the content
        challenge_result = self.challenge_claim(content, evidence)
        
        # Evaluate argument strength
        evaluation_result = self.evaluate_argument(content, evidence)
        
        # Identify assumptions
        assumptions_result = self.identify_assumptions(content)
        
        # Generate counterargument
        counterargument_result = self.generate_counterargument(content, context)
        
        # Compile comprehensive analysis
        timestamp = datetime.utcnow().isoformat()
        
        analysis = {
            "content": content,
            "timestamp": timestamp,
            "challenge_result": challenge_result,
            "evaluation_result": evaluation_result,
            "assumptions_result": assumptions_result,
            "counterargument": counterargument_result,
            "overall_skepticism_score": (challenge_result["challenge_strength"] + 
                                        (1.0 - evaluation_result["argument_strength"]) + 
                                        len(assumptions_result["assumptions"]) * 0.1) / 3,
            "questions_to_consider": challenge_result["questions"] + 
                                    evaluation_result["questions"] + 
                                    assumptions_result["questions"]
        }
        
        return analysis
