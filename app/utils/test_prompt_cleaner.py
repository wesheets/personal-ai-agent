# /app/utils/test_prompt_cleaner.py

import unittest
from prompt_cleaner import clean_prompt

class TestPromptCleaner(unittest.TestCase):
    """
    Test cases for the prompt_cleaner module to verify sanitization functionality.
    """
    
    def test_agent_name_sanitization(self):
        """Test that agent names are properly sanitized."""
        test_cases = [
            ("HAL received a message", "Agent received a message"),
            ("ASH is processing data", "Agent is processing data"),
            ("NOVA and ORCHESTRATOR are working", "Agent and Agent are working"),
            ("hal is lowercase", "hal is lowercase"),  # Should not match lowercase
            ("HALOGEN is a chemical", "HALOGEN is a chemical"),  # Should not match partial words
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(clean_prompt(input_text), expected_output)
    
    def test_platform_name_sanitization(self):
        """Test that platform names are properly sanitized."""
        test_cases = [
            ("Welcome to Promethios", "Welcome to the system"),
            ("Life Tree is running", "the system is running"),
            ("LifeTree and Prometheus", "the system and the system"),
            ("prometheus in lowercase", "prometheus in lowercase"),  # Should not match lowercase
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(clean_prompt(input_text), expected_output)
    
    def test_email_sanitization(self):
        """Test that email addresses are properly sanitized."""
        test_cases = [
            ("Contact john@example.com", "Contact [REDACTED_EMAIL]"),
            ("Multiple emails: first.last@domain.co.uk and another@test.org", 
             "Multiple emails: [REDACTED_EMAIL] and [REDACTED_EMAIL]"),
            ("Complex email: user+tag-123@sub.domain-name.com", 
             "Complex email: [REDACTED_EMAIL]"),
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(clean_prompt(input_text), expected_output)
    
    def test_uuid_sanitization(self):
        """Test that UUID-like strings are properly sanitized."""
        test_cases = [
            ("UUID: 550e8400-e29b-41d4-a716-446655440000", 
             "UUID: [REDACTED_UUID]"),
            ("Mixed case UUID: 550E8400-E29B-41D4-A716-446655440000", 
             "Mixed case UUID: [REDACTED_UUID]"),
            ("Multiple UUIDs: 123e4567-e89b-12d3-a456-426614174000 and 123e4567-e89b-12d3-a456-426614174001", 
             "Multiple UUIDs: [REDACTED_UUID] and [REDACTED_UUID]"),
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(clean_prompt(input_text), expected_output)
    
    def test_user_name_sanitization(self):
        """Test that tagged user names are properly sanitized."""
        test_cases = [
            ("user: John Doe", "user: [REDACTED_USER]"),
            ("USER: Jane Smith", "user: [REDACTED_USER]"),
            ("User: Bob Johnson is asking", "user: [REDACTED_USER]"),
            ("username: test123", "username: test123"),  # Should not match 'username:'
        ]
        
        for input_text, expected_output in test_cases:
            self.assertEqual(clean_prompt(input_text), expected_output)
    
    def test_comprehensive_sanitization(self):
        """Test all sanitization patterns together in a complex example."""
        input_text = """
        HAL received a prompt from John Doe at john@doe.com about Life Tree. 
        User: Jane Smith with ID 550e8400-e29b-41d4-a716-446655440000 is using Promethios.
        NOVA and ORCHESTRATOR are processing requests for Prometheus.
        """
        
        # Clean the input and then check if all required elements are sanitized
        cleaned = clean_prompt(input_text)
        self.assertIn("Agent received", cleaned)
        self.assertIn("[REDACTED_EMAIL]", cleaned)
        self.assertIn("about the system", cleaned)
        self.assertIn("user: [REDACTED_USER]", cleaned)
        self.assertIn("[REDACTED_UUID]", cleaned)
        self.assertIn("using the system", cleaned)
        self.assertIn("Agent and Agent", cleaned)
        self.assertIn("requests for the system", cleaned)
    
    def test_provided_test_case(self):
        """Test the specific test case provided in the requirements."""
        input_text = """HAL received a prompt from John Doe at john@doe.com about Life Tree. user: Jane Smith."""
        expected_output = """Agent received a prompt from John Doe at [REDACTED_EMAIL] about the system. user: [REDACTED_USER]."""
        
        self.assertEqual(clean_prompt(input_text), expected_output)


if __name__ == "__main__":
    unittest.main()
