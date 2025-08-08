from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/approval_demo.html", response_class=HTMLResponse)
async def approval_demo():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Courzly Approval Workflow Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-3xl font-bold text-gray-900 mb-8">Courzly Approval Workflow Demo</h1>
            
            <div class="bg-white rounded-lg shadow p-6 mb-6">
                <h2 class="text-xl font-semibold mb-4">Test Controls</h2>
                <div class="flex space-x-4">
                    <button id="createWorkflow" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Create Test Workflow
                    </button>
                    <button id="checkApprovals" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                        Check Pending Approvals
                    </button>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold mb-4">Workflow Status</h3>
                    <div id="workflowStatus">
                        <p class="text-gray-500">No workflow created yet</p>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold mb-4">Pending Approvals</h3>
                    <div id="pendingApprovals">
                        <p class="text-gray-500">No pending approvals</p>
                    </div>
                </div>
            </div>

            <div class="bg-gray-900 text-green-400 rounded-lg p-4 mt-6">
                <h3 class="text-lg font-semibold mb-4 text-white">Console Logs</h3>
                <div id="logs" class="font-mono text-sm space-y-1 max-h-64 overflow-y-auto">
                    <p>Ready to test approval workflow...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = window.location.origin;
        let currentWorkflowId = null;

        function log(message, type = 'info') {
            const logs = document.getElementById('logs');
            const timestamp = new Date().toLocaleTimeString();
            const colors = {
                info: 'text-green-400',
                error: 'text-red-400',
                success: 'text-blue-400'
            };
            
            const logEntry = document.createElement('p');
            logEntry.className = colors[type] || 'text-green-400';
            logEntry.textContent = `[${timestamp}] ${message}`;
            logs.appendChild(logEntry);
            logs.scrollTop = logs.scrollHeight;
        }

        async function createWorkflow() {
            try {
                log('Creating test workflow...', 'info');
                
                const response = await fetch(`${API_BASE}/api/workflows/course/create`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        title: 'Demo Course - Approval Test',
                        description: 'Testing approval workflow',
                        config: { course_topic: 'Web Development' }
                    })
                });

                if (response.ok) {
                    const workflow = await response.json();
                    currentWorkflowId = workflow.id;
                    log(`Workflow created: ${workflow.id}`, 'success');
                    
                    document.getElementById('workflowStatus').innerHTML = `
                        <p><strong>ID:</strong> ${workflow.id}</p>
                        <p><strong>Status:</strong> ${workflow.status}</p>
                        <p><strong>Stage:</strong> ${workflow.current_stage}</p>
                    `;
                } else {
                    log('Failed to create workflow', 'error');
                }
            } catch (error) {
                log(`Error: ${error.message}`, 'error');
            }
        }

        async function checkApprovals() {
            if (!currentWorkflowId) {
                log('No workflow ID available', 'error');
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/api/hitl/${currentWorkflowId}/pending-approvals`);
                
                if (response.ok) {
                    const approvals = await response.json();
                    log(`Found ${approvals.length} pending approvals`, 'info');
                    
                    if (approvals.length > 0) {
                        document.getElementById('pendingApprovals').innerHTML = approvals.map(a => `
                            <div class="border rounded p-2 mb-2">
                                <p class="font-medium">${a.stage}</p>
                                <p class="text-sm text-gray-600">${a.checkpoint_id}</p>
                            </div>
                        `).join('');
                    }
                } else {
                    log('Failed to check approvals', 'error');
                }
            } catch (error) {
                log(`Error: ${error.message}`, 'error');
            }
        }

        document.getElementById('createWorkflow').addEventListener('click', createWorkflow);
        document.getElementById('checkApprovals').addEventListener('click', checkApprovals);
    </script>
</body>
</html>"""