from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Dict, Any, List
import asyncio
import uuid
from datetime import datetime

from agents.course_agent import CourseOutlineAgent, ContentGenerationAgent, ReviewAgent
from models import Workflow, WorkflowCheckpoint, Content, WorkflowStatus, WorkflowStage
from database.connection import get_db
from middleware.logging import workflow_logger
from chat.manager import connection_manager

class CourseWorkflowState:
    """State management for course creation workflow"""
    
    def __init__(self):
        self.workflow_id: str = ""
        self.title: str = ""
        self.description: str = ""
        self.config: Dict[str, Any] = {}
        self.current_stage: str = "outline"
        self.outline: Dict[str, Any] = {}
        self.modules: List[Dict[str, Any]] = []
        self.content: List[Dict[str, Any]] = []
        self.review_feedback: List[Dict[str, Any]] = []
        self.approval_required: bool = False
        self.human_input: Dict[str, Any] = {}
        self.errors: List[str] = []

class CourseWorkflow:
    """LangGraph-based course creation workflow"""
    
    def __init__(self, workflow_id: str, config: Dict[str, Any] = None):
        self.workflow_id = workflow_id
        self.config = config or {}
        self.state = CourseWorkflowState()
        self.state.workflow_id = workflow_id
        self.state.config = self.config
        
        # Initialize LangGraph
        self.graph = self._build_graph()
        self.checkpointer = SqliteSaver.from_conn_string(":memory:")
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(CourseWorkflowState)
        
        # Add nodes
        workflow.add_node("create_outline", self._create_outline)
        workflow.add_node("human_review_outline", self._human_review_outline)
        workflow.add_node("generate_content", self._generate_content)
        workflow.add_node("human_review_content", self._human_review_content)
        workflow.add_node("final_assembly", self._final_assembly)
        workflow.add_node("export_course", self._export_course)
        
        # Add edges
        workflow.set_entry_point("create_outline")
        workflow.add_edge("create_outline", "human_review_outline")
        workflow.add_conditional_edges(
            "human_review_outline",
            self._should_regenerate_outline,
            {
                "approved": "generate_content",
                "rejected": "create_outline",
                "needs_revision": "create_outline"
            }
        )
        workflow.add_edge("generate_content", "human_review_content")
        workflow.add_conditional_edges(
            "human_review_content",
            self._should_regenerate_content,
            {
                "approved": "final_assembly",
                "rejected": "generate_content",
                "needs_revision": "generate_content"
            }
        )
        workflow.add_edge("final_assembly", "export_course")
        workflow.add_edge("export_course", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def start(self):
        """Start the workflow"""
        try:
            workflow_logger.log_workflow_start(
                self.workflow_id, "course_creation", self.config.get("user_id")
            )
            
            # Update workflow status
            await self._update_workflow_status(WorkflowStatus.RUNNING, WorkflowStage.OUTLINE)
            
            # Initialize state
            self.state.title = self.config.get("title", "")
            self.state.description = self.config.get("description", "")
            
            # Run workflow
            config = {"configurable": {"thread_id": self.workflow_id}}
            result = await self.graph.ainvoke(self.state, config)
            
            workflow_logger.log_workflow_completion(self.workflow_id, 0)  # TODO: track duration
            
        except Exception as e:
            workflow_logger.log_workflow_error(self.workflow_id, str(e))
            await self._update_workflow_status(WorkflowStatus.FAILED)
            raise
    
    async def resume(self):
        """Resume workflow from last checkpoint"""
        try:
            config = {"configurable": {"thread_id": self.workflow_id}}
            
            # Get last checkpoint
            checkpoints = self.graph.get_state_history(config)
            if not checkpoints:
                raise ValueError("No checkpoints found for workflow")
            
            # Resume from last checkpoint
            result = await self.graph.ainvoke(None, config)
            
        except Exception as e:
            workflow_logger.log_workflow_error(self.workflow_id, str(e))
            raise
    
    async def _create_outline(self, state: CourseWorkflowState) -> CourseWorkflowState:
        """Create course outline using AI agent"""
        try:
            await self._update_workflow_status(WorkflowStatus.RUNNING, WorkflowStage.OUTLINE)
            
            outline_agent = CourseOutlineAgent()
            outline = await outline_agent.generate_outline(
                title=state.title,
                description=state.description,
                config=state.config
            )
            
            state.outline = outline
            
            # Save content to database
            await self._save_content("outline", outline, is_ai_generated=True)
            
            # Create checkpoint
            await self._create_checkpoint(WorkflowStage.OUTLINE, state, requires_approval=True)
            
            return state
            
        except Exception as e:
            state.errors.append(f"Outline creation failed: {str(e)}")
            workflow_logger.log_workflow_error(self.workflow_id, str(e), "outline")
            return state
    
    async def _human_review_outline(self, state: CourseWorkflowState) -> CourseWorkflowState:
        """Wait for human review of outline"""
        try:
            await self._update_workflow_status(WorkflowStatus.WAITING_APPROVAL, WorkflowStage.OUTLINE)
            
            # Notify via WebSocket
            await connection_manager.broadcast_status_update(self.workflow_id, {
                "status": "waiting_approval",
                "stage": "outline",
                "message": "Outline ready for review"
            })
            
            # Wait for human input (this will be resumed when approval comes)
            state.approval_required = True
            
            return state
            
        except Exception as e:
            state.errors.append(f"Human review setup failed: {str(e)}")
            return state
    
    async def _generate_content(self, state: CourseWorkflowState) -> CourseWorkflowState:
        """Generate course content using AI agent"""
        try:
            await self._update_workflow_status(WorkflowStatus.RUNNING, WorkflowStage.CONTENT_GENERATION)
            
            content_agent = ContentGenerationAgent()
            
            # Generate content for each module in outline
            modules = []
            for module_outline in state.outline.get("modules", []):
                module_content = await content_agent.generate_module_content(
                    module_outline=module_outline,
                    course_context=state.outline,
                    config=state.config
                )
                modules.append(module_content)
                
                # Save each module
                await self._save_content("module", module_content, is_ai_generated=True)
            
            state.modules = modules
            
            # Create checkpoint
            await self._create_checkpoint(WorkflowStage.CONTENT_GENERATION, state, requires_approval=True)
            
            return state
            
        except Exception as e:
            state.errors.append(f"Content generation failed: {str(e)}")
            workflow_logger.log_workflow_error(self.workflow_id, str(e), "content_generation")
            return state
    
    async def _human_review_content(self, state: CourseWorkflowState) -> CourseWorkflowState:
        """Wait for human review of content"""
        try:
            await self._update_workflow_status(WorkflowStatus.WAITING_APPROVAL, WorkflowStage.CONTENT_GENERATION)
            
            # Notify via WebSocket
            await connection_manager.broadcast_status_update(self.workflow_id, {
                "status": "waiting_approval",
                "stage": "content_generation",
                "message": "Content ready for review"
            })
            
            state.approval_required = True
            
            return state
            
        except Exception as e:
            state.errors.append(f"Content review setup failed: {str(e)}")
            return state
    
    async def _final_assembly(self, state: CourseWorkflowState) -> CourseWorkflowState:
        """Assemble final course"""
        try:
            await self._update_workflow_status(WorkflowStatus.RUNNING, WorkflowStage.FINAL_ASSEMBLY)
            
            # Combine outline and modules into final course structure
            final_course = {
                "title": state.title,
                "description": state.description,
                "outline": state.outline,
                "modules": state.modules,
                "metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "workflow_id": state.workflow_id,
                    "version": "1.0"
                }
            }
            
            state.content = [final_course]
            
            # Save final course
            await self._save_content("final_course", final_course, is_ai_generated=False, is_approved=True)
            
            return state
            
        except Exception as e:
            state.errors.append(f"Final assembly failed: {str(e)}")
            workflow_logger.log_workflow_error(self.workflow_id, str(e), "final_assembly")
            return state
    
    async def _export_course(self, state: CourseWorkflowState) -> CourseWorkflowState:
        """Export course in various formats"""
        try:
            await self._update_workflow_status(WorkflowStatus.RUNNING, WorkflowStage.EXPORT)
            
            # Export logic would go here
            # For now, just mark as completed
            await self._update_workflow_status(WorkflowStatus.COMPLETED, WorkflowStage.EXPORT)
            
            # Notify completion
            await connection_manager.broadcast_status_update(self.workflow_id, {
                "status": "completed",
                "stage": "export",
                "message": "Course creation completed successfully"
            })
            
            return state
            
        except Exception as e:
            state.errors.append(f"Export failed: {str(e)}")
            workflow_logger.log_workflow_error(self.workflow_id, str(e), "export")
            return state
    
    def _should_regenerate_outline(self, state: CourseWorkflowState) -> str:
        """Determine if outline should be regenerated"""
        # This would be set by the approval process
        approval_status = state.human_input.get("outline_approval", "pending")
        
        if approval_status == "approved":
            return "approved"
        elif approval_status == "rejected":
            return "rejected"
        else:
            return "needs_revision"
    
    def _should_regenerate_content(self, state: CourseWorkflowState) -> str:
        """Determine if content should be regenerated"""
        approval_status = state.human_input.get("content_approval", "pending")
        
        if approval_status == "approved":
            return "approved"
        elif approval_status == "rejected":
            return "rejected"
        else:
            return "needs_revision"
    
    async def _update_workflow_status(self, status: WorkflowStatus, stage: WorkflowStage = None):
        """Update workflow status in database"""
        try:
            db = next(get_db())
            workflow = db.query(Workflow).filter(Workflow.id == self.workflow_id).first()
            
            if workflow:
                workflow.status = status
                if stage:
                    workflow.current_stage = stage
                workflow.langgraph_state = self.state.__dict__
                
                db.commit()
                
        except Exception as e:
            print(f"Error updating workflow status: {e}")
    
    async def _create_checkpoint(self, stage: WorkflowStage, state: CourseWorkflowState, requires_approval: bool = False):
        """Create workflow checkpoint"""
        try:
            checkpoint_id = str(uuid.uuid4())
            
            db = next(get_db())
            checkpoint = WorkflowCheckpoint(
                id=checkpoint_id,
                workflow_id=self.workflow_id,
                stage=stage,
                state_data=state.__dict__,
                requires_approval=requires_approval
            )
            
            db.add(checkpoint)
            db.commit()
            
            workflow_logger.log_workflow_checkpoint(self.workflow_id, stage.value, checkpoint_id)
            
        except Exception as e:
            print(f"Error creating checkpoint: {e}")
    
    async def _save_content(self, content_type: str, content_data: dict, is_ai_generated: bool = True, is_approved: bool = False):
        """Save content to database"""
        try:
            content_id = str(uuid.uuid4())
            
            db = next(get_db())
            content = Content(
                id=content_id,
                workflow_id=self.workflow_id,
                title=content_data.get("title", content_type),
                content_type=content_type,
                content_data=content_data,
                is_ai_generated=is_ai_generated,
                is_approved=is_approved
            )
            
            db.add(content)
            db.commit()
            
        except Exception as e:
            print(f"Error saving content: {e}")