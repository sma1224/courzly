#!/bin/bash

# Courzly Production Deployment Script
# This script deploys the complete Courzly platform to EC2

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEPLOY_ENV="${DEPLOY_ENV:-production}"
DOMAIN="${DOMAIN:-courzly.example.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    log_success "System requirements check passed"
}

# Setup environment variables
setup_environment() {
    log_info "Setting up environment variables..."
    
    ENV_FILE="$PROJECT_ROOT/.env.production"
    
    if [[ ! -f "$ENV_FILE" ]]; then
        log_warning "Production environment file not found. Creating template..."
        
        cat > "$ENV_FILE" << EOF
# Database Configuration
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)

# API Configuration
API_SECRET_KEY=$(openssl rand -base64 64)
SENDGRID_API_KEY=your_sendgrid_api_key_here

# Flowise Configuration
FLOWISE_USERNAME=admin
FLOWISE_PASSWORD=$(openssl rand -base64 32)

# Monitoring Configuration
GRAFANA_PASSWORD=$(openssl rand -base64 32)

# Domain Configuration
DOMAIN=$DOMAIN

# Google Drive Integration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
EOF
        
        log_warning "Please edit $ENV_FILE with your actual configuration values"
        log_warning "Press Enter to continue after editing the file..."
        read -r
    fi
    
    # Source environment variables
    set -a
    source "$ENV_FILE"
    set +a
    
    log_success "Environment variables configured"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    sudo mkdir -p /opt/courzly/{data,logs,backups,ssl}
    sudo mkdir -p /opt/courzly/data/{postgres,redis,flowise,grafana,prometheus}
    sudo chown -R $USER:$USER /opt/courzly
    
    log_success "Directories created"
}

# Setup SSL certificates
setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    SSL_DIR="/opt/courzly/ssl"
    
    if [[ ! -f "$SSL_DIR/cert.pem" ]]; then
        log_info "Installing certbot..."
        sudo apt-get update
        sudo apt-get install -y certbot
        
        log_info "Generating SSL certificate for $DOMAIN..."
        sudo certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN"
        
        # Copy certificates to our directory
        sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
        sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"
        sudo chown $USER:$USER "$SSL_DIR"/*.pem
        
        # Setup auto-renewal
        echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
    fi
    
    log_success "SSL certificates configured"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build API image
    log_info "Building API image..."
    docker build -f backend/api/Dockerfile.prod -t courzly/api:latest backend/api/
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -f frontend/Dockerfile.prod -t courzly/frontend:latest frontend/
    
    log_success "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log_info "Deploying services..."
    
    cd "$PROJECT_ROOT/docker/production"
    
    # Copy environment file
    cp "$PROJECT_ROOT/.env.production" .env
    
    # Pull latest images
    docker-compose pull
    
    # Stop existing services
    docker-compose down
    
    # Start services
    docker-compose up -d
    
    log_success "Services deployed successfully"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
    
    log_success "Monitoring setup completed"
}

# Check service health
check_service_health() {
    log_info "Checking service health..."
    
    services=("postgres:5432" "redis:6379" "api:8000" "flowise:3000")
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        
        if docker-compose exec -T "$name" nc -z localhost "$port" 2>/dev/null; then
            log_success "$name service is healthy"
        else
            log_error "$name service is not responding"
            return 1
        fi
    done
    
    # Test API endpoint
    if curl -f http://localhost:8000/api/v1/health &>/dev/null; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi
}

# Setup backup
setup_backup() {
    log_info "Setting up backup system..."
    
    BACKUP_SCRIPT="/opt/courzly/backup.sh"
    
    cat > "$BACKUP_SCRIPT" << 'EOF'
#!/bin/bash

# Courzly Backup Script
BACKUP_DIR="/opt/courzly/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup database
docker-compose exec -T postgres pg_dump -U courzly_user courzly > "$BACKUP_DIR/$DATE/database.sql"

# Backup Flowise data
docker cp courzly-flowise:/root/.flowise "$BACKUP_DIR/$DATE/flowise"

# Backup configuration
cp -r /opt/courzly/ssl "$BACKUP_DIR/$DATE/"
cp .env "$BACKUP_DIR/$DATE/"

# Compress backup
tar -czf "$BACKUP_DIR/courzly_backup_$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"
rm -rf "$BACKUP_DIR/$DATE"

# Keep only last 7 backups
find "$BACKUP_DIR" -name "courzly_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: courzly_backup_$DATE.tar.gz"
EOF
    
    chmod +x "$BACKUP_SCRIPT"
    
    # Setup daily backup cron job
    (crontab -l 2>/dev/null; echo "0 2 * * * $BACKUP_SCRIPT") | crontab -
    
    log_success "Backup system configured"
}

# Setup log rotation
setup_log_rotation() {
    log_info "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/courzly > /dev/null << EOF
/opt/courzly/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        docker-compose restart nginx
    endscript
}
EOF
    
    log_success "Log rotation configured"
}

# Main deployment function
main() {
    log_info "Starting Courzly production deployment..."
    
    check_root
    check_requirements
    setup_environment
    create_directories
    setup_ssl
    build_images
    deploy_services
    setup_monitoring
    setup_backup
    setup_log_rotation
    
    log_success "Deployment completed successfully!"
    log_info "Access your application at: https://$DOMAIN"
    log_info "Grafana dashboard: https://$DOMAIN:3001"
    log_info "Flowise admin: https://$DOMAIN/flowise"
    
    # Display service status
    echo
    log_info "Service Status:"
    docker-compose ps
}

# Run main function
main "$@"