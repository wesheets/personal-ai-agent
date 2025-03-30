import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// API interfaces
export interface AgentRequest {
  input: string;
  context?: Record<string, any>;
  model?: string;
  save_to_memory?: boolean;
  auto_orchestrate?: boolean;
  enable_retry_loop?: boolean;
  skip_reflection?: boolean;
  priority_memory?: boolean;
  tools?: string[];
}

export interface AgentResponse {
  output: string;
  metadata: Record<string, any>;
  reflection?: Record<string, any>;
  retry_data?: Record<string, any>;
  nudge?: Record<string, any>;
  escalation?: Record<string, any>;
}

export interface MemoryAddRequest {
  content: string;
  metadata?: Record<string, any>;
  priority?: boolean;
}

export interface MemorySearchRequest {
  query: string;
  limit?: number;
  priority_only?: boolean;
}

export interface MemoryItem {
  id: string;
  content: string;
  metadata: Record<string, any>;
  similarity?: number;
  priority: boolean;
  created_at: string;
}

export interface MemorySearchResponse {
  results: MemoryItem[];
  metadata: Record<string, any>;
}

// Agent API functions
export const sendAgentRequest = async (
  agentType: string,
  request: AgentRequest
): Promise<AgentResponse> => {
  try {
    const response = await api.post<AgentResponse>(`/agent/${agentType}`, request);
    return response.data;
  } catch (error) {
    console.error(`Error sending request to ${agentType} agent:`, error);
    throw error;
  }
};

// Memory API functions
export const addMemory = async (request: MemoryAddRequest): Promise<{ id: string }> => {
  try {
    const response = await api.post<{ id: string }>('/memory/add', request);
    return response.data;
  } catch (error) {
    console.error('Error adding memory:', error);
    throw error;
  }
};

export const searchMemory = async (request: MemorySearchRequest): Promise<MemorySearchResponse> => {
  try {
    const response = await api.post<MemorySearchResponse>('/memory/search', request);
    return response.data;
  } catch (error) {
    console.error('Error searching memory:', error);
    throw error;
  }
};

// System API functions
export const getAvailableModels = async (): Promise<string[]> => {
  try {
    const response = await api.get<string[]>('/system/models');
    return response.data;
  } catch (error) {
    console.error('Error getting available models:', error);
    throw error;
  }
};

export default api;
