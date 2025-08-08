import axios from 'axios';
import { User, Workflow, Content, ChatMessage, Checkpoint, Approval } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },
  
  register: async (userData: { email: string; username: string; full_name: string; password: string }) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },
  
  getMe: async (): Promise<User> => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  
  logout: async () => {
    await api.post('/api/auth/logout');
  }
};

// Workflows API
export const workflowsApi = {
  create: async (data: { title: string; description?: string; config?: any }): Promise<Workflow> => {
    const response = await api.post('/api/workflows/course/create', data);
    return response.data;
  },
  
  getStatus: async (workflowId: string): Promise<Workflow> => {
    const response = await api.get(`/api/workflows/${workflowId}/status`);
    return response.data;
  },
  
  getCheckpoints: async (workflowId: string): Promise<Checkpoint[]> => {
    const response = await api.get(`/api/workflows/${workflowId}/checkpoints`);
    return response.data;
  },
  
  resume: async (workflowId: string) => {
    const response = await api.post(`/api/workflows/${workflowId}/resume`);
    return response.data;
  },
  
  pause: async (workflowId: string) => {
    const response = await api.post(`/api/workflows/${workflowId}/pause`);
    return response.data;
  }
};

// HITL API
export const hitlApi = {
  approve: async (workflowId: string, data: { status: string; comments?: string; changes_made?: any }) => {
    const response = await api.post(`/api/hitl/${workflowId}/approve`, data);
    return response.data;
  },
  
  editContent: async (workflowId: string, contentId: string, data: { content_data: any; comments?: string }) => {
    const response = await api.post(`/api/hitl/${workflowId}/edit?content_id=${contentId}`, data);
    return response.data;
  },
  
  compareContent: async (workflowId: string, contentId: string) => {
    const response = await api.get(`/api/hitl/${workflowId}/compare/${contentId}`);
    return response.data;
  },
  
  getPendingApprovals: async (workflowId: string) => {
    const response = await api.get(`/api/hitl/${workflowId}/pending-approvals`);
    return response.data;
  }
};

// Content API
export const contentApi = {
  getWorkflowContent: async (workflowId: string): Promise<Content[]> => {
    const response = await api.get(`/api/content/${workflowId}`);
    return response.data;
  },
  
  getContentById: async (workflowId: string, contentId: string): Promise<Content> => {
    const response = await api.get(`/api/content/${workflowId}/${contentId}`);
    return response.data;
  },
  
  updateContent: async (workflowId: string, contentId: string, data: { title?: string; content_data: any }) => {
    const response = await api.put(`/api/content/${workflowId}/${contentId}`, data);
    return response.data;
  },
  
  exportContent: async (workflowId: string, format: string, options: any = {}) => {
    const response = await api.post(`/api/content/${workflowId}/export`, { format, options }, {
      responseType: 'blob'
    });
    return response.data;
  }
};

// Chat API
export const chatApi = {
  sendMessage: async (workflowId: string, data: { message: string; message_type?: string; metadata?: any }) => {
    const response = await api.post(`/api/chat/${workflowId}/message`, data);
    return response.data;
  },
  
  getHistory: async (workflowId: string, limit: number = 50, offset: number = 0): Promise<{ messages: ChatMessage[]; total_count: number }> => {
    const response = await api.get(`/api/chat/${workflowId}/history?limit=${limit}&offset=${offset}`);
    return response.data;
  },
  
  deleteMessage: async (workflowId: string, messageId: string) => {
    const response = await api.delete(`/api/chat/${workflowId}/messages/${messageId}`);
    return response.data;
  }
};

export default api;