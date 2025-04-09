import React from 'react';
import { Box, Flex, useColorMode, Text, Center } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import AgentChat from './components/AgentChat';
import AuthenticatedLayout from './components/AuthenticatedLayout';
import TrainingDashboard from './components/TrainingDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import StatusOverlay from './components/StatusOverlay';
import { StatusProvider } from './context/StatusContext';
import { SettingsProvider } from './context/SettingsContext';
import ControlRoom from './components/control-room/ControlRoom';

// Import actual page components from remote
import Dashboard from './pages/Dashboard';
import MemoryBrowser from './pages/MemoryBrowser';
import MainActivityFeed from './pages/MainActivityFeed';
import AgentListPage from './pages/AgentListPage';
import AgentActivityPage from './pages/AgentActivityPage';
import SettingsPage from './pages/SettingsPage';

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  // Show loading indicator while auth state is being determined
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minH="100vh">
        <Text fontSize="lg">Loading...</Text>
      </Box>
    );
  }

  // Only redirect if not authenticated and not in loading state
  if (!isAuthenticated()) {
    return <Navigate to="/auth" />;
  }

  // Render the authenticated layout with children
  return <AuthenticatedLayout>{children}</AuthenticatedLayout>;
};

function App() {
  const { colorMode } = useColorMode();

  return (
    <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
      <Routes>
        {/* Auth route */}
        <Route path="/auth" element={<LoginPage />} />

        {/* Protected routes - all wrapped with AuthenticatedLayout */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/memory-browser"
          element={
            <ProtectedRoute>
              <MemoryBrowser />
            </ProtectedRoute>
          }
        />
        <Route
          path="/activity"
          element={
            <ProtectedRoute>
              <MainActivityFeed />
            </ProtectedRoute>
          }
        />
        <Route
          path="/agent-activity"
          element={
            <ProtectedRoute>
              <AgentActivityPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <SettingsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/agents"
          element={
            <ProtectedRoute>
              <AgentListPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/training"
          element={
            <ProtectedRoute>
              <TrainingDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/control-room"
          element={
            <ProtectedRoute>
              <ControlRoom />
            </ProtectedRoute>
          }
        />

        {/* Unified agent route */}
        <Route
          path="/agent/:agentId"
          element={
            <ProtectedRoute>
              <AgentChat />
            </ProtectedRoute>
          }
        />

        {/* Root path redirect to Core.Forge if authenticated, otherwise to auth */}
        <Route path="/" element={<Navigate to="/agent/core-forge" />} />

        {/* Fallback for unknown routes */}
        <Route path="*" element={<Navigate to="/agent/core-forge" />} />
      </Routes>
    </Box>
  );
}

const AppWithProviders = () => {
  return (
    <ErrorBoundary>
      <SettingsProvider>
        <StatusProvider>
          <Router>
            <AuthProvider>
              <App />
              <StatusOverlay />
            </AuthProvider>
          </Router>
        </StatusProvider>
      </SettingsProvider>
    </ErrorBoundary>
  );
};

export default AppWithProviders;
