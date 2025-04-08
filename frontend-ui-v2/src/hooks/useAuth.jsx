import { useState, createContext, useContext } from 'react';

// Create auth context
const AuthContext = createContext(null);

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(localStorage.getItem('isAuthenticated') === 'true');
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user') || 'null'));

  // Login function
  const login = async (email, password) => {
    // In a real app, this would make an API call
    // For now, we'll just simulate authentication with hardcoded credentials
    if (email === 'admin@promethios.ai' && password === 'ignite') {
      const userData = {
        email,
        name: 'Admin User',
        role: 'admin',
        lastLogin: new Date().toISOString()
      };

      // Store auth state in localStorage
      localStorage.setItem('isAuthenticated', 'true');
      localStorage.setItem('user', JSON.stringify(userData));

      // Update state
      setIsLoggedIn(true);
      setUser(userData);

      return true;
    } else {
      throw new Error('Invalid credentials');
    }
  };

  // Logout function
  const logout = () => {
    // Clear auth state from localStorage
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');

    // Update state
    setIsLoggedIn(false);
    setUser(null);
  };

  // Check if user is authenticated
  // Modified to check localStorage directly to ensure consistent auth state
  const isAuthenticated = () => {
    // Always check localStorage directly to avoid stale state issues
    const authStatus = localStorage.getItem('isAuthenticated') === 'true';

    // Update state if it doesn't match localStorage
    if (authStatus !== isLoggedIn) {
      setIsLoggedIn(authStatus);
    }

    return authStatus;
  };

  // Auth context value
  const value = {
    user,
    login,
    logout,
    isAuthenticated
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default useAuth;
