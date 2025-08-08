#!/usr/bin/env python3
"""
Test script for Courzly Approval Workflow
Demonstrates the human-in-the-loop approval process
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpass123"
}

class ApprovalWorkflowTester:
    def __init__(self):
        self.token = None
        self.workflow_id = None
        
    def authenticate(self):
        """Authenticate and get token"""
        response = requests.post(f"{API_BASE}/api/auth/login", json=TEST_USER)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print("✅ Authentication successful")
        else:
            print("❌ Authentication failed")
            return False
        return True
    
    def get_headers(self):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def create_workflow(self):
        """Create a test course workflow"""
        workflow_data = {
            "title": "Test Course - Approval Workflow",
            "description": "Testing the approval workflow functionality",
            "config": {
                "course_topic": "Python Programming Basics",
                "target_audience": "Beginners",
                "duration": "4 weeks"
            }
        }
        
        response = requests.post(
            f"{API_BASE}/api/workflows/course/create",
            json=workflow_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            self.workflow_id = response.json()["id"]
            print(f"✅ Workflow created: {self.workflow_id}")
            return True
        else:
            print(f"❌ Failed to create workflow: {response.text}")
            return False
    
    def wait_for_approval_checkpoint(self, timeout=60):
        """Wait for workflow to reach approval checkpoint"""
        print("⏳ Waiting for approval checkpoint...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{API_BASE}/api/hitl/{self.workflow_id}/pending-approvals",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                approvals = response.json()
                if approvals:
                    print(f"✅ Found {len(approvals)} pending approval(s)")
                    return approvals
            
            time.sleep(2)
        
        print("❌ Timeout waiting for approval checkpoint")
        return None
    
    def get_workflow_status(self):
        """Get current workflow status"""
        response = requests.get(
            f"{API_BASE}/api/workflows/{self.workflow_id}/status",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            status = response.json()
            print(f"📊 Workflow Status: {status['status']} - {status['current_stage']}")
            return status
        return None
    
    def approve_checkpoint(self, comments="Approved via test script"):
        """Approve the pending checkpoint"""
        approval_data = {
            "status": "approved",
            "comments": comments
        }
        
        response = requests.post(
            f"{API_BASE}/api/hitl/{self.workflow_id}/approve",
            json=approval_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            print("✅ Checkpoint approved successfully")
            return True
        else:
            print(f"❌ Failed to approve checkpoint: {response.text}")
            return False
    
    def reject_checkpoint(self, comments="Needs revision - test rejection"):
        """Reject the pending checkpoint"""
        approval_data = {
            "status": "rejected",
            "comments": comments
        }
        
        response = requests.post(
            f"{API_BASE}/api/hitl/{self.workflow_id}/approve",
            json=approval_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            print("✅ Checkpoint rejected successfully")
            return True
        else:
            print(f"❌ Failed to reject checkpoint: {response.text}")
            return False
    
    def get_approval_history(self):
        """Get approval history for the workflow"""
        response = requests.get(
            f"{API_BASE}/api/hitl/{self.workflow_id}/approval-history",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            history = response.json()
            print(f"📋 Approval History ({len(history)} entries):")
            for approval in history:
                print(f"  - {approval['status'].upper()}: {approval['comments']}")
            return history
        return None
    
    def run_approval_test(self):
        """Run complete approval workflow test"""
        print("🚀 Starting Approval Workflow Test")
        print("=" * 50)
        
        # Step 1: Authenticate
        if not self.authenticate():
            return False
        
        # Step 2: Create workflow
        if not self.create_workflow():
            return False
        
        # Step 3: Wait for approval checkpoint
        approvals = self.wait_for_approval_checkpoint()
        if not approvals:
            return False
        
        # Step 4: Show current status
        self.get_workflow_status()
        
        # Step 5: Test approval
        print("\n🔍 Testing Approval Process:")
        if self.approve_checkpoint("Test approval - outline looks good!"):
            time.sleep(2)
            self.get_workflow_status()
        
        # Step 6: Wait for next checkpoint (if any)
        print("\n⏳ Checking for additional checkpoints...")
        time.sleep(5)
        next_approvals = self.wait_for_approval_checkpoint(timeout=30)
        
        if next_approvals:
            print("\n🔍 Testing Rejection Process:")
            if self.reject_checkpoint("Needs more detail in module 2"):
                time.sleep(2)
                self.get_workflow_status()
        
        # Step 7: Show approval history
        print("\n📋 Final Approval History:")
        self.get_approval_history()
        
        print("\n✅ Approval workflow test completed!")
        return True

def main():
    """Main test function"""
    tester = ApprovalWorkflowTester()
    
    try:
        success = tester.run_approval_test()
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed!")
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")

if __name__ == "__main__":
    main()