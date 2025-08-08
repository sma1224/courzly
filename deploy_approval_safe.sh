#!/bin/bash
# Safe deployment of approval workflow to containerized backend

echo "🔒 Creating backup and deploying approval workflow..."

# SSH to server and backup + deploy
ssh root@agent01.digitz.cloud << 'EOF'
cd /opt/courzly

# 1. Backup existing backend
echo "📦 Creating backup..."
cp -r backend backend_backup_$(date +%Y%m%d_%H%M%S)

# 2. Stop backend container
echo "⏹️ Stopping backend container..."
docker compose stop backend

# 3. Create deployment package locally
echo "📋 Current backend structure:"
ls -la backend/

echo "✅ Backup created. Ready for manual deployment."
echo "Next steps:"
echo "1. Copy new backend files to /opt/courzly/backend/"
echo "2. Run: docker compose up -d backend"
EOF