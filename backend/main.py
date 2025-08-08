from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import time

from api.workflows import router as workflows_router
from api.chat import router as chat_router
from api.content import router as content_router
from api.system import router as system_router
from api.hitl import router as hitl_router
from api.auth import router as auth_router
from api.demo import router as demo_router
from database.connection import init_db, close_db
from chat.manager import ConnectionManager
from middleware.auth import verify_token
from middleware.metrics import MetricsMiddleware
from middleware.logging import LoggingMiddleware

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
WEBSOCKET_CONNECTIONS = Counter('websocket_connections_total', 'Total WebSocket connections')
WORKFLOW_OPERATIONS = Counter('workflow_operations_total', 'Total workflow operations', ['operation', 'status'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Courzly API server...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Courzly API server...")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="Courzly API",
    description="Dynamic Agent Platform for Course Creation with Human-in-the-Loop Workflows",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# API Routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(workflows_router, prefix="/api/workflows", tags=["workflows"])
app.include_router(hitl_router, prefix="/api/hitl", tags=["human-in-the-loop"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(content_router, prefix="/api/content", tags=["content"])
app.include_router(system_router, prefix="/system", tags=["system"])
app.include_router(demo_router, prefix="/demo", tags=["demo"])

# WebSocket connection manager
manager = ConnectionManager()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Courzly Dynamic Agent Platform API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "courzly-api"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

@app.websocket("/ws/chat/{workflow_id}")
async def websocket_chat_endpoint(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for real-time chat in workflows"""
    WEBSOCKET_CONNECTIONS.inc()
    await manager.connect(websocket, workflow_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            # Process and broadcast message
            await manager.handle_message(workflow_id, data, websocket)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for workflow {workflow_id}")
        manager.disconnect(websocket, workflow_id)
    except Exception as e:
        logger.error(f"WebSocket error for workflow {workflow_id}: {e}")
        manager.disconnect(websocket, workflow_id)

@app.websocket("/ws/workflow/{workflow_id}/status")
async def websocket_workflow_status(websocket: WebSocket, workflow_id: str):
    """WebSocket endpoint for real-time workflow status updates"""
    await manager.connect_status(websocket, workflow_id)
    
    try:
        while True:
            # Keep connection alive and send status updates
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        logger.info(f"Status WebSocket disconnected for workflow {workflow_id}")
        manager.disconnect_status(websocket, workflow_id)
    except Exception as e:
        logger.error(f"Status WebSocket error for workflow {workflow_id}: {e}")
        manager.disconnect_status(websocket, workflow_id)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )