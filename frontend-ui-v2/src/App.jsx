import React from 'react';
import { Box, Flex, useColorMode } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import AgentChat from './components/AgentChat';
import { useAuth } from './hooks/useAuth';

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated()) {
    return <Navigate to="/auth" />;
  }
  
  return children;
};

function App() {
  const { colorMode } = useColorMode();
  
  return (
    <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
      <Routes>
        {/* Auth route */}
        <Route path="/auth" element={<LoginPage />} />
        
        {/* HAL Agent Chat - default interface after authentication */}
        <Route 
          path="/hal" 
          element={
            <ProtectedRoute>
              <AgentChat />
            </ProtectedRoute>
          } 
        />
        
        {/* Root path redirect based on auth status */}
        <Route 
          path="/" 
          element={<Navigate to="/auth" />} 
        />
        
        {/* Fallback for unknown routes */}
        <Route 
          path="*" 
          element={<Navigate to="/auth" />} 
        />
      </Routes>
    </Box>
  );
}

// Wrapped App with providers
const AppWithProviders = () => {
  return (
    <AuthProvider>
      <Router>
        <App />
      </Router>
    </AuthProvider>
  );
};

export default AppWithProviders;
