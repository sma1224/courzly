import httpx
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class APIClient:
    """HTTP client for Courzly API"""
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=30.0
        )
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Courzly-CLI/1.0.0'
        }
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
            
        return headers
    
    async def create_course(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new course"""
        response = await self.client.post('/api/v1/courses/create', json=course_data)
        response.raise_for_status()
        return response.json()
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get execution status"""
        response = await self.client.get(f'/api/v1/executions/{execution_id}/status')
        response.raise_for_status()
        return response.json()
    
    async def create_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent"""
        response = await self.client.post('/api/v1/agents/create', json=config)
        response.raise_for_status()
        return response.json()
    
    async def execute_workflow(self, agent_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow"""
        data = {
            'agent_id': agent_id,
            'parameters': parameters
        }
        response = await self.client.post('/api/v1/workflows/execute', json=data)
        response.raise_for_status()
        return response.json()
    
    async def get_templates(self, category: Optional[str] = None, search: Optional[str] = None) -> Dict[str, Any]:
        """Get available templates"""
        params = {}
        if category:
            params['category'] = category
        if search:
            params['search'] = search
            
        response = await self.client.get('/api/v1/templates', params=params)
        response.raise_for_status()
        return response.json()
    
    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new template"""
        response = await self.client.post('/api/v1/templates/create', json=template_data)
        response.raise_for_status()
        return response.json()
    
    async def get_pending_approvals(self) -> Dict[str, Any]:
        """Get pending approvals"""
        response = await self.client.get('/api/v1/approvals/pending')
        response.raise_for_status()
        return response.json()
    
    async def respond_to_approval(self, approval_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Respond to an approval request"""
        response = await self.client.post(f'/api/v1/approvals/{approval_id}/respond', json=response_data)
        response.raise_for_status()
        return response.json()
    
    async def execute_batch(self, executions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute batch operations"""
        data = {'executions': executions}
        response = await self.client.post('/api/v1/batch/execute', json=data)
        response.raise_for_status()
        return response.json()
    
    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get batch execution status"""
        response = await self.client.get(f'/api/v1/batch/{batch_id}/status')
        response.raise_for_status()
        return response.json()
    
    async def get_analytics(self, time_range: str = '7d') -> Dict[str, Any]:
        """Get analytics data"""
        response = await self.client.get(f'/api/v1/analytics?range={time_range}')
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = await self.client.get('/api/v1/health')
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()