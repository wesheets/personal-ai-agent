#!/usr/bin/env python3
"""
Comprehensive fix script to correct JSON validation issues in schema files.
This script converts Python-style boolean values (True/False) to JSON-style boolean values (true/false).
"""

import json
import os
import glob
import re
from typing import Dict, List, Tuple, Any
import datetime

def fix_python_booleans(file_path: str) -> Tuple[bool, str, bool]:
    """
    Fix Python-style boolean values in JSON files.
    
    Args:
        file_path: Path to the JSON file to fix
        
    Returns:
        Tuple containing:
        - Boolean indicating if the fix was successful
        - Error message if the fix failed, empty string otherwise
        - Boolean indicating if any changes were made
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file contains Python-style boolean values
        if re.search(r':\s*True\b', content) or re.search(r':\s*False\b', content):
            # Replace Python-style boolean values with JSON-style boolean values
            modified_content = re.sub(r':\s*True\b', ': true', content)
            modified_content = re.sub(r':\s*False\b', ': false', modified_content)
            
            # Write the modified content back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # Verify the fix by trying to parse the JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                return True, "", True
            except json.JSONDecodeError as e:
                return False, f"Failed to validate after fix: {str(e)}", True
        else:
            return True, "", False
    except Exception as e:
        return False, f"Error processing file: {str(e)}", False

def validate_json_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate a JSON file and return validation status and error message.
    
    Args:
        file_path: Path to the JSON file to validate
        
    Returns:
        Tuple containing:
        - Boolean indicating if validation passed
        - Error message if validation failed, empty string otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
            return True, ""
    except json.JSONDecodeError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def main():
    """Main function to fix all schema files with Python-style boolean values."""
    # Find all schema files in the repository
    schema_patterns = [
        '/home/ubuntu/personal-ai-agent/schemas/**/*.json',
        '/home/ubuntu/personal-ai-agent/app/schemas/**/*.json',
        '/home/ubuntu/personal-ai-agent/app/loop/debug/*.schema*.json'
    ]
    
    all_files = []
    for pattern in schema_patterns:
        all_files.extend(glob.glob(pattern, recursive=True))
    
    print(f"Found {len(all_files)} schema files to process")
    
    # Fix all files and collect results
    fix_results = []
    fixed_count = 0
    already_valid_count = 0
    
    for file_path in all_files:
        print(f"Processing: {file_path}")
        
        # Check if the file is already valid
        is_valid, error_msg = validate_json_file(file_path)
        if is_valid:
            print(f"  ✅ Already valid")
            already_valid_count += 1
            continue
        
        # Fix Python-style boolean values
        success, error_msg, changes_made = fix_python_booleans(file_path)
        
        result = {
            "file_path": file_path,
            "success": success,
            "changes_made": changes_made,
            "error_message": error_msg
        }
        
        if success and changes_made:
            fixed_count += 1
            print(f"  ✅ Successfully fixed")
        elif not success:
            print(f"  ❌ Failed to fix: {error_msg}")
        else:
            print(f"  ⚠️ No changes needed")
        
        fix_results.append(result)
    
    print(f"\nSummary: Fixed {fixed_count} files, {already_valid_count} were already valid, {len(all_files) - fixed_count - already_valid_count} could not be fixed")
    
    # Save results to a file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f'/home/ubuntu/schema_fix_results_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump({
            "total_files": len(all_files),
            "fixed_count": fixed_count,
            "already_valid_count": already_valid_count,
            "failed_count": len(all_files) - fixed_count - already_valid_count,
            "timestamp": datetime.datetime.now().isoformat(),
            "detailed_results": fix_results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to /home/ubuntu/schema_fix_results_{timestamp}.json")
    
    # Create a memory tag file
    with open('/home/ubuntu/schema_fix_complete.txt', 'w', encoding='utf-8') as f:
        f.write(f"schema_fix_complete_{timestamp}\n")
        f.write(f"Fixed {fixed_count} files with Python-style boolean values\n")
    
    print(f"\nMemory tag created: schema_fix_complete_{timestamp}")

if __name__ == "__main__":
    main()
