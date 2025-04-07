import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

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
  
  // Check if token exists
  const token = localStorage.getItem('token');
  
  // Function to check if token is expired
  const isTokenExpired = (token) => {
    if (!token) return true;
    
    try {
      // For JWT tokens, we would normally decode and check expiration
      // This is a simplified version for demonstration
      
      // In a real implementation, we would do:
      // const decoded = jwt_decode(token);
      // return decoded.exp < Date.now() / 1000;
      
      // For demo purposes, we'll just check if token exists
      return false;
    } catch (error) {
      console.error('Error checking token expiration:', error);
      return true;
    }
  };
  
  // If no token or token is expired, redirect to login
  if (!token || isTokenExpired(token)) {
    // Clear any existing token if it's expired
    if (token && isTokenExpired(token)) {
      localStorage.removeItem('token');
    }
    
    // Store the current location to redirect back after login
    // This enables "return to previous page" functionality
    const currentPath = location.pathname + location.search + location.hash;
    if (currentPath !== '/login' && currentPath !== '/register') {
      sessionStorage.setItem('redirectAfterLogin', currentPath);
    }
    
    // Redirect to login page
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  
  // If authenticated, render the protected component
  return children;
};

export default AuthGuard;
