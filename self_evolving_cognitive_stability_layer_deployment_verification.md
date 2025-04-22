# Self-Evolving Cognitive Stability Layer Deployment Verification

This document provides instructions for verifying the deployment of the Self-Evolving Cognitive Stability Layer for Promethios.

## Prerequisites

- Promethios core system installed and running
- Python 3.8 or higher
- Access to the Promethios configuration system

## Verification Steps

Follow these steps to verify that the Self-Evolving Cognitive Stability Layer is properly deployed and functioning:

### 1. Verify Component Installation

First, verify that all components are properly installed:

```python
# Check Rebuilder Agent
from app.plugins.agents.rebuilder.rebuilder import run_agent
print("Rebuilder Agent installed:", run_agent is not None)

# Check Project Manifest System
from app.modules.project_manifest import load_manifest, get_manifest_summary
print("Project Manifest System installed:", load_manifest is not None and get_manifest_summary is not None)

# Check Loop CI Test Runner
from app.modules.loop_ci_test_runner import run_tests, get_latest_result
print("Loop CI Test Runner installed:", run_tests is not None and get_latest_result is not None)

# Check Integration Module
from app.modules.loop_hardening_integration import StabilityIntegration
print("Integration Module installed:", StabilityIntegration is not None)
```

All checks should print `True` if the components are properly installed.

### 2. Verify Project Manifest

Check that the project manifest can be loaded and accessed:

```python
from app.modules.project_manifest import load_manifest, get_manifest_summary

# Load project manifest
project_id = "promethios-core"  # Replace with your project ID
manifest = load_manifest(project_id)
print("Project Manifest loaded:", manifest is not None)

# Get manifest summary
summary = get_manifest_summary(project_id)
print("Manifest Summary:", summary)
```

The manifest summary should show information about the project, including modules, belief versions, and stability scores.

### 3. Run CI Tests

Verify that the Loop CI Test Runner can execute tests:

```python
from app.modules.loop_ci_test_runner import run_tests, get_latest_result

# Run CI tests for a single module
project_id = "promethios-core"  # Replace with your project ID
module_name = "loop"  # Replace with a module name from your project
result = run_tests(project_id, [module_name])
print("CI Test Result:", result)

# Get latest result
latest = get_latest_result(project_id)
print("Latest CI Result:", latest)
```

The test result should include information about the tests that were run, including status, scores, and any failures.

### 4. Run Stability Check

Verify that the Rebuilder Agent can perform a stability check:

```python
from app.plugins.agents.rebuilder.rebuilder import run_agent

# Create context for Rebuilder Agent
context = {
    "project_id": "promethios-core",  # Replace with your project ID
    "orchestrator_mode": "BALANCED",
    "loop_id": f"verification-{int(time.time())}"
}

# Run Rebuilder Agent
result = run_agent(context)
print("Stability Check Result:", result)
```

The stability check result should include a stability score, rebuild events (if any), and recommendations.

### 5. Start Monitoring

Verify that the stability monitoring can be started:

```python
from app.modules.loop_hardening_integration import StabilityIntegration

# Create stability integration
project_id = "promethios-core"  # Replace with your project ID
integration = StabilityIntegration(project_id)

# Start background tasks
success = integration.start_background_tasks()
print("Monitoring Started:", success)

# Wait for a few seconds
import time
time.sleep(5)

# Stop background tasks
success = integration.stop_background_tasks()
print("Monitoring Stopped:", success)
```

Both the start and stop operations should print `True` if successful.

### 6. Verify Schema Compatibility

Verify that the schema updates are compatible with existing systems:

```python
import json
import os

# Load schema files
schema_dir = "/home/ubuntu/repo/personal-ai-agent/app/loop/debug"
schema_v1 = json.load(open(os.path.join(schema_dir, "loop_trace.schema.v1.0.0.json")))
schema_v2 = json.load(open(os.path.join(schema_dir, "loop_trace.schema.v1.0.2.json")))

# Check that all required properties in v1 are also in v2
v1_required = set(schema_v1.get("required", []))
v2_required = set(schema_v2.get("required", []))
print("All v1 required properties in v2:", v1_required.issubset(v2_required))

# Check that all v1 properties exist in v2
v1_properties = set(schema_v1.get("properties", {}).keys())
v2_properties = set(schema_v2.get("properties", {}).keys())
print("All v1 properties in v2:", v1_properties.issubset(v2_properties))
```

Both checks should print `True` if the schema updates are backward compatible.

### 7. Verify Sample Files

Verify that the sample files are properly formatted and can be loaded:

```python
import json
import os

# Load sample files
data_dir = "/home/ubuntu/repo/personal-ai-agent/data"
manifest_file = os.path.join(data_dir, "project_manifest/promethios-core.json")
ci_result_file = os.path.join(data_dir, "ci_results/promethios-core_20250422033700.json")
loop_trace_file = os.path.join(data_dir, "loop_traces/stability-check-20250422033800.json")

# Load and verify manifest
manifest = json.load(open(manifest_file))
print("Manifest loaded:", "project_id" in manifest and "modules" in manifest)

# Load and verify CI result
ci_result = json.load(open(ci_result_file))
print("CI Result loaded:", "project_id" in ci_result and "module_results" in ci_result)

# Load and verify loop trace
loop_trace = json.load(open(loop_trace_file))
print("Loop Trace loaded:", "loop_id" in loop_trace and "rebuild_events" in loop_trace)
```

All checks should print `True` if the sample files are properly formatted and can be loaded.

## Troubleshooting

If any of the verification steps fail, check the following:

1. **Component Installation**: Ensure that all components are properly installed and accessible.
2. **File Permissions**: Ensure that the system has proper permissions to read and write files.
3. **Configuration**: Check the configuration files for any errors or missing values.
4. **Dependencies**: Ensure that all dependencies are installed and accessible.
5. **Logs**: Check the system logs for any error messages or warnings.

## Next Steps

After verifying the deployment, you can:

1. **Configure Monitoring**: Adjust the monitoring configuration to suit your needs.
2. **Integrate with Workflows**: Integrate the stability checks into your existing workflows.
3. **Set Up Notifications**: Configure notifications for stability issues.
4. **Train Users**: Train users on how to interpret and respond to stability reports.

## Support

If you encounter any issues during deployment verification, please contact the Promethios support team for assistance.
