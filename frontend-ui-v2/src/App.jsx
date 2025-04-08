import React from 'react';
import { Box, Flex, useColorMode } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import AgentChat from './components/AgentChat';
import AuthenticatedLayout from './components/AuthenticatedLayout';
import { useAuth } from './hooks/useAuth';

function App() {
  const { colorMode } = useColorMode();
  const { isAuthenticated } = useAuth();
  
  return (
    <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
      <Routes>
        {/* Auth route */}
        <Route path="/auth" element={<LoginPage />} />
        
        {/* HAL Agent Chat - default interface after authentication */}
        <Route 
          path="/hal" 
          element={
            isAuthenticated() ? (
              <AuthenticatedLayout>
                <AgentChat />
              </AuthenticatedLayout>
            ) : <Navigate to="/auth" />
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
