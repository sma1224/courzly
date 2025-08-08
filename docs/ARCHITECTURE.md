# Courzly System Architecture

## Overview

Courzly is a production-ready Dynamic Agent Platform for Course Creation that combines AI-powered content generation with human-in-the-loop workflows. The system is built using modern microservices architecture with containerized deployment.

## System Components

### Frontend Layer
- **Technology**: React 18 + TypeScript
- **Features**: WYSIWYG editor, real-time chat, approval dashboards
- **State Management**: React Query for server state, React Context for auth
- **Styling**: Tailwind CSS with custom components
- **Real-time**: WebSocket integration for live updates

### Backend Layer
- **Framework**: FastAPI (Python 3.11)
- **Workflow Engine**: LangGraph for state management
- **AI Integration**: OpenAI GPT-4 for content generation
- **Authentication**: JWT with role-based access control
- **API Design**: RESTful endpoints + WebSocket for real-time features

### Data Layer
- **Primary Database**: PostgreSQL 15 with persistent volumes
- **Cache/Sessions**: Redis 7 with persistence enabled
- **File Storage**: Docker volumes for uploads and media
- **Backup Strategy**: Automated daily backups with retention

### Infrastructure Layer
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx with SSL termination
- **SSL/TLS**: Let's Encrypt with auto-renewal
- **Monitoring**: Prometheus + Grafana dashboards
- **Security**: UFW firewall + fail2ban + rate limiting

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Monitoring    │    │   Backup System │
│     (Nginx)     │    │ (Prometheus +   │    │   (Automated)   │
│                 │    │   Grafana)      │    │                 │
└─────────┬───────┘    └─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐
│   Frontend      │
│   (React TS)    │
│   Port: 3000    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Backend API   │◄──►│   WebSocket     │◄──►│   AI Agents     │
│   (FastAPI)     │    │   Manager       │    │   (LangGraph)   │
│   Port: 8000    │    │                 │    │                 │
└─────────┬───────┘    └─────────────────┘    └─────────────────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │
│   Port: 5432    │    │   Port: 6379    │
│   (Persistent)  │    │  (Persistent)   │
└─────────────────┘    └─────────────────┘
```

## Data Flow

### Course Creation Workflow
1. **User Input** → Frontend form submission
2. **API Request** → FastAPI validates and creates workflow
3. **LangGraph** → Initiates course generation state machine
4. **AI Agents** → Generate outline using OpenAI GPT-4
5. **Database** → Store generated content and checkpoint
6. **WebSocket** → Notify frontend of status update
7. **Human Review** → User approves/rejects via HITL interface
8. **Iteration** → Repeat for content generation, review, assembly
9. **Export** → Generate final course in multiple formats

### Real-time Communication
1. **WebSocket Connection** → Client connects to workflow channel
2. **Message Broadcasting** → Server broadcasts to all connected clients
3. **AI Integration** → Chat messages trigger AI responses
4. **State Synchronization** → All clients receive live updates

## Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Role-based Access**: Admin, Editor, Reviewer, Viewer roles
- **API Security**: All endpoints protected with middleware
- **Session Management**: Redis-based session storage

### Network Security
- **HTTPS Only**: SSL/TLS encryption for all traffic
- **Rate Limiting**: API and auth endpoint protection
- **Firewall**: UFW with minimal open ports (22, 80, 443)
- **Intrusion Prevention**: fail2ban for automated blocking

### Data Security
- **Encryption at Rest**: Database and file encryption
- **Secure Headers**: XSS, CSRF, clickjacking protection
- **Input Validation**: Pydantic models for all API inputs
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

## Scalability Design

### Horizontal Scaling
- **Stateless Backend**: Multiple FastAPI instances behind load balancer
- **Database Scaling**: Read replicas and connection pooling
- **Redis Clustering**: High availability cache layer
- **CDN Integration**: Static asset delivery optimization

### Performance Optimization
- **Database Indexing**: Optimized queries with proper indexes
- **Caching Strategy**: Redis for session, API responses, and chat history
- **Async Processing**: Background tasks for AI generation
- **Connection Pooling**: Efficient database connection management

## Monitoring & Observability

### Metrics Collection
- **Application Metrics**: Request rates, response times, error rates
- **Business Metrics**: Workflow completion rates, user engagement
- **System Metrics**: CPU, memory, disk usage, network traffic
- **Custom Metrics**: AI generation times, approval rates

### Logging Strategy
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARN, ERROR with proper categorization
- **Log Aggregation**: Centralized logging with retention policies
- **Security Logging**: Authentication attempts, authorization failures

### Alerting
- **Threshold Alerts**: CPU, memory, disk space warnings
- **Error Rate Alerts**: API error rate monitoring
- **Business Alerts**: Workflow failure notifications
- **Health Checks**: Service availability monitoring

## Deployment Architecture

### Container Strategy
- **Multi-stage Builds**: Optimized Docker images
- **Health Checks**: Container-level health monitoring
- **Resource Limits**: CPU and memory constraints
- **Restart Policies**: Automatic recovery from failures

### Environment Management
- **Configuration**: Environment variables for all settings
- **Secrets Management**: Secure handling of API keys and passwords
- **Environment Separation**: Dev, staging, production isolation
- **Feature Flags**: Runtime configuration changes

### CI/CD Pipeline
- **Automated Testing**: Unit, integration, and E2E tests
- **Code Quality**: Linting, formatting, security scanning
- **Automated Deployment**: GitHub Actions with EC2 deployment
- **Rollback Strategy**: Quick reversion to previous versions

## Data Architecture

### Database Design
- **Normalized Schema**: Efficient relational design
- **Audit Trails**: Complete change history tracking
- **Soft Deletes**: Data retention for compliance
- **Indexing Strategy**: Query optimization with proper indexes

### Data Flow
- **CRUD Operations**: RESTful API design patterns
- **Event Sourcing**: Workflow state change tracking
- **Data Validation**: Multi-layer validation (frontend, API, database)
- **Backup Strategy**: Automated backups with point-in-time recovery

## Integration Architecture

### External APIs
- **OpenAI Integration**: GPT-4 for content generation
- **Google Drive**: OAuth-based file synchronization
- **Email Services**: Notification and alert delivery
- **Analytics**: Usage tracking and reporting

### Webhook Support
- **Event Notifications**: Workflow status changes
- **Integration Points**: Third-party system connectivity
- **Retry Logic**: Reliable delivery mechanisms
- **Security**: Signed webhook payloads

## Disaster Recovery

### Backup Strategy
- **Database Backups**: Daily automated PostgreSQL dumps
- **File Backups**: User uploads and generated content
- **Configuration Backups**: System settings and certificates
- **Retention Policy**: 30-day backup retention with archival

### Recovery Procedures
- **RTO Target**: 4 hours maximum downtime
- **RPO Target**: 1 hour maximum data loss
- **Failover Process**: Documented recovery procedures
- **Testing**: Regular disaster recovery drills

## Performance Characteristics

### Response Times
- **API Endpoints**: < 200ms average response time
- **AI Generation**: 30-60 seconds for outline, 2-5 minutes for content
- **WebSocket**: < 50ms message delivery
- **Database Queries**: < 100ms for complex queries

### Throughput
- **Concurrent Users**: 100+ simultaneous users
- **API Requests**: 1000+ requests per minute
- **WebSocket Connections**: 500+ concurrent connections
- **Workflow Processing**: 10+ concurrent workflows

### Resource Requirements
- **Minimum**: 4GB RAM, 2 CPU cores, 20GB storage
- **Recommended**: 8GB RAM, 4 CPU cores, 50GB storage
- **Production**: 16GB RAM, 8 CPU cores, 100GB storage
- **Scaling**: Linear scaling with additional resources