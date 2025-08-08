import pytest
import asyncio
from unittest.mock import patch, Mock

@pytest.mark.asyncio
class TestWorkflowIntegration:
    
    async def test_complete_workflow_cycle(self, client, auth_headers, db_session, test_user):
        """Test complete workflow from creation to completion"""
        
        # Step 1: Create workflow
        workflow_data = {
            "title": "Integration Test Course",
            "description": "Full workflow test",
            "config": {
                "target_audience": "Developers",
                "level": "intermediate",
                "num_modules": "3"
            }
        }
        
        with patch('api.workflows.start_course_workflow'):
            response = client.post(
                "/api/workflows/course/create",
                json=workflow_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            workflow_id = response.json()["id"]
        
        # Step 2: Check workflow status
        response = client.get(
            f"/api/workflows/{workflow_id}/status",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["status"] == "created"
        
        # Step 3: Simulate outline generation and approval
        from models import WorkflowCheckpoint, WorkflowStage, Content
        
        # Add outline content
        outline_content = Content(
            id="outline-content",
            workflow_id=workflow_id,
            title="Course Outline",
            content_type="outline",
            content_data={
                "title": "Integration Test Course",
                "modules": [
                    {"title": "Module 1", "description": "First module"},
                    {"title": "Module 2", "description": "Second module"}
                ]
            },
            version=1,
            is_ai_generated=True
        )
        
        checkpoint = WorkflowCheckpoint(
            id="outline-checkpoint",
            workflow_id=workflow_id,
            stage=WorkflowStage.OUTLINE,
            requires_approval=True,
            approved=False,
            state_data={"outline": outline_content.content_data}
        )
        
        db_session.add(outline_content)
        db_session.add(checkpoint)
        db_session.commit()
        
        # Step 4: Approve outline
        approval_data = {
            "status": "approved",
            "comments": "Outline looks good!"
        }
        
        response = client.post(
            f"/api/hitl/{workflow_id}/approve",
            json=approval_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 5: Check content was created
        response = client.get(
            f"/api/content/{workflow_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        content_list = response.json()
        assert len(content_list) >= 1
        assert any(item["content_type"] == "outline" for item in content_list)
    
    async def test_chat_integration(self, client, auth_headers, db_session, test_user):
        """Test chat functionality with workflow context"""
        
        from models import Workflow, Content
        
        # Create workflow with content
        workflow = Workflow(
            id="chat-test-workflow",
            title="Chat Test Course",
            created_by=test_user.id
        )
        
        content = Content(
            id="chat-content",
            workflow_id="chat-test-workflow",
            title="Test Content",
            content_type="outline",
            content_data={"title": "Test Outline"},
            version=1
        )
        
        db_session.add(workflow)
        db_session.add(content)
        db_session.commit()
        
        # Send chat message
        message_data = {
            "message": "Can you review the outline?",
            "message_type": "user_query"
        }
        
        with patch('workflows.ai_chat.generate_ai_response') as mock_ai:
            mock_ai.return_value = "I've reviewed your outline and it looks comprehensive!"
            
            response = client.post(
                "/api/chat/chat-test-workflow/message",
                json=message_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            
            # Check message was saved
            response = client.get(
                "/api/chat/chat-test-workflow/history",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            history = response.json()
            assert history["total_count"] >= 1
    
    async def test_content_editing_workflow(self, client, auth_headers, db_session, test_user):
        """Test content editing and versioning"""
        
        from models import Workflow, Content
        
        workflow = Workflow(
            id="edit-test-workflow",
            title="Edit Test Course",
            created_by=test_user.id
        )
        
        original_content = Content(
            id="original-content",
            workflow_id="edit-test-workflow",
            title="Original Content",
            content_type="module",
            content_data={"content": "Original content text"},
            version=1,
            is_ai_generated=True
        )
        
        db_session.add(workflow)
        db_session.add(original_content)
        db_session.commit()
        
        # Edit content
        edit_data = {
            "content_data": {"content": "Edited content text"},
            "comments": "Improved clarity"
        }
        
        response = client.post(
            f"/api/hitl/edit-test-workflow/edit?content_id=original-content",
            json=edit_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Check new version was created
        response = client.get(
            "/api/content/edit-test-workflow",
            headers=auth_headers
        )
        
        content_list = response.json()
        versions = [item for item in content_list if item["title"] == "Original Content"]
        assert len(versions) >= 2  # Original + edited version
    
    async def test_export_functionality(self, client, auth_headers, db_session, test_user):
        """Test content export in different formats"""
        
        from models import Workflow, Content
        
        workflow = Workflow(
            id="export-test-workflow",
            title="Export Test Course",
            created_by=test_user.id
        )
        
        content = Content(
            id="export-content",
            workflow_id="export-test-workflow",
            title="Export Content",
            content_type="final_course",
            content_data={
                "title": "Export Test Course",
                "modules": [{"title": "Module 1", "content": "Test content"}]
            },
            version=1,
            is_approved=True
        )
        
        db_session.add(workflow)
        db_session.add(content)
        db_session.commit()
        
        # Test HTML export
        export_data = {
            "format": "html",
            "options": {}
        }
        
        response = client.post(
            f"/api/content/export-test-workflow/export",
            json=export_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"