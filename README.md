# Server Port Configuration

# trigger redeploy

The backend server is configured to run on port 8001.

## Accessing the Server

- API Endpoints: http://localhost:8001/
- Swagger Documentation: http://localhost:8001/docs
- OpenAPI Schema: http://localhost:8001/openapi.json

## Memory Module Endpoints

The memory module endpoints are available at:

- `/api/modules/memory/summarize` - Summarize agent memories
- Other memory endpoints as documented in the API

## Starting the Server

To start the server, use the following command:

```bash
cd personal-ai-agent
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## Troubleshooting Connection Issues

If you're unable to connect to the server:

1. Verify the server is running with `ps aux | grep uvicorn`
2. Check if the port is accessible with `curl http://localhost:8001/health`
3. Ensure no firewall is blocking the connection
4. Try accessing via 127.0.0.1 instead of localhost if DNS resolution is an issue
