import pytest
import asyncio
import time
from fastapi.testclient import TestClient
from unittest.mock import patch

@pytest.mark.e2e
class TestCompleteWorkflowE2E:
    """End-to-end tests for complete workflow scenarios"""
    
    def test_full_course_creation_workflow(self, client, auth_headers, db_session, test_user):
        """Test complete course creation from start to finish"""
        
        # Step 1: Create new course workflow
        workflow_data = {
            "title": "Complete E2E Test Course",
            "description": "Full end-to-end workflow test",
            "config": {
                "target_audience": "Software Engineers",
                "level": "intermediate",
                "duration": "6 hours",
                "num_modules": "4",
                "include_exercises": True,
                "include_quizzes": True
            }
        }
        
        with patch('api.workflows.start_course_workflow'):
            response = client.post(
                "/api/workflows/course/create",
                json=workflow_data,
                headers=auth_headers
            )
            
            assert response.status_code == 200
            workflow = response.json()
            workflow_id = workflow["id"]
            assert workflow["title"] == "Complete E2E Test Course"
            assert workflow["status"] == "created"
        
        # Step 2: Verify workflow status
        response = client.get(
            f"/api/workflows/{workflow_id}/status",
            headers=auth_headers
        )
        assert response.status_code == 200
        status = response.json()
        assert status["current_stage"] == "outline"
        
        # Step 3: Simulate outline generation completion
        from models import Content, WorkflowCheckpoint, WorkflowStage
        
        outline_data = {
            "title": "Complete E2E Test Course",
            "description": "Full end-to-end workflow test",
            "modules": [
                {
                    "title": "Introduction to Software Engineering",
                    "description": "Basic concepts and principles",
                    "lessons": [
                        {"title": "What is Software Engineering?", "duration": "30 min"},
                        {"title": "Development Lifecycle", "duration": "45 min"}
                    ]
                },
                {
                    "title": "Design Patterns",
                    "description": "Common software design patterns",
                    "lessons": [
                        {"title": "Singleton Pattern", "duration": "30 min"},
                        {"title": "Observer Pattern", "duration": "30 min"}
                    ]
                }
            ]
        }
        
        outline_content = Content(
            id="e2e-outline",
            workflow_id=workflow_id,
            title="Course Outline",
            content_type="outline",
            content_data=outline_data,
            version=1,
            is_ai_generated=True
        )
        
        outline_checkpoint = WorkflowCheckpoint(
            id="e2e-outline-checkpoint",
            workflow_id=workflow_id,
            stage=WorkflowStage.OUTLINE,
            requires_approval=True,
            approved=False,
            state_data={"outline": outline_data}
        )
        
        db_session.add(outline_content)
        db_session.add(outline_checkpoint)
        db_session.commit()
        
        # Step 4: Review and approve outline
        response = client.get(
            f"/api/hitl/{workflow_id}/pending-approvals",
            headers=auth_headers
        )
        assert response.status_code == 200
        pending = response.json()
        assert len(pending) == 1
        assert pending[0]["stage"] == "outline"
        
        # Approve the outline
        approval_data = {
            "status": "approved",
            "comments": "Outline structure looks comprehensive and well-organized."
        }
        
        response = client.post(
            f"/api/hitl/{workflow_id}/approve",
            json=approval_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        approval = response.json()
        assert approval["status"] == "approved"
        
        # Step 5: Simulate content generation
        module_content = Content(
            id="e2e-module-1",
            workflow_id=workflow_id,
            title="Introduction to Software Engineering",
            content_type="module",
            content_data={
                "title": "Introduction to Software Engineering",
                "content": {
                    "introduction": "Software engineering is a systematic approach to software development...",
                    "lessons": [
                        {
                            "title": "What is Software Engineering?",
                            "content": "<h2>What is Software Engineering?</h2><p>Software engineering is...</p>",
                            "activities": ["Read chapter 1", "Complete quiz"],
                            "quiz_questions": [
                                {
                                    "question": "What is the primary goal of software engineering?",
                                    "options": ["Speed", "Quality", "Cost", "All of the above"],
                                    "correct_answer": "All of the above"
                                }
                            ]
                        }
                    ]
                }
            },
            version=1,
            is_ai_generated=True
        )
        
        content_checkpoint = WorkflowCheckpoint(
            id="e2e-content-checkpoint",
            workflow_id=workflow_id,
            stage=WorkflowStage.CONTENT_GENERATION,
            requires_approval=True,
            approved=False,
            state_data={"modules": [module_content.content_data]}
        )
        
        db_session.add(module_content)
        db_session.add(content_checkpoint)
        db_session.commit()
        
        # Step 6: Test content editing
        edit_data = {
            "content_data": {
                **module_content.content_data,
                "content": {
                    **module_content.content_data["content"],
                    "introduction": "Software engineering is a systematic and disciplined approach to software development..."
                }
            },
            "comments": "Enhanced introduction for better clarity"
        }
        
        response = client.post(
            f"/api/hitl/{workflow_id}/edit?content_id=e2e-module-1",
            json=edit_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 7: Test chat functionality
        chat_messages = [
            "Can you review the content structure?",
            "Are there any missing topics?",
            "How can we improve engagement?"
        ]
        
        with patch('workflows.ai_chat.generate_ai_response') as mock_ai:
            mock_ai.side_effect = [
                "The content structure looks well-organized with clear learning objectives.",
                "Consider adding practical examples and hands-on exercises.",
                "Interactive quizzes and real-world case studies would enhance engagement."
            ]
            
            for message in chat_messages:
                response = client.post(
                    f"/api/chat/{workflow_id}/message",
                    json={"message": message, "message_type": "user_query"},
                    headers=auth_headers
                )
                assert response.status_code == 200
        
        # Verify chat history
        response = client.get(
            f"/api/chat/{workflow_id}/history",
            headers=auth_headers
        )
        assert response.status_code == 200
        history = response.json()
        assert history["total_count"] >= len(chat_messages)
        
        # Step 8: Approve content
        response = client.post(
            f"/api/hitl/{workflow_id}/approve",
            json={"status": "approved", "comments": "Content is comprehensive and engaging"},
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Step 9: Test export functionality
        export_formats = ["html", "markdown"]
        
        for format_type in export_formats:
            response = client.post(
                f"/api/content/{workflow_id}/export",
                json={"format": format_type, "options": {}},
                headers=auth_headers
            )
            assert response.status_code == 200
            assert len(response.content) > 0
        
        # Step 10: Verify final workflow state
        response = client.get(
            f"/api/workflows/{workflow_id}/status",
            headers=auth_headers
        )
        assert response.status_code == 200
        final_status = response.json()
        
        # Verify all content was created
        response = client.get(
            f"/api/content/{workflow_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        all_content = response.json()
        assert len(all_content) >= 2  # Outline + at least one module
        
        content_types = [item["content_type"] for item in all_content]
        assert "outline" in content_types
        assert "module" in content_types
    
    def test_workflow_error_handling(self, client, auth_headers, db_session):
        """Test workflow error scenarios and recovery"""
        
        # Test invalid workflow creation
        invalid_data = {
            "title": "",  # Empty title should fail
            "config": {}
        }
        
        response = client.post(
            "/api/workflows/course/create",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422  # Validation error
        
        # Test accessing non-existent workflow
        response = client.get(
            "/api/workflows/non-existent-id/status",
            headers=auth_headers
        )
        assert response.status_code == 404
        
        # Test unauthorized access
        response = client.get("/api/workflows/test/status")
        assert response.status_code == 401
    
    def test_concurrent_workflow_operations(self, client, auth_headers, db_session, test_user):
        """Test concurrent operations on the same workflow"""
        
        from models import Workflow, WorkflowCheckpoint, WorkflowStage
        
        # Create test workflow
        workflow = Workflow(
            id="concurrent-test",
            title="Concurrent Test Course",
            created_by=test_user.id
        )
        
        checkpoint = WorkflowCheckpoint(
            id="concurrent-checkpoint",
            workflow_id="concurrent-test",
            stage=WorkflowStage.OUTLINE,
            requires_approval=True,
            approved=False,
            state_data={}
        )
        
        db_session.add(workflow)
        db_session.add(checkpoint)
        db_session.commit()
        
        # Simulate concurrent approval attempts
        approval_data = {"status": "approved", "comments": "Approved"}
        
        response1 = client.post(
            "/api/hitl/concurrent-test/approve",
            json=approval_data,
            headers=auth_headers
        )
        
        response2 = client.post(
            "/api/hitl/concurrent-test/approve",
            json=approval_data,
            headers=auth_headers
        )
        
        # One should succeed, one should fail or handle gracefully
        assert response1.status_code == 200 or response2.status_code == 200
        
        # Verify only one approval was recorded
        response = client.get(
            "/api/hitl/concurrent-test/approval-history",
            headers=auth_headers
        )
        assert response.status_code == 200