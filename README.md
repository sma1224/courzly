# Courzly - Dynamic Agent Platform for Course Creation

🎯 **Production-ready Dynamic Agent Execution Platform with specialized course creation focus**

## Overview

Courzly is a comprehensive platform that combines Flowise workflow automation with custom API layers and modern web interfaces to create an intelligent course creation system. The platform enables automated course generation through multi-stage approval workflows while providing universal agent configuration capabilities.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   FastAPI Layer │    │ Flowise Workflows│
│   - Course UI    │◄──►│   - Agent Config │◄──►│ - Course Creation│
│   - Approvals    │    │   - Templates    │    │ - AI Agents     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Tools     │    │   PostgreSQL    │    │  Google Drive   │
│   - Batch Ops   │    │   - Workflows   │    │  - Course Files │
│   - Automation  │    │   - User Data   │    │  - Organization │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Features

### 🎓 Course Creation System
- **Intelligent Requirements Gathering**: Dynamic questioning agents
- **Pedagogical Course Outlines**: Learning objectives and assessments
- **Human Approval Checkpoints**: Review and feedback integration
- **Detailed Content Generation**: 2000-3000 word lessons with assessments
- **Automated Organization**: Google Drive integration with folder management

### 🤖 Universal Agent Platform
- **JSON-based Configuration**: Universal agent definitions
- **Template Management**: Versioning and sharing capabilities
- **Batch Processing**: Enterprise-scale workflow execution
- **Real-time Monitoring**: Progress tracking and notifications
- **External Integrations**: Webhook system and API endpoints

### 🌐 Multi-Interface Access
- **Web Interface**: Modern React application with real-time collaboration
- **CLI Tools**: Command-line interface for automation and batch operations
- **REST API**: Comprehensive endpoints for external integrations

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ and Python 3.9+
- PostgreSQL and Redis
- SSL certificates for production

### Local Development
```bash
# Clone repository
git clone https://github.com/sma1224/courzly.git
cd courzly

# Start development environment
docker-compose up -d

# Install dependencies
npm install
pip install -r requirements.txt

# Start development servers
npm run dev        # Frontend
python -m api.main # Backend API
```

### Production Deployment
```bash
# Deploy to EC2
./scripts/deploy/production.sh

# Configure SSL
./scripts/setup/ssl-setup.sh

# Initialize database
./scripts/setup/db-init.sh
```

## Project Structure

```
courzly/
├── .github/workflows/     # CI/CD automation
├── backend/
│   ├── flowise/          # Flowise configurations
│   ├── api/              # Custom API layer
│   └── extensions/       # Custom Flowise extensions
├── frontend/
│   ├── src/              # React application
│   └── public/           # Static assets
├── cli/
│   └── src/              # Command-line tool
├── docker/               # Container configurations
├── scripts/
│   ├── deploy/           # Deployment automation
│   └── setup/            # Environment setup
├── docs/                 # Documentation
└── configs/              # Configuration files
```

## Documentation

- [API Documentation](docs/api/README.md)
- [Workflow Guides](docs/workflows/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [CLI Reference](docs/cli/README.md)

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please open an issue in the GitHub repository or contact the development team.