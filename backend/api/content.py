from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import uuid
import json
from io import BytesIO

from database.connection import get_db
from models import Content, Workflow
from middleware.auth import get_current_user
from export.formats import PDFExporter, SCORMExporter, HTMLExporter

router = APIRouter()

class ContentResponse(BaseModel):
    id: str
    workflow_id: str
    title: Optional[str]
    content_type: str
    content_data: dict
    version: int
    is_ai_generated: bool
    is_human_edited: bool
    is_approved: bool
    created_at: str

class ContentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content_data: dict

class ExportRequest(BaseModel):
    format: str  # pdf, html, scorm, markdown
    options: dict = {}

@router.get("/{workflow_id}", response_model=List[ContentResponse])
async def get_workflow_content(
    workflow_id: str,
    content_type: Optional[str] = None,
    version: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all content for a workflow"""
    query = db.query(Content).filter(Content.workflow_id == workflow_id)
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    if version:
        query = query.filter(Content.version == version)
    
    content_items = query.order_by(Content.created_at).all()
    
    return [
        ContentResponse(
            id=item.id,
            workflow_id=item.workflow_id,
            title=item.title,
            content_type=item.content_type,
            content_data=item.content_data,
            version=item.version,
            is_ai_generated=item.is_ai_generated,
            is_human_edited=item.is_human_edited,
            is_approved=item.is_approved,
            created_at=item.created_at.isoformat()
        )
        for item in content_items
    ]

@router.get("/{workflow_id}/{content_id}", response_model=ContentResponse)
async def get_content_by_id(
    workflow_id: str,
    content_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get specific content by ID"""
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.workflow_id == workflow_id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return ContentResponse(
        id=content.id,
        workflow_id=content.workflow_id,
        title=content.title,
        content_type=content.content_type,
        content_data=content.content_data,
        version=content.version,
        is_ai_generated=content.is_ai_generated,
        is_human_edited=content.is_human_edited,
        is_approved=content.is_approved,
        created_at=content.created_at.isoformat()
    )

@router.put("/{workflow_id}/{content_id}", response_model=ContentResponse)
async def update_content(
    workflow_id: str,
    content_id: str,
    request: ContentUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update content (creates new version)"""
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
        title=request.title or original_content.title,
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
    
    return ContentResponse(
        id=new_content.id,
        workflow_id=new_content.workflow_id,
        title=new_content.title,
        content_type=new_content.content_type,
        content_data=new_content.content_data,
        version=new_content.version,
        is_ai_generated=new_content.is_ai_generated,
        is_human_edited=new_content.is_human_edited,
        is_approved=new_content.is_approved,
        created_at=new_content.created_at.isoformat()
    )

@router.get("/{workflow_id}/{content_id}/versions", response_model=List[ContentResponse])
async def get_content_versions(
    workflow_id: str,
    content_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all versions of a content item"""
    # Get the content and all its versions
    content_versions = db.query(Content).filter(
        Content.workflow_id == workflow_id
    ).filter(
        (Content.id == content_id) | (Content.parent_id == content_id)
    ).order_by(Content.version).all()
    
    if not content_versions:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return [
        ContentResponse(
            id=item.id,
            workflow_id=item.workflow_id,
            title=item.title,
            content_type=item.content_type,
            content_data=item.content_data,
            version=item.version,
            is_ai_generated=item.is_ai_generated,
            is_human_edited=item.is_human_edited,
            is_approved=item.is_approved,
            created_at=item.created_at.isoformat()
        )
        for item in content_versions
    ]

@router.get("/{workflow_id}/{content_id}/diff")
async def get_content_diff(
    workflow_id: str,
    content_id: str,
    compare_version: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get diff between content versions"""
    current_content = db.query(Content).filter(
        Content.id == content_id,
        Content.workflow_id == workflow_id
    ).first()
    
    if not current_content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Get comparison version
    if compare_version:
        compare_content = db.query(Content).filter(
            Content.workflow_id == workflow_id,
            Content.version == compare_version
        ).first()
    else:
        # Compare with parent version
        compare_content = db.query(Content).filter(
            Content.id == current_content.parent_id
        ).first() if current_content.parent_id else None
    
    if not compare_content:
        return {"diff": {}, "message": "No comparison version available"}
    
    # Calculate diff
    diff = calculate_content_diff(compare_content.content_data, current_content.content_data)
    
    return {
        "current_version": current_content.version,
        "compare_version": compare_content.version,
        "diff": diff
    }

@router.post("/{workflow_id}/export")
async def export_workflow_content(
    workflow_id: str,
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export workflow content in various formats"""
    # Get workflow and content
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    content_items = db.query(Content).filter(
        Content.workflow_id == workflow_id,
        Content.is_approved == True
    ).order_by(Content.created_at).all()
    
    if not content_items:
        raise HTTPException(status_code=404, detail="No approved content found")
    
    # Export based on format
    try:
        if request.format == "pdf":
            exporter = PDFExporter()
            file_data = await exporter.export(workflow, content_items, request.options)
            media_type = "application/pdf"
            filename = f"{workflow.title}.pdf"
            
        elif request.format == "html":
            exporter = HTMLExporter()
            file_data = await exporter.export(workflow, content_items, request.options)
            media_type = "text/html"
            filename = f"{workflow.title}.html"
            
        elif request.format == "scorm":
            exporter = SCORMExporter()
            file_data = await exporter.export(workflow, content_items, request.options)
            media_type = "application/zip"
            filename = f"{workflow.title}_scorm.zip"
            
        elif request.format == "markdown":
            # Simple markdown export
            markdown_content = export_to_markdown(workflow, content_items)
            file_data = markdown_content.encode('utf-8')
            media_type = "text/markdown"
            filename = f"{workflow.title}.md"
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        return Response(
            content=file_data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

def calculate_content_diff(old_data: dict, new_data: dict) -> dict:
    """Calculate differences between content versions"""
    diff = {}
    
    all_keys = set(old_data.keys()) | set(new_data.keys())
    
    for key in all_keys:
        if key not in old_data:
            diff[key] = {"type": "added", "value": new_data[key]}
        elif key not in new_data:
            diff[key] = {"type": "removed", "value": old_data[key]}
        elif old_data[key] != new_data[key]:
            diff[key] = {
                "type": "modified",
                "old_value": old_data[key],
                "new_value": new_data[key]
            }
    
    return diff

def export_to_markdown(workflow, content_items) -> str:
    """Export content to markdown format"""
    markdown = f"# {workflow.title}\n\n"
    
    if workflow.description:
        markdown += f"{workflow.description}\n\n"
    
    for item in content_items:
        markdown += f"## {item.title or item.content_type.title()}\n\n"
        
        # Extract text content from content_data
        if isinstance(item.content_data, dict):
            if 'text' in item.content_data:
                markdown += f"{item.content_data['text']}\n\n"
            elif 'content' in item.content_data:
                markdown += f"{item.content_data['content']}\n\n"
        
        markdown += "---\n\n"
    
    return markdown