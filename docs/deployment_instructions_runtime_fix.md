# Deployment Instructions for Fixing 404 Error on `/api/project/start` Endpoint

## Overview

This document provides instructions for deploying the fix for the 404 error on the `/api/project/start` endpoint. Our investigation revealed that while the router registration code exists in the codebase, there might be runtime issues preventing the route from being properly registered. The implemented fixes add robust error handling, detailed logging, and debug endpoints to ensure the route is properly registered at runtime.

## Deployment Steps

### 1. Create and Merge Pull Request

```bash
# The branch has already been pushed to GitHub
# Create a pull request from the feature/fix-project-start-route-runtime branch to the main branch
```

Visit: https://github.com/wesheets/personal-ai-agent/pull/new/feature/fix-project-start-route-runtime

After code review, merge the pull request into the main branch.

### 2. Deploy to Railway

Once the pull request is merged, deploy the updated code to Railway:

1. Log in to your Railway dashboard
2. Select the Promethios project
3. Navigate to the Deployments tab
4. Click "Deploy" to deploy the latest code from the main branch
5. Wait for the deployment to complete (usually takes 2-3 minutes)

### 3. Verify the Deployment

After deployment, verify that the endpoint is accessible using the debug endpoints:

1. Check the debug endpoint to verify router registration:

   ```bash
   curl https://your-railway-app.railway.app/api/debug/project-start-registered
   ```

   Expected response:

   ```json
   {
     "status": "ok",
     "project_start_routes": [
       {
         "path": "/api/project/start",
         "methods": ["POST"]
       }
     ],
     "registered": true,
     "timestamp": "2025-04-14T22:44:00.000000"
   }
   ```

2. Test the actual endpoint:

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
     "agents": [...]
   }
   ```

### 4. Check Railway Logs

If the endpoint is still not accessible, check the Railway logs for any errors:

1. Go to the Railway dashboard
2. Select the Promethios project
3. Navigate to the Logs tab
4. Look for logs related to the project start router:
   - `🔄 Importing project start router for Phase 12.0 (Agent Playground)`
   - `✅ Successfully imported project start router`
   - `📡 Including Project Start router from /app/api/project/start.py`
   - `✅ Successfully registered /api/project/start route`

If you see any error messages, they will provide clues about what's going wrong.

## Implemented Fixes

The following fixes have been implemented to ensure the route is properly registered:

1. **Robust Error Handling for Router Import**

   - Added try-except block around the import of the project start router
   - Added detailed logging for import errors
   - Created a placeholder router to prevent app startup failure if import fails

2. **Robust Error Handling for Router Registration**

   - Added try-except block around the router registration code
   - Added detailed logging for registration errors
   - Created a debug endpoint to verify router registration status

3. **Debug Endpoints**

   - `/api/debug/project-start-registered`: Returns information about the registered routes
   - `/api/debug/project-start-error`: Returns error information if registration fails

4. **Test Script**
   - Added a comprehensive test script to verify router registration
   - The script can be run locally to test the fix before deployment

## Troubleshooting

If the endpoint is still returning a 404 error after deployment, try the following:

1. **Check if the Debug Endpoints are Accessible**

   - If the debug endpoints are accessible but the main endpoint is not, there might be an issue with the route declaration in start.py
   - If the debug endpoints are not accessible, there might be a more fundamental issue with the application startup

2. **Restart the Application**

   - In the Railway dashboard, select the Promethios project
   - Navigate to the Settings tab
   - Click "Restart" to restart the application

3. **Check for Conflicting Routes**

   - The debug endpoint will show all routes matching `/api/project/start`
   - If there are multiple routes with the same path, there might be a conflict

4. **Verify HTTP Method**
   - Ensure you're using the correct HTTP method (POST) when accessing the endpoint
   - The route is defined with `@router.post("/start")` in start.py

## Contact

If you continue to experience issues after following these steps, please contact the development team for further assistance.
