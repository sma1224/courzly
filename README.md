# Courzly - Dynamic Agent Platform for Course Creation

Production-ready AI-powered course creation platform with human-in-the-loop workflows, real-time collaboration, and multi-stage approval processes.

## Architecture

- **Backend**: FastAPI + LangGraph for workflow orchestration
- **Frontend**: React TypeScript with WYSIWYG editing
- **Database**: PostgreSQL with persistent volumes
- **Cache/Sessions**: Redis with persistence
- **Monitoring**: Prometheus + Grafana
- **Deployment**: Docker Compose + Nginx + SSL

## Quick Start

```bash
# Clone and setup
git clone https://github.com/sma1224/courzly.git
cd courzly

# Deploy to EC2 (single command)
./scripts/deploy/deploy.sh

# Local development
docker-compose up -d
```

## Features

- Multi-stage course workflows with AI agents
- Human-in-the-loop editing and approval
- Real-time chat and collaboration
- Rich text editing with version control
- Export to multiple formats (PDF, SCORM, etc.)
- Google Drive integration
- Comprehensive monitoring and backup

## API Endpoints

- `POST /api/workflows/course/create` - Create course workflow
- `GET /api/workflows/{id}/status` - Get workflow status
- `WebSocket /ws/chat/{workflow_id}` - Real-time chat
- `POST /api/workflows/{id}/approve` - Approve checkpoint

## Development

See [docs/](./docs/) for detailed documentation.