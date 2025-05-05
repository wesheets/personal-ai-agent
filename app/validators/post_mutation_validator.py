#!/usr/bin/env python3.11
import os
import subprocess
import logging

# Configure logging
LOG_FILE = "/home/ubuntu/personal-ai-agent/app/logs/post_mutation_validator.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

def validate_mutation(loop_id: str, file_path: str) -> bool:
    """Validates a file after a mutation.

    Args:
        loop_id: The ID of the current loop.
        file_path: The absolute path to the file that was mutated.

    Returns:
        True if validation passes, False otherwise.
    """
    logging.info(f"[{loop_id}] Starting post-mutation validation for: {file_path}")

    # 1. Check file existence
    if not os.path.exists(file_path):
        logging.error(f"[{loop_id}] Validation FAILED: File not found at {file_path}")
        return False
    logging.info(f"[{loop_id}] Validation PASSED: File exists at {file_path}")

    # 2. Basic Python syntax check (if it's a .py file)
    if file_path.endswith(".py"):
        try:
            # Use subprocess to run py_compile
            result = subprocess.run(["python3.11", "-m", "py_compile", file_path], 
                                    check=True, capture_output=True, text=True)
            logging.info(f"[{loop_id}] Validation PASSED: Python syntax check for {file_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"[{loop_id}] Validation FAILED: Python syntax error in {file_path}. Error: {e.stderr}")
            return False
        except Exception as e:
            logging.error(f"[{loop_id}] Validation FAILED: Error during Python syntax check for {file_path}. Error: {e}")
            return False

    # Add more checks here if needed (e.g., JSON validation, linting)

    logging.info(f"[{loop_id}] Post-mutation validation completed successfully for: {file_path}")
    return True

# Example usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    # Create a dummy valid python file
    valid_py_content = "def hello():\n    print(\"Hello, world!\")\nhello()\n"
    valid_py_path = "/home/ubuntu/valid_test.py"
    with open(valid_py_path, "w") as f:
        f.write(valid_py_content)
    
    # Create a dummy invalid python file
    invalid_py_content = "def hello():\nprint(\"Missing indent\")\nhello()\n"
    invalid_py_path = "/home/ubuntu/invalid_test.py"
    with open(invalid_py_path, "w") as f:
        f.write(invalid_py_content)

    # Test cases
    print("Testing valid file...")
    validate_mutation("test_loop_valid", valid_py_path)
    
    print("\nTesting invalid file...")
    validate_mutation("test_loop_invalid", invalid_py_path)
    
    print("\nTesting non-existent file...")
    validate_mutation("test_loop_nonexistent", "/home/ubuntu/nonexistent.py")
    
    # Clean up dummy files
    os.remove(valid_py_path)
    os.remove(invalid_py_path)

