# Phase 3.1: Endpoint Health Verification System - Architectural Design Plan

## 1. Purpose of Endpoint Health Verification

The Endpoint Health Verification System is designed to continuously monitor and validate the operational status, performance, and reliability of critical API endpoints within the personal AI agent infrastructure. This system serves several key purposes:

- **Proactive Issue Detection**: Identify potential problems with API endpoints before they impact end users or dependent systems.
- **Service Level Agreement (SLA) Compliance**: Ensure that API endpoints meet defined performance and availability standards.
- **Drift Detection**: Monitor for unexpected changes in API behavior, response formats, or performance characteristics over time.
- **System Reliability**: Contribute to the overall reliability and resilience of the personal AI agent ecosystem by ensuring stable communication channels.
- **Quality Assurance**: Provide a mechanism for validating that API endpoints continue to function as expected after updates or changes to the system.
- **Performance Monitoring**: Track response times and other performance metrics to identify optimization opportunities.

The system will operate as an independent verification layer, regularly checking endpoints against predefined expectations and generating reports when discrepancies are detected.

## 2. Validation Targets

The following critical API endpoints will be monitored by the Endpoint Health Verification System:

### Core Agent API Endpoints
- `/api/v1/agent/query` - Primary interface for agent interactions
- `/api/v1/agent/status` - Agent operational status endpoint
- `/api/v1/agent/reset` - Agent context reset functionality

### Knowledge Base Endpoints
- `/api/v1/knowledge/search` - Knowledge retrieval endpoint
- `/api/v1/knowledge/update` - Knowledge base update mechanism
- `/api/v1/knowledge/status` - Knowledge base status and statistics

### Tool Integration Endpoints
- `/api/v1/tools/list` - Available tools listing
- `/api/v1/tools/execute` - Tool execution endpoint
- `/api/v1/tools/status/{tool_id}` - Individual tool status checking

### Authentication and User Management
- `/api/v1/auth/login` - Authentication endpoint
- `/api/v1/auth/refresh` - Token refresh mechanism
- `/api/v1/users/profile` - User profile information
- `/api/v1/users/preferences` - User preference management

### System Administration
- `/api/v1/admin/metrics` - System performance metrics
- `/api/v1/admin/logs` - Log access endpoint
- `/api/v1/admin/config` - Configuration management

### External Integration Points
- `/api/v1/integrations/webhook` - Webhook receiver for external systems
- `/api/v1/integrations/export` - Data export functionality
- `/api/v1/integrations/import` - Data import functionality

## 3. Expected Response Checks

For each endpoint, the following validation checks will be performed:

### Status Code Validation
- **Success Codes**: Verify appropriate 2xx status codes for successful operations
- **Error Handling**: Validate proper 4xx/5xx status codes for error conditions
- **Redirect Handling**: Ensure 3xx redirects function as expected when applicable

### Response Payload Validation
- **Schema Compliance**: Validate response structure against predefined JSON schemas
- **Data Type Verification**: Ensure all fields contain expected data types
- **Required Field Presence**: Confirm all required fields are present in responses
- **Field Value Validation**: Check that field values fall within expected ranges or patterns
- **Null/Empty Handling**: Verify proper handling of null or empty values

### Response Time Metrics
- **Baseline Response Time**: Establish and monitor against baseline response times for each endpoint
- **Percentile Measurements**: Track p50, p90, and p99 response times
- **Timeout Handling**: Verify proper behavior when response times exceed thresholds
- **Performance Degradation**: Detect gradual performance degradation over time

### Authentication and Authorization
- **Token Validation**: Verify proper handling of authentication tokens
- **Permission Enforcement**: Ensure endpoints correctly enforce access permissions
- **Session Management**: Validate session handling behavior

### Content and Encoding
- **Character Encoding**: Verify proper UTF-8 encoding in responses
- **Content-Type Headers**: Validate correct content-type headers
- **Compression**: Check proper handling of compression when applicable

