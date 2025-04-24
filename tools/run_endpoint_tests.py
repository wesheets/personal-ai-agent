#!/usr/bin/env python3
"""
Wrapper script for test_endpoints.py that logs results to the system manifest.

This script runs the endpoint testing tool and logs the results in the
system manifest under the "testing" section.

Usage:
  python run_endpoint_tests.py [--base-url URL] [--verbose]
"""

import argparse
import datetime
import json
import os
import subprocess
import sys

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import manifest manager
try:
    from app.utils.manifest_manager import log_endpoint_test_results
except ImportError as e:
    print(f"❌ Error importing manifest manager: {e}")
    sys.exit(1)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run endpoint tests and log results to system manifest")
    parser.add_argument("--base-url", default="https://web-production-2639.up.railway.app",
                        help="Base URL of the API")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed information for each endpoint")
    return parser.parse_args()

def run_endpoint_tests(base_url, verbose=False):
    """Run the endpoint tests and return the results."""
    # Build the command
    cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "test_endpoints.py")]
    
    if base_url:
        cmd.extend(["--base-url", base_url])
    
    if verbose:
        cmd.append("--verbose")
    
    # Run the command
    try:
        print(f"🔍 Running endpoint tests with command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check if the command was successful
        if result.returncode == 0:
            print("✅ Endpoint tests completed successfully")
            status = "✅ PASSED"
        else:
            print(f"❌ Endpoint tests failed with return code {result.returncode}")
            status = "❌ FAILED"
        
        # Print the output
        if verbose or result.returncode != 0:
            print("\nOutput:")
            print(result.stdout)
        
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
        
        return status, result.stdout, result.stderr
    
    except Exception as e:
        print(f"❌ Error running endpoint tests: {e}")
        return "❌ ERROR", str(e), ""

def main():
    """Main entry point."""
    args = parse_args()
    
    # Run the endpoint tests
    status, stdout, stderr = run_endpoint_tests(args.base_url, args.verbose)
    
    # Log the results to the manifest
    timestamp = datetime.datetime.utcnow().isoformat()
    log_result = log_endpoint_test_results(status, timestamp)
    
    if log_result:
        print(f"✅ Logged endpoint test results to manifest: {status}")
    else:
        print("❌ Failed to log endpoint test results to manifest")
    
    # Return the status code
    return 0 if status == "✅ PASSED" else 1

if __name__ == "__main__":
    sys.exit(main())
