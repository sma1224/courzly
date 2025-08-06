# Courzly API Documentation

The Courzly API provides comprehensive endpoints for managing dynamic agents, course creation workflows, and platform administration.

## Base URL
```
https://your-domain.com/api/v1
```

## Authentication

All API endpoints require authentication using JWT tokens:

```http
Authorization: Bearer <your-jwt-token>
```

## Course Creation API

### Create Course
Create a new course using the AI-powered workflow.

```http
POST /courses/create
```

**Request Body:**
```json
{
  "title": "Introduction to Python Programming",
  "description": "A comprehensive course for beginners",
  "target_audience": "Programming beginners",
  "duration": "8 weeks",
  "difficulty_level": "beginner",
  "learning_objectives": [
    "Understand Python syntax",
    "Build simple applications",
    "Debug Python code"
  ],
  "topics": [
    "Variables and data types",
    "Control structures",
    "Functions and modules"
  ],
  "assessment_type": "projects",
  "template_id": "technical-course"
}
```

**Response:**
```json
{
  "success": true,
  "execution_id": "exec_123456789",
  "message": "Course creation started successfully"
}
```

### Get Course Status
Monitor the progress of course creation.

```http
GET /executions/{execution_id}/status
```

**Response:**
```json
{
  "execution_id": "exec_123456789",
  "status": "running",
  "progress": 45.5,
  "current_step": "content-creation",
  "steps_completed": 3,
  "total_steps": 7,
  "started_at": "2024-01-15T10:30:00Z",
  "logs": [
    {
      "timestamp": "2024-01-15T10:35:00Z",
      "message": "Requirements gathering completed"
    }
  ]
}
```

## Agent Configuration API

### Create Agent
Create a new agent from JSON configuration.

```http
POST /agents/create
```

**Request Body:**
```json
{
  "name": "Custom Course Creator",
  "description": "Specialized agent for technical courses",
  "nodes": [
    {
      "id": "start",
      "type": "conversationalAgent",
      "label": "Requirements Gatherer",
      "data": {
        "systemMessage": "Gather course requirements...",
        "inputs": {}
      },
      "position": {"x": 100, "y": 100}
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "start",
      "target": "process"
    }
  ],
  "metadata": {
    "name": "Custom Workflow",
    "version": "1.0.0",
    "category": "education"
  }
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "agent_123456789",
  "workflow_id": "workflow_987654321",
  "message": "Agent created successfully"
}
```

### Execute Workflow
Execute a workflow with specific parameters.

```http
POST /workflows/execute
```

**Request Body:**
```json
{
  "agent_id": "agent_123456789",
  "parameters": {
    "course_title": "Advanced Python",
    "target_level": "intermediate",
    "custom_requirements": {
      "include_projects": true,
      "assessment_weight": 0.4
    }
  }
}
```

## Template Management API

### List Templates
Get available workflow templates.

```http
GET /templates?category=education&search=python
```

**Response:**
```json
{
  "templates": [
    {
      "id": "template_123",
      "name": "Technical Course Template",
      "description": "Template for programming courses",
      "category": "education",
      "created_at": "2024-01-10T09:00:00Z",
      "is_public": true
    }
  ]
}
```

### Create Template
Create a new workflow template.

```http
POST /templates/create
```

**Request Body:**
```json
{
  "name": "Business Course Template",
  "description": "Template for business skill courses",
  "category": "business",
  "template_config": {
    "nodes": [...],
    "edges": [...],
    "metadata": {...}
  },
  "is_public": false,
  "tags": ["business", "management"]
}
```

## Approval Management API

### List Pending Approvals
Get all pending approval requests.

```http
GET /approvals/pending
```

**Response:**
```json
{
  "approvals": [
    {
      "id": "approval_123",
      "execution_id": "exec_456",
      "type": "outline_review",
      "message": "Please review the course outline",
      "data": {
        "course_outline": {...}
      },
      "created_at": "2024-01-15T11:00:00Z",
      "expires_at": "2024-01-16T11:00:00Z"
    }
  ]
}
```

### Respond to Approval
Respond to an approval request.

```http
POST /approvals/{approval_id}/respond
```

