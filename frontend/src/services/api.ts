import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface CourseCreationRequest {
  title: string;
  description: string;
  target_audience: string;
  duration: string;
  difficulty_level: 'beginner' | 'intermediate' | 'advanced';
  learning_objectives: string[];
  topics: string[];
  assessment_type: string;
  template_id?: string;
  custom_requirements?: Record<string, any>;
}

export interface AgentConfig {
  name: string;
  description: string;
  nodes: any[];
  edges: any[];
  metadata: any;
  variables?: Record<string, any>;
}

export interface WorkflowExecution {
  id: string;
  agent_id: string;
  status: string;
  progress: number;
  current_step?: string;
  started_at: string;
  completed_at?: string;
  parameters: Record<string, any>;
  result?: Record<string, any>;
}

// Course Creation API
export const createCourse = async (data: CourseCreationRequest) => {
  const response = await api.post('/api/v1/courses/create', data);
  return response.data;
};

export const getCourseStatus = async (executionId: string) => {
  const response = await api.get(`/api/v1/executions/${executionId}/status`);
  return response.data;
};

// Agent Configuration API
export const createAgent = async (config: AgentConfig) => {
  const response = await api.post('/api/v1/agents/create', config);
  return response.data;
};

export const executeWorkflow = async (agentId: string, parameters: Record<string, any>) => {
  const response = await api.post('/api/v1/workflows/execute', {
    agent_id: agentId,
    parameters,
  });
  return response.data;
};

export const getExecutionStatus = async (executionId: string) => {
  const response = await api.get(`/api/v1/executions/${executionId}/status`);
  return response.data;
};

// Template Management API
export const getTemplates = async (category?: string, search?: string) => {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (search) params.append('search', search);
  
  const response = await api.get(`/api/v1/templates?${params.toString()}`);
  return response.data;
};

export const createTemplate = async (templateData: any) => {
  const response = await api.post('/api/v1/templates/create', templateData);
  return response.data;
};

// Approval Management API
export const getPendingApprovals = async () => {
  const response = await api.get('/api/v1/approvals/pending');
  return response.data;
};

export const respondToApproval = async (approvalId: string, response: any) => {
  const result = await api.post(`/api/v1/approvals/${approvalId}/respond`, response);
  return result.data;
};

// Batch Operations API
export const executeBatch = async (executions: any[]) => {
  const response = await api.post('/api/v1/batch/execute', { executions });
  return response.data;
};

export const getBatchStatus = async (batchId: string) => {
  const response = await api.get(`/api/v1/batch/${batchId}/status`);
  return response.data;
};

// Analytics API
export const getAnalytics = async (timeRange: string = '7d') => {
  const response = await api.get(`/api/v1/analytics?range=${timeRange}`);
  return response.data;
};

export const getExecutionMetrics = async () => {
  const response = await api.get('/api/v1/analytics/executions');
  return response.data;
};

export default api;