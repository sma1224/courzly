from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uuid

app = FastAPI()

@app.get("/approval_demo.html", response_class=HTMLResponse)
async def approval_demo():
    return """<!DOCTYPE html>
<html>
<head><title>Approval Demo</title></head>
<body>
<h1>Approval Workflow Test</h1>
<button onclick="testWorkflow()">Test Workflow</button>
<div id="result"></div>
<script>
async function testWorkflow() {
    document.getElementById('result').innerHTML = 'Testing workflow creation...';
    try {
        const response = await fetch('/test-workflow', {method: 'POST'});
        const data = await response.json();
        document.getElementById('result').innerHTML = JSON.stringify(data, null, 2);
    } catch (e) {
        document.getElementById('result').innerHTML = 'Error: ' + e.message;
    }
}
</script>
</body>
</html>"""

@app.post("/test-workflow")
async def test_workflow():
    return {
        "workflow_id": str(uuid.uuid4()),
        "status": "created",
        "message": "Test workflow created successfully"
    }