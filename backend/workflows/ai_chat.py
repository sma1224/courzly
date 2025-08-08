from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, Any
import os
import json

from database.connection import get_db
from models import Workflow, Content

class WorkflowChatAgent:
    """AI agent for workflow-aware chat interactions"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.system_prompt = """You are an AI assistant helping with course creation workflows. 
        You have access to the current workflow context and can provide guidance, suggestions, 
        and answer questions about the course being created.
        
        Your capabilities include:
        1. Providing feedback on course outlines and content
        2. Suggesting improvements and alternatives
        3. Answering questions about instructional design
        4. Helping with content structure and organization
        5. Providing writing and editing suggestions
        
        Always be helpful, constructive, and focused on improving the course quality.
        Keep responses concise but informative."""
    
    async def generate_response(self, workflow_id: str, user_message: str) -> str:
        """Generate AI response based on workflow context"""
        
        # Get workflow context
        context = await self._get_workflow_context(workflow_id)
        
        # Build context-aware prompt
        context_prompt = self._build_context_prompt(context)
        
        messages = [
            SystemMessage(content=self.system_prompt),
            SystemMessage(content=context_prompt),
            HumanMessage(content=user_message)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            return f"I'm having trouble responding right now. Error: {str(e)}"
    
    async def _get_workflow_context(self, workflow_id: str) -> Dict[str, Any]:
        """Get current workflow context"""
        try:
            db = next(get_db())
            
            # Get workflow
            workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                return {}
            
            # Get content
            content_items = db.query(Content).filter(
                Content.workflow_id == workflow_id
            ).order_by(Content.created_at).all()
            
            context = {
                "workflow": {
                    "id": workflow.id,
                    "title": workflow.title,
                    "description": workflow.description,
                    "status": workflow.status.value,
                    "current_stage": workflow.current_stage.value,
                    "config": workflow.config
                },
                "content": []
            }
            
            for item in content_items:
                context["content"].append({
                    "type": item.content_type,
                    "title": item.title,
                    "data": item.content_data,
                    "is_ai_generated": item.is_ai_generated,
                    "is_approved": item.is_approved
                })
            
            return context
            
        except Exception as e:
            print(f"Error getting workflow context: {e}")
            return {}
    
    def _build_context_prompt(self, context: Dict[str, Any]) -> str:
        """Build context-aware system prompt"""
        if not context:
            return "No workflow context available."
        
        workflow = context.get("workflow", {})
        content = context.get("content", [])
        
        prompt = f"""
        Current Workflow Context:
        - Course Title: {workflow.get('title', 'Unknown')}
        - Description: {workflow.get('description', 'No description')}
        - Current Status: {workflow.get('status', 'Unknown')}
        - Current Stage: {workflow.get('current_stage', 'Unknown')}
        
        Content Created So Far:
        """
        
        for item in content:
            prompt += f"\n- {item['type']}: {item['title']} (AI: {item['is_ai_generated']}, Approved: {item['is_approved']})"
        
        prompt += "\n\nUse this context to provide relevant and helpful responses."
        
        return prompt

async def generate_ai_response(workflow_id: str, user_message: str) -> str:
    """Generate AI response for workflow chat"""
    agent = WorkflowChatAgent()
    return await agent.generate_response(workflow_id, user_message)