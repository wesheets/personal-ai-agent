import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized errors (expired or invalid token)
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');

      // Store current path for redirect after login
      const currentPath = window.location.pathname + window.location.search + window.location.hash;
      if (currentPath !== '/login' && currentPath !== '/register') {
        sessionStorage.setItem('redirectAfterLogin', currentPath);
      }

      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const authService = {
  // Login user
  login: async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to login');
    }
  },

  // Register user
  register: async (email, password, name) => {
    try {
      const response = await api.post('/auth/register', { email, password, name });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to register');
    }
  },

  // Get current user
  getCurrentUser: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to get user data');
    }
  },

  // Logout user
  logout: async () => {
    try {
      await api.post('/auth/logout');
      localStorage.removeItem('token');

      // Redirect to login page after logout
      window.location.href = '/login';
    } catch (error) {
      console.error('Logout error:', error);
      // Still remove token and redirect even if API call fails
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
  }
};

export default authService;
