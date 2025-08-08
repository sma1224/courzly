# Courzly API Documentation

## Overview

The Courzly API provides endpoints for managing AI-powered course creation workflows with human-in-the-loop capabilities.

**Base URL**: `https://your-domain.com/api`

## Authentication

All API endpoints require JWT authentication via Bearer token.

```bash
Authorization: Bearer <your-jwt-token>
```

### Get Token
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

## Core Endpoints

### Workflows

#### Create Course Workflow
```http
POST /api/workflows/course/create
Authorization: Bearer <token>

{
  "title": "Introduction to Python",
  "description": "Comprehensive Python course",
  "config": {
    "target_audience": "Beginners",
    "level": "beginner",
    "duration": "4 hours",
    "num_modules": "5",
    "include_exercises": true,
    "include_quizzes": true
  }
}
```

**Response**:
```json
{
  "id": "workflow-uuid",
  "title": "Introduction to Python",
  "status": "created",
  "current_stage": "outline",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get Workflow Status
```http
GET /api/workflows/{workflow_id}/status
Authorization: Bearer <token>
```

#### Resume/Pause Workflow
```http
POST /api/workflows/{workflow_id}/resume
POST /api/workflows/{workflow_id}/pause
Authorization: Bearer <token>
```

### Human-in-the-Loop (HITL)

#### Approve Checkpoint
```http
POST /api/hitl/{workflow_id}/approve
Authorization: Bearer <token>

{
  "status": "approved",
  "comments": "Looks good, proceed to next stage",
  "changes_made": {}
}
```

#### Edit Content
```http
POST /api/hitl/{workflow_id}/edit?content_id={content_id}
Authorization: Bearer <token>

{
  "content_data": {
    "title": "Updated Title",
    "content": "Updated content..."
  },
  "comments": "Improved clarity and examples"
}
```

#### Compare Content Versions
```http
GET /api/hitl/{workflow_id}/compare/{content_id}
Authorization: Bearer <token>
```

### Content Management

#### Get Workflow Content
```http
GET /api/content/{workflow_id}
Authorization: Bearer <token>
```

#### Export Content
```http
POST /api/content/{workflow_id}/export
Authorization: Bearer <token>

{
  "format": "pdf|html|scorm|markdown",
  "options": {
    "include_exercises": true,
    "theme": "default"
  }
}
```

### Chat & Collaboration

#### Send Message
```http
POST /api/chat/{workflow_id}/message
Authorization: Bearer <token>

{
  "message": "Can you review the outline?",
  "message_type": "user_query"
}
```

#### Get Chat History
```http
GET /api/chat/{workflow_id}/history?limit=50&offset=0
Authorization: Bearer <token>
```

## WebSocket Endpoints

### Real-time Chat
```javascript
const socket = new WebSocket('wss://your-domain.com/ws/chat/{workflow_id}');

// Send message
socket.send(JSON.stringify({
  message: "Hello AI assistant",
  message_type: "user_query"
}));

// Receive messages
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New message:', data);
};
```

### Workflow Status Updates
```javascript
const statusSocket = new WebSocket('wss://your-domain.com/ws/workflow/{workflow_id}/status');

statusSocket.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Status update:', update);
};
```

## Error Handling

All endpoints return standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

**Error Response Format**:
```json
{
  "error": "Error description",
  "status_code": 400,
  "details": {}
}
```

## Rate Limiting

- API endpoints: 10 requests/second
- Auth endpoints: 5 requests/second
- WebSocket connections: No limit

## Data Models

### Workflow
```typescript
interface Workflow {
  id: string;
  title: string;
  description?: string;
  status: 'created' | 'running' | 'paused' | 'waiting_approval' | 'completed' | 'failed';
  current_stage: 'outline' | 'content_generation' | 'review' | 'final_assembly' | 'export';
  created_at: string;
  config: Record<string, any>;
}
```

### Content
```typescript
interface Content {
  id: string;
  workflow_id: string;
  title?: string;
  content_type: string;
  content_data: Record<string, any>;
  version: number;
  is_ai_generated: boolean;
  is_human_edited: boolean;
  is_approved: boolean;
  created_at: string;
}
```

## SDK Examples

### Python
```python
import requests

class CourzlyAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def create_workflow(self, title, description, config):
        response = requests.post(
            f"{self.base_url}/api/workflows/course/create",
            json={"title": title, "description": description, "config": config},
            headers=self.headers
        )
        return response.json()
```

### JavaScript
```javascript
class CourzlyAPI {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.headers = { 'Authorization': `Bearer ${token}` };
  }
  
  async createWorkflow(title, description, config) {
    const response = await fetch(`${this.baseUrl}/api/workflows/course/create`, {
      method: 'POST',
      headers: { ...this.headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description, config })
    });
    return response.json();
  }
}
```