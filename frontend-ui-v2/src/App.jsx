import React from 'react';
import { Box, Flex, useColorMode } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route, Navigate, useParams } from 'react-router-dom';

import { AuthProvider, useAuth } from './hooks/useAuth';
import LoginPage from './pages/LoginPage';
import AgentChat from './components/AgentChat';
import AuthenticatedLayout from './components/AuthenticatedLayout';
import TrainingDashboard from './components/TrainingDashboard';
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
import ErrorBoundary from './components/ErrorBoundary';
import StatusOverlay from './components/StatusOverlay';
import { StatusProvider } from './context/StatusContext';
import { SettingsProvider } from './context/SettingsContext';

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
              name: 'HAL 9000',
              icon: '🔴',
              status: 'ready',
              type: 'system',
              description: 'I am HAL 9000, a highly advanced AI system.'
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
  if (error) return <Box p={5} color="red.500">{error}</Box>;
  if (!agentData) return <Box p={5}>Agent Not Found</Box>;

  return (
    <Box p={4}>
      <Flex align="center" mb={6}>
        <Box fontSize="3xl" mr={3}>{agentData.icon}</Box>
        <Box>
          <Box fontSize="2xl" fontWeight="bold">{agentData.name}</Box>
          <Box color="gray.500">Status: {agentData.status}</Box>
        </Box>
      </Flex>
      <Box mb={6}>{agentData.description}</Box>
      <Box p={4} borderWidth="1px" borderRadius="lg">Chat with {agentData.name} coming soon.</Box>
    </Box>
  );
};

function App() {
  const { colorMode } = useColorMode();
  const { isAuthenticated } = useAuth();

  return (
    <Box minH="100vh" bg={colorMode === 'light' ? 'gray.50' : 'gray.800'}>
      <Routes>
        <Route path="/auth" element={<LoginPage />} />
        <Route path="/hal" element={
          isAuthenticated() ? (
            <AuthenticatedLayout>
              <AgentChat />
            </AuthenticatedLayout>
          ) : <Navigate to="/auth" />
        } />
        <Route path="/training" element={
          isAuthenticated() ? (
            <AuthenticatedLayout>
              <TrainingDashboard />
            </AuthenticatedLayout>
          ) : <Navigate to="/auth" />
        } />
        <Route path="/" element={
          isAuthenticated() ? <Navigate to="/hal" /> : <Navigate to="/auth" />
        } />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/chat/:agentId" element={<AgentChatView />} />
        <Route path="/builder" element={<BuilderAgent />} />
        <Route path="/ops" element={<OpsAgent />} />
        <Route path="/research" element={<ResearchAgent />} />
        <Route path="/memory" element={<MemoryAgentView />} />
        <Route path="/memory-browser" element={<MemoryBrowser />} />
        <Route path="/activity" element={<MainActivityFeed />} />
        <Route path="/agent-activity" element={<AgentActivityPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/agents" element={<AgentListPage />} />
        <Route path="*" element={<Navigate to="/auth" />} />
      </Routes>
    </Box>
  );
}

const AppWithProviders = () => {
  return (
    <AuthProvider>
      <ErrorBoundary>
        <SettingsProvider>
          <StatusProvider>
            <Router>
              <App />
              <StatusOverlay />
            </Router>
          </StatusProvider>
        </SettingsProvider>
      </ErrorBoundary>
    </AuthProvider>
  );
};

export default AppWithProviders;
