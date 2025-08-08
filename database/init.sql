-- Initialize Courzly database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflows_created_by ON workflows(created_by);
CREATE INDEX IF NOT EXISTS idx_workflows_created_at ON workflows(created_at);

CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_workflow_id ON workflow_checkpoints(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_stage ON workflow_checkpoints(stage);

CREATE INDEX IF NOT EXISTS idx_content_workflow_id ON content(workflow_id);
CREATE INDEX IF NOT EXISTS idx_content_type ON content(content_type);
CREATE INDEX IF NOT EXISTS idx_content_version ON content(version);

CREATE INDEX IF NOT EXISTS idx_chat_messages_workflow_id ON chat_messages(workflow_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

CREATE INDEX IF NOT EXISTS idx_approvals_workflow_id ON approvals(workflow_id);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);