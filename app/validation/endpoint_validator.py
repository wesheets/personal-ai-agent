"""
Endpoint Validator Module

This module provides functionality to validate the health of API endpoints
by sending HTTP requests and verifying responses.

Usage:
    python -m app.validation.endpoint_validator

This module can be used to validate all API endpoints in the system and
generate a report of the validation results.
"""

import os
import sys
import json
import logging
import argparse
import datetime
import requests
from typing import Dict, Any, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Configure logging
def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configure logging for the endpoint validator.
    
    Args:
        verbose: Whether to enable verbose logging
        
    Returns:
        Logger instance
    """
    # Create logs directory if it doesn't exist
    base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO
    log_file = os.path.join(log_dir, f"endpoint_validation_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('endpoint_validator')
    logger.info(f"Logging initialized at level {logging.getLevelName(log_level)}")
    logger.info(f"Log file: {log_file}")
    
    return logger

class EndpointValidator:
    """
    Validates the health of API endpoints by sending HTTP requests and verifying responses.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", max_workers: int = 5):
        """
        Initialize the endpoint validator.
        
        Args:
            base_url: Base URL for API endpoints
            max_workers: Maximum number of concurrent workers for validation
        """
        self.base_url = base_url
        self.max_workers = max_workers
        self.logger = logging.getLogger('endpoint_validator')
        
    def discover_endpoints(self) -> List[Dict[str, Any]]:
        """
        Discover API endpoints in the system.
        
        This method should be implemented to discover all API endpoints
        in the system. For now, it returns a hardcoded list of endpoints
        based on the API directory structure.
        
        Returns:
            List of endpoint dictionaries with method and path
        """
        # This is a simplified implementation that returns a hardcoded list
        # In a real implementation, this would discover endpoints dynamically
        
        # Basic endpoints from app/api directory
        api_endpoints = [
            {"method": "GET", "path": "/api/health"},
            {"method": "GET", "path": "/api/status"},
            {"method": "GET", "path": "/api/agent/list"},
            {"method": "POST", "path": "/api/agent/run"},
            {"method": "GET", "path": "/api/agent/status"},
            {"method": "GET", "path": "/api/memory/list"},
            {"method": "GET", "path": "/api/memory/get"},
            {"method": "POST", "path": "/api/memory/create"},
            {"method": "GET", "path": "/api/goals/list"},
            {"method": "POST", "path": "/api/goals/create"},
            {"method": "GET", "path": "/api/logs/list"},
            {"method": "GET", "path": "/api/control/status"},
            {"method": "POST", "path": "/api/delegate/task"}
        ]
        
        # Orchestrator endpoints
        orchestrator_endpoints = [
            {"method": "POST", "path": "/api/orchestrator/consult"},
            {"method": "POST", "path": "/api/orchestrator/respond"},
            {"method": "POST", "path": "/api/orchestrator/confirm"},
            {"method": "POST", "path": "/api/orchestrator/credentials"},
            {"method": "POST", "path": "/api/orchestrator/checkpoint"},
            {"method": "GET", "path": "/api/orchestrator/status"},
            {"method": "POST", "path": "/api/orchestrator/approve"},
            {"method": "POST", "path": "/api/orchestrator/delegate"},
            {"method": "POST", "path": "/api/orchestrator/reflect"}
        ]
        
        # Combine all endpoints
        all_endpoints = api_endpoints + orchestrator_endpoints
        
        self.logger.info(f"Discovered {len(all_endpoints)} endpoints")
        return all_endpoints
    
    def validate_endpoint(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single endpoint by sending an HTTP request and verifying the response.
        
        Args:
            endpoint: Endpoint dictionary with method and path
            
        Returns:
            Validation result dictionary
        """
        method = endpoint["method"]
        path = endpoint["path"]
        url = f"{self.base_url}{path}"
        
        # Replace path parameters with placeholder values
        if "{" in path:
            # For simplicity, replace all path parameters with "test_id"
            url = url.replace("{", "test_").replace("}", "")
        
        self.logger.debug(f"Validating endpoint: {method} {url}")
        
        try:
            start_time = datetime.datetime.now()
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                # Send a minimal JSON payload
                response = requests.post(url, json={"test": "data"}, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json={"test": "data"}, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, json={"test": "data"}, timeout=10)
            else:
                return {
                    "url": url,
                    "method": method,
                    "status_code": None,
                    "validation_status": "fail",
                    "failure_reason": f"Unsupported method: {method}",
                    "response_time_ms": 0,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            end_time = datetime.datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Check if response is successful (status code 2xx)
            is_success = 200 <= response.status_code < 300
            
            # Optionally check if response has a non-empty payload
            has_payload = False
            try:
                if response.text and response.text.strip():
                    has_payload = True
            except:
                pass
            
            validation_status = "pass" if is_success else "fail"
            failure_reason = None if is_success else f"HTTP {response.status_code}: {response.reason}"
            
            result = {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "validation_status": validation_status,
                "failure_reason": failure_reason,
                "response_time_ms": response_time_ms,
                "has_payload": has_payload,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            self.logger.debug(f"Endpoint validation result: {method} {url} - {validation_status}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating endpoint {method} {url}: {str(e)}")
            return {
                "url": url,
                "method": method,
                "status_code": None,
                "validation_status": "fail",
                "failure_reason": f"Exception: {str(e)}",
                "response_time_ms": 0,
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def validate_all_endpoints(self) -> List[Dict[str, Any]]:
        """
        Validate all endpoints in parallel using a thread pool.
        
        Returns:
            List of validation result dictionaries
        """
        endpoints = self.discover_endpoints()
        results = []
        
        self.logger.info(f"Starting validation of {len(endpoints)} endpoints with {self.max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_endpoint = {executor.submit(self.validate_endpoint, endpoint): endpoint for endpoint in endpoints}
            for future in as_completed(future_to_endpoint):
                endpoint = future_to_endpoint[future]
                try:
                    result = future.result()
                    results.append(result)
                    status = "✅ PASS" if result["validation_status"] == "pass" else "❌ FAIL"
                    self.logger.info(f"{status} - {result['method']} {result['url']}")
                except Exception as e:
                    self.logger.error(f"Error processing result for {endpoint['method']} {endpoint['path']}: {str(e)}")
                    results.append({
                        "url": f"{self.base_url}{endpoint['path']}",
                        "method": endpoint["method"],
                        "status_code": None,
                        "validation_status": "fail",
                        "failure_reason": f"Exception during processing: {str(e)}",
                        "response_time_ms": 0,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
        
        self.logger.info(f"Completed validation of {len(endpoints)} endpoints")
        return results
    
    def generate_drift_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a drift report from validation results.
        
        Args:
            results: List of validation result dictionaries
            
        Returns:
            Drift report dictionary
        """
        total_endpoints = len(results)
        passed_endpoints = sum(1 for result in results if result["validation_status"] == "pass")
        failed_endpoints = total_endpoints - passed_endpoints
        
        # Calculate health score as percentage of passing endpoints
        health_score = (passed_endpoints / total_endpoints) * 100 if total_endpoints > 0 else 0
        
        # Get details of failed endpoints
        failed_endpoint_details = [
            {
                "url": result["url"],
                "method": result["method"],
                "status_code": result["status_code"],
                "failure_reason": result["failure_reason"]
            }
            for result in results if result["validation_status"] == "fail"
        ]
        
        # Generate report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_endpoints": total_endpoints,
            "passed_endpoints": passed_endpoints,
            "failed_endpoints": failed_endpoints,
            "endpoint_health_score": round(health_score, 1),
            "failed_endpoint_details": failed_endpoint_details,
            "validation_results": results
        }
        
        self.logger.info(f"Generated drift report: {total_endpoints} endpoints, {passed_endpoints} passed, {failed_endpoints} failed, {health_score:.1f}% health score")
        return report
    
    def save_drift_report(self, report: Dict[str, Any]) -> str:
        """
        Save the drift report to a file.
        
        Args:
            report: Drift report dictionary
            
        Returns:
            Path to the saved report file
        """
        # Create logs directory if it doesn't exist
        base_path = os.environ.get("PROMETHIOS_BASE_PATH", "")
        log_dir = os.path.join(base_path, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate filename with current date
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        report_file = os.path.join(log_dir, f"endpoint_drift_report_{date_str}.json")
        
        # Save report
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Saved drift report to {report_file}")
        return report_file

def main():
    """
    Main entry point for the endpoint validator.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Promethios Endpoint Health Validator")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL for API endpoints")
    parser.add_argument("--max-workers", type=int, default=5, help="Maximum number of concurrent workers")
    parser.add_argument("--base-path", default="", help="Base path to prepend to file paths")
    args = parser.parse_args()
    
    # Set base path environment variable
    if args.base_path:
        os.environ["PROMETHIOS_BASE_PATH"] = args.base_path
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    try:
        logger.info("Starting Promethios Endpoint Health Validation")
        
        # Create endpoint validator
        validator = EndpointValidator(base_url=args.base_url, max_workers=args.max_workers)
        
        # Validate all endpoints
        results = validator.validate_all_endpoints()
        
        # Generate drift report
        report = validator.generate_drift_report(results)
        
        # Save drift report
        report_path = validator.save_drift_report(report)
        
        # Log completion
        if report["failed_endpoints"] > 0:
            logger.warning(f"Endpoint validation completed with {report['failed_endpoints']} failed endpoints")
            print(f"\n⚠️  ENDPOINT VALIDATION COMPLETED: {report['endpoint_health_score']:.1f}% health score")
            print(f"⚠️  {report['failed_endpoints']} of {report['total_endpoints']} endpoints failed")
            print(f"⚠️  Report saved to {report_path}")
            print("\nFailed endpoints:")
            for i, endpoint in enumerate(report['failed_endpoint_details'][:5]):  # Show top 5 failures
                print(f"  {i+1}. {endpoint['method']} {endpoint['url']} - {endpoint['failure_reason']}")
            if len(report['failed_endpoint_details']) > 5:
                print(f"  ... and {len(report['failed_endpoint_details']) - 5} more failures")
            print("\nNo automatic repairs will be performed. Operator intervention required.")
        else:
            logger.info(f"All endpoints validated successfully")
            print(f"\n✅ ALL ENDPOINTS VALIDATED: {report['endpoint_health_score']:.1f}% health score")
            print(f"✅ {report['passed_endpoints']} of {report['total_endpoints']} endpoints passed")
            print(f"✅ Report saved to {report_path}")
        
        return 0 if report["failed_endpoints"] == 0 else 1
    
    except Exception as e:
        logger.error(f"Error during endpoint validation: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: Endpoint validation failed: {str(e)}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
