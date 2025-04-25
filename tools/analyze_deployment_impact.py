#!/usr/bin/env python3
"""
Deployment Impact Analyzer
Analyzes the impact of deployed fixes and investigates why they haven't improved endpoint status.
"""

import os
import json
import datetime
from collections import defaultdict

# Configuration
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
FRESH_SWEEP_FILE = "/home/ubuntu/personal-ai-agent/logs/postman_sweep_after_deployment.json"
COMPARISON_FILE = "/home/ubuntu/personal-ai-agent/logs/deployment_impact_analysis.json"
FIX_IMPLEMENTATION_FILE = "/home/ubuntu/personal-ai-agent/logs/endpoint_fix_implementation.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/deployment_fix_analysis.json"

def load_fresh_sweep():
    """Load fresh Postman sweep results"""
    with open(FRESH_SWEEP_FILE, "r") as f:
        return json.load(f)

def load_comparison():
    """Load deployment impact comparison"""
    with open(COMPARISON_FILE, "r") as f:
        return json.load(f)

def load_fix_implementation():
    """Load fix implementation details"""
    with open(FIX_IMPLEMENTATION_FILE, "r") as f:
        return json.load(f)

def analyze_fixed_endpoints_status(fresh_sweep, fix_implementation):
    """Analyze the status of fixed endpoints in the fresh sweep"""
    fixed_endpoints = []
    for fixed in fix_implementation["fixed_endpoints"]:
        endpoint = fixed["endpoint"]
        method = endpoint["method"]
        route_path = endpoint["route_path"]
        
        # Find this endpoint in the fresh sweep
        for result in fresh_sweep["results"]:
            if result["method"] == method and result["route_path"] == route_path:
                fixed_endpoints.append({
                    "method": method,
                    "route_path": route_path,
                    "status_code": result["status_code"],
                    "status": result["status"],
                    "fix_type": endpoint["fix_type"],
                    "priority": endpoint["priority"],
                    "fix_details": fixed["result"]
                })
                break
    
    return fixed_endpoints

def categorize_fixed_endpoints(fixed_endpoints):
    """Categorize fixed endpoints by status code"""
    status_endpoints = defaultdict(list)
    
    for endpoint in fixed_endpoints:
        status_code = endpoint["status_code"]
        if status_code is None:
            status_code = "error"
        status_endpoints[status_code].append(endpoint)
    
    return status_endpoints

def identify_deployment_issues(fixed_endpoints, status_endpoints):
    """Identify issues with the deployment of fixes"""
    issues = []
    
    # Check if any fixed endpoints are still returning errors
    if 500 in status_endpoints or "error" in status_endpoints:
        issues.append({
            "issue_type": "server_errors",
            "description": "Some fixed endpoints are still returning server errors",
            "affected_endpoints": status_endpoints.get(500, []) + status_endpoints.get("error", []),
            "severity": "high"
        })
    
    # Check if fixed endpoints are still returning 404
    if 404 in status_endpoints:
        issues.append({
            "issue_type": "not_found",
            "description": "Some fixed endpoints are still returning 404 Not Found",
            "affected_endpoints": status_endpoints[404],
            "severity": "high"
        })
    
    # Check if no fixed endpoints improved
    if all(endpoint["status_code"] not in [200, 422] for endpoint in fixed_endpoints):
        issues.append({
            "issue_type": "no_improvements",
            "description": "None of the fixed endpoints improved their status",
            "affected_endpoints": fixed_endpoints,
            "severity": "critical"
        })
    
    return issues

