"""
__init__.py for the db package

This file initializes the db package and ensures the directory structure exists.
"""

import os

# Ensure the db directory exists
os.makedirs(os.path.dirname(__file__), exist_ok=True)
