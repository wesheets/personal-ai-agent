# Deployment Instructions for Runtime Route Inspector

## Overview

This document provides instructions for deploying the runtime route inspector that will help confirm whether the `/api/project/start` route is being properly registered inside the FastAPI app. This debug tool will help diagnose the 404 error we're experiencing when POSTing to this endpoint.

## Deployment Steps

### 1. Create and Merge Pull Request

```bash
# The branch has already been pushed to GitHub
# Create a pull request from the feature/route-debug-logger branch to the main branch
```

Visit: https://github.com/wesheets/personal-ai-agent/pull/new/feature/route-debug-logger

After code review, merge the pull request into the main branch.

### 2. Deploy to Railway

Once the pull request is merged, deploy the updated code to Railway:

1. Log in to your Railway dashboard
2. Select the Promethios project
3. Navigate to the Deployments tab
4. Click "Deploy" to deploy the latest code from the main branch
5. Wait for the deployment to complete (usually takes 2-3 minutes)

### 3. Check Railway Logs

After deployment, check the Railway logs for the route debug output:

1. In the Railway dashboard, select the Promethios project
2. Navigate to the Logs tab
3. Look for the following output:

```
🔍 [ROUTE DEBUG] Registered routes:
📍 /api/project/start -> start_project
...
✅ [ROUTE DEBUG] Route listing complete
```

### 4. Interpret the Results

Based on the logs, you can determine the cause of the 404 error:

- If `/api/project/start` is **present** in the logs:
  - The route is properly registered
  - The 404 error is likely caused by an incorrect method (e.g., using GET instead of POST), prefix, or path mismatch
  - Check how the endpoint is being called from the client side

- If `/api/project/start` is **missing** from the logs:
  - The import or router registration failed silently
  - Check for import errors or issues with the router registration in main.py
  - Verify that the start.py file is in the correct location and contains the proper route definition

### 5. Next Steps

Based on the findings, take appropriate action:

- If the route is properly registered, focus on how it's being called
- If the route is missing, investigate the import and registration process

## Implemented Fix

The following fix has been implemented to help diagnose route registration issues:

1. **Runtime Route Inspector**
   - Added a startup hook in main.py that logs all registered routes when the app boots
   - The hook uses a clear, concise format that makes it easy to identify registered routes
   - This will help determine if the `/api/project/start` route is properly registered

2. **Preserved Existing Functionality**
   - Kept the existing route logging functionality to maintain backward compatibility
   - The new debug logger provides additional, more focused information

## Future Benefits

This debug tool will help validate any route in future builds and prevent silent 404s from causing misdiagnosis. It can be used to:

1. Verify that new routes are properly registered
2. Identify naming conflicts or duplicate routes
3. Ensure that all expected routes are available at runtime

## Contact

If you continue to experience issues after following these steps, please contact the development team for further assistance.
