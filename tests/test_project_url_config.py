import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.modules.project import trigger_plan_generation, PLAN_GENERATION_URL

class TestProjectInitiateEndpoint(unittest.TestCase):
    """Test the project initiate endpoint and URL configuration."""
    
    def setUp(self):
        """Set up test environment."""
        # Save original environment variable if it exists
        self.original_url = os.environ.get('PLAN_GENERATION_URL')
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment variable
        if self.original_url:
            os.environ['PLAN_GENERATION_URL'] = self.original_url
        elif 'PLAN_GENERATION_URL' in os.environ:
            del os.environ['PLAN_GENERATION_URL']
    
    def test_default_url_configuration(self):
        """Test that the default URL is used when no environment variable is set."""
        # Remove environment variable if it exists
        if 'PLAN_GENERATION_URL' in os.environ:
            del os.environ['PLAN_GENERATION_URL']
        
        # Import the module again to reload the PLAN_GENERATION_URL constant
        from importlib import reload
        import app.api.modules.project
        reload(app.api.modules.project)
        
        # Check that the default URL is used
        self.assertEqual(
            app.api.modules.project.PLAN_GENERATION_URL,
            "http://localhost:8000/api/modules/plan/user-goal"
        )
    
    def test_environment_url_configuration(self):
        """Test that the environment variable is used when set."""
        # Set environment variable
        test_url = "https://test-api.example.com/api/modules/plan/user-goal"
        os.environ['PLAN_GENERATION_URL'] = test_url
        
        # Import the module again to reload the PLAN_GENERATION_URL constant
        from importlib import reload
        import app.api.modules.project
        reload(app.api.modules.project)
        
        # Check that the environment URL is used
        self.assertEqual(
            app.api.modules.project.PLAN_GENERATION_URL,
            test_url
        )
    
    @patch('httpx.AsyncClient')
    async def test_trigger_plan_generation_uses_configured_url(self, mock_client):
        """Test that trigger_plan_generation uses the configured URL."""
        # Set up mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value.post.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        # Set environment variable
        test_url = "https://production-api.example.com/api/modules/plan/user-goal"
        os.environ['PLAN_GENERATION_URL'] = test_url
        
        # Import the module again to reload the PLAN_GENERATION_URL constant
        from importlib import reload
        import app.api.modules.project
        reload(app.api.modules.project)
        
        # Call the function
        await app.api.modules.project.trigger_plan_generation(
            user_id="test_user",
            goal="Test goal",
            project_id="test_project",
            goal_id="test_goal"
        )
        
        # Check that the correct URL was used
        mock_client_instance.__aenter__.return_value.post.assert_called_once()
        call_args = mock_client_instance.__aenter__.return_value.post.call_args[0]
        self.assertEqual(call_args[0], test_url)

if __name__ == '__main__':
    unittest.main()
