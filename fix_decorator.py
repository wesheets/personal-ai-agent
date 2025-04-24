#!/usr/bin/env python3
"""
Fix retry_with_backoff decorator usage in health_monitor.py

This script updates all occurrences of the retry_with_backoff decorator in 
health_monitor.py to use the correct parameter names.
"""

import re

def fix_decorator_usage(file_path):
    """
    Fix the retry_with_backoff decorator usage in the specified file.
    
    Args:
        file_path: Path to the file to fix
    """
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace all occurrences of the decorator with the correct parameter names
    fixed_content = re.sub(
        r'@retry_with_backoff\(max_retries=3, base_delay=1, backoff_factor=2\)',
        '@retry_with_backoff(retries=3, backoff=2)',
        content
    )
    
    # Write the fixed content back to the file
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed retry_with_backoff decorator usage in {file_path}")

if __name__ == "__main__":
    file_path = "app/modules/health_monitor.py"
    fix_decorator_usage(file_path)
