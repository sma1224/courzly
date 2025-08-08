import pytest
from unittest.mock import Mock, patch
from workflows.course_workflow import CourseWorkflow, CourseWorkflowState
from agents.course_agent import CourseOutlineAgent, ContentGenerationAgent

class TestCourseWorkflow:
    
    @pytest.fixture
    def workflow_config(self):
        return {
            "title": "Test Course",
            "description": "Test Description",
            "target_audience": "Developers",
            "level": "intermediate"
        }
    
    @pytest.fixture
    def workflow(self, workflow_config):
        return CourseWorkflow("test-workflow-id", workflow_config)
    
    def test_workflow_initialization(self, workflow, workflow_config):
        assert workflow.workflow_id == "test-workflow-id"
        assert workflow.config == workflow_config
        assert workflow.state.workflow_id == "test-workflow-id"
    
    @pytest.mark.asyncio
    async def test_create_outline(self, workflow):
        # Mock the outline agent
        with patch('workflows.course_workflow.CourseOutlineAgent') as mock_agent:
            mock_instance = Mock()
            mock_agent.return_value = mock_instance
            mock_instance.generate_outline.return_value = {
                "title": "Test Course",
                "modules": [{"title": "Module 1", "description": "Test module"}]
            }
            
            # Mock database operations
            with patch.object(workflow, '_save_content') as mock_save, \
                 patch.object(workflow, '_create_checkpoint') as mock_checkpoint, \
                 patch.object(workflow, '_update_workflow_status') as mock_status:
                
                result = await workflow._create_outline(workflow.state)
                
                assert result.outline["title"] == "Test Course"
                assert len(result.outline["modules"]) == 1
                mock_save.assert_called_once()
                mock_checkpoint.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_content(self, workflow):
        # Set up state with outline
        workflow.state.outline = {
            "modules": [{"title": "Module 1", "description": "Test module"}]
        }
        
        with patch('workflows.course_workflow.ContentGenerationAgent') as mock_agent:
            mock_instance = Mock()
            mock_agent.return_value = mock_instance
            mock_instance.generate_module_content.return_value = {
                "title": "Module 1",
                "content": {"introduction": "Test content"}
            }
            
            with patch.object(workflow, '_save_content') as mock_save, \
                 patch.object(workflow, '_create_checkpoint') as mock_checkpoint, \
                 patch.object(workflow, '_update_workflow_status') as mock_status:
                
                result = await workflow._generate_content(workflow.state)
                
                assert len(result.modules) == 1
                assert result.modules[0]["title"] == "Module 1"

class TestCourseOutlineAgent:
    
    @pytest.fixture
    def agent(self):
        return CourseOutlineAgent()
    
    @pytest.mark.asyncio
    async def test_generate_outline(self, agent):
        with patch.object(agent.llm, 'ainvoke') as mock_llm:
            mock_response = Mock()
            mock_response.content = '''
            {
                "title": "Test Course",
                "description": "Test Description",
                "modules": [
                    {
                        "title": "Module 1",
                        "description": "First module",
                        "lessons": [
                            {"title": "Lesson 1", "description": "First lesson"}
                        ]
                    }
                ]
            }
            '''
            mock_llm.return_value = mock_response
            
            result = await agent.generate_outline(
                title="Test Course",
                description="Test Description",
                config={"target_audience": "Developers"}
            )
            
            assert result["title"] == "Test Course"
            assert len(result["modules"]) == 1
            assert result["modules"][0]["title"] == "Module 1"
    
    def test_validate_outline(self, agent):
        valid_outline = {
            "title": "Test Course",
            "description": "Test Description",
            "modules": [{"title": "Module 1", "lessons": []}]
        }
        
        result = agent._validate_outline(valid_outline)
        assert "metadata" in result
        assert result["metadata"]["generated_by"] == "CourseOutlineAgent"
    
    def test_validate_outline_missing_fields(self, agent):
        invalid_outline = {"description": "Missing title"}
        
        with pytest.raises(ValueError, match="Missing required field: title"):
            agent._validate_outline(invalid_outline)