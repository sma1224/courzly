#!/bin/bash
set -e

echo "🚀 Installing system dependencies for Ubuntu 24.04 Noble..."

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install essential packages
sudo apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban \
    snapd

# Install Docker (Ubuntu 24.04 compatible)
echo "📦 Installing Docker..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu noble stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Install Docker Compose standalone (for compatibility)
echo "🐳 Installing Docker Compose..."
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Install Node.js 18 (Ubuntu 24.04 compatible)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python 3.12 (default in Ubuntu 24.04)
echo "🐍 Installing Python..."
sudo apt-get install -y python3 python3-pip python3-venv python3-dev

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Configure fail2ban
echo "🛡️ Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Start and enable Docker
sudo systemctl enable docker
sudo systemctl start docker

echo "✅ System dependencies installed successfully!"
echo "⚠️  Please log out and back in for Docker group changes to take effect."
echo "🔄 Or run: newgrp docker"