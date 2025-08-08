from sqlalchemy import Column, String, Boolean, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(255))
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Role and permissions
    role = Column(Enum(UserRole), default=UserRole.EDITOR)
    permissions = Column(JSON, default={})
    
    # Profile
    avatar_url = Column(String(500))
    preferences = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Google Drive integration
    google_refresh_token = Column(String(500))
    google_drive_folder_id = Column(String(100))

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False)
    user_id = Column(String, nullable=True)  # None for AI messages
    
    # Message content
    message = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, system, ai_response
    metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="chat_messages")

class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False)
    checkpoint_id = Column(String, nullable=False)
    
    # Approval details
    approver_id = Column(String, nullable=False)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    comments = Column(Text)
    
    # Changes made during approval
    changes_made = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True))
    
    # Relationships
    workflow = relationship("Workflow", back_populates="approvals")