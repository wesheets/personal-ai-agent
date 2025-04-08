import { useState, createContext, useContext, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

// Create auth context
const AuthContext = createContext(null);

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(localStorage.getItem('isAuthenticated') === 'true');
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user') || 'null'));
  const location = useLocation();

  // Effect to check authentication status on route change
  useEffect(() => {
    // Check localStorage on every navigation to ensure auth state is consistent
    const storedAuthState = localStorage.getItem('isAuthenticated') === 'true';
    if (storedAuthState !== isLoggedIn) {
      setIsLoggedIn(storedAuthState);
    }

    const storedUser = JSON.parse(localStorage.getItem('user') || 'null');
    if (JSON.stringify(storedUser) !== JSON.stringify(user)) {
      setUser(storedUser);
    }
  }, [location.pathname]); // Re-run when route changes

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
  const isAuthenticated = () => {
    // Always check localStorage directly to ensure we have the latest state
    return localStorage.getItem('isAuthenticated') === 'true';
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
