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
import { useAuth } from './context/AuthContext';
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
  const { isAuthenticated, loading } = useAuth();
  
  // Show loading state while auth is initializing
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
            
            {/* Root path redirect based on auth status */}
            <Route path="/" element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />
            } />
            
            {/* Protected routes */}
            <Route path="/dashboard" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <Dashboard />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            <Route path="/builder" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <BuilderAgent />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            <Route path="/ops" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <OpsAgent />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            <Route path="/research" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <ResearchAgent />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            <Route path="/memory" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <MemoryAgentView />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            <Route path="/memory-browser" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <MemoryBrowser />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            <Route path="/activity" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <MainActivityFeed />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            <Route path="/agent-activity" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <AgentActivityPage />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            <Route path="/settings" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <SettingsPage />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            <Route path="/agents" element={
              <AuthGuard>
                <AuthenticatedLayout>
                  <ErrorBoundary>
                    <AgentListPage />
                  </ErrorBoundary>
                </AuthenticatedLayout>
              </AuthGuard>
            } />
            
            {/* Fallback redirect for unknown routes */}
            <Route path="*" element={
              isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/login" />
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
