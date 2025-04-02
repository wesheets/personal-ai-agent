"""
Logging Manager for the Personal AI Agent System.
This module provides enhanced logging capabilities for API requests and responses,
with support for excluding sensitive fields and storing logs for later retrieval.
"""
import os
import json
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import Request, Response
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Sensitive fields that should be redacted in logs
SENSITIVE_FIELDS = [
    "api_key", 
    "key", 
    "password", 
    "secret", 
    "token", 
    "authorization",
    "access_token",
    "refresh_token",
    "OPENAI_API_KEY",
    "SUPABASE_KEY",
    "GITHUB_TOKEN"
]

class LogEntry(BaseModel):
    """Model for a log entry"""
    timestamp: str
    method: str
    path: str
    status_code: Optional[int] = None
    request_headers: Dict[str, str] = {}
    request_body: Optional[Any] = None
    response_headers: Dict[str, str] = {}
    response_body: Optional[Any] = None
    process_time_ms: Optional[float] = None
    error: Optional[str] = None
    stack_trace: Optional[str] = None

class LoggingManager:
    """
    Manager for API request and response logging
    """
    
    def __init__(self):
        """Initialize the LoggingManager"""
        # Set up storage directory
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Maximum number of logs to keep
        self.max_logs = 1000
        
        # In-memory cache of recent logs for quick access
        self.recent_logs = []
        self.max_recent_logs = 100
    
    async def log_request(self, request, response, process_time, status_code, error=None):
        """
        Log an API request and response
        
        Args:
            request: The FastAPI request object
            response: The FastAPI response object
            process_time: The time taken to process the request in seconds
            status_code: The HTTP status code of the response
            error: Optional exception if an error occurred
        """
        try:
            # Debug logging
            try:
                path = getattr(request.url, "path", None) or str(request.url).split(str(request.base_url))[1] if hasattr(request, 'base_url') else str(request.url)
            except (AttributeError, IndexError):
                path = str(request.url)
            
            logger.info(f"[DEBUG] log_request called for path: {path}")
            logger.info(f"[DEBUG] response is None: {response is None}")
            logger.info(f"[DEBUG] status_code provided: {status_code}")
            if response is not None:
                logger.info(f"[DEBUG] response.status_code: {getattr(response, 'status_code', 'N/A')}")
            
            # Create log entry with safe attribute access
            try:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "method": getattr(request, "method", "UNKNOWN"),
                    "url": str(request.url),
                    "status_code": status_code if status_code is not None else (getattr(response, 'status_code', 500) if response else 500),
                    "process_time": process_time,
                    "client_ip": getattr(request.client, "host", "unknown") if hasattr(request, "client") else "unknown",
                    "user_agent": getattr(request, "headers", {}).get("user-agent", "unknown"),
                }
            except Exception as e:
                logger.error(f"Error creating log entry: {str(e)}")
                # Create minimal log entry as fallback
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "method": "UNKNOWN",
                    "url": str(request.url) if hasattr(request, "url") else "unknown",
                    "status_code": status_code if status_code is not None else 500,
                    "process_time": process_time,
                }
            
            # Add error information if available
            if error:
                log_entry["error"] = str(error)
            
            # Add request body if available
            try:
                body = request.body()
                if body:
                    try:
                        body_json = json.loads(body)
                        log_entry["request_body"] = self._redact_sensitive_data(body_json)
                    except:
                        # Not JSON, store as string with limited length
                        log_entry["request_body"] = str(body)[:1000] + "..." if len(str(body)) > 1000 else str(body)
            except:
                log_entry["request_body"] = "Could not read request body"
            
            # Store log
            self.recent_logs.append(log_entry)
            if len(self.recent_logs) > self.max_recent_logs:
                self.recent_logs.pop(0)
                
            # Write to file
            log_file = os.path.join(self.logs_dir, f"api_log_{datetime.now().strftime('%Y%m%d')}.json")
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
            return log_entry
        except Exception as e:
            # Use the already imported logger instead of creating a new one
            logger.error(f"Error logging request: {str(e)}")
            return None
    
    def get_recent_logs(self, limit=50):
        """
        Get recent logs
        
        Args:
            limit: Maximum number of logs to return
        """
        # Convert dictionary logs to LogEntry objects if needed
        result_logs = []
        for log in self.recent_logs[-limit:] if limit < len(self.recent_logs) else self.recent_logs:
            if isinstance(log, dict):
                try:
                    # Ensure required fields exist
                    if 'path' not in log and 'url' in log:
                        # Extract path from URL if missing
                        url = log['url']
                        path = url.split('://')[-1].split('/', 1)[-1] if '/' in url else ''
                        log['path'] = f"/{path}" if not path.startswith('/') else path
                    elif 'path' not in log:
                        log['path'] = 'unknown'
                        
                    # Create LogEntry object
                    log_entry = LogEntry(
                        timestamp=log.get('timestamp', datetime.now().isoformat()),
                        method=log.get('method', 'UNKNOWN'),
                        path=log.get('path', 'unknown'),
                        status_code=log.get('status_code', 500),
                        request_headers=log.get('request_headers', {}),
                        request_body=log.get('request_body', None),
                        response_headers=log.get('response_headers', {}),
                        response_body=log.get('response_body', None),
                        process_time_ms=log.get('process_time', 0) * 1000 if 'process_time' in log else None,
                        error=log.get('error', None),
                        stack_trace=log.get('stack_trace', None)
                    )
                    result_logs.append(log_entry)
                except Exception as e:
                    logger.error(f"Error converting log dict to LogEntry: {str(e)}")
                    # Skip this log entry
            else:
                # Already a LogEntry object
                result_logs.append(log)
                
        return result_logs
    
    def _redact_sensitive_data(self, data: Any) -> Any:
        """
        Redact sensitive data from logs
        
        Args:
            data: Data to redact
            
        Returns:
            Redacted data
        """
        if isinstance(data, dict):
            redacted_data = {}
            for key, value in data.items():
                # Check if this key should be redacted
                if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
                    redacted_data[key] = "***REDACTED***"
                else:
                    # Recursively redact nested dictionaries
                    redacted_data[key] = self._redact_sensitive_data(value)
            return redacted_data
        elif isinstance(data, list):
            # Recursively redact items in lists
            return [self._redact_sensitive_data(item) for item in data]
        else:
            # Return primitive values as is
            return data
    
    async def log_request_response(self, request: Request, response: Response, process_time: float, error: Optional[Exception] = None) -> str:
        """
        Log a request and response
        
        Args:
            request: The FastAPI request
            response: The FastAPI response
            process_time: Time taken to process the request in seconds
            error: Optional exception if an error occurred
            
        Returns:
            ID of the log entry
        """
        # Generate timestamp
        timestamp = datetime.now().isoformat()
        
        # Debug logging
        logger.info(f"[DEBUG] log_request_response called for URL: {request.url}")
        logger.info(f"[DEBUG] response is None: {response is None}")
        
        # Extract request details with safe attribute access
        try:
            method = getattr(request, "method", "UNKNOWN")
            
            # Try multiple methods to get the path
            try:
                path = getattr(request.url, "path", None)
                if not path:
                    path = str(request.url).split(str(request.base_url))[1]
            except (AttributeError, IndexError):
                # Fallback if we can't extract path from base_url
                path = str(request.url)
                logger.info(f"[DEBUG] Using fallback path: {path}")
            
            request_headers = dict(getattr(request, "headers", {}))
        except Exception as e:
            logger.error(f"Error extracting request details: {str(e)}")
            method = "UNKNOWN"
            path = "unknown"
            request_headers = {}
        
        # Try to get request body
        request_body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                # Reset request body position
                await request.body()
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        # Try to parse as JSON
                        request_body = json.loads(body_bytes)
                    except:
                        # If not JSON, store as string
                        request_body = body_bytes.decode()
            except Exception as e:
                logger.warning(f"Could not read request body: {str(e)}")
        
        # Extract response details with safe attribute access
        try:
            status_code = getattr(response, 'status_code', 500) if response else 500
            response_headers = dict(getattr(response, 'headers', {})) if response else {}
        except Exception as e:
            logger.error(f"Error extracting response details: {str(e)}")
            status_code = 500
            response_headers = {}
        
        # Try to get response body
        response_body = None
        
        # Debug logging
        logger.info(f"[DEBUG] Extracted status_code: {status_code}")
        
        # Process error if any
        try:
            error_str = None
            stack_trace = None
            if error:
                error_str = str(error)
                stack_trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        except Exception as e:
            logger.error(f"Error processing exception details: {str(e)}")
            error_str = "Error processing exception details"
            stack_trace = None
        
        # Create log entry with additional error handling
        try:
            log_entry = LogEntry(
                timestamp=timestamp,
                method=method,
                path=path,
                status_code=status_code,
                request_headers=self._redact_sensitive_data(request_headers),
                request_body=self._redact_sensitive_data(request_body),
                response_headers=self._redact_sensitive_data(response_headers),
                response_body=self._redact_sensitive_data(response_body),
                process_time_ms=process_time * 1000,  # Convert to milliseconds
                error=error_str,
                stack_trace=stack_trace
            )
            logger.info(f"[DEBUG] Successfully created LogEntry object")
        except Exception as e:
            logger.error(f"Error creating LogEntry: {str(e)}")
            # Create a minimal valid log entry as fallback
            log_entry = LogEntry(
                timestamp=timestamp,
                method=method,
                path=path if path else "unknown",
                status_code=status_code
            )
        
        # Generate log ID with error handling
        try:
            safe_path = path.replace('/', '_') if path else "unknown_path"
            log_id = f"{int(time.time())}_{method}_{safe_path}"
            logger.info(f"[DEBUG] Generated log_id: {log_id}")
        except Exception as e:
            logger.error(f"Error generating log_id: {str(e)}")
            log_id = f"{int(time.time())}_{method}_unknown_path"
        
        # Save to file with error handling
        try:
            log_path = os.path.join(self.logs_dir, f"{log_id}.json")
            with open(log_path, "w") as f:
                f.write(log_entry.model_dump_json(indent=2))
        except Exception as e:
            logger.error(f"Error saving log to file: {str(e)}")
            # Continue execution even if file saving fails
        
        # Add to recent logs with error handling
        try:
            self.recent_logs.append(log_entry)
            if len(self.recent_logs) > self.max_recent_logs:
                self.recent_logs.pop(0)  # Remove oldest log
        except Exception as e:
            logger.error(f"Error adding log to recent_logs: {str(e)}")
        
        # Clean up old logs if needed
        try:
            self._cleanup_old_logs()
        except Exception as e:
            logger.error(f"Error during log cleanup: {str(e)}")
        
        return log_id
    
    def _cleanup_old_logs(self):
        """Clean up old logs if there are too many"""
        try:
            log_files = [os.path.join(self.logs_dir, f) for f in os.listdir(self.logs_dir) if f.endswith(".json")]
            log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Delete oldest logs if we have too many
            if len(log_files) > self.max_logs:
                for old_log in log_files[self.max_logs:]:
                    try:
                        os.remove(old_log)
                    except Exception as e:
                        logger.warning(f"Could not delete old log {old_log}: {str(e)}")
        except Exception as e:
            logger.warning(f"Error during log cleanup: {str(e)}")
    
    def get_latest_logs(self, limit: int = 20) -> List[LogEntry]:
        """
        Get the latest logs
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        try:
            # Use in-memory cache if available
            if self.recent_logs:
                return sorted(self.recent_logs, key=lambda x: x.timestamp, reverse=True)[:limit]
            
            # Otherwise read from disk
            try:
                log_files = [os.path.join(self.logs_dir, f) for f in os.listdir(self.logs_dir) if f.endswith(".json")]
                log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                
                logs = []
                for log_file in log_files[:limit]:
                    try:
                        with open(log_file, "r") as f:
                            log_data = json.load(f)
                            logs.append(LogEntry(**log_data))
                    except Exception as e:
                        logger.warning(f"Could not read log file {log_file}: {str(e)}")
                
                return logs
            except Exception as e:
                logger.error(f"Error getting latest logs from disk: {str(e)}")
                return []
        except Exception as e:
            logger.error(f"Error in get_latest_logs: {str(e)}")
            return []

# Singleton instance
_logging_manager = None

def get_logging_manager() -> LoggingManager:
    """
    Get the singleton LoggingManager instance
    """
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager
