import axios from 'axios';

// Base API URL - configured from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Goals API
export const goalsService = {
  // Get all goals with their subtasks
  getGoals: async () => {
    try {
      const response = await apiClient.get('/api/goals');
      return response.data;
    } catch (error) {
      console.error('Error fetching goals:', error);
      throw error;
    }
  },
  
  // Get task state
  getTaskState: async () => {
    try {
      const response = await apiClient.get('/api/task-state');
      return response.data;
    } catch (error) {
      console.error('Error fetching task state:', error);
      throw error;
    }
  },
  
  // Kill a task
  killTask: async (taskId) => {
    try {
      const response = await apiClient.post(`/api/task-state/${taskId}/kill`);
      return response.data;
    } catch (error) {
      console.error(`Error killing task ${taskId}:`, error);
      throw error;
    }
  },
  
  // Restart a task
  restartTask: async (taskId) => {
    try {
      const response = await apiClient.post(`/api/task-state/${taskId}/restart`);
      return response.data;
    } catch (error) {
      console.error(`Error restarting task ${taskId}:`, error);
      throw error;
    }
  }
};

// Memory API
export const memoryService = {
  // Get memory entries with optional filtering
  getMemoryEntries: async (filters = {}) => {
    try {
      const response = await apiClient.get('/api/memory', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error fetching memory entries:', error);
      throw error;
    }
  },
  
  // Create a new memory entry
  createMemoryEntry: async (memoryData) => {
    try {
      const response = await apiClient.post('/api/memory', memoryData);
      return response.data;
    } catch (error) {
      console.error('Error creating memory entry:', error);
      throw error;
    }
  }
};

// Control API
export const controlService = {
  // Get system control mode
  getControlMode: async () => {
    try {
      const response = await apiClient.get('/api/system/control-mode');
      return response.data;
    } catch (error) {
      console.error('Error fetching control mode:', error);
      throw error;
    }
  },
  
  // Set system control mode
  setControlMode: async (mode) => {
    try {
      const response = await apiClient.post('/api/system/control-mode', { mode });
      return response.data;
    } catch (error) {
      console.error(`Error setting control mode to ${mode}:`, error);
      throw error;
    }
  },
  
  // Get agent status
  getAgentStatus: async () => {
    try {
      const response = await apiClient.get('/api/agent/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching agent status:', error);
      throw error;
    }
  },
  
  // Delegate task to another agent
  delegateTask: async (taskId, targetAgent, taskDescription = null) => {
    try {
      const payload = {
        task_id: taskId,
        target_agent: targetAgent
      };
      
      // Add task_description to payload if provided
      if (taskDescription) {
        payload.task_description = taskDescription;
      }
      
      const response = await apiClient.post('/api/agent/delegate', payload);
      return response.data;
    } catch (error) {
      console.error(`Error delegating task to ${targetAgent}:`, error);
      throw error;
    }
  },
  
  // Edit task prompt
  editTaskPrompt: async (taskId, prompt) => {
    try {
      const response = await apiClient.post(`/api/agent/goal/${taskId}/edit-prompt`, { prompt });
      return response.data;
    } catch (error) {
      console.error(`Error editing prompt for task ${taskId}:`, error);
      throw error;
    }
  }
};

// Logs API
export const logsService = {
  // Get latest logs
  getLatestLogs: async () => {
    try {
      const response = await apiClient.get('/api/logs/latest');
      return response.data;
    } catch (error) {
      console.error('Error fetching latest logs:', error);
      throw error;
    }
  }
};

export default {
  goalsService,
  memoryService,
  controlService,
  logsService
};
