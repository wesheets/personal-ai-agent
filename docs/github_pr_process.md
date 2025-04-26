# GitHub PR Process for Personal AI Agent System

## Overview

This document outlines the recommended PR process for making changes to the Personal AI Agent system. Following this process will ensure better control over deployments and provide more visibility into changes before they're merged to the main branch.

## PR Process

### 1. Create a Feature Branch

Always create a feature branch for your changes:

```bash
# Start from an up-to-date main branch
git checkout main
git pull origin main

# Create a feature branch with a descriptive name
git checkout -b feature/descriptive-name
```

Branch naming conventions:
- `feature/` - For new features or enhancements
- `fix/` - For bug fixes
- `refactor/` - For code refactoring
- `docs/` - For documentation updates

### 2. Make and Test Changes

Implement your changes and test them thoroughly:

```bash
# Make your changes
...

# Run tests to verify your changes
python tools/batch1_postman_sweep_updated.py
python tools/batch2_postman_sweep.py
```

### 3. Commit Changes with Descriptive Messages

Use descriptive commit messages with emoji prefixes:

```bash
git add .
git commit -m "🔧 Fix: Resolve memory endpoint 500 errors"
```

Commit message prefixes:
- 🔧 Fix: For bug fixes
- ✨ Feature: For new features
- 📝 Docs: For documentation
- ♻️ Refactor: For code refactoring
- 🧪 Test: For adding or updating tests

### 4. Push Branch and Create PR

Push your branch to GitHub and create a PR:

```bash
git push -u origin feature/descriptive-name
```

Then go to GitHub and create a PR with:
- Clear title describing the change
- Detailed description of what was changed and why
- Any testing that was performed
- Any related issues or dependencies

### 5. PR Review and Approval

- Wait for at least one review before merging
- Address any feedback or comments
- Make sure all tests pass
- Get approval from a team member

### 6. Merge PR

Once approved, merge the PR using the GitHub interface:
- Use "Squash and merge" for cleaner history
- Make sure the squash commit message is descriptive

### 7. Verify Deployment

After merging:
- Wait for the deployment to complete
- Run verification tests to ensure everything works as expected
- Monitor logs for any errors

## Memory Tags

For significant changes, create a memory tag in the appropriate format:

```json
{
  "memory_tag": "feature_name_<timestamp>",
  "timestamp": "YYYY-MM-DDThh:mm:ssZ",
  "event_type": "feature_implementation",
  "status": "success",
  "summary": "Brief description of the change",
  "details": {
    "key_changes": [
      "Description of change 1",
      "Description of change 2"
    ]
  }
}
```

Save this to `/app/logs/memory_events/feature_name_<timestamp>.json`

## ACI Updates

Update the Agent Cognition Index (ACI) for any changes that affect agent behavior or endpoints:

1. Update the `passes_full_test` flag
2. Add or update `responsible_routes`
3. Update `logic_notes` with relevant information
4. Update the `checklist` items
5. Set `last_tested_by` to your name
6. Update `last_modified` timestamp

## Benefits of This Process

- Better visibility into changes
- Controlled deployments
- Code review and quality assurance
- Clear history of changes
- Easier rollback if needed
- Better coordination among team members
