import unittest
import json
import os
import sys

# Adjust path to import from app
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Correctly navigate up to the project root from the script's location
# tests/standalone/batch_26_1_tests -> tests/standalone -> tests -> personal-ai-agent (PROJECT_ROOT)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
APP_DIR_FOR_IMPORT = os.path.join(PROJECT_ROOT, "app")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# It's generally better to add the directory *containing* 'app' to sys.path,
# and then import as 'from app.validators...'
# So, adding PROJECT_ROOT is usually sufficient if 'app' is directly under it.

from app.validators.assess_drift_awareness import assess_drift_awareness

class TestAssessDriftAwarenessStandalone(unittest.TestCase):

    def test_assess_drift_awareness_high_awareness(self):
        """Test assess_drift_awareness with high awareness score."""
        current_emotion_profile = {"happiness": 0.2}
        historical_emotion_data = [
            {"happiness": 0.8, "sadness": 0.2, "timestamp": "2023-01-01T12:00:00Z"},
            {"happiness": 0.7, "sadness": 0.3, "timestamp": "2023-01-01T12:05:00Z"}
        ]
        awareness_score = assess_drift_awareness("test_agent", current_emotion_profile, historical_emotion_data)
        self.assertGreaterEqual(awareness_score, 0.8) # Expecting high awareness

    def test_assess_drift_awareness_low_awareness(self):
        """Test assess_drift_awareness with low awareness score."""
        current_emotion_profile = {"happiness": 0.7}
        historical_emotion_data = [
            {"happiness": 0.8, "sadness": 0.2, "timestamp": "2023-01-01T12:00:00Z"},
            {"happiness": 0.75, "sadness": 0.25, "timestamp": "2023-01-01T12:05:00Z"}
        ]
        awareness_score = assess_drift_awareness("test_agent", current_emotion_profile, historical_emotion_data)
        self.assertLess(awareness_score, 0.3) # Expecting low awareness

    def test_assess_drift_awareness_no_history(self):
        """Test assess_drift_awareness with no historical data."""
        current_emotion_profile = {"happiness": 0.5}
        historical_emotion_data = []
        awareness_score = assess_drift_awareness("test_agent", current_emotion_profile, historical_emotion_data)
        self.assertEqual(awareness_score, 0.0) # Expecting 0.0 for no history

if __name__ == '__main__':
    unittest.main()
