import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import UIv2Shell from './pages/UIv2Shell';
import AuthGuard from './components/auth/AuthGuard';
import { AuthProvider } from './context/AuthContext';

/**
 * App - Main application component
 * Handles routing and authentication protection
 * Implements authentication failsafe protection to prevent lockout
 */
const App = () => {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes - always accessible */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<LoginPage isRegister={true} />} />
        
        {/* Protected routes - require authentication */}
        <Route path="/" element={
          <AuthGuard>
            <Navigate to="/dashboard" replace />
          </AuthGuard>
        } />
        
        {/* Agent OS Shell routes */}
        <Route path="/dashboard" element={
          <AuthGuard>
            <UIv2Shell activePage="dashboard" />
          </AuthGuard>
        } />
        
        <Route path="/chat/:agentId" element={
          <AuthGuard>
            <UIv2Shell activePage="chat" />
          </AuthGuard>
        } />
        
        <Route path="/agent/:agentId" element={
          <AuthGuard>
            <UIv2Shell activePage="agent" />
          </AuthGuard>
        } />
        
        {/* Fallback route - redirects to login if not authenticated */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </AuthProvider>
  );
};

export default App;
