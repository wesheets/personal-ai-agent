"""
Test configuration for SAGE review endpoint
"""

# Add SAGE review endpoint to the test configuration
ENDPOINTS.update({
    "sage_review": {
        "path": "/sage/review",
        "method": "POST",
        "expected": 200,
        "payload": {
            "loop_id": "test_loop_123",
            "summary_text": "The user is trying to optimize their data processing pipeline. They've mentioned issues with the current ETL process being too slow and error-prone. They're looking for automated solutions that can handle large datasets efficiently."
        }
    }
})
