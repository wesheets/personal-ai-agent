"""
Summary Realism Scorer Module

This module provides functionality for evaluating the realism and accuracy of loop summaries.
It supports:
- Multi-dimensional scoring of summary realism
- Advanced NLP techniques for semantic analysis
- Reference validation against source materials
- Confidence metrics for score reliability
- Adaptive thresholds based on context and history

The summary realism scorer helps ensure that loop summaries accurately reflect
the actual execution and outcomes, preventing hallucinations or misrepresentations.
"""

import os
import json
import logging
import asyncio
import time
import re
import math
import statistics
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from datetime import datetime, timedelta
import uuid
from collections import defaultdict, Counter

# For advanced NLP capabilities
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    
    # Download required NLTK resources if not already present
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
    
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    logging.warning("Advanced NLP capabilities not available. Install sklearn and nltk for full functionality.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock function for reading from memory
# In a real implementation, this would read from a database or storage system
async def read_from_memory(key: str) -> Optional[Any]:
    """Read data from memory storage."""
    # Simulate memory read
    await asyncio.sleep(0.1)
    
    # Mock data for testing
    if key.startswith("loop_summary["):
        loop_id = key[13:-1]  # Extract loop_id from "loop_summary[loop_id]"
        return {
            "loop_id": loop_id,
            "summary": "This is a test summary of loop execution.",
            "timestamp": datetime.utcnow().isoformat(),
            "author": "system"
        }
    elif key.startswith("loop_execution["):
        loop_id = key[15:-1]  # Extract loop_id from "loop_execution[loop_id]"
        return {
            "loop_id": loop_id,
            "agents": [
                {
                    "id": "agent_1",
                    "role": "planner",
                    "output": {
                        "text": "Planning to solve the problem by breaking it into steps."
                    }
                },
                {
                    "id": "agent_2",
                    "role": "researcher",
                    "output": {
                        "text": "Researched the topic and found relevant information."
                    }
                },
                {
                    "id": "agent_3",
                    "role": "implementer",
                    "output": {
                        "text": "Implemented the solution based on the research."
                    }
                }
            ],
            "beliefs_referenced": ["accuracy", "thoroughness"],
            "execution_time_ms": 1500,
            "timestamp": datetime.utcnow().isoformat()
        }
    elif key.startswith("realism_score["):
        loop_id = key[14:-1]  # Extract loop_id from "realism_score[loop_id]"
        return {
            "loop_id": loop_id,
            "overall_score": 0.85,
            "factual_accuracy": 0.9,
            "logical_consistency": 0.8,
            "emotional_congruence": 0.85,
            "temporal_coherence": 0.85,
            "confidence": 0.75,
            "timestamp": datetime.utcnow().isoformat()
        }
    elif key.startswith("historical_scores"):
        return [
            {
                "loop_id": "previous_loop_1",
                "overall_score": 0.82,
                "factual_accuracy": 0.88,
                "logical_consistency": 0.79,
                "emotional_congruence": 0.80,
                "temporal_coherence": 0.81,
                "confidence": 0.70,
                "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat()
            },
            {
                "loop_id": "previous_loop_2",
                "overall_score": 0.79,
                "factual_accuracy": 0.85,
                "logical_consistency": 0.76,
                "emotional_congruence": 0.78,
                "temporal_coherence": 0.77,
                "confidence": 0.65,
                "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat()
            }
        ]
    
    return None

# Mock function for writing to memory
# In a real implementation, this would write to a database or storage system
async def write_to_memory(key: str, value: Any) -> bool:
    """Write data to memory storage."""
    # Simulate memory write
    await asyncio.sleep(0.1)
    logger.debug(f"Writing to memory: {key} = {json.dumps(value, indent=2)}")
    return True

class SummaryDimension:
    """Class representing a dimension for summary evaluation."""
    
    def __init__(self, name: str, weight: float = 1.0, 
                threshold_low: float = 0.3, threshold_high: float = 0.7):
        """Initialize a new SummaryDimension."""
        self.name = name
        self.weight = weight
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
    
    def get_level(self, score: float) -> str:
        """Get the level based on the score."""
        if score < self.threshold_low:
            return "low"
        elif score < self.threshold_high:
            return "medium"
        else:
            return "high"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "weight": self.weight,
            "threshold_low": self.threshold_low,
            "threshold_high": self.threshold_high
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SummaryDimension':
        """Create a SummaryDimension from a dictionary."""
        return cls(
            name=data["name"],
            weight=data.get("weight", 1.0),
            threshold_low=data.get("threshold_low", 0.3),
            threshold_high=data.get("threshold_high", 0.7)
        )

class AdaptiveThreshold:
    """Class for managing adaptive thresholds based on historical data."""
    
    def __init__(self, dimension: str, initial_low: float = 0.3, 
                initial_high: float = 0.7, adaptation_rate: float = 0.1):
        """Initialize a new AdaptiveThreshold."""
        self.dimension = dimension
        self.low = initial_low
        self.high = initial_high
        self.adaptation_rate = adaptation_rate
        self.history: List[float] = []
    
    def update(self, score: float) -> None:
        """Update thresholds based on a new score."""
        self.history.append(score)
        
        # Only adapt if we have enough history
        if len(self.history) >= 5:
            # Calculate mean and standard deviation
            mean = statistics.mean(self.history)
            stdev = statistics.stdev(self.history) if len(self.history) > 1 else 0.1
            
            # Adapt thresholds
            self.low = max(0.1, mean - stdev)
            self.high = min(0.9, mean + stdev)
    
    def get_level(self, score: float) -> str:
        """Get the level based on the score."""
        if score < self.low:
            return "low"
        elif score < self.high:
            return "medium"
        else:
            return "high"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "dimension": self.dimension,
            "low": self.low,
            "high": self.high,
            "adaptation_rate": self.adaptation_rate,
            "history": self.history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdaptiveThreshold':
        """Create an AdaptiveThreshold from a dictionary."""
        threshold = cls(
            dimension=data["dimension"],
            initial_low=data.get("low", 0.3),
            initial_high=data.get("high", 0.7),
            adaptation_rate=data.get("adaptation_rate", 0.1)
        )
        threshold.history = data.get("history", [])
        return threshold

class ConfidenceMetric:
    """Class for calculating confidence in realism scores."""
    
    def __init__(self, base_confidence: float = 0.5):
        """Initialize a new ConfidenceMetric."""
        self.base_confidence = base_confidence
        self.factors: Dict[str, float] = {}
    
    def add_factor(self, name: str, value: float) -> None:
        """Add a confidence factor."""
        self.factors[name] = value
    
    def calculate(self) -> float:
        """Calculate overall confidence."""
        if not self.factors:
            return self.base_confidence
        
        # Start with base confidence
        confidence = self.base_confidence
        
        # Apply factors
        for factor_value in self.factors.values():
            # Factors can increase or decrease confidence
            if factor_value > 0:
                # Increase confidence (diminishing returns)
                confidence += (1 - confidence) * factor_value
            else:
                # Decrease confidence
                confidence += confidence * factor_value
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def get_explanation(self) -> List[Dict[str, Any]]:
        """Get explanation of confidence calculation."""
        return [
            {
                "factor": name,
                "value": value,
                "impact": "positive" if value > 0 else "negative",
                "magnitude": abs(value)
            }
            for name, value in self.factors.items()
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "base_confidence": self.base_confidence,
            "factors": self.factors,
            "overall_confidence": self.calculate(),
            "explanation": self.get_explanation()
        }

class SummaryRealismScorer:
    """
    Class for evaluating the realism and accuracy of loop summaries.
    """
    
    def __init__(self):
        """Initialize a new SummaryRealismScorer."""
        # Define dimensions for evaluation
        self.dimensions = {
            "factual_accuracy": SummaryDimension("factual_accuracy", weight=1.0),
            "logical_consistency": SummaryDimension("logical_consistency", weight=0.8),
            "emotional_congruence": SummaryDimension("emotional_congruence", weight=0.6),
            "temporal_coherence": SummaryDimension("temporal_coherence", weight=0.7)
        }
        
        # Initialize adaptive thresholds
        self.adaptive_thresholds = {
            "overall": AdaptiveThreshold("overall"),
            "factual_accuracy": AdaptiveThreshold("factual_accuracy"),
            "logical_consistency": AdaptiveThreshold("logical_consistency"),
            "emotional_congruence": AdaptiveThreshold("emotional_congruence"),
            "temporal_coherence": AdaptiveThreshold("temporal_coherence")
        }
        
        # Initialize NLP components if available
        if NLP_AVAILABLE:
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
        
        # Historical scores for adaptive thresholds
        self.historical_scores = []
        
        logger.info("Initialized summary realism scorer")
    
    async def load_historical_scores(self) -> None:
        """Load historical scores for adaptive thresholds."""
        if not self.historical_scores:
            scores = await read_from_memory("historical_scores")
            if scores:
                self.historical_scores = scores
                
                # Update adaptive thresholds
                for score in scores:
                    self.adaptive_thresholds["overall"].update(score.get("overall_score", 0.5))
                    self.adaptive_thresholds["factual_accuracy"].update(score.get("factual_accuracy", 0.5))
                    self.adaptive_thresholds["logical_consistency"].update(score.get("logical_consistency", 0.5))
                    self.adaptive_thresholds["emotional_congruence"].update(score.get("emotional_congruence", 0.5))
                    self.adaptive_thresholds["temporal_coherence"].update(score.get("temporal_coherence", 0.5))
    
    async def score_summary(self, loop_id: str, summary: Optional[str] = None, 
                          reference_materials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Score the realism of a loop summary.
        
        Args:
            loop_id: The ID of the loop
            summary: Optional summary text (if not provided, will be loaded from memory)
            reference_materials: Optional reference materials for validation
            
        Returns:
            Dictionary with scoring information
        """
        logger.info(f"Scoring summary realism for loop {loop_id}")
        
        # Load historical scores for adaptive thresholds
        await self.load_historical_scores()
        
        # Get summary if not provided
        if not summary:
            summary_data = await read_from_memory(f"loop_summary[{loop_id}]")
            if summary_data:
                summary = summary_data.get("summary", "")
            else:
                return {
                    "error": f"Summary not found for loop {loop_id}",
                    "loop_id": loop_id
                }
        
        # Get reference materials if not provided
        if not reference_materials:
            execution_data = await read_from_memory(f"loop_execution[{loop_id}]")
            if execution_data:
                reference_materials = execution_data
            else:
                reference_materials = {}
        
        # Initialize confidence metric
        confidence = ConfidenceMetric()
        
        # Add confidence factor based on reference materials
        if reference_materials:
            confidence.add_factor("reference_materials_available", 0.2)
        else:
            confidence.add_factor("reference_materials_missing", -0.3)
        
        # Score each dimension
        factual_accuracy, factual_details = self._score_factual_accuracy(summary, reference_materials)
        logical_consistency, logical_details = self._score_logical_consistency(summary, reference_materials)
        emotional_congruence, emotional_details = self._score_emotional_congruence(summary, reference_materials)
        temporal_coherence, temporal_details = self._score_temporal_coherence(summary, reference_materials)
        
        # Add confidence factors based on scoring details
        if factual_details.get("reference_match_count", 0) > 0:
            confidence.add_factor("factual_references", 0.15)
        
        if logical_details.get("contradiction_count", 0) > 0:
            confidence.add_factor("logical_contradictions", -0.2)
        
        # Calculate overall score with dimension weights
        total_weight = sum(dim.weight for dim in self.dimensions.values())
        overall_score = (
            factual_accuracy * self.dimensions["factual_accuracy"].weight +
            logical_consistency * self.dimensions["logical_consistency"].weight +
            emotional_congruence * self.dimensions["emotional_congruence"].weight +
            temporal_coherence * self.dimensions["temporal_coherence"].weight
        ) / total_weight
        
        # Update adaptive thresholds
        self.adaptive_thresholds["overall"].update(overall_score)
        self.adaptive_thresholds["factual_accuracy"].update(factual_accuracy)
        self.adaptive_thresholds["logical_consistency"].update(logical_consistency)
        self.adaptive_thresholds["emotional_congruence"].update(emotional_congruence)
        self.adaptive_thresholds["temporal_coherence"].update(temporal_coherence)
        
        # Calculate overall confidence
        overall_confidence = confidence.calculate()
        
        # Create result
        result = {
            "loop_id": loop_id,
            "overall_score": round(overall_score, 2),
            "factual_accuracy": round(factual_accuracy, 2),
            "logical_consistency": round(logical_consistency, 2),
            "emotional_congruence": round(emotional_congruence, 2),
            "temporal_coherence": round(temporal_coherence, 2),
            "confidence": round(overall_confidence, 2),
            "confidence_explanation": confidence.get_explanation(),
            "adaptive_thresholds": {
                "overall": {
                    "low": round(self.adaptive_thresholds["overall"].low, 2),
                    "high": round(self.adaptive_thresholds["overall"].high, 2)
                }
            },
            "levels": {
                "overall": self.adaptive_thresholds["overall"].get_level(overall_score),
                "factual_accuracy": self.adaptive_thresholds["factual_accuracy"].get_level(factual_accuracy),
                "logical_consistency": self.adaptive_thresholds["logical_consistency"].get_level(logical_consistency),
                "emotional_congruence": self.adaptive_thresholds["emotional_congruence"].get_level(emotional_congruence),
                "temporal_coherence": self.adaptive_thresholds["temporal_coherence"].get_level(temporal_coherence)
            },
            "details": {
                "factual_accuracy": factual_details,
                "logical_consistency": logical_details,
                "emotional_congruence": emotional_details,
                "temporal_coherence": temporal_details
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Save to memory
        await write_to_memory(f"realism_score[{loop_id}]", result)
        
        # Add to historical scores
        self.historical_scores.append({
            "loop_id": loop_id,
            "overall_score": result["overall_score"],
            "factual_accuracy": result["factual_accuracy"],
            "logical_consistency": result["logical_consistency"],
            "emotional_congruence": result["emotional_congruence"],
            "temporal_coherence": result["temporal_coherence"],
            "confidence": result["confidence"],
            "timestamp": result["timestamp"]
        })
        
        # Save historical scores
        await write_to_memory("historical_scores", self.historical_scores)
        
        logger.info(f"Scored summary realism for loop {loop_id}: {overall_score:.2f}")
        
        return result
    
    def _score_factual_accuracy(self, summary: str, reference_materials: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score factual accuracy of a summary.
        
        Args:
            summary: The summary text
            reference_materials: Reference materials for validation
            
        Returns:
            Tuple of (score, details)
        """
        details = {}
        
        # Extract key facts from reference materials
        key_facts = self._extract_key_facts(reference_materials)
        details["key_facts"] = key_facts
        
        # Check for presence of key facts in summary
        if NLP_AVAILABLE and key_facts:
            # Use semantic similarity for more accurate matching
            fact_matches = []
            summary_sentences = sent_tokenize(summary)
            
            for fact in key_facts:
                best_match_score = 0
                best_match_sentence = ""
                
                for sentence in summary_sentences:
                    similarity = self._calculate_semantic_similarity(fact, sentence)
                    if similarity > best_match_score:
                        best_match_score = similarity
                        best_match_sentence = sentence
                
                if best_match_score > 0.5:  # Threshold for considering it a match
                    fact_matches.append({
                        "fact": fact,
                        "match": best_match_sentence,
                        "similarity": round(best_match_score, 2)
                    })
            
            details["fact_matches"] = fact_matches
            details["reference_match_count"] = len(fact_matches)
            
            # Calculate score based on match ratio and similarity
            if key_facts:
                match_ratio = len(fact_matches) / len(key_facts)
                avg_similarity = (
                    sum(match["similarity"] for match in fact_matches) / len(fact_matches)
                    if fact_matches else 0
                )
                
                # Combine match ratio and similarity
                score = 0.7 * match_ratio + 0.3 * avg_similarity
            else:
                score = 0.5  # Neutral score if no key facts
        else:
            # Fallback to simpler method if NLP not available
            if key_facts:
                matches = 0
                for fact in key_facts:
                    if fact.lower() in summary.lower():
                        matches += 1
                
                score = matches / len(key_facts) if key_facts else 0.5
            else:
                score = 0.5  # Neutral score if no key facts
            
            details["reference_match_count"] = matches if 'matches' in locals() else 0
        
        # Check for hallucinations (facts in summary not in reference)
        hallucinations = self._detect_hallucinations(summary, reference_materials)
        details["hallucinations"] = hallucinations
        
        # Adjust score based on hallucinations
        if hallucinations:
            hallucination_penalty = min(0.5, len(hallucinations) * 0.1)
            score = max(0.1, score - hallucination_penalty)
            details["hallucination_penalty"] = hallucination_penalty
        
        return score, details
    
    def _score_logical_consistency(self, summary: str, reference_materials: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score logical consistency of a summary.
        
        Args:
            summary: The summary text
            reference_materials: Reference materials for validation
            
        Returns:
            Tuple of (score, details)
        """
        details = {}
        
        # Check for internal contradictions in summary
        contradictions = self._detect_contradictions(summary)
        details["contradictions"] = contradictions
        details["contradiction_count"] = len(contradictions)
        
        # Check for logical flow
        logical_flow_score = self._evaluate_logical_flow(summary)
        details["logical_flow_score"] = logical_flow_score
        
        # Check for consistency with reference materials
        if reference_materials:
            reference_consistency = self._evaluate_reference_consistency(summary, reference_materials)
            details["reference_consistency"] = reference_consistency
        else:
            reference_consistency = 0.5  # Neutral score if no references
        
        # Calculate overall logical consistency score
        if contradictions:
            contradiction_penalty = min(0.5, len(contradictions) * 0.15)
            base_score = max(0.1, 1.0 - contradiction_penalty)
        else:
            base_score = 0.9  # High base score if no contradictions
        
        # Combine with logical flow and reference consistency
        score = (
            0.5 * base_score +
            0.3 * logical_flow_score +
            0.2 * reference_consistency
        )
        
        return score, details
    
    def _score_emotional_congruence(self, summary: str, reference_materials: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score emotional congruence of a summary.
        
        Args:
            summary: The summary text
            reference_materials: Reference materials for validation
            
        Returns:
            Tuple of (score, details)
        """
        details = {}
        
        # Extract emotional tone from summary
        summary_tone = self._extract_emotional_tone(summary)
        details["summary_tone"] = summary_tone
        
        # Extract emotional tone from reference materials
        reference_tone = self._extract_emotional_tone_from_references(reference_materials)
        details["reference_tone"] = reference_tone
        
        # Compare tones
        if summary_tone and reference_tone:
            tone_similarity = self._calculate_tone_similarity(summary_tone, reference_tone)
            details["tone_similarity"] = tone_similarity
            score = tone_similarity
        else:
            score = 0.5  # Neutral score if tones couldn't be extracted
        
        return score, details
    
    def _score_temporal_coherence(self, summary: str, reference_materials: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score temporal coherence of a summary.
        
        Args:
            summary: The summary text
            reference_materials: Reference materials for validation
            
        Returns:
            Tuple of (score, details)
        """
        details = {}
        
        # Extract temporal markers from summary
        temporal_markers = self._extract_temporal_markers(summary)
        details["temporal_markers"] = temporal_markers
        
        # Check for temporal inconsistencies
        temporal_inconsistencies = self._detect_temporal_inconsistencies(summary)
        details["temporal_inconsistencies"] = temporal_inconsistencies
        
        # Extract sequence from reference materials
        reference_sequence = self._extract_reference_sequence(reference_materials)
        details["reference_sequence"] = reference_sequence
        
        # Compare summary sequence with reference sequence
        if reference_sequence and temporal_markers:
            sequence_alignment = self._calculate_sequence_alignment(temporal_markers, reference_sequence)
            details["sequence_alignment"] = sequence_alignment
            
            # Calculate score based on alignment and inconsistencies
            if temporal_inconsistencies:
                inconsistency_penalty = min(0.5, len(temporal_inconsistencies) * 0.1)
                score = max(0.1, sequence_alignment - inconsistency_penalty)
            else:
                score = sequence_alignment
        else:
            # If no temporal markers or reference sequence, check for inconsistencies only
            if temporal_inconsistencies:
                inconsistency_penalty = min(0.5, len(temporal_inconsistencies) * 0.1)
                score = max(0.1, 0.7 - inconsistency_penalty)  # Start from 0.7 (decent) and penalize
            else:
                score = 0.7  # Decent score if no inconsistencies
        
        return score, details
    
    def _extract_key_facts(self, reference_materials: Dict[str, Any]) -> List[str]:
        """
        Extract key facts from reference materials.
        
        Args:
            reference_materials: Reference materials
            
        Returns:
            List of key facts
        """
        facts = []
        
        # Extract from agent outputs
        agents = reference_materials.get("agents", [])
        for agent in agents:
            output = agent.get("output", {}).get("text", "")
            if output:
                # Split into sentences and add as facts
                sentences = sent_tokenize(output)
                facts.extend(sentences)
        
        # Extract from beliefs referenced
        beliefs = reference_materials.get("beliefs_referenced", [])
        for belief in beliefs:
            facts.append(f"Referenced belief: {belief}")
        
        # Extract from execution time
        execution_time = reference_materials.get("execution_time_ms")
        if execution_time:
            facts.append(f"Execution time: {execution_time} ms")
        
        return facts
    
    def _detect_hallucinations(self, summary: str, reference_materials: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect potential hallucinations in the summary.
        
        Args:
            summary: The summary text
            reference_materials: Reference materials
            
        Returns:
            List of potential hallucinations
        """
        hallucinations = []
        
        if not NLP_AVAILABLE:
            return hallucinations
        
        # Extract named entities and key terms from summary
        summary_entities = self._extract_entities(summary)
        
        # Extract named entities and key terms from reference materials
        reference_text = ""
        for agent in reference_materials.get("agents", []):
            output = agent.get("output", {}).get("text", "")
            if output:
                reference_text += " " + output
        
        reference_entities = self._extract_entities(reference_text)
        
        # Find entities in summary not in reference
        for entity in summary_entities:
            found = False
            for ref_entity in reference_entities:
                similarity = self._calculate_semantic_similarity(entity, ref_entity)
                if similarity > 0.7:  # High similarity threshold
                    found = True
                    break
            
            if not found:
                # Extract context
                context = self._extract_entity_context(summary, entity)
                
                hallucinations.append({
                    "entity": entity,
                    "context": context,
                    "confidence": 0.7  # Confidence in hallucination detection
                })
        
        return hallucinations
    
    def _extract_entities(self, text: str) -> List[str]:
        """
        Extract named entities and key terms from text.
        
        Args:
            text: The text to extract from
            
        Returns:
            List of entities
        """
        if not NLP_AVAILABLE:
            return []
        
        # Simple entity extraction using noun phrases
        # In a real implementation, this would use NER
        entities = []
        
        # Tokenize and tag parts of speech
        tokens = word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
        
        # Extract noun phrases (simple approach)
        i = 0
        while i < len(pos_tags):
            if pos_tags[i][1].startswith('NN'):  # Noun
                # Check if it's part of a noun phrase
                phrase = [pos_tags[i][0]]
                j = i + 1
                while j < len(pos_tags) and pos_tags[j][1].startswith('NN'):
                    phrase.append(pos_tags[j][0])
                    j += 1
                
                if len(phrase) > 1:
                    entities.append(' '.join(phrase))
                    i = j
                else:
                    # Single noun, check if it's capitalized (potential named entity)
                    if pos_tags[i][0][0].isupper() and pos_tags[i][0].lower() not in self.stop_words:
                        entities.append(pos_tags[i][0])
                    i += 1
            else:
                i += 1
        
        return entities
    
    def _extract_entity_context(self, text: str, entity: str) -> str:
        """
        Extract context around an entity in text.
        
        Args:
            text: The text to extract from
            entity: The entity to find context for
            
        Returns:
            Context string
        """
        # Find the entity in the text
        index = text.lower().find(entity.lower())
        if index == -1:
            return ""
        
        # Extract context (50 characters before and after)
        start = max(0, index - 50)
        end = min(len(text), index + len(entity) + 50)
        
        return text[start:end]
    
    def _detect_contradictions(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect contradictions within text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of contradictions
        """
        contradictions = []
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        if NLP_AVAILABLE and len(sentences) > 1:
            # Compare each pair of sentences for contradictions
            for i in range(len(sentences)):
                for j in range(i+1, len(sentences)):
                    # Check for negation patterns
                    if self._contains_contradiction(sentences[i], sentences[j]):
                        contradictions.append({
                            "sentence1": sentences[i],
                            "sentence2": sentences[j],
                            "confidence": 0.8
                        })
        
        return contradictions
    
    def _contains_contradiction(self, sentence1: str, sentence2: str) -> bool:
        """
        Check if two sentences contain a contradiction.
        
        Args:
            sentence1: First sentence
            sentence2: Second sentence
            
        Returns:
            True if contradiction detected, False otherwise
        """
        if not NLP_AVAILABLE:
            return False
        
        # Simple contradiction detection using negation patterns
        # In a real implementation, this would use more sophisticated NLP
        
        # Check for direct negation
        negation_words = ["not", "no", "never", "isn't", "aren't", "wasn't", "weren't", "doesn't", "don't", "didn't"]
        
        # Tokenize and lemmatize
        tokens1 = [self.lemmatizer.lemmatize(token.lower()) for token in word_tokenize(sentence1)]
        tokens2 = [self.lemmatizer.lemmatize(token.lower()) for token in word_tokenize(sentence2)]
        
        # Check for shared content words
        content_words1 = [token for token in tokens1 if token not in self.stop_words]
        content_words2 = [token for token in tokens2 if token not in self.stop_words]
        
        shared_words = set(content_words1).intersection(set(content_words2))
        
        # If sentences share content words and one contains negation
        if shared_words and (
            any(neg in tokens1 for neg in negation_words) != any(neg in tokens2 for neg in negation_words)
        ):
            return True
        
        return False
    
    def _evaluate_logical_flow(self, text: str) -> float:
        """
        Evaluate logical flow of text.
        
        Args:
            text: The text to evaluate
            
        Returns:
            Score for logical flow
        """
        # Check for logical connectors
        logical_connectors = ["because", "therefore", "thus", "consequently", "as a result", "since", "so", "hence"]
        
        # Count logical connectors
        connector_count = sum(1 for connector in logical_connectors if connector in text.lower())
        
        # Split into sentences
        sentences = sent_tokenize(text)
        
        # Calculate connector density
        if len(sentences) > 1:
            connector_density = connector_count / (len(sentences) - 1)
        else:
            connector_density = 0
        
        # Score based on connector density
        if connector_density > 0.5:
            return 0.9  # Excellent logical flow
        elif connector_density > 0.3:
            return 0.8  # Good logical flow
        elif connector_density > 0.1:
            return 0.7  # Decent logical flow
        else:
            return 0.5  # Neutral logical flow
    
    def _evaluate_reference_consistency(self, summary: str, reference_materials: Dict[str, Any]) -> float:
        """
        Evaluate consistency between summary and reference materials.
        
        Args:
            summary: The summary text
            reference_materials: Reference materials
            
        Returns:
            Consistency score
        """
        if not NLP_AVAILABLE:
            return 0.5  # Neutral score if NLP not available
        
        # Extract reference text
        reference_text = ""
        for agent in reference_materials.get("agents", []):
            output = agent.get("output", {}).get("text", "")
            if output:
                reference_text += " " + output
        
        if not reference_text:
            return 0.5  # Neutral score if no reference text
        
        # Calculate semantic similarity
        similarity = self._calculate_semantic_similarity(summary, reference_text)
        
        return similarity
    
    def _extract_emotional_tone(self, text: str) -> Dict[str, float]:
        """
        Extract emotional tone from text.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary of emotion -> intensity
        """
        # Simple emotion detection using keyword matching
        # In a real implementation, this would use sentiment analysis
        
        emotion_keywords = {
            "positive": ["good", "great", "excellent", "success", "happy", "pleased", "satisfied"],
            "negative": ["bad", "poor", "failure", "sad", "disappointed", "unsatisfied"],
            "neutral": ["average", "moderate", "standard", "normal", "typical"],
            "confident": ["certain", "confident", "sure", "definitely", "clearly"],
            "uncertain": ["maybe", "perhaps", "possibly", "uncertain", "unclear"]
        }
        
        # Count occurrences of emotion keywords
        emotion_counts = {emotion: 0 for emotion in emotion_keywords}
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                emotion_counts[emotion] += len(re.findall(r'\b' + keyword + r'\b', text.lower()))
        
        # Normalize counts to intensities
        total_count = sum(emotion_counts.values())
        if total_count > 0:
            emotion_intensities = {emotion: count / total_count for emotion, count in emotion_counts.items()}
        else:
            # Default to neutral if no emotion keywords found
            emotion_intensities = {emotion: 0.2 for emotion in emotion_keywords}
            emotion_intensities["neutral"] = 0.4
        
        return emotion_intensities
    
    def _extract_emotional_tone_from_references(self, reference_materials: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract emotional tone from reference materials.
        
        Args:
            reference_materials: Reference materials
            
        Returns:
            Dictionary of emotion -> intensity
        """
        # Extract text from reference materials
        reference_text = ""
        for agent in reference_materials.get("agents", []):
            output = agent.get("output", {}).get("text", "")
            if output:
                reference_text += " " + output
        
        if not reference_text:
            # Default to neutral if no reference text
            return {
                "positive": 0.2,
                "negative": 0.2,
                "neutral": 0.4,
                "confident": 0.1,
                "uncertain": 0.1
            }
        
        return self._extract_emotional_tone(reference_text)
    
    def _calculate_tone_similarity(self, tone1: Dict[str, float], tone2: Dict[str, float]) -> float:
        """
        Calculate similarity between two emotional tones.
        
        Args:
            tone1: First emotional tone
            tone2: Second emotional tone
            
        Returns:
            Similarity score
        """
        if not tone1 or not tone2:
            return 0.5  # Neutral score if tones not available
        
        # Calculate Euclidean distance between tone vectors
        squared_diff_sum = sum((tone1.get(emotion, 0) - tone2.get(emotion, 0)) ** 2 
                              for emotion in set(tone1.keys()).union(set(tone2.keys())))
        distance = math.sqrt(squared_diff_sum)
        
        # Convert distance to similarity (1 - normalized distance)
        # Max possible distance is sqrt(2) for normalized vectors
        similarity = 1 - min(1.0, distance / math.sqrt(2))
        
        return similarity
    
    def _extract_temporal_markers(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract temporal markers from text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of temporal markers
        """
        # Define temporal marker patterns
        temporal_patterns = [
            (r'\bfirst\b', 1),
            (r'\bsecond\b', 2),
            (r'\bthird\b', 3),
            (r'\bfourth\b', 4),
            (r'\bfifth\b', 5),
            (r'\bnext\b', None),
            (r'\bthen\b', None),
            (r'\bafter\b', None),
            (r'\bbefore\b', None),
            (r'\binitially\b', 1),
            (r'\bfinally\b', 999)  # High number to indicate last
        ]
        
        markers = []
        
        # Find all sentences with temporal markers
        sentences = sent_tokenize(text)
        
        for i, sentence in enumerate(sentences):
            for pattern, order in temporal_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    # If order is None, use sentence position
                    if order is None:
                        order = i + 1
                    
                    markers.append({
                        "marker": re.search(pattern, sentence, re.IGNORECASE).group(),
                        "sentence": sentence,
                        "position": i,
                        "order": order
                    })
        
        # Sort by order
        markers.sort(key=lambda x: x["order"])
        
        return markers
    
    def _detect_temporal_inconsistencies(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect temporal inconsistencies in text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of temporal inconsistencies
        """
        inconsistencies = []
        
        # Extract temporal markers
        markers = self._extract_temporal_markers(text)
        
        # Check for position vs order inconsistencies
        for i in range(len(markers) - 1):
            current = markers[i]
            next_marker = markers[i + 1]
            
            # If position is out of order
            if current["position"] > next_marker["position"]:
                inconsistencies.append({
                    "type": "order_position_mismatch",
                    "marker1": current["marker"],
                    "marker2": next_marker["marker"],
                    "sentence1": current["sentence"],
                    "sentence2": next_marker["sentence"],
                    "description": f"Marker '{current['marker']}' (order {current['order']}) appears after '{next_marker['marker']}' (order {next_marker['order']}) in the text"
                })
        
        return inconsistencies
    
    def _extract_reference_sequence(self, reference_materials: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract sequence information from reference materials.
        
        Args:
            reference_materials: Reference materials
            
        Returns:
            List of sequence steps
        """
        sequence = []
        
        # Extract from agent outputs in order
        agents = reference_materials.get("agents", [])
        for i, agent in enumerate(agents):
            sequence.append({
                "step": i + 1,
                "agent_id": agent.get("id", f"agent_{i+1}"),
                "role": agent.get("role", "unknown"),
                "text": agent.get("output", {}).get("text", "")
            })
        
        return sequence
    
    def _calculate_sequence_alignment(self, markers: List[Dict[str, Any]], 
                                    reference_sequence: List[Dict[str, Any]]) -> float:
        """
        Calculate alignment between summary sequence and reference sequence.
        
        Args:
            markers: Temporal markers from summary
            reference_sequence: Sequence from reference materials
            
        Returns:
            Alignment score
        """
        if not markers or not reference_sequence:
            return 0.5  # Neutral score if no sequence information
        
        # Check if number of steps matches
        steps_match_score = 1.0 - min(1.0, abs(len(markers) - len(reference_sequence)) / max(len(markers), len(reference_sequence)))
        
        # Check content alignment
        content_alignment_scores = []
        
        for i, marker in enumerate(markers):
            if i < len(reference_sequence):
                ref_step = reference_sequence[i]
                
                # Calculate similarity between marker sentence and reference step
                if NLP_AVAILABLE:
                    similarity = self._calculate_semantic_similarity(marker["sentence"], ref_step["text"])
                else:
                    # Simple word overlap
                    marker_words = set(word_tokenize(marker["sentence"].lower()))
                    ref_words = set(word_tokenize(ref_step["text"].lower()))
                    
                    if marker_words and ref_words:
                        overlap = len(marker_words.intersection(ref_words))
                        similarity = overlap / min(len(marker_words), len(ref_words))
                    else:
                        similarity = 0
                
                content_alignment_scores.append(similarity)
        
        # Calculate average content alignment
        avg_content_alignment = (
            sum(content_alignment_scores) / len(content_alignment_scores)
            if content_alignment_scores else 0.5
        )
        
        # Combine scores
        alignment_score = 0.4 * steps_match_score + 0.6 * avg_content_alignment
        
        return alignment_score
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score
        """
        if not NLP_AVAILABLE:
            return 0.5  # Neutral score if NLP not available
        
        # Handle empty texts
        if not text1 or not text2:
            return 0
        
        try:
            # Create TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity
        except Exception as e:
            logger.warning(f"Error calculating semantic similarity: {e}")
            
            # Fallback to simpler method
            words1 = set(word.lower() for word in word_tokenize(text1) if word.lower() not in self.stop_words)
            words2 = set(word.lower() for word in word_tokenize(text2) if word.lower() not in self.stop_words)
            
            if not words1 or not words2:
                return 0
            
            # Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0

# Global summary realism scorer instance
_summary_realism_scorer = None

def get_summary_realism_scorer() -> SummaryRealismScorer:
    """
    Get the global summary realism scorer instance.
    
    Returns:
        SummaryRealismScorer instance
    """
    global _summary_realism_scorer
    if _summary_realism_scorer is None:
        _summary_realism_scorer = SummaryRealismScorer()
    
    return _summary_realism_scorer

async def score_summary(loop_id: str, summary: Optional[str] = None, 
                      reference_materials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Score the realism of a loop summary.
    
    Args:
        loop_id: The ID of the loop
        summary: Optional summary text (if not provided, will be loaded from memory)
        reference_materials: Optional reference materials for validation
        
    Returns:
        Dictionary with scoring information
    """
    scorer = get_summary_realism_scorer()
    return await scorer.score_summary(loop_id, summary, reference_materials)
