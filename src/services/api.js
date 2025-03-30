// API service for connecting to the backend

import axios from 'axios';

// Base API URL - configured from environment variable
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://personal-ai-agent-production.up.railway.app';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const fetchGoals = async () => {
  try {
    const response = await api.get('/api/goals');
    return response.data;
  } catch (error) {
    console.error('Error fetching goals:', error);
    throw error;
  }
};

export const fetchTaskState = async () => {
  try {
    const response = await api.get('/api/task-state');
    return response.data;
  } catch (error) {
    console.error('Error fetching task state:', error);
    throw error;
  }
};

export const fetchControlMode = async () => {
  try {
    const response = await api.get('/api/system/control-mode');
    return response.data;
  } catch (error) {
    console.error('Error fetching control mode:', error);
    throw error;
  }
};

export const fetchAgentStatus = async () => {
  try {
    const response = await api.get('/api/agent/status');
    return response.data;
  } catch (error) {
    console.error('Error fetching agent status:', error);
    throw error;
  }
};

export default api;
