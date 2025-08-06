# Courzly Production Deployment Guide

This guide provides comprehensive instructions for deploying the Courzly Dynamic Agent Platform to AWS EC2.

## Prerequisites

### System Requirements
- AWS EC2 instance (m7i-flex.large or larger)
- Ubuntu 22.04 LTS
- 8GB RAM minimum
- 50GB storage minimum
- Domain name with DNS access

### Required Software
- Docker Engine 24.0+
- Docker Compose 2.0+
- Git
- Nginx (handled by container)
- Certbot (for SSL certificates)

## Quick Deployment

### 1. Clone Repository
```bash
git clone https://github.com/sma1224/courzly.git
cd courzly
```

### 2. Run Deployment Script
```bash
# Set your domain
export DOMAIN=your-domain.com

# Run deployment
./scripts/deploy/production.sh
```

The script will automatically:
- Install dependencies
- Generate SSL certificates
- Build Docker images
- Deploy all services
- Setup monitoring and backups

## Manual Deployment Steps

### 1. Environment Setup

Create production environment file:
```bash
cp .env.example .env.production
```

Edit `.env.production` with your configuration:
```env
# Database Configuration
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_password

# API Configuration
API_SECRET_KEY=your_secret_key
SENDGRID_API_KEY=your_sendgrid_key

# Flowise Configuration
FLOWISE_USERNAME=admin
FLOWISE_PASSWORD=your_secure_password

# Domain Configuration
DOMAIN=your-domain.com

# Google Drive Integration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 2. SSL Certificate Setup

```bash
# Install certbot
sudo apt-get update
sudo apt-get install -y certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo mkdir -p /opt/courzly/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/courzly/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/courzly/ssl/key.pem
```

### 3. Build and Deploy

```bash
# Build images
docker build -f backend/api/Dockerfile.prod -t courzly/api:latest backend/api/
docker build -f frontend/Dockerfile.prod -t courzly/frontend:latest frontend/

# Deploy services
cd docker/production
docker-compose up -d
```

### 4. Verify Deployment

```bash
# Check service status
docker-compose ps

# Test API health
curl https://your-domain.com/api/v1/health

# Check logs
docker-compose logs -f
```

## Service Architecture

### Core Services
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Flowise**: AI workflow engine
- **API**: FastAPI backend
- **Frontend**: React application
- **Nginx**: Reverse proxy and SSL termination

### Monitoring Services
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

## Configuration Details

### Database Configuration
```yaml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: courzly
    POSTGRES_USER: courzly_user
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

### API Configuration
```yaml
api:
  environment:
    - DATABASE_URL=postgresql://courzly_user:${POSTGRES_PASSWORD}@postgres:5432/courzly
    - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
    - FLOWISE_URL=http://flowise:3000
```

### Nginx Configuration
- SSL termination with Let's Encrypt certificates
- Rate limiting for API endpoints
- Security headers (HSTS, CSP, etc.)
- Gzip compression
- Static file caching

## Security Features

### SSL/TLS
- TLS 1.2+ only
- Strong cipher suites
- HSTS headers
- Perfect forward secrecy

### Application Security
- JWT authentication
- Rate limiting
- CORS configuration
- Input validation
- SQL injection protection

### Infrastructure Security
- Non-root containers
- Network isolation
- Firewall configuration
- Regular security updates

## Monitoring and Logging

### Prometheus Metrics
- Application performance metrics
- System resource usage
- Custom business metrics
- Alert rules

### Grafana Dashboards
- System overview
- Application performance
- Course creation metrics
- Error tracking

### Log Management
- Centralized logging
- Log rotation
- Error alerting
- Audit trails

## Backup and Recovery

### Automated Backups
```bash
# Database backup
docker-compose exec postgres pg_dump -U courzly_user courzly > backup.sql

# Flowise data backup
docker cp courzly-flowise:/root/.flowise ./flowise-backup

# Configuration backup
tar -czf config-backup.tar.gz .env ssl/
```

### Backup Schedule
- Daily database backups at 2 AM
- Weekly full system backups
- 30-day retention policy
- Offsite backup storage

### Recovery Procedures
1. Stop services: `docker-compose down`
2. Restore database: `psql -U courzly_user -d courzly < backup.sql`
3. Restore Flowise data: `docker cp flowise-backup courzly-flowise:/root/.flowise`
4. Start services: `docker-compose up -d`

## Scaling Considerations

### Horizontal Scaling
- Load balancer configuration
- Database read replicas
- Redis clustering
- Container orchestration

### Performance Optimization
- Database indexing
- Query optimization
- Caching strategies
- CDN integration

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Check resource usage
docker stats

# Restart service
docker-compose restart service-name
```

#### SSL Certificate Issues
```bash
# Renew certificate
sudo certbot renew

# Update certificate in container
docker-compose restart nginx
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready

# Reset database connection
docker-compose restart api
```

### Health Checks
- API: `https://your-domain.com/api/v1/health`
- Flowise: `https://your-domain.com/flowise/api/v1/ping`
- Database: `docker-compose exec postgres pg_isready`

## Maintenance

### Regular Tasks
- Update Docker images
- Renew SSL certificates
- Monitor disk usage
- Review security logs
- Update dependencies

### Update Procedure
```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Update services
docker-compose up -d
```

## Support

For deployment issues:
1. Check the troubleshooting section
2. Review service logs
3. Consult the GitHub issues
4. Contact the development team

## Security Considerations

- Change all default passwords
- Configure firewall rules
- Enable fail2ban
- Regular security updates
- Monitor access logs
- Implement backup encryption