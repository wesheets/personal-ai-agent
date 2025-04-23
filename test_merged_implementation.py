import unittest
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.modules.schema_validation import validate_schema, validate_before_export
from app.modules.loop_map_visualizer import create_visualizer, visualize_loop

class TestMergedImplementation(unittest.TestCase):
    
    def test_schema_validation_functions(self):
        """Test that schema validation functions exist and work as expected."""
        # Test validate_schema
        result = validate_schema({"test": "data"})
        self.assertTrue(result, "validate_schema should return True")
        
        # Test validate_before_export
        result = validate_before_export({"test": "data"})
        self.assertTrue(result, "validate_before_export should return True")
    
    def test_create_visualizer_function(self):
        """Test that create_visualizer function exists and works as expected."""
        result = create_visualizer()
        self.assertIsInstance(result, dict, "create_visualizer should return a dictionary")
        self.assertIn("status", result, "create_visualizer result should contain 'status' key")
        self.assertIn("Visualizer not implemented", result["status"], 
                     "create_visualizer status should indicate stub implementation")
    
    def test_visualize_loop_function(self):
        """Test that visualize_loop function exists and works as expected."""
        result = visualize_loop("test_loop_id", {})
        self.assertIsInstance(result, dict, "visualize_loop should return a dictionary")
        self.assertIn("status", result, "visualize_loop result should contain 'status' key")
        self.assertEqual("success", result["status"], "visualize_loop status should be 'success'")
        self.assertIn("visualization", result, "visualize_loop result should contain 'visualization' key")
        self.assertIn("content", result["visualization"], 
                     "visualize_loop visualization should contain 'content' key")
        self.assertIn("Stub function active", result["visualization"]["content"], 
                     "visualize_loop content should indicate stub implementation")

if __name__ == "__main__":
    unittest.main()
