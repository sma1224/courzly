export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: 'admin' | 'editor' | 'reviewer' | 'viewer';
  is_active: boolean;
  created_at: string;
}

export interface Workflow {
  id: string;
  title: string;
  description?: string;
  status: 'created' | 'running' | 'paused' | 'waiting_approval' | 'completed' | 'failed' | 'cancelled';
  current_stage: 'outline' | 'content_generation' | 'review' | 'final_assembly' | 'export';
  created_at: string;
  config: Record<string, any>;
}

export interface Content {
  id: string;
  workflow_id: string;
  title?: string;
  content_type: string;
  content_data: Record<string, any>;
  version: number;
  is_ai_generated: boolean;
  is_human_edited: boolean;
  is_approved: boolean;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  workflow_id: string;
  user_id?: string;
  message: string;
  message_type: string;
  metadata: Record<string, any>;
  created_at: string;
  is_ai: boolean;
}

export interface Checkpoint {
  id: string;
  stage: string;
  requires_approval: boolean;
  approved: boolean;
  created_at: string;
  state_data: Record<string, any>;
}

export interface Approval {
  id: string;
  status: 'pending' | 'approved' | 'rejected';
  comments?: string;
  approver_id: string;
  decided_at?: string;
}