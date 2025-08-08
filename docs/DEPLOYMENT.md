# Courzly Deployment Guide

## Quick Deployment (EC2)

### Prerequisites
- Ubuntu 24.04 EC2 instance
- Domain name (optional, for SSL)
- OpenAI API key

### One-Command Deployment
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Initialize and deploy
curl -fsSL https://raw.githubusercontent.com/sma1224/courzly/main/scripts/setup/ec2-init.sh | bash
cd /opt/courzly
sudo nano .env  # Configure your settings
./scripts/deploy/deploy.sh
```

## Manual Deployment

### 1. System Requirements
- **OS**: Ubuntu 24.04 LTS
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum
- **CPU**: 2 cores minimum

### 2. Environment Setup

#### Clone Repository
```bash
git clone https://github.com/sma1224/courzly.git
cd courzly
```

#### Configure Environment
```bash
cp .env.example .env
nano .env
```

**Required Environment Variables**:
```bash
# Database
POSTGRES_PASSWORD=secure_random_password

# Redis
REDIS_PASSWORD=secure_random_password

# Application
SECRET_KEY=your-secret-key-min-32-chars
OPENAI_API_KEY=sk-your-openai-api-key

# Domain (for SSL)
DOMAIN=your-domain.com
EMAIL=your-email@domain.com

# Monitoring
GRAFANA_PASSWORD=admin_password
```

### 3. Installation Steps

#### Install Dependencies
```bash
./scripts/setup/install-dependencies.sh
```

#### Setup SSL Certificates
```bash
# For production with domain
./scripts/setup/ssl-setup.sh your-domain.com your-email@domain.com

# For local development
./scripts/setup/ssl-setup.sh
```

#### Deploy Services
```bash
./scripts/deploy/deploy.sh
```

### 4. Verification

#### Check Service Status
```bash
docker-compose ps
```

#### Test Endpoints
```bash
# Health check
curl -k https://localhost/system/health

# API status
curl -k https://localhost/api/auth/login
```

#### Access Services
- **Frontend**: https://your-domain.com
- **API**: https://your-domain.com/api
- **Grafana**: http://your-domain.com:3001
- **Prometheus**: http://your-domain.com:9090

## Production Configuration

### Security Hardening

#### Firewall Setup
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

#### SSL Configuration
- Automatic Let's Encrypt certificates
- Auto-renewal via cron
- HTTPS redirect enforced

#### Rate Limiting
- API: 10 req/sec per IP
- Auth: 5 req/sec per IP
- Configurable in `configs/nginx.conf`

### Monitoring Setup

#### Prometheus Metrics
- HTTP request metrics
- Database operations
- Workflow statistics
- System resources

#### Grafana Dashboards
- System overview
- Application metrics
- Error tracking
- Performance monitoring

### Backup Strategy

#### Automated Backups
```bash
# Daily backups at 2 AM
crontab -e
0 2 * * * /opt/courzly/scripts/backup.sh
```

#### Manual Backup
```bash
./scripts/backup.sh
```

#### Restore from Backup
```bash
# Stop services
docker-compose down

# Restore database
docker-compose exec postgres psql -U courzly -d courzly < backup_file.sql

# Restore files
tar -xzf backup_uploads.tar.gz

# Start services
docker-compose up -d
```

## Scaling & Performance

### Horizontal Scaling

#### Load Balancer Setup
```nginx
upstream courzly_backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

#### Database Scaling
- Read replicas for PostgreSQL
- Redis Cluster for high availability
- Connection pooling optimization

### Performance Optimization

#### Database Tuning
```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
```

#### Redis Configuration
```bash
# Memory optimization
maxmemory 512mb
maxmemory-policy allkeys-lru
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check disk space
df -h

# Check memory
free -h
```

#### SSL Certificate Issues
```bash
# Renew certificates
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Check connections
docker-compose exec postgres psql -U courzly -c "SELECT * FROM pg_stat_activity;"
```

### Log Locations
- **Application**: `docker-compose logs -f`
- **Nginx**: `/var/log/nginx/`
- **System**: `/var/log/syslog`
- **Backup**: `./logs/backup.log`

### Performance Monitoring
```bash
# System resources
htop

# Docker stats
docker stats

# Database performance
docker-compose exec postgres psql -U courzly -c "SELECT * FROM pg_stat_statements;"
```

## Maintenance

### Regular Tasks

#### Weekly
- Review system logs
- Check backup integrity
- Monitor disk usage
- Update security patches

#### Monthly
- Review performance metrics
- Optimize database queries
- Clean old backups
- Update dependencies

### Updates

#### Application Updates
```bash
cd /opt/courzly
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

#### System Updates
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot  # If kernel updates
```

## Support

### Health Checks
- **System**: `/system/health`
- **Database**: Automatic monitoring
- **Services**: Docker health checks

### Monitoring Alerts
- Configure Grafana alerts
- Email notifications
- Slack integration available

### Backup Verification
```bash
# Test backup integrity
./scripts/test-backup.sh backup_file.tar.gz
```