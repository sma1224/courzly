# Approval Workflow Deployment Instructions

## 🔒 Safe Deployment Process

### Step 1: Backup Current Backend
```bash
# SSH to server
ssh root@agent01.digitz.cloud

# Navigate to project
cd /opt/courzly

# Create backup
cp -r backend backend_backup_$(date +%Y%m%d_%H%M%S)

# Stop backend container
docker compose stop backend
```

### Step 2: Deploy New Backend
```bash
# Copy the approval-backend-update.tar.gz to server
scp approval-backend-update.tar.gz root@agent01.digitz.cloud:/opt/courzly/

# SSH to server
ssh root@agent01.digitz.cloud

# Extract new backend
cd /opt/courzly
tar -xzf approval-backend-update.tar.gz

# Restart backend container
docker compose up -d backend
```

### Step 3: Verify Deployment
```bash
# Check if backend is running
docker compose ps

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Test approval workflow endpoint
curl http://localhost:8000/api/hitl/test/pending-approvals
```

### Step 4: Test Approval Demo
Visit: `http://agent01.digitz.cloud:8000/agents/approval_demo.html`

## 🔄 Rollback (if needed)
```bash
# Stop current backend
docker compose stop backend

# Restore backup
rm -rf backend
mv backend_backup_YYYYMMDD_HHMMSS backend

# Restart
docker compose up -d backend
```

## 📋 What's Being Deployed
- ✅ HITL API endpoints (`/api/hitl/`)
- ✅ Approval workflow logic
- ✅ Database models for approvals
- ✅ Frontend approval dashboard
- ✅ WebSocket integration
- ✅ Demo page for testing

The approval workflow will be fully functional after deployment!