#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Courzly deployment on Ubuntu 24.04...${NC}"

# Check if running as root (common on EC2)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Running as root. Creating courzly user...${NC}"
    useradd -m -s /bin/bash courzly 2>/dev/null || true
    usermod -aG sudo courzly 2>/dev/null || true
    usermod -aG docker courzly 2>/dev/null || true
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${RED}❌ Please configure .env file with your settings and run again.${NC}"
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=("POSTGRES_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY" "OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required environment variable $var is not set${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment variables validated${NC}"

# Install system dependencies
echo -e "${BLUE}📦 Installing system dependencies...${NC}"
./scripts/setup/install-dependencies.sh

# Apply Docker group changes without logout
echo -e "${BLUE}🔄 Applying Docker group changes...${NC}"
newgrp docker << EONG
# Setup SSL certificates
echo -e "${BLUE}🔐 Setting up SSL certificates...${NC}"
if [ -n "$DOMAIN" ]; then
    ./scripts/setup/ssl-setup.sh "$DOMAIN" "$EMAIL"
else
    ./scripts/setup/ssl-setup.sh
fi

# Create necessary directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p logs backups uploads

# Set proper permissions
chmod 755 logs backups uploads

# Build and start services
echo -e "${BLUE}🐳 Building and starting Docker services...${NC}"
docker-compose down --remove-orphans 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 45

# Check service health with retries
echo -e "${BLUE}🏥 Checking service health...${NC}"
max_attempts=60
attempt=1

while [ \$attempt -le \$max_attempts ]; do
    if curl -f -s -k https://localhost/system/health > /dev/null 2>&1 || curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend service is healthy${NC}"
        break
    fi
    
    if [ \$attempt -eq \$max_attempts ]; then
        echo -e "${RED}❌ Backend service failed to start${NC}"
        echo -e "${YELLOW}📋 Service status:${NC}"
        docker-compose ps
        echo -e "${YELLOW}📋 Backend logs:${NC}"
        docker-compose logs --tail=50 backend
        exit 1
    fi
    
    echo -e "${YELLOW}⏳ Attempt \$attempt/\$max_attempts - waiting for backend...${NC}"
    sleep 10
    ((attempt++))
done

# Setup monitoring dashboards
echo -e "${BLUE}📊 Setting up monitoring dashboards...${NC}"
sleep 15

# Check Grafana
if curl -f -s http://localhost:3001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Grafana is ready${NC}"
else
    echo -e "${YELLOW}⚠️  Grafana not ready, will be available shortly${NC}"
fi

# Setup backup cron job
echo -e "${BLUE}💾 Setting up automated backups...${NC}"
(crontab -l 2>/dev/null; echo "0 2 * * * cd $(pwd) && ./scripts/backup.sh") | crontab -

# Final status check
echo -e "${BLUE}🔍 Final system check...${NC}"
docker-compose ps

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}📋 Service URLs:${NC}"
if [ -n "$DOMAIN" ]; then
    echo -e "  Frontend: https://$DOMAIN"
    echo -e "  API: https://$DOMAIN/api"
else
    echo -e "  Frontend: https://localhost (self-signed cert)"
    echo -e "  API: https://localhost/api"
fi
echo -e "  Grafana: http://localhost:3001 (admin/\$GRAFANA_PASSWORD)"
echo -e "  Prometheus: http://localhost:9090"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo -e "  1. Access the application at the frontend URL"
echo -e "  2. Create your first admin user"
echo -e "  3. Configure monitoring alerts in Grafana"
echo -e "  4. Review logs: docker-compose logs -f"
echo ""
echo -e "${GREEN}✅ Courzly is now running on Ubuntu 24.04!${NC}"
EONG