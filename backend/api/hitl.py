from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from database.connection import get_db
from models import Workflow, WorkflowCheckpoint, Content, Approval
from middleware.auth import get_current_user

router = APIRouter()

class ApprovalRequest(BaseModel):
    status: str  # approved, rejected
    comments: Optional[str] = None
    changes_made: dict = {}

class ContentEditRequest(BaseModel):
    content_data: dict
    comments: Optional[str] = None

class ApprovalResponse(BaseModel):
    id: str
    status: str
    comments: Optional[str]
    approver_id: str
    decided_at: Optional[str]

class ContentCompareResponse(BaseModel):
    original: dict
    current: dict
    changes: dict
    version: int

@router.post("/{workflow_id}/approve")
async def approve_checkpoint(
    workflow_id: str,
    request: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Approve or reject a workflow checkpoint"""
    # Get the latest checkpoint requiring approval
    checkpoint = db.query(WorkflowCheckpoint).filter(
        WorkflowCheckpoint.workflow_id == workflow_id,
        WorkflowCheckpoint.requires_approval == True,
        WorkflowCheckpoint.approved == False
    ).order_by(WorkflowCheckpoint.created_at.desc()).first()
    
    if not checkpoint:
        raise HTTPException(status_code=404, detail="No pending approval found")
    
    # Create approval record
    approval = Approval(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        checkpoint_id=checkpoint.id,
        approver_id=current_user.id,
        status=request.status,
        comments=request.comments,
        changes_made=request.changes_made,
        decided_at=datetime.utcnow()
    )
    
    db.add(approval)
    
    # Update checkpoint
    if request.status == "approved":
        checkpoint.approved = True
        checkpoint.approved_by = current_user.id
        checkpoint.approved_at = datetime.utcnow()
        
        # Update workflow status
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if workflow:
            workflow.status = "running"
    
    db.commit()
    
    return ApprovalResponse(
        id=approval.id,
        status=approval.status,
        comments=approval.comments,
        approver_id=approval.approver_id,
        decided_at=approval.decided_at.isoformat() if approval.decided_at else None
    )

@router.post("/{workflow_id}/edit")
async def edit_content(
    workflow_id: str,
    content_id: str,
    request: ContentEditRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Edit content during human-in-the-loop review"""
    # Get original content
    original_content = db.query(Content).filter(
        Content.id == content_id,
        Content.workflow_id == workflow_id
    ).first()
    
    if not original_content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Create new version
    new_content = Content(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        title=original_content.title,
        content_type=original_content.content_type,
        content_data=request.content_data,
        version=original_content.version + 1,
        parent_id=original_content.id,
        is_ai_generated=False,
        is_human_edited=True,
        is_approved=False
    )
    
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    
    return {
        "message": "Content edited successfully",
        "content_id": new_content.id,
        "version": new_content.version
    }

@router.get("/{workflow_id}/compare/{content_id}")
async def compare_content_versions(
    workflow_id: str,
    content_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Compare content versions for review"""
    # Get current content
    current_content = db.query(Content).filter(
        Content.id == content_id,
        Content.workflow_id == workflow_id
    ).first()
    
    if not current_content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Get original version
    original_content = None
    if current_content.parent_id:
        original_content = db.query(Content).filter(
            Content.id == current_content.parent_id
        ).first()
    
    # Calculate changes (simplified diff)
    changes = {}
    if original_content:
        changes = calculate_content_diff(
            original_content.content_data,
            current_content.content_data
        )
    
    return ContentCompareResponse(
        original=original_content.content_data if original_content else {},
        current=current_content.content_data,
        changes=changes,
        version=current_content.version
    )

@router.get("/{workflow_id}/pending-approvals")
async def get_pending_approvals(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all pending approvals for a workflow"""
    checkpoints = db.query(WorkflowCheckpoint).filter(
        WorkflowCheckpoint.workflow_id == workflow_id,
        WorkflowCheckpoint.requires_approval == True,
        WorkflowCheckpoint.approved == False
    ).all()
    
    return [
        {
            "checkpoint_id": cp.id,
            "stage": cp.stage.value,
            "created_at": cp.created_at.isoformat(),
            "state_data": cp.state_data
        }
        for cp in checkpoints
    ]

@router.get("/{workflow_id}/approval-history")
async def get_approval_history(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get approval history for a workflow"""
    approvals = db.query(Approval).filter(
        Approval.workflow_id == workflow_id
    ).order_by(Approval.decided_at.desc()).all()
    
    return [
        ApprovalResponse(
            id=approval.id,
            status=approval.status,
            comments=approval.comments,
            approver_id=approval.approver_id,
            decided_at=approval.decided_at.isoformat() if approval.decided_at else None
        )
        for approval in approvals
    ]

def calculate_content_diff(original: dict, current: dict) -> dict:
    """Calculate differences between content versions"""
    changes = {}
    
    # Simple diff implementation
    for key in set(original.keys()) | set(current.keys()):
        if key not in original:
            changes[key] = {"type": "added", "value": current[key]}
        elif key not in current:
            changes[key] = {"type": "removed", "value": original[key]}
        elif original[key] != current[key]:
            changes[key] = {
                "type": "modified",
                "old_value": original[key],
                "new_value": current[key]
            }
    
    return changes