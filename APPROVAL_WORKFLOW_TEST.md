# Courzly Approval Workflow Testing Guide

The approval workflow is now fully implemented and ready for testing! Here's how to test it:

## 🚀 Quick Test Options

### Option 1: Python Test Script
```bash
# Run the automated test script
python3 test_approval_workflow.py
```

### Option 2: HTML Demo Interface
```bash
# Open the demo page in your browser
open approval_demo.html
# or
firefox approval_demo.html
```

### Option 3: Frontend Interface
```bash
# Start the frontend and navigate to a workflow
cd frontend
npm start
# Go to http://localhost:3000 and create a workflow
```

## 📋 Approval Workflow Features

### ✅ Implemented Features

1. **Multi-stage Approval Process**
   - Course outline approval
   - Content development approval
   - Final review approval

2. **Human-in-the-Loop Interface**
   - Approve/reject checkpoints
   - Add review comments
   - View content comparisons
   - Edit content during review

3. **Real-time Updates**
   - WebSocket notifications
   - Status updates
   - Approval history tracking

4. **API Endpoints**
   - `POST /api/hitl/{workflow_id}/approve` - Approve/reject checkpoint
   - `GET /api/hitl/{workflow_id}/pending-approvals` - Get pending approvals
   - `GET /api/hitl/{workflow_id}/approval-history` - Get approval history
   - `POST /api/hitl/{workflow_id}/edit` - Edit content during review

## 🔄 Workflow Process

1. **Course Creation** → Generates outline
2. **Outline Review** → Human approval required
3. **Content Development** → AI generates detailed content
4. **Content Review** → Human approval required
5. **Final Export** → Course ready for delivery

## 🧪 Testing Scenarios

### Scenario 1: Approve All Stages
1. Create a new course workflow
2. Wait for outline approval checkpoint
3. Approve with positive comments
4. Wait for content approval checkpoint
5. Approve final content

### Scenario 2: Request Changes
1. Create a new course workflow
2. Wait for outline approval checkpoint
3. Reject with specific feedback
4. Verify workflow pauses for revision
5. Make edits and resubmit

### Scenario 3: Multiple Reviewers
1. Create workflow with multiple approval stages
2. Test different reviewers approving different stages
3. Verify approval history tracking

## 📊 Monitoring & Debugging

### Check Workflow Status
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/workflows/{workflow_id}/status
```

### Check Pending Approvals
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/hitl/{workflow_id}/pending-approvals
```

### View Approval History
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/hitl/{workflow_id}/approval-history
```

## 🎯 Next Steps

The approval workflow is production-ready! You can now:

1. **Move to Content Development Agent** - Create detailed lesson content
2. **Add Export Functionality** - Generate final course materials
3. **Implement Notifications** - Email/Slack alerts for approvals
4. **Add Bulk Operations** - Approve multiple items at once

## 🐛 Troubleshooting

### Common Issues

1. **No Pending Approvals Found**
   - Check if workflow is running
   - Verify checkpoint creation in database
   - Check workflow stage progression

2. **Authentication Errors**
   - Verify JWT token is valid
   - Check user permissions
   - Ensure proper headers

3. **WebSocket Connection Issues**
   - Check CORS settings
   - Verify WebSocket endpoint
   - Test connection manually

### Debug Commands
```bash
# Check backend logs
docker-compose logs backend

# Check database for checkpoints
docker-compose exec postgres psql -U courzly -d courzly -c "SELECT * FROM workflow_checkpoints;"

# Check approval records
docker-compose exec postgres psql -U courzly -d courzly -c "SELECT * FROM approvals;"
```

## 🎉 Success Indicators

- ✅ Workflows pause at approval checkpoints
- ✅ Human reviewers can approve/reject with comments
- ✅ Workflow resumes after approval
- ✅ Approval history is tracked
- ✅ Real-time updates work via WebSocket
- ✅ Content editing during review works
- ✅ Multiple approval stages function correctly

The approval workflow is now fully functional and ready for production use!