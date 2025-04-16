import React, { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';

// Create the authentication context
const AuthContext = createContext(null);

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Helper for safely accessing browser APIs
const isBrowser = typeof window !== 'undefined';

// Safe localStorage functions
const safeLocalStorage = {
  getItem: (key) => {
    if (isBrowser) {
      return localStorage.getItem(key);
    }
    return null;
  },
  setItem: (key, value) => {
    if (isBrowser) {
      localStorage.setItem(key, value);
    }
  },
  removeItem: (key) => {
    if (isBrowser) {
      localStorage.removeItem(key);
    }
  }
};

// Provider component that wraps the app and makes auth object available to any child component that calls useAuth()
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Check if user is authenticated on initial load
  useEffect(() => {
    // Skip on server-side
    if (!isBrowser) {
      setLoading(false);
      return;
    }

    const checkUserAuthentication = async () => {
      try {
        setLoading(true);
        const token = safeLocalStorage.getItem('token');

        if (token) {
          // Verify token and get user data
          try {
            const userData = await authService.getCurrentUser();
            setCurrentUser(userData);
          } catch (err) {
            // If token is invalid or expired, clear it and redirect to login
            console.error('Authentication error:', err);
            safeLocalStorage.removeItem('token');
            setCurrentUser(null);
            navigate('/login');
          }
        }
      } catch (err) {
        console.error('Auth check error:', err);
        setError('Failed to authenticate user');
      } finally {
        setLoading(false);
      }
    };

    checkUserAuthentication();
  }, [navigate]);

  // Login function
  const login = async (email, password) => {
    try {
      setLoading(true);
      setError('');
      const data = await authService.login(email, password);

      // Store token in localStorage
      safeLocalStorage.setItem('token', data.token);

      // Set current user
      setCurrentUser(data.user);

      // Redirect to dashboard
      navigate('/dashboard');

      return data;
    } catch (err) {
      setError(err.message || 'Failed to login');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (email, password, name) => {
    try {
      setLoading(true);
      setError('');
      const data = await authService.register(email, password, name);

      // Store token in localStorage
      safeLocalStorage.setItem('token', data.token);

      // Set current user
      setCurrentUser(data.user);

      // Redirect to dashboard
      navigate('/dashboard');

      return data;
    } catch (err) {
      setError(err.message || 'Failed to register');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    // Clear token from localStorage
    safeLocalStorage.removeItem('token');

    // Clear current user
    setCurrentUser(null);

    // Redirect to login
    navigate('/login');
  };

  // Check if token is expired
  const isTokenExpired = () => {
    const token = safeLocalStorage.getItem('token');
    if (!token) return true;

    try {
      // In a real implementation, we would decode the JWT and check expiration
      // For now, we'll just return false (not expired)
      return false;
    } catch (error) {
      console.error('Error checking token expiration:', error);
      return true;
    }
  };

  // Value object that will be passed to consumers
  const value = {
    currentUser,
    loading,
    error,
    login,
    register,
    logout,
    isTokenExpired,
    isAuthenticated: !!currentUser
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
