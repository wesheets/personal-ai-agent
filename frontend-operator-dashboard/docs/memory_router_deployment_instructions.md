# Memory Router Fix Deployment Instructions

## Overview

This document provides step-by-step instructions for deploying the memory router fix to resolve the 404 Not Found errors with the `/memory/read` endpoint (PROM-247).

## Deployment Steps

### 1. Prepare for Deployment

Before deploying the changes, ensure you have:

- Access to the production server
- Ability to restart the FastAPI application
- Backup of the current code (recommended)

### 2. Update Code Files

Three files need to be updated or added:

#### a. Update `app/api/modules/memory.py`

Ensure the read endpoint uses the `/memory/` prefix:

```python
@router.get("/memory/read")
async def read_memory(...):
    # Function implementation
```

#### b. Update `app/main.py`

Change the memory router registration:

```python
# Change this:
app.include_router(memory_router, prefix="/api/modules/memory")

# To this:
app.include_router(memory_router, prefix="/api")
```

Also add the route logging code:

```python
# Import and use the enhanced route logger for detailed diagnostics
try:
    from app.utils.route_logger import log_registered_routes
    print("📋 Using enhanced route logging for deployment diagnostics")
except ImportError:
    print("⚠️ Enhanced route logger not available, using basic logging")
    log_registered_routes = lambda app: print("⚠️ Enhanced route logging not available")

# Add route registration logging at the end of startup
@app.on_event("startup")
async def log_routes_on_startup():
    """Log all registered routes after startup for debugging."""
    try:
        log_registered_routes(app)
    except Exception as e:
        print(f"⚠️ Error logging routes: {str(e)}")
        logger.error(f"⚠️ Error logging routes: {str(e)}")
```

#### c. Add `app/utils/route_logger.py`

Create this new file with the enhanced route logging utility.

### 3. Deploy the Changes

1. **Stop the Application**:

   ```bash
   # If using systemd
   sudo systemctl stop personal-ai-agent

   # If using supervisor
   sudo supervisorctl stop personal-ai-agent
   ```

2. **Update the Code**:

   ```bash
   # Pull the latest changes if using git
   cd /path/to/personal-ai-agent
   git pull

   # Or manually update the files
   scp app/api/modules/memory.py user@server:/path/to/personal-ai-agent/app/api/modules/
   scp app/main.py user@server:/path/to/personal-ai-agent/app/
   scp app/utils/route_logger.py user@server:/path/to/personal-ai-agent/app/utils/
   ```

3. **Create utils directory if it doesn't exist**:

   ```bash
   mkdir -p /path/to/personal-ai-agent/app/utils
   touch /path/to/personal-ai-agent/app/utils/__init__.py
   ```

4. **Restart the Application**:

   ```bash
   # If using systemd
   sudo systemctl start personal-ai-agent

   # If using supervisor
   sudo supervisorctl start personal-ai-agent
   ```

### 4. Verify the Deployment

1. **Check Application Logs**:

   ```bash
   # If using systemd
   sudo journalctl -u personal-ai-agent -n 100

   # If using supervisor
   sudo supervisorctl tail -f personal-ai-agent
   ```

2. **Look for Route Registration Diagnostics**:

   - Find the "ROUTE REGISTRATION DIAGNOSTIC" section in the logs
   - Verify memory routes are listed under "Memory-specific Routes"

3. **Test the Endpoints**:

   ```bash
   # Test the read endpoint
   curl -X GET https://your-api-domain.com/api/memory/read?limit=5

   # Test the write endpoint
   curl -X POST https://your-api-domain.com/api/memory/write -H "Content-Type: application/json" -d '{"agent_id":"test","memory_type":"test","content":"Test memory"}'
   ```

### 5. Update Client Code (If Necessary)

If any client code is hardcoded to use the old paths, update it to use the new paths:

- Old: `/api/modules/memory/read`
- New: `/api/memory/read`

### 6. Rollback Plan (If Needed)

If issues occur after deployment:

1. **Restore Previous Code**:

   ```bash
   # If using git
   cd /path/to/personal-ai-agent
   git checkout <previous-commit-hash>

   # Or manually restore from backup
   ```

2. **Restart the Application**:

   ```bash
   # If using systemd
   sudo systemctl restart personal-ai-agent

   # If using supervisor
   sudo supervisorctl restart personal-ai-agent
   ```

## Troubleshooting

If the endpoints still return 404 after deployment:

1. **Verify URL Paths**: Ensure you're using the new paths (`/api/memory/read` not `/api/modules/memory/read`)

2. **Check for Caching**: Some environments may have caching at various levels:

   ```bash
   # Clear application cache (if applicable)
   rm -rf /path/to/cache

   # Restart reverse proxy (if using nginx)
   sudo systemctl restart nginx
   ```

3. **Force Full Restart**: Sometimes a full restart of all components is needed:

   ```bash
   # Restart the entire application stack
   sudo systemctl restart personal-ai-agent nginx
   ```

4. **Check File Permissions**: Ensure the new route_logger.py file is readable by the application user:
   ```bash
   sudo chown -R app-user:app-group /path/to/personal-ai-agent/app/utils
   sudo chmod 644 /path/to/personal-ai-agent/app/utils/route_logger.py
   ```

## Contact

If you encounter any issues during deployment, please contact the development team with:

- Application logs showing the route registration diagnostics
- The exact error messages you're seeing
- Details of your deployment environment
