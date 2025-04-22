"""
Tests for the enhanced Summary Realism Scorer module.

This module tests the new features added to the Summary Realism Scorer:
- Multi-dimensional scoring
- Advanced NLP techniques
- Reference validation
- Confidence metrics
- Adaptive thresholds
"""

import os
import json
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

from app.modules.summary_realism_scorer import (
    SummaryRealismScorer,
    SummaryDimension,
    AdaptiveThreshold,
    ConfidenceMetric,
    score_summary,
    get_summary_realism_scorer
)

# Test data
TEST_LOOP_ID = "test_loop_123"

# Mock loop data for testing
MOCK_LOOP_DATA = {
    "loop_id": TEST_LOOP_ID,
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

# Test summaries
GOOD_SUMMARY = """
First, the planner agent broke down the problem into manageable steps.
Then, the researcher agent gathered relevant information about the topic.
Finally, the implementer agent created a solution based on the research findings.
The execution referenced the beliefs of accuracy and thoroughness and took 1500ms to complete.
"""

BAD_SUMMARY = """
The implementer agent started working immediately.
Then the researcher found information that wasn't used.
The planner agent didn't contribute anything useful.
The execution took 5000ms and referenced beliefs that weren't actually used.
"""

CONTRADICTORY_SUMMARY = """
The planner agent created a detailed plan.
The planner agent didn't create any plan at all.
The researcher found useful information.
The implementer created a solution that didn't use any research.
"""

@pytest.fixture
def summary_realism_scorer():
    """Create a summary realism scorer instance for testing."""
    with patch('app.modules.summary_realism_scorer.read_from_memory') as mock_read, \
         patch('app.modules.summary_realism_scorer.write_to_memory') as mock_write, \
         patch('app.modules.summary_realism_scorer.NLP_AVAILABLE', True):
        
        # Mock read_from_memory to return test data
        async def mock_read_impl(key):
            if key == f"loop_execution[{TEST_LOOP_ID}]":
                return MOCK_LOOP_DATA
            elif key == "historical_scores":
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
        
        mock_read.side_effect = mock_read_impl
        mock_write.return_value = True
        
        # Create mock NLP components
        with patch('app.modules.summary_realism_scorer.TfidfVectorizer') as mock_tfidf, \
             patch('app.modules.summary_realism_scorer.cosine_similarity') as mock_cosine, \
             patch('app.modules.summary_realism_scorer.WordNetLemmatizer') as mock_lemmatizer, \
             patch('app.modules.summary_realism_scorer.stopwords') as mock_stopwords:
            
            # Mock TF-IDF vectorizer
            mock_tfidf_instance = MagicMock()
            mock_tfidf.return_value = mock_tfidf_instance
            
            # Mock cosine similarity to return reasonable values
            def mock_cosine_impl(matrix1, matrix2):
                # Return higher similarity for good summary, lower for bad
                if "planner agent broke down the problem" in GOOD_SUMMARY:
                    return [[0.85]]
                else:
                    return [[0.4]]
            
            mock_cosine.side_effect = mock_cosine_impl
            
            # Mock lemmatizer
            mock_lemmatizer_instance = MagicMock()
            mock_lemmatizer_instance.lemmatize.side_effect = lambda x: x
            mock_lemmatizer.return_value = mock_lemmatizer_instance
            
            # Mock stopwords
            mock_stopwords.words.return_value = ["a", "an", "the", "and", "or", "but", "in", "on", "at"]
            
            scorer = SummaryRealismScorer()
            yield scorer

class TestSummaryDimension:
    """Tests for the SummaryDimension class."""
    
    def test_summary_dimension_creation(self):
        """Test creating summary dimensions."""
        # Default thresholds
        dimension = SummaryDimension("test_dimension")
        assert dimension.name == "test_dimension"
        assert dimension.weight == 1.0
        assert dimension.threshold_low == 0.3
        assert dimension.threshold_high == 0.7
        
        # Custom values
        dimension = SummaryDimension("custom", weight=0.5, threshold_low=0.2, threshold_high=0.8)
        assert dimension.name == "custom"
        assert dimension.weight == 0.5
        assert dimension.threshold_low == 0.2
        assert dimension.threshold_high == 0.8
    
    def test_get_level(self):
        """Test getting level based on score."""
        dimension = SummaryDimension("test", threshold_low=0.3, threshold_high=0.7)
        
        assert dimension.get_level(0.1) == "low"
        assert dimension.get_level(0.3) == "medium"
        assert dimension.get_level(0.5) == "medium"
        assert dimension.get_level(0.7) == "high"
        assert dimension.get_level(0.9) == "high"
    
    def test_dict_conversion(self):
        """Test converting to and from dictionary."""
        dimension = SummaryDimension("test", weight=0.5, threshold_low=0.2, threshold_high=0.8)
        
        # To dictionary
        dimension_dict = dimension.to_dict()
        assert dimension_dict["name"] == "test"
        assert dimension_dict["weight"] == 0.5
        assert dimension_dict["threshold_low"] == 0.2
        assert dimension_dict["threshold_high"] == 0.8
        
        # From dictionary
        new_dimension = SummaryDimension.from_dict(dimension_dict)
        assert new_dimension.name == dimension.name
        assert new_dimension.weight == dimension.weight
        assert new_dimension.threshold_low == dimension.threshold_low
        assert new_dimension.threshold_high == dimension.threshold_high

class TestAdaptiveThreshold:
    """Tests for the AdaptiveThreshold class."""
    
    def test_adaptive_threshold_creation(self):
        """Test creating adaptive thresholds."""
        # Default values
        threshold = AdaptiveThreshold("test_dimension")
        assert threshold.dimension == "test_dimension"
        assert threshold.low == 0.3
        assert threshold.high == 0.7
        assert threshold.adaptation_rate == 0.1
        assert threshold.history == []
        
        # Custom values
        threshold = AdaptiveThreshold("custom", initial_low=0.2, initial_high=0.8, adaptation_rate=0.2)
        assert threshold.dimension == "custom"
        assert threshold.low == 0.2
        assert threshold.high == 0.8
        assert threshold.adaptation_rate == 0.2
    
    def test_update(self):
        """Test updating thresholds based on new scores."""
        threshold = AdaptiveThreshold("test")
        
        # Add scores
        threshold.update(0.5)
        threshold.update(0.6)
        threshold.update(0.7)
        threshold.update(0.8)
        
        # Not enough history yet
        assert threshold.low == 0.3
        assert threshold.high == 0.7
        
        # Add one more score to trigger adaptation
        threshold.update(0.9)
        
        # Thresholds should have adapted
        assert threshold.low != 0.3
        assert threshold.high != 0.7
        assert threshold.low < threshold.high
    
    def test_get_level(self):
        """Test getting level based on score."""
        threshold = AdaptiveThreshold("test", initial_low=0.4, initial_high=0.6)
        
        assert threshold.get_level(0.3) == "low"
        assert threshold.get_level(0.5) == "medium"
        assert threshold.get_level(0.7) == "high"
    
    def test_dict_conversion(self):
        """Test converting to and from dictionary."""
        threshold = AdaptiveThreshold("test", initial_low=0.2, initial_high=0.8)
        threshold.history = [0.5, 0.6, 0.7]
        
        # To dictionary
        threshold_dict = threshold.to_dict()
        assert threshold_dict["dimension"] == "test"
        assert threshold_dict["low"] == 0.2
        assert threshold_dict["high"] == 0.8
        assert threshold_dict["history"] == [0.5, 0.6, 0.7]
        
        # From dictionary
        new_threshold = AdaptiveThreshold.from_dict(threshold_dict)
        assert new_threshold.dimension == threshold.dimension
        assert new_threshold.low == threshold.low
        assert new_threshold.high == threshold.high
        assert new_threshold.history == threshold.history

class TestConfidenceMetric:
    """Tests for the ConfidenceMetric class."""
    
    def test_confidence_metric_creation(self):
        """Test creating confidence metrics."""
        # Default base confidence
        confidence = ConfidenceMetric()
        assert confidence.base_confidence == 0.5
        assert confidence.factors == {}
        
        # Custom base confidence
        confidence = ConfidenceMetric(base_confidence=0.7)
        assert confidence.base_confidence == 0.7
    
    def test_add_factor(self):
        """Test adding confidence factors."""
        confidence = ConfidenceMetric()
        
        confidence.add_factor("test_factor", 0.2)
        assert "test_factor" in confidence.factors
        assert confidence.factors["test_factor"] == 0.2
    
    def test_calculate(self):
        """Test calculating overall confidence."""
        confidence = ConfidenceMetric(base_confidence=0.5)
        
        # No factors
        assert confidence.calculate() == 0.5
        
        # Add positive factor
        confidence.add_factor("positive", 0.2)
        assert confidence.calculate() > 0.5
        
        # Add negative factor
        confidence.add_factor("negative", -0.1)
        
        # Result should be between 0 and 1
        result = confidence.calculate()
        assert 0 <= result <= 1
    
    def test_get_explanation(self):
        """Test getting explanation of confidence calculation."""
        confidence = ConfidenceMetric()
        
        confidence.add_factor("positive", 0.2)
        confidence.add_factor("negative", -0.1)
        
        explanation = confidence.get_explanation()
        assert len(explanation) == 2
        
        # Check explanation structure
        for item in explanation:
            assert "factor" in item
            assert "value" in item
            assert "impact" in item
            assert "magnitude" in item
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        confidence = ConfidenceMetric(base_confidence=0.6)
        confidence.add_factor("test", 0.1)
        
        result = confidence.to_dict()
        assert "base_confidence" in result
        assert "factors" in result
        assert "overall_confidence" in result
        assert "explanation" in result

class TestSummaryRealismScorerEnhancements:
    """Tests for the enhanced SummaryRealismScorer class."""
    
    @pytest.mark.asyncio
    async def test_multi_dimensional_scoring(self, summary_realism_scorer):
        """Test multi-dimensional scoring of summaries."""
        # Score a good summary
        result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=GOOD_SUMMARY,
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Check for multiple dimensions
        assert "factual_accuracy" in result
        assert "logical_consistency" in result
        assert "emotional_congruence" in result
        assert "temporal_coherence" in result
        
        # Check for overall score
        assert "overall_score" in result
        
        # Check for dimension details
        assert "details" in result
        assert "factual_accuracy" in result["details"]
        assert "logical_consistency" in result["details"]
        assert "emotional_congruence" in result["details"]
        assert "temporal_coherence" in result["details"]
    
    @pytest.mark.asyncio
    async def test_confidence_metrics(self, summary_realism_scorer):
        """Test confidence metrics for scoring."""
        # Score a summary
        result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=GOOD_SUMMARY,
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Check for confidence score
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1
        
        # Check for confidence explanation
        assert "confidence_explanation" in result
        assert isinstance(result["confidence_explanation"], list)
        
        # Score without reference materials
        result_no_ref = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=GOOD_SUMMARY,
            reference_materials={}
        )
        
        # Confidence should be lower without references
        assert result_no_ref["confidence"] < result["confidence"]
    
    @pytest.mark.asyncio
    async def test_adaptive_thresholds(self, summary_realism_scorer):
        """Test adaptive thresholds for scoring levels."""
        # Score a summary
        result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=GOOD_SUMMARY,
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Check for adaptive thresholds
        assert "adaptive_thresholds" in result
        assert "overall" in result["adaptive_thresholds"]
        assert "low" in result["adaptive_thresholds"]["overall"]
        assert "high" in result["adaptive_thresholds"]["overall"]
        
        # Check for levels
        assert "levels" in result
        assert "overall" in result["levels"]
        assert "factual_accuracy" in result["levels"]
        assert "logical_consistency" in result["levels"]
        assert "emotional_congruence" in result["levels"]
        assert "temporal_coherence" in result["levels"]
        
        # Levels should be one of: low, medium, high
        for dimension, level in result["levels"].items():
            assert level in ["low", "medium", "high"]
    
    @pytest.mark.asyncio
    async def test_factual_accuracy_scoring(self, summary_realism_scorer):
        """Test factual accuracy scoring."""
        # Score a good summary
        good_result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=GOOD_SUMMARY,
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Score a bad summary
        bad_result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=BAD_SUMMARY,
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Good summary should have higher factual accuracy
        assert good_result["factual_accuracy"] > bad_result["factual_accuracy"]
        
        # Check for factual details
        assert "key_facts" in good_result["details"]["factual_accuracy"]
        
        # Check for hallucination detection
        assert "hallucinations" in bad_result["details"]["factual_accuracy"]
    
    @pytest.mark.asyncio
    async def test_logical_consistency_scoring(self, summary_realism_scorer):
        """Test logical consistency scoring."""
        # Score a contradictory summary
        contradictory_result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=CONTRADICTORY_SUMMARY,
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Score a good summary
        good_result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=GOOD_SUMMARY,
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Contradictory summary should have lower logical consistency
        assert contradictory_result["logical_consistency"] < good_result["logical_consistency"]
        
        # Check for contradiction detection
        assert "contradictions" in contradictory_result["details"]["logical_consistency"]
        assert len(contradictory_result["details"]["logical_consistency"]["contradictions"]) > 0
    
    @pytest.mark.asyncio
    async def test_temporal_coherence_scoring(self, summary_realism_scorer):
        """Test temporal coherence scoring."""
        # Score a summary with good temporal markers
        good_result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=GOOD_SUMMARY,  # Contains "First", "Then", "Finally"
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Score a summary with poor temporal markers
        bad_result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=BAD_SUMMARY,  # Contains "Then" but in wrong order
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Good summary should have higher temporal coherence
        assert good_result["temporal_coherence"] > bad_result["temporal_coherence"]
        
        # Check for temporal markers
        assert "temporal_markers" in good_result["details"]["temporal_coherence"]
        
        # Check for temporal inconsistencies
        assert "temporal_inconsistencies" in bad_result["details"]["temporal_coherence"]
    
    @pytest.mark.asyncio
    async def test_emotional_congruence_scoring(self, summary_realism_scorer):
        """Test emotional congruence scoring."""
        # Score a summary
        result = await summary_realism_scorer.score_summary(
            loop_id=TEST_LOOP_ID,
            summary=GOOD_SUMMARY,
            reference_materials=MOCK_LOOP_DATA
        )
        
        # Check for emotional tone extraction
        assert "summary_tone" in result["details"]["emotional_congruence"]
        assert "reference_tone" in result["details"]["emotional_congruence"]
        
        # Check for tone similarity
        assert "tone_similarity" in result["details"]["emotional_congruence"]
        assert 0 <= result["details"]["emotional_congruence"]["tone_similarity"] <= 1
    
    @pytest.mark.asyncio
    async def test_get_summary_realism_scorer_function(self):
        """Test the get_summary_realism_scorer function."""
        with patch('app.modules.summary_realism_scorer.SummaryRealismScorer') as mock_scorer:
            # First call should create a new instance
            scorer1 = get_summary_realism_scorer()
            assert mock_scorer.called
            
            # Reset the mock
            mock_scorer.reset_mock()
            
            # Second call should return the existing instance
            scorer2 = get_summary_realism_scorer()
            assert not mock_scorer.called
            assert scorer1 == scorer2
    
    @pytest.mark.asyncio
    async def test_score_summary_function(self, summary_realism_scorer):
        """Test the score_summary function."""
        with patch('app.modules.summary_realism_scorer.get_summary_realism_scorer') as mock_get_scorer:
            mock_get_scorer.return_value = summary_realism_scorer
            
            # Call the function
            result = await score_summary(
                loop_id=TEST_LOOP_ID,
                summary=GOOD_SUMMARY,
                reference_materials=MOCK_LOOP_DATA
            )
            
            # Check that the function returns the expected result
            assert "overall_score" in result
            assert "factual_accuracy" in result
            assert "logical_consistency" in result
            assert "emotional_congruence" in result
            assert "temporal_coherence" in result
            assert "confidence" in result

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