### Functional Validation
- **Business Logic**: Verify that endpoints implement expected business logic
- **State Changes**: Confirm that state-changing operations work as expected
- **Idempotency**: Validate idempotent behavior for applicable endpoints

## 4. Proposed Tool Structure (endpoint_validator.py)

The `endpoint_validator.py` tool will be designed with a modular, extensible architecture to facilitate endpoint health verification. The proposed structure is as follows:

```python
# endpoint_validator.py

import requests
import json
import time
import logging
import jsonschema
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class EndpointConfig:
    """Configuration for an individual endpoint to be validated."""
    def __init__(self, name: str, url: str, method: str, headers: Dict[str, str],
                 payload: Optional[Dict[str, Any]] = None,
                 expected_status: int = 200,
                 schema_path: Optional[str] = None,
                 timeout: float = 5.0):
        self.name = name
        self.url = url
        self.method = method
        self.headers = headers
        self.payload = payload
        self.expected_status = expected_status
        self.schema_path = schema_path
        self.timeout = timeout

class ValidationResult:
    """Results of an endpoint validation check."""
    def __init__(self, endpoint_name: str, timestamp: datetime):
        self.endpoint_name = endpoint_name
        self.timestamp = timestamp
        self.status_code = None
        self.response_time = None
        self.schema_valid = None
        self.payload_valid = None
        self.errors = []
        self.warnings = []
        self.raw_response = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary for serialization."""
        return {
            "endpoint_name": self.endpoint_name,
            "timestamp": self.timestamp.isoformat(),
            "status_code": self.status_code,
            "response_time": self.response_time,
            "schema_valid": self.schema_valid,
            "payload_valid": self.payload_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }

class EndpointValidator:
    """Main validator class for checking endpoint health."""
    def __init__(self, config_path: str, output_dir: str):
        self.config_path = config_path
        self.output_dir = output_dir
        self.endpoints = []
        self.logger = self._setup_logging()
        self.load_config()
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the validator."""
        logger = logging.getLogger("endpoint_validator")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(f"{self.output_dir}/endpoint_validator.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def load_config(self) -> None:
        """Load endpoint configurations from config file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            for endpoint_config in config.get("endpoints", []):
                self.endpoints.append(EndpointConfig(
                    name=endpoint_config["name"],
                    url=endpoint_config["url"],
                    method=endpoint_config["method"],
                    headers=endpoint_config.get("headers", {}),
                    payload=endpoint_config.get("payload"),
                    expected_status=endpoint_config.get("expected_status", 200),
                    schema_path=endpoint_config.get("schema_path"),
                    timeout=endpoint_config.get("timeout", 5.0)
                ))
            self.logger.info(f"Loaded {len(self.endpoints)} endpoint configurations")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
    def validate_endpoint(self, endpoint: EndpointConfig) -> ValidationResult:
        """Validate a single endpoint and return results."""
        result = ValidationResult(endpoint.name, datetime.now())
        
        try:
            start_time = time.time()
            
            if endpoint.method.upper() == "GET":
                response = requests.get(
                    endpoint.url, 
                    headers=endpoint.headers,
                    timeout=endpoint.timeout
                )
            elif endpoint.method.upper() == "POST":
                response = requests.post(
                    endpoint.url,
                    headers=endpoint.headers,
                    json=endpoint.payload,
                    timeout=endpoint.timeout
                )
            # Additional HTTP methods can be added here
            
            end_time = time.time()
            
            # Record basic metrics
            result.status_code = response.status_code
            result.response_time = end_time - start_time
            result.raw_response = response.text
            
            # Validate status code
            if response.status_code != endpoint.expected_status:
                result.errors.append(f"Expected status code {endpoint.expected_status}, got {response.status_code}")
            
            # Validate schema if provided
            if endpoint.schema_path:
                try:
                    with open(endpoint.schema_path, 'r') as f:
                        schema = json.load(f)
                    
                    response_json = response.json()
                    jsonschema.validate(response_json, schema)
                    result.schema_valid = True
                except json.JSONDecodeError:
                    result.schema_valid = False
                    result.errors.append("Response is not valid JSON")
                except jsonschema.exceptions.ValidationError as e:
                    result.schema_valid = False
                    result.errors.append(f"Schema validation failed: {str(e)}")
            
            # Additional validation logic can be added here
            
        except requests.exceptions.Timeout:
            result.errors.append(f"Request timed out after {endpoint.timeout} seconds")
        except requests.exceptions.RequestException as e:
            result.errors.append(f"Request failed: {str(e)}")
        except Exception as e:
            result.errors.append(f"Validation error: {str(e)}")
        
        return result
    
    def validate_all_endpoints(self) -> List[ValidationResult]:
        """Validate all configured endpoints and return results."""
        results = []
        for endpoint in self.endpoints:
            self.logger.info(f"Validating endpoint: {endpoint.name}")
            result = self.validate_endpoint(endpoint)
            results.append(result)
            if result.errors:
                self.logger.warning(f"Endpoint {endpoint.name} has {len(result.errors)} errors")
            else:
                self.logger.info(f"Endpoint {endpoint.name} validated successfully")
        return results
    
    def generate_drift_report(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate a drift report based on validation results."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_endpoints": len(results),
            "healthy_endpoints": sum(1 for r in results if not r.errors),
            "unhealthy_endpoints": sum(1 for r in results if r.errors),
            "endpoints": [r.to_dict() for r in results]
        }
        return report
    
    def save_drift_report(self, report: Dict[str, Any]) -> str:
        """Save drift report to a JSON file."""
        date_str = datetime.now().strftime("%Y%m%d")
        report_path = f"{self.output_dir}/endpoint_drift_report_{date_str}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Drift report saved to {report_path}")
        return report_path

def main():
    """Main entry point for the endpoint validator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate API endpoint health")
    parser.add_argument("--config", required=True, help="Path to endpoint configuration file")
    parser.add_argument("--output-dir", default="./reports", help="Directory for output reports")
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    import os
    os.makedirs(args.output_dir, exist_ok=True)
    
    validator = EndpointValidator(args.config, args.output_dir)
    results = validator.validate_all_endpoints()
    report = validator.generate_drift_report(results)
    report_path = validator.save_drift_report(report)
    
    print(f"Validation complete. Report saved to {report_path}")

if __name__ == "__main__":
    main()
```

