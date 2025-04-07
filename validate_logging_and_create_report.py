import os
import json
import datetime
import glob

def validate_logging_and_create_report():
    """
    - Validate logging in:
        - /logs/execution_logs/
        - /logs/control_violations.json
        - /logs/task_state_log.json
        - /logs/diagnostics/
    - Output summary to /logs/diagnostics/system_readiness_report.json
    """
    base_log_dir = "/home/ubuntu/personal-ai-agent/app/logs"
    report_file = f"{base_log_dir}/diagnostics/system_readiness_report.json"
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    # Initialize report
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "system_name": "Personal AI Agent",
        "diagnostic_summary": {
            "total_checks": 7,
            "passed_checks": 0,
            "failed_checks": 0,
            "success_rate": 0
        },
        "component_status": {
            "tools": {
                "status": "unknown",
                "details": {}
            },
            "agents": {
                "status": "unknown",
                "details": {}
            },
            "control_system": {
                "status": "unknown",
                "details": {}
            },
            "memory_system": {
                "status": "unknown",
                "details": {}
            },
            "task_orchestration": {
                "status": "unknown",
                "details": {}
            },
            "logging_system": {
                "status": "unknown",
                "details": {}
            }
        },
        "logging_validation": {
            "execution_logs": {
                "exists": False,
                "entries_found": 0,
                "status": "failure"
            },
            "control_violations": {
                "exists": False,
                "entries_found": 0,
                "status": "failure"
            },
            "task_state_log": {
                "exists": False,
                "entries_found": 0,
                "status": "failure"
            },
            "diagnostics": {
                "exists": False,
                "entries_found": 0,
                "status": "failure"
            }
        },
        "recommendations": [],
        "overall_status": "failure"
    }
    
    # Check execution logs
    execution_logs_dir = f"{base_log_dir}/execution_logs"
    if os.path.exists(execution_logs_dir) and os.path.isdir(execution_logs_dir):
        report["logging_validation"]["execution_logs"]["exists"] = True
        log_files = glob.glob(f"{execution_logs_dir}/*.json")
        report["logging_validation"]["execution_logs"]["entries_found"] = len(log_files)
        if len(log_files) > 0:
            report["logging_validation"]["execution_logs"]["status"] = "success"
    else:
        # Create directory if it doesn't exist
        os.makedirs(execution_logs_dir, exist_ok=True)
        report["recommendations"].append("Create sample execution logs for testing")
    
    # Check control violations log
    control_violations_file = f"{base_log_dir}/control_violations.json"
    if os.path.exists(control_violations_file):
        report["logging_validation"]["control_violations"]["exists"] = True
        try:
            with open(control_violations_file, 'r') as f:
                violations = json.load(f)
                if "violations" in violations:
                    report["logging_validation"]["control_violations"]["entries_found"] = len(violations["violations"])
                    if len(violations["violations"]) > 0:
                        report["logging_validation"]["control_violations"]["status"] = "success"
        except Exception as e:
            report["recommendations"].append(f"Fix control_violations.json: {str(e)}")
    
    # Check task state log
    task_state_file = f"{base_log_dir}/task_state_log.json"
    if os.path.exists(task_state_file):
        report["logging_validation"]["task_state_log"]["exists"] = True
        try:
            with open(task_state_file, 'r') as f:
                tasks = json.load(f)
                if "tasks" in tasks:
                    report["logging_validation"]["task_state_log"]["entries_found"] = len(tasks["tasks"])
                    if len(tasks["tasks"]) > 0:
                        report["logging_validation"]["task_state_log"]["status"] = "success"
        except Exception as e:
            report["recommendations"].append(f"Fix task_state_log.json: {str(e)}")
    
    # Check diagnostics directory
    diagnostics_dir = f"{base_log_dir}/diagnostics"
    if os.path.exists(diagnostics_dir) and os.path.isdir(diagnostics_dir):
        report["logging_validation"]["diagnostics"]["exists"] = True
        diagnostic_files = glob.glob(f"{diagnostics_dir}/*.json")
        report["logging_validation"]["diagnostics"]["entries_found"] = len(diagnostic_files)
        if len(diagnostic_files) > 0:
            report["logging_validation"]["diagnostics"]["status"] = "success"
    
    # Load and incorporate previous diagnostic results
    diagnostic_files = {
        "tool_health_report.json": "tools",
        "agent_execution_test.json": "agents",
        "control_violation_simulation.json": "control_system",
        "vector_memory_schema.json": "memory_system",
        "task_memory_loop_check.json": "task_orchestration"
    }
    
    passed_checks = 0
    
    for file_name, component in diagnostic_files.items():
        file_path = f"{diagnostics_dir}/{file_name}"
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                    # Extract status
                    status = data.get("status", "unknown")
                    if status == "success":
                        passed_checks += 1
                        report["component_status"][component]["status"] = "operational"
                    else:
                        report["component_status"][component]["status"] = "issues_detected"
                    
                    # Add details
                    report["component_status"][component]["details"] = {
                        "diagnostic_file": file_name,
                        "timestamp": data.get("timestamp", "unknown"),
                        "status": status
                    }
                    
                    # Add component-specific details
                    if component == "tools":
                        report["component_status"][component]["details"].update({
                            "total_tools": data.get("total_tools", 0),
                            "tools_with_run_method": data.get("tools_with_run_method", 0),
                            "success_rate": data.get("success_rate", 0)
                        })
                    elif component == "agents":
                        report["component_status"][component]["details"].update({
                            "total_agents": data.get("total_agents", 0),
                            "successful_agents": data.get("successful_agents", 0),
                            "success_rate": data.get("success_rate", 0)
                        })
            except Exception as e:
                report["recommendations"].append(f"Fix {file_name}: {str(e)}")
    
    # Check logging system status
    logging_statuses = [
        report["logging_validation"]["execution_logs"]["status"],
        report["logging_validation"]["control_violations"]["status"],
        report["logging_validation"]["task_state_log"]["status"],
        report["logging_validation"]["diagnostics"]["status"]
    ]
    
    if all(status == "success" for status in logging_statuses):
        report["component_status"]["logging_system"]["status"] = "operational"
        passed_checks += 1
    elif any(status == "success" for status in logging_statuses):
        report["component_status"]["logging_system"]["status"] = "partially_operational"
    else:
        report["component_status"]["logging_system"]["status"] = "not_operational"
    
    report["component_status"]["logging_system"]["details"] = {
        "execution_logs": report["logging_validation"]["execution_logs"]["status"],
        "control_violations": report["logging_validation"]["control_violations"]["status"],
        "task_state_log": report["logging_validation"]["task_state_log"]["status"],
        "diagnostics": report["logging_validation"]["diagnostics"]["status"]
    }
    
    # Update diagnostic summary
    report["diagnostic_summary"]["passed_checks"] = passed_checks
    report["diagnostic_summary"]["failed_checks"] = report["diagnostic_summary"]["total_checks"] - passed_checks
    report["diagnostic_summary"]["success_rate"] = (passed_checks / report["diagnostic_summary"]["total_checks"]) * 100
    
    # Determine overall status
    if report["diagnostic_summary"]["success_rate"] >= 85:
        report["overall_status"] = "ready"
    elif report["diagnostic_summary"]["success_rate"] >= 70:
        report["overall_status"] = "ready_with_warnings"
    else:
        report["overall_status"] = "not_ready"
    
    # Add final recommendations
    if report["overall_status"] != "ready":
        for component, details in report["component_status"].items():
            if details["status"] != "operational":
                report["recommendations"].append(f"Fix issues with {component.replace('_', ' ')}")
    
    # Write report to file
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"System readiness report completed. Results saved to {report_file}")
    print(f"Total checks: {report['diagnostic_summary']['total_checks']}")
    print(f"Passed checks: {report['diagnostic_summary']['passed_checks']}")
    print(f"Failed checks: {report['diagnostic_summary']['failed_checks']}")
    print(f"Success rate: {report['diagnostic_summary']['success_rate']:.2f}%")
    print(f"Overall status: {report['overall_status']}")
    
    return report

if __name__ == "__main__":
    validate_logging_and_create_report()
