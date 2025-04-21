# Promethios API Deployment Instructions

This document provides instructions for deploying the Promethios API to Railway.

## Prerequisites

1. Install the Railway CLI:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link to the existing project:
   ```bash
   railway link
   ```

## Deployment Steps

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Test the API locally:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Verify that all routes are working correctly by accessing:
   - http://localhost:8000/health
   - http://localhost:8000/docs (to check all routes)

4. Deploy to Railway:
   ```bash
   railway up
   ```

5. After deployment, verify the API is working by accessing:
   - https://web-production-2639.up.railway.app/health
   - https://web-production-2639.up.railway.app/docs

## Deployment Configuration

The deployment configuration is defined in `railway.json`:

```json
{
  "version": 2,
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "python serve.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "healthcheckPath": "/health",
    "healthcheckTimeout": 5,
    "healthcheckInterval": 10
  }
}
```

The `serve.py` file is used to start the application:

```python
import os
import uvicorn

port = int(os.environ.get("PORT", 8000))

uvicorn.run("app.main:app", host="0.0.0.0", port=port)
```

## Troubleshooting

If you encounter any issues during deployment:

1. Check the Railway logs:
   ```bash
   railway logs
   ```

2. Verify that all required environment variables are set in the Railway dashboard.

3. Ensure that the `serve.py` file is in the root directory and properly configured.

4. If routes are not accessible, check that they are properly mounted in `app/main.py`.

## Monitoring

After deployment, monitor the API health using:

```bash
curl https://web-production-2639.up.railway.app/health
```

You can also check the system status:

```bash
curl https://web-production-2639.up.railway.app/system/status
```
