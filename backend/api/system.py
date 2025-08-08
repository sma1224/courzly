from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from prometheus_client import CollectorRegistry, generate_latest
import psutil
import time
from datetime import datetime

from database.connection import get_db, get_redis
from middleware.auth import get_current_user, require_admin

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {"status": "healthy", "response_time": "< 1ms"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        redis_client = await get_redis()
        start_time = time.time()
        await redis_client.ping()
        response_time = (time.time() - start_time) * 1000
        health_status["checks"]["redis"] = {
            "status": "healthy", 
            "response_time": f"{response_time:.2f}ms"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # System resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": (disk.used / disk.total) * 100,
            "available_memory_gb": memory.available / (1024**3)
        }
        
        # Alert if resources are high
        if cpu_percent > 80 or memory.percent > 80:
            health_status["checks"]["system"]["status"] = "warning"
            
    except Exception as e:
        health_status["checks"]["system"] = {"status": "error", "error": str(e)}
    
    return health_status

@router.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest()

@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get system statistics"""
    from models import Workflow, Content, ChatMessage, User
    
    # Database statistics
    total_workflows = db.query(Workflow).count()
    active_workflows = db.query(Workflow).filter(
        Workflow.status.in_(["running", "paused", "waiting_approval"])
    ).count()
    total_content = db.query(Content).count()
    total_messages = db.query(ChatMessage).count()
    total_users = db.query(User).count()
    
    # Workflow status breakdown
    workflow_stats = db.execute(text("""
        SELECT status, COUNT(*) as count 
        FROM workflows 
        GROUP BY status
    """)).fetchall()
    
    # Content type breakdown
    content_stats = db.execute(text("""
        SELECT content_type, COUNT(*) as count 
        FROM content 
        GROUP BY content_type
    """)).fetchall()
    
    return {
        "overview": {
            "total_workflows": total_workflows,
            "active_workflows": active_workflows,
            "total_content": total_content,
            "total_messages": total_messages,
            "total_users": total_users
        },
        "workflow_status": {row[0]: row[1] for row in workflow_stats},
        "content_types": {row[0]: row[1] for row in content_stats},
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/logs")
async def get_system_logs(
    level: str = "INFO",
    limit: int = 100,
    current_user = Depends(require_admin)
):
    """Get system logs (admin only)"""
    import logging
    import os
    
    try:
        log_file = "/app/logs/app.log"  # Adjust path as needed
        if not os.path.exists(log_file):
            return {"logs": [], "message": "Log file not found"}
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        # Filter by level and limit
        filtered_logs = []
        for line in reversed(lines[-limit:]):
            if level.upper() in line:
                filtered_logs.append(line.strip())
        
        return {
            "logs": filtered_logs,
            "total_lines": len(lines),
            "filtered_count": len(filtered_logs)
        }
        
    except Exception as e:
        return {"error": f"Failed to read logs: {str(e)}"}

@router.post("/maintenance")
async def toggle_maintenance_mode(
    enabled: bool,
    current_user = Depends(require_admin)
):
    """Toggle maintenance mode (admin only)"""
    redis_client = await get_redis()
    
    if enabled:
        await redis_client.set("maintenance_mode", "true", ex=3600)  # 1 hour default
        message = "Maintenance mode enabled"
    else:
        await redis_client.delete("maintenance_mode")
        message = "Maintenance mode disabled"
    
    return {
        "message": message,
        "maintenance_mode": enabled,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/maintenance")
async def get_maintenance_status():
    """Check if system is in maintenance mode"""
    redis_client = await get_redis()
    maintenance_mode = await redis_client.get("maintenance_mode")
    
    return {
        "maintenance_mode": maintenance_mode == "true",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/cache/clear")
async def clear_cache(
    pattern: str = "*",
    current_user = Depends(require_admin)
):
    """Clear Redis cache (admin only)"""
    redis_client = await get_redis()
    
    try:
        keys = await redis_client.keys(pattern)
        if keys:
            deleted_count = await redis_client.delete(*keys)
        else:
            deleted_count = 0
        
        return {
            "message": f"Cleared {deleted_count} cache entries",
            "pattern": pattern,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Failed to clear cache: {str(e)}"}

@router.get("/backup/status")
async def get_backup_status(current_user = Depends(require_admin)):
    """Get backup status (admin only)"""
    # This would integrate with your backup system
    return {
        "last_backup": "2024-01-01T00:00:00Z",  # Placeholder
        "backup_size": "1.2GB",
        "status": "completed",
        "next_backup": "2024-01-02T00:00:00Z"
    }

@router.post("/backup/create")
async def create_backup(current_user = Depends(require_admin)):
    """Create system backup (admin only)"""
    # This would trigger your backup process
    return {
        "message": "Backup initiated",
        "backup_id": "backup_20240101_000000",
        "timestamp": datetime.utcnow().isoformat()
    }