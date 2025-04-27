#!/bin/bash
# Post-Merge Validation Hook Script
#
# This script triggers the Post-Merge Surface Validation system after code merges.
# It should be run manually after merging code into the main branch.
#
# Usage: ./merge_hook.sh [--verbose]

set -e

# Parse arguments
VERBOSE=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose|-v)
      VERBOSE="--verbose"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./merge_hook.sh [--verbose]"
      exit 1
      ;;
  esac
done

# Determine script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "========================================================"
echo "🔍 PROMETHIOS POST-MERGE VALIDATION"
echo "========================================================"
echo "Starting post-merge validation at $(date)"
echo "Project root: ${PROJECT_ROOT}"
echo "========================================================"

# Create logs directory if it doesn't exist
mkdir -p "${PROJECT_ROOT}/logs"

# Log file for this run
LOG_FILE="${PROJECT_ROOT}/logs/postmerge_hook_$(date +%Y%m%d_%H%M%S).log"
echo "Log file: ${LOG_FILE}"

# Function to log messages
log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $1" | tee -a "${LOG_FILE}"
}

# Check if we're in a git repository
if [ ! -d "${PROJECT_ROOT}/.git" ]; then
  log "❌ ERROR: Not a git repository. This script should be run from a Promethios git repository."
  exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git -C "${PROJECT_ROOT}" rev-parse --abbrev-ref HEAD)
log "Current branch: ${CURRENT_BRANCH}"

# Warn if not on main branch
if [ "${CURRENT_BRANCH}" != "main" ] && [ "${CURRENT_BRANCH}" != "master" ]; then
  log "⚠️  WARNING: You are not on the main branch. Post-merge validation is typically run after merging to main."
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Validation cancelled by user."
    exit 0
  fi
fi

# Get latest commit info
LATEST_COMMIT=$(git -C "${PROJECT_ROOT}" rev-parse HEAD)
COMMIT_MSG=$(git -C "${PROJECT_ROOT}" log -1 --pretty=%B)
COMMIT_AUTHOR=$(git -C "${PROJECT_ROOT}" log -1 --pretty=%an)
COMMIT_DATE=$(git -C "${PROJECT_ROOT}" log -1 --pretty=%ad)

log "Latest commit: ${LATEST_COMMIT}"
log "Commit message: ${COMMIT_MSG}"
log "Commit author: ${COMMIT_AUTHOR}"
log "Commit date: ${COMMIT_DATE}"

# Run post-merge validation
log "Running post-merge validation..."
echo "========================================================"

# Set environment variable for base path
export PROMETHIOS_BASE_PATH="${PROJECT_ROOT}"

# Run the validation script
if python3 -m app.startup_validation.postmerge_validator --base-path="${PROJECT_ROOT}" ${VERBOSE}; then
  VALIDATION_STATUS=$?
  echo "========================================================"
  if [ $VALIDATION_STATUS -eq 0 ]; then
    log "✅ Post-merge validation completed successfully. All surfaces are healthy."
    echo "========================================================"
    exit 0
  elif [ $VALIDATION_STATUS -eq 1 ]; then
    log "⚠️  Post-merge validation completed with drift detected. See report for details."
    echo "========================================================"
    echo "⚠️  IMPORTANT: Surface drift detected after merge!"
    echo "⚠️  Please review the drift report and take appropriate action."
    echo "⚠️  No automatic repairs have been performed."
    echo "========================================================"
    exit 1
  else
    log "❌ Post-merge validation failed with an error."
    echo "========================================================"
    echo "❌ ERROR: Post-merge validation failed!"
    echo "❌ Please check the logs for details."
    echo "========================================================"
    exit 2
  fi
else
  log "❌ Failed to run post-merge validation script."
  echo "========================================================"
  echo "❌ ERROR: Failed to run post-merge validation script!"
  echo "❌ Please check that the script exists and is executable."
  echo "========================================================"
  exit 2
fi
