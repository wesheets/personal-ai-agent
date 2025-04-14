# Deployment Instructions for Circular Import Fix

## Overview

This document provides instructions for deploying the fix for the circular import issue in the `/api/project/start` endpoint. The implemented fix decouples the internal HTTP call logic from the global app reference, resolving the `ImportError: cannot import name 'app' from partially initialized module 'app.main'` error.

## Deployment Steps

### 1. Create and Merge Pull Request

```bash
# The branch has already been pushed to GitHub
# Create a pull request from the feature/fix-circular-import-start-route branch to the main branch
```

Visit: https://github.com/wesheets/personal-ai-agent/pull/new/feature/fix-circular-import-start-route

After code review, merge the pull request into the main branch.

### 2. Deploy to Railway

Once the pull request is merged, deploy the updated code to Railway:

1. Log in to your Railway dashboard
2. Select the Promethios project
3. Navigate to the Deployments tab
4. Click "Deploy" to deploy the latest code from the main branch
5. Wait for the deployment to complete (usually takes 2-3 minutes)

### 3. Verify the Deployment

After deployment, verify that the circular import issue has been resolved:

1. Check the Railway deployment logs for successful startup without import errors
2. Look for these specific log messages:
   ```
   ✅ Successfully registered /api/project/start route
   ✅ Chain triggered internally via /orchestrator/chain
   ```

3. Test the endpoint using Postman or curl:
   ```bash
   curl -X POST https://your-railway-app.railway.app/api/project/start \
     -H "Content-Type: application/json" \
     -d '{"goal": "Write a Python function that reverses a string"}'
   ```

4. Test via the Playground UI to ensure the full multi-agent cognition is working

### 4. Monitor for Errors

After deployment, monitor the Railway logs for any errors related to the chain execution or import issues. The improved error handling will provide more detailed information if issues occur.

## Implemented Fix

The following fixes have been implemented to resolve the circular import issue:

1. **Created Chain Runner Helper**
   - Added a new utility file `app/utils/chain_runner.py`
   - Implemented a `run_internal_chain` function that takes the app reference as a parameter
   - This decouples the internal HTTP call logic from the global app reference

2. **Updated Project Start Endpoint**
   - Removed the direct import of app from main.py in start.py
   - Updated the code to use the chain runner helper instead
   - Now passing `request.app` as the app reference to the helper function
   - Simplified error handling by centralizing it in the helper function

3. **Verified Router Registration**
   - Confirmed that the router registration in main.py is properly implemented
   - The registration includes error handling and debug endpoints

## Troubleshooting

If you encounter issues after deployment, check the following:

1. **Check Railway Logs**
   - Look for import errors during startup
   - Verify that the `/api/project/start` route is registered successfully

2. **Use Debug Endpoints**
   - Access `/api/debug/project-start-registered` to verify route registration
   - If there are issues, check `/api/debug/project-start-error` for details

3. **Test with Simple Goal**
   - If the endpoint is working but chain execution fails, try with a simpler goal

4. **Restart the Deployment**
   - Sometimes a simple restart can resolve issues
   - In the Railway dashboard, select the Promethios project and click "Restart"

## Contact

If you continue to experience issues after following these steps, please contact the development team for further assistance.
