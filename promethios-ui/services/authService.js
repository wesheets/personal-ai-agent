// Simple auth service for Promethios UI
const authService = {
  // Login function (mock implementation)
  login: async (email, password) => {
    // In a real implementation, this would call an API
    return {
      token: 'mock-token',
      user: {
        username: email,
        role: 'operator'
      }
    };
  },

  // Register function (mock implementation)
  register: async (email, password, name) => {
    // In a real implementation, this would call an API
    return {
      token: 'mock-token',
      user: {
        username: email,
        name,
        role: 'operator'
      }
    };
  },

  // Get current user function (mock implementation)
  getCurrentUser: async () => {
    // In a real implementation, this would validate the token and get user data
    try {
      const token = localStorage.getItem('token');
      if (!token) return null;
      
      // Parse token if it's JSON
      try {
        const userData = JSON.parse(token);
        return {
          username: userData.user || 'operator',
          role: 'operator'
        };
      } catch (e) {
        // If token is not JSON, just return a default user
        return {
          username: 'operator',
          role: 'operator'
        };
      }
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  },

  // Logout function
  logout: () => {
    try {
      localStorage.removeItem('token');
    } catch (error) {
      console.error('Error during logout:', error);
    }
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    try {
      return !!localStorage.getItem('token');
    } catch (error) {
      console.error('Error checking authentication:', error);
      return false;
    }
  }
};

export default authService;