### Key Components:

1. **EndpointConfig**: Configuration class for each endpoint to be validated, including URL, method, expected status, and schema path.

2. **ValidationResult**: Class to store the results of endpoint validation, including status code, response time, and any errors or warnings.

3. **EndpointValidator**: Main class that handles loading configurations, validating endpoints, and generating reports.

4. **Schema Validation**: Uses the `jsonschema` library to validate response payloads against predefined JSON schemas.

5. **Logging**: Comprehensive logging to track validation activities and errors.

6. **Command-line Interface**: Simple CLI for running validations with configurable input and output paths.

## 5. Drift Reporting Output Format

The Endpoint Health Verification System will generate drift reports in JSON format to provide a structured, machine-readable record of endpoint validation results. The reports will be named according to the pattern `endpoint_drift_report_YYYYMMDD.json`.

### Sample Drift Report Structure:

```json
{
  "timestamp": "2025-04-27T15:30:00.000Z",
  "total_endpoints": 18,
  "healthy_endpoints": 16,
  "unhealthy_endpoints": 2,
  "endpoints": [
    {
      "endpoint_name": "agent_query",
      "timestamp": "2025-04-27T15:29:45.123Z",
      "status_code": 200,
      "response_time": 0.245,
      "schema_valid": true,
      "payload_valid": true,
      "errors": [],
      "warnings": []
    },
    {
      "endpoint_name": "knowledge_search",
      "timestamp": "2025-04-27T15:29:46.456Z",
      "status_code": 200,
      "response_time": 0.189,
      "schema_valid": true,
      "payload_valid": true,
      "errors": [],
      "warnings": ["Response time increased by 15% compared to baseline"]
    },
    {
      "endpoint_name": "auth_login",
      "timestamp": "2025-04-27T15:29:47.789Z",
      "status_code": 500,
      "response_time": 1.245,
      "schema_valid": false,
      "payload_valid": false,
      "errors": [
        "Expected status code 200, got 500",
        "Response is not valid JSON"
      ],
      "warnings": []
    }
  ],
  "performance_metrics": {
    "average_response_time": 0.312,
    "p50_response_time": 0.245,
    "p90_response_time": 0.789,
    "p99_response_time": 1.245
  },
  "historical_comparison": {
    "new_errors": 1,
    "resolved_errors": 0,
    "degraded_endpoints": 2,
    "improved_endpoints": 1
  }
}
```

