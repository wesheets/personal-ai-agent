
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
    const storedAuthState = localStorage.getItem('isAuthenticated') === 'true';
    if (storedAuthState !== isLoggedIn) {
      setIsLoggedIn(storedAuthState);
    }

    const storedUser = JSON.parse(localStorage.getItem('user') || 'null');
    if (JSON.stringify(storedUser) !== JSON.stringify(user)) {
      setUser(storedUser);
    }
  }, [location.pathname, isLoggedIn, user]);

  // Login function
  const login = async (email, password) => {
    if (email === 'admin@promethios.ai' && password === 'ignite') {
      const userData = {
        email,
        name: 'Admin User',
        role: 'admin',
        lastLogin: new Date().toISOString()
      };

      localStorage.setItem('isAuthenticated', 'true');
      localStorage.setItem('user', JSON.stringify(userData));

      setIsLoggedIn(true);
      setUser(userData);

      return true;
    } else {
      throw new Error('Invalid credentials');
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('user');
    setIsLoggedIn(false);
    setUser(null);
    
    // Use relative path for logout redirect
    window.location.href = '/auth';
  };

  // Check if user is authenticated with localStorage as source of truth
  const isAuthenticated = () => {
    const authStatus = localStorage.getItem('isAuthenticated') === 'true';
    if (authStatus !== isLoggedIn) {
      setIsLoggedIn(authStatus);
    }
    return authStatus;
  };

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
