# /app/modules/test_llm_infer.py

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the parent directory to sys.path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.modules.llm_infer import LLMInferenceModule, infer_with_llm
from app.utils.prompt_cleaner import clean_prompt

class TestLLMInferModule(unittest.TestCase):
    """
    Test cases for the LLMInferenceModule to verify integration with prompt_cleaner.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variable for API key
        os.environ["OPENAI_API_KEY"] = "test_api_key"
        self.llm_module = LLMInferenceModule()
    
    @patch('app.modules.llm_infer.requests.post')
    def test_prompt_sanitization_in_infer(self, mock_post):
        """Test that prompts are sanitized before being sent to the LLM API."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is a test response"}}]
        }
        mock_post.return_value = mock_response
        
        # Test prompt with elements that should be sanitized
        test_prompt = "HAL received a message from john@example.com about Life Tree. user: John Doe"
        expected_sanitized = "Agent received a message from [REDACTED_EMAIL] about the system. user: [REDACTED_USER]"
        
        # Call the infer method
        self.llm_module.infer(test_prompt)
        
        # Get the payload that was sent to the API
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]['data'])
        
        # Verify that the sanitized prompt was used in the API call
        self.assertEqual(payload['messages'][0]['content'], expected_sanitized)
    
    @patch('app.modules.llm_infer.LLMInferenceModule')
    def test_convenience_function(self, mock_module_class):
        """Test that the convenience function properly uses the LLMInferenceModule."""
        # Mock the module instance and its infer method
        mock_instance = MagicMock()
        mock_module_class.return_value = mock_instance
        mock_instance.infer.return_value = {"result": "test"}
        
        # Test the convenience function
        test_prompt = "HAL received a message"
        result = infer_with_llm(test_prompt, api_key="test_key")
        
        # Verify that the module was instantiated with the correct API key
        mock_module_class.assert_called_once_with("test_key")
        
        # Verify that the infer method was called with the correct prompt
        mock_instance.infer.assert_called_once_with(test_prompt, "gpt-4")
        
        # Verify that the result is correctly returned
        self.assertEqual(result, {"result": "test"})
    
    def test_direct_integration_with_prompt_cleaner(self):
        """Test direct integration between llm_infer and prompt_cleaner."""
        # Test prompt with elements that should be sanitized
        test_prompt = """
        HAL and NOVA are processing a request from user: Jane Smith with ID 550e8400-e29b-41d4-a716-446655440000.
        Please contact support@lifetree.com if you have questions about Promethios.
        """
        
        # Clean the prompt directly using the prompt_cleaner
        sanitized = clean_prompt(test_prompt)
        
        # Verify that all elements are properly sanitized
        self.assertIn("Agent and Agent", sanitized)
        self.assertIn("user: [REDACTED_USER]", sanitized)
        self.assertIn("[REDACTED_UUID]", sanitized)
        self.assertIn("[REDACTED_EMAIL]", sanitized)
        self.assertIn("the system", sanitized)
        self.assertNotIn("HAL", sanitized)
        self.assertNotIn("NOVA", sanitized)
        self.assertNotIn("Jane Smith", sanitized)
        self.assertNotIn("550e8400-e29b-41d4-a716-446655440000", sanitized)
        self.assertNotIn("support@lifetree.com", sanitized)
        self.assertNotIn("Promethios", sanitized)


if __name__ == "__main__":
    unittest.main()
