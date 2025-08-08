import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_create_workflow(client, auth_headers, db_session):
    workflow_data = {
        "title": "Test Course",
        "description": "Test Description",
        "config": {"target_audience": "Developers"}
    }
    
    with patch('api.workflows.start_course_workflow') as mock_start:
        response = client.post(
            "/api/workflows/course/create",
            json=workflow_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Course"
        assert data["status"] == "created"

def test_get_workflow_status(client, auth_headers, db_session, test_user):
    # Create a test workflow in database
    from models import Workflow, WorkflowStatus, WorkflowStage
    
    workflow = Workflow(
        id="test-workflow",
        title="Test Course",
        status=WorkflowStatus.RUNNING,
        current_stage=WorkflowStage.OUTLINE,
        created_by=test_user.id
    )
    db_session.add(workflow)
    db_session.commit()
    
    response = client.get(
        "/api/workflows/test-workflow/status",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-workflow"
    assert data["status"] == "running"

def test_approve_checkpoint(client, auth_headers, db_session, test_user):
    from models import Workflow, WorkflowCheckpoint, WorkflowStage
    
    # Create test workflow and checkpoint
    workflow = Workflow(
        id="test-workflow",
        title="Test Course",
        created_by=test_user.id
    )
    checkpoint = WorkflowCheckpoint(
        id="test-checkpoint",
        workflow_id="test-workflow",
        stage=WorkflowStage.OUTLINE,
        requires_approval=True,
        approved=False,
        state_data={}
    )
    
    db_session.add(workflow)
    db_session.add(checkpoint)
    db_session.commit()
    
    approval_data = {
        "status": "approved",
        "comments": "Looks good!"
    }
    
    response = client.post(
        "/api/hitl/test-workflow/approve",
        json=approval_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"

def test_send_chat_message(client, auth_headers, db_session, test_user):
    from models import Workflow
    
    workflow = Workflow(
        id="test-workflow",
        title="Test Course",
        created_by=test_user.id
    )
    db_session.add(workflow)
    db_session.commit()
    
    message_data = {
        "message": "Hello, AI assistant!",
        "message_type": "user_query"
    }
    
    with patch('api.chat.trigger_ai_response') as mock_ai:
        response = client.post(
            "/api/chat/test-workflow/message",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello, AI assistant!"
        assert data["user_id"] == test_user.id

def test_get_content(client, auth_headers, db_session, test_user):
    from models import Workflow, Content
    
    workflow = Workflow(
        id="test-workflow",
        title="Test Course",
        created_by=test_user.id
    )
    content = Content(
        id="test-content",
        workflow_id="test-workflow",
        title="Test Content",
        content_type="outline",
        content_data={"title": "Test Outline"},
        version=1
    )
    
    db_session.add(workflow)
    db_session.add(content)
    db_session.commit()
    
    response = client.get(
        "/api/content/test-workflow",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Content"

def test_unauthorized_access(client):
    response = client.get("/api/workflows/test/status")
    assert response.status_code == 401

def test_invalid_workflow_id(client, auth_headers):
    response = client.get(
        "/api/workflows/nonexistent/status",
        headers=auth_headers
    )
    assert response.status_code == 404