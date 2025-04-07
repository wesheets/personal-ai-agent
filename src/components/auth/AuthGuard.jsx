import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

// Helper for safely accessing browser APIs
const isBrowser = typeof window !== 'undefined';

// Safe sessionStorage functions
const safeSessionStorage = {
  getItem: (key) => {
    if (isBrowser) {
      return sessionStorage.getItem(key);
    }
    return null;
  },
  setItem: (key, value) => {
    if (isBrowser) {
      sessionStorage.setItem(key, value);
    }
  },
  removeItem: (key) => {
    if (isBrowser) {
      sessionStorage.removeItem(key);
    }
  }
};

/**
 * AuthGuard - Component to protect routes that require authentication
 * Redirects to login page if user is not authenticated or token is expired
 * 
 * Enhanced with failsafe protection to prevent lockout:
 * - Always redirects to /login if no token exists
 * - Redirects to /login if token is expired
 * - Stores the attempted URL to redirect back after successful login
 */
const AuthGuard = ({ children }) => {
  const location = useLocation();
  const { isAuthenticated, loading } = useAuth();
  
  // If auth is still loading, show nothing or a loader
  if (loading) {
    return null;
  }
  
  // If not authenticated, redirect to login
  if (!isAuthenticated) {
    // Store the current location to redirect back after login
    // This enables "return to previous page" functionality
    if (isBrowser) {
      const currentPath = location.pathname + location.search + location.hash;
      if (currentPath !== '/login' && currentPath !== '/register') {
        safeSessionStorage.setItem('redirectAfterLogin', currentPath);
      }
    }
    
    // Redirect to login page
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  
  // If authenticated, render the protected component
  return children;
};

export default AuthGuard;
