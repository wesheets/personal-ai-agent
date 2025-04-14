import React from 'react';
import { Box, Flex, useColorMode } from '@chakra-ui/react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AuthGuard from './components/auth/AuthGuard';
import LoginPage from './pages/LoginPage';
import ColorModeToggle from './components/ColorModeToggle';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import { BuilderAgent, OpsAgent, ResearchAgent } from './pages/AgentPanels';
import MemoryAgentView from './pages/MemoryAgentView';
import MemoryBrowser from './pages/MemoryBrowser';
import MainActivityFeed from './pages/MainActivityFeed';
import SettingsPage from './pages/SettingsPage';
import AgentListPage from './pages/AgentListPage';
import AgentActivityPage from './pages/AgentActivityPage';
import ErrorBoundary from './components/ErrorBoundary';
import StatusOverlay from './components/StatusOverlay';
import { StatusProvider } from './context/StatusContext';
import { SettingsProvider } from './context/SettingsContext';
import { isAuthenticated } from './hooks/useAuth';
import UIv2Shell from './pages/UIv2Shell';
import AgentChat from './AgentChat';
import './styles/animations.css';

// Layout component for authenticated routes
const AuthenticatedLayout = ({ children }) => {
  const { colorMode } = useColorMode();
  
  return (
    <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
      <Flex direction="column" h="100vh">
        {/* Top navigation area with color mode toggle */}
        <Flex 
          as="header" 
          position="fixed" 
          w="full" 
          zIndex="1000"
          bg={colorMode === 'light' ? 'white' : 'gray.800'}
          boxShadow="sm"
          justifyContent="flex-end"
          p={2}
        >
          <ColorModeToggle />
        </Flex>
        
        {/* Sidebar navigation */}
        <Sidebar />
        
        {/* Main content area */}
        <Box ml={{ base: 0, md: '60' }} p="4" pt="20">
          {children}
        </Box>
      </Flex>
    </Box>
  );
};

function App() {
  // Show loading state while app is initializing
  const loading = false;
  
  if (loading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minH="100vh"
        bg="gray.100"
      >
        <Box 
          p={8} 
          bg="white" 
          borderRadius="md" 
          boxShadow="md"
          textAlign="center"
        >
          Loading...
        </Box>
      </Box>
    );
  }
  
  return (
    <ErrorBoundary>
      <SettingsProvider>
        <StatusProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<LoginPage isRegister={true} />} />
            
            {/* Auth route */}
            <Route path="/auth" element={<LoginPage />} />
            
            {/* Root path redirect based on auth status */}
            <Route path="/" element={
              isAuthenticated() ? <Navigate to="/agent/hal" /> : <Navigate to="/auth" />
            } />
            
            {/* HAL Agent Chat - default interface after authentication */}
            <Route path="/hal" element={
              isAuthenticated() ? (
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <AgentChat />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              ) : <Navigate to="/auth" />
            } />
            
            {/* Protected routes */}
            <Route path="/dashboard" element={
              isAuthenticated() ? (
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <Dashboard />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              ) : <Navigate to="/auth" />
            } />
            
            <Route path="/memory-browser" element={
              isAuthenticated() ? (
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <MemoryBrowser />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              ) : <Navigate to="/auth" />
            } />
            
            <Route path="/activity" element={
              isAuthenticated() ? (
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <MainActivityFeed />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              ) : <Navigate to="/auth" />
            } />
            
            <Route path="/agent-activity" element={
              isAuthenticated() ? (
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <AgentActivityPage />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              ) : <Navigate to="/auth" />
            } />
            
            <Route path="/settings" element={
              isAuthenticated() ? (
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <SettingsPage />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              ) : <Navigate to="/auth" />
            } />
            
            <Route path="/agents" element={
              isAuthenticated() ? (
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <AgentListPage />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              ) : <Navigate to="/auth" />
            } />
            
            {/* Agent detail routes - unified under /agent/:agentId */}
            <Route path="/agent/:agentId" element={
              isAuthenticated() ? (
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <AgentChat />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              ) : <Navigate to="/auth" />
            } />
            
            {/* Improved fallback redirect for unknown routes - now renders AgentChat with error message */}
            <Route path="*" element={
              isAuthenticated() ? (
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <Box p={4} borderRadius="md" bg="red.50" color="red.600" mb={4}>
                      Route not found. Redirected to default agent interface.
                    </Box>
                    <AgentChat />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              ) : <Navigate to="/auth" />
            } />
          </Routes>
          
          {/* Global StatusOverlay - now accessible from anywhere in the app */}
          <StatusOverlay />
        </StatusProvider>
      </SettingsProvider>
    </ErrorBoundary>
  );
}

export default App;
