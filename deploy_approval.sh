#!/bin/bash
# Deploy approval workflow to server

echo "🚀 Deploying approval workflow..."

# Create deployment package
tar -czf approval-update.tar.gz \
  backend/main.py \
  backend/api/ \
  backend/models/ \
  backend/database/ \
  backend/middleware/ \
  backend/chat/ \
  backend/workflows/ \
  backend/requirements.txt \
  backend/agents/

# Copy to server
scp approval-update.tar.gz root@agent01.digitz.cloud:/opt/courzly/

# Deploy on server
ssh root@agent01.digitz.cloud << 'EOF'
cd /opt/courzly
tar -xzf approval-update.tar.gz
docker compose restart backend
echo "✅ Deployment complete"
EOF

echo "🎉 Approval workflow deployed!"