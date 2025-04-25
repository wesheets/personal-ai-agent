#!/usr/bin/env python3
"""
Final Endpoint Repair Report Generator
Generates a comprehensive report on endpoint repair results and recommendations.
"""

import os
import json
import datetime
from pathlib import Path

# Configuration
LOGS_DIR = "/home/ubuntu/personal-ai-agent/logs"
VERIFICATION_FILE = "/home/ubuntu/personal-ai-agent/logs/endpoint_status_verification.json"
POSTMAN_SWEEP_FILE = "/home/ubuntu/personal-ai-agent/logs/postman_sweep_after_deploy.json"
FIX_IMPLEMENTATION_FILE = "/home/ubuntu/personal-ai-agent/logs/endpoint_fix_implementation.json"
OUTPUT_FILE = "/home/ubuntu/personal-ai-agent/logs/final_endpoint_repair_report.json"
MEMORY_EVENT_FILE = "/home/ubuntu/personal-ai-agent/app/logs/memory_events/endpoint_repair_report_{timestamp}.json"

def load_verification_results():
    """Load endpoint verification results"""
    with open(VERIFICATION_FILE, "r") as f:
        return json.load(f)

def load_postman_sweep_results():
    """Load Postman sweep validation results"""
    with open(POSTMAN_SWEEP_FILE, "r") as f:
        return json.load(f)

def load_fix_implementation_results():
    """Load fix implementation results"""
    with open(FIX_IMPLEMENTATION_FILE, "r") as f:
        return json.load(f)

def generate_success_summary(verification_results):
    """Generate a summary of successful endpoints"""
    success_rate = verification_results["success_rate"]
    success_count = verification_results["success_count"]
    unprocessable_count = verification_results["unprocessable_count"]
    total_endpoints = verification_results["total_endpoints"]
    
    return {
        "success_rate": success_rate,
        "success_count": success_count,
        "unprocessable_count": unprocessable_count,
        "total_endpoints": total_endpoints,
        "operational_count": success_count + unprocessable_count,
        "operational_rate": round((success_count + unprocessable_count) / total_endpoints * 100, 1)
    }

def generate_failure_summary(verification_results):
    """Generate a summary of failed endpoints"""
    not_found_count = verification_results["not_found_count"]
    server_error_count = verification_results["server_error_count"]
    error_count = verification_results["error_count"]
    total_endpoints = verification_results["total_endpoints"]
    
    return {
        "not_found_count": not_found_count,
        "server_error_count": server_error_count,
        "error_count": error_count,
        "total_failure_count": not_found_count + server_error_count + error_count,
        "failure_rate": round((not_found_count + server_error_count + error_count) / total_endpoints * 100, 1)
    }

def generate_fixed_endpoints_summary(verification_results, fix_results):
    """Generate a summary of fixed endpoints"""
    fixed_endpoints = verification_results["fixed_endpoints"]
    fixed_count = fixed_endpoints["total"]
    fixed_success_rate = fixed_endpoints["success_rate"]
    status_breakdown = fixed_endpoints["status_breakdown"]
    
    return {
        "fixed_count": fixed_count,
        "fixed_success_rate": fixed_success_rate,
        "status_breakdown": status_breakdown,
        "fixed_details": fix_results["fixed_endpoints"]
    }

def generate_module_summary(verification_results, sweep_results):
    """Generate a summary of endpoint status by module"""
    module_endpoints = verification_results["module_endpoints"]
    results = sweep_results["results"]
    
    # Group results by module
    module_results = {}
    for module, count in module_endpoints.items():
        module_results[module] = {
            "total": count,
            "operational": 0,
            "not_found": 0,
            "server_error": 0,
            "error": 0
        }
    
    # Count status codes for each module
    for result in results:
        route_path = result["route_path"]
        parts = route_path.strip("/").split("/")
        
        if parts:
            module = parts[0]
            status_code = result.get("status_code")
            
            if status_code == 200 or status_code == 422:
                module_results[module]["operational"] += 1
            elif status_code == 404:
                module_results[module]["not_found"] += 1
            elif status_code and status_code >= 500:
                module_results[module]["server_error"] += 1
            else:
                module_results[module]["error"] += 1
    
    # Calculate success rate for each module
    for module, data in module_results.items():
        if data["total"] > 0:
            data["success_rate"] = round(data["operational"] / data["total"] * 100, 1)
        else:
            data["success_rate"] = 0
    
    # Sort modules by success rate
    sorted_modules = sorted(module_results.items(), key=lambda x: x[1]["success_rate"], reverse=True)
    
    return {
        "module_count": len(module_results),
        "modules": {module: data for module, data in sorted_modules}
    }

def generate_critical_failures_summary(verification_results):
    """Generate a summary of critical failures"""
    critical_failures = verification_results["critical_failures"]
    
    return {
        "critical_failure_count": len(critical_failures),
        "critical_failures": critical_failures
    }

