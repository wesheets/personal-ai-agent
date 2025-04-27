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
        
        # Define expected fields for different endpoint types
        self.expected_fields = {
            "default": ["status"],
            "agent": ["status", "agent_id", "data"],
            "memory": ["status", "memory_id", "data"],
            "orchestrator": ["status", "request_id", "success"],
            "health": ["status", "version", "uptime"],
            "status": ["status", "system_state", "components"]
        }
        
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
            {"method": "GET", "path": "/api/health", "endpoint_type": "health"},
            {"method": "GET", "path": "/api/status", "endpoint_type": "status"},
            {"method": "GET", "path": "/api/agent/list", "endpoint_type": "agent"},
            {"method": "POST", "path": "/api/agent/run", "endpoint_type": "agent"},
            {"method": "GET", "path": "/api/agent/status", "endpoint_type": "agent"},
            {"method": "GET", "path": "/api/memory/list", "endpoint_type": "memory"},
            {"method": "GET", "path": "/api/memory/get", "endpoint_type": "memory"},
            {"method": "POST", "path": "/api/memory/create", "endpoint_type": "memory"},
            {"method": "GET", "path": "/api/goals/list", "endpoint_type": "default"},
            {"method": "POST", "path": "/api/goals/create", "endpoint_type": "default"},
            {"method": "GET", "path": "/api/logs/list", "endpoint_type": "default"},
            {"method": "GET", "path": "/api/control/status", "endpoint_type": "default"},
            {"method": "POST", "path": "/api/delegate/task", "endpoint_type": "default"}
        ]
        
        # Orchestrator endpoints
        orchestrator_endpoints = [
            {"method": "POST", "path": "/api/orchestrator/consult", "endpoint_type": "orchestrator"},
            {"method": "POST", "path": "/api/orchestrator/respond", "endpoint_type": "orchestrator"},
            {"method": "POST", "path": "/api/orchestrator/confirm", "endpoint_type": "orchestrator"},
            {"method": "POST", "path": "/api/orchestrator/credentials", "endpoint_type": "orchestrator"},
            {"method": "POST", "path": "/api/orchestrator/checkpoint", "endpoint_type": "orchestrator"},
            {"method": "GET", "path": "/api/orchestrator/status", "endpoint_type": "orchestrator"},
            {"method": "POST", "path": "/api/orchestrator/approve", "endpoint_type": "orchestrator"},
            {"method": "POST", "path": "/api/orchestrator/delegate", "endpoint_type": "orchestrator"},
            {"method": "POST", "path": "/api/orchestrator/reflect", "endpoint_type": "orchestrator"}
        ]
        
        # Combine all endpoints
        all_endpoints = api_endpoints + orchestrator_endpoints
        
        self.logger.info(f"Discovered {len(all_endpoints)} endpoints")
        return all_endpoints
    
    def validate_payload(self, response: requests.Response, endpoint_type: str) -> Dict[str, Any]:
        """
        Validate the response payload from an endpoint.
        
        Args:
            response: HTTP response object
            endpoint_type: Type of endpoint (agent, memory, orchestrator, etc.)
            
        Returns:
            Dictionary with payload validation results
        """
        # Initialize validation result
        validation_result = {
            "payload_validation_status": "fail",
            "payload_drift_type": None,
            "missing_fields": [],
            "payload_size_bytes": 0,
            "is_json": False
        }
        
        # Check if response has content
        if not response.text or not response.text.strip():
            validation_result["payload_drift_type"] = "EmptyPayload"
            return validation_result
        
        # Check if response is JSON
        try:
            payload = response.json()
            validation_result["is_json"] = True
            validation_result["payload_size_bytes"] = len(response.text)
        except json.JSONDecodeError:
            validation_result["payload_drift_type"] = "MalformedResponse"
            return validation_result
        
        # Check if payload is empty object or array
        if not payload:
            validation_result["payload_drift_type"] = "EmptyPayload"
            return validation_result
        
        # Get expected fields for this endpoint type
        expected_fields = self.expected_fields.get(endpoint_type, self.expected_fields["default"])
        
        # Check for missing fields
        missing_fields = [field for field in expected_fields if field not in payload]
        validation_result["missing_fields"] = missing_fields
        
        if missing_fields:
            validation_result["payload_drift_type"] = "MissingFields"
        else:
            validation_result["payload_validation_status"] = "pass"
            
        return validation_result
    
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
        endpoint_type = endpoint.get("endpoint_type", "default")
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
                    "timestamp": datetime.datetime.now().isoformat(),
                    "payload_validation_status": "fail",
                    "payload_drift_type": "UnsupportedMethod",
                    "missing_fields": [],
                    "payload_size_bytes": 0,
                    "is_json": False
                }
            
            end_time = datetime.datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Check if response is successful (status code 2xx)
            is_success = 200 <= response.status_code < 300
            
            # Validate payload if response is successful
            payload_validation = self.validate_payload(response, endpoint_type) if is_success else {
                "payload_validation_status": "fail",
                "payload_drift_type": "HttpError",
                "missing_fields": [],
                "payload_size_bytes": 0,
                "is_json": False
            }
            
            # Determine overall validation status
            validation_status = "pass" if is_success and payload_validation["payload_validation_status"] == "pass" else "fail"
            
            # Determine failure reason
            if not is_success:
                failure_reason = f"HTTP {response.status_code}: {response.reason}"
            elif payload_validation["payload_validation_status"] == "fail":
                drift_type = payload_validation["payload_drift_type"]
                if drift_type == "EmptyPayload":
                    failure_reason = "Empty response payload"
                elif drift_type == "MalformedResponse":
                    failure_reason = "Malformed JSON response"
                elif drift_type == "MissingFields":
                    missing = ", ".join(payload_validation["missing_fields"])
                    failure_reason = f"Missing required fields: {missing}"
                else:
                    failure_reason = f"Payload validation failed: {drift_type}"
            else:
                failure_reason = None
            
            result = {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "validation_status": validation_status,
                "failure_reason": failure_reason,
                "response_time_ms": response_time_ms,
                "timestamp": datetime.datetime.now().isoformat(),
                "endpoint_type": endpoint_type,
                **payload_validation
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
                "timestamp": datetime.datetime.now().isoformat(),
                "endpoint_type": endpoint_type,
                "payload_validation_status": "fail",
                "payload_drift_type": "ConnectionError",
                "missing_fields": [],
                "payload_size_bytes": 0,
                "is_json": False
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
                        "timestamp": datetime.datetime.now().isoformat(),
                        "endpoint_type": endpoint.get("endpoint_type", "default"),
                        "payload_validation_status": "fail",
                        "payload_drift_type": "ProcessingError",
                        "missing_fields": [],
                        "payload_size_bytes": 0,
                        "is_json": False
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
        
        # Calculate endpoint health score as percentage of passing endpoints
        endpoint_health_score = (passed_endpoints / total_endpoints) * 100 if total_endpoints > 0 else 0
        
        # Calculate payload health metrics
        endpoints_with_payload = sum(1 for result in results if result["status_code"] is not None and 200 <= result["status_code"] < 300)
        passed_payloads = sum(1 for result in results if result["payload_validation_status"] == "pass")
        failed_payloads = endpoints_with_payload - passed_payloads
        
        # Calculate payload health score as percentage of passing payloads
        payload_health_score = (passed_payloads / endpoints_with_payload) * 100 if endpoints_with_payload > 0 else 0
        
        # Count drift types
        drift_type_counts = {}
        for result in results:
            if result["payload_drift_type"]:
                drift_type = result["payload_drift_type"]
                drift_type_counts[drift_type] = drift_type_counts.get(drift_type, 0) + 1
        
        # Get details of failed endpoints
        failed_endpoint_details = [
            {
                "url": result["url"],
                "method": result["method"],
                "status_code": result["status_code"],
                "failure_reason": result["failure_reason"],
                "payload_drift_type": result["payload_drift_type"],
                "missing_fields": result["missing_fields"]
            }
            for result in results if result["validation_status"] == "fail"
        ]
        
        # Generate report
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "total_endpoints": total_endpoints,
            "passed_endpoints": passed_endpoints,
            "failed_endpoints": failed_endpoints,
            "endpoint_health_score": round(endpoint_health_score, 1),
            "endpoints_with_payload": endpoints_with_payload,
            "passed_payloads": passed_payloads,
            "failed_payloads": failed_payloads,
            "payload_health_score": round(payload_health_score, 1),
            "drift_type_counts": drift_type_counts,
            "failed_endpoint_details": failed_endpoint_details,
            "validation_results": results
        }
        
        self.logger.info(f"Generated drift report: {total_endpoints} endpoints, {passed_endpoints} passed, {failed_endpoints} failed")
        self.logger.info(f"Endpoint health score: {endpoint_health_score:.1f}%, Payload health score: {payload_health_score:.1f}%")
        self.logger.info(f"Drift types detected: {drift_type_counts}")
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
        logger.info("Starting Promethios Endpoint Health and Payload Validation")
        
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
            print(f"\n⚠️  ENDPOINT VALIDATION COMPLETED:")
            print(f"⚠️  Endpoint Health: {report['endpoint_health_score']:.1f}% ({report['failed_endpoints']} of {report['total_endpoints']} endpoints failed)")
            print(f"⚠️  Payload Health: {report['payload_health_score']:.1f}% ({report['failed_payloads']} of {report['endpoints_with_payload']} payloads failed)")
            print(f"⚠️  Report saved to {report_path}")
            print("\nDrift types detected:")
            for drift_type, count in report['drift_type_counts'].items():
                print(f"  - {drift_type}: {count} instances")
            print("\nFailed endpoints (top 5):")
            for i, endpoint in enumerate(report['failed_endpoint_details'][:5]):  # Show top 5 failures
                print(f"  {i+1}. {endpoint['method']} {endpoint['url']} - {endpoint['failure_reason']}")
            if len(report['failed_endpoint_details']) > 5:
                print(f"  ... and {len(report['failed_endpoint_details']) - 5} more failures")
            print("\nNo automatic repairs will be performed. Operator intervention required.")
        else:
            logger.info(f"All endpoints validated successfully")
            print(f"\n✅ ALL ENDPOINTS VALIDATED:")
            print(f"✅ Endpoint Health: {report['endpoint_health_score']:.1f}% (all endpoints passed)")
            print(f"✅ Payload Health: {report['payload_health_score']:.1f}% (all payloads passed)")
            print(f"✅ Report saved to {report_path}")
        
        return 0 if report["failed_endpoints"] == 0 else 1
    
    except Exception as e:
        logger.error(f"Error during endpoint validation: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: Endpoint validation failed: {str(e)}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
