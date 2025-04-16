import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import SplashPage from '../components/SplashPage';

const Index: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Check if user is already authenticated
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (username: string, password: string) => {
    // For the easter egg case, we already handle it in the LoginForm component

    // Check credentials against environment variables
    // Using fallback values for manual deployment
    const validUsername = process.env.VITE_OPERATOR_USERNAME || 'admin';
    const validPassword = process.env.VITE_OPERATOR_PASSWORD || 'securekey';

    if (username === validUsername && password === validPassword) {
      // Set authentication token in localStorage
      localStorage.setItem('auth_token', 'operator_authenticated');
      setIsAuthenticated(true);
    } else {
      setError('Access denied. You are not the operator.');
    }
  };

  // Redirect to dashboard if authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <SplashPage onLogin={handleLogin} error={error} />;
};

export default Index;
