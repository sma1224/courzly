# Courzly Documentation

Welcome to the Courzly documentation! This directory contains comprehensive guides for users, developers, and system administrators.

## Quick Links

### For Users
- **[User Manual](USER_MANUAL.md)** - Complete guide to using Courzly
- **[Getting Started](#getting-started)** - Quick start guide

### For Developers
- **[API Documentation](api/README.md)** - Complete API reference
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to Courzly
- **[Architecture Overview](ARCHITECTURE.md)** - System design and architecture

### For Administrators
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[System Architecture](ARCHITECTURE.md)** - Technical architecture details

## Getting Started

### What is Courzly?

Courzly is a production-ready Dynamic Agent Platform for Course Creation that combines AI-powered content generation with human-in-the-loop workflows. It enables educators and content creators to build high-quality courses efficiently by leveraging AI assistance while maintaining human oversight and control.

### Key Features

- 🤖 **AI-Powered Generation**: Automated course outline and content creation using GPT-4
- 👥 **Human-in-the-Loop**: Review, edit, and approve content at every stage
- 💬 **Real-time Collaboration**: Chat with AI assistant and collaborate with team members
- 📝 **Rich Text Editing**: WYSIWYG editor with version control
- 📊 **Approval Workflows**: Multi-stage approval process with audit trails
- 📤 **Multi-format Export**: PDF, HTML, SCORM, and Markdown export options
- 🔒 **Enterprise Security**: JWT authentication, role-based access, SSL/TLS
- 📈 **Monitoring & Analytics**: Comprehensive system monitoring and usage analytics

### Quick Start

#### For End Users
1. **Access Courzly**: Navigate to your Courzly instance
2. **Login**: Use your credentials to access the platform
3. **Create Course**: Click "New Course" and fill in details
4. **Review & Approve**: Guide the AI through each stage
5. **Export**: Download your completed course materials

#### For Developers
```bash
# Clone repository
git clone https://github.com/sma1224/courzly.git
cd courzly

# Setup development environment
cp .env.example .env
docker-compose up -d

# Run tests
./scripts/test.sh
```

#### For System Administrators
```bash
# Deploy to EC2 (Ubuntu 24.04)
curl -fsSL https://raw.githubusercontent.com/sma1224/courzly/main/scripts/setup/ec2-init.sh | bash
cd /opt/courzly
sudo nano .env  # Configure settings
./scripts/deploy/deploy.sh
```

## Documentation Structure

### User Documentation
- **[User Manual](USER_MANUAL.md)** - Complete user guide with screenshots and examples
- **Tutorials** - Step-by-step tutorials for common tasks
- **FAQ** - Frequently asked questions and troubleshooting

### Developer Documentation
- **[API Reference](api/README.md)** - Complete REST API and WebSocket documentation
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup and contribution guidelines
- **Code Examples** - SDK examples and integration patterns
- **Testing Guide** - Testing strategies and best practices

### Administrator Documentation
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment and configuration
- **[Architecture Guide](ARCHITECTURE.md)** - System architecture and design decisions
- **Operations Guide** - Monitoring, backup, and maintenance procedures
- **Security Guide** - Security configuration and best practices

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 24.04 LTS (or compatible Linux distribution)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum, 50GB recommended
- **CPU**: 2 cores minimum, 4 cores recommended
- **Network**: Stable internet connection for AI API calls

### Software Dependencies
- **Docker**: 24.0+ with Docker Compose
- **Node.js**: 18+ (for local development)
- **Python**: 3.11+ (for local development)
- **PostgreSQL**: 15+ (containerized)
- **Redis**: 7+ (containerized)

## Architecture Overview

```
Frontend (React TS) ←→ Backend (FastAPI) ←→ AI Agents (LangGraph)
        ↓                      ↓                    ↓
   User Interface      REST API + WebSocket    Content Generation
        ↓                      ↓                    ↓
   Authentication      Database (PostgreSQL)   Workflow Engine
        ↓                      ↓                    ↓
   Authorization       Cache (Redis)           State Management
```

### Core Components
- **Frontend**: React TypeScript with real-time updates
- **Backend**: FastAPI with async processing
- **Database**: PostgreSQL with Redis caching
- **AI Engine**: LangGraph with OpenAI GPT-4
- **Infrastructure**: Docker containers with Nginx proxy

## Support and Community

### Getting Help
1. **Documentation**: Check this documentation first
2. **GitHub Issues**: Report bugs and request features
3. **Discussions**: Community discussions and Q&A
4. **Email Support**: Contact support team for urgent issues

### Contributing
We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for:
- Development setup instructions
- Code style guidelines
- Pull request process
- Issue reporting guidelines

### Security
For security-related issues, please email: security@courzly.com

## License

Courzly is released under the MIT License. See the [LICENSE](../LICENSE) file for details.

## Changelog

See [CHANGELOG.md](../CHANGELOG.md) for version history and release notes.

## Acknowledgments

- **OpenAI** - For GPT-4 API powering content generation
- **LangGraph** - For workflow orchestration framework
- **FastAPI** - For high-performance Python web framework
- **React** - For modern frontend development
- **Contributors** - All community contributors and maintainers

---

**Need help?** Check our [User Manual](USER_MANUAL.md) or open an issue on GitHub!