### Key Report Sections:

1. **Report Metadata**:
   - `timestamp`: When the report was generated
   - `total_endpoints`: Total number of endpoints validated
   - `healthy_endpoints`: Number of endpoints with no errors
   - `unhealthy_endpoints`: Number of endpoints with errors

2. **Endpoint Details**:
   - `endpoint_name`: Identifier for the endpoint
   - `timestamp`: When the endpoint was validated
   - `status_code`: HTTP status code received
   - `response_time`: Time taken to receive response (in seconds)
   - `schema_valid`: Whether the response matches the expected schema
   - `payload_valid`: Whether the payload contains valid data
   - `errors`: List of validation errors (empty if none)
   - `warnings`: List of potential issues that don't constitute errors

3. **Performance Metrics**:
   - Aggregate statistics on response times
   - Percentile measurements (p50, p90, p99)

4. **Historical Comparison**:
   - Changes since the previous validation run
   - New and resolved errors
   - Performance trends (degraded or improved endpoints)

### Report Usage:

The drift reports will serve multiple purposes:

1. **Alerting**: Trigger notifications when critical endpoints fail validation
2. **Trending**: Track performance and reliability trends over time
3. **Debugging**: Provide detailed information for troubleshooting
4. **Compliance**: Document API health for compliance and audit purposes
5. **Dashboarding**: Feed data into monitoring dashboards

The JSON format ensures that reports can be easily parsed by automated systems, integrated with monitoring tools, and archived for historical analysis.

## 6. Implementation Plan

The implementation of the Endpoint Health Verification System will proceed in the following phases:

1. **Configuration Setup**:
   - Create endpoint configuration files
   - Define JSON schemas for response validation
   - Set up directory structure for reports and logs

2. **Core Validator Development**:
   - Implement the `endpoint_validator.py` tool
   - Develop unit tests for validation logic
   - Create mock endpoints for testing

3. **Integration and Testing**:
   - Test against development endpoints
   - Refine validation logic based on test results
   - Optimize performance for large-scale validation

4. **Reporting and Alerting**:
   - Implement drift report generation
   - Develop alerting mechanisms for critical failures
   - Create visualization tools for report data

5. **Deployment and Automation**:
   - Set up scheduled validation runs
   - Configure CI/CD integration
   - Document usage and maintenance procedures

## 7. Future Enhancements

While the initial implementation will focus on basic endpoint health verification, several enhancements could be considered for future phases:

1. **Advanced Validation**:
   - Content-based validation (beyond schema checking)
   - Cross-endpoint consistency validation
   - Stateful transaction validation

2. **Performance Testing**:
   - Load testing integration
   - Stress testing capabilities
   - Concurrency testing

3. **Security Validation**:
   - Authentication/authorization testing
   - Security header verification
   - OWASP vulnerability checking

4. **Intelligent Analysis**:
   - Machine learning for anomaly detection
   - Predictive failure analysis
   - Automated root cause identification

5. **Extended Reporting**:
   - Interactive dashboards
   - Trend analysis reports
   - SLA compliance reporting
