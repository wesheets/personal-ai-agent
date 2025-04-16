# CORS Configuration Documentation

## Overview

This document outlines the CORS (Cross-Origin Resource Sharing) configuration required for the Manus Personal AI Agent System to function properly in both development and production environments.

## Backend CORS Configuration

The backend API must explicitly allow requests from the frontend domain. The following configuration should be implemented on the backend:

```python
origins = [
  "http://localhost:5173",  # For local development
  "https://your-frontend.up.railway.app"  # Replace with actual Railway domain after deployment
]
```

## Frontend Configuration

The frontend has been configured to use environment variables for all API calls to ensure CORS-safe operation:

### Development Environment (.env)

```
VITE_API_BASE_URL=http://localhost:8000
```

### Production Environment (.env.production)

```
VITE_API_BASE_URL=https://personal-ai-agent-backend-production.up.railway.app
```

## API Service Implementation

All API calls in the frontend use the `VITE_API_BASE_URL` environment variable:

```javascript
// From ApiService.js
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});
```

## Deployment Checklist for CORS

1. Build the frontend application
2. Deploy to Railway as a static site
3. Note the assigned domain (e.g., https://your-frontend.up.railway.app)
4. Update the backend CORS configuration to include this domain
5. Verify CORS is working by testing API calls from the deployed frontend

## Common CORS Issues and Solutions

1. **Issue**: "No 'Access-Control-Allow-Origin' header is present"
   **Solution**: Ensure the backend CORS configuration includes the frontend domain

2. **Issue**: Preflight requests failing
   **Solution**: Ensure the backend handles OPTIONS requests properly

3. **Issue**: Credentials not being sent
   **Solution**: Set `withCredentials: true` in axios configuration if needed

## Important Notes

- Do NOT use proxy hacks in vite.config.js as specified in the requirements
- No development proxies or "proxy": "..." tricks should be used
- Always use environment variables for API URLs, never hardcode them
- After deployment, inform the backend team of the exact frontend domain for CORS whitelist
