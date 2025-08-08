from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge
import time
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections',
    ['workflow_id']
)

WORKFLOW_OPERATIONS = Counter(
    'workflow_operations_total',
    'Total workflow operations',
    ['operation', 'status']
)

DATABASE_OPERATIONS = Counter(
    'database_operations_total',
    'Total database operations',
    ['operation', 'table']
)

CACHE_OPERATIONS = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract endpoint info
        method = request.method
        path = request.url.path
        
        # Normalize path for metrics (remove IDs)
        normalized_path = self.normalize_path(path)
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            status_code = 500
            response = Response("Internal Server Error", status_code=500)
        
        # Record metrics
        duration = time.time() - start_time
        
        REQUEST_COUNT.labels(
            method=method,
            endpoint=normalized_path,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=normalized_path
        ).observe(duration)
        
        # Add response headers
        response.headers["X-Process-Time"] = str(duration)
        
        return response
    
    def normalize_path(self, path: str) -> str:
        """Normalize path by replacing IDs with placeholders"""
        import re
        
        # Replace UUIDs with {id}
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        
        # Replace other numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        return path

def record_workflow_operation(operation: str, status: str):
    """Record workflow operation metric"""
    WORKFLOW_OPERATIONS.labels(operation=operation, status=status).inc()

def record_database_operation(operation: str, table: str):
    """Record database operation metric"""
    DATABASE_OPERATIONS.labels(operation=operation, table=table).inc()

def record_cache_operation(operation: str, result: str):
    """Record cache operation metric"""
    CACHE_OPERATIONS.labels(operation=operation, result=result).inc()

def update_active_connections(workflow_id: str, count: int):
    """Update active WebSocket connections gauge"""
    ACTIVE_CONNECTIONS.labels(workflow_id=workflow_id).set(count)