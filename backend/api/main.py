from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
import asyncio

from .models import AgentConfig, WorkflowTemplate, ExecutionStatus
from .services import FlowiseService, WorkflowExecutor, TemplateManager
from .database import get_db, SessionLocal
from .auth import verify_token

app = FastAPI(
    title="Courzly Agent Configuration API",
    description="Universal agent configuration system for dynamic workflow execution",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Services
flowise_service = FlowiseService()
workflow_executor = WorkflowExecutor()
template_manager = TemplateManager()

@app.post("/api/v1/agents/create")
async def create_agent(
    config: AgentConfig,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SessionLocal = Depends(get_db)
):
    """Create a new agent from JSON configuration"""
    try:
        # Validate token
        user = verify_token(credentials.credentials)
        
        # Validate configuration
        validated_config = AgentConfig.validate(config.dict())
        
        # Generate unique agent ID
        agent_id = str(uuid.uuid4())
        
        # Create Flowise workflow
        workflow_data = await flowise_service.create_workflow(
            agent_id, validated_config
        )
        
        # Store in database
        agent_record = {
            "id": agent_id,
            "name": validated_config.name,
            "config": validated_config.dict(),
            "workflow_id": workflow_data["id"],
            "created_by": user["id"],
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        # Save to database
        db.execute(
            "INSERT INTO agents (id, name, config, workflow_id, created_by, created_at, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            tuple(agent_record.values())
        )
        db.commit()
        
        return {
            "success": True,
            "agent_id": agent_id,
            "workflow_id": workflow_data["id"],
            "message": f"Agent '{validated_config.name}' created successfully"
        }
        
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Configuration validation failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {e}")

@app.post("/api/v1/workflows/execute")
async def execute_workflow(
    execution_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SessionLocal = Depends(get_db)
):
    """Execute a workflow with given parameters"""
    try:
        user = verify_token(credentials.credentials)
        
        agent_id = execution_request.get("agent_id")
        parameters = execution_request.get("parameters", {})
        
        # Get agent configuration
        agent = db.execute(
            "SELECT * FROM agents WHERE id = %s AND status = 'active'",
            (agent_id,)
        ).fetchone()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution_record = {
            "id": execution_id,
            "agent_id": agent_id,
            "parameters": json.dumps(parameters),
            "status": "running",
            "started_by": user["id"],
            "started_at": datetime.utcnow()
        }
        
        db.execute(
            "INSERT INTO executions (id, agent_id, parameters, status, started_by, started_at) VALUES (%s, %s, %s, %s, %s, %s)",
            tuple(execution_record.values())
        )
        db.commit()
        
        # Execute workflow in background
        background_tasks.add_task(
            workflow_executor.execute,
            execution_id,
            agent["workflow_id"],
            parameters
        )
        
        return {
            "success": True,
            "execution_id": execution_id,
            "status": "running",
            "message": "Workflow execution started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute workflow: {e}")

@app.get("/api/v1/executions/{execution_id}/status")
async def get_execution_status(
    execution_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SessionLocal = Depends(get_db)
):
    """Get real-time execution status"""
    try:
        user = verify_token(credentials.credentials)
        
        execution = db.execute(
            "SELECT * FROM executions WHERE id = %s",
            (execution_id,)
        ).fetchone()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        # Get detailed status from workflow executor
        detailed_status = await workflow_executor.get_status(execution_id)
        
        return {
            "execution_id": execution_id,
            "status": execution["status"],
            "progress": detailed_status.get("progress", 0),
            "current_step": detailed_status.get("current_step"),
            "steps_completed": detailed_status.get("steps_completed", 0),
            "total_steps": detailed_status.get("total_steps", 0),
            "started_at": execution["started_at"],
            "updated_at": detailed_status.get("updated_at"),
            "logs": detailed_status.get("logs", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get execution status: {e}")

@app.post("/api/v1/templates/create")
async def create_template(
    template_data: WorkflowTemplate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SessionLocal = Depends(get_db)
):
    """Create a new workflow template"""
    try:
        user = verify_token(credentials.credentials)
        
        template_id = str(uuid.uuid4())
        template_record = {
            "id": template_id,
            "name": template_data.name,
            "description": template_data.description,
            "category": template_data.category,
            "template_data": json.dumps(template_data.dict()),
            "created_by": user["id"],
            "created_at": datetime.utcnow(),
            "is_public": template_data.is_public
        }
        
        db.execute(
            "INSERT INTO templates (id, name, description, category, template_data, created_by, created_at, is_public) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            tuple(template_record.values())
        )
        db.commit()
        
        return {
            "success": True,
            "template_id": template_id,
            "message": f"Template '{template_data.name}' created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create template: {e}")

@app.get("/api/v1/templates")
async def list_templates(
    category: Optional[str] = None,
    search: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SessionLocal = Depends(get_db)
):
    """List available workflow templates"""
    try:
        user = verify_token(credentials.credentials)
        
        query = "SELECT * FROM templates WHERE (is_public = true OR created_by = %s)"
        params = [user["id"]]
        
        if category:
            query += " AND category = %s"
            params.append(category)
            
        if search:
            query += " AND (name ILIKE %s OR description ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        templates = db.execute(query, tuple(params)).fetchall()
        
        return {
            "templates": [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "description": t["description"],
                    "category": t["category"],
                    "created_at": t["created_at"],
                    "is_public": t["is_public"]
                }
                for t in templates
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list templates: {e}")

@app.post("/api/v1/batch/execute")
async def batch_execute(
    batch_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SessionLocal = Depends(get_db)
):
    """Execute multiple workflows in batch"""
    try:
        user = verify_token(credentials.credentials)
        
        executions = batch_request.get("executions", [])
        batch_id = str(uuid.uuid4())
        
        # Create batch record
        batch_record = {
            "id": batch_id,
            "total_executions": len(executions),
            "status": "running",
            "created_by": user["id"],
            "created_at": datetime.utcnow()
        }
        
        db.execute(
            "INSERT INTO batch_executions (id, total_executions, status, created_by, created_at) VALUES (%s, %s, %s, %s, %s)",
            tuple(batch_record.values())
        )
        db.commit()
        
        # Start batch execution
        background_tasks.add_task(
            workflow_executor.execute_batch,
            batch_id,
            executions
        )
        
        return {
            "success": True,
            "batch_id": batch_id,
            "total_executions": len(executions),
            "message": "Batch execution started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start batch execution: {e}")

@app.post("/api/v1/approvals/{approval_id}/respond")
async def respond_to_approval(
    approval_id: str,
    response_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: SessionLocal = Depends(get_db)
):
    """Respond to a human approval request"""
    try:
        user = verify_token(credentials.credentials)
        
        approval = db.execute(
            "SELECT * FROM approvals WHERE id = %s AND status = 'pending'",
            (approval_id,)
        ).fetchone()
        
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found")
        
        # Update approval status
        db.execute(
            "UPDATE approvals SET status = %s, response = %s, responded_by = %s, responded_at = %s WHERE id = %s",
            (
                response_data["decision"],
                json.dumps(response_data.get("feedback", {})),
                user["id"],
                datetime.utcnow(),
                approval_id
            )
        )
        db.commit()
        
        # Continue workflow execution
        await workflow_executor.continue_after_approval(
            approval["execution_id"],
            response_data
        )
        
        return {
            "success": True,
            "message": "Approval response recorded and workflow continued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to respond to approval: {e}")

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "flowise": "connected",
            "redis": "connected"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)