**Request Body:**
```json
{
  "decision": "approve",
  "feedback": {
    "outline_quality": "excellent",
    "suggested_changes": []
  },
  "comments": "The outline looks comprehensive and well-structured."
}
```

## Batch Operations API

### Execute Batch
Execute multiple workflows in batch.

```http
POST /batch/execute
```

**Request Body:**
```json
{
  "executions": [
    {
      "agent_id": "agent_123",
      "parameters": {"course_title": "Python Basics"}
    },
    {
      "agent_id": "agent_123",
      "parameters": {"course_title": "Python Advanced"}
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "batch_id": "batch_789",
  "total_executions": 2,
  "message": "Batch execution started"
}
```

### Get Batch Status
Monitor batch execution progress.

```http
GET /batch/{batch_id}/status
```

**Response:**
```json
{
  "batch_id": "batch_789",
  "status": "running",
  "total_executions": 2,
  "completed_executions": 1,
  "failed_executions": 0,
  "progress": 50.0,
  "executions": [
    {
      "execution_id": "exec_001",
      "status": "completed"
    },
    {
      "execution_id": "exec_002",
      "status": "running"
    }
  ]
}
```

## Analytics API

### Get Analytics
Retrieve platform analytics and metrics.

```http
GET /analytics?range=7d
```

**Response:**
```json
{
  "time_range": "7d",
  "course_creation": {
    "total_courses": 45,
    "completed_courses": 38,
    "success_rate": 84.4,
    "average_duration": "2.5 hours"
  },
  "workflow_execution": {
    "total_executions": 156,
    "successful_executions": 142,
    "failed_executions": 14,
    "success_rate": 91.0
  },
  "user_activity": {
    "active_users": 23,
    "new_users": 5,
    "total_sessions": 89
  }
}
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "validation_error",
  "message": "Invalid request parameters",
  "details": {
    "field": "title",
    "issue": "Title is required"
  }
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate limited:
- General endpoints: 100 requests per minute
- Course creation: 10 requests per minute
- Batch operations: 5 requests per minute

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## Webhooks

Configure webhooks to receive real-time notifications:

```http
POST /webhooks/configure
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": [
    "course.created",
    "workflow.completed",
    "approval.required"
  ],
  "secret": "your-webhook-secret"
}
```

### Webhook Events

#### Course Created
```json
{
  "event": "course.created",
  "data": {
    "execution_id": "exec_123",
    "course_title": "Python Basics",
    "status": "completed"
  },
  "timestamp": "2024-01-15T12:00:00Z"
}
```

#### Approval Required
```json
{
  "event": "approval.required",
  "data": {
    "approval_id": "approval_456",
    "execution_id": "exec_123",
    "type": "outline_review",
    "expires_at": "2024-01-16T12:00:00Z"
  },
  "timestamp": "2024-01-15T12:00:00Z"
}
```

## SDK and Libraries

### Python SDK
```python
from courzly import CourzlyClient

client = CourzlyClient(
    api_url="https://your-domain.com/api/v1",
    auth_token="your-jwt-token"
)

# Create course
course = client.courses.create({
    "title": "Python Basics",
    "description": "Learn Python programming",
    "difficulty_level": "beginner"
})

# Monitor progress
status = client.executions.get_status(course.execution_id)
```

### JavaScript SDK
```javascript
import { CourzlyClient } from '@courzly/sdk';

const client = new CourzlyClient({
  apiUrl: 'https://your-domain.com/api/v1',
  authToken: 'your-jwt-token'
});

// Create course
const course = await client.courses.create({
  title: 'Python Basics',
  description: 'Learn Python programming',
  difficulty_level: 'beginner'
});

// Monitor progress
const status = await client.executions.getStatus(course.execution_id);
```

## Testing

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00Z",
  "services": {
    "database": "connected",
    "flowise": "connected",
    "redis": "connected"
  }
}
```

### API Testing
Use the provided Postman collection or OpenAPI specification for testing:
- Postman Collection: `/docs/postman/courzly-api.json`
- OpenAPI Spec: `https://your-domain.com/api/v1/openapi.json`