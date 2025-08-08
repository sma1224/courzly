#!/bin/bash
set -e

echo "🚀 Initializing Courzly on EC2 Ubuntu 24.04..."

# Update system first
sudo apt-get update -y

# Install git if not present
sudo apt-get install -y git

# Clone repository if not exists
if [ ! -d "/opt/courzly" ]; then
    echo "📥 Cloning Courzly repository..."
    sudo git clone https://github.com/sma1224/courzly.git /opt/courzly
    sudo chown -R ubuntu:ubuntu /opt/courzly
fi

cd /opt/courzly

# Create .env from template
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚙️ Created .env file - please configure it before deployment"
fi

# Make scripts executable
chmod +x scripts/setup/*.sh scripts/deploy/*.sh scripts/*.sh

echo "✅ EC2 initialization complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit /opt/courzly/.env with your configuration"
echo "2. Run: cd /opt/courzly && ./scripts/deploy/deploy.sh"
echo ""
echo "🔧 Required .env variables:"
echo "  - POSTGRES_PASSWORD"
echo "  - REDIS_PASSWORD" 
echo "  - SECRET_KEY"
echo "  - OPENAI_API_KEY"
echo "  - DOMAIN (your EC2 public DNS or domain)"
echo "  - EMAIL (for Let's Encrypt)"