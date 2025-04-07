import React from 'react';
import { Box, Flex, useColorMode } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
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
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import AuthSwitcher from './components/auth/AuthSwitcher';
import './styles/animations.css';

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <Box p={5}>Loading...</Box>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Auth layout without sidebar for login/register pages
const AuthLayout = ({ children }) => {
  const { colorMode } = useColorMode();
  
  return (
    <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
      <Flex direction="column" h="100vh" justifyContent="center" alignItems="center">
        {children}
      </Flex>
    </Box>
  );
};

// Main application with routing
function AppRoutes() {
  const { colorMode } = useColorMode();
  const { user, isAuthenticated } = useAuth();
  
  return (
    <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
      <Flex direction="column" h="100vh">
        {/* Top navigation area with color mode toggle and auth switcher */}
        <Flex 
          as="header" 
          position="fixed" 
          w="full" 
          zIndex="1000"
          bg={colorMode === 'light' ? 'white' : 'gray.800'}
          boxShadow="sm"
          justifyContent="space-between"
          alignItems="center"
          p={2}
        >
          <Box></Box> {/* Empty box for flex spacing */}
          <Flex alignItems="center" gap={4}>
            <AuthSwitcher user={user} isAuthenticated={isAuthenticated} />
            <ColorModeToggle />
          </Flex>
        </Flex>
        
        {/* Sidebar navigation - only shown when authenticated */}
        {isAuthenticated && <Sidebar />}
        
        {/* Main content area */}
        <Box 
          ml={{ base: 0, md: isAuthenticated ? '60' : 0 }} 
          p="4" 
          pt="20"
          width="full"
        >
          <Routes>
            {/* Auth routes */}
            <Route path="/login" element={
              <AuthLayout>
                <LoginPage />
              </AuthLayout>
            } />
            <Route path="/register" element={
              <AuthLayout>
                <RegisterPage />
              </AuthLayout>
            } />
            
            {/* Protected routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <Dashboard />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
            <Route path="/builder" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <BuilderAgent />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
            <Route path="/ops" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <OpsAgent />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
            <Route path="/research" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <ResearchAgent />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
            <Route path="/memory" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <MemoryAgentView />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
            <Route path="/memory-browser" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <MemoryBrowser />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
            <Route path="/activity" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <MainActivityFeed />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
            <Route path="/agent-activity" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <AgentActivityPage />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <SettingsPage />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
            <Route path="/agents" element={
              <ProtectedRoute>
                <ErrorBoundary>
                  <AgentListPage />
                </ErrorBoundary>
              </ProtectedRoute>
            } />
          </Routes>
        </Box>
      </Flex>
      
      {/* Global StatusOverlay - now accessible from anywhere in the app */}
      <StatusOverlay />
    </Box>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <SettingsProvider>
          <StatusProvider>
            <AuthProvider>
              <AppRoutes />
            </AuthProvider>
          </StatusProvider>
        </SettingsProvider>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
