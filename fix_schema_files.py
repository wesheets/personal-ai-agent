#!/usr/bin/env python3
"""
Script to fix truncated $schema URLs in JSON schema files.
This script fixes the "Extra data: line 1 column 3" error by properly formatting the $schema URLs.
"""

import json
import os
import glob
import re

# Standard JSON schema URL to use as replacement
SCHEMA_URL = "http://json-schema.org/draft-07/schema#"

def fix_schema_file(file_path):
    """Fix a schema file by properly formatting the $schema URL."""
    print(f"Processing: {file_path}")
    
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file has the truncated $schema field
        if '"$schema": "http' in content:
            print(f"  Found schema URL issue in {file_path}")
            
            # Fix the specific pattern where schema URL and title are incorrectly joined
            fixed_content = re.sub(
                r'"\$schema": "http://json-schema.org/draft-07/schema#"title":', 
                '"$schema": "http://json-schema.org/draft-07/schema#",\n  "title":', 
                content
            )
            
            # Write the fixed content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            # Verify the fix by trying to parse the JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"  ✅ Successfully fixed and validated {file_path}")
                return True
            except json.JSONDecodeError as e:
                print(f"  ❌ Failed to validate after fix: {e}")
                return False
        else:
            print(f"  No schema URL issue found in {file_path}")
            return False
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to find and fix all schema files."""
    # Find all schema files in the repository
    schema_files = glob.glob('/home/ubuntu/personal-ai-agent/schemas/**/*.schema.json', recursive=True)
    
    # Also check the loop trace schema files which had similar issues
    loop_schema_files = glob.glob('/home/ubuntu/personal-ai-agent/app/loop/debug/*.schema*.json', recursive=True)
    
    all_files = schema_files + loop_schema_files
    
    print(f"Found {len(all_files)} schema files to check")
    
    fixed_count = 0
    for file_path in all_files:
        if fix_schema_file(file_path):
            fixed_count += 1
    
    print(f"\nSummary: Fixed {fixed_count} out of {len(all_files)} schema files")
    
    # Create a report file
    with open('/home/ubuntu/schema_fix_report.json', 'w', encoding='utf-8') as f:
        report = {
            "total_files_checked": len(all_files),
            "files_fixed": fixed_count,
            "timestamp": "2025-04-25T02:35:00Z",
            "error_type": "Extra data: line 1 column 3",
            "fix_description": "Fixed schema URL and title formatting in JSON schema files"
        }
        json.dump(report, f, indent=2)
    
    print(f"Report saved to /home/ubuntu/schema_fix_report.json")

if __name__ == "__main__":
    main()
