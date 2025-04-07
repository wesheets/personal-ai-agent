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
    console.log('🚀 API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    // Handle errors globally
    console.error('❌ API Error:', error?.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Agent control service implementation
export const controlService = {
  // Get agent status from API or return mock data if endpoint doesn't exist
  getAgentStatus: async () => {
    try {
      // Attempt to call the actual API endpoint
      const response = await apiClient.get('/agents/status');
      return response.data;
    } catch (error) {
      console.warn("Using mock data for agent status - API endpoint may not exist yet");
      // Return mock data if the API call fails
      return {
        agents: [
          { id: 'hal9000', name: 'HAL 9000', icon: '🔴', status: 'ready', type: 'system' },
          { id: 'ash-xenomorph', name: 'Ash', icon: '🧬', status: 'idle', type: 'persona' }
        ]
      };
    }
  },
  
  // Get control mode or return default if not implemented
  getControlMode: async () => {
    try {
      // Attempt to call the actual API endpoint
      const response = await apiClient.get('/agents/control-mode');
      return response.data;
    } catch (error) {
      console.warn("Using default control mode - API endpoint may not exist yet");
      // Return default control mode if the API call fails
      return {
        mode: 'standard',
        permissions: ['chat', 'memory', 'files']
      };
    }
  }
};

// API service functions with null-safe handling
const ApiService = {
  // Agent delegation (legacy non-streaming version)
  delegateTask: async (agentType, taskName, taskGoal) => {
    try {
      console.log('📤 Delegate Task Request:', { agent: agentType, name: taskName, goal: taskGoal });
      
      const response = await apiClient.post('/api/agent/delegate', {
        agent_id: agentType,
        task: {
          task_id: `task-${Date.now()}`,
          task_type: 'text',
          input: taskGoal
        }
      });
      
      // Log the raw response for debugging
      console.log('📥 Delegate Task Raw Response:', response);
      
      // Ensure we're returning a properly formatted object
      const responseData = response?.data ?? { error: 'No data returned' };
      console.log('🔄 Delegate Task Formatted Response:', responseData);
      
      // If response doesn't have expected shape, create a standardized one
      if (!responseData.status && !responseData.task_id) {
        console.log('⚠️ Standardizing response format');
        return {
          status: 'success',
          task_id: responseData.task_id || responseData.id || `task-${Date.now()}`,
          message: responseData.message || `Task delegated to ${agentType} agent`
        };
      }
      
      return responseData;
    } catch (error) {
      console.error(`❌ Error delegating task to ${agentType} agent:`, error);
      throw error;
    }
  },

  // Agent delegation with streaming support
  delegateTaskStreaming: async (agentId, taskName, taskGoal, onProgress, onComplete, onError) => {
    try {
      console.log('📤 Streaming Delegate Task Request:', { agent_id: agentId, name: taskName, goal: taskGoal });
      
      // Prepare request body
      const requestBody = {
        agent_id: agentId,
        task: {
          task_id: `task-${Date.now()}`,
          task_type: 'text',
          input: taskGoal
        }
      };

      // Use fetch API for streaming support
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/delegate-stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) {
        throw new Error(`Request failed: ${response.status} ${response.statusText}`);
      }
      
      // Handle streaming response
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let done = false;
      let finalResponse = null;
      
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            
            // Handle different types of streaming responses
            if (data.status === 'progress' && typeof onProgress === 'function') {
              onProgress(data);
            } else if (data.status === 'success') {
              finalResponse = data;
              if (typeof onComplete === 'function') {
                onComplete(data);
              }
            } else if (data.status === 'error' && typeof onError === 'function') {
              onError(data);
            }
          } catch (parseError) {
            console.error('Error parsing JSON from stream:', parseError, line);
            if (typeof onError === 'function') {
              onError({ status: 'error', message: 'Error parsing response', error: parseError.message });
            }
          }
        }
      }
      
      return finalResponse;
    } catch (error) {
      console.error(`❌ Error streaming task to ${agentId} agent:`, error);
      if (typeof onError === 'function') {
        onError({ status: 'error', message: error.message });
      }
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
