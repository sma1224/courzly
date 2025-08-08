#!/bin/bash
# Deploy approval workflow to server

SERVER="agent01.digitz.cloud"
USER="root"

echo "🚀 Deploying approval workflow to $SERVER..."

# Upload deployment package
echo "📦 Uploading backend code..."
scp approval-backend-update.tar.gz $USER@$SERVER:/opt/courzly/

# Deploy on server
echo "🔧 Deploying on server..."
ssh $USER@$SERVER << 'EOF'
cd /opt/courzly

# Backup existing backend
echo "📋 Creating backup..."
cp -r backend backend_backup_$(date +%Y%m%d_%H%M%S)

# Stop backend
echo "⏹️ Stopping backend..."
docker compose stop backend

# Extract new code
echo "📂 Extracting new backend..."
tar -xzf approval-backend-update.tar.gz

# Restart backend
echo "🔄 Starting backend..."
docker compose up -d backend

# Wait and test
sleep 5
echo "🧪 Testing deployment..."
curl -s http://localhost:8000/health

echo "✅ Deployment complete!"
echo "🌐 Access approval demo at: http://agent01.digitz.cloud:8000/agents/approval_demo.html"
EOF