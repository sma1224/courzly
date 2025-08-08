from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid

from database.connection import get_db
from models import Workflow, WorkflowStatus, WorkflowStage, WorkflowCheckpoint
from workflows.course_workflow import CourseWorkflow
from middleware.auth import get_current_user

router = APIRouter()

class WorkflowCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    config: dict = {}

class WorkflowResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    current_stage: str
    created_at: str
    config: dict

class CheckpointResponse(BaseModel):
    id: str
    stage: str
    requires_approval: bool
    approved: bool
    created_at: str
    state_data: dict

@router.post("/course/create", response_model=WorkflowResponse)
async def create_course_workflow(
    request: WorkflowCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new course creation workflow"""
    workflow_id = str(uuid.uuid4())
    
    # Create workflow record
    workflow = Workflow(
        id=workflow_id,
        title=request.title,
        description=request.description,
        status=WorkflowStatus.CREATED,
        current_stage=WorkflowStage.OUTLINE,
        created_by=current_user.id,
        config=request.config
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    # Start workflow in background
    background_tasks.add_task(start_course_workflow, workflow_id, request.config)
    
    return WorkflowResponse(
        id=workflow.id,
        title=workflow.title,
        description=workflow.description,
        status=workflow.status.value,
        current_stage=workflow.current_stage.value,
        created_at=workflow.created_at.isoformat(),
        config=workflow.config
    )

@router.get("/{workflow_id}/status", response_model=WorkflowResponse)
async def get_workflow_status(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get workflow status and current stage"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return WorkflowResponse(
        id=workflow.id,
        title=workflow.title,
        description=workflow.description,
        status=workflow.status.value,
        current_stage=workflow.current_stage.value,
        created_at=workflow.created_at.isoformat(),
        config=workflow.config
    )

@router.get("/{workflow_id}/checkpoints", response_model=List[CheckpointResponse])
async def get_workflow_checkpoints(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all checkpoints for a workflow"""
    checkpoints = db.query(WorkflowCheckpoint).filter(
        WorkflowCheckpoint.workflow_id == workflow_id
    ).order_by(WorkflowCheckpoint.created_at).all()
    
    return [
        CheckpointResponse(
            id=cp.id,
            stage=cp.stage.value,
            requires_approval=cp.requires_approval,
            approved=cp.approved,
            created_at=cp.created_at.isoformat(),
            state_data=cp.state_data
        )
        for cp in checkpoints
    ]

@router.post("/{workflow_id}/resume")
async def resume_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Resume a paused workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.status not in [WorkflowStatus.PAUSED, WorkflowStatus.WAITING_APPROVAL]:
        raise HTTPException(status_code=400, detail="Workflow cannot be resumed")
    
    # Update status
    workflow.status = WorkflowStatus.RUNNING
    db.commit()
    
    # Resume workflow in background
    background_tasks.add_task(resume_course_workflow, workflow_id)
    
    return {"message": "Workflow resumed", "workflow_id": workflow_id}

@router.post("/{workflow_id}/pause")
async def pause_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Pause a running workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow.status != WorkflowStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Only running workflows can be paused")
    
    workflow.status = WorkflowStatus.PAUSED
    db.commit()
    
    return {"message": "Workflow paused", "workflow_id": workflow_id}

@router.delete("/{workflow_id}")
async def cancel_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cancel a workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow.status = WorkflowStatus.CANCELLED
    db.commit()
    
    return {"message": "Workflow cancelled", "workflow_id": workflow_id}

async def start_course_workflow(workflow_id: str, config: dict):
    """Background task to start course workflow"""
    course_workflow = CourseWorkflow(workflow_id, config)
    await course_workflow.start()

async def resume_course_workflow(workflow_id: str):
    """Background task to resume course workflow"""
    course_workflow = CourseWorkflow(workflow_id)
    await course_workflow.resume()