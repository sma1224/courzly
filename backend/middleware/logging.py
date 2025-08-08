from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid
import json
from datetime import datetime

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Extract request info
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Log request
        request_log = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "headers": dict(request.headers),
            "type": "request"
        }
        
        # Remove sensitive headers
        request_log["headers"] = self.sanitize_headers(request_log["headers"])
        
        logger.info(f"Request started: {json.dumps(request_log)}")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            response_log = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "response_size": response.headers.get("content-length", "unknown"),
                "type": "response"
            }
            
            # Determine log level based on status code
            if response.status_code >= 500:
                logger.error(f"Request failed: {json.dumps(response_log)}")
            elif response.status_code >= 400:
                logger.warning(f"Request error: {json.dumps(response_log)}")
            else:
                logger.info(f"Request completed: {json.dumps(response_log)}")
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            error_log = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "error_type": type(e).__name__,
                "duration_ms": round(duration * 1000, 2),
                "type": "error"
            }
            
            logger.error(f"Request exception: {json.dumps(error_log)}")
            raise
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers (load balancer/proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def sanitize_headers(self, headers: dict) -> dict:
        """Remove sensitive information from headers"""
        sensitive_headers = {
            "authorization",
            "cookie",
            "x-api-key",
            "x-auth-token"
        }
        
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized

class WorkflowLogger:
    """Specialized logger for workflow operations"""
    
    def __init__(self):
        self.logger = logging.getLogger("workflow")
    
    def log_workflow_start(self, workflow_id: str, workflow_type: str, user_id: str):
        """Log workflow start"""
        log_data = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "workflow_started"
        }
        self.logger.info(json.dumps(log_data))
    
    def log_workflow_checkpoint(self, workflow_id: str, stage: str, checkpoint_id: str):
        """Log workflow checkpoint"""
        log_data = {
            "workflow_id": workflow_id,
            "stage": stage,
            "checkpoint_id": checkpoint_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "checkpoint_reached"
        }
        self.logger.info(json.dumps(log_data))
    
    def log_workflow_approval(self, workflow_id: str, checkpoint_id: str, approver_id: str, status: str):
        """Log workflow approval"""
        log_data = {
            "workflow_id": workflow_id,
            "checkpoint_id": checkpoint_id,
            "approver_id": approver_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "approval_decision"
        }
        self.logger.info(json.dumps(log_data))
    
    def log_workflow_error(self, workflow_id: str, error: str, stage: str = None):
        """Log workflow error"""
        log_data = {
            "workflow_id": workflow_id,
            "error": error,
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "workflow_error"
        }
        self.logger.error(json.dumps(log_data))
    
    def log_workflow_completion(self, workflow_id: str, duration_seconds: float):
        """Log workflow completion"""
        log_data = {
            "workflow_id": workflow_id,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.utcnow().isoformat(),
            "event": "workflow_completed"
        }
        self.logger.info(json.dumps(log_data))

# Global workflow logger instance
workflow_logger = WorkflowLogger()