#!/bin/bash

# Recalculate API Health Percentage for API Sweep V7
# This script corrects the health percentage calculation based on expected working endpoints

# Configuration
RESULTS_DIR="/home/ubuntu/api_sweep_v7"
SUMMARY_FILE="$RESULTS_DIR/api_sweep_v7_summary.md"
CORRECTED_SUMMARY_FILE="$RESULTS_DIR/api_sweep_v7_summary_corrected.md"

# Define expected working endpoints (marked with ✅ in the requirements)
EXPECTED_WORKING_ENDPOINTS=(
    "/api/agent/list"
    "/api/agent/run"
    "/api/agent/loop"
    "/api/agent/delegate"
    "/api/memory/write"
    "/api/memory/read"
    "/api/memory/thread"
    "/api/memory/summarize"
    "/api/debug/memory/log"
    "/api/project/state"
    "/api/orchestrator/consult"
)

# Define expected failing endpoints (marked with ❌ in the requirements)
EXPECTED_FAILING_ENDPOINTS=(
    "/api/train"
    "/api/plan"
    "/api/snapshot"
    "/api/status"
    "/api/system/integrity"
    "/api/debug/agents"
)

# Count total expected working endpoints
TOTAL_EXPECTED_WORKING=$(echo "${#EXPECTED_WORKING_ENDPOINTS[@]}")

# Initialize counters
ACTUAL_WORKING=0
ACTUAL_FAILING=0

# Read the summary file and count actual working endpoints
while IFS= read -r line; do
    # Check if line contains endpoint info
    if [[ $line == *"| /api/"* && $line == *"PASS"* ]]; then
        endpoint=$(echo "$line" | awk -F'|' '{print $2}' | awk -F'?' '{print $1}' | xargs)
        
        # Check if this endpoint was expected to work
        for expected in "${EXPECTED_WORKING_ENDPOINTS[@]}"; do
            if [[ "$endpoint" == "$expected"* ]]; then
                ((ACTUAL_WORKING++))
                break
            fi
        done
    fi
    
    # Check if line contains failing endpoint that was expected to work
    if [[ $line == *"| /api/"* && $line == *"FAIL"* ]]; then
        endpoint=$(echo "$line" | awk -F'|' '{print $2}' | awk -F'?' '{print $1}' | xargs)
        
        # Check if this endpoint was expected to work
        for expected in "${EXPECTED_WORKING_ENDPOINTS[@]}"; do
            if [[ "$endpoint" == "$expected"* ]]; then
                ((ACTUAL_FAILING++))
                break
            fi
        done
    fi
done < "$SUMMARY_FILE"

# Calculate corrected health percentage
HEALTH_PERCENTAGE=$(echo "scale=2; ($ACTUAL_WORKING / $TOTAL_EXPECTED_WORKING) * 100" | bc)

# Create corrected summary file
cp "$SUMMARY_FILE" "$CORRECTED_SUMMARY_FILE"

# Update the health percentage in the corrected summary file
sed -i "s/- API Health Percentage: .*%/- API Health Percentage: ${HEALTH_PERCENTAGE}%/" "$CORRECTED_SUMMARY_FILE"

# Add explanation about the calculation
cat >> "$CORRECTED_SUMMARY_FILE" << EOF

## Corrected Health Percentage Calculation

The API health percentage has been recalculated based on the expected working endpoints from the requirements:
- Total expected working endpoints: $TOTAL_EXPECTED_WORKING
- Actually working endpoints: $ACTUAL_WORKING
- Failed endpoints that should be working: $ACTUAL_FAILING
- Corrected health percentage: ${HEALTH_PERCENTAGE}%

This calculation only considers endpoints that were expected to work (marked with ✅ in the requirements)
and does not include endpoints that were expected to fail (marked with ❌ in the requirements).
EOF

echo "Corrected API health percentage: ${HEALTH_PERCENTAGE}%"
echo "Corrected summary saved to: $CORRECTED_SUMMARY_FILE"