def generate_next_steps_recommendations(verification_results, sweep_results):
    """Generate recommendations for next steps"""
    next_batch = verification_results["next_batch_recommendations"]
    
    # Group recommendations by priority
    priority_recommendations = {
        "high": [],
        "medium": [],
        "low": []
    }
    
    for rec in next_batch:
        priority = rec["priority"]
        priority_recommendations[priority].append(rec)
    
    # Generate deployment recommendations
    deployment_recommendations = []
    
    # If fixed endpoints have 0% success rate, recommend deployment
    if verification_results["fixed_endpoints"]["success_rate"] == 0:
        deployment_recommendations.append({
            "recommendation": "Deploy local fixes to server",
            "reason": "Fixed endpoints have 0% success rate, indicating local fixes haven't been deployed",
            "priority": "high"
        })
    
    # If there are server errors, recommend investigating them
    if verification_results["server_error_count"] > 0:
        deployment_recommendations.append({
            "recommendation": "Investigate server errors",
            "reason": f"There are {verification_results['server_error_count']} endpoints returning server errors",
            "priority": "high"
        })
    
    # Recommend fixing critical modules first
    critical_modules = ["agent", "memory", "loop", "orchestrator", "hal", "forge"]
    for module in critical_modules:
        if module in verification_results["module_endpoints"]:
            deployment_recommendations.append({
                "recommendation": f"Focus on fixing {module} module endpoints",
                "reason": f"{module} is a critical module for system functionality",
                "priority": "medium"
            })
    
    return {
        "next_batch": next_batch,
        "deployment_recommendations": deployment_recommendations,
        "priority_recommendations": priority_recommendations
    }

def main():
    """Main function to generate final endpoint repair report"""
    print("Starting final endpoint repair report generation...")
    
    # Load results
    verification_results = load_verification_results()
    sweep_results = load_postman_sweep_results()
    fix_results = load_fix_implementation_results()
    print("Loaded verification, sweep, and fix implementation results")
    
    # Generate summaries
    success_summary = generate_success_summary(verification_results)
    failure_summary = generate_failure_summary(verification_results)
    fixed_endpoints_summary = generate_fixed_endpoints_summary(verification_results, fix_results)
    module_summary = generate_module_summary(verification_results, sweep_results)
    critical_failures_summary = generate_critical_failures_summary(verification_results)
    next_steps = generate_next_steps_recommendations(verification_results, sweep_results)
    
    print("Generated summaries for success, failure, fixed endpoints, modules, critical failures, and next steps")
    
    # Generate timestamp for memory tag
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    memory_tag = f"endpoint_repair_report_{timestamp}"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # Prepare output
    output = {
        "timestamp": timestamp,
        "memory_tag": memory_tag,
        "success_summary": success_summary,
        "failure_summary": failure_summary,
        "fixed_endpoints_summary": fixed_endpoints_summary,
        "module_summary": module_summary,
        "critical_failures_summary": critical_failures_summary,
        "next_steps": next_steps
    }
    
    # Save output to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Final endpoint repair report generated. Results saved to {OUTPUT_FILE}")
    
    # Save memory event
    memory_event_file = MEMORY_EVENT_FILE.format(timestamp=timestamp)
    os.makedirs(os.path.dirname(memory_event_file), exist_ok=True)
    
    memory_event = {
        "event_type": "endpoint_repair_report",
        "timestamp": timestamp,
        "tag": memory_tag,
        "success_rate": success_summary["success_rate"],
        "operational_rate": success_summary["operational_rate"],
        "fixed_endpoints_success_rate": fixed_endpoints_summary["fixed_success_rate"],
        "critical_failures_count": critical_failures_summary["critical_failure_count"],
        "next_steps": "Deploy local fixes to server and continue fixing remaining endpoints"
    }
    
    with open(memory_event_file, 'w') as f:
        json.dump(memory_event, f, indent=2)
    
    print(f"Memory event saved to {memory_event_file}")
    
    # Print summary
    print("\nEndpoint Repair Summary:")
    print(f"Total Endpoints: {success_summary['total_endpoints']}")
    print(f"Operational Endpoints: {success_summary['operational_count']} ({success_summary['operational_rate']}%)")
    print(f"Failed Endpoints: {failure_summary['total_failure_count']} ({failure_summary['failure_rate']}%)")
    print(f"Fixed Endpoints: {fixed_endpoints_summary['fixed_count']} (Success Rate: {fixed_endpoints_summary['fixed_success_rate']}%)")
    print(f"Critical Failures: {critical_failures_summary['critical_failure_count']}")
    print("\nTop Recommendations:")
    for rec in next_steps["deployment_recommendations"][:3]:
        print(f"  - {rec['recommendation']} ({rec['priority']})")
    
    return output

if __name__ == "__main__":
    main()