def generate_next_steps(issues, fixed_endpoints):
    """Generate recommendations for next steps based on identified issues"""
    recommendations = []
    
    # If there are critical issues, recommend checking deployment
    if any(issue["severity"] == "critical" for issue in issues):
        recommendations.append({
            "recommendation": "Verify deployment process",
            "description": "Check if the fixes were actually deployed to the production server",
            "steps": [
                "Confirm deployment logs show successful deployment",
                "Check if the server was restarted after deployment",
                "Verify the deployed code matches the fixed code"
            ],
            "priority": "critical"
        })
    
    # If there are server errors, recommend investigating them
    if any(issue["issue_type"] == "server_errors" for issue in issues):
        recommendations.append({
            "recommendation": "Investigate server errors",
            "description": "Check server logs to understand why fixed endpoints are still returning errors",
            "steps": [
                "Access server logs for error details",
                "Check for syntax errors or missing dependencies",
                "Verify environment variables and configuration"
            ],
            "priority": "high"
        })
    
    # If endpoints are still not found, recommend checking routing
    if any(issue["issue_type"] == "not_found" for issue in issues):
        recommendations.append({
            "recommendation": "Check routing configuration",
            "description": "Verify that routes are properly registered in the application",
            "steps": [
                "Confirm main.py includes all router imports",
                "Check that app.include_router() calls are present for all routers",
                "Verify route paths match the expected format"
            ],
            "priority": "high"
        })
    
    # Recommend continuing with the next batch of fixes
    recommendations.append({
        "recommendation": "Continue with next batch of fixes",
        "description": "Proceed with fixing the next batch of endpoints while investigating deployment issues",
        "steps": [
            "Identify high-priority endpoints for the next batch",
            "Implement fixes for these endpoints",
            "Include more detailed logging to diagnose deployment issues"
        ],
        "priority": "medium"
    })
    
    # Recommend direct server-side fixes
    recommendations.append({
        "recommendation": "Consider direct server-side fixes",
        "description": "If deployment issues persist, consider making changes directly on the server",
        "steps": [
            "Request server access credentials",
            "Make minimal changes directly on the server to test deployment",
            "Document any changes made for future reference"
        ],
        "priority": "low"
    })
    
    return recommendations

def main():
    """Main function to analyze deployment impact"""
    print("Starting deployment impact analysis...")
    
    # Load data
    fresh_sweep = load_fresh_sweep()
    comparison = load_comparison()
    fix_implementation = load_fix_implementation()
    print("Loaded fresh sweep, comparison, and fix implementation data")
    
    # Analyze fixed endpoints status
    fixed_endpoints = analyze_fixed_endpoints_status(fresh_sweep, fix_implementation)
    print(f"Analyzed status of {len(fixed_endpoints)} fixed endpoints")
    
    # Categorize fixed endpoints
    status_endpoints = categorize_fixed_endpoints(fixed_endpoints)
    print("Categorized fixed endpoints by status:")
    for status, endpoints in status_endpoints.items():
        print(f"  {status}: {len(endpoints)}")
    
    # Identify deployment issues
    issues = identify_deployment_issues(fixed_endpoints, status_endpoints)
    print(f"Identified {len(issues)} deployment issues")
    
    # Generate next steps
    recommendations = generate_next_steps(issues, fixed_endpoints)
    print(f"Generated {len(recommendations)} recommendations")
    
    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Prepare output
    output = {
        "timestamp": timestamp,
        "success_rate": fresh_sweep["analysis"]["success_rate"],
        "success_rate_change": comparison["comparison"]["success_rate_change"],
        "fixed_endpoints": fixed_endpoints,
        "status_breakdown": {str(status): len(endpoints) for status, endpoints in status_endpoints.items()},
        "issues": issues,
        "recommendations": recommendations
    }
    
    # Save output to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Deployment impact analysis completed. Results saved to {OUTPUT_FILE}")
    
    # Print summary
    print("\nDeployment Analysis Summary:")
    print(f"Success Rate: {output['success_rate']}%")
    print(f"Success Rate Change: {output['success_rate_change']}%")
    print("\nFixed Endpoints Status:")
    for status, count in output["status_breakdown"].items():
        print(f"  {status}: {count}")
    
    print("\nKey Issues:")
    for issue in issues:
        print(f"  - {issue['description']} (Severity: {issue['severity']})")
    
    print("\nTop Recommendations:")
    for rec in sorted(recommendations, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x["priority"]]):
        print(f"  - {rec['recommendation']} (Priority: {rec['priority']})")
    
    return output

if __name__ == "__main__":
    main()
