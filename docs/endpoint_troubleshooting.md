# API Endpoint Troubleshooting Guide

## Overview

This document provides guidance on troubleshooting and fixing API endpoint issues in the Personal AI Agent backend. It was created after resolving 404 errors for critical endpoints in April 2025.

## Common Issues and Solutions

### 1. 404 Errors for API Endpoints

When endpoints return 404 errors despite being defined in route files, check the following:

#### Route File Location Conflicts

The system has multiple locations for route files:
- `/routes/` - Original route location
- `/app/routes/` - Alternative route location
- `/app/api/` - Additional route location for API modules

**Problem**: Having duplicate route files in different locations causes confusion for the dynamic route loader.

**Solution**: 
- Ensure route files exist in only one location, preferably `/app/routes/`
- If duplicates exist, make sure they define the same endpoints consistently

#### Path Definition Issues

**Problem**: Routes defined without the `/api` prefix but accessed with it.

**Solution**:
- Define routes with the correct path (e.g., `/memory/write` not `/api/memory/write`)
- Ensure the router is included with the correct prefix in `main.py`:
  ```python
  app.include_router(memory_routes.router, prefix="/api")
  ```

#### Missing Schema Validation

**Problem**: Endpoints defined without proper schema validation.

**Solution**:
- Create schema definitions in `app/schemas/` directory
- Import and use these schemas in route definitions:
  ```python
  from app.schemas.loop_schema import LoopResponseRequest
  
  @router.post("/loop/respond")
  async def loop_respond_endpoint(request: LoopResponseRequest):
      # Implementation
  ```

#### Missing Dependencies

**Problem**: Routes depend on modules that don't exist or have import errors.

**Solution**:
- Create missing modules or mock implementations
- Fix import paths to point to the correct locations
- Use try/except blocks for imports that might fail in different environments

### 2. Dynamic Route Loader Issues

The system uses a dynamic route loader to import routes from multiple locations.

**Problem**: The loader might not correctly handle routes in different locations.

**Solution**:
- Ensure the dynamic route loader checks all possible locations
- Add proper error handling for import failures
- Create stub routers for missing routes to prevent 404 errors

## Testing Endpoints

Use the endpoint testing tool to verify all endpoints are working:

```bash
python tools/test_endpoints.py --verbose
```

This tool will test all 32 endpoints and provide a detailed report of successes and failures.

## Recent Fixes (April 2025)

### Fixed Memory Routes

1. Created proper schema definitions
2. Added memory writer module in `app/modules/memory_writer.py`
3. Updated memory module in `app/api/modules/memory.py`
4. Created memory routes in `app/routes/memory_routes.py`
5. Ensured routes are defined with proper paths (`/memory/write` and `/memory/read`)

### Fixed Loop Routes

1. Updated loop routes in `app/routes/loop_routes.py`
2. Ensured the `/loop/respond` endpoint is properly defined
3. Fixed dependencies and imports for HAL agent code generation

## Best Practices

1. **Consistent Route Location**: Place all route files in the same directory structure
2. **Schema Validation**: Always use Pydantic models for request validation
3. **Proper Error Handling**: Use try/except blocks for imports and operations that might fail
4. **Testing**: Regularly run the endpoint testing tool to verify all endpoints are working
5. **Documentation**: Keep this document updated with new issues and solutions

## Troubleshooting Checklist

When an endpoint returns 404:

1. Verify the route file exists in one of the standard locations
2. Check that the route is defined with the correct path
3. Ensure the router is included with the correct prefix
4. Verify all dependencies and imports are working
5. Check for schema validation issues
6. Run the endpoint testing tool to identify patterns in failures
7. Review the dynamic route loader implementation in `main.py`

By following this guide, you should be able to resolve most endpoint-related issues in the Personal AI Agent backend.
