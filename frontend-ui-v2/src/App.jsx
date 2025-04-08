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

// Import actual page components from remote
import Dashboard from './pages/Dashboard';
import BuilderAgent from './pages/AgentPanels';
import OpsAgent from './pages/AgentPanels';
import ResearchAgent from './pages/AgentPanels';
import MemoryAgentView from './pages/MemoryAgentView';
import MemoryBrowser from './pages/MemoryBrowser';
import MainActivityFeed from './pages/MainActivityFeed';
import AgentListPage from './pages/AgentListPage';
import AgentActivityPage from './pages/AgentActivityPage';
import SettingsPage from './pages/SettingsPage';

const AgentChatView = () => {
  const { agentId } = useParams();
  const [agentData, setAgentData] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const fetchAgentData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/agents/${agentId}`);
        if (!response.ok) {
          if (agentId === 'hal9000') {
            setAgentData({
              id: 'hal9000',
              name: 'Core.Forge',
              icon: '🔴',
              status: 'ready',
              type: 'system',
              description: 'I am Core.Forge, a highly advanced AI system.'
            });
          } else {
            setAgentData({
              id: agentId,
              name: `Agent ${agentId}`,
              icon: '🤖',
              status: 'unknown',
              type: 'generic',
              description: 'Agent information not available.'
            });
          }
        } else {
          const data = await response.json();
          setAgentData(data);
        }
      } catch (err) {
        console.error('Error fetching agent data:', err);
        setError('Failed to load agent data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (agentId) {
      fetchAgentData();
    }
  }, [agentId]);

  if (loading) return <Box p={5}>Loading agent interface...</Box>;
  if (error)
    return (
      <Box p={5} color="red.500">
        {error}
      </Box>
    );
  if (!agentData) return <Box p={5}>Agent Not Found</Box>;

  return (
    <Box p={4}>
      <Flex align="center" mb={6}>
        <Box fontSize="3xl" mr={3}>
          {agentData.icon}
        </Box>
        <Box>
          <Box fontSize="2xl" fontWeight="bold">
            {agentData.name}
          </Box>
          <Box color="gray.500">Status: {agentData.status}</Box>
        </Box>
      </Flex>
      <Box mb={6}>{agentData.description}</Box>
      <Box p={4} borderWidth="1px" borderRadius="lg">
        Chat with {agentData.name} coming soon.
      </Box>
    </Box>
  );
};

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
          path="/builder"
          element={
            <ProtectedRoute>
              <BuilderAgent />
            </ProtectedRoute>
          }
        />
        <Route
          path="/ops"
          element={
            <ProtectedRoute>
              <OpsAgent />
            </ProtectedRoute>
          }
        />
        <Route
          path="/research"
          element={
            <ProtectedRoute>
              <ResearchAgent />
            </ProtectedRoute>
          }
        />
        <Route
          path="/memory"
          element={
            <ProtectedRoute>
              <MemoryAgentView />
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
          path="/chat/:agentId"
          element={
            <ProtectedRoute>
              <AgentChatView />
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

        {/* Core.Forge Agent Chat - default interface after authentication */}
        <Route
          path="/hal"
          element={
            <ProtectedRoute>
              <AgentChat />
            </ProtectedRoute>
          }
        />

        {/* Root path redirect to Core.Forge if authenticated, otherwise to auth */}
        <Route path="/" element={<Navigate to="/core-forge" />} />

        {/* Fallback for unknown routes */}
        <Route path="*" element={<Navigate to="/core-forge" />} />
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
