import axios from 'axios';

// Create an API client with the base URL from environment variables
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for logging or additional headers
apiClient.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method?.toUpperCase(), config.url);
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
    console.error('❌ API Error:', error?.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Control service for system status and control operations
export const controlService = {
  // Get agent status
  getAgentStatus: async () => {
    try {
      const response = await apiClient.get('/api/agent/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching agent status:', error);
      return {
        agents: [{ id: 'core-forge', name: 'Core.Forge', icon: '🔴', status: 'unknown' }]
      };
    }
  },

  // Get control mode
  getControlMode: async () => {
    try {
      const response = await apiClient.get('/api/system/control-mode');
      return response.data;
    } catch (error) {
      console.error('Error getting control mode:', error);
      return {
        mode: 'unknown',
        permissions: []
      };
    }
  },

  // Set control mode
  setControlMode: async (mode) => {
    try {
      const response = await apiClient.post('/api/system/control-mode', { mode });
      return response.data;
    } catch (error) {
      console.error('Error setting control mode:', error);
      return { success: false };
    }
  }
};

// API service functions with null-safe handling
const ApiService = {
  // Mock streaming function for development
  delegateTaskStreaming: async (agentId, taskName, taskGoal, onProgress, onComplete, onError) => {
    try {
      console.log('📤 Streaming Delegate Task Request:', {
        agent_id: agentId,
        name: taskName,
        goal: taskGoal
      });

      // Simulate streaming response
      const simulateStream = async () => {
        // Initial delay
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Split the response into chunks to simulate streaming
        const response = `I'm Core.Forge, the Promethios AI assistant. I've received your message: "${taskGoal}"

Let me process that for you. I can help with a wide range of tasks including research, coding, data analysis, and more.

What specific information or assistance do you need regarding this topic?`;

        const chunks = response.split(' ');

        // Stream each word with a small delay
        for (let i = 0; i < chunks.length; i++) {
          if (onProgress) {
            onProgress({
              status: 'progress',
              content: chunks[i] + ' ',
              thoughts: i % 5 === 0 ? `Processing word ${i} of ${chunks.length}...` : undefined
            });
          }

          // Add random delay between words
          await new Promise((resolve) => setTimeout(resolve, 50 + Math.random() * 150));
        }

        // Complete the stream
        if (onComplete) {
          onComplete({
            status: 'success',
            content: response,
            task_id: `task-${Date.now()}`
          });
        }
      };

      // Start the simulation
      simulateStream();

      return {
        status: 'streaming',
        message: 'Streaming started'
      };
    } catch (error) {
      console.error(`❌ Error streaming task to ${agentId} agent:`, error);
      if (onError) {
        onError({ status: 'error', message: error.message });
      }
      throw error;
    }
  },

  // Mock file upload function
  uploadFile: async (file) => {
    try {
      console.log('📤 File Upload Request:', file.name, file.type, file.size);

      // Simulate upload delay
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Return mock response
      return {
        status: 'success',
        url: `https://storage.promethios.ai/uploads/${file.name}`,
        file_id: `file-${Date.now()}`
      };
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  }
};

export default ApiService;
