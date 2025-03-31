import axios from 'axios';

// Create an API client with the base URL from environment variables
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging or additional headers
apiClient.interceptors.request.use(
  (config) => {
    // You can add auth tokens or other headers here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle errors globally
    console.error('API Error:', error?.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API service functions with null-safe handling
const ApiService = {
  // Agent delegation
  delegateTask: async (agentType, taskName, taskGoal) => {
    try {
      const response = await apiClient.post('/api/agent/delegate', {
        agent: agentType,
        name: taskName,
        goal: taskGoal,
      });
      return response?.data ?? { error: 'No data returned' };
    } catch (error) {
      console.error(`Error delegating task to ${agentType} agent:`, error);
      throw error;
    }
  },

  // Memory operations
  getMemories: async () => {
    try {
      const response = await apiClient.get('/api/memory');
      return response?.data ?? [];
    } catch (error) {
      console.error('Error fetching memories:', error);
      throw error;
    }
  },

  saveMemory: async (content, type = 'text') => {
    try {
      const response = await apiClient.post('/api/memory', {
        content,
        type,
      });
      return response?.data ?? { error: 'No data returned' };
    } catch (error) {
      console.error('Error saving memory:', error);
      throw error;
    }
  },

  uploadFile: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/api/memory', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response?.data ?? { error: 'No data returned' };
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  },

  // Logs
  getLogs: async () => {
    try {
      const response = await apiClient.get('/api/logs/latest');
      return response?.data ?? [];
    } catch (error) {
      console.error('Error fetching logs:', error);
      throw error;
    }
  },
};

export default ApiService;
