from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum

class WorkflowStatus(enum.Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStage(enum.Enum):
    OUTLINE = "outline"
    CONTENT_GENERATION = "content_generation"
    REVIEW = "review"
    FINAL_ASSEMBLY = "final_assembly"
    EXPORT = "export"

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.CREATED)
    current_stage = Column(Enum(WorkflowStage), default=WorkflowStage.OUTLINE)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, ForeignKey("users.id"))
    
    # Configuration
    config = Column(JSON, default={})
    
    # LangGraph state
    langgraph_state = Column(JSON, default={})
    checkpoint_id = Column(String)
    
    # Relationships
    checkpoints = relationship("WorkflowCheckpoint", back_populates="workflow", cascade="all, delete-orphan")
    content = relationship("Content", back_populates="workflow", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="workflow", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="workflow", cascade="all, delete-orphan")

class WorkflowCheckpoint(Base):
    __tablename__ = "workflow_checkpoints"
    
    id = Column(String, primary_key=True)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    stage = Column(Enum(WorkflowStage), nullable=False)
    
    # Checkpoint data
    state_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Human intervention
    requires_approval = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    approved_by = Column(String, ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # Relationships
    workflow = relationship("Workflow", back_populates="checkpoints")

class Content(Base):
    __tablename__ = "content"
    
    id = Column(String, primary_key=True)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    
    # Content details
    title = Column(String(255))
    content_type = Column(String(50))  # outline, module, lesson, etc.
    content_data = Column(JSON, nullable=False)
    
    # Versioning
    version = Column(Integer, default=1)
    parent_id = Column(String, ForeignKey("content.id"))
    
    # Status
    is_ai_generated = Column(Boolean, default=True)
    is_human_edited = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="content")
    children = relationship("Content", backref="parent", remote_side=[id])