# Deployment Instructions for Internal Chain Call Fix

## Overview

This document provides instructions for deploying the fix for the internal chain call in the `/api/project/start` route. The implemented fix changes how the backend calls the `/api/orchestrator/chain` endpoint to use an internal FastAPI call rather than an external HTTP request, which was failing in the Railway deployment container.

## Deployment Steps

### 1. Create and Merge Pull Request

```bash
# The branch has already been pushed to GitHub
# Create a pull request from the feature/fix-chain-internal-call branch to the main branch
```

Visit: https://github.com/wesheets/personal-ai-agent/pull/new/feature/fix-chain-internal-call

After code review, merge the pull request into the main branch.

### 2. Deploy to Railway

Once the pull request is merged, deploy the updated code to Railway:

1. Log in to your Railway dashboard
2. Select the Promethios project
3. Navigate to the Deployments tab
4. Click "Deploy" to deploy the latest code from the main branch
5. Wait for the deployment to complete (usually takes 2-3 minutes)

### 3. Verify the Deployment

After deployment, verify that the `/api/project/start` endpoint is working correctly:

1. Check the Railway deployment logs for successful chain execution messages:
   ```
   ✅ Chain execution request succeeded
   ✅ Agent chain executed: HAL → ASH → NOVA
   ```

2. Test the endpoint using Postman or curl:
   ```bash
   curl -X POST https://your-railway-app.railway.app/api/project/start \
     -H "Content-Type: application/json" \
     -d '{"goal": "Write a Python function that reverses a string"}'
   ```

   Expected response:
   ```json
   {
     "project_id": "...",
     "chain_id": "...",
     "agents": [
       { "agent": "hal", "status": "complete", ... },
       { "agent": "ash", "status": "complete", ... },
       { "agent": "nova", "status": "complete", ... }
     ]
   }
   ```

3. Test via the Playground UI to ensure the full multi-agent cognition is working

### 4. Monitor for Errors

After deployment, monitor the Railway logs for any errors related to the chain execution. The improved error handling will provide more detailed information if issues occur.

## Implemented Fix

The following fixes have been implemented to ensure the internal chain call works correctly in the Railway deployment:

1. **Internal FastAPI Call**
   - Changed from using an external HTTP request to an internal FastAPI call
   - Implemented using `httpx.AsyncClient(app=app, base_url="http://testserver")`
   - Modified the URL from `http://localhost:3000/api/orchestrator/chain` to `/api/orchestrator/chain`

2. **Improved Error Handling**
   - Added specific handling for different types of exceptions:
     - `httpx.RequestError` for connection issues
     - `httpx.TimeoutException` for timeout errors
     - General `Exception` for unexpected errors
   - Each error type has appropriate status codes and detailed error messages
   - All errors include the project_id for tracking

3. **Test Script**
   - Added a test script to verify the internal chain call works correctly
   - The script can be used for local testing before deployment

## Troubleshooting

If you encounter issues after deployment, check the following:

1. **Verify the App Import**
   - Ensure the `app` import from `app.main` is working correctly
   - Check for circular import issues if they arise

2. **Check Railway Logs**
   - Look for detailed error messages in the Railway logs
   - The improved error handling will provide more information about what's going wrong

3. **Test with Simplified Goal**
   - If the endpoint is timing out, try testing with a simpler goal that requires less processing

4. **Restart the Deployment**
   - Sometimes a simple restart can resolve issues
   - In the Railway dashboard, select the Promethios project and click "Restart"

## Contact

If you continue to experience issues after following these steps, please contact the development team for further assistance